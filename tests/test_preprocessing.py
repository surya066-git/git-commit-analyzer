from src.preprocessing import clean_commit_message, tokenize


def test_clean_commit_message_preserves_technical_terms():
    assert clean_commit_message("Fix Login Authentication Bug #123") == "fix login authentication bug"


def test_tokenize_handles_programming_terms():
    assert tokenize("api auth token-refresh") == ["api", "auth", "token-refresh"]

