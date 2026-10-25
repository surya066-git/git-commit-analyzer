"""GitHub REST API client for collecting real commit data."""

from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)
GITHUB_API_URL = "https://api.github.com"
REPOSITORY_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


class GitHubAPIError(RuntimeError):
    """Raised when the GitHub API returns an error or cannot be reached."""

    def __init__(self, message: str, status_code: int | None = None, reset_at: int | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.reset_at = reset_at


@dataclass(frozen=True)
class RepositoryRef:
    """Owner and repository name parsed from a GitHub URL."""

    owner: str
    repo: str

    @property
    def full_name(self) -> str:
        """Return owner/repo."""
        return f"{self.owner}/{self.repo}"


def parse_github_repo_url(repository_url: str) -> RepositoryRef:
    """Parse a GitHub URL, SSH URL, or owner/repo string."""
    value = (repository_url or "").strip()
    if not value:
        raise ValueError("Repository URL is required.")

    if value.startswith("git@github.com:"):
        path = value.split(":", 1)[1]
    elif "://" not in value and re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?$", value):
        path = value
    else:
        parsed = urlparse(value)
        if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
            raise ValueError("Only github.com repository URLs are supported.")
        path = parsed.path.strip("/")

    parts = [part for part in path.split("/") if part]
    if len(parts) < 2:
        raise ValueError("Repository URL must include both owner and repository name.")

    owner = parts[0]
    repo = parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]

    if not REPOSITORY_NAME_PATTERN.match(owner) or not REPOSITORY_NAME_PATTERN.match(repo):
        raise ValueError("Repository owner or name contains invalid characters.")

    return RepositoryRef(owner=owner, repo=repo)


