import sqlite3
import secrets

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import (
    BOVINE_BREEDS,
    SPECIES_CATALOG,
    SPECIES_LABELS,
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
from app.services.notification_service import NotificationService
from app.services.simulator import CattleSimulator
from app.services.auth import router as auth_router, current_user, authorize_animal, visible_ids

app = FastAPI(title="My Ganado API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5174",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.include_router(auth_router)


@app.middleware("http")
async def protect_origin(request: Request, call_next):
    origin = request.headers.get("origin")
    allowed = {"http://127.0.0.1:5173", "http://localhost:5173", "http://127.0.0.1:5174", "http://localhost:5174", str(request.base_url).rstrip("/")}
    if request.method in {"POST", "PUT", "PATCH", "DELETE"} and origin and origin not in allowed:
        return JSONResponse({"detail": "Origen no autorizado"}, status_code=403)
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/catalogs/breeds", response_model=list[str])
def list_breeds(user=Depends(current_user)) -> list[str]:
    return BOVINE_BREEDS


@app.get("/api/v1/catalogs/species")
def list_species(user=Depends(current_user)):
    return SPECIES_CATALOG


@app.post("/api/v1/animals", response_model=AnimalResponse, status_code=201)
def create_animal(request: AnimalCreate, user=Depends(current_user)) -> AnimalResponse:
    if user["role"] != "productor":
        raise HTTPException(403, "Solo los productores pueden registrar animales")
    try:
        animal = request.model_dump()
        if animal["animal_id"] is None:
            animal["animal_id"] = f"animal-{secrets.token_hex(4)}"
        if animal["breed"] is None:
            animal["breed"] = "No especificada"
        return AnimalResponse(**Repository().create_animal(animal, user["id"]))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="No se pudo asignar el identificador. Intenta guardar de nuevo.") from exc


@app.get("/api/v1/animals", response_model=list[AnimalResponse])
def list_animals(user=Depends(current_user)) -> list[AnimalResponse]:
    ids = visible_ids(user)
    return [AnimalResponse(**animal) for animal in Repository().list_animals() if animal["animal_id"] in ids]


@app.get("/api/v1/animals/{animal_id}/history", response_model=list[HistoryItem])
def animal_history(animal_id: str, user=Depends(current_user)) -> list[HistoryItem]:
    authorize_animal(user, animal_id)
    repository = Repository()
    if not repository.animal_exists(animal_id):
        raise HTTPException(status_code=404, detail="animal not found")
    return [HistoryItem(**item) for item in repository.get_history(animal_id)]


@app.get("/api/v1/alerts", response_model=list[AlertResponse])
def list_alerts(animal_id: str | None = None, user=Depends(current_user)) -> list[AlertResponse]:
    if animal_id:
        authorize_animal(user, animal_id)
    ids = visible_ids(user)
    return [AlertResponse(**alert) for alert in Repository().list_alerts(animal_id) if alert["animal_id"] in ids]


@app.get("/api/v1/notifications")
def list_notifications(animal_id: str | None = None, user=Depends(current_user)) -> list[dict]:
    if animal_id:
        authorize_animal(user, animal_id)
    ids = visible_ids(user)
    return [item for item in Repository().list_notifications(animal_id) if item["animal_id"] in ids]


@app.post("/api/v1/predictions", response_model=PredictionResponse)
def predict(request: PredictionRequest, user=Depends(current_user)) -> PredictionResponse:
    try:
        return PredictionService().predict(request)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/v1/animals/{animal_id}/measurements", response_model=MeasurementResponse, status_code=201)
def record_measurement(animal_id: str, request: PredictionRequest, user=Depends(current_user)) -> MeasurementResponse:
    authorize_animal(user, animal_id, write=True)
    animal = next((animal for animal in Repository().list_animals() if animal["animal_id"] == animal_id), None)
    if not animal:
        raise HTTPException(status_code=404, detail="animal not found")
    if animal.get("species", "bovine_adult") != "bovine_adult":
        raise HTTPException(status_code=422, detail="El modelo de mastitis solo está disponible para bovinas adultas.")
    try:
        return MeasurementService().record(animal_id, request)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/v1/simulations", response_model=SimulationResponse)
def simulate(request: SimulationRequest, user=Depends(current_user)) -> SimulationResponse:
    if user["role"] != "productor":
        raise HTTPException(403, "La simulación está disponible para productores")
    if request.animal_id is not None:
        authorize_animal(user, request.animal_id, write=True)
        animal = next((animal for animal in Repository().list_animals() if animal["animal_id"] == request.animal_id), None)
        if not animal:
            raise HTTPException(status_code=404, detail="animal not found")
        if animal.get("species", "bovine_adult") != "bovine_adult":
            raise HTTPException(status_code=422, detail="El modelo de mastitis solo está disponible para bovinas adultas.")
    try:
        reading = CattleSimulator().generate(request.scenario, request.seed)
        prediction = PredictionService().predict(reading)
        measurement_id = None
        if request.animal_id is not None:
            repository = Repository()
            if not repository.animal_exists(request.animal_id):
                raise HTTPException(status_code=404, detail="animal not found")
            stored = repository.save_measurement(
                animal_id=request.animal_id,
                payload=reading.model_dump(),
                risk_level=prediction.risk_level,
                probability=prediction.probability,
                model=prediction.model,
            )
            NotificationService(repository).dispatch_for_prediction(stored["prediction_id"])
            measurement_id = stored["measurement_id"]
        return SimulationResponse(
            scenario=request.scenario,
            seed=request.seed,
            animal_id=request.animal_id,
            measurement_id=measurement_id,
            reading=reading,
            prediction=prediction,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
