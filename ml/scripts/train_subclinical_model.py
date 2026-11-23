"""Train a separate binary model for subclinical mastitis in the Rwanda dataset.

This model is not interchangeable with the clinical mastitis model: it uses
farm questionnaire features and predicts CMT-screened subclinical status.
"""
from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

PROJECT = Path(__file__).resolve().parents[1]
RAW = PROJECT / "data" / "raw" / "rwanda_subclinical_mastitis.xlsx"
CSV = PROJECT / "data" / "processed" / "rwanda_subclinical_mastitis.csv"
MODEL_DIR = PROJECT / "models"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def read_first_sheet(path: Path) -> pd.DataFrame:
    """Read the downloaded XLSX with the standard library (no Excel engine needed)."""
    with zipfile.ZipFile(path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(node.text or "" for node in item.findall(".//m:t", NS))
                      for item in root.findall("m:si", NS)]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheet = workbook.find(".//m:sheet", NS)
        rel_id = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        target = next(item.attrib["Target"] for item in rels
                      if item.attrib["Id"] == rel_id)
        sheet_path = target.lstrip("/") if target.startswith("/") else "xl/" + target
        root = ET.fromstring(archive.read(sheet_path))
        rows = []
        for row in root.findall(".//m:sheetData/m:row", NS):
            values = {}
            for cell in row.findall("m:c", NS):
                ref = cell.attrib["r"]
                letters = "".join(ch for ch in ref if ch.isalpha())
                col = 0
                for char in letters:
                    col = col * 26 + ord(char.upper()) - 64
                node = cell.find("m:v", NS)
                value = node.text if node is not None else ""
                if cell.attrib.get("t") == "s" and value:
                    value = shared[int(value)]
                values[col - 1] = value
            if values:
                rows.append([values.get(i, "") for i in range(max(values) + 1)])
    return pd.DataFrame(rows[1:], columns=[str(c).strip() for c in rows[0]])


def main() -> None:
    if not RAW.exists():
        raise FileNotFoundError(f"Download the article's S1 XLSX to {RAW}")
    data = read_first_sheet(RAW)
    target = "Subclinical"
    if target not in data:
        raise ValueError(f"Expected target column {target!r}; found {list(data.columns)}")
    # In the source workbook, 1 denotes CMT-positive and 2 denotes negative.
    target_values = pd.to_numeric(data[target], errors="coerce")
    keep = target_values.isin([1, 2])
    data = data.loc[keep].copy()
    y = target_values.loc[keep].map({1: "MEDIO", 2: "BAJO"})
    X = data.drop(columns=[target])
    X = X.replace(r"^\s*$", pd.NA, regex=True)
    X = X.drop(columns=[c for c in X if X[c].nunique(dropna=True) <= 1])
    numeric = X.select_dtypes(include="number").columns.tolist()
    categorical = [column for column in X if column not in numeric]
    preprocess = ColumnTransformer([
        ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric),
        ("categorical", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                                  ("encode", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ], remainder="drop")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y)
    candidates = {
        "LogisticRegression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=42),
    }
    results = []
    for name, estimator in candidates.items():
        pipeline = Pipeline([("preprocessor", preprocess), ("model", estimator)])
        pipeline.fit(X_train, y_train)
        prediction = pipeline.predict(X_test)
        results.append({"name": name, "pipeline": pipeline,
                        "macro_f1": f1_score(y_test, prediction, average="macro"),
                        "accuracy": accuracy_score(y_test, prediction),
                        "confusion_matrix": confusion_matrix(y_test, prediction, labels=["BAJO", "MEDIO"]).tolist(),
                        "report": classification_report(y_test, prediction, labels=["BAJO", "MEDIO"], output_dict=True, zero_division=0)})
    selected = max(results, key=lambda item: item["macro_f1"])
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    CSV.parent.mkdir(parents=True, exist_ok=True)
    data.assign(target=y).to_csv(CSV, index=False)
    joblib.dump(selected["pipeline"], MODEL_DIR / "subclinical_mastitis_model.joblib")
    metrics = {"selected_model": selected["name"], "target": "CMT-screened subclinical mastitis",
               "mapping": {"source 1 positive": "MEDIO", "source 2 negative": "BAJO"},
               "source_rows": len(data), "class_counts": y.value_counts().to_dict(),
               "features": X.columns.tolist(), "split": "stratified 75/25, random_state=42",
               "accuracy": selected["accuracy"], "macro_f1": selected["macro_f1"],
               "confusion_matrix_labels": ["BAJO", "MEDIO"],
               "confusion_matrix": selected["confusion_matrix"], "classification_report": selected["report"],
               "candidates": [{"model": r["name"], "accuracy": r["accuracy"], "macro_f1": r["macro_f1"]} for r in results],
               "limitation": "Standalone questionnaire-based subclinical model; not compatible with the clinical mastitis API feature vector and does not predict ALTO."}
    (MODEL_DIR / "subclinical_mastitis_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