class GitHubClient:
    """Small GitHub REST API wrapper with pagination and rate-limit errors."""

    def __init__(self, token: str | None = None, timeout: int = 20):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "git-commit-analyzer",
            }
        )
        if self.token:
            self.session.headers["Authorization"] = f"Bearer {self.token}"

    def _url(self, path: str) -> str:
        """Build an absolute GitHub API URL."""
        return f"{GITHUB_API_URL}{path}"

    def _request(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Run a GET request and normalize GitHub API errors."""
        try:
            response = self.session.get(self._url(path), params=params, timeout=self.timeout)
        except requests.RequestException as exc:
            raise GitHubAPIError(f"Network error while contacting GitHub: {exc}") from exc

        if response.status_code >= 400:
            had_token = "Authorization" in self.session.headers
            if response.status_code == 401 and had_token:
                logger.warning("GitHub token returned 401 Bad credentials. Falling back to unauthenticated request...")
                self.session.headers.pop("Authorization", None)
                self.token = None
                try:
                    retry_response = self.session.get(self._url(path), params=params, timeout=self.timeout)
                    if retry_response.status_code < 400:
                        if not retry_response.content:
                            return None
                        return retry_response.json()
                    if retry_response.status_code == 404:
                        raise GitHubAPIError(
                            "Repository not found or access denied. Your GITHUB_TOKEN in .env is invalid or expired ('Bad credentials'). "
                            "Please update it with a valid token if this repository is private.",
                            status_code=401,
                        )
                    response = retry_response
                except requests.RequestException:
                    pass

            reset_at = _header_int(response.headers.get("X-RateLimit-Reset"))
            message = _error_message(response)
            if response.status_code == 401:
                message = (
                    "GitHub authentication failed (Bad credentials). Your GITHUB_TOKEN in .env is invalid or expired. "
                    "Please update it with a valid Personal Access Token or clear it to analyze public repositories."
                )
            elif response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
                reset_text = f" Reset time: {time.ctime(reset_at)}." if reset_at else ""
                message = f"GitHub API rate limit exceeded.{reset_text}"
            raise GitHubAPIError(message, status_code=response.status_code, reset_at=reset_at)

        if not response.content:
            return None
        return response.json()

    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Validate and fetch repository details."""
        return self._request(f"/repos/{owner}/{repo}")

    def get_rate_limit(self) -> Dict[str, Any]:
        """Return the current GitHub API rate-limit status."""
        return self._request("/rate_limit")

    def _get_paginated(
        self,
        path: str,
        *,
        max_items: int,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch a paginated GitHub list endpoint."""
        collected: List[Dict[str, Any]] = []
        page = 1
        per_page = min(100, max(1, max_items))

        while len(collected) < max_items:
            request_params = dict(params or {})
            request_params.update({"per_page": per_page, "page": page})
            page_items = self._request(path, params=request_params)
            if not page_items:
                break
            collected.extend(page_items)
            if len(page_items) < per_page:
                break
            page += 1

        return collected[:max_items]

    def fetch_commits(
        self,
        owner: str,
        repo: str,
        *,
        max_commits: int = 10,
        include_pull_requests: bool = True,
    ) -> List[Dict[str, Any]]:
        """Fetch latest commits and enrich each one with file stats."""
        summaries = self._get_paginated(f"/repos/{owner}/{repo}/commits", max_items=max_commits)
        commits: List[Dict[str, Any]] = []
        seen_shas: set[str] = set()

        for summary in summaries:
            sha = summary.get("sha")
            if not sha or sha in seen_shas:
                continue
            seen_shas.add(sha)
            commits.append(
                self.fetch_commit_detail(
                    owner,
                    repo,
                    sha,
                    include_pull_requests=include_pull_requests,
                )
            )

        return commits

    def fetch_commit_detail(
        self,
        owner: str,
        repo: str,
        sha: str,
        *,
        include_pull_requests: bool = True,
    ) -> Dict[str, Any]:
        """Fetch one commit with stats, changed files, and optional PR review data."""
        detail = self._request(f"/repos/{owner}/{repo}/commits/{sha}")
        commit = detail.get("commit", {})
        author_data = commit.get("author") or {}
        stats = detail.get("stats") or {}
        files = detail.get("files") or []

        pull_requests: List[Dict[str, Any]] = []
        review_count = 0
        review_states: List[str] = []
        if include_pull_requests:
            pull_requests = self.fetch_pull_requests_for_commit(owner, repo, sha)
            if pull_requests:
                first_pull = pull_requests[0]
                reviews = self.fetch_pull_reviews(owner, repo, first_pull.get("number"))
                review_count = len(reviews)
                review_states = sorted({str(review.get("state", "")).lower() for review in reviews if review.get("state")})

        changed_file_names = [file_info.get("filename", "") for file_info in files if file_info.get("filename")]
        return {
            "commit_id": sha,
            "repository": f"{owner}/{repo}",
            "commit_message": commit.get("message", ""),
            "author": author_data.get("name") or (detail.get("author") or {}).get("login") or "Unknown",
            "commit_date": author_data.get("date", ""),
            "files_changed": len(changed_file_names),
            "lines_added": int(stats.get("additions") or 0),
            "lines_deleted": int(stats.get("deletions") or 0),
            "changed_files": changed_file_names,
            "file_types": "",
            "has_issue": 0,
            "has_pr": int(bool(pull_requests)),
            "pull_request_numbers": [pull.get("number") for pull in pull_requests if pull.get("number")],
            "review_count": review_count,
            "review_states": review_states,
            "html_url": detail.get("html_url", ""),
        }

    def fetch_pull_requests_for_commit(self, owner: str, repo: str, sha: str) -> List[Dict[str, Any]]:
        """Fetch pull requests associated with a commit when GitHub can provide them."""
        try:
            result = self._request(f"/repos/{owner}/{repo}/commits/{sha}/pulls")
        except GitHubAPIError as exc:
            if exc.status_code in {404, 409, 422}:
                return []
            raise
        return result or []

    def fetch_pull_reviews(self, owner: str, repo: str, pull_number: Any) -> List[Dict[str, Any]]:
        """Fetch PR reviews for a pull request number."""
        if not pull_number:
            return []
        try:
            result = self._request(f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews")
        except GitHubAPIError as exc:
            if exc.status_code in {404, 409, 422}:
                return []
            raise
        return result or []


def _header_int(value: str | None) -> int | None:
    """Parse an integer response header."""
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _error_message(response: requests.Response) -> str:
    """Extract a clear message from a GitHub error response."""
    try:
        payload = response.json()
    except ValueError:
        return response.text or f"GitHub API returned HTTP {response.status_code}."
    message = payload.get("message") or f"GitHub API returned HTTP {response.status_code}."
    return str(message)

