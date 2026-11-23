"""Create a reproducible quality profile for the raw and cleaned cattle data."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ML_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ML_ROOT / "data" / "raw" / "cattle_mastitis.csv"
CLEAN_PATH = ML_ROOT / "data" / "cleaned" / "cattle_mastitis_cleaned.csv"
OUTPUT_PATH = ML_ROOT.parent / "docs" / "DATASET_PROFILE.md"


def profile_frame(frame: pd.DataFrame, target: str) -> dict:
    result = {
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "missing_cells": int(frame.isna().sum().sum()),
        "duplicate_rows": int(frame.duplicated().sum()),
        "classes": {str(key): int(value) for key, value in frame[target].value_counts(dropna=False).items()},
    }
    if "cow_id" in frame.columns:
        result["animals"] = int(frame["cow_id"].nunique())
        without_id = frame.drop(columns=["cow_id"])
        result["duplicate_rows_without_animal_id"] = int(without_id.duplicated().sum())
    if "breed" in frame.columns:
        result["breeds"] = {str(key): int(value) for key, value in frame["breed"].value_counts(dropna=False).items()}
    numeric = frame.select_dtypes(include="number")
    result["numeric_ranges"] = {
        str(column): {"min": float(numeric[column].min()), "max": float(numeric[column].max())}
        for column in numeric.columns
    }
    result["class_percentages"] = {
        str(key): round(float(value / len(frame) * 100), 2)
        for key, value in frame[target].value_counts(dropna=False).items()
    }
    return result


def main() -> None:
    raw = pd.read_csv(RAW_PATH)
    cleaned = pd.read_csv(CLEAN_PATH)
    raw_profile = profile_frame(raw, "class1")
    cleaned_profile = profile_frame(cleaned, "risk_level")
    payload = {"raw": raw_profile, "cleaned": cleaned_profile}
    report = "# Perfil de calidad del dataset\n\n"
    report += "Generado por `ml/scripts/profile_data.py`. Los rangos son descriptivos y no representan umbrales clínicos.\n\n"
    report += "## Datos originales\n\n```json\n" + json.dumps(raw_profile, indent=2, ensure_ascii=False) + "\n```\n\n"
    report += "## Datos limpios\n\n```json\n" + json.dumps(cleaned_profile, indent=2, ensure_ascii=False) + "\n```\n\n"
    report += "## Interpretación y límites\n\n"
    report += "La etiqueta original es binaria (`0` normal, `1` mastitis) y se transforma en `BAJO`/`ALTO`; no hay clase `MEDIO`. "
    report += "Las mediciones repetidas por animal deben permanecer agrupadas al evaluar modelos. El identificador se conserva para esa partición y se excluye de las variables predictoras. "
    report += "La detección de duplicados se informa tanto con como sin `cow_id`, porque quitarlo puede hacer equivalentes observaciones de animales distintos. "
    report += "El dataset describe mastitis clínica y no representa por sí solo todas las enfermedades ni las condiciones ambientales del producto.\n"
    OUTPUT_PATH.write_text(report, encoding="utf-8")
    print(f"Saved dataset profile to {OUTPUT_PATH}")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
