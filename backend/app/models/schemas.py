from typing import Literal

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    day: int = Field(ge=1)
    breed: str = Field(min_length=1)
    months_after_giving_birth: int = Field(ge=0)
    previous_mastitis_status: int = Field(ge=0, le=1)
    iu_fl: float
    eu_fl: float
    iu_fr: float
    eu_fr: float
    iu_rl: float
    eu_rl: float
    iu_rr: float
    eu_rr: float
    temperature: float
    hardness: int = Field(ge=0, le=1)
    pain: int = Field(ge=0, le=1)
    milk_visibility: int = Field(ge=0, le=1)


class PredictionResponse(BaseModel):
    risk_level: Literal["BAJO", "MEDIO", "ALTO"]
    model_label: str
    probability: float = Field(ge=0, le=1)
    model: str
    disclaimer: str


class SimulationRequest(BaseModel):
    scenario: Literal["normal", "estres_ambiental", "posible_riesgo", "alto", "persistente"]
    seed: int = Field(default=42, ge=0)


class SimulationResponse(BaseModel):
    scenario: str
    seed: int
    reading: PredictionRequest
    prediction: PredictionResponse


class AnimalCreate(BaseModel):
    animal_id: str = Field(min_length=1)
    breed: str = Field(min_length=1)
    age_months: int = Field(ge=0)
    weight_kg: float = Field(gt=0)
    owner: str = Field(min_length=1)


class AnimalResponse(AnimalCreate):
    id: int
    created_at: str


class MeasurementResponse(BaseModel):
    measurement_id: int
    prediction_id: int
    animal_id: str
    risk_level: Literal["BAJO", "MEDIO", "ALTO"]
    probability: float = Field(ge=0, le=1)
    model: str
    alert_status: str
    created_at: str
    prediction: PredictionResponse


class HistoryItem(BaseModel):
    measurement_id: int
    prediction_id: int
    animal_id: str
    payload: PredictionRequest
    risk_level: Literal["BAJO", "MEDIO", "ALTO"]
    probability: float = Field(ge=0, le=1)
    model: str
    created_at: str


class AlertResponse(BaseModel):
    id: int
    animal_id: str
    prediction_id: int
    risk_level: Literal["BAJO", "MEDIO", "ALTO"]
    status: str
    created_at: str
