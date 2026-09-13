"""Train and compare commit quality classifiers."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any, Dict, Tuple

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

from src.features import QUALITY_LABELS, build_model_pipeline, prepare_feature_frame
from src.utils import ensure_parent, project_path, write_json


DEFAULT_DATASET_PATH = project_path("data", "processed", "commit_dataset.csv")
DEFAULT_MODEL_PATH = project_path("models", "best_model.pkl")
DEFAULT_METRICS_PATH = project_path("models", "metrics.json")


def load_training_data(dataset_path: Path, *, allow_weak_labels: bool = False) -> pd.DataFrame:
    """Load labeled training data and keep labels separate from input features."""
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    frame = pd.read_csv(dataset_path)
    if "quality_category" not in frame.columns:
        raise ValueError("Dataset must include a quality_category target column.")

    frame["quality_category"] = frame["quality_category"].fillna("").astype(str).str.strip()
    if "label_source" not in frame.columns:
        frame["label_source"] = "manual"
    frame["label_source"] = frame["label_source"].fillna("").astype(str).str.strip().str.lower()

    if allow_weak_labels:
        allowed_sources = {"manual", "human", "weak_rule"}
    else:
        allowed_sources = {"manual", "human"}

    labeled = frame[
        frame["quality_category"].isin(QUALITY_LABELS) & frame["label_source"].isin(allowed_sources)
    ].copy()
    if labeled.empty:
        if allow_weak_labels:
            raise ValueError("No usable labeled rows found. Add quality_category labels before training.")
        raise ValueError(
            "No manual labels found. Fill data/processed/manual_label_template.csv or rerun with "
            "--allow-weak-labels for a transparent bootstrap model."
        )

    labeled = prepare_feature_frame(labeled)
    if labeled["quality_category"].nunique() < 2:
        raise ValueError("Training requires at least two quality categories.")
    return labeled


def candidate_models() -> Dict[str, Any]:
    """Return the classifiers compared during training."""
    return {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        "linear_svm": LinearSVC(class_weight="balanced", random_state=42),
        "naive_bayes": MultinomialNB(),
        "random_forest": RandomForestClassifier(n_estimators=120, class_weight="balanced", random_state=42),
    }


def _can_stratify(labels: pd.Series, test_size: float) -> bool:
    """Check whether sklearn can safely stratify a split."""
    class_count = labels.nunique()
    if class_count < 2 or labels.value_counts().min() < 2:
        return False
    test_count = math.ceil(len(labels) * test_size)
    train_count = len(labels) - test_count
    return test_count >= class_count and train_count >= class_count


def split_dataset(frame: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split the data into train, validation, and test sets."""
    test_size = 0.30 if len(frame) >= 10 else 0.34
    stratify = frame["quality_category"] if _can_stratify(frame["quality_category"], test_size) else None
    train_frame, temp_frame = train_test_split(
        frame,
        test_size=test_size,
        random_state=42,
        stratify=stratify,
    )

    if len(temp_frame) < 4:
        return train_frame, temp_frame.iloc[0:0].copy(), temp_frame

    stratify_temp = temp_frame["quality_category"] if _can_stratify(temp_frame["quality_category"], 0.5) else None
    validation_frame, test_frame = train_test_split(
        temp_frame,
        test_size=0.5,
        random_state=42,
        stratify=stratify_temp,
    )
    return train_frame, validation_frame, test_frame


def _evaluate_predictions(y_true: pd.Series, y_pred: Any) -> Dict[str, Any]:
    """Calculate classification metrics for one prediction set."""
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "classification_report": classification_report(y_true, y_pred, output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=QUALITY_LABELS).tolist(),
        "labels": QUALITY_LABELS,
    }


def train_from_dataset(
    dataset_path: Path = DEFAULT_DATASET_PATH,
    *,
    model_path: Path = DEFAULT_MODEL_PATH,
    metrics_path: Path = DEFAULT_METRICS_PATH,
    allow_weak_labels: bool = False,
) -> Dict[str, Any]:
    """Train candidate models, select the best validation performer, and save it."""
    data = load_training_data(dataset_path, allow_weak_labels=allow_weak_labels)
    train_frame, validation_frame, test_frame = split_dataset(data)

    model_results: Dict[str, Dict[str, Any]] = {}
    trained_candidates: Dict[str, Any] = {}
    score_frame = validation_frame if not validation_frame.empty else test_frame

    for name, estimator in candidate_models().items():
        pipeline = build_model_pipeline(estimator)
        pipeline.fit(train_frame, train_frame["quality_category"])
        predictions = pipeline.predict(score_frame)
        metrics = _evaluate_predictions(score_frame["quality_category"], predictions)
        model_results[name] = {
            "selection_accuracy": metrics["accuracy"],
            "selection_macro_f1": metrics["macro_f1"],
            "selection_set": "validation" if not validation_frame.empty else "test",
        }
        trained_candidates[name] = pipeline

    best_name = max(model_results, key=lambda name: model_results[name]["selection_macro_f1"])
    final_train_frame = (
        pd.concat([train_frame, validation_frame], ignore_index=True) if not validation_frame.empty else train_frame
    )
    best_pipeline = build_model_pipeline(candidate_models()[best_name])
    best_pipeline.fit(final_train_frame, final_train_frame["quality_category"])
    test_predictions = best_pipeline.predict(test_frame)
    test_metrics = _evaluate_predictions(test_frame["quality_category"], test_predictions)

    artifact = {
        "pipeline": best_pipeline,
        "model_name": best_name,
        "feature_columns": list(final_train_frame.columns),
        "label_policy": "manual_or_human" if not allow_weak_labels else "manual_human_or_weak_rule",
        "trained_rows": int(len(final_train_frame)),
        "test_rows": int(len(test_frame)),
    }
    ensure_parent(model_path)
    joblib.dump(artifact, model_path)

    metrics_payload = {
        "best_model": best_name,
        "candidate_models": model_results,
        "test_metrics": test_metrics,
        "row_counts": {
            "total_labeled_rows": int(len(data)),
            "train_rows": int(len(train_frame)),
            "validation_rows": int(len(validation_frame)),
            "test_rows": int(len(test_frame)),
        },
        "label_policy": artifact["label_policy"],
        "note": (
            "Metrics are computed from the provided labels. If weak_rule labels were allowed, "
            "these numbers validate the bootstrap rubric, not human review quality."
        ),
    }
    write_json(metrics_path, metrics_payload)
    return metrics_payload


def _path(value: str) -> Path:
    """Resolve a CLI path."""
    return Path(value).expanduser().resolve()


def build_parser() -> argparse.ArgumentParser:
    """Create the train.py CLI parser."""
    parser = argparse.ArgumentParser(description="Train commit quality ML models.")
    parser.add_argument("--dataset-path", type=_path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--model-path", type=_path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--metrics-path", type=_path, default=DEFAULT_METRICS_PATH)
    parser.add_argument(
        "--allow-weak-labels",
        action="store_true",
        help="Allow transparent weak_rule labels when manual labels are unavailable.",
    )
    return parser


def main() -> None:
    """Run training from the command line."""
    args = build_parser().parse_args()
    metrics = train_from_dataset(
        args.dataset_path,
        model_path=args.model_path,
        metrics_path=args.metrics_path,
        allow_weak_labels=args.allow_weak_labels,
    )
    print(f"Best model: {metrics['best_model']}")
    print(f"Test accuracy: {metrics['test_metrics']['accuracy']:.3f}")
    print(f"Test macro F1: {metrics['test_metrics']['macro_f1']:.3f}")


if __name__ == "__main__":
    main()

