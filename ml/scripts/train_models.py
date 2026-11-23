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
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
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
                Pipeline(steps=[("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]),
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
            max_iter=2000,
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
                "f1_macro": f1_score(y_test, y_pred, average="macro"),
                "precision_macro": precision_score(y_test, y_pred, average="macro", zero_division=0),
                "recall_macro": recall_score(y_test, y_pred, average="macro", zero_division=0),
                "confusion_matrix": confusion_matrix(y_test, y_pred, labels=sorted(set(y_test))).tolist(),
                "classes": sorted(set(y_test)),
                "report": classification_report(y_test, y_pred, zero_division=0, output_dict=True),
            }
        )

    return results


def train_and_save_selected_model(X: pd.DataFrame, y: pd.Series, evaluation: list[dict], split_strategy: str) -> None:
    selected = max(evaluation, key=lambda result: (result["f1_macro"], result["recall_macro"]))["model"]
    estimators = {
        "RandomForest": RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced"),
        "DecisionTree": DecisionTreeClassifier(random_state=42, class_weight="balanced"),
        "LogisticRegression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
    }
    model = Pipeline(
        steps=[
            ("preprocessor", build_model_pipeline(X, y)),
            ("model", estimators[selected]),
        ]
    )
    model.fit(X, y)
    MODEL_ROOT.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_ROOT / "risk_model.joblib")
    metadata = {
        "model": selected,
        "selection_rule": "highest grouped-test macro F1, then macro recall",
        "target": "risk_level",
        "features": X.columns.tolist(),
        "classes": model.named_steps["model"].classes_.tolist(),
        "source": "Mendeley Data: Clinical Mastitis in Cows based on Udder Parameter using IoT",
        "evaluation_split": split_strategy,
        "evaluation_metrics": [
            {key: value for key, value in result.items() if key != "report"}
            for result in evaluation
        ],
    }
    (MODEL_ROOT / "risk_model.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (MODEL_ROOT / "evaluation_metrics.json").write_text(
        json.dumps(
            {
                "split_strategy": split_strategy,
                "models": evaluation,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
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
    groups = df["cow_id"] if "cow_id" in df.columns else None
    X = df.drop(columns=[target_col, "cow_id"], errors="ignore")
    y = df[target_col]

    if y.isnull().any():
        raise ValueError("Target column contains null values. Clean the dataset before training.")

    if groups is not None:
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
        train_indices, test_indices = next(splitter.split(X, y, groups))
        X_train, X_test = X.iloc[train_indices], X.iloc[test_indices]
        y_train, y_test = y.iloc[train_indices], y.iloc[test_indices]
        split_strategy = "GroupShuffleSplit by cow_id (80/20; random_state=42)"
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y if y.nunique() > 1 else None,
        )
        split_strategy = "Stratified row split (cow_id unavailable; possible animal leakage)"

    results = evaluate_models(X_train, X_test, y_train, y_test)

    for result in results:
        print(f"\n=== {result['model']} ===")
        print(f"Accuracy: {result['accuracy']:.4f}")
        print(f"Weighted F1: {result['f1']:.4f}")
        print(f"Macro precision: {result['precision_macro']:.4f}")
        print(f"Macro recall: {result['recall_macro']:.4f}")
        print("Confusion Matrix:")
        print(result["confusion_matrix"])
        print("Classification Report:")
        print(result["report"])

    train_and_save_selected_model(X, y, results, split_strategy)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"Data validation error: {exc}")
        raise SystemExit(1)
