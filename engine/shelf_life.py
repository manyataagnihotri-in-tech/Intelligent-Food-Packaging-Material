import math
from typing import Dict, List, Any

# Baseline reference shelf life in days at optimal temperature
BASELINE_SHELF_LIFE_DAYS = {
    "mango_alphonso": 21.0,
    "tomato_fresh": 18.0,
    "apple_shimla": 60.0,
    "spinach_fresh": 8.0,
    "banana_cavendish": 16.0,
    "mushroom_button": 7.0,
    "paneer_fresh": 12.0,
    "milk_pasteurized": 7.0,
    "curd_dahi": 15.0,
    "cheese_cheddar": 45.0,
    "butter_ghee": 90.0,
    "poultry_chicken": 8.0,
    "mutton_goat": 9.0,
    "minced_meat": 4.5,
    "buffalo_meat": 12.0,
    "rohu_fish_fillet": 6.0,
    "shrimp_prawns": 5.0,
    "fish_steaks": 6.0,
    "dried_fish": 180.0,
    "eggs_shell": 30.0,
    "egg_liquid": 21.0,
    "namkeen_bhujia": 180.0,
    "potato_chips": 180.0,
    "roasted_nuts": 270.0,
    "white_bread": 6.0,
    "cookies_biscuits": 180.0,
    "roti_packaged": 14.0,
    "basmati_rice": 365.0,
    "wheat_atta": 180.0,
    "toor_dal": 365.0,
    "rte_dal_makhani": 365.0,
    "rte_palak_paneer": 365.0,
    "spices_ground": 365.0,
    "rte_butter_chicken": 365.0,
    "chicken_sausage": 28.0
}

# Commodity-specific Q10 temperature acceleration coefficients
COMMODITY_Q10 = {
    "mango_alphonso": 2.2,
    "tomato_fresh": 2.0,
    "apple_shimla": 2.1,
    "spinach_fresh": 2.5,
    "banana_cavendish": 2.3,
    "mushroom_button": 2.8,
    "paneer_fresh": 2.5,
    "milk_pasteurized": 2.8,
    "curd_dahi": 2.2,
    "cheese_cheddar": 2.0,
    "butter_ghee": 1.8,
    "poultry_chicken": 2.7,
    "mutton_goat": 2.6,
    "minced_meat": 3.0,
    "buffalo_meat": 2.5,
    "rohu_fish_fillet": 3.0,
    "shrimp_prawns": 3.2,
    "fish_steaks": 3.0,
    "dried_fish": 1.5,
    "eggs_shell": 2.0,
    "egg_liquid": 2.6,
    "namkeen_bhujia": 1.5,
    "potato_chips": 1.5,
    "roasted_nuts": 1.4,
    "white_bread": 1.8,
    "cookies_biscuits": 1.4,
    "roti_packaged": 2.0,
    "basmati_rice": 1.2,
    "wheat_atta": 1.3,
    "toor_dal": 1.2,
    "rte_dal_makhani": 1.4,
    "rte_palak_paneer": 1.4,
    "spices_ground": 1.3,
    "rte_butter_chicken": 1.4,
    "chicken_sausage": 2.3
}

def infer_baseline_shelf_life(category: str, food_type: str = "veg") -> float:
    cat_l = category.lower()
    if any(k in cat_l for k in ["fish", "seafood", "prawn", "shrimp"]):
        return 6.0
    elif any(k in cat_l for k in ["meat", "poultry", "chicken", "mutton", "pork", "beef", "keema"]):
        return 7.0
    elif any(k in cat_l for k in ["dairy", "milk", "paneer", "yogurt", "cheese", "curd"]):
        return 12.0
    elif any(k in cat_l for k in ["fruit", "vegetable", "produce", "greens", "herb"]):
        return 16.0
    elif any(k in cat_l for k in ["bakery", "bread", "cake", "pastry"]):
        return 7.0
    elif any(k in cat_l for k in ["snack", "fried", "chips", "crisp", "nuts"]):
        return 180.0
    elif any(k in cat_l for k in ["grain", "pulse", "cereal", "flour", "rice", "dal", "atta", "spice"]):
        return 365.0
    elif any(k in cat_l for k in ["retort", "rte", "ready-to-eat", "canned", "aseptic"]):
        return 365.0
    elif any(k in cat_l for k in ["frozen"]):
        return 180.0
    return 14.0

def infer_q10(category: str) -> float:
    cat_l = category.lower()
    if any(k in cat_l for k in ["fish", "seafood", "prawn"]):
        return 3.0
    elif any(k in cat_l for k in ["meat", "poultry", "chicken", "mutton"]):
        return 2.7
    elif any(k in cat_l for k in ["dairy", "milk", "paneer"]):
        return 2.5
    elif any(k in cat_l for k in ["fruit", "vegetable", "produce"]):
        return 2.2
    elif any(k in cat_l for k in ["bakery", "bread"]):
        return 1.8
    elif any(k in cat_l for k in ["snack", "fried"]):
        return 1.5
    elif any(k in cat_l for k in ["grain", "pulse", "retort", "rte"]):
        return 1.3
    return 2.0

def simulate_shelf_life(
    commodity: Dict[str, Any],
    material: Dict[str, Any],
    active_features_enabled: bool,
    storage_temp_c: float,
    storage_rh_pct: float
) -> Dict[str, Any]:
    """
    Simulates dynamic shelf-life based on:
    - Base commodity stability (supports custom defined foods)
    - Arrhenius / Q10 temperature acceleration: Rate = Rate_ref * Q10^((T - T_ref)/10)
    - Packaging barrier protection multiplier (OTR & WVTR performance)
    - Active packaging extension bonus (e.g., O2 scavengers, antimicrobial pads)
    """
    comm_id = commodity.get("id", "")
    comm_cat = commodity.get("category", "")
    food_type = commodity.get("food_type", "veg")

    # Determine baseline days
    if "baseline_shelf_life_days" in commodity and commodity["baseline_shelf_life_days"]:
        base_days = float(commodity["baseline_shelf_life_days"])
    elif comm_id in BASELINE_SHELF_LIFE_DAYS:
        base_days = BASELINE_SHELF_LIFE_DAYS[comm_id]
    else:
        base_days = infer_baseline_shelf_life(comm_cat, food_type)

    # Determine Q10
    if "q10" in commodity and commodity["q10"]:
        q10 = float(commodity["q10"])
    elif comm_id in COMMODITY_Q10:
        q10 = COMMODITY_Q10[comm_id]
    else:
        q10 = infer_q10(comm_cat)

    opt_temp = float(commodity.get("optimal_temp_c", 10.0))

    # 1. Temperature factor
    delta_t = storage_temp_c - opt_temp
    # Higher temperature accelerates spoilage
    temp_acceleration = math.pow(q10, delta_t / 10.0)
    temp_adjusted_days = base_days / max(0.2, temp_acceleration)

    # 2. Packaging barrier performance multiplier
    target_otr = commodity.get("target_otr_range", [10, 100])
    target_wvtr = commodity.get("target_wvtr_range", [2, 10])
    
    cat_lower = comm_cat.lower()
    is_respiring = "fruit" in cat_lower or "vegetable" in cat_lower or "produce" in cat_lower
    
    # Calculate how well packaging matches commodity
    otr_mid = (target_otr[0] + target_otr[1]) / 2.0
    wvtr_mid = (target_wvtr[0] + target_wvtr[1]) / 2.0

    # Barrier efficacy factor [0.4 to 1.3]
    if is_respiring:
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
    rh_opt = float(commodity.get("optimal_rh_pct", 75.0))
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
