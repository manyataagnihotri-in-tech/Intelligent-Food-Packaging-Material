import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import json

from engine.recommender import load_data, recommend_packaging
from engine.shelf_life import simulate_shelf_life
from engine.lca import compute_lca_metrics
from engine.report_generator import generate_pdf_report

# Page Config
st.set_page_config(
    page_title="AI Food Packaging Recommendation System | MoFPI & FSSAI",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Minimalist Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Clean Modern Background */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Sleek Executive Header */
    .executive-header {
        background: linear-gradient(135deg, #064e3b 0%, #065f46 50%, #047857 100%);
        padding: 22px 28px;
        border-radius: 14px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 18px rgba(6, 78, 59, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    .header-top-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 10px;
    }
    .header-badges-group {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
    }
    .pill-gov {
        background: rgba(254, 243, 199, 0.95);
        color: #92400e;
        border: 1px solid #fde68a;
        padding: 3px 11px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 5px;
        letter-spacing: 0.2px;
    }
    .pill-veg {
        background: #ecfdf5;
        color: #065f46;
        border: 1px solid #a7f3d0;
        padding: 3px 11px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    .pill-nonveg {
        background: #fef2f2;
        color: #991b1b;
        border: 1px solid #fecaca;
        padding: 3px 11px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    .pill-meta {
        background: rgba(255, 255, 255, 0.16);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.25);
        padding: 3px 11px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .executive-header h1 {
        color: white;
        margin: 0;
        font-size: 1.80rem;
        font-weight: 800;
        letter-spacing: -0.4px;
        line-height: 1.25;
    }
    .executive-header p {
        color: #e2e8f0;
        margin-top: 6px;
        margin-bottom: 0;
        font-size: 0.94rem;
        max-width: 950px;
        line-height: 1.45;
    }
    
    /* Clean Minimalist Metric Cards */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border-color: #cbd5e1;
    }
    .kpi-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .kpi-title {
        font-size: 0.72rem;
        color: #64748b;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .kpi-icon-pill {
        font-size: 0.72rem;
        background: #f1f5f9;
        color: #475569;
        padding: 2px 7px;
        border-radius: 6px;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 1.80rem;
        color: #0f172a;
        font-weight: 800;
        letter-spacing: -0.5px;
        line-height: 1.1;
        margin: 2px 0 6px 0;
    }
    .kpi-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 9999px;
        width: fit-content;
    }
    .kpi-badge-green {
        background: #ecfdf5;
        color: #059669;
        border: 1px solid #a7f3d0;
    }
    .kpi-badge-blue {
        background: #eff6ff;
        color: #2563eb;
        border: 1px solid #bfdbfe;
    }
    .kpi-badge-red {
        background: #fef2f2;
        color: #b91c1c;
        border: 1px solid #fecaca;
    }
    .kpi-caption {
        font-size: 0.74rem;
        color: #94a3b8;
        margin-top: 6px;
    }
    
    /* Tabs & Clean Navigation */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 0px;
        margin-bottom: 16px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 18px;
        font-weight: 600;
        font-size: 0.90rem;
        border-radius: 8px 8px 0 0;
        color: #64748b;
        background-color: transparent;
        border: none;
        transition: color 0.15s ease;
    }
    .stTabs [aria-selected="true"] {
        color: #065f46 !important;
        font-weight: 700 !important;
        border-bottom: 2.5px solid #059669 !important;
        background-color: transparent !important;
    }
    
    /* Clean Cards for Materials */
    .material-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .material-card-best {
        background: #ffffff;
        border: 1.5px solid #059669;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 3px 10px rgba(5, 150, 105, 0.08);
    }
    
    /* Section Headings */
    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0f172a;
        margin: 4px 0 12px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Load Reference Data
commodities, materials, features = load_data()

# Category Icons for intuitive visual selection
CATEGORY_ICONS = {
    "Fruits & Vegetables": "🥬",
    "Dairy Products": "🥛",
    "Bakery & Confectionery": "🍞",
    "Grains & Pulses": "🌾",
    "Snacks & Fried Foods": "🍿",
    "Ready-to-Eat (Veg)": "🍲",
    "Spices & Condiments": "🌿",
    "Meat & Poultry": "🥩",
    "Fish & Seafood": "🐟",
    "Eggs & Egg Products": "🥚",
    "Processed Meats": "🥓",
    "Ready-to-Eat (Non-Veg)": "🍗"
}

# Sector Biophysical Defaults for foolproof Custom Entry
SECTOR_DEFAULTS = {
    "Meat & Poultry": {
        "food_type": "non_veg",
        "optimal_temp_c": 2.0,
        "optimal_rh_pct": 90.0,
        "target_otr_range": [5, 25],
        "target_wvtr_range": [2, 6],
        "baseline_shelf_life_days": 8.0,
        "q10": 2.7,
        "spoilage_factors": ["Microbial spoilage (Pseudomonas)", "Myoglobin browning", "TVB-N accumulation"]
    },
    "Fish & Seafood": {
        "food_type": "non_veg",
        "optimal_temp_c": 1.0,
        "optimal_rh_pct": 95.0,
        "target_otr_range": [2, 20],
        "target_wvtr_range": [1, 5],
        "baseline_shelf_life_days": 6.0,
        "q10": 3.0,
        "spoilage_factors": ["TMA / TVB-N amine stench", "Autolytic breakdown", "Psychrophilic bacteria"]
    },
    "Eggs & Egg Products": {
        "food_type": "non_veg",
        "optimal_temp_c": 4.0,
        "optimal_rh_pct": 80.0,
        "target_otr_range": [10, 50],
        "target_wvtr_range": [2, 8],
        "baseline_shelf_life_days": 30.0,
        "q10": 2.2,
        "spoilage_factors": ["Salmonella contamination", "Moisture loss", "Air cell enlargement"]
    },
    "Processed Meats": {
        "food_type": "non_veg",
        "optimal_temp_c": 4.0,
        "optimal_rh_pct": 85.0,
        "target_otr_range": [2, 20],
        "target_wvtr_range": [1, 5],
        "baseline_shelf_life_days": 28.0,
        "q10": 2.3,
        "spoilage_factors": ["Listeria monocytogenes", "Lipid oxidation", "Discoloration"]
    },
    "Ready-to-Eat (Non-Veg)": {
        "food_type": "non_veg",
        "optimal_temp_c": 25.0,
        "optimal_rh_pct": 65.0,
        "target_otr_range": [0.1, 2],
        "target_wvtr_range": [0.1, 1],
        "baseline_shelf_life_days": 365.0,
        "q10": 1.4,
        "spoilage_factors": ["Seal micro-leakage", "Thermal deterioration", "Oxygen ingress rancidity"]
    },
    "Fruits & Vegetables": {
        "food_type": "veg",
        "optimal_temp_c": 10.0,
        "optimal_rh_pct": 90.0,
        "target_otr_range": [2500, 6000],
        "target_wvtr_range": [15, 30],
        "baseline_shelf_life_days": 14.0,
        "q10": 2.2,
        "spoilage_factors": ["Ethylene over-ripening", "Transpiration moisture loss", "Anthracnose fungal rot"]
    },
    "Dairy Products": {
        "food_type": "veg",
        "optimal_temp_c": 4.0,
        "optimal_rh_pct": 85.0,
        "target_otr_range": [5, 30],
        "target_wvtr_range": [1, 5],
        "baseline_shelf_life_days": 10.0,
        "q10": 2.5,
        "spoilage_factors": ["Lactic souring", "Psychrotrophic bacteria", "Lipid oxidation"]
    },
    "Bakery & Confectionery": {
        "food_type": "veg",
        "optimal_temp_c": 22.0,
        "optimal_rh_pct": 60.0,
        "target_otr_range": [20, 100],
        "target_wvtr_range": [4, 15],
        "baseline_shelf_life_days": 7.0,
        "q10": 1.8,
        "spoilage_factors": ["Rhizopus / Penicillium mold", "Starch staling", "Moisture migration"]
    },
    "Grains & Pulses": {
        "food_type": "veg",
        "optimal_temp_c": 25.0,
        "optimal_rh_pct": 50.0,
        "target_otr_range": [50, 200],
        "target_wvtr_range": [2, 8],
        "baseline_shelf_life_days": 365.0,
        "q10": 1.2,
        "spoilage_factors": ["Insect infestation", "Moisture caking", "Mold spores"]
    },
    "Snacks & Fried Foods": {
        "food_type": "veg",
        "optimal_temp_c": 25.0,
        "optimal_rh_pct": 45.0,
        "target_otr_range": [1, 15],
        "target_wvtr_range": [0.5, 3],
        "baseline_shelf_life_days": 180.0,
        "q10": 1.5,
        "spoilage_factors": ["Lipid oxidation / Rancidity", "Moisture absorption", "Loss of crispness"]
    },
    "Ready-to-Eat (Veg)": {
        "food_type": "veg",
        "optimal_temp_c": 25.0,
        "optimal_rh_pct": 65.0,
        "target_otr_range": [0.1, 2],
        "target_wvtr_range": [0.1, 1],
        "baseline_shelf_life_days": 365.0,
        "q10": 1.4,
        "spoilage_factors": ["Seal micro-leakage", "Thermal deterioration", "Oxidation"]
    },
    "Spices & Condiments": {
        "food_type": "veg",
        "optimal_temp_c": 25.0,
        "optimal_rh_pct": 55.0,
        "target_otr_range": [10, 50],
        "target_wvtr_range": [1, 5],
        "baseline_shelf_life_days": 365.0,
        "q10": 1.3,
        "spoilage_factors": ["Essential oil volatilization", "Moisture caking", "Color degradation"]
    }
}

all_categories = list(SECTOR_DEFAULTS.keys())

# ==================== SIDEBAR CONFIGURATION ====================
st.sidebar.markdown("### 🎯 Food & Logistics Setup")

# 1. Clean Simple Selection Mode
input_mode = st.sidebar.radio(
    "Food Selection Mode",
    ["📂 Standard Food Catalog", "✍️ Custom Food Entry"],
    index=0
)

current_commodity = None

if input_mode == "📂 Standard Food Catalog":
    # Category Dropdown
    selected_category = st.sidebar.selectbox(
        "Select Food Category",
        all_categories,
        format_func=lambda x: f"{CATEGORY_ICONS.get(x, '📦')} {x}",
        key="sb_category"
    )
    
    # Filter commodities belonging to this category
    commodities_in_cat = [c for c in commodities if c["category"] == selected_category]
    commodity_options = {c["name"]: c for c in commodities_in_cat}
    
    # Specific Commodity Dropdown (Guaranteed working and synced!)
    selected_food_name = st.sidebar.selectbox(
        "Select Food Commodity",
        list(commodity_options.keys()),
        key="sb_food_item"
    )
    
    current_commodity = commodity_options[selected_food_name]
    detected_diet = current_commodity.get("food_type", "veg")

else:
    # Custom Food Entry Mode
    custom_name = st.sidebar.text_input("Commodity Name", value="Fresh Boneless Chicken Breast")
    
    custom_category = st.sidebar.selectbox(
        "Food Category / Sector",
        all_categories,
        format_func=lambda x: f"{CATEGORY_ICONS.get(x, '📦')} {x}",
        index=0,  # Default to Meat & Poultry
        key="sb_custom_cat"
    )
    
    # Automatically apply biophysical properties of the selected sector!
    defaults = SECTOR_DEFAULTS.get(custom_category, SECTOR_DEFAULTS["Meat & Poultry"])
    detected_diet = defaults["food_type"]
    
    current_commodity = {
        "id": f"custom_{custom_name.lower().replace(' ', '_')}",
        "name": custom_name,
        "category": custom_category,
        "food_type": detected_diet,
        "optimal_temp_c": defaults["optimal_temp_c"],
        "optimal_rh_pct": defaults["optimal_rh_pct"],
        "target_otr_range": defaults["target_otr_range"],
        "target_wvtr_range": defaults["target_wvtr_range"],
        "baseline_shelf_life_days": defaults["baseline_shelf_life_days"],
        "q10": defaults["q10"],
        "spoilage_factors": defaults["spoilage_factors"]
    }

# Display dynamic FSSAI Status Badge right under food selection
if detected_diet == "veg":
    st.sidebar.markdown("""
    <div style="background:#ecfdf5; border:1px solid #a7f3d0; border-radius:8px; padding:7px 12px; margin-bottom:14px; display:flex; align-items:center; gap:8px;">
        <span style="font-size:0.95rem;">🟢</span>
        <div>
            <div style="font-size:0.68rem; color:#047857; font-weight:700; text-transform:uppercase; letter-spacing:0.3px;">FSSAI Classification</div>
            <div style="font-size:0.84rem; color:#065f46; font-weight:700;">Vegetarian Food (Veg)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:8px; padding:7px 12px; margin-bottom:14px; display:flex; align-items:center; gap:8px;">
        <span style="font-size:0.95rem;">🔴</span>
        <div>
            <div style="font-size:0.68rem; color:#b91c1c; font-weight:700; text-transform:uppercase; letter-spacing:0.3px;">FSSAI Classification</div>
            <div style="font-size:0.84rem; color:#991b1b; font-weight:700;">Non-Vegetarian Food (Non-Veg)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")

# 2. Transit & Cold-Chain Logistics Simulation
st.sidebar.markdown("### 🌡️ Transit & Storage Conditions")

optimal_temp = float(current_commodity.get("optimal_temp_c", 4.0))

base_storage_temp = st.sidebar.slider(
    "Storage Temperature (°C)",
    min_value=-5.0,
    max_value=45.0,
    value=optimal_temp,
    step=0.5,
    help="Defaults to recommended storage temperature for the selected food item."
)

# Cold-Chain Failure Simulator Toggle
simulate_breach = st.sidebar.checkbox(
    "🚨 Trigger Cold-Chain Failure (Thermal Abuse)",
    value=False,
    help="Simulates transit refrigeration equipment failure or severe tropical heat spike."
)

if simulate_breach:
    breach_delta = st.sidebar.slider(
        "Thermal Abuse Temperature Spike (+°C)",
        min_value=5.0,
        max_value=25.0,
        value=15.0,
        step=1.0,
        help="Degrees added on top of base storage temperature."
    )
    storage_temp = min(50.0, base_storage_temp + breach_delta)
    st.sidebar.markdown(f"""
    <div style="background:#fee2e2; border:1px solid #fca5a5; border-radius:8px; padding:8px 12px; margin-top:6px;">
        <div style="font-size:0.72rem; color:#991b1b; font-weight:700; text-transform:uppercase;">🚨 Thermal Abuse Active</div>
        <div style="font-size:0.86rem; color:#7f1d1d; font-weight:700;">Spiked Temp: {storage_temp:.1f}°C (+{breach_delta:.0f}°C spike)</div>
    </div>
    """, unsafe_allow_html=True)
else:
    breach_delta = 0.0
    storage_temp = base_storage_temp

# 3. Dedicated Start / Run Button
st.sidebar.markdown("<br>", unsafe_allow_html=True)
run_button = st.sidebar.button("🚀 Run Packaging Analysis", type="primary", use_container_width=True)

# 4. Optional Advanced Tuning (Inside clean expander to eliminate complexity!)
with st.sidebar.expander("⚙️ Advanced Optimization Settings (Optional)", expanded=False):
    priority_mode = st.selectbox(
        "Decision Priority Profile",
        [
            "Balanced (Standard MCDM)",
            "Eco-Conscious / Sustainable",
            "Maximum Shelf-Life & Protection",
            "Cost-Optimized (SME / Rural)",
            "Custom Weight Sliders"
        ]
    )

    custom_weights = None
    if priority_mode == "Custom Weight Sliders":
        w_b = st.slider("Barrier Weight", 0.05, 0.80, 0.40, 0.05)
        w_e = st.slider("Eco Weight", 0.05, 0.80, 0.25, 0.05)
        w_c = st.slider("Cost Weight", 0.05, 0.80, 0.20, 0.05)
        w_s = st.slider("Strength Weight", 0.05, 0.80, 0.15, 0.05)
        total_w = w_b + w_e + w_c + w_s
        custom_weights = {
            "barrier": w_b / total_w,
            "sustainability": w_e / total_w,
            "cost": w_c / total_w,
            "strength": w_s / total_w
        }

    storage_rh = st.slider(
        "Relative Humidity (% RH)",
        min_value=30.0,
        max_value=98.0,
        value=float(current_commodity.get("optimal_rh_pct", 75.0)),
        step=1.0
    )

    enable_active_features = st.checkbox(
        "Include Active Scavengers & Smart Sensors",
        value=True
    )

    batch_volume = st.number_input(
        "Production Batch Size (Units)",
        min_value=1000,
        max_value=1000000,
        value=10000,
        step=5000
    )

# Set defaults if advanced expander untouched
if "priority_mode" not in locals():
    priority_mode = "Balanced (Standard MCDM)"
    custom_weights = None
    storage_rh = float(current_commodity.get("optimal_rh_pct", 75.0))
    enable_active_features = True
    batch_volume = 10000

# ==================== RUN SCIENTIFIC RECOMMENDATION ENGINES ====================
rec_result = recommend_packaging(
    commodity=current_commodity,
    priority_mode=priority_mode.split(" (")[0],
    storage_temp_c=storage_temp,
    storage_rh_pct=storage_rh,
    custom_weights=custom_weights
)

top_recs = rec_result["recommendations"]
best_match = top_recs[0]

# Calculate shelf life under current storage condition
shelf_life = simulate_shelf_life(
    commodity=current_commodity,
    material=best_match["material"],
    active_features_enabled=enable_active_features,
    storage_temp_c=storage_temp,
    storage_rh_pct=storage_rh
)

# Also calculate shelf life under normal base temperature for direct before/after comparison!
shelf_life_normal = simulate_shelf_life(
    commodity=current_commodity,
    material=best_match["material"],
    active_features_enabled=enable_active_features,
    storage_temp_c=base_storage_temp,
    storage_rh_pct=storage_rh
)

lca = compute_lca_metrics(
    material=best_match["material"],
    production_volume_units=batch_volume
)

# ==================== MAIN PAGE: EXECUTIVE HEADER ====================
is_veg = current_commodity.get("food_type", "veg").lower() == "veg"
fssai_badge = """<span class="pill-veg">🟢 FSSAI VEGETARIAN</span>""" if is_veg else """<span class="pill-nonveg">🔴 FSSAI NON-VEGETARIAN</span>"""
mode_name = "User Custom Food" if "custom" in current_commodity.get("id", "") else "MoFPI Catalog"

st.markdown(f"""
<div class="executive-header">
    <div class="header-top-row">
        <div class="header-badges-group">
            <span class="pill-gov">🇮🇳 MoFPI | SIH26236</span>
            {fssai_badge}
            <span class="pill-meta">{CATEGORY_ICONS.get(current_commodity['category'], '📦')} {current_commodity['category']}</span>
            <span class="pill-meta">⚡ {mode_name}</span>
        </div>
        <div style="font-size:0.75rem; color:#cbd5e1; font-weight:600;">Standard ISO 22000 & IS 9845 Aligned</div>
    </div>
    <h1>AI Intelligent Food Packaging Material Recommendation System</h1>
    <p>Biophysical property matching, kinetic shelf-life simulation, and bio-circular LCA for <b>{current_commodity['name']}</b>.</p>
</div>
""", unsafe_allow_html=True)

# HIGH-CONTRAST BOLD ALERT FOR COLD-CHAIN BREACH
if simulate_breach:
    loss_days = round(max(0.0, shelf_life_normal["estimated_days"] - shelf_life["estimated_days"]), 1)
    loss_pct = round((loss_days / max(0.1, shelf_life_normal["estimated_days"])) * 100, 1)
    
    st.markdown(f"""
    <div style="background:#fef2f2; border:1.5px solid #f87171; border-radius:12px; padding:16px 20px; margin-bottom:20px; display:flex; align-items:center; justify-content:space-between; box-shadow:0 2px 8px rgba(239, 68, 68, 0.08);">
        <div style="display:flex; align-items:center; gap:14px;">
            <span style="font-size:1.8rem;">🚨</span>
            <div>
                <div style="font-size:0.92rem; font-weight:800; color:#991b1b; text-transform:uppercase; letter-spacing:0.5px;">Cold-Chain Thermal Abuse Failure Active</div>
                <div style="font-size:0.88rem; color:#7f1d1d; margin-top:3px;">
                    Transit temperature spiked to <b>{storage_temp:.1f}°C</b> (+{breach_delta:.0f}°C breach above base {base_storage_temp:.1f}°C).
                    Kinetic degradation accelerated by <b>{shelf_life['temperature_impact_factor']}x</b>!
                </div>
            </div>
        </div>
        <div style="text-align:right; background:#fee2e2; border:1px solid #fca5a5; padding:8px 16px; border-radius:8px;">
            <div style="font-size:0.70rem; color:#991b1b; font-weight:700; text-transform:uppercase;">Shelf-Life Loss</div>
            <div style="font-size:1.15rem; font-weight:800; color:#dc2626;">-{loss_pct}% (-{loss_days}d lost)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== MINIMAL KPI METRIC ROW ====================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-header">
            <span class="kpi-title">Top Material Match</span>
            <span class="kpi-icon-pill">🎯 Rank #1</span>
        </div>
        <div class="kpi-value">{best_match['overall_score']}%</div>
        <div>
            <span class="kpi-badge kpi-badge-green">{best_match['material']['name'].split('/')[0].strip()}</span>
        </div>
        <div class="kpi-caption">Thickness: {best_match['material']['thickness_um']} µm • {best_match['material']['category']}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if simulate_breach:
        shelf_badge = f"""<span class="kpi-badge kpi-badge-red">🚨 -{loss_pct}% Thermal Crash</span>"""
        shelf_caption = f"""Crashed from {shelf_life_normal['estimated_days']}d at {base_storage_temp:.1f}°C to {shelf_life['estimated_days']}d at {storage_temp:.1f}°C"""
    else:
        shelf_badge = f"""<span class="kpi-badge kpi-badge-green">+{shelf_life['active_enhancement_gain_days']}d Smart Gain</span>"""
        shelf_caption = f"""Baseline: {shelf_life['baseline_days']}d at recommended {base_storage_temp:.1f}°C"""
        
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-header">
            <span class="kpi-title">Predicted Shelf Life</span>
            <span class="kpi-icon-pill">⏱️ Shelf Life</span>
        </div>
        <div class="kpi-value">{shelf_life['estimated_days']} <span style="font-size:1.05rem;font-weight:600;color:#64748b;">Days</span></div>
        <div>
            {shelf_badge}
        </div>
        <div class="kpi-caption">{shelf_caption}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-header">
            <span class="kpi-title">Carbon Avoidance</span>
            <span class="kpi-icon-pill">🍃 Eco LCA</span>
        </div>
        <div class="kpi-value">{lca['co2_reduction_pct']}%</div>
        <div>
            <span class="kpi-badge kpi-badge-green">{lca['co2_saved_kg']} kg CO₂ Diverted</span>
        </div>
        <div class="kpi-caption">Batch: {batch_volume:,} units vs fossil plastic</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-header">
            <span class="kpi-title">Unit Material Cost</span>
            <span class="kpi-icon-pill">🏷️ Pricing</span>
        </div>
        <div class="kpi-value">₹{best_match['material']['cost_per_sqm_inr']} <span style="font-size:0.95rem;font-weight:600;color:#64748b;">/ m²</span></div>
        <div>
            <span class="kpi-badge kpi-badge-blue">{'100% Compostable' if best_match['material']['biodegradable'] else 'Circular Recyclable'}</span>
        </div>
        <div class="kpi-caption">FSSAI IS 9845 Food Safe Certified</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# ==================== MINIMALIST INTERACTIVE TABS ====================
tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 Material Recommendations",
    "⏳ Kinetic Shelf-Life & Sensors",
    "🌱 LCA & Environmental Impact",
    "📄 Dossier & Export"
])

# ----------------- TAB 1: RECOMMENDATIONS -----------------
with tab1:
    col_left, col_right = st.columns([1.15, 0.85])
    
    with col_left:
        st.markdown(f"<div class='section-title'>🏆 Recommended Packaging Solutions for {current_commodity['name']}</div>", unsafe_allow_html=True)
        
        for idx, rec in enumerate(top_recs[:3]):
            mat = rec["material"]
            is_best = idx == 0
            card_class = "material-card-best" if is_best else "material-card"
            badge_text = "⭐ Top Recommendation" if is_best else f"Alternative #{idx+1}"
            badge_bg = "#059669" if is_best else "#64748b"
            
            st.markdown(f"""
            <div class="{card_class}">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="background:{badge_bg}; color:white; padding:3px 10px; border-radius:6px; font-size:0.72rem; font-weight:700;">{badge_text}</span>
                    <span style="font-size:1.15rem; font-weight:800; color:{'#059669' if is_best else '#334155'};">Score: {rec['overall_score']}%</span>
                </div>
                <div style="font-size:1.05rem; font-weight:700; color:#0f172a; margin-bottom:4px;">{mat['name']}</div>
                <div style="font-size:0.82rem; color:#64748b; margin-bottom:10px;">
                    <b>Class:</b> {mat['category']} &nbsp;|&nbsp; <b>Thickness:</b> {mat['thickness_um']} µm &nbsp;|&nbsp; <b>Cost:</b> ₹{mat['cost_per_sqm_inr']}/m²
                </div>
                <div style="display:flex; flex-wrap:wrap; gap:8px; font-size:0.80rem; color:#334155; background:#f8fafc; padding:8px 12px; border-radius:8px; border:1px solid #f1f5f9;">
                    <span>🛡️ OTR: <b>{mat['otr']} cc</b></span>
                    <span>💧 WVTR: <b>{mat['wvtr']} g</b></span>
                    <span>💪 Tensile: <b>{mat['tensile_strength_mpa']} MPa</b></span>
                    <span>🌿 <b>{'100% Compostable' if mat['biodegradable'] else 'Recyclable'}</b></span>
                </div>
                <div style="font-size:0.80rem; color:#64748b; margin-top:8px; line-height:1.45;"><i>{mat['notes']}</i></div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='section-title'>🎯 Multi-Attribute Decision Radar</div>", unsafe_allow_html=True)
        categories_radar = ['Barrier Protection', 'Sustainability', 'Cost Score', 'Tensile Strength']
        fig_radar = go.Figure()
        
        radar_palettes = [
            {'line': '#059669', 'fill': 'rgba(5, 150, 105, 0.16)', 'prefix': '⭐ Top: '},
            {'line': '#4f46e5', 'fill': 'rgba(79, 70, 229, 0.08)', 'prefix': '#2: '},
            {'line': '#64748b', 'fill': 'rgba(100, 116, 139, 0.05)', 'prefix': '#3: '}
        ]
        
        for i, rec in enumerate(top_recs[:3]):
            b = rec["breakdown"]
            short_name = rec['material']['name'].split('/')[0].strip()
            fig_radar.add_trace(go.Scatterpolar(
                r=[b['barrier_score'], b['sustainability_score'], b['cost_score'], b['mechanical_score']],
                theta=categories_radar,
                fill='toself',
                name=f"{radar_palettes[i]['prefix']}{short_name}",
                line=dict(color=radar_palettes[i]['line'], width=2.5 if i == 0 else 1.8),
                fillcolor=radar_palettes[i]['fill'],
                marker=dict(size=6 if i == 0 else 4, color=radar_palettes[i]['line']),
                hovertemplate="<b>%{theta}</b>: %{r:.0f}%<extra>%{fullData.name}</extra>"
            ))
            
        fig_radar.update_layout(
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(
                    visible=True, 
                    range=[0, 100], 
                    tickfont=dict(size=9, color="#94a3b8"), 
                    gridcolor="#e2e8f0",
                    linecolor="#cbd5e1"
                ),
                angularaxis=dict(
                    tickfont=dict(size=10, color="#334155", family="Plus Jakarta Sans"), 
                    gridcolor="#e2e8f0",
                    linecolor="#cbd5e1"
                )
            ),
            showlegend=True,
            legend=dict(
                orientation="h", 
                yanchor="top", 
                y=-0.14, 
                xanchor="center", 
                x=0.5, 
                font=dict(size=10, family="Plus Jakarta Sans"),
                bgcolor="rgba(255,255,255,0.7)",
                bordercolor="#f1f5f9",
                borderwidth=1
            ),
            margin=dict(l=35, r=35, t=15, b=45),
            height=330,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # Barrier Comparison against Target
    st.markdown("---")
    st.markdown("<div class='section-title'>🛡️ Barrier Permeability vs Critical Targets</div>", unsafe_allow_html=True)
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        otr_names = [r["material"]["name"].split('/')[0].strip() for r in top_recs[:4]]
        otr_vals = [r["material"]["otr"] for r in top_recs[:4]]
        otr_colors = ['#0d9488' if idx == 0 else '#94a3b8' for idx in range(len(otr_names))]
        
        fig_otr = go.Figure(data=[
            go.Bar(
                name='Material OTR', 
                x=otr_names, 
                y=otr_vals, 
                marker_color=otr_colors, 
                marker_line_width=0,
                marker_cornerradius=5,
                hovertemplate="<b>%{x}</b><br>OTR: %{y:,.1f} cc/m²·day·atm<extra></extra>"
            )
        ])
        fig_otr.add_hline(
            y=current_commodity["target_otr_range"][1],
            line_dash="dot",
            annotation_text=f"Max Target ({current_commodity['target_otr_range'][1]} cc)",
            annotation_position="top right",
            annotation_font=dict(size=10, color="#f43f5e", family="Plus Jakarta Sans"),
            line_color="#f43f5e",
            line_width=1.5
        )
        fig_otr.update_layout(
            title=dict(text="Oxygen Transmission Rate (OTR cc/m²·day·atm) [Log Scale]", font=dict(size=12, color="#334155", family="Plus Jakarta Sans")),
            yaxis_type="log",
            margin=dict(l=20, r=20, t=35, b=20),
            height=280,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickfont=dict(size=9, color="#475569")),
            yaxis=dict(gridcolor="#f1f5f9", tickfont=dict(size=9, color="#94a3b8"))
        )
        st.plotly_chart(fig_otr, use_container_width=True)

    with col_b2:
        wvtr_vals = [r["material"]["wvtr"] for r in top_recs[:4]]
        wvtr_colors = ['#059669' if idx == 0 else '#94a3b8' for idx in range(len(otr_names))]
        
        fig_wvtr = go.Figure(data=[
            go.Bar(
                name='Material WVTR', 
                x=otr_names, 
                y=wvtr_vals, 
                marker_color=wvtr_colors, 
                marker_line_width=0,
                marker_cornerradius=5,
                hovertemplate="<b>%{x}</b><br>WVTR: %{y:,.1f} g/m²·day<extra></extra>"
            )
        ])
        fig_wvtr.add_hline(
            y=current_commodity["target_wvtr_range"][1],
            line_dash="dot",
            annotation_text=f"Max Target ({current_commodity['target_wvtr_range'][1]} g)",
            annotation_position="top right",
            annotation_font=dict(size=10, color="#f43f5e", family="Plus Jakarta Sans"),
            line_color="#f43f5e",
            line_width=1.5
        )
        fig_wvtr.update_layout(
            title=dict(text="Water Vapor Transmission Rate (WVTR g/m²·day)", font=dict(size=12, color="#334155", family="Plus Jakarta Sans")),
            margin=dict(l=20, r=20, t=35, b=20),
            height=280,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickfont=dict(size=9, color="#475569")),
            yaxis=dict(gridcolor="#f1f5f9", tickfont=dict(size=9, color="#94a3b8"))
        )
        st.plotly_chart(fig_wvtr, use_container_width=True)

# ----------------- TAB 2: SHELF LIFE & SENSORS -----------------
with tab2:
    st.markdown("<div class='section-title'>⏳ Arrhenius Kinetic Spoilage Modeling & Halochromic Freshness Sensing</div>", unsafe_allow_html=True)
    
    col_k1, col_k2 = st.columns([1.2, 0.8])
    with col_k1:
        curve_df = pd.DataFrame(shelf_life["quality_curve"])
        
        sim_day = st.slider(
            "Inspect Day Along Kinetic Timeline",
            0,
            int(shelf_life["estimated_days"] * 1.3),
            int(min(shelf_life["estimated_days"] * 0.5, 10))
        )
        day_stat = next((d for d in shelf_life["quality_curve"] if d["day"] == sim_day), shelf_life["quality_curve"][-1])
        q_val = day_stat["quality_index"]
        
        # Determine status & sensor color
        if q_val >= 70:
            sensor_color = "#4f46e5"  # Anthocyanin Indigo
            status_text = "SAFE & FRESH"
            status_color = "#059669"
            status_bg = "#ecfdf5"
            status_border = "#a7f3d0"
            tvbn = round(8.0 + (100 - q_val) * 0.2, 1)
        elif q_val >= 45:
            sensor_color = "#0d9488"  # Soft Sage Teal
            status_text = "MARGINAL (Consume Soon)"
            status_color = "#d97706"
            status_bg = "#fffbeb"
            status_border = "#fde68a"
            tvbn = round(15.0 + (70 - q_val) * 0.4, 1)
        else:
            sensor_color = "#f59e0b"  # Warm Acid Shift Amber
            status_text = "SPOILED / UNFIT"
            status_color = "#dc2626"
            status_bg = "#fef2f2"
            status_border = "#fecaca"
            tvbn = round(26.0 + (45 - q_val) * 0.6, 1)

        fig_curve = go.Figure()
        fig_curve.add_trace(go.Scatter(
            x=curve_df["day"],
            y=curve_df["quality_index"],
            mode="lines",
            line=dict(color="#059669", width=3, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(5, 150, 105, 0.06)",
            name="Quality Index",
            hovertemplate="Day %{x}: <b>%{y:.1f}%</b> Quality<extra></extra>"
        ))
        # Active inspection day marker
        fig_curve.add_trace(go.Scatter(
            x=[sim_day],
            y=[q_val],
            mode="markers",
            marker=dict(size=12, color=sensor_color, line=dict(color="#ffffff", width=2.5)),
            name=f"Inspected Day {sim_day}",
            hovertemplate=f"Day {sim_day} Inspection: <b>{q_val}%</b> Quality<extra></extra>"
        ))
        # Guidelines
        fig_curve.add_hline(
            y=70, 
            line_dash="dot", 
            line_color="#10b981", 
            line_width=1.5, 
            annotation_text="Fresh Limit (≥70%)", 
            annotation_font=dict(size=10, color="#059669", family="Plus Jakarta Sans"),
            annotation_position="top left"
        )
        fig_curve.add_hline(
            y=45, 
            line_dash="dot", 
            line_color="#f59e0b", 
            line_width=1.5, 
            annotation_text="Marginal Limit (45%)", 
            annotation_font=dict(size=10, color="#d97706", family="Plus Jakarta Sans"),
            annotation_position="bottom left"
        )
        
        curve_title = f"Quality Retention Curve at {storage_temp:.1f}°C"
        if simulate_breach:
            curve_title += f" (🚨 Thermal Abuse +{breach_delta:.0f}°C Spike!)"
            
        fig_curve.update_layout(
            title=dict(text=curve_title, font=dict(size=13, color="#334155", family="Plus Jakarta Sans")),
            xaxis_title="Storage Duration (Days)",
            yaxis_title="Quality Index (%)",
            height=330,
            margin=dict(l=20, r=20, t=35, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor="#f1f5f9", tickfont=dict(size=9, color="#64748b")),
            yaxis=dict(range=[0, 105], gridcolor="#f1f5f9", tickfont=dict(size=9, color="#64748b")),
            showlegend=False
        )
        st.plotly_chart(fig_curve, use_container_width=True)

    with col_k2:
        st.markdown("<div class='section-title'>🏷️ Smart Freshness Tag</div>", unsafe_allow_html=True)
        st.caption("Anthocyanin tag reacting to Volatile Basic Nitrogen (TVB-N) & organic acids.")
        
        st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:20px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
            <div style="font-size:0.75rem; color:#64748b; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">On-Pack Smart Tag • Day {sim_day}</div>
            <div style="margin:16px auto; width:84px; height:84px; border-radius:50%; background:{sensor_color}; border:4px solid #ffffff; box-shadow:0 4px 14px rgba(0,0,0,0.12), inset 0 2px 4px rgba(255,255,255,0.4);"></div>
            <div style="font-size:1.25rem; font-weight:800; color:#0f172a;">Quality: {q_val}%</div>
            <div style="display:inline-block; margin-top:4px; font-size:0.80rem; font-weight:700; color:{status_color}; background:{status_bg}; padding:3px 10px; border-radius:9999px; border:1px solid {status_border};">● {status_text}</div>
            <div style="margin-top:12px; font-size:0.78rem; color:#475569; background:#f8fafc; padding:6px 12px; border-radius:8px; border:1px solid #f1f5f9; display:flex; justify-content:space-between;">
                <span>TVB-N Level:</span>
                <b>{tvbn} mg/100g</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div class='section-title'>💡 Compatible Active Enhancements & Sensors</div>", unsafe_allow_html=True)
    
    s_cols = st.columns(len(rec_result["intelligent_features"][:3]))
    for idx, feat in enumerate(rec_result["intelligent_features"][:3]):
        with s_cols[idx]:
            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:14px; height:100%; box-shadow:0 1px 2px rgba(0,0,0,0.02);">
                <div style="font-size:0.72rem; font-weight:700; color:#059669; text-transform:uppercase;">{feat['type']}</div>
                <div style="font-size:0.92rem; font-weight:700; color:#0f172a; margin:4px 0 6px 0;">{feat['name']}</div>
                <div style="font-size:0.78rem; color:#475569; margin-bottom:4px;"><b>Target:</b> {feat['target_hazard']}</div>
                <div style="font-size:0.76rem; color:#64748b; line-height:1.45;">{feat['mechanism']}</div>
                <div style="font-size:0.78rem; font-weight:700; color:#1e293b; margin-top:8px;">Cost: ₹{feat['estimated_cost_inr']} / unit</div>
            </div>
            """, unsafe_allow_html=True)

# ----------------- TAB 3: LCA & SUSTAINABILITY -----------------
with tab3:
    st.markdown("<div class='section-title'>🌱 Life Cycle Assessment (LCA) & Bio-Circularity</div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background:#ecfdf5; border:1px solid #a7f3d0; border-radius:10px; padding:14px 18px; margin-bottom:18px; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div style="font-weight:700; color:#065f46; font-size:1.0rem;">🏅 {lca['eco_tier']}</div>
            <div style="color:#047857; font-size:0.85rem; margin-top:2px;">
                Benchmarked against virgin multi-layer fossil plastic over a batch of <b>{batch_volume:,} units</b>.
            </div>
        </div>
        <div style="text-align:right;">
            <span style="background:#dcfce7; color:#15803d; font-weight:700; font-size:0.78rem; padding:4px 10px; border-radius:9999px; border:1px solid #86efac;">MoFPI Net-Zero Circularity</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_l1, col_l2 = st.columns(2)
    with col_l1:
        bench_val = lca['benchmark_carbon_emissions_kg_co2']
        mat_val = lca['total_carbon_emissions_kg_co2']
        
        fig_carbon = go.Figure(data=[
            go.Bar(
                name='Virgin Fossil Baseline', 
                x=['Fossil Baseline'], 
                y=[bench_val], 
                marker_color='#94a3b8', 
                marker_line_width=0,
                marker_cornerradius=6,
                text=[f"{bench_val:,.1f} kg"],
                textposition='outside',
                textfont=dict(family="Plus Jakarta Sans", size=10, color="#64748b")
            ),
            go.Bar(
                name='Eco Packaging Solution', 
                x=['Eco Packaging'], 
                y=[mat_val], 
                marker_color='#059669', 
                marker_line_width=0,
                marker_cornerradius=6,
                text=[f"{mat_val:,.1f} kg"],
                textposition='outside',
                textfont=dict(family="Plus Jakarta Sans", size=10, color="#059669")
            )
        ])
        fig_carbon.update_layout(
            title=dict(text=f"Lifecycle Carbon Footprint (kg CO₂ eq / {batch_volume:,} units)", font=dict(size=12, color="#334155", family="Plus Jakarta Sans")),
            height=300,
            margin=dict(l=20, r=20, t=35, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(gridcolor="#f1f5f9", tickfont=dict(size=9, color="#94a3b8")),
            xaxis=dict(tickfont=dict(size=10, color="#334155", family="Plus Jakarta Sans")),
            showlegend=False
        )
        st.plotly_chart(fig_carbon, use_container_width=True)

    with col_l2:
        st.markdown("<div class='section-title'>📦 Extended Producer Responsibility (EPR) Scorecard</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:16px; margin-bottom:12px;">
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; font-size:0.82rem;">
                <div style="background:#f8fafc; padding:8px 12px; border-radius:8px; border:1px solid #f1f5f9;">
                    <div style="color:#64748b; font-size:0.72rem; font-weight:600;">TOTAL MATERIAL WEIGHT</div>
                    <div style="font-weight:700; color:#0f172a; font-size:0.95rem;">{lca['total_material_weight_kg']:,} kg</div>
                </div>
                <div style="background:#ecfdf5; padding:8px 12px; border-radius:8px; border:1px solid #a7f3d0;">
                    <div style="color:#047857; font-size:0.72rem; font-weight:600;">NET AVOIDED CARBON</div>
                    <div style="font-weight:700; color:#065f46; font-size:0.95rem;">{lca['co2_saved_kg']:,} kg CO₂</div>
                </div>
                <div style="background:#f8fafc; padding:8px 12px; border-radius:8px; border:1px solid #f1f5f9;">
                    <div style="color:#64748b; font-size:0.72rem; font-weight:600;">FOSSIL PLASTIC REPLACED</div>
                    <div style="font-weight:700; color:#0f172a; font-size:0.95rem;">{lca['plastic_waste_diverted_kg']:,} kg</div>
                </div>
                <div style="background:#f8fafc; padding:8px 12px; border-radius:8px; border:1px solid #f1f5f9;">
                    <div style="color:#64748b; font-size:0.72rem; font-weight:600;">CIRCULAR DISPOSITION</div>
                    <div style="font-weight:700; color:#0f172a; font-size:0.86rem;">{'Compostable (' + str(lca['compostability_days']) + 'd)' if lca['is_biodegradable'] else 'Formal Recycling'}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(1.0, lca['co2_reduction_pct'] / 100.0), text=f"MoFPI Carbon Reduction Target: {lca['co2_reduction_pct']}% Achieved")

# ----------------- TAB 4: DOSSIER & EXPORT -----------------
with tab4:
    st.markdown("<div class='section-title'>📄 Official MoFPI Compliance Dossier & Data Export</div>", unsafe_allow_html=True)
    st.caption("Generate formal compliance certificates and benchmark matrices for regulatory filings, FSSAI compliance, and exporter dossiers.")

    pdf_bytes = generate_pdf_report(
        commodity=current_commodity,
        top_material=best_match,
        active_features=rec_result["intelligent_features"],
        shelf_life_data=shelf_life,
        lca_data=lca
    )

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            label="📥 Download MoFPI Compliance Dossier (PDF)",
            data=pdf_bytes,
            file_name=f"MoFPI_Dossier_{current_commodity.get('id', 'food')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with col_d2:
        export_df = pd.DataFrame([
            {
                "Material": r["material"]["name"],
                "Category": r["material"]["category"],
                "Overall_Score": r["overall_score"],
                "Barrier_Score": r["breakdown"]["barrier_score"],
                "Sustainability_Score": r["breakdown"]["sustainability_score"],
                "Cost_Score": r["breakdown"]["cost_score"],
                "Tensile_Score": r["breakdown"]["mechanical_score"],
                "OTR": r["material"]["otr"],
                "WVTR": r["material"]["wvtr"],
                "Cost_INR_per_sqm": r["material"]["cost_per_sqm_inr"],
                "Biodegradable": r["material"]["biodegradable"]
            }
            for r in top_recs
        ])
        st.download_button(
            label="📊 Export Material Benchmark Matrix (CSV)",
            data=export_df.to_csv(index=False).encode('utf-8'),
            file_name=f"Material_Benchmarks_{current_commodity.get('id', 'food')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    st.markdown("---")
    st.markdown("<div class='section-title'>📋 Parameter Inspection Summary</div>", unsafe_allow_html=True)
    summary_df = pd.DataFrame([
        {"Parameter": "Target Commodity", "Specification": current_commodity["name"]},
        {"Parameter": "Food Category / Sector", "Specification": current_commodity["category"]},
        {"Parameter": "FSSAI Classification", "Specification": "Vegetarian (Green Dot)" if current_commodity.get("food_type") == "veg" else "Non-Vegetarian (Red Dot)"},
        {"Parameter": "Recommended Packaging Solution", "Specification": best_match["material"]["name"]},
        {"Parameter": "Material Classification", "Specification": best_match["material"]["category"]},
        {"Parameter": "Calculated Shelf Life", "Specification": f"{shelf_life['estimated_days']} Days (at {storage_temp:.1f}°C)"},
        {"Parameter": "Baseline Shelf Life Gain", "Specification": f"+{shelf_life['active_enhancement_gain_days']} Days with Smart Add-ons"},
        {"Parameter": "Estimated Material Unit Cost", "Specification": f"₹{best_match['material']['cost_per_sqm_inr']} per m²"},
        {"Parameter": "Carbon Footprint Reduction", "Specification": f"{lca['co2_reduction_pct']}% vs Conventional Fossil Plastic"},
        {"Parameter": "Smart Sensor Integration", "Specification": ", ".join([f["name"] for f in rec_result["intelligent_features"][:2]])}
    ])
    st.dataframe(summary_df, use_container_width=True, hide_index=True)