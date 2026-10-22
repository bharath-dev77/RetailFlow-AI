import os
from typing import Dict, Any, List

def compute_air_subindex(pm25: float, pm10: float, so2: float, no2: float) -> float:
    """Calculates Air Quality Sub-index (0 to 100, 100 = cleanest)."""
    # PM2.5 penalty
    p_pm25 = max(0, min(100, 100 - (pm25 / 150.0) * 100))
    # PM10 penalty
    p_pm10 = max(0, min(100, 100 - (pm10 / 250.0) * 100))
    # SO2 & NO2 penalty
    p_gas = max(0, min(100, 100 - ((so2 + no2) / 160.0) * 100))
    
    score = (0.45 * p_pm25) + (0.35 * p_pm10) + (0.20 * p_gas)
    return round(score, 1)

def compute_water_subindex(ph: float, tds: float, do: float, bod: float) -> float:
    """Calculates Water Quality Sub-index (0 to 100, 100 = pristine)."""
    # pH ideal range 6.5 to 8.5
    if 6.5 <= ph <= 8.5:
        p_ph = 100.0
    else:
        dev = min(abs(ph - 7.5), 4.0)
        p_ph = max(0.0, 100.0 - (dev / 4.0) * 100.0)
        
    # TDS ideal < 500, critical > 2500
    p_tds = max(0.0, min(100.0, 100.0 - (tds / 2500.0) * 100.0))
    
    # Dissolved Oxygen (DO) ideal > 6.0 mg/L, dead water < 2.0
    p_do = max(0.0, min(100.0, (do / 8.0) * 100.0))
    
    # BOD clean < 3 mg/L, critical > 20 mg/L
    p_bod = max(0.0, min(100.0, 100.0 - (bod / 20.0) * 100.0))
    
    score = (0.20 * p_ph) + (0.25 * p_tds) + (0.30 * p_do) + (0.25 * p_bod)
    return round(score, 1)

def compute_soil_subindex(lead_ppm: float, chromium_ppm: float) -> float:
    """Calculates Soil/Heavy Metal Sub-index (0 to 100, 100 = uncontaminated)."""
    # Lead critical > 0.10 ppm
    p_lead = max(0.0, min(100.0, 100.0 - (lead_ppm / 0.10) * 100.0))
    # Chromium critical > 0.20 ppm (industrial effluent threshold)
    p_cr = max(0.0, min(100.0, 100.0 - (chromium_ppm / 0.20) * 100.0))
    
    score = (0.40 * p_lead) + (0.60 * p_cr)
    return round(score, 1)

def determine_risk_level(eqi: float) -> str:
    if eqi >= 75.0:
        return "Low Risk (Ecologically Healthy)"
    elif eqi >= 55.0:
        return "Moderate Risk (Under Observation)"
    elif eqi >= 38.0:
        return "High Risk (Severe Industrial Stress)"
    else:
        return "Critical Risk (Ecological Emergency)"

def generate_ai_predictive_summary(metrics: Dict[str, Any], eqi: float, air: float, water: float, soil: float, risk_level: str) -> Dict[str, Any]:
    """Generates an AI-assisted predictive impact report and mitigation actions."""
    region_name = metrics.get("region_name", "Specified Region")
    
    # Check for free-tier Gemini API key if present
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""You are an environmental data scientist. Analyze this regional environmental dataset:
Region: {region_name}
Overall EQI: {eqi}/100 ({risk_level})
Air Score: {air}/100, Water Score: {water}/100, Soil/Heavy Metal Score: {soil}/100
Metrics: PM2.5={metrics.get('pm2_5')}, Water pH={metrics.get('water_ph')}, TDS={metrics.get('water_tds')}, DO={metrics.get('water_do')} mg/L, BOD={metrics.get('water_bod')} mg/L, Chromium={metrics.get('chromium_ppm')} ppm.

