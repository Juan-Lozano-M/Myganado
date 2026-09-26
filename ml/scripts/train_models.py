"""Training pipeline for My Ganado ML models.

This is a working baseline for the next project phase:
- locate a real dataset under ml/data/
- validate that a target column exists
- prepare features and target
- train Random Forest, Decision Tree and Logistic Regression
- print metrics for evaluation

The file is intentionally conservative: if no real dataset is present yet,
this script exits with a clear guidance message instead of inventing data.
"""

from __future__ import annotations

from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data"
MODEL_ROOT = PROJECT_ROOT / "models"


def find_dataset() -> Path | None:
    """Find the first usable CSV dataset in the ML data folders."""
    candidate_dirs = [
        DATA_ROOT / "processed",
        DATA_ROOT / "cleaned",
        DATA_ROOT / "raw",
    ]

    for directory in candidate_dirs:
        if not directory.exists():
            continue
        for csv_file in sorted(directory.glob("*.csv")):
            if csv_file.stat().st_size <= 0:
                continue
            try:
                preview = pd.read_csv(csv_file, nrows=3)
            except Exception:
                continue
            if preview.empty or preview.shape[1] == 0:
                continue
            return csv_file

    return None


def pick_target_column(df: pd.DataFrame) -> str:
    candidates = [
        "risk_level",
        "risk",
        "nivel_riesgo",
        "target",
        "label",
        "class1",
        "class",
        "mastitis",
        "status",
    ]
    for candidate in candidates:
        if candidate in df.columns:
            return candidate

    for candidate in df.columns:
        if "class" in str(candidate).lower() or "risk" in str(candidate).lower() or "target" in str(candidate).lower():
            return candidate

    raise ValueError(
        "No target column found. Expected one of: "
        + ", ".join(candidates)
        + ". If the dataset does not have a direct risk label, document a derived target before training."
    )


def build_model_pipeline(X: pd.DataFrame, y: pd.Series):
    numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = [col for col in X.columns if col not in numeric_cols]

    transformers = []
    if numeric_cols:
        transformers.append(
            (
                "numeric",
                Pipeline(steps=[("imputer", SimpleImputer(strategy="median"))]),
                numeric_cols,
            )
        )
    if categorical_cols:
        transformers.append(
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_cols,
            )
        )

    preprocessor = ColumnTransformer(transformers=transformers, remainder="drop")
    return preprocessor


def evaluate_models(X_train, X_test, y_train, y_test):
    models = {
        "RandomForest": RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced",
        ),
        "DecisionTree": DecisionTreeClassifier(
            random_state=42,
            class_weight="balanced",
        ),
        "LogisticRegression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
        ),
    }

    results = []
    for name, model in models.items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", build_model_pipeline(X_train, y_train)),
                ("model", model),
            ]
        )
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        results.append(
            {
                "model": name,
                "accuracy": accuracy_score(y_test, y_pred),
                "f1": f1_score(y_test, y_pred, average="weighted"),
                "confusion_matrix": confusion_matrix(y_test, y_pred),
                "report": classification_report(y_test, y_pred),
            }
        )

    return results


def train_and_save_selected_model(X: pd.DataFrame, y: pd.Series) -> None:
    model = Pipeline(
        steps=[
            ("preprocessor", build_model_pipeline(X, y)),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=200,
                    random_state=42,
                    class_weight="balanced",
                ),
            ),
        ]
    )
    model.fit(X, y)
    MODEL_ROOT.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_ROOT / "risk_model.joblib")
    metadata = {
        "model": "RandomForest",
        "target": "risk_level",
        "features": X.columns.tolist(),
        "classes": model.named_steps["model"].classes_.tolist(),
        "source": "Mendeley Data: Clinical Mastitis in Cows based on Udder Parameter using IoT",
    }
    (MODEL_ROOT / "risk_model.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Saved selected model to: {MODEL_ROOT / 'risk_model.joblib'}")


def main() -> int:
    dataset_path = find_dataset()
    if dataset_path is None:
        print("No dataset found in ml/data/raw, ml/data/cleaned or ml/data/processed.")
        print("Add a real dataset CSV before running the training pipeline.")
        return 0

    print(f"Loading dataset: {dataset_path}")
    df = pd.read_csv(dataset_path)
    print(f"Rows: {len(df)}, columns: {list(df.columns)}")

    if df.empty:
        raise ValueError(f"Dataset {dataset_path} is empty and cannot be used for training.")

    target_col = pick_target_column(df)
    X = df.drop(columns=[target_col])
    y = df[target_col]

    if y.isnull().any():
        raise ValueError("Target column contains null values. Clean the dataset before training.")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y if y.nunique() > 1 else None,
    )

    results = evaluate_models(X_train, X_test, y_train, y_test)

    for result in results:
        print(f"\n=== {result['model']} ===")
        print(f"Accuracy: {result['accuracy']:.4f}")
        print(f"Weighted F1: {result['f1']:.4f}")
        print("Confusion Matrix:")
        print(result["confusion_matrix"])
        print("Classification Report:")
        print(result["report"])

    train_and_save_selected_model(X, y)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"Data validation error: {exc}")
        raise SystemExit(1)
