from fastapi.testclient import TestClient

from app.main import GitHubClient, app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_endpoint_with_mocked_github(monkeypatch):
    def fake_get_repository(self, owner, repo):
        return {"description": "Test repo", "default_branch": "main"}

    def fake_fetch_commits(self, owner, repo, max_commits=5, include_pull_requests=True):
        return [
            {
                "commit_id": "abc123",
                "repository": f"{owner}/{repo}",
                "commit_message": "Fix login authentication redirect bug #42",
                "author": "Test Author",
                "commit_date": "2024-01-01T00:00:00Z",
                "files_changed": 2,
                "lines_added": 20,
                "lines_deleted": 5,
                "changed_files": ["src/auth.py", "tests/test_auth.py"],
                "has_pr": 1,
                "html_url": "https://github.com/example/repo/commit/abc123",
            }
        ]

    monkeypatch.setattr(GitHubClient, "get_repository", fake_get_repository)
    monkeypatch.setattr(GitHubClient, "fetch_commits", fake_fetch_commits)

    response = client.post(
        "/analyze",
        json={"repository_url": "https://github.com/example/repo", "max_commits": 1},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["repository"] == "example/repo"
    assert payload["commit_count"] == 1
    assert payload["results"][0]["quality_category"] in {"Poor", "Average", "Good"}


def test_analyze_rejects_invalid_url():
    response = client.post("/analyze", json={"repository_url": "https://example.com/repo", "max_commits": 1})
    assert response.status_code == 422

