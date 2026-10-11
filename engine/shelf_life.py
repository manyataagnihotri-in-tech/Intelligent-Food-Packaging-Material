import math
from typing import Dict, List, Any

# Baseline reference shelf life in days at optimal temperature
BASELINE_SHELF_LIFE_DAYS = {
    "mango_alphonso": 21.0,
    "tomato_fresh": 18.0,
    "paneer_fresh": 12.0,
    "milk_pasteurized": 7.0,
    "poultry_chicken": 8.0,
    "rohu_fish_fillet": 6.0,
    "namkeen_bhujia": 180.0,
    "white_bread": 6.0,
    "basmati_rice": 365.0,
    "rte_dal_makhani": 365.0
}

# Commodity-specific Q10 temperature acceleration coefficients
COMMODITY_Q10 = {
    "mango_alphonso": 2.2,
    "tomato_fresh": 2.0,
    "paneer_fresh": 2.5,
    "milk_pasteurized": 2.8,
    "poultry_chicken": 2.7,
    "rohu_fish_fillet": 3.0,
    "namkeen_bhujia": 1.5,
    "white_bread": 1.8,
    "basmati_rice": 1.2,
    "rte_dal_makhani": 1.4
}

def simulate_shelf_life(
    commodity: Dict[str, Any],
    material: Dict[str, Any],
    active_features_enabled: bool,
    storage_temp_c: float,
    storage_rh_pct: float
) -> Dict[str, Any]:
    """
    Simulates dynamic shelf-life based on:
    - Base commodity stability
    - Arrhenius / Q10 temperature acceleration: Rate = Rate_ref * Q10^((T - T_ref)/10)
    - Packaging barrier protection multiplier (OTR & WVTR performance)
    - Active packaging extension bonus (e.g., O2 scavengers, antimicrobial pads)
    """
    comm_id = commodity["id"]
    base_days = BASELINE_SHELF_LIFE_DAYS.get(comm_id, 14.0)
    q10 = COMMODITY_Q10.get(comm_id, 2.0)
    opt_temp = commodity.get("optimal_temp_c", 10.0)

    # 1. Temperature factor
    delta_t = storage_temp_c - opt_temp
    # Higher temperature accelerates spoilage
    temp_acceleration = math.pow(q10, delta_t / 10.0)
    temp_adjusted_days = base_days / max(0.2, temp_acceleration)

    # 2. Packaging barrier performance multiplier
    target_otr = commodity["target_otr_range"]
    target_wvtr = commodity["target_wvtr_range"]
    
    # Calculate how well packaging matches commodity
    otr_mid = (target_otr[0] + target_otr[1]) / 2.0
    wvtr_mid = (target_wvtr[0] + target_wvtr[1]) / 2.0

    # Barrier efficacy factor [0.4 to 1.3]
    otr_ratio = material["otr"] / max(otr_mid, 1e-4)
    wvtr_ratio = material["wvtr"] / max(wvtr_mid, 1e-4)
    
    # If breathable needed vs high barrier
    if "Fruits" in commodity["category"]:
        # If too tight (< target), produce suffocates
        if material["otr"] < target_otr[0]:
            barrier_factor = 0.45
        elif target_otr[0] <= material["otr"] <= target_otr[1]:
            barrier_factor = 1.15
        else:
            barrier_factor = 0.85
    else:
        # Non-respiring: lower permeability is superior
        barrier_factor = min(1.3, max(0.4, 1.2 - 0.25 * (math.log10(max(material["otr"], 0.1)) / 3.0)))

    # Relative humidity penalty if packaging has poor WVTR and storage RH is high
    rh_opt = commodity.get("optimal_rh_pct", 75.0)
    if storage_rh_pct > rh_opt and material["wvtr"] > target_wvtr[1]:
        rh_penalty = 0.85
    else:
        rh_penalty = 1.0

    # 3. Active packaging bonus
    active_bonus = 1.35 if active_features_enabled else 1.0

    estimated_shelf_life_days = round(temp_adjusted_days * barrier_factor * rh_penalty * active_bonus, 1)
    estimated_shelf_life_days = max(1.0, estimated_shelf_life_days)

    # Generate daily degradation curve (Quality Retention Index % over time)
    # Uses first-order kinetic loss model: Q(t) = 100 * exp(-k * t)
    k_rate = math.log(2.0) / (estimated_shelf_life_days * 0.7)  # 50% quality threshold
    
    timeline_days = list(range(0, int(math.ceil(estimated_shelf_life_days * 1.4)) + 1))
    quality_curve = []
    for day in timeline_days:
        quality = 100.0 * math.exp(-k_rate * day)
        quality_curve.append({
            "day": day,
            "quality_index": max(0.0, round(quality, 1)),
            "status": "Safe / Fresh" if quality >= 70 else ("Marginal / Consume Soon" if quality >= 45 else "Spoiled / Unsafe")
        })

    return {
        "estimated_days": estimated_shelf_life_days,
        "baseline_days": base_days,
        "temperature_impact_factor": round(temp_acceleration, 2),
        "barrier_preservation_factor": round(barrier_factor, 2),
        "active_enhancement_gain_days": round(estimated_shelf_life_days - (estimated_shelf_life_days / active_bonus), 1) if active_features_enabled else 0.0,
        "quality_curve": quality_curve
    }
