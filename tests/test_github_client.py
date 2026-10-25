import pytest

from src.github_client import parse_github_repo_url


def test_parse_https_github_url():
    repo = parse_github_repo_url("https://github.com/psf/requests.git")
    assert repo.owner == "psf"
    assert repo.repo == "requests"
    assert repo.full_name == "psf/requests"


def test_parse_owner_repo():
    repo = parse_github_repo_url("fastapi/fastapi")
    assert repo.full_name == "fastapi/fastapi"


def test_reject_non_github_url():
    with pytest.raises(ValueError):
        parse_github_repo_url("https://example.com/owner/repo")


def test_github_client_fallback_on_401(monkeypatch):
    from unittest.mock import MagicMock
    from src.github_client import GitHubClient

    client = GitHubClient(token="invalid_token")
    assert "Authorization" in client.session.headers

    mock_resp_401 = MagicMock()
    mock_resp_401.status_code = 401
    mock_resp_401.json.return_value = {"message": "Bad credentials"}

    mock_resp_200 = MagicMock()
    mock_resp_200.status_code = 200
    mock_resp_200.content = b'{"full_name": "owner/repo"}'
    mock_resp_200.json.return_value = {"full_name": "owner/repo"}

    responses = [mock_resp_401, mock_resp_200]
    monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: responses.pop(0))

    data = client._request("/repos/owner/repo")
    assert data == {"full_name": "owner/repo"}
    assert "Authorization" not in client.session.headers
    assert client.token is None


def test_github_client_raises_informative_error_on_persistent_401(monkeypatch):
    from unittest.mock import MagicMock
    from src.github_client import GitHubClient, GitHubAPIError

    client = GitHubClient(token=None)

    mock_resp_401 = MagicMock()
    mock_resp_401.status_code = 401
    mock_resp_401.headers = {}
    mock_resp_401.json.return_value = {"message": "Bad credentials"}

    monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: mock_resp_401)

    with pytest.raises(GitHubAPIError) as exc_info:
        client._request("/repos/owner/repo")
    assert "Bad credentials" in str(exc_info.value)
    assert "GITHUB_TOKEN" in str(exc_info.value)

