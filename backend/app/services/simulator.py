from typing import Literal

from app.models.schemas import PredictionRequest

Scenario = Literal["normal", "estres_ambiental", "posible_riesgo", "alto", "persistente"]


SCENARIO_OVERRIDES: dict[str, dict[str, float | int]] = {
    "normal": {
        "temperature": 38.5,
        "hardness": 0,
        "pain": 0,
        "milk_visibility": 0,
        "previous_mastitis_status": 0,
    },
    "estres_ambiental": {
        "temperature": 40.0,
        "hardness": 0,
        "pain": 0,
        "milk_visibility": 0,
        "previous_mastitis_status": 0,
    },
    "posible_riesgo": {
        "temperature": 41.5,
        "hardness": 1,
        "pain": 1,
        "milk_visibility": 1,
        "previous_mastitis_status": 1,
    },
    "alto": {
        "temperature": 43.0,
        "hardness": 1,
        "pain": 1,
        "milk_visibility": 1,
        "previous_mastitis_status": 1,
    },
    "persistente": {
        "temperature": 42.0,
        "hardness": 1,
        "pain": 1,
        "milk_visibility": 1,
        "previous_mastitis_status": 1,
    },
}


class CattleSimulator:
    def generate(self, scenario: Scenario, seed: int = 42) -> PredictionRequest:
        if scenario not in SCENARIO_OVERRIDES:
            raise ValueError(f"Unsupported scenario: {scenario}")

        offset = seed % 7
        values: dict[str, float | int | str] = {
            "day": 1 + offset,
            "breed": "Jersey",
            "months_after_giving_birth": 1,
            "iu_fl": 150 + offset,
            "eu_fl": 180 + offset,
            "iu_fr": 150 + offset,
            "eu_fr": 180 + offset,
            "iu_rl": 150 + offset,
            "eu_rl": 181 + offset,
            "iu_rr": 150 + offset,
            "eu_rr": 181 + offset,
        }
        values.update(SCENARIO_OVERRIDES[scenario])
        return PredictionRequest.model_validate(values)
