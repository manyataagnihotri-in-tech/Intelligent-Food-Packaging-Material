# AI-Based Intelligent Food Packaging Material Recommendation System
**Ministry of Food Processing Industries (MoFPI) | Smart India Hackathon (SIH)**  
*Theme: Agriculture, FoodTech & Rural Development*

---

## 🌟 Overview
Post-harvest food loss in India exceeds 30% for perishables, driven by inadequate, static, and non-optimized packaging. This solution is an **AI-driven, Multi-Criteria Decision Making (MCDM) & Kinetic Simulation Platform** designed for food processors, rural MSMEs, and agricultural exporters.

It transforms packaging selection from guesswork into a scientific, multi-dimensional optimization process evaluating:
1. **Biophysical Commodity Properties:** Respiration rate ($R_{O_2}, R_{CO_2}$), moisture sensitivity ($a_w$), transpiration, ethylene ($C_2H_4$) sensitivity, and lipid oxidation vulnerability.
2. **Barrier Engineering:** Oxygen Transmission Rate (OTR), Water Vapor Transmission Rate (WVTR), and $CO_2$ permeability.
3. **Intelligent & Active Systems:** Colorimetric anthocyanin/curcumin pH freshness indicators, Time-Temperature Indicators (TTI), $O_2$/ethylene scavengers, and cryptographic NFC/QR batch traceability.
4. **Bio-Circular Sustainability & LCA:** Biodegradability, compostability days, recyclability, carbon footprint (kg $CO_2$ eq), and MoFPI Extended Producer Responsibility (EPR) alignment.
5. **Kinetic Shelf-Life Modeling:** Modified Arrhenius and $Q_{10}$ temperature acceleration curves.

---

## 🚀 Key Modules & Capabilities

* **🧠 Multi-Criteria Decision Making (MCDM) Engine:** Weights barrier integrity, environmental sustainability, economic affordability, and tensile strength across user selectable profiles (*Balanced, Eco-Conscious, Maximum Protection, SME/Rural Cost-Optimized*).
* **⏳ Arrhenius & $Q_{10}$ Shelf-Life Simulator:** Predicts real-time quality retention curves across varying ambient temperatures (-5°C to 45°C) and RH levels, highlighting shelf-life extensions achieved by active scavengers.
* **🏷️ Halochromic Freshness Sensor Emulator:** Simulates how natural colorimetric anthocyanin indicator labels shift from purple (fresh) to yellow (spoiled) based on volatile amine accumulation.
* **🌱 Life Cycle Assessment (LCA) Calculator:** Measures carbon emissions and landfill diversion compared to conventional virgin non-recyclable multi-layer plastics (PET/LDPE).
* **📄 MoFPI Official Dossier Generator:** Generates a downloadable, printable PDF compliance dossier and technical data sheet via ReportLab.

---

## 📂 Project Architecture

```
Intelligent Food Packaging Material/
├── app.py                      # Interactive Streamlit Web Dashboard
├── requirements.txt            # Core dependencies
├── README.md                   # Documentation & Methodology
├── data/
│   ├── commodities.json        # Biophysical database (Fruits, Dairy, Poultry, Seafood, etc.)
│   ├── materials.json          # Packaging barrier & LCA database (PLA, PHA, EVOH, etc.)
│   └── intelligent_features.json # Smart sensors, scavengers, and indicators
└── engine/
    ├── recommender.py          # TOPSIS & MCDM matching engine
    ├── shelf_life.py           # Arrhenius kinetic shelf-life prediction
    ├── lca.py                  # Carbon footprint & EPR compliance engine
    └── report_generator.py     # PDF compliance dossier generator
```

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Web Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🏛️ Regulatory & Standards Alignment
* **FSSAI (Packaging) Regulations, 2018:** Mandatory overall migration limits & non-toxic food contact surfaces.
* **MoFPI PM-FME Scheme:** Support for rural micro food processing enterprises adopting sustainable packaging.
* **EPR (Extended Producer Responsibility):** Plastic Waste Management Rules compliance.
