"""Small shared utilities for paths and JSON files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def project_path(*parts: str) -> Path:
    """Return an absolute path inside the project root."""
    return PROJECT_ROOT.joinpath(*parts)


def ensure_parent(path: Path) -> None:
    """Create a file's parent directory if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: Any) -> None:
    """Write pretty JSON with a stable encoding."""
    ensure_parent(path)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def read_json(path: Path) -> Any:
    """Read a JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))

