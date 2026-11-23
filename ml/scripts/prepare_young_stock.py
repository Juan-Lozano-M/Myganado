"""Validate and prepare the secondary multi-species young-stock health data."""

from __future__ import annotations

import hashlib
import json
import csv
from collections import Counter
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ML_ROOT / "data" / "raw" / "young_stock" / "YSM_Animal_Health_Data.tab"
CLEAN_DIR = ML_ROOT / "data" / "cleaned" / "young_stock"
PROFILE_DIR = ML_ROOT / "data" / "processed" / "young_stock"


def main() -> None:
    with RAW_PATH.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        columns = [str(column).strip().lower() for column in (reader.fieldnames or [])]
        if "index" not in columns:
            raise ValueError("Expected the source row identifier column 'index'.")
        original_rows = []
        for source_row in reader:
            row = {str(key).strip().lower(): (value or "").strip() for key, value in source_row.items() if key is not None}
            if "species" in row:
                row["species"] = row["species"].lower() or ""
            original_rows.append(row)

    if not columns:
        raise ValueError("Expected the source row identifier column 'index'.")
    unique_rows = []
    seen_rows = set()
    for row in original_rows:
        key = tuple(row.get(column, "") for column in columns)
        if key not in seen_rows:
            seen_rows.add(key)
            unique_rows.append(row)
    duplicate_rows = len(original_rows) - len(unique_rows)

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    cleaned_path = CLEAN_DIR / "young_stock_health_cleaned.csv"
    profile_path = PROFILE_DIR / "young_stock_profile.json"
    with cleaned_path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(unique_rows)

    species_counts = Counter(row.get("species", "") or "unspecified" for row in unique_rows)
    missing_cells = sum(not row.get(column, "") for row in unique_rows for column in columns)
    temperature_values_for_review = Counter()
    for row in unique_rows:
        value = row.get("rectal_temp", "")
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            continue
        if numeric_value < 30 or numeric_value > 45:
            temperature_values_for_review[value] += 1

    profile = {
        "source": "Harvard Dataverse DOI 10.7910/DVN/E6EV2K",
        "license": "CC0-1.0",
        "source_file": RAW_PATH.name,
        "source_sha256": hashlib.sha256(RAW_PATH.read_bytes()).hexdigest(),
        "rows_before": len(original_rows),
        "rows_after_exact_deduplication": len(unique_rows),
        "exact_duplicate_rows_removed": duplicate_rows,
        "columns": len(columns),
        "missing_cells": missing_cells,
        "species_counts_including_missing": dict(species_counts),
        "rectal_temperature_values_outside_screening_range_30_45": dict(temperature_values_for_review),
        "target_status": "No single cross-species risk target defined; retain source diagnostic fields separately.",
        "output_csv": str(cleaned_path.relative_to(ML_ROOT.parent)),
    }
    profile_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(profile, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
