from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

from app import database, analyzer
from app.models import EnvironmentalDataInput, AnalysisResponse, RegionResponse

app = FastAPI(
    title="Smart Environmental Impact Analyzer API",
    description="REST API for automated regional environmental risk scoring, ecological indices, and AI summary generation.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    database.init_db()

@app.get("/")
def read_root():
    return {
        "project": "Smart Environmental Impact Analyzer",
        "status": "online",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def healthcheck():
    return {"status": "healthy", "database": "connected"}

@app.get("/api/regions", response_model=List[RegionResponse])
def get_regions():
    return database.get_all_regions()

@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze_region(payload: EnvironmentalDataInput):
    data_dict = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    result = analyzer.analyze_environmental_metrics(data_dict)
    
    # Save to history ledger
    database.save_analysis(
        region_name=result["region_name"],
        latitude=payload.latitude or 0.0,
        longitude=payload.longitude or 0.0,
        overall_eqi=result["overall_eqi"],
        air_score=result["air_subindex"],
        water_score=result["water_subindex"],
        soil_score=result["soil_subindex"],
        risk_level=result["risk_level"],
        ai_summary=result["ai_summary"],
        recommendations=result["recommendations"]
    )
    
    return result

@app.get("/api/history")
def get_history():
    return {"history": database.get_analysis_history()}
