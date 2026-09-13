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

