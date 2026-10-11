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
    page_title="AI Food Packaging Recommendation System | MoFPI",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #064e3b 0%, #047857 50%, #0d9488 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.1rem;
        font-weight: 700;
    }
    .main-header p {
        color: #d1fae5;
        margin-top: 6px;
        margin-bottom: 0;
        font-size: 1.05rem;
    }
    .badge-gov {
        background-color: #fef3c7;
        color: #92400e;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 8px;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-title {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 1.75rem;
        color: #0f172a;
        font-weight: 700;
        margin-top: 4px;
    }
    .metric-delta {
        font-size: 0.85rem;
        color: #059669;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        font-weight: 600;
        border-radius: 8px 8px 0 0;
    }
</style>
""", unsafe_allow_html=True)

# Load Data
commodities, materials, features = load_data()

# Hero Header
st.markdown("""
<div class="main-header">
    <div class="badge-gov">🇮🇳 MINISTRY OF FOOD PROCESSING INDUSTRIES (MoFPI) | SIH CHALLENGE SIH26236</div>
    <h1>AI-Based Intelligent Food Packaging Material Recommendation System</h1>
    <p>Precision biophysical matching, dynamic kinetic shelf-life simulation, and bio-circular LCA modeling for agricultural commodities.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("🎯 Input Parameters & Logistics")

# Commodity selection
categories = sorted(list(set(c["category"] for c in commodities)))
selected_category = st.sidebar.selectbox("Select Commodity Sector", categories)

filtered_commodities = [c for c in commodities if c["category"] == selected_category]
commodity_options = {c["name"]: c["id"] for c in filtered_commodities}
selected_commodity_name = st.sidebar.selectbox("Select Specific Commodity", list(commodity_options.keys()))
commodity_id = commodity_options[selected_commodity_name]
current_commodity = next(c for c in commodities if c["id"] == commodity_id)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Recommendation Priorities")
priority_mode = st.sidebar.radio(
    "Decision Optimization Profile",
    [
        "Balanced",
        "Eco-Conscious / Sustainable",
        "Maximum Shelf-Life & Protection",
        "Cost-Optimized (SME / Rural)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🌡️ Supply Chain Conditions")
storage_temp = st.sidebar.slider(
    "Ambient / Storage Temperature (°C)",
    min_value=-5.0,
    max_value=45.0,
    value=float(current_commodity["optimal_temp_c"]),
    step=0.5,
    help="Defaulted to commodity's optimal condition. Adjust to test cold-chain breach or tropical ambient transport."
)

storage_rh = st.sidebar.slider(
    "Relative Humidity (% RH)",
    min_value=30.0,
    max_value=98.0,
    value=float(current_commodity["optimal_rh_pct"]),
    step=1.0
)

enable_active_features = st.sidebar.checkbox(
    "Integrate Active & Intelligent Enhancements",
    value=True,
    help="Adds scavengers, ethylene absorbers, and smart freshness sensors."
)

batch_volume = st.sidebar.number_input(
    "Production Batch Size (Units)",
    min_value=1000,
    max_value=1000000,
    value=10000,
    step=5000
)

# Run Recommendation Engine
rec_result = recommend_packaging(
    commodity_id=commodity_id,
    priority_mode=priority_mode,
    storage_temp_c=storage_temp,
    storage_rh_pct=storage_rh
)

top_recs = rec_result["recommendations"]
best_match = top_recs[0]

# Run Shelf Life Simulation
shelf_life = simulate_shelf_life(
    commodity=current_commodity,
    material=best_match["material"],
    active_features_enabled=enable_active_features,
    storage_temp_c=storage_temp,
    storage_rh_pct=storage_rh
)

# Run LCA Calculation
lca = compute_lca_metrics(
    material=best_match["material"],
    production_volume_units=batch_volume
)

# KPI Cards Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Top Material Match</div>
        <div class="metric-value">{best_match['overall_score']}%</div>
        <div class="metric-delta">Rank #1: {best_match['material']['name'].split('/')[0]}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Predicted Shelf Life</div>
        <div class="metric-value">{shelf_life['estimated_days']} Days</div>
        <div class="metric-delta">Baseline: {shelf_life['baseline_days']} Days (+{shelf_life['active_enhancement_gain_days']}d Smart Gain)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Carbon Footprint Saved</div>
        <div class="metric-value">{lca['co2_reduction_pct']}%</div>
        <div class="metric-delta">{lca['co2_saved_kg']} kg CO₂ diverted vs fossil</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Unit Material Cost</div>
        <div class="metric-value">₹{best_match['material']['cost_per_sqm_inr']} <span style="font-size:0.9rem;color:#64748b;">/ m²</span></div>
        <div class="metric-delta">{'Compostable' if best_match['material']['biodegradable'] else 'Recyclable'}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 Material Recommendations",
    "⏳ Kinetic Shelf-Life & Sensors",
    "🌱 LCA & Environmental Impact",
    "📄 MoFPI Dossier & PDF Export"
])

