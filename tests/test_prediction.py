from pathlib import Path

from src.predict import CommitQualityPredictor
from src.train import train_from_dataset


FIXTURE_DATASET = Path("tests/fixtures/sample_labeled_commits.csv").resolve()


def test_training_saves_loadable_model(tmp_path):
    model_path = tmp_path / "best_model.pkl"
    metrics_path = tmp_path / "metrics.json"

    metrics = train_from_dataset(
        FIXTURE_DATASET,
        model_path=model_path,
        metrics_path=metrics_path,
        allow_weak_labels=False,
    )

    assert model_path.exists()
    assert metrics_path.exists()
    assert metrics["best_model"]

    predictor = CommitQualityPredictor(model_path=model_path)
    result = predictor.predict_commit(
        {
            "commit_id": "abc123",
            "commit_message": "Fix login authentication redirect bug #42",
            "author": "Test Author",
            "commit_date": "2024-01-01T00:00:00Z",
            "changed_files": ["src/auth.py", "tests/test_auth.py"],
            "files_changed": 2,
            "lines_added": 20,
            "lines_deleted": 5,
            "has_pr": 1,
        }
    )

    assert result["quality_category"] in {"Poor", "Average", "Good"}
    assert 1 <= result["review_score"] <= 10
    assert result["reasons"]
    assert result["suggestions"]

