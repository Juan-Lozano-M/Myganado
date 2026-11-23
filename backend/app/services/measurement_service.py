from app.models.schemas import MeasurementResponse, PredictionRequest
from app.services.prediction_service import PredictionService
from app.services.repository import Repository
from app.services.notification_service import NotificationService


class MeasurementService:
    def __init__(self) -> None:
        self.repository = Repository()
        self.prediction_service = PredictionService()

    def record(self, animal_id: str, request: PredictionRequest) -> MeasurementResponse:
        prediction = self.prediction_service.predict(request)
        stored = self.repository.save_measurement(
            animal_id=animal_id,
            payload=request.model_dump(),
            risk_level=prediction.risk_level,
            probability=prediction.probability,
            model=prediction.model,
        )
        NotificationService(self.repository).dispatch_for_prediction(stored["prediction_id"])
        return MeasurementResponse(**stored, prediction=prediction)
