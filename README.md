# Git Commit Analyzer

Git Commit Analyzer is a real-time NLP and machine learning project that analyzes real GitHub commits and predicts a review quality category: `Poor`, `Average`, or `Good`. It also returns a practical 1-10 review score, reasons for the score, and suggestions to improve the commit message.

The app is intentionally simple enough for a college project, but the architecture is real: collect commits from GitHub, build a dataset, preprocess text, train sklearn models, save the best model, and load that saved model in a FastAPI web app.

## Problem Statement

Commit messages are often the first thing reviewers and future maintainers read. This project predicts whether a commit message and its Git metadata look poor, average, or good for review quality.

Input features include commit text, files changed, additions, deletions, file types, issue references, PR presence, description presence, and action words.

Target label:

- `quality_category`: `Poor`, `Average`, or `Good`

Optional target:

- `review_score`: 1-10

## Architecture

1. User enters a GitHub repository URL.
2. FastAPI validates the URL.
3. The backend fetches real commits using the GitHub REST API.
4. Commit messages are cleaned with NLP preprocessing.
5. TF-IDF text features are combined with Git metadata features.
6. The saved sklearn model predicts a quality category.
7. A rule-based suggestion engine explains and improves the result.
8. The frontend displays each analyzed commit.

Real-time analysis does not retrain the model. Training is a separate step.

## Project Structure

```text
data/
  raw/
  processed/
models/
notebooks/
  01_eda.ipynb
src/
  __init__.py
  data_collector.py
  preprocessing.py
  features.py
  train.py
  evaluate.py
  predict.py
  github_client.py
  utils.py
app/
  main.py
  templates/index.html
  static/style.css
  static/script.js
tests/
  fixtures/sample_labeled_commits.csv
.env.example
requirements.txt
README.md
.gitignore
```

Older `backend`, `frontend`, and `ml-service` folders may exist in this workspace, but the completed project described here lives at the root paths above.

## Features

- Accepts GitHub repository URLs, SSH URLs, and `owner/repo` strings.
- Fetches real commit history from the GitHub REST API.
- Extracts commit SHA, message, author, date, files changed, additions, deletions, file types, PR presence, and review counts when available.
- Builds raw JSON and processed CSV datasets.
- Provides a manual labeling template.
- Uses NLP preprocessing that preserves useful technical terms such as `fix`, `bug`, `api`, `login`, `database`, and `security`.
- Combines TF-IDF with numerical and categorical Git metadata.
- Compares Logistic Regression, Linear SVM, Naive Bayes, and Random Forest.
- Saves `models/best_model.pkl` for real-time prediction.
- Serves a FastAPI backend and simple HTML/CSS/JavaScript frontend.

## GitHub API Setup

Create a `.env` file in the project root:

```env
GITHUB_TOKEN=your_token_here
```

Public repositories can sometimes be analyzed without a token, but GitHub's unauthenticated rate limit is small. A token is recommended, especially because the project fetches per-commit file stats and PR metadata.

Never put the token in frontend code. `.env` is ignored by git.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

On macOS/Linux, activate with:

```bash
source .venv/bin/activate
```

## Data Collection

Collect real commits:

```bash
python -m src.data_collector collect --repository-url https://github.com/psf/requests --max-commits 20
```

This writes:

- `data/raw/github_commits.json`
- `data/processed/commit_dataset.csv`

To create a human labeling file:

```bash
python -m src.data_collector label-template
```

Fill `quality_category` with `Poor`, `Average`, or `Good`, set `review_score` from 1-10 if available, and keep `label_source` as `manual`.

For a transparent bootstrap demo only, you can collect weak labels:

```bash
python -m src.data_collector collect --repository-url https://github.com/psf/requests --max-commits 20 --weak-labels
```

Weak labels are rule-based, not human review labels. They are useful for checking the end-to-end pipeline, not for claiming scientific model quality.

## NLP Preprocessing

`src/preprocessing.py` performs:

- lowercasing
- URL removal
- issue/ticket reference cleanup for text representation
- special character cleanup
- whitespace normalization
- tokenization
- stop-word removal while preserving technical words

Example:

```text
Fix Login Authentication Bug #123
```

becomes:

```text
fix login authentication bug
```

## Feature Engineering

`src/features.py` creates:

- TF-IDF input text
- message length
- word count
- files changed
- lines added
- lines deleted
- total changes
- file types
- issue reference presence
- PR presence
- commit type
- description presence
- action-word presence

The model target remains separate as `quality_category`.

## Training

Train only from manual labels:

```bash
python -m src.train
```

Train from weak labels only when you are bootstrapping the pipeline:

```bash
python -m src.train --allow-weak-labels
```

Training saves:

- `models/best_model.pkl`
- `models/metrics.json`

The training script splits the data, compares multiple models, chooses the best validation macro F1 score, then evaluates the selected model on a held-out test set.

## Evaluation

Evaluate a saved model:

```bash
python -m src.evaluate --allow-weak-labels
```

This writes `models/evaluation.json` with accuracy, precision, recall, F1 score, and confusion matrix values from the actual labels in the dataset. The project does not invent performance numbers.

## EDA

Run the EDA script:

```bash
python -m src.eda
```

It writes a summary JSON file and charts for quality distribution, message length, files changed, additions/deletions, feature correlation, and word frequency.

The notebook `notebooks/01_eda.ipynb` calls the same EDA function.

## Running the Application

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Useful endpoints:

- `GET /`
- `GET /health`
- `POST /analyze`
- `POST /train`

Example `/analyze` request:

```json
{
  "repository_url": "https://github.com/psf/requests",
  "max_commits": 5
}
```

Example response shape:

```json
{
  "repository": "psf/requests",
  "commit_count": 5,
  "results": [
    {
      "commit_message": "Fix login authentication bug",
      "commit_sha": "abc123",
      "author": "Example Author",
      "date": "2024-01-01T00:00:00Z",
      "files_changed": 3,
      "lines_added": 42,
      "lines_deleted": 15,
      "quality_category": "Good",
      "review_score": 8,
      "reasons": ["Commit message gives a useful amount of detail."],
      "suggestions": ["Add an issue or PR reference when the project uses one."]
    }
  ]
}
```

## Testing

Run tests:

```bash
pytest
```

The file `tests/fixtures/sample_labeled_commits.csv` is a tiny sample used only for automated tests. It is not the final training dataset.

## Limitations

- The app needs real manual labels for meaningful model quality.
- Weak labels are available only to bootstrap and verify the workflow.
- PR and review metadata depends on GitHub API availability and permissions.
- Unauthenticated GitHub API requests can hit rate limits quickly.
- The 1-10 review score is practical and rule-assisted unless you add reliable human `review_score` labels.

## Future Improvements

- Add a larger human-reviewed dataset.
- Add reviewer agreement tracking for labels.
- Train a separate regression model for `review_score`.
- Add repository-level trend charts.
- Add authentication for analyzing private repositories safely.
- Add CI for tests and model training checks.

