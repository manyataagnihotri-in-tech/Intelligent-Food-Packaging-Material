import json
import math
from pathlib import Path
from typing import Dict, List, Any, Union

DATA_DIR = Path(__file__).parent.parent / "data"

def load_data():
    with open(DATA_DIR / "commodities.json", "r", encoding="utf-8") as f:
        commodities = json.load(f)
    with open(DATA_DIR / "materials.json", "r", encoding="utf-8") as f:
        materials = json.load(f)
    with open(DATA_DIR / "intelligent_features.json", "r", encoding="utf-8") as f:
        features = json.load(f)
    return commodities, materials, features

def compute_barrier_score(mat_val: float, target_range: List[float]) -> float:
    """
    Computes a normalized compatibility score [0.0 to 1.0] for barrier properties (OTR or WVTR)
    using logarithmic distance from optimal window.
    """
    min_val, max_val = target_range
    if min_val <= mat_val <= max_val:
        return 1.0
    
    # Distance penalty in log space
    if mat_val < min_val:
        # Lower permeability than required: Usually acceptable unless commodity is fresh produce needing breathability
        ratio = mat_val / max(min_val, 1e-4)
        score = max(0.05, 1.0 - (0.4 * abs(math.log10(max(ratio, 1e-3)))))
    else:
        # Higher permeability than target: spoilage danger
        ratio = mat_val / max(max_val, 1e-4)
        score = max(0.0, 1.0 - (0.6 * abs(math.log10(ratio))))
    return min(1.0, max(0.0, score))

def recommend_packaging(
    commodity: Union[str, Dict[str, Any]],
    priority_mode: str = "Balanced",
    target_shelf_life_days: int = 14,
    storage_temp_c: float = 15.0,
    storage_rh_pct: float = 75.0,
    custom_weights: Dict[str, float] = None,
    commodity_id: str = None
) -> Dict[str, Any]:
    """
    Core AI & MCDM Recommendation algorithm.
    Accepts either commodity dictionary or commodity ID string.
    """
    commodities, materials, features = load_data()
    
    # Resolve commodity
    if isinstance(commodity, dict):
        current_commodity = commodity
    else:
        target_id = commodity or commodity_id
        current_commodity = next((c for c in commodities if c["id"] == target_id), None)
        if not current_commodity:
            raise ValueError(f"Commodity ID '{target_id}' not found.")

    # Preset weights: [Barrier, Eco/LCA, Cost, Mechanical]
    weights_map = {
        "Balanced": {"barrier": 0.40, "sustainability": 0.25, "cost": 0.20, "strength": 0.15},
        "Eco-Conscious / Sustainable": {"barrier": 0.30, "sustainability": 0.45, "cost": 0.15, "strength": 0.10},
        "Maximum Shelf-Life & Protection": {"barrier": 0.60, "sustainability": 0.10, "cost": 0.15, "strength": 0.15},
        "Cost-Optimized (SME / Rural)": {"barrier": 0.35, "sustainability": 0.10, "cost": 0.45, "strength": 0.10}
    }
    
    weights = custom_weights or weights_map.get(priority_mode, weights_map["Balanced"])
    
    # Normalize custom weights to sum to 1.0 if needed
    weight_sum = sum(weights.values())
    if weight_sum > 0 and abs(weight_sum - 1.0) > 1e-3:
        weights = {k: v / weight_sum for k, v in weights.items()}
    
    target_otr = current_commodity.get("target_otr_range", [10, 100])
    target_wvtr = current_commodity.get("target_wvtr_range", [2, 10])
    
    cat_lower = current_commodity.get("category", "").lower()
    resp_rate_lower = current_commodity.get("respiration_rate", "").lower()
    is_respiring = (
        "fruit" in cat_lower or 
        "vegetable" in cat_lower or 
        "produce" in cat_lower or 
        ("moderate" in resp_rate_lower or "high" in resp_rate_lower) and "zero" not in resp_rate_lower and "non-respiring" not in resp_rate_lower
    )

    scored_materials = []
    
    # Pre-calculate ranges for min-max normalization
    costs = [m["cost_per_sqm_inr"] for m in materials]
    strengths = [m["tensile_strength_mpa"] for m in materials]
    cfps = [m["carbon_footprint_kg_co2"] for m in materials]
    
    min_cost, max_cost = min(costs), max(costs)
    min_str, max_str = min(strengths), max(strengths)
    min_cfp, max_cfp = min(cfps), max(cfps)

    for mat in materials:
        # Hard check for respiring produce: strictly penalize ultra-barrier films (causes anaerobic fermentation)
        if is_respiring and mat["otr"] < 50:
            barrier_otr_score = 0.05
        else:
            barrier_otr_score = compute_barrier_score(mat["otr"], target_otr)
            
        barrier_wvtr_score = compute_barrier_score(mat["wvtr"], target_wvtr)
        barrier_score = 0.6 * barrier_otr_score + 0.4 * barrier_wvtr_score

        # Sustainability score
        bio_bonus = 0.5 if mat["biodegradable"] else (0.25 if mat["recyclable"] else 0.0)
        cfp_normalized = 1.0 - ((mat["carbon_footprint_kg_co2"] - min_cfp) / max(1e-4, max_cfp - min_cfp))
        sustainability_score = 0.5 * cfp_normalized + bio_bonus

        # Cost score (lower cost = higher score)
        cost_score = 1.0 - ((mat["cost_per_sqm_inr"] - min_cost) / max(1e-4, max_cost - min_cost))

        # Strength score (higher strength = higher score)
        strength_score = (mat["tensile_strength_mpa"] - min_str) / max(1e-4, max_str - min_str)

        # Composite MCDM Score (0 - 100)
        total_score = (
            weights["barrier"] * barrier_score +
            weights["sustainability"] * sustainability_score +
            weights["cost"] * cost_score +
            weights["strength"] * strength_score
        ) * 100

        # Category affinity bonus
        best_suited = [s.lower() for s in mat.get("best_suited_for", [])]
        comm_name_lower = current_commodity.get("name", "").lower()
        if any(b in cat_lower or cat_lower in b or b in comm_name_lower for b in best_suited):
            total_score = min(100.0, total_score * 1.05)

        scored_materials.append({
            "material": mat,
            "overall_score": round(total_score, 1),
            "breakdown": {
                "barrier_score": round(barrier_score * 100, 1),
                "sustainability_score": round(sustainability_score * 100, 1),
                "cost_score": round(cost_score * 100, 1),
                "mechanical_score": round(strength_score * 100, 1)
            }
        })

    # Sort descending by overall score
    scored_materials.sort(key=lambda x: x["overall_score"], reverse=True)

    # Relevant intelligent features matching commodity category
    matched_features = [
        f for f in features
        if any(cat.lower() in cat_lower or cat_lower in cat.lower() for cat in f["applicable_categories"])
    ]
    if not matched_features:
        # Generic fallback active & intelligent features
        matched_features = [features[1], features[2], features[5]]

    return {
        "commodity": current_commodity,
        "priority_mode": priority_mode,
        "weights": weights,
        "recommendations": scored_materials,
        "intelligent_features": matched_features
    }
