"""Evaluate a saved commit quality model on a labeled dataset."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict

import joblib
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from src.features import QUALITY_LABELS
from src.train import DEFAULT_DATASET_PATH, DEFAULT_MODEL_PATH, load_training_data
from src.utils import project_path, write_json


DEFAULT_EVALUATION_PATH = project_path("models", "evaluation.json")


def evaluate_saved_model(
    model_path: Path = DEFAULT_MODEL_PATH,
    dataset_path: Path = DEFAULT_DATASET_PATH,
    *,
    output_path: Path = DEFAULT_EVALUATION_PATH,
    allow_weak_labels: bool = False,
) -> Dict[str, Any]:
    """Load a saved model and calculate actual metrics on labeled rows."""
    artifact = joblib.load(model_path)
    pipeline = artifact["pipeline"]
    data = load_training_data(dataset_path, allow_weak_labels=allow_weak_labels)
    predictions = pipeline.predict(data)
    metrics = {
        "model_name": artifact.get("model_name", "unknown"),
        "accuracy": float(accuracy_score(data["quality_category"], predictions)),
        "macro_f1": float(f1_score(data["quality_category"], predictions, average="macro", zero_division=0)),
        "classification_report": classification_report(
            data["quality_category"],
            predictions,
            output_dict=True,
            zero_division=0,
        ),
        "confusion_matrix": confusion_matrix(data["quality_category"], predictions, labels=QUALITY_LABELS).tolist(),
        "labels": QUALITY_LABELS,
        "evaluated_rows": int(len(data)),
        "note": "These metrics are only as reliable as the labels in the dataset.",
    }
    write_json(output_path, metrics)
    return metrics


def _path(value: str) -> Path:
    """Resolve a CLI path."""
    return Path(value).expanduser().resolve()


def build_parser() -> argparse.ArgumentParser:
    """Create the evaluate.py CLI parser."""
    parser = argparse.ArgumentParser(description="Evaluate the saved commit quality model.")
    parser.add_argument("--model-path", type=_path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--dataset-path", type=_path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--output-path", type=_path, default=DEFAULT_EVALUATION_PATH)
    parser.add_argument("--allow-weak-labels", action="store_true")
    return parser


def main() -> None:
    """Run model evaluation from the command line."""
    args = build_parser().parse_args()
    metrics = evaluate_saved_model(
        args.model_path,
        args.dataset_path,
        output_path=args.output_path,
        allow_weak_labels=args.allow_weak_labels,
    )
    print(f"Accuracy: {metrics['accuracy']:.3f}")
    print(f"Macro F1: {metrics['macro_f1']:.3f}")


if __name__ == "__main__":
    main()

