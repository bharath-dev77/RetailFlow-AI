from pydantic import BaseModel, Field
from typing import Optional, List

class EnvironmentalDataInput(BaseModel):
    region_name: str = Field(..., example="Palar River Basin")
    latitude: Optional[float] = Field(12.92, example=12.92)
    longitude: Optional[float] = Field(79.33, example=79.33)
    pm2_5: float = Field(..., example=88.5)
    pm10: float = Field(..., example=165.2)
    so2: float = Field(..., example=42.0)
    no2: float = Field(..., example=55.1)
    water_ph: float = Field(..., example=5.8)
    water_tds: float = Field(..., example=1850.0)
    water_do: float = Field(..., example=3.2)
    water_bod: float = Field(..., example=14.5)
    lead_ppm: float = Field(..., example=0.08)
    chromium_ppm: float = Field(..., example=0.42)
    industrial_density: Optional[str] = Field("High", example="High")

class AnalysisResponse(BaseModel):
    region_name: str
    overall_eqi: float
    air_subindex: float
    water_subindex: float
    soil_subindex: float
    risk_level: str
    ai_summary: str
    recommendations: List[str]
    engine: str

class RegionResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    pm2_5: float
    pm10: float
    so2: float
    no2: float
    water_ph: float
    water_tds: float
    water_do: float
    water_bod: float
    lead_ppm: float
    chromium_ppm: float
    industrial_density: str
