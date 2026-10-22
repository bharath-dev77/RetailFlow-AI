import os
import sys
import json
import pandas as pd
import streamlit as st

# Setup backend import paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import database, analyzer

# Initialize database
database.init_db()

st.set_page_config(
    page_title="Smart Environmental Impact Analyzer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #065F46;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.2rem;
    }
    .risk-safe {
        color: #059669;
        font-weight: bold;
    }
    .risk-watch {
        color: #D97706;
        font-weight: bold;
    }
    .risk-hazard {
        color: #DC2626;
        font-weight: bold;
    }
    .metric-box {
        background-color: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=400&q=80", use_container_width=True)
    st.title("🌍 EcoAnalyzer AI")
    st.caption("Open Source Environmental Analytics")
    st.markdown("---")
    st.write("**Framework:** EcoAnalyzer AI Engine")
    st.write("**Environment:** Real-Time Monitoring")
    
    
    st.markdown("---")
    
    st.write("🌿 **System Status:** Active")
    st.write("⚡ **AI Mode:** Free-Tier Heuristic / Gemini Ready")
    st.caption("100% Free & Open-Source Stack")

# App Header
st.markdown("<div class='main-title'>🌍 Smart Environmental Impact Analyzer</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>An AI-assisted educational and analytical tool for transforming complex industrial pollution datasets into organized predictive risk summaries.</div>", unsafe_allow_html=True)

# Navigation Tabs
tab_overview, tab_input, tab_analysis, tab_history, tab_about = st.tabs([
    "🌿 Regional Overview",
    "📥 Data Input & CSV Upload",
    "📊 AI Impact Analysis",
    "📜 History & Comparison",
    "ℹ️ About & Guide"
])

# -------------------------------------------------------------
# TAB 1: REGIONAL OVERVIEW
# -------------------------------------------------------------
with tab_overview:
    st.subheader("Monitored Industrial Regions & Baseline Metrics")
    regions = database.get_all_regions()
    
    if regions:
        df_regions = pd.DataFrame(regions)
        
        # Summary KPI Cards
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Monitored Regions", len(regions))
        avg_pm25 = df_regions["pm2_5"].mean()
        c2.metric("Avg PM2.5 Level", f"{avg_pm25:.1f} µg/m³", delta="Air Hazard" if avg_pm25 > 60 else "Safe", delta_color="inverse")
        avg_tds = df_regions["water_tds"].mean()
        c3.metric("Avg Water TDS", f"{avg_tds:.0f} mg/L", delta="Saline / Polluted" if avg_tds > 1000 else "Normal", delta_color="inverse")
        high_risk_count = sum(1 for r in regions if r["industrial_density"] in ["High", "Very High"])
        c4.metric("High Industrial Zones", high_risk_count)
        
        st.markdown("### 📍 Regional Geographic Clusters")
        map_data = df_regions[["latitude", "longitude"]].copy()
        st.map(map_data, zoom=7)
        
        st.markdown("### 📋 Detailed Environmental Parameters")
        display_cols = ["name", "latitude", "longitude", "pm2_5", "pm10", "water_ph", "water_tds", "water_do", "chromium_ppm", "industrial_density"]
        st.dataframe(df_regions[display_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No regions registered in database.")

# -------------------------------------------------------------
# TAB 2: DATA INPUT & CSV UPLOAD
# -------------------------------------------------------------
with tab_input:
    st.subheader("Regional Environmental Data Ingestion")
    st.write("Upload a CSV/JSON file of sensor readings or manually specify parameters for a new industrial cluster.")
    
    input_mode = st.radio("Choose Input Method:", ["Select from Pre-Loaded Regions", "Upload CSV Dataset", "Manual Coordinate & Metric Entry"], horizontal=True)
    
    selected_metrics = None
    
    if input_mode == "Select from Pre-Loaded Regions":
        regions = database.get_all_regions()
        reg_names = [r["name"] for r in regions]
        chosen_name = st.selectbox("Select Target Cluster:", reg_names)
        chosen_reg = next(r for r in regions if r["name"] == chosen_name)
        selected_metrics = {
            "region_name": chosen_reg["name"],
            "latitude": chosen_reg["latitude"],
            "longitude": chosen_reg["longitude"],
            "pm2_5": chosen_reg["pm2_5"],
            "pm10": chosen_reg["pm10"],
            "so2": chosen_reg["so2"],
            "no2": chosen_reg["no2"],
            "water_ph": chosen_reg["water_ph"],
            "water_tds": chosen_reg["water_tds"],
            "water_do": chosen_reg["water_do"],
            "water_bod": chosen_reg["water_bod"],
            "lead_ppm": chosen_reg["lead_ppm"],
            "chromium_ppm": chosen_reg["chromium_ppm"],
            "industrial_density": chosen_reg["industrial_density"]
        }
        st.success(f"Selected: **{chosen_reg['name']}** (Lat: {chosen_reg['latitude']}, Lon: {chosen_reg['longitude']})")
        
    elif input_mode == "Upload CSV Dataset":
        st.info("Download sample CSV format or upload your custom regional monitoring logs.")
        sample_csv_path = os.path.join(CURRENT_DIR, "..", "data", "sample_regional_data.csv")
        if os.path.exists(sample_csv_path):
            with open(sample_csv_path, "r") as f:
                st.download_button("📥 Download Sample Regional Dataset (CSV)", f.read(), file_name="sample_environmental_data.csv", mime="text/csv")
                
        uploaded_file = st.file_uploader("Upload CSV Data File", type=["csv"])
        if uploaded_file:
            try:
                df_up = pd.read_csv(uploaded_file)
                st.write("Uploaded Preview:")
                st.dataframe(df_up.head(), use_container_width=True)
                
                row_idx = st.selectbox("Select Row to Analyze:", range(len(df_up)), format_func=lambda i: f"Row {i+1}: {df_up.iloc[i].get('region_name', 'Region ' + str(i+1))}")
                sel_row = df_up.iloc[row_idx]
                selected_metrics = {
                    "region_name": str(sel_row.get("region_name", f"Uploaded Region {row_idx+1}")),
                    "latitude": float(sel_row.get("latitude", 13.0)),
                    "longitude": float(sel_row.get("longitude", 80.0)),
                    "pm2_5": float(sel_row.get("pm2_5", 50.0)),
                    "pm10": float(sel_row.get("pm10", 90.0)),
                    "so2": float(sel_row.get("so2", 20.0)),
                    "no2": float(sel_row.get("no2", 30.0)),
                    "water_ph": float(sel_row.get("water_ph", 7.0)),
                    "water_tds": float(sel_row.get("water_tds", 800.0)),
                    "water_do": float(sel_row.get("water_do", 6.0)),
                    "water_bod": float(sel_row.get("water_bod", 4.0)),
                    "lead_ppm": float(sel_row.get("lead_ppm", 0.01)),
                    "chromium_ppm": float(sel_row.get("chromium_ppm", 0.02)),
                    "industrial_density": str(sel_row.get("industrial_density", "Moderate"))
                }
            except Exception as e:
                st.error(f"Error reading CSV: {e}")
                
    else:
        st.markdown("### ✍️ Manual Ecological Reading Entry")
        with st.form("manual_entry_form"):
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                man_name = st.text_input("Region Name", value="Ranipet SIPCOT Industrial Zone")
                man_lat = st.number_input("Latitude", value=12.92, format="%.4f")
                man_lon = st.number_input("Longitude", value=79.33, format="%.4f")
                man_pm25 = st.number_input("PM2.5 (µg/m³)", value=85.0, min_value=0.0)
                man_pm10 = st.number_input("PM10 (µg/m³)", value=150.0, min_value=0.0)
                man_so2 = st.number_input("SO2 (µg/m³)", value=35.0, min_value=0.0)
                man_no2 = st.number_input("NO2 (µg/m³)", value=45.0, min_value=0.0)
            with col_m2:
                man_ph = st.number_input("Water pH", value=6.2, min_value=0.0, max_value=14.0)
                man_tds = st.number_input("Water TDS (mg/L)", value=1750.0, min_value=0.0)
                man_do = st.number_input("Dissolved Oxygen (mg/L)", value=3.5, min_value=0.0)
                man_bod = st.number_input("BOD (mg/L)", value=12.0, min_value=0.0)
                man_lead = st.number_input("Lead Content (ppm)", value=0.06, format="%.4f")
                man_cr = st.number_input("Chromium Content (ppm)", value=0.35, format="%.4f")
                man_density = st.selectbox("Industrial Activity Level", ["Low", "Moderate", "High", "Very High"])
                
            btn_save = st.form_submit_button("Load Metrics for Analysis")
            if btn_save:
                selected_metrics = {
                    "region_name": man_name,
                    "latitude": man_lat,
                    "longitude": man_lon,
                    "pm2_5": man_pm25,
                    "pm10": man_pm10,
                    "so2": man_so2,
                    "no2": man_no2,
                    "water_ph": man_ph,
                    "water_tds": man_tds,
                    "water_do": man_do,
                    "water_bod": man_bod,
                    "lead_ppm": man_lead,
                    "chromium_ppm": man_cr,
                    "industrial_density": man_density
                }
                st.success(f"Metrics prepared for: **{man_name}**")

    if selected_metrics:
        st.session_state["active_metrics"] = selected_metrics
        st.info("Metrics locked! Navigate to the 'AI Impact Analysis' tab or click the button below to generate the report.")
        if st.button("🚀 Run AI Impact Analysis Now", type="primary"):
            st.session_state["trigger_analysis"] = True

# -------------------------------------------------------------
# TAB 3: AI IMPACT ANALYSIS
# -------------------------------------------------------------
with tab_analysis:
    st.subheader("AI Predictive Environmental Risk Assessment")
    
    curr_metrics = st.session_state.get("active_metrics")
    if not curr_metrics:
        # Default to Palar River Basin
        default_reg = database.get_region_by_name("Palar River Basin (Ranipet Industrial Area)")
        if default_reg:
            curr_metrics = default_reg
            st.session_state["active_metrics"] = default_reg
            
    if curr_metrics:
        st.write(f"Analyzing Target: **{curr_metrics['region_name']}**")
        
        # Run analysis
        with st.spinner("Processing multi-factor ecological models and generating AI synthesis..."):
            result = analyzer.analyze_environmental_metrics(curr_metrics)
            
        # Top-level indicators
        col_res1, col_res2, col_res3, col_res4 = st.columns(4)
        eqi_val = result["overall_eqi"]
        
        col_res1.metric("Overall EQI", f"{eqi_val}/100", help="Environmental Quality Index: 100 = Pristine, <40 = Severe Hazard")
        col_res2.metric("Air Health Score", f"{result['air_subindex']}/100")
        col_res3.metric("Water Quality Score", f"{result['water_subindex']}/100")
        col_res4.metric("Soil/Effluent Score", f"{result['soil_subindex']}/100")
        
        # Risk Badge
        risk_lvl = result["risk_level"]
        if "Low Risk" in risk_lvl:
            st.success(f"🌿 **Ecosystem Classification:** {risk_lvl}")
        elif "Moderate" in risk_lvl:
            st.warning(f"⚠️ **Ecosystem Classification:** {risk_lvl}")
        else:
            st.error(f"🚨 **Ecosystem Classification:** {risk_lvl}")
            
        st.markdown("---")
        
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            st.markdown("### 🤖 AI-Generated Predictive Summary")
            st.markdown(result["ai_summary"])
            st.caption(f"Synthesized by: {result['engine']}")
            
            st.markdown("### 🛠️ Recommended Remediation Protocol")
            for idx, rec in enumerate(result.get("recommendations", [])):
                st.markdown(f"**{idx+1}.** {rec}")
                
        with col_right:
            st.markdown("### 📊 Sub-Index Health Breakdown")
            scores_df = pd.DataFrame({
                "Domain": ["Air Quality", "Water Quality", "Soil & Heavy Metals", "Overall EQI"],
                "Score (0-100)": [result["air_subindex"], result["water_subindex"], result["soil_subindex"], result["overall_eqi"]]
            })
            st.bar_chart(scores_df.set_index("Domain"))
            
            # Save button
            if st.button("💾 Save This Assessment to History"):
                database.save_analysis(
                    region_name=result["region_name"],
                    latitude=curr_metrics.get("latitude", 0.0),
                    longitude=curr_metrics.get("longitude", 0.0),
                    overall_eqi=result["overall_eqi"],
                    air_score=result["air_subindex"],
                    water_score=result["water_subindex"],
                    soil_score=result["soil_subindex"],
                    risk_level=result["risk_level"],
                    ai_summary=result["ai_summary"],
                    recommendations=result.get("recommendations", [])
                )
                st.success("Assessment archived to database successfully!")
    else:
        st.warning("Please select or input regional data in the 'Data Input' tab first.")

# -------------------------------------------------------------
# TAB 4: HISTORY & REGION COMPARISON
# -------------------------------------------------------------
with tab_history:
    st.subheader("Historical Assessment Ledger & Region Review")
    history_logs = database.get_analysis_history()
    
    if history_logs:
        df_hist = pd.DataFrame(history_logs)
        st.dataframe(df_hist[["id", "region_name", "overall_eqi", "air_score", "water_score", "soil_score", "risk_level", "created_at"]], hide_index=True, use_container_width=True)
        
        st.markdown("### 🔍 Historical Comparison Chart")
        comp_df = df_hist[["region_name", "overall_eqi", "air_score", "water_score"]].drop_duplicates("region_name")
        st.line_chart(comp_df.set_index("region_name"))
    else:
        st.info("No assessments logged yet. Run your first analysis in Tab 3!")

# -------------------------------------------------------------
# TAB 5: ABOUT & SCIENTIFIC GUIDE
# -------------------------------------------------------------
with tab_about:
    st.subheader("About the Project & Ecological Standards")
    st.markdown("""
    **Project Title:** Smart Environmental Impact Analyzer  
    **Project:** Open-Source Ecological Risk Platform  
    **Engine:** Heuristic NLP + Multi-Domain EQI  
      
      
      

    ---

    ### 📖 Metric Definitions & Reference Thresholds
    1. **PM2.5 / PM10 (Particulate Matter):** Fine inhalable particles. Thresholds derived from Central Pollution Control Board (CPCB) standards (Safe: PM2.5 < 60 µg/m³, PM10 < 100 µg/m³).
    2. **Water TDS (Total Dissolved Solids):** Measures mineral, salt, and organic dissolved matter. Safe drinking water is < 500 mg/L. Heavy industrial effluents exceed 1500 mg/L.
    3. **Dissolved Oxygen (DO):** Vital indicator of waterbody health. DO levels < 4.0 mg/L induce aquatic hypoxia.
    4. **BOD (Biochemical Oxygen Demand):** Measures organic pollution load. Values > 8.0 mg/L indicate serious municipal or industrial wastewater contamination.
    5. **Hexavalent Chromium (Cr VI):** Characteristic heavy metal contaminant associated with industrial leather tanning and dyeing, strictly bounded at 0.05 ppm.

    *Note: Designed as an educational and analytical tool for engineering research.*
    """)
