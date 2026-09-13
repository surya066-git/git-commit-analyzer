"""Feature engineering for commit text and Git metadata."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder

from src.preprocessing import clean_commit_message, first_line, tokenize


QUALITY_LABELS = ["Poor", "Average", "Good"]

NUMERIC_FEATURES = [
    "message_length",
    "word_count",
    "files_changed",
    "lines_added",
    "lines_deleted",
    "total_changes",
    "has_issue",
    "has_pr",
    "has_description",
    "has_action_word",
]

CATEGORICAL_FEATURES = ["commit_type", "file_types"]
TEXT_FEATURE = "commit_message"
FEATURE_COLUMNS = [TEXT_FEATURE, *NUMERIC_FEATURES, *CATEGORICAL_FEATURES]

ACTION_WORDS = {
    "add",
    "allow",
    "build",
    "change",
    "clean",
    "create",
    "delete",
    "disable",
    "document",
    "enable",
    "fix",
    "handle",
    "implement",
    "improve",
    "move",
    "prevent",
    "refactor",
    "remove",
    "rename",
    "replace",
    "resolve",
    "restore",
    "support",
    "test",
    "update",
    "upgrade",
    "validate",
}

GENERIC_MESSAGES = {
    "change",
    "changes",
    "fix",
    "fixed",
    "misc",
    "stuff",
    "update",
    "updated",
    "work",
    "wip",
}

CONVENTIONAL_TYPES = {
    "feat": "feature",
    "feature": "feature",
    "fix": "bugfix",
    "bugfix": "bugfix",
    "docs": "documentation",
    "doc": "documentation",
    "style": "style",
    "refactor": "refactor",
    "perf": "performance",
    "test": "test",
    "tests": "test",
    "build": "build",
    "ci": "ci",
    "chore": "chore",
    "revert": "revert",
}

ISSUE_REFERENCE_PATTERN = re.compile(
    r"(#\d+|\b[A-Z][A-Z0-9]+-\d+\b|\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#?\d+)",
    flags=re.IGNORECASE,
)


def _as_mapping(record: Mapping[str, Any] | pd.Series) -> Dict[str, Any]:
    """Convert dict-like rows to a normal dictionary."""
    if isinstance(record, pd.Series):
        return record.to_dict()
    return dict(record)


def safe_int(value: Any, default: int = 0) -> int:
    """Convert unknown numeric values to an integer safely."""
    try:
        if pd.isna(value):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def extract_file_types(file_names: Iterable[str] | str | None) -> str:
    """Return a stable space-separated list of changed file extensions."""
    if not file_names:
        return "unknown"

    if isinstance(file_names, str):
        candidates = [item.strip() for item in re.split(r"[,;\n|]", file_names) if item.strip()]
    else:
        candidates = [str(item).strip() for item in file_names if str(item).strip()]

    types: set[str] = set()
    for file_name in candidates:
        suffix = Path(file_name).suffix.lower().lstrip(".")
        if suffix:
            types.add(suffix)
        elif "/" in file_name:
            types.add(file_name.split("/", 1)[0].lower())

    return " ".join(sorted(types)) if types else "unknown"


def detect_commit_type(message: object) -> str:
    """Infer a simple commit type from conventional prefixes or keywords."""
    subject = first_line(message).lower()
    match = re.match(r"^([a-z]+)(?:\([^)]+\))?!?:", subject)
    if match:
        return CONVENTIONAL_TYPES.get(match.group(1), match.group(1))

    clean_message = clean_commit_message(subject, drop_stop_words=False)
    tokens = tokenize(clean_message)
    if not tokens:
        return "unknown"

    first_token = tokens[0]
    if first_token in {"merge"}:
        return "merge"
    if first_token in {"revert"}:
        return "revert"
    if first_token in {"fix", "resolve", "repair"}:
        return "bugfix"
    if first_token in {"add", "create", "implement", "support", "enable"}:
        return "feature"
    if first_token in {"doc", "docs", "document"}:
        return "documentation"
    if first_token in {"test", "tests"}:
        return "test"
    if first_token in {"refactor", "clean"}:
        return "refactor"
    if first_token in {"build", "ci"}:
        return first_token
    return "other"


def has_issue_reference(message: object) -> int:
    """Return 1 when a commit message references an issue or ticket."""
    if message is None:
        return 0
    return int(bool(ISSUE_REFERENCE_PATTERN.search(str(message))))


def has_description(message: object) -> int:
    """Return 1 when the commit contains a body or enough detail in the subject."""
    if message is None:
        return 0
    text = str(message).strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) > 1:
        return 1
    return int(len(tokenize(clean_commit_message(text))) >= 7)


def has_action_word(message: object) -> int:
    """Return 1 when the message includes a clear action verb."""
    tokens = tokenize(clean_commit_message(message, drop_stop_words=False))
    return int(any(token in ACTION_WORDS for token in tokens))


def extract_basic_features(record: Mapping[str, Any] | pd.Series) -> Dict[str, Any]:
    """Build text and Git metadata features for one commit record."""
    row = _as_mapping(record)
    message = row.get("commit_message", "")
    changed_files = row.get("changed_files") or row.get("file_names") or row.get("files") or []
    lines_added = safe_int(row.get("lines_added", row.get("additions", 0)))
    lines_deleted = safe_int(row.get("lines_deleted", row.get("deletions", 0)))
    files_changed = safe_int(row.get("files_changed", 0))

    if not files_changed and changed_files:
        if isinstance(changed_files, str):
            files_changed = len([item for item in re.split(r"[,;\n|]", changed_files) if item.strip()])
        else:
            files_changed = len(list(changed_files))

    clean_message = clean_commit_message(message)
    return {
        "commit_message": str(message or ""),
        "clean_message": clean_message,
        "message_length": len(first_line(message)),
        "word_count": len(tokenize(clean_message)),
        "files_changed": files_changed,
        "lines_added": lines_added,
        "lines_deleted": lines_deleted,
        "total_changes": lines_added + lines_deleted,
        "file_types": extract_file_types(changed_files),
        "has_issue": safe_int(row.get("has_issue", has_issue_reference(message))),
        "has_pr": safe_int(row.get("has_pr", 0)),
        "commit_type": str(row.get("commit_type") or detect_commit_type(message)),
        "has_description": safe_int(row.get("has_description", has_description(message))),
        "has_action_word": safe_int(row.get("has_action_word", has_action_word(message))),
    }


def prepare_feature_frame(records: Iterable[Mapping[str, Any] | pd.Series] | pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame containing all model features and any existing labels."""
    if isinstance(records, pd.DataFrame):
        iterable = records.to_dict(orient="records")
    else:
        iterable = list(records)

    rows: List[Dict[str, Any]] = []
    for record in iterable:
        base = _as_mapping(record)
        base.update(extract_basic_features(base))
        rows.append(base)

    frame = pd.DataFrame(rows)
    for column in FEATURE_COLUMNS:
        if column not in frame.columns:
            frame[column] = "" if column in CATEGORICAL_FEATURES or column == TEXT_FEATURE else 0

    for column in NUMERIC_FEATURES:
        frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0)
    for column in CATEGORICAL_FEATURES + [TEXT_FEATURE]:
        frame[column] = frame[column].fillna("").astype(str)
    return frame


