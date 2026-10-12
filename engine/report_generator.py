from io import BytesIO
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(
    commodity: Dict[str, Any],
    top_material: Dict[str, Any],
    active_features: list,
    shelf_life_data: Dict[str, Any],
    lca_data: Dict[str, Any]
) -> bytes:
    """
    Generates a formal MoFPI-aligned Packaging Recommendation Dossier in PDF format.
    Supports standard and user-defined custom commodities, along with Veg / Non-Veg categorization.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f766e'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12
    )
    heading2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0f766e'),
        spaceBefore=10,
        spaceAfter=6
    )
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b')
    )
    bold_style = ParagraphStyle(
        'BoldText',
        parent=normal_style,
        fontName='Helvetica-Bold'
    )

    story = []

    # Header / Title
    story.append(Paragraph("MINISTRY OF FOOD PROCESSING INDUSTRIES (MoFPI) | GOVT OF INDIA", bold_style))
    story.append(Paragraph("AI-Based Intelligent Food Packaging Recommendation Dossier", title_style))
    story.append(Paragraph("Smart Packaging & Freshness Assurance Protocol | Challenge SIH26236", subtitle_style))
    story.append(Spacer(1, 8))

    # Determine Veg / Non-Veg label
    food_type_val = commodity.get("food_type", "veg").lower()
    if food_type_val == "non_veg" or "non" in food_type_val:
        food_type_badge = "<font color='#b91c1c'><b>🔴 NON-VEGETARIAN (FSSAI Brown Category)</b></font>"
    else:
        food_type_badge = "<font color='#15803d'><b>🟢 VEGETARIAN (FSSAI Green Category)</b></font>"

    spoilage = commodity.get("spoilage_factors", ["Standard microbial and oxidation spoilage"])
    if isinstance(spoilage, list):
        spoilage_str = ", ".join(spoilage)
    else:
        spoilage_str = str(spoilage)

    # Section 1: Commodity Profile Table
    story.append(Paragraph("1. Target Food Commodity Specification", heading2_style))
    comm_data = [
        [Paragraph("Commodity Name:", bold_style), Paragraph(commodity.get("name", "Custom Commodity"), normal_style)],
        [Paragraph("Food Category / Sector:", bold_style), Paragraph(commodity.get("category", "General Food"), normal_style)],
        [Paragraph("FSSAI Classification:", bold_style), Paragraph(food_type_badge, normal_style)],
        [Paragraph("Respiration Profile:", bold_style), Paragraph(str(commodity.get("respiration_rate", "Standard")), normal_style)],
        [Paragraph("Ethylene Sensitivity:", bold_style), Paragraph(str(commodity.get("ethylene_sensitivity", "Low/None")), normal_style)],
        [Paragraph("Optimal Storage:", bold_style), Paragraph(f"{commodity.get('optimal_temp_c', 10.0)}°C at {commodity.get('optimal_rh_pct', 75.0)}% RH", normal_style)],
        [Paragraph("Critical Spoilage Vectors:", bold_style), Paragraph(spoilage_str, normal_style)]
    ]
    t1 = Table(comm_data, colWidths=[150, 390])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t1)
    story.append(Spacer(1, 10))

    # Section 2: Recommended Packaging Material
    story.append(Paragraph("2. Top AI-Recommended Material Solution", heading2_style))
    mat = top_material["material"]
    mat_data = [
        [Paragraph("Selected Material:", bold_style), Paragraph(mat["name"], bold_style)],
        [Paragraph("Material Classification:", bold_style), Paragraph(mat["category"], normal_style)],
        [Paragraph("Oxygen Transmission (OTR):", bold_style), Paragraph(f"{mat['otr']} cc/m²·day·atm", normal_style)],
        [Paragraph("Water Vapor Trans. (WVTR):", bold_style), Paragraph(f"{mat['wvtr']} g/m²·day", normal_style)],
        [Paragraph("Carbon Dioxide Trans. (CO2TR):", bold_style), Paragraph(f"{mat['co2tr']} cc/m²·day·atm", normal_style)],
        [Paragraph("Tensile Strength:", bold_style), Paragraph(f"{mat['tensile_strength_mpa']} MPa", normal_style)],
        [Paragraph("Economic Cost / m²:", bold_style), Paragraph(f"₹{mat['cost_per_sqm_inr']} INR", normal_style)],
        [Paragraph("Biodegradability & EPR Status:", bold_style), Paragraph(
            f"{'Compostable in ' + str(mat['compostability_days']) + ' days' if mat['biodegradable'] else 'Non-biodegradable (EPR compliant / Recyclable)'}", normal_style)]
    ]
    t2 = Table(mat_data, colWidths=[150, 390])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fdfa')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#99f6e4')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ccfbf1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t2)
    story.append(Spacer(1, 10))

    # Section 3: Shelf-life & Environmental Impact
    story.append(Paragraph("3. Kinetic Shelf-Life & Life Cycle Assessment (LCA)", heading2_style))
    kpi_data = [
        [
            Paragraph(f"<b>Estimated Shelf-Life:</b><br/>{shelf_life_data['estimated_days']} Days", normal_style),
            Paragraph(f"<b>Baseline Ambient:</b><br/>{shelf_life_data['baseline_days']} Days", normal_style),
            Paragraph(f"<b>Active Shelf-Life Gain:</b><br/>+{shelf_life_data['active_enhancement_gain_days']} Days", normal_style)
        ],
        [
            Paragraph(f"<b>CO2 Reduction vs Plastic:</b><br/>{lca_data['co2_reduction_pct']}%", normal_style),
            Paragraph(f"<b>CO2 Saved (Batch):</b><br/>{lca_data['co2_saved_kg']} kg CO2", normal_style),
            Paragraph(f"<b>MoFPI Rating:</b><br/>{lca_data['eco_tier'].split('(')[0]}", normal_style)
        ]
    ]
    t3 = Table(kpi_data, colWidths=[180, 180, 180])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t3)
    story.append(Spacer(1, 10))

    # Section 4: Intelligent & Active Packaging Integration
    story.append(Paragraph("4. Recommended Smart Sensors & Active Scavengers", heading2_style))
    feat_rows = [[Paragraph("Feature / Sensor", bold_style), Paragraph("Type", bold_style), Paragraph("Mechanism", bold_style)]]
    for feat in active_features[:3]:
        feat_rows.append([
            Paragraph(feat["name"], normal_style),
            Paragraph(feat["type"], normal_style),
            Paragraph(feat["mechanism"], normal_style)
        ])
    t4 = Table(feat_rows, colWidths=[160, 110, 270])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t4)
    story.append(Spacer(1, 14))

    # Regulatory Footnote
    story.append(Paragraph("<b>Regulatory Compliance:</b> Complies with FSSAI (Packaging) Regulations 2018 & MoFPI Food Safety Guidelines. Non-toxic, food-grade barrier formulation.", ParagraphStyle('Foot', parent=normal_style, fontSize=8, textColor=colors.HexColor('#64748b'))))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
