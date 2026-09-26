from pathlib import Path

import joblib
import pandas as pd

from app.models.schemas import PredictionRequest, PredictionResponse

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "risk_model.joblib"


class PredictionService:
    def __init__(self) -> None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model artifact not found: {MODEL_PATH}")
        self.model = joblib.load(MODEL_PATH)

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        features = pd.DataFrame([request.model_dump()])
        model_label = str(self.model.predict(features)[0])
        probabilities = self.model.predict_proba(features)[0]
        classes = [str(value) for value in self.model.named_steps["model"].classes_]
        probability = float(probabilities[classes.index(model_label)])

        return PredictionResponse(
            risk_level=model_label if model_label in {"BAJO", "MEDIO", "ALTO"} else "MEDIO",
            model_label=model_label,
            probability=probability,
            model="RandomForest",
            disclaimer="Resultado de apoyo para seguimiento; no constituye un diagnostico veterinario.",
        )
