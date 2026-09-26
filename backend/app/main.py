import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import (
    AnimalCreate,
    AnimalResponse,
    AlertResponse,
    HistoryItem,
    MeasurementResponse,
    PredictionRequest,
    PredictionResponse,
    SimulationRequest,
    SimulationResponse,
)
from app.services.measurement_service import MeasurementService
from app.services.prediction_service import PredictionService
from app.services.repository import Repository
from app.services.simulator import CattleSimulator

app = FastAPI(title="My Ganado API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/animals", response_model=AnimalResponse, status_code=201)
def create_animal(request: AnimalCreate) -> AnimalResponse:
    try:
        return AnimalResponse(**Repository().create_animal(request.model_dump()))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="animal_id already exists") from exc


@app.get("/api/v1/animals", response_model=list[AnimalResponse])
def list_animals() -> list[AnimalResponse]:
    return [AnimalResponse(**animal) for animal in Repository().list_animals()]


@app.get("/api/v1/animals/{animal_id}/history", response_model=list[HistoryItem])
def animal_history(animal_id: str) -> list[HistoryItem]:
    repository = Repository()
    if not repository.animal_exists(animal_id):
        raise HTTPException(status_code=404, detail="animal not found")
    return [HistoryItem(**item) for item in repository.get_history(animal_id)]


@app.get("/api/v1/alerts", response_model=list[AlertResponse])
def list_alerts(animal_id: str | None = None) -> list[AlertResponse]:
    return [AlertResponse(**alert) for alert in Repository().list_alerts(animal_id)]


@app.post("/api/v1/predictions", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    try:
        return PredictionService().predict(request)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/v1/animals/{animal_id}/measurements", response_model=MeasurementResponse, status_code=201)
def record_measurement(animal_id: str, request: PredictionRequest) -> MeasurementResponse:
    if not any(animal["animal_id"] == animal_id for animal in Repository().list_animals()):
        raise HTTPException(status_code=404, detail="animal not found")
    try:
        return MeasurementService().record(animal_id, request)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/v1/simulations", response_model=SimulationResponse)
def simulate(request: SimulationRequest) -> SimulationResponse:
    try:
        reading = CattleSimulator().generate(request.scenario, request.seed)
        prediction = PredictionService().predict(reading)
        return SimulationResponse(
            scenario=request.scenario,
            seed=request.seed,
            reading=reading,
            prediction=prediction,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
