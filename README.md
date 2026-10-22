# 🏪 RetailFlow AI — AI-Powered Local Retail Automator

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Database](https://img.shields.io/badge/Database-SQLite3-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Operational Cost](https://img.shields.io/badge/Operational%20Cost-100%25%20Free-brightgreen.svg)](#zero-cost-architecture)

> A lightweight, zero-cost AI assistant and operations suite designed specifically for local retail, convenience, and Kirana stores. Automates customer inquiries via WhatsApp/SMS, digitizes vendor bills with automated text extraction, and tracks real-time inventory and sales.

---

## 🌟 Key Features

* **💬 Conversational Customer Assistant (WhatsApp / SMS Ready):**
  * Automatically handles incoming customer queries regarding product availability, pricing, store hours, and order placement.
  * Powered by an offline rule-based NLP intent parser with zero external API dependencies, with optional Google Gemini Free-Tier support.

* **🧾 Zero-Cost Vendor Bill & Receipt Digitizer:**
  * Extracts product names, quantities, unit prices, and grand totals from supplier invoices and delivery notes.
  * Synchronizes digitized items directly into the store's inventory database with a single click.

* **📦 Live Inventory Management:**
  * Real-time stock status monitoring with proactive low-stock alert thresholds.
  * Quick stock increment/decrement controls (`+1`, `-1`, `+10`) and catalog management.

* **📊 Point of Sale (POS) & Sales Ledger:**
  * Streamlined counter billing interface supporting Cash, UPI, and Store Credit (Khata).
  * Automatically deducts sold quantities from live inventory upon bill completion.

---

## 🏗️ System Architecture

```text
       ┌───────────────────────────────┐
       │   Customer (WhatsApp / Web)   │
       └──────────────┬────────────────┘
                      │ Inbound Queries
                      ▼
       ┌───────────────────────────────┐
       │       RetailFlow API          │
       │         (FastAPI)             │
       └──────┬───────────────┬────────┘
              │               │
      Intent Parsing    Inventory Check
              │               │
       ┌──────▼────────┐┌─────▼────────┐
       │ AI & OCR      ││ SQLite       │
       │ Engine        ││ Database     │
       └───────────────┘└──────────────┘
              ▲               ▲
              │ Operations    │ Read/Write
       ┌──────┴───────────────┴────────┐
       │  Merchant Streamlit Dashboard │
       │  (Inventory, POS, Bill Scan)  │
       └───────────────────────────────┘
```

---

## 🛠️ Zero-Cost Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Backend API** | FastAPI + Uvicorn | High-performance asynchronous Python REST API |
| **Database** | SQLite 3 | Embedded, zero-configuration local SQL database |
| **Merchant Dashboard** | Streamlit + Pandas | Modern reactive web UI with zero frontend build tooling |
| **AI Intent Engine** | Heuristic NLP / Gemini Free-Tier | Offline regex & entity parser + optional Gemini Free Tier |
| **Invoice Digitizer** | Heuristic Text/OCR Parser | Rule-based structural parser for receipts and delivery notes |

---

## 📁 Repository Structure

```text
ai-retail-automator/
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── database.py         # SQLite database models, initialization & CRUD helpers
│       ├── main.py             # FastAPI REST application endpoints
│       ├── models.py           # Pydantic data schemas
│       └── services/
│           ├── __init__.py
│           ├── ai_service.py   # Intent classification & customer reply generator
│           └── ocr_service.py  # Receipt/invoice line item parsing engine
├── frontend/
│   └── app.py                  # Streamlit Merchant Operations Dashboard
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ai-retail-automator.git
cd ai-retail-automator
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

### 4. Run the Streamlit Merchant Dashboard
```bash
python -m streamlit run frontend/app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### 5. (Optional) Run the FastAPI Backend
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```
Interactive Swagger API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 📡 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Verify API and database status |
| `GET` | `/api/products` | Retrieve all items and current stock levels |
| `POST` | `/api/products` | Add or update a product in the catalog |
| `POST` | `/api/chat` | Process customer query and return AI response |
| `POST` | `/api/receipt` | Parse supplier invoice text and extract line items |
| `GET` | `/api/sales` | Fetch sales ledger and total revenue |
| `POST` | `/api/sales` | Record counter sale and decrement stock |

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