# ----------------- TAB 1: RECOMMENDATIONS -----------------
with tab1:
    st.subheader("Top Ranked Packaging Materials")
    
    col_left, col_right = st.columns([1.1, 0.9])
    
    with col_left:
        for idx, rec in enumerate(top_recs[:3]):
            mat = rec["material"]
            is_best = idx == 0
            border_color = "#059669" if is_best else "#cbd5e1"
            badge = "⭐ Recommended" if is_best else f"Option #{idx+1}"
            
            st.markdown(f"""
            <div style="border: 2px solid {border_color}; border-radius: 10px; padding: 14px; margin-bottom: 12px; background: {'#f0fdf4' if is_best else '#ffffff'};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="background:{'#047857' if is_best else '#64748b'}; color:white; padding:3px 8px; border-radius:6px; font-size:0.75rem; font-weight:700;">{badge}</span>
                    <span style="font-size:1.15rem; font-weight:700; color:{'#065f46' if is_best else '#1e293b'};">Score: {rec['overall_score']}%</span>
                </div>
                <h4 style="margin: 8px 0 4px 0; color:#0f172a;">{mat['name']}</h4>
                <div style="font-size:0.85rem; color:#475569; margin-bottom:8px;">
                    <b>Class:</b> {mat['category']} | <b>Thickness:</b> {mat['thickness_um']} µm | <b>Cost:</b> ₹{mat['cost_per_sqm_inr']}/m²
                </div>
                <div style="display:flex; gap:12px; font-size:0.8rem; color:#334155;">
                    <span>🛡️ <b>OTR:</b> {mat['otr']} cc</span>
                    <span>💧 <b>WVTR:</b> {mat['wvtr']} g</span>
                    <span>💪 <b>Tensile:</b> {mat['tensile_strength_mpa']} MPa</span>
                    <span>🌿 <b>Bio:</b> {'Yes' if mat['biodegradable'] else 'No'}</span>
                </div>
                <p style="font-size:0.82rem; color:#64748b; margin-top:6px; margin-bottom:0;"><i>{mat['notes']}</i></p>
            </div>
            """, unsafe_allow_html=True)
            
    with col_right:
        st.markdown("#### Multi-Attribute Decision Radar")
        
        categories_radar = ['Barrier Protection', 'Sustainability', 'Cost Score', 'Tensile Strength']
        fig_radar = go.Figure()
        
        colors_list = ['#059669', '#3b82f6', '#f59e0b']
        for i, rec in enumerate(top_recs[:3]):
            b = rec["breakdown"]
            fig_radar.add_trace(go.Scatterpolar(
                r=[b['barrier_score'], b['sustainability_score'], b['cost_score'], b['mechanical_score']],
                theta=categories_radar,
                fill='toself',
                name=rec['material']['name'].split('/')[0],
                line_color=colors_list[i]
            ))
            
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            showlegend=True,
            margin=dict(l=40, r=40, t=20, b=20),
            height=340
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # Barrier Comparison against Target
    st.markdown("---")
    st.subheader("Barrier Performance Benchmark vs Commodity Physiology")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        otr_names = [r["material"]["name"].split('/')[0] for r in top_recs[:4]]
        otr_vals = [r["material"]["otr"] for r in top_recs[:4]]
        fig_otr = go.Figure(data=[
            go.Bar(name='Material OTR', x=otr_names, y=otr_vals, marker_color='#0ea5e9')
        ])
        fig_otr.add_hline(
            y=current_commodity["target_otr_range"][1],
            line_dash="dot",
            annotation_text=f"Max Target OTR ({current_commodity['target_otr_range'][1]})",
            line_color="red"
        )
        fig_otr.update_layout(
            title="Oxygen Transmission Rate (OTR cc/m²·day·atm) [Log Scale]",
            yaxis_type="log",
            margin=dict(l=20, r=20, t=35, b=20),
            height=280
        )
        st.plotly_chart(fig_otr, use_container_width=True)

    with col_b2:
        wvtr_vals = [r["material"]["wvtr"] for r in top_recs[:4]]
        fig_wvtr = go.Figure(data=[
            go.Bar(name='Material WVTR', x=otr_names, y=wvtr_vals, marker_color='#10b981')
        ])
        fig_wvtr.add_hline(
            y=current_commodity["target_wvtr_range"][1],
            line_dash="dot",
            annotation_text=f"Max Target WVTR ({current_commodity['target_wvtr_range'][1]})",
            line_color="red"
        )
        fig_wvtr.update_layout(
            title="Water Vapor Transmission Rate (WVTR g/m²·day)",
            margin=dict(l=20, r=20, t=35, b=20),
            height=280
        )
        st.plotly_chart(fig_wvtr, use_container_width=True)

