from typing import Literal, get_args
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, model_validator

# Exact Breed values in ml/data/raw/cattle_mastitis.csv and its processed copy.
# Preserve "hostlene": interpreting it as Holstein would require source validation.
BovineBreed = Literal["Jersey", "hostlene"]
BOVINE_BREEDS = list(get_args(BovineBreed))
AnimalSpecies = Literal["bovine_adult", "bovine_young", "lamb", "goat_kid"]
SPECIES_CATALOG = [
    {"id": "bovine_adult", "label": "Bovina adulta (vaca)", "count": 6600, "dataset": "cattle_mastitis"},
    {"id": "bovine_young", "label": "Bovino joven (ternera/o)", "count": 300, "dataset": "young_stock"},
    {"id": "lamb", "label": "Cordero", "count": 97, "dataset": "young_stock"},
    {"id": "goat_kid", "label": "Cabrito", "count": 44, "dataset": "young_stock"},
]
SPECIES_LABELS = {species["id"]: species["label"] for species in SPECIES_CATALOG}


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
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
    temperature: float = Field(ge=0, le=100, allow_inf_nan=False)
    hardness: int = Field(ge=0, le=1)
    pain: int = Field(ge=0, le=1)
    milk_visibility: int = Field(ge=0, le=1)
    ambient_temperature_c: float | None = Field(default=None, ge=-20, le=60, allow_inf_nan=False)
    humidity_pct: float | None = Field(default=None, ge=0, le=100, allow_inf_nan=False)
    water_available: bool | None = None
    observed_at: datetime | None = None


class PredictionResponse(BaseModel):
    risk_level: Literal["BAJO", "MEDIO", "ALTO"]
    model_label: str
    probability: float = Field(ge=0, le=1)
    model: str
    disclaimer: str


class SimulationRequest(BaseModel):
    scenario: Literal["normal", "estres_ambiental", "posible_riesgo", "alto", "persistente"]
    seed: int = Field(default=42, ge=0)
    animal_id: str | None = Field(default=None, min_length=1)


class SimulationResponse(BaseModel):
    scenario: str
    seed: int
    animal_id: str | None = None
    measurement_id: int | None = None
    reading: PredictionRequest
    prediction: PredictionResponse


class AnimalCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    animal_id: str | None = Field(default=None, min_length=1, max_length=100)
    species: AnimalSpecies
    breed: BovineBreed | None = None
    age_months: int = Field(ge=0)
    weight_kg: float = Field(gt=0, allow_inf_nan=False)
    owner: str = Field(min_length=1, max_length=150)

    @model_validator(mode="after")
    def validate_breed_for_species(self):
        if self.species == "bovine_adult" and self.breed is None:
            raise ValueError("Selecciona la raza bovina")
        if self.species != "bovine_adult" and self.breed is not None:
            raise ValueError("El dataset de animales jóvenes no proporciona razas")
        return self


class AnimalResponse(BaseModel):
    # Responses retain historical IDs and breed labels without rewriting old data.
    animal_id: str
    breed: str
    species: AnimalSpecies = "bovine_adult"
    age_months: int
    weight_kg: float
    owner: str
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
