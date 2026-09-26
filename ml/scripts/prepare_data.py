"""Script base para preparar la semilla real de datos del proyecto My Ganado.

Este archivo es un esqueleto inicial del pipeline de limpieza. Debe usarse para:
- cargar un dataset real desde ml/data/raw/
- eliminar duplicados y valores inconsistentes
- tratar faltantes
- normalizar nombres y tipos
- guardar una versión limpia en ml/data/cleaned/
- dejar la data procesada lista para entrenamiento en ml/data/processed/

Importante: nunca modificar el dataset original en raw.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
CLEANED_DIR = Path(__file__).resolve().parents[1] / "data" / "cleaned"
PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"


def ensure_directories() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def find_raw_dataset() -> Path | None:
    if not RAW_DIR.exists():
        return None

    csv_files = sorted(RAW_DIR.glob("*.csv"))
    for csv_file in csv_files:
        if csv_file.stat().st_size <= 0:
            continue
        try:
            preview = pd.read_csv(csv_file, nrows=3)
        except Exception:
            continue
        if not preview.empty and preview.shape[1] > 0:
            return csv_file

    return None


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "Cow_ID": "cow_id",
        "Day": "day",
        "Breed": "breed",
        "Months after giving birth": "months_after_giving_birth",
        "Previous_Mastits_status": "previous_mastitis_status",
        "IUFL": "iu_fl",
        "EUFL": "eu_fl",
        "IUFR": "iu_fr",
        "EUFR": "eu_fr",
        "IURL": "iu_rl",
        "EURL": "eu_rl",
        "IURR": "iu_rr",
        "EURR": "eu_rr",
        "Temperature": "temperature",
        "Hardness": "hardness",
        "Pain": "pain",
        "Milk_visibility": "milk_visibility",
        "class1": "risk_level",
    }
    normalized = df.rename(columns=rename_map)
    if "risk_level" in normalized.columns:
        normalized["risk_level"] = normalized["risk_level"].map({0: "BAJO", 1: "ALTO"})
    return normalized


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned = cleaned.drop_duplicates()
    cleaned = cleaned.replace({"": pd.NA})

    if "risk_level" in cleaned.columns:
        cleaned = cleaned.dropna(subset=["risk_level"])

    if "cow_id" in cleaned.columns:
        cleaned = cleaned.drop(columns=["cow_id"])

    return cleaned.reset_index(drop=True)


def save_cleaned_data(cleaned: pd.DataFrame) -> None:
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    cleaned_path = CLEANED_DIR / "cattle_mastitis_cleaned.csv"
    processed_path = PROCESSED_DIR / "cattle_mastitis_processed.csv"

    cleaned.to_csv(cleaned_path, index=False)
    cleaned.to_csv(processed_path, index=False)

    print(f"Saved cleaned dataset to: {cleaned_path}")
    print(f"Saved processed dataset to: {processed_path}")


def main() -> None:
    ensure_directories()
    dataset_path = find_raw_dataset()
    if dataset_path is None:
        print("No CSV dataset found in ml/data/raw.")
        return

    print(f"Reading raw dataset: {dataset_path}")
    raw_df = pd.read_csv(dataset_path)
    normalized = normalize_columns(raw_df)
    cleaned = clean_dataset(normalized)

    print(f"Original rows: {len(raw_df)}")
    print(f"Cleaned rows: {len(cleaned)}")
    print(f"Columns: {list(cleaned.columns)}")

    save_cleaned_data(cleaned)


if __name__ == "__main__":
    main()
