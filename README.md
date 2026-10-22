# 🌍 EcoAnalyzer AI — Smart Environmental Impact & Risk Analyzer

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Database](https://img.shields.io/badge/Database-SQLite3-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Operational Cost](https://img.shields.io/badge/Operational%20Cost-100%25%20Free-brightgreen.svg)](#zero-cost-architecture)

> An open-source, full-stack AI analytical platform that transforms multi-sensor ecological and industrial pollution datasets into simplified, structured predictive risk summaries, multi-domain health indices, and actionable mitigation protocols.

---

## 🌟 Overview

Tracking and understanding regional environmental impact across complex air, water, and soil metrics is notoriously challenging due to fragmented reporting and non-standardized formats.

**EcoAnalyzer AI** bridges this gap by unifying sensor parameters into a standardized **Environmental Quality Index (EQI)**. The system evaluates air quality (PM2.5, PM10, SO2, NO2), riverine and groundwater potability (pH, TDS, Dissolved Oxygen, BOD), and industrial heavy metal soil contamination (Lead, Hexavalent Chromium), providing environmental researchers, municipal bodies, and citizens with transparent, automated predictive hazard assessments.

---

## 🚀 Key Features

* **🗺️ Interactive Regional Pollution Map:**
  * Geospatial cluster tracking and baseline environmental parameter visualization across industrial corridors.

* **📥 Multi-Format Ecological Data Ingestion:**
  * Ingest data via pre-seeded regional monitoring stations, custom CSV/JSON batch file upload, or manual sensor parameter entry.

* **📊 Multi-Factor Environmental Quality Index (EQI):**
  * Computes standardized Air Quality, Water Quality, and Soil/Heavy Metal Sub-indices on a 0–100 scale.
  * Classifies ecosystems into **Low Risk (Healthy)**, **Moderate Risk (Watchlist)**, **High Risk (Hazardous)**, or **Critical Risk (Ecological Emergency)**.

* **🤖 AI-Generated Predictive Impact Summaries:**
  * Generates structured markdown impact assessments explaining primary pollution drivers, downstream groundwater risks, and localized degradation trends.
  * Proposes concrete remediation protocols (e.g., Zero-Liquid-Discharge audits, floating bio-retention, phytoremediation).
  * Operates 100% offline with zero external API fees, with optional support for Google Gemini Free-Tier.

* **📜 Longitudinal Comparison Ledger:**
  * Archives assessments in an embedded SQLite database for historical trend analysis and cross-regional ecological comparisons.

---

## 🏗️ System Architecture

```text
       ┌───────────────────────────────┐
       │   Researcher / User (Web)     │
       └──────────────┬────────────────┘
                      │ Sensor Data / CSV / Queries
                      ▼
       ┌───────────────────────────────┐
       │       EcoAnalyzer API         │
       │         (FastAPI)             │
       └──────┬───────────────┬────────┘
              │               │
       Sub-Index Models    Database Storage
              │               │
       ┌──────▼────────┐┌─────▼────────┐
       │ AI Predictive ││ SQLite       │
       │ Synthesis     ││ Database     │
       └───────────────┘└──────────────┘
              ▲               ▲
              │ Analytics     │ Read/Write
       ┌──────┴───────────────┴────────┐
       │   Streamlit Web Interface    │
       │ (Map, Upload, EQI, Ledger)    │
       └───────────────────────────────┘
```

---

## 🛠️ Zero-Cost Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Backend API** | FastAPI + Uvicorn | High-performance asynchronous REST endpoints |
| **Database** | SQLite3 | Embedded, zero-configuration local database |
| **Interactive UI** | Streamlit + Pandas | Modern reactive dashboard with maps, charts, and metric gauges |
| **AI Risk Engine** | Heuristic NLP / Gemini Free-Tier | Deterministic ecological scoring + optional Google Generative AI |
| **Data Visualization** | Streamlit native charts + Matplotlib | Sub-index breakdown and longitudinal comparison trends |

---

## 📁 Repository Layout

```text
smart_environmental_analyzer/
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── database.py       # SQLite models, region seeding & historical ledger
│       ├── analyzer.py       # EQI computation, risk scoring & AI synthesis
│       ├── models.py         # Pydantic schema validation
│       └── main.py           # FastAPI web application endpoints
├── frontend/
│   └── app.py                # Multi-tab Streamlit user interface
├── data/
│   └── sample_regional_data.csv  # Sample multi-region ecological dataset
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## ⚡ Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/smart-environmental-analyzer.git
cd smart-environmental-analyzer
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Run the Streamlit Dashboard
```bash
python -m streamlit run frontend/app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### 5. (Optional) Run the FastAPI REST Server
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```
Interactive API docs will be live at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 📡 API Endpoints

| Method | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Verify API and SQLite database status |
| `GET` | `/api/regions` | Retrieve all registered regional baseline readings |
| `POST` | `/api/analyze` | Submit environmental parameters and return AI EQI assessment |
| `GET` | `/api/history` | Retrieve historical analysis log entries |

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
