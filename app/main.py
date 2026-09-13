"""FastAPI application for real-time Git commit quality analysis."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.github_client import GitHubAPIError, GitHubClient, parse_github_repo_url
from src.predict import CommitQualityPredictor
from src.train import DEFAULT_DATASET_PATH, DEFAULT_METRICS_PATH, DEFAULT_MODEL_PATH, train_from_dataset
from src.utils import project_path

# AI Imports
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

load_dotenv()

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
TEMPLATE_DIR = APP_DIR / "templates"

app = FastAPI(title="Git Commit Analyzer", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

predictor = CommitQualityPredictor()


class AnalyzeRequest(BaseModel):
    """Request body for repository analysis."""
    repository_url: str = Field(..., min_length=3)
    max_commits: int = Field(default=5, ge=1, le=25)


class TrainRequest(BaseModel):
    """Request body for model retraining."""
    dataset_path: str | None = None
    allow_weak_labels: bool = False


class ScoreTextRequest(BaseModel):
    """Request body for scoring arbitrary text with existing metadata."""
    commit_message: str
    files_changed: int = 1
    lines_added: int = 10
    lines_deleted: int = 2
    has_issue: bool = False
    has_pr: bool = False


class GenerateFixRequest(BaseModel):
    """Request body for AI rewrite of a commit message."""
    commit_message: str
    reasons: List[str] = []
    suggestions: List[str] = []


@app.get("/")
def index() -> FileResponse:
    """Serve the browser UI."""
    return FileResponse(TEMPLATE_DIR / "index.html")


@app.get("/health")
def health() -> Dict[str, Any]:
    """Return application health and model configuration."""
    return {
        "status": "ok",
        "model_loaded": predictor.is_model_loaded,
        "model_path": str(DEFAULT_MODEL_PATH),
        "model_error": predictor.load_error,
        "github_token_configured": bool(os.getenv("GITHUB_TOKEN")),
        "gemini_token_configured": bool(os.getenv("GEMINI_API_KEY")),
    }


@app.post("/analyze")
def analyze_repository(request: AnalyzeRequest) -> Dict[str, Any]:
    """Fetch real commits from GitHub and predict quality for each commit."""
    try:
        repo_ref = parse_github_repo_url(request.repository_url)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))
    try:
        repository = client.get_repository(repo_ref.owner, repo_ref.repo)
        commits = client.fetch_commits(
            repo_ref.owner,
            repo_ref.repo,
            max_commits=request.max_commits,
            include_pull_requests=True,
        )
    except GitHubAPIError as exc:
        status_code = exc.status_code if exc.status_code and exc.status_code < 500 else 502
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    if not commits:
        raise HTTPException(status_code=404, detail="No commits were found for this repository.")

    results: List[Dict[str, Any]] = [predictor.predict_commit(commit) for commit in commits]
    return {
        "repository": repo_ref.full_name,
        "repository_description": repository.get("description"),
        "default_branch": repository.get("default_branch"),
        "commit_count": len(results),
        "model_loaded": predictor.is_model_loaded,
        "model_name": results[0].get("model_name") if results else None,
        "score_note": "Review score is a practical 1-10 score derived from the predicted class plus transparent rules.",
        "results": results,
    }


@app.post("/score-text")
def score_text(request: ScoreTextRequest) -> Dict[str, Any]:
    """Score a specific text using the existing ML pipeline."""
    # Build a simulated record that features.py can consume
    record = {
        "commit_message": request.commit_message,
        "commit_id": "ai-generated",
        "author": "AI Assistant",
        "commit_date": "Just now",
        "html_url": "",
        # Metadata mapped back so extract_basic_features can pull them if needed
        # (Our features.py usually parses the raw github commit, but we can pass raw stats if features.py allows it or handles it,
        # otherwise we just let it fall back. We will provide dict keys that match what features.py expects from GitHub payload)
        "files": [{"filename": "dummy.txt", "additions": request.lines_added, "deletions": request.lines_deleted, "changes": request.lines_added + request.lines_deleted}] * request.files_changed,
    }
    
    # If the feature extractor needs `stats`
    record["stats"] = {
        "total": request.lines_added + request.lines_deleted,
        "additions": request.lines_added,
        "deletions": request.lines_deleted
    }
    
    # If the original commit was linked to a PR or issue, simulate that in the message or PR field
    if request.has_pr:
        record["associated_pull_requests"] = {"total_count": 1}
    
    return predictor.predict_commit(record)


@app.post("/generate-fix")
def generate_fix(request: GenerateFixRequest) -> Dict[str, str]:
    """Use Gemini AI to rewrite the commit message."""
    if not HAS_GENAI:
        raise HTTPException(status_code=500, detail="google-genai library is not installed.")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400, 
            detail="GEMINI_API_KEY is not configured in .env. AI Fix requires a Gemini API key."
        )

    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
You are an expert developer helping to improve a Git commit message.
The original commit message was rated poorly by our ML model.

Original message:
{request.commit_message}

Reasons for poor score:
{chr(10).join(request.reasons)}

Suggestions:
{chr(10).join(request.suggestions)}

Please write an improved, professional commit message.
It should be descriptive, start with an action word (Fix, Add, Update, etc.), and follow best practices.
Return ONLY the improved commit message text, with no markdown, no quotes, and no extra explanation.
"""
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
        )
        return {"improved_message": response.text.strip()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(exc)}") from exc


@app.post("/train")
def train_model(request: TrainRequest | None = None) -> Dict[str, Any]:
    """Retrain the saved model separately from real-time analysis."""
    body = request or TrainRequest()
    dataset_path = Path(body.dataset_path).expanduser().resolve() if body.dataset_path else DEFAULT_DATASET_PATH
    try:
        metrics = train_from_dataset(
            dataset_path,
            model_path=DEFAULT_MODEL_PATH,
            metrics_path=DEFAULT_METRICS_PATH,
            allow_weak_labels=body.allow_weak_labels,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    predictor.load()
    return {
        "status": "trained",
        "metrics_path": str(DEFAULT_METRICS_PATH),
        "model_path": str(DEFAULT_MODEL_PATH),
        "metrics": metrics,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
