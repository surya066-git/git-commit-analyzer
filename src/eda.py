"""Simple exploratory data analysis for the processed commit dataset."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

try:
    import seaborn as sns
except Exception:  # pragma: no cover - optional dependency fallback
    sns = None

from src.features import prepare_feature_frame
from src.train import DEFAULT_DATASET_PATH
from src.utils import project_path, write_json


DEFAULT_SUMMARY_PATH = project_path("data", "processed", "eda_summary.json")
DEFAULT_FIGURE_DIR = project_path("reports", "figures")


def run_eda(
    dataset_path: Path = DEFAULT_DATASET_PATH,
    *,
    summary_path: Path = DEFAULT_SUMMARY_PATH,
    figure_dir: Path = DEFAULT_FIGURE_DIR,
) -> Dict[str, Any]:
    """Analyze the processed dataset and generate simple charts."""
    frame = pd.read_csv(dataset_path)
    frame = prepare_feature_frame(frame)
    figure_dir.mkdir(parents=True, exist_ok=True)

    summary: Dict[str, Any] = {
        "rows": int(len(frame)),
        "columns": list(frame.columns),
        "missing_values": frame.isna().sum().to_dict(),
        "duplicate_commit_ids": int(frame["commit_id"].duplicated().sum()) if "commit_id" in frame.columns else 0,
        "message_length": frame["message_length"].describe().to_dict(),
        "word_count": frame["word_count"].describe().to_dict(),
        "files_changed": frame["files_changed"].describe().to_dict(),
        "lines_added": frame["lines_added"].describe().to_dict(),
        "lines_deleted": frame["lines_deleted"].describe().to_dict(),
        "commit_type_distribution": frame["commit_type"].value_counts().to_dict(),
    }
    if "quality_category" in frame.columns:
        summary["quality_distribution"] = frame["quality_category"].fillna("unlabeled").value_counts().to_dict()

    _bar_plot(frame, "quality_category", figure_dir / "quality_distribution.png")
    _hist_plot(frame, "message_length", figure_dir / "message_length_distribution.png")
    _hist_plot(frame, "files_changed", figure_dir / "files_changed_distribution.png")
    _hist_plot(frame, "lines_added", figure_dir / "lines_added_distribution.png")
    _hist_plot(frame, "lines_deleted", figure_dir / "lines_deleted_distribution.png")
    _correlation_plot(frame, figure_dir / "feature_correlation.png")
    _word_frequency_plot(frame, figure_dir / "word_frequency.png")

    write_json(summary_path, summary)
    return summary


def _bar_plot(frame: pd.DataFrame, column: str, path: Path) -> None:
    """Create a count bar plot."""
    if column not in frame.columns:
        return
    plt.figure(figsize=(7, 4))
    counts = frame[column].fillna("unlabeled").replace("", "unlabeled").value_counts()
    if sns:
        sns.barplot(x=counts.index, y=counts.values)
    else:
        plt.bar(counts.index, counts.values)
    plt.title(column.replace("_", " ").title())
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def _hist_plot(frame: pd.DataFrame, column: str, path: Path) -> None:
    """Create a histogram for a numeric feature."""
    if column not in frame.columns:
        return
    plt.figure(figsize=(7, 4))
    values = pd.to_numeric(frame[column], errors="coerce").fillna(0)
    if sns:
        sns.histplot(values, bins=20)
    else:
        plt.hist(values, bins=20)
    plt.title(column.replace("_", " ").title())
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def _correlation_plot(frame: pd.DataFrame, path: Path) -> None:
    """Create a numeric feature correlation heatmap."""
    numeric = frame.select_dtypes(include="number")
    if numeric.empty:
        return
    plt.figure(figsize=(8, 6))
    correlation = numeric.corr(numeric_only=True)
    if sns:
        sns.heatmap(correlation, annot=False, cmap="Blues")
    else:
        plt.imshow(correlation, cmap="Blues")
        plt.xticks(range(len(correlation.columns)), correlation.columns, rotation=90)
        plt.yticks(range(len(correlation.columns)), correlation.columns)
        plt.colorbar()
    plt.title("Feature Correlation")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def _word_frequency_plot(frame: pd.DataFrame, path: Path) -> None:
    """Create a simple top-word frequency chart."""
    words: Dict[str, int] = {}
    for message in frame["clean_message"].fillna(""):
        for word in str(message).split():
            words[word] = words.get(word, 0) + 1
    top_words = sorted(words.items(), key=lambda item: item[1], reverse=True)[:15]
    if not top_words:
        return
    labels, values = zip(*top_words)
    plt.figure(figsize=(8, 4))
    plt.bar(labels, values)
    plt.xticks(rotation=45, ha="right")
    plt.title("Common Commit Words")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def _path(value: str) -> Path:
    """Resolve a CLI path."""
    return Path(value).expanduser().resolve()


def build_parser() -> argparse.ArgumentParser:
    """Create the EDA CLI parser."""
    parser = argparse.ArgumentParser(description="Run simple EDA on commit_dataset.csv.")
    parser.add_argument("--dataset-path", type=_path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--summary-path", type=_path, default=DEFAULT_SUMMARY_PATH)
    parser.add_argument("--figure-dir", type=_path, default=DEFAULT_FIGURE_DIR)
    return parser


def main() -> None:
    """Run EDA from the command line."""
    args = build_parser().parse_args()
    summary = run_eda(args.dataset_path, summary_path=args.summary_path, figure_dir=args.figure_dir)
    print(f"Analyzed {summary['rows']} commits")


if __name__ == "__main__":
    main()

