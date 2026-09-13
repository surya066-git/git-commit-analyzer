"""Collect real commit data from GitHub and build datasets."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd
from dotenv import load_dotenv

from src.features import prepare_feature_frame, weak_label_record
from src.github_client import GitHubClient, parse_github_repo_url
from src.utils import ensure_parent, project_path, read_json, write_json


RAW_DATA_PATH = project_path("data", "raw", "github_commits.json")
PROCESSED_DATASET_PATH = project_path("data", "processed", "commit_dataset.csv")
LABEL_TEMPLATE_PATH = project_path("data", "processed", "manual_label_template.csv")


def collect_repository_commits(
    repository_url: str,
    *,
    max_commits: int = 20,
    token: str | None = None,
    include_pull_requests: bool = True,
) -> List[Dict[str, Any]]:
    """Collect real commits from one GitHub repository URL."""
    repo_ref = parse_github_repo_url(repository_url)
    client = GitHubClient(token=token)
    client.get_repository(repo_ref.owner, repo_ref.repo)
    return client.fetch_commits(
        repo_ref.owner,
        repo_ref.repo,
        max_commits=max_commits,
        include_pull_requests=include_pull_requests,
    )


def load_raw_records(path: Path = RAW_DATA_PATH) -> List[Dict[str, Any]]:
    """Load raw commit records, returning an empty list if no file exists."""
    if not path.exists():
        return []
    data = read_json(path)
    if isinstance(data, list):
        return data
    return data.get("commits", [])


def save_raw_records(records: Iterable[Dict[str, Any]], path: Path = RAW_DATA_PATH) -> None:
    """Save raw commit records as JSON."""
    write_json(path, list(records))


def merge_commit_records(existing: Iterable[Dict[str, Any]], new_records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge commit records by commit_id so repeated collection is safe."""
    by_id: Dict[str, Dict[str, Any]] = {}
    for record in [*existing, *new_records]:
        commit_id = str(record.get("commit_id") or "").strip()
        if commit_id:
            by_id[commit_id] = record
    return list(by_id.values())


def build_dataset(records: Iterable[Dict[str, Any]], *, weak_labels: bool = False) -> pd.DataFrame:
    """Build the processed commit dataset from raw GitHub records."""
    frame = prepare_feature_frame(records)
    if frame.empty:
        return frame

    if weak_labels:
        weak_labels_frame = pd.DataFrame([weak_label_record(record) for record in frame.to_dict(orient="records")])
        for column in weak_labels_frame.columns:
            frame[column] = weak_labels_frame[column]
    else:
        if "quality_category" not in frame.columns:
            frame["quality_category"] = ""
        if "review_score" not in frame.columns:
            frame["review_score"] = ""
        if "label_source" not in frame.columns:
            frame["label_source"] = "unlabeled"

    ordered_columns = [
        "commit_id",
        "repository",
        "commit_message",
        "author",
        "commit_date",
        "files_changed",
        "lines_added",
        "lines_deleted",
        "file_types",
        "has_issue",
        "has_pr",
        "commit_type",
        "message_length",
        "word_count",
        "has_description",
        "has_action_word",
        "quality_category",
        "review_score",
        "label_source",
        "changed_files",
        "pull_request_numbers",
        "review_count",
        "review_states",
        "html_url",
    ]
    for column in ordered_columns:
        if column not in frame.columns:
            frame[column] = ""
    return frame[ordered_columns]


def save_dataset(frame: pd.DataFrame, path: Path = PROCESSED_DATASET_PATH) -> None:
    """Save the processed dataset CSV."""
    ensure_parent(path)
    frame.to_csv(path, index=False)


def create_labeling_template(
    dataset_path: Path = PROCESSED_DATASET_PATH,
    output_path: Path = LABEL_TEMPLATE_PATH,
) -> pd.DataFrame:
    """Create a CSV where humans can add quality labels and review scores."""
    frame = pd.read_csv(dataset_path)
    label_columns = [
        "commit_id",
        "repository",
        "commit_message",
        "author",
        "commit_date",
        "files_changed",
        "lines_added",
        "lines_deleted",
        "file_types",
        "has_issue",
        "has_pr",
        "quality_category",
        "review_score",
        "label_source",
    ]
    for column in label_columns:
        if column not in frame.columns:
            frame[column] = ""
    frame["quality_category"] = frame["quality_category"].fillna("")
    frame["review_score"] = frame["review_score"].fillna("")
    frame["label_source"] = "manual"
    template = frame[label_columns]
    ensure_parent(output_path)
    template.to_csv(output_path, index=False)
    return template


def collect_repository_to_files(
    repository_url: str,
    *,
    max_commits: int,
    raw_path: Path = RAW_DATA_PATH,
    processed_path: Path = PROCESSED_DATASET_PATH,
    weak_labels: bool = False,
    include_pull_requests: bool = True,
) -> pd.DataFrame:
    """Collect commits and update raw plus processed dataset files."""
    load_dotenv()
    records = collect_repository_commits(
        repository_url,
        max_commits=max_commits,
        token=os.getenv("GITHUB_TOKEN"),
        include_pull_requests=include_pull_requests,
    )
    merged = merge_commit_records(load_raw_records(raw_path), records)
    save_raw_records(merged, raw_path)
    dataset = build_dataset(merged, weak_labels=weak_labels)
    save_dataset(dataset, processed_path)
    return dataset


def _path(value: str) -> Path:
    """Resolve a CLI path relative to the current working directory."""
    return Path(value).expanduser().resolve()


def build_parser() -> argparse.ArgumentParser:
    """Build the data collector command-line parser."""
    parser = argparse.ArgumentParser(description="Collect real GitHub commits and build a dataset.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    collect = subparsers.add_parser("collect", help="Collect commits from a GitHub repository.")
    collect.add_argument("--repository-url", required=True, help="GitHub repository URL, SSH URL, or owner/repo.")
    collect.add_argument("--max-commits", type=int, default=20, help="Maximum commits to collect.")
    collect.add_argument("--raw-path", type=_path, default=RAW_DATA_PATH)
    collect.add_argument("--processed-path", type=_path, default=PROCESSED_DATASET_PATH)
    collect.add_argument("--weak-labels", action="store_true", help="Attach transparent rule-based labels for bootstrapping.")
    collect.add_argument("--skip-prs", action="store_true", help="Skip PR/review lookup to reduce API calls.")

    label = subparsers.add_parser("label-template", help="Create a manual labeling CSV template.")
    label.add_argument("--dataset-path", type=_path, default=PROCESSED_DATASET_PATH)
    label.add_argument("--output-path", type=_path, default=LABEL_TEMPLATE_PATH)
    return parser


def main() -> None:
    """Run the data collection CLI."""
    args = build_parser().parse_args()
    if args.command == "collect":
        dataset = collect_repository_to_files(
            args.repository_url,
            max_commits=args.max_commits,
            raw_path=args.raw_path,
            processed_path=args.processed_path,
            weak_labels=args.weak_labels,
            include_pull_requests=not args.skip_prs,
        )
        print(f"Saved {len(dataset)} commits to {args.processed_path}")
    elif args.command == "label-template":
        template = create_labeling_template(args.dataset_path, args.output_path)
        print(f"Saved {len(template)} rows to {args.output_path}")


if __name__ == "__main__":
    main()