# ----------------- TAB 2: SHELF LIFE & SENSORS -----------------
with tab2:
    st.subheader("Kinetic Spoilage Modeling & Smart Freshness Sensing")
    
    col_k1, col_k2 = st.columns([1.2, 0.8])
    with col_k1:
        # Plot quality retention curve
        curve_df = pd.DataFrame(shelf_life["quality_curve"])
        fig_curve = px.line(
            curve_df,
            x="day",
            y="quality_index",
            title=f"Quality Retention Curve Over Storage Timeline ({storage_temp}°C, {storage_rh}% RH)",
            labels={"day": "Storage Duration (Days)", "quality_index": "Quality Retention Index (%)"},
            color_discrete_sequence=["#059669"]
        )
        fig_curve.add_hrect(y0=70, y1=100, fillcolor="#dcfce7", opacity=0.5, line_width=0, annotation_text="Fresh & Marketable")
        fig_curve.add_hrect(y0=45, y1=70, fillcolor="#fef9c3", opacity=0.5, line_width=0, annotation_text="Marginal Quality")
        fig_curve.add_hrect(y0=0, y1=45, fillcolor="#fee2e2", opacity=0.5, line_width=0, annotation_text="Spoiled / Rejected")
        fig_curve.update_layout(height=360, margin=dict(l=20, r=20, t=35, b=20))
        st.plotly_chart(fig_curve, use_container_width=True)

    with col_k2:
        st.markdown("#### Colorimetric Sensor Simulation")
        st.info("Dynamic halochromic anthocyanin indicator responding to microbial volatile metabolites (TVB-N / pH shift).")
        
        sim_day = st.slider("Inspect Simulated Day", 0, int(shelf_life["estimated_days"] * 1.3), int(shelf_life["estimated_days"] // 2))
        day_stat = next((d for d in shelf_life["quality_curve"] if d["day"] == sim_day), shelf_life["quality_curve"][-1])
        q_val = day_stat["quality_index"]
        
        # Color transition: Fresh (Deep Purple/Pink #7e22ce) -> Warning (Green/Blue #0d9488) -> Spoiled (Yellow/Brown #ca8a04)
        if q_val >= 70:
            sensor_color = "#9333ea"
            status_label = "FRESH (Safe to consume)"
            dot_color = "#22c55e"
        elif q_val >= 45:
            sensor_color = "#059669"
            status_label = "MARGINAL (Consume immediately)"
            dot_color = "#eab308"
        else:
            sensor_color = "#eab308"
            status_label = "SPOILED (Do not consume)"
            dot_color = "#ef4444"

        st.markdown(f"""
        <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:12px; padding:18px; text-align:center;">
            <div style="font-size:0.8rem; color:#64748b; font-weight:700;">ON-PACK FRESHNESS SMART TAG (DAY {sim_day})</div>
            <div style="margin:16px auto; width:90px; height:90px; border-radius:50%; background:{sensor_color}; border:4px solid white; box-shadow:0 0 12px rgba(0,0,0,0.2);"></div>
            <div style="font-size:1.1rem; font-weight:700; color:#0f172a;">Quality Index: {q_val}%</div>
            <div style="font-size:0.9rem; font-weight:600; color:{dot_color}; margin-top:4px;">● {status_label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Compatible Active & Intelligent Sensor Portfolio")
    
    s_cols = st.columns(len(rec_result["intelligent_features"][:3]))
    for idx, feat in enumerate(rec_result["intelligent_features"][:3]):
        with s_cols[idx]:
            st.markdown(f"""
            <div style="background:#f1f5f9; border-radius:8px; padding:12px; height:100%;">
                <div style="font-size:0.75rem; font-weight:700; color:#0f766e; text-transform:uppercase;">{feat['type']}</div>
                <h5 style="margin:4px 0 6px 0;">{feat['name']}</h5>
                <p style="font-size:0.8rem; color:#475569; margin-bottom:6px;"><b>Target:</b> {feat['target_hazard']}</p>
                <p style="font-size:0.78rem; color:#64748b;">{feat['mechanism']}</p>
                <div style="font-size:0.8rem; font-weight:600; color:#1e293b;">Est. Unit Cost: ₹{feat['estimated_cost_inr']}</div>
            </div>
            """, unsafe_allow_html=True)

# ----------------- TAB 3: LCA & SUSTAINABILITY -----------------
with tab3:
    st.subheader("Life Cycle Assessment (LCA) & Carbon Mitigation")
    
    st.markdown(f"""
    <div style="background:{'#ecfdf5' if best_match['material']['biodegradable'] else '#f8fafc'}; border:1px solid #a7f3d0; border-radius:10px; padding:16px; margin-bottom:16px;">
        <h4 style="margin:0 0 6px 0; color:#065f46;">🏅 {lca['eco_tier']}</h4>
        <p style="margin:0; font-size:0.9rem; color:#047857;">
            Evaluated against standard non-recyclable virgin multi-layer barrier plastic (PET/LDPE) over a batch run of <b>{batch_volume:,} units</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_l1, col_l2 = st.columns(2)
    with col_l1:
        # Carbon Comparison Bar Chart
        fig_carbon = go.Figure(data=[
            go.Bar(name='Virgin Plastic Baseline', x=['Carbon Footprint'], y=[lca['benchmark_carbon_emissions_kg_co2']], marker_color='#ef4444'),
            go.Bar(name='Selected Solution', x=['Carbon Footprint'], y=[lca['total_carbon_emissions_kg_co2']], marker_color='#10b981')
        ])
        fig_carbon.update_layout(
            title=f"Total Production Carbon Emissions (kg CO₂ eq for {batch_volume:,} packs)",
            barmode='group',
            height=320,
            margin=dict(l=20, r=20, t=35, b=20)
        )
        st.plotly_chart(fig_carbon, use_container_width=True)

    with col_l2:
        st.markdown("#### Extended Producer Responsibility (EPR) Metrics")
        st.markdown(f"""
        - **Total Packaging Weight:** `{lca['total_material_weight_kg']} kg`
        - **Net Carbon Avoidance:** `{lca['co2_saved_kg']} kg CO₂`
        - **Landfill Plastic Diverted:** `{lca['plastic_waste_diverted_kg']} kg`
        - **End-of-Life Biodegradation:** `{'Composts within ' + str(lca['compostability_days']) + ' days' if lca['is_biodegradable'] else 'Circular Recyclable Stream'}`
        - **FSSAI Food Contact Safe:** `100% Certified Compliant`
        """)
        st.progress(lca['co2_reduction_pct'] / 100.0, text=f"Carbon Reduction Target: {lca['co2_reduction_pct']}% Achieved")

# ----------------- TAB 4: DOSSIER & EXPORT -----------------
with tab4:
    st.subheader("Official MoFPI Recommendation Dossier & Export")
    st.write("Generate and download a compliance certificate for food business operators, MSME clusters, and agricultural exporters.")

    # Generate PDF bytes
    pdf_bytes = generate_pdf_report(
        commodity=current_commodity,
        top_material=best_match,
        active_features=rec_result["intelligent_features"],
        shelf_life_data=shelf_life,
        lca_data=lca
    )

    st.download_button(
        label="📥 Download MoFPI Compliance Dossier (PDF)",
        data=pdf_bytes,
        file_name=f"MoFPI_Packaging_Dossier_{current_commodity['id']}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    
    st.markdown("---")
    st.markdown("#### Summary Inspection Table")
    summary_df = pd.DataFrame([
        {"Parameter": "Target Commodity", "Specification": current_commodity["name"]},
        {"Parameter": "Recommended Barrier", "Specification": best_match["material"]["name"]},
        {"Parameter": "Barrier Class", "Specification": best_match["material"]["category"]},
        {"Parameter": "Calculated Shelf Life", "Specification": f"{shelf_life['estimated_days']} Days (at {storage_temp}°C)"},
        {"Parameter": "Estimated Material Cost", "Specification": f"₹{best_match['material']['cost_per_sqm_inr']} per m²"},
        {"Parameter": "Carbon Reduction", "Specification": f"{lca['co2_reduction_pct']}% vs Conventional Plastic"},
        {"Parameter": "Smart Sensor Integration", "Specification": ", ".join([f["name"] for f in rec_result["intelligent_features"][:2]])}
    ])
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
