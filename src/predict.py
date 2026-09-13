"""Prediction and suggestion engine for commit quality review."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Mapping

import joblib
import numpy as np

from src.features import (
    GENERIC_MESSAGES,
    extract_basic_features,
    heuristic_review_score,
    prepare_feature_frame,
    quality_category_from_score,
)
from src.preprocessing import clean_commit_message, tokenize
from src.utils import project_path


DEFAULT_MODEL_PATH = project_path("models", "best_model.pkl")


class CommitQualityPredictor:
    """Load a saved model once and use it for real-time predictions."""

    def __init__(self, model_path: Path = DEFAULT_MODEL_PATH):
        self.model_path = model_path
        self.artifact: Dict[str, Any] | None = None
        self.load_error: str | None = None
        self.load()

    @property
    def is_model_loaded(self) -> bool:
        """Return whether the sklearn model is available."""
        return self.artifact is not None

    def load(self) -> None:
        """Load the saved model from disk."""
        if not self.model_path.exists():
            self.artifact = None
            self.load_error = f"Model file not found: {self.model_path}"
            return
        try:
            self.artifact = joblib.load(self.model_path)
            self.load_error = None
        except Exception as exc:  # pragma: no cover - defensive runtime path
            self.artifact = None
            self.load_error = f"Could not load model: {exc}"

    def predict_commit(self, record: Mapping[str, Any]) -> Dict[str, Any]:
        """Predict quality, score, reasons, and suggestions for one commit."""
        frame = prepare_feature_frame([record])
        features = extract_basic_features(record)

        if self.artifact is None:
            review_score = heuristic_review_score(record)
            category = quality_category_from_score(review_score)
            confidence = 0.0
            model_status = "rule_fallback_no_saved_model"
            model_name = "heuristic_fallback"
        else:
            pipeline = self.artifact["pipeline"]
            category = str(pipeline.predict(frame)[0])
            confidence = _prediction_confidence(pipeline, frame)
            review_score = score_from_category_and_rules(category, record)
            model_status = "model_loaded"
            model_name = str(self.artifact.get("model_name", "unknown"))

        reasons = build_reasons(features, category, review_score)
        suggestions = build_suggestions(features)

        return {
            "commit_message": record.get("commit_message", ""),
            "commit_sha": record.get("commit_id", ""),
            "author": record.get("author", "Unknown"),
            "date": record.get("commit_date", ""),
            "files_changed": int(features["files_changed"]),
            "lines_added": int(features["lines_added"]),
            "lines_deleted": int(features["lines_deleted"]),
            "file_types": features["file_types"],
            "has_issue": bool(features["has_issue"]),
            "has_pr": bool(features["has_pr"]),
            "quality_category": category,
            "review_score": int(review_score),
            "confidence": confidence,
            "reasons": reasons,
            "suggestions": suggestions,
            "model_status": model_status,
            "model_name": model_name,
            "html_url": record.get("html_url", ""),
        }


def _prediction_confidence(pipeline: Any, frame: Any) -> float:
    """Return a confidence-like value when the classifier supports it."""
    if hasattr(pipeline, "predict_proba"):
        probabilities = pipeline.predict_proba(frame)[0]
        return float(max(probabilities))
    if hasattr(pipeline, "decision_function"):
        scores = pipeline.decision_function(frame)
        scores_array = np.asarray(scores[0] if np.asarray(scores).ndim > 1 else scores, dtype=float)
        exp_scores = np.exp(scores_array - np.max(scores_array))
        total = float(exp_scores.sum())
        return float(exp_scores.max() / total) if total else 0.0
    return 0.0


def score_from_category_and_rules(category: str, record: Mapping[str, Any]) -> int:
    """Create a practical 1-10 score from the predicted class and transparent rules."""
    category_base = {"Poor": 3, "Average": 6, "Good": 8}.get(category, 5)
    heuristic = heuristic_review_score(record)
    combined = round((category_base * 0.65) + (heuristic * 0.35))
    return max(1, min(10, int(combined)))


def build_reasons(features: Mapping[str, Any], category: str, review_score: int) -> List[str]:
    """Build human-readable reasons for a prediction."""
    reasons: List[str] = []
    clean_message = clean_commit_message(features.get("commit_message", ""), drop_stop_words=False)
    tokens = tokenize(clean_message)

    if not tokens:
        reasons.append("Commit message is empty after preprocessing.")
    elif clean_message in GENERIC_MESSAGES or len(tokens) <= 1:
        reasons.append("Commit message is too generic to explain the change.")
    elif features.get("word_count", 0) >= 5:
        reasons.append("Commit message gives a useful amount of detail.")
    else:
        reasons.append("Commit message has some context but could be more specific.")

    if features.get("has_action_word"):
        reasons.append("Message includes a clear action word.")
    else:
        reasons.append("Message does not clearly state the action taken.")

    if features.get("has_description"):
        reasons.append("Message includes extra description or enough subject detail.")
    if features.get("has_issue") or features.get("has_pr"):
        reasons.append("Commit is linked to an issue or pull request context.")
    if features.get("files_changed", 0) and features.get("total_changes", 0):
        reasons.append(
            f"Metadata shows {features['files_changed']} file(s) changed with "
            f"{features['total_changes']} total line changes."
        )

    reasons.append(f"Predicted category is {category} with a practical score of {review_score}/10.")
    return reasons


def build_suggestions(features: Mapping[str, Any]) -> List[str]:
    """Build simple rule-based improvement suggestions."""
    suggestions: List[str] = []
    clean_message = clean_commit_message(features.get("commit_message", ""), drop_stop_words=False)
    tokens = tokenize(clean_message)

    if not tokens:
        suggestions.append("Write a concise subject that describes what changed.")
    elif clean_message in GENERIC_MESSAGES or len(tokens) <= 2:
        suggestions.append("Use a more descriptive commit message, such as 'Fix login token refresh error'.")
    elif len(tokens) < 5:
        suggestions.append("Add the affected area or behavior to make the message more specific.")

    if not features.get("has_action_word"):
        suggestions.append("Start with an action word such as fix, add, refactor, remove, or update.")
    if not features.get("has_issue") and not features.get("has_pr"):
        suggestions.append("Add an issue or PR reference when the project uses one.")
    if not features.get("has_description") and int(features.get("total_changes", 0)) > 100:
        suggestions.append("For larger changes, add a short body explaining why the change was needed.")

    if not suggestions:
        suggestions.append("Commit message is clear and descriptive.")
    return suggestions


def predict_record(record: Mapping[str, Any], model_path: Path = DEFAULT_MODEL_PATH) -> Dict[str, Any]:
    """Convenience function for predicting one commit record."""
    return CommitQualityPredictor(model_path=model_path).predict_commit(record)


def _sigmoid(value: float) -> float:
    """Return a sigmoid value."""
    return 1 / (1 + math.exp(-value))

