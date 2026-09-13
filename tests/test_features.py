from src.features import detect_commit_type, extract_basic_features, extract_file_types, heuristic_review_score


def test_extract_file_types_from_list():
    assert extract_file_types(["src/app.py", "README.md", "tests/test_api.py"]) == "md py"


def test_detect_commit_type_from_conventional_message():
    assert detect_commit_type("feat(api): add pagination") == "feature"


def test_extract_basic_features():
    features = extract_basic_features(
        {
            "commit_message": "Fix login authentication bug #123",
            "changed_files": ["src/auth.py", "tests/test_auth.py"],
            "lines_added": 42,
            "lines_deleted": 15,
            "has_pr": 1,
        }
    )
    assert features["word_count"] == 4
    assert features["files_changed"] == 2
    assert features["has_issue"] == 1
    assert features["has_action_word"] == 1


def test_heuristic_score_penalizes_generic_message():
    generic = heuristic_review_score({"commit_message": "fix"})
    descriptive = heuristic_review_score({"commit_message": "Fix login authentication token refresh bug #42"})
    assert generic < descriptive

