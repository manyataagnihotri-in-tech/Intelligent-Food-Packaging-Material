from typing import Dict, Any

# Benchmark standard packaging: Virgin fossil Multilayer Plastic (e.g. PET/PE)
BENCHMARK_VIRGIN_PLASTIC = {
    "name": "Standard Virgin PET/LDPE Laminate",
    "carbon_footprint_kg_co2": 5.2,
    "biodegradable": False,
    "recyclable": False,
    "fossil_fuel_depletion_mj": 85.0
}

def compute_lca_metrics(
    material: Dict[str, Any],
    production_volume_units: int = 10000,
    area_per_unit_sqm: float = 0.08  # Approx 200g - 500g pouch surface area
) -> Dict[str, Any]:
    """
    Computes environmental and life-cycle impact compared to virgin non-recyclable multi-layer plastics.
    Aligns with MoFPI Extended Producer Responsibility (EPR) & plastic waste management targets.
    """
    total_area_sqm = production_volume_units * area_per_unit_sqm
    
    # Weight estimation based on thickness (assuming standard density ~1.2 g/cm3)
    thickness_cm = (material["thickness_um"] / 10000.0)
    density_g_cm3 = 1.2
    weight_per_sqm_kg = (10000.0 * thickness_cm * density_g_cm3) / 1000.0
    total_material_weight_kg = total_area_sqm * weight_per_sqm_kg

    # Carbon emissions in kg CO2 eq
    mat_cfp = total_material_weight_kg * material["carbon_footprint_kg_co2"]
    bench_cfp = total_material_weight_kg * BENCHMARK_VIRGIN_PLASTIC["carbon_footprint_kg_co2"]
    co2_saved_kg = max(0.0, bench_cfp - mat_cfp)
    co2_reduction_pct = round((co2_saved_kg / max(1e-4, bench_cfp)) * 100.0, 1)

    # Virgin plastic diverted from landfill
    plastic_diverted_kg = total_material_weight_kg if (material["biodegradable"] or material.get("recyclable", False)) else 0.0

    # MoFPI Sustainability Green Tier
    if material["biodegradable"] and material["carbon_footprint_kg_co2"] <= 1.5:
        eco_tier = "MoFPI Platinum Eco-Certified (100% Compostable / Low Carbon)"
        tier_color = "#10b981"
    elif material.get("recyclable", False) or material["carbon_footprint_kg_co2"] <= 2.5:
        eco_tier = "MoFPI Gold Circular Certified (High Recyclability / Lower Emission)"
        tier_color = "#f59e0b"
    else:
        eco_tier = "Conventional High-Barrier (EPR Offset Required)"
        tier_color = "#64748b"

    return {
        "production_volume_units": production_volume_units,
        "total_material_weight_kg": round(total_material_weight_kg, 2),
        "total_carbon_emissions_kg_co2": round(mat_cfp, 2),
        "benchmark_carbon_emissions_kg_co2": round(bench_cfp, 2),
        "co2_saved_kg": round(co2_saved_kg, 2),
        "co2_reduction_pct": co2_reduction_pct,
        "plastic_waste_diverted_kg": round(plastic_diverted_kg, 2),
        "eco_tier": eco_tier,
        "tier_color": tier_color,
        "is_biodegradable": material["biodegradable"],
        "compostability_days": material.get("compostability_days", -1)
    }