def quality_category_from_score(score: int) -> str:
    """Map a 1-10 review score to the three project categories."""
    if score <= 4:
        return "Poor"
    if score <= 7:
        return "Average"
    return "Good"


def heuristic_review_score(record: Mapping[str, Any] | pd.Series) -> int:
    """Score a commit with transparent rules for bootstrapping or suggestions."""
    row = extract_basic_features(record)
    subject = clean_commit_message(row["commit_message"], drop_stop_words=False)
    tokens = tokenize(subject)
    score = 5

    if not tokens:
        score -= 4
    elif subject.startswith("merge pull request"):
        score -= 3
    elif subject in GENERIC_MESSAGES or len(tokens) <= 1:
        score -= 3
    elif len(tokens) <= 3:
        score -= 1
    elif len(tokens) >= 6:
        score += 1

    if row["has_action_word"]:
        score += 1
    else:
        score -= 1

    if row["has_description"]:
        score += 1
    if row["has_issue"] or row["has_pr"]:
        score += 1
    if not row["has_action_word"] and not row["has_issue"] and not row["has_pr"] and not row["has_description"]:
        score -= 1
    if row["files_changed"] > 20 or row["total_changes"] > 1500:
        score -= 1

    return max(1, min(10, score))


def weak_label_record(record: Mapping[str, Any] | pd.Series) -> Dict[str, Any]:
    """Attach transparent weak labels for demos when human labels are not ready."""
    score = heuristic_review_score(record)
    return {
        "quality_category": quality_category_from_score(score),
        "review_score": score,
        "label_source": "weak_rule",
    }


def make_one_hot_encoder() -> OneHotEncoder:
    """Create a OneHotEncoder that works across recent sklearn versions."""
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=True)
    except TypeError:  # pragma: no cover - sklearn < 1.2
        return OneHotEncoder(handle_unknown="ignore", sparse=True)


def build_model_pipeline(estimator: Any) -> Pipeline:
    """Build a TF-IDF plus metadata sklearn pipeline."""
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", MinMaxScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", make_one_hot_encoder()),
        ]
    )

    transformer = ColumnTransformer(
        transformers=[
            (
                "message_tfidf",
                TfidfVectorizer(
                    preprocessor=clean_commit_message,
                    ngram_range=(1, 2),
                    max_features=5000,
                    min_df=1,
                ),
                TEXT_FEATURE,
            ),
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )

    return Pipeline(steps=[("features", transformer), ("model", estimator)])
