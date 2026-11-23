from pathlib import Path

import joblib
import json
import numpy as np
import pandas as pd

from app.models.schemas import PredictionRequest, PredictionResponse

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "risk_model.joblib"
METADATA_PATH = MODEL_PATH.with_suffix(".json")


# Threshold for mapping binary model output to 3-level risk system
_RISK_CONFIDENCE_THRESHOLD = 0.7


class PredictionService:
    def __init__(self) -> None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model artifact not found: {MODEL_PATH}")
        self.model = joblib.load(MODEL_PATH)
        self.metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8")) if METADATA_PATH.exists() else {}
        self.model_name = self.metadata.get("model", "Modelo entrenado")

    def _classify_risk_level(self, model_label: str, probability: float) -> str:
        """Map binary model output (BAJO/ALTO) to 3-level risk system (BAJO/MEDIO/ALTO).

        The model was trained as binary classification (BAJO/ALTO). MEDIO is assigned
        when the model's confidence is at most 0.7. This is an uncertainty band,
        not a clinically validated severity grade.
        """
        if model_label == "BAJO":
            if probability > _RISK_CONFIDENCE_THRESHOLD:
                # High confidence BAJO -> return BAJO
                return "BAJO"
            return "MEDIO"
        if model_label == "ALTO":
            if probability > _RISK_CONFIDENCE_THRESHOLD:
                # High confidence ALTO -> return ALTO
                return "ALTO"
            return "MEDIO"
        return "MEDIO"

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        features = pd.DataFrame([request.model_dump(include=set(self.metadata.get("features", type(request).model_fields)))])
        model_label = str(self.model.predict(features)[0])
        probabilities = self.model.predict_proba(features)[0]
        classes = [str(value) for value in self.model.named_steps["model"].classes_]
        probability = float(probabilities[classes.index(model_label)])

        risk_level = self._classify_risk_level(model_label, probability)

        return PredictionResponse(
            risk_level=risk_level,
            model_label=model_label,
            probability=round(probability, 4),
            model=self.model_name,
            disclaimer="Resultado de apoyo para seguimiento; no constituye un diagnostico veterinario.",
        )