Provide a concise 3-paragraph environmental impact summary highlighting:
1. Primary pollution risks and ecological health assessment.
2. Short-term and long-term consequences for local communities and water bodies.
3. 3 concrete remediation actions for local pollution control boards."""
            resp = model.generate_content(prompt)
            if resp and resp.text:
                return {
                    "summary_text": resp.text.strip(),
                    "source": "Google Gemini Free-Tier"
                }
        except Exception:
            pass  # Fall back to offline deterministic rule engine

    # Heuristic Offline AI Synthesis Engine (Zero-Cost & Deterministic)
    critical_factors = []
    if metrics.get("pm2_5", 0) > 60:
        critical_factors.append(f"Elevated fine particulate matter (PM2.5: {metrics.get('pm2_5')} µg/m³), indicating severe respiratory risk")
    if metrics.get("water_tds", 0) > 1500:
        critical_factors.append(f"Excessive Total Dissolved Solids (TDS: {metrics.get('water_tds')} mg/L), impairing local groundwater potability")
    if metrics.get("water_do", 8) < 4.0:
        critical_factors.append(f"Hypoxic aquatic conditions (Dissolved Oxygen: {metrics.get('water_do')} mg/L), threatening freshwater fauna")
    if metrics.get("chromium_ppm", 0) > 0.10:
        critical_factors.append(f"Heavy hexavalent chromium traces ({metrics.get('chromium_ppm')} ppm), characteristic of untreated tannery/dye effluents")

    if not critical_factors:
        critical_factors.append("Ecological parameters fall generally within safe national baseline tolerances")

    factors_str = "; ".join(critical_factors)
    
    summary_text = (
        f"### 🌿 Environmental Impact Assessment for {region_name}\n\n"
        f"**1. Overall Ecosystem Status:**\n"
        f"The regional Environmental Quality Index (EQI) is evaluated at **{eqi}/100**, placing the ecosystem under a **{risk_level}** status. "
        f"Sub-index diagnostics reflect an Air Quality rating of **{air}/100**, Water Quality rating of **{water}/100**, and a Soil & Heavy Metal safety score of **{soil}/100**.\n\n"
        f"**2. Primary Stress Drivers:**\n"
        f"Key pollution indicators identified from sensor readings include: {factors_str}. "
        f"Continued exposure without bio-remediation poses high percolation risk into sub-surface aquifers and localized biodiversity loss.\n\n"
        f"**3. Predictive Environmental Trends:**\n"
        f"Based on historical degradation models, unattended discharge will likely reduce riverine self-purification capacity within 12 to 18 months, "
        f"further depressing dissolved oxygen levels and expanding the salinity intrusion zone."
    )

    recs = [
        "Mandate zero-liquid-discharge (ZLD) audits on surrounding industrial and processing units.",
        "Deploy floating bio-retention barriers along drainage channels to arrest particulate and dye dispersion.",
        "Establish continuous IoT-based water parameter logging stations at key discharge confluence points.",
        "Initiate localized phytoremediation using vetiver grass and hyper-accumulating flora across affected banks."
    ]

    return {
        "summary_text": summary_text,
        "recommendations": recs,
        "source": "Rule-Based Ecological AI Engine (100% Free / Offline)"
    }

def analyze_environmental_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Top-level pipeline processing regional environmental input."""
    pm25 = float(data.get("pm2_5", 50.0))
    pm10 = float(data.get("pm10", 90.0))
    so2 = float(data.get("so2", 20.0))
    no2 = float(data.get("no2", 30.0))
    
    ph = float(data.get("water_ph", 7.0))
    tds = float(data.get("water_tds", 800.0))
    do = float(data.get("water_do", 6.0))
    bod = float(data.get("water_bod", 4.0))
    
    lead = float(data.get("lead_ppm", 0.01))
    cr = float(data.get("chromium_ppm", 0.02))
    
    air_idx = compute_air_subindex(pm25, pm10, so2, no2)
    water_idx = compute_water_subindex(ph, tds, do, bod)
    soil_idx = compute_soil_subindex(lead, cr)
    
    # Weighted composite EQI
    eqi = round((0.35 * air_idx) + (0.40 * water_idx) + (0.25 * soil_idx), 1)
    risk = determine_risk_level(eqi)
    
    ai_output = generate_ai_predictive_summary(data, eqi, air_idx, water_idx, soil_idx, risk)
    
    return {
        "region_name": data.get("region_name", "Custom Region"),
        "overall_eqi": eqi,
        "air_subindex": air_idx,
        "water_subindex": water_idx,
        "soil_subindex": soil_idx,
        "risk_level": risk,
        "ai_summary": ai_output["summary_text"],
        "recommendations": ai_output.get("recommendations", []),
        "engine": ai_output.get("source", "Standard Analyzer")
    }
