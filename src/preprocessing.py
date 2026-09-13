"""Text preprocessing helpers for Git commit messages."""

from __future__ import annotations

import re
from typing import Iterable, List

try:
    from nltk.tokenize import RegexpTokenizer
except Exception:  # pragma: no cover - fallback for minimal installs
    RegexpTokenizer = None


TECHNICAL_KEEP_WORDS = {
    "api",
    "auth",
    "authentication",
    "bug",
    "cache",
    "database",
    "db",
    "error",
    "feature",
    "fix",
    "login",
    "migration",
    "refactor",
    "security",
    "test",
    "tests",
    "ui",
}

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
}

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", flags=re.IGNORECASE)
ISSUE_PATTERN = re.compile(r"(?:#\d+|\b[A-Z][A-Z0-9]+-\d+\b)")
SPECIAL_PATTERN = re.compile(r"[^a-z0-9_+\-\s]")
SPACE_PATTERN = re.compile(r"\s+")


def normalize_space(text: str) -> str:
    """Collapse repeated whitespace and trim the result."""
    return SPACE_PATTERN.sub(" ", text).strip()


def tokenize(text: str) -> List[str]:
    """Tokenize text into programming-friendly word tokens."""
    if RegexpTokenizer is not None:
        tokenizer = RegexpTokenizer(r"[A-Za-z0-9_+\-]+")
        return tokenizer.tokenize(text)
    return re.findall(r"[A-Za-z0-9_+\-]+", text)


def remove_stop_words(tokens: Iterable[str]) -> List[str]:
    """Remove common English stop words while keeping useful technical terms."""
    cleaned_tokens = []
    for token in tokens:
        if token in TECHNICAL_KEEP_WORDS or token not in STOP_WORDS:
            cleaned_tokens.append(token)
    return cleaned_tokens


def clean_commit_message(message: object, *, drop_stop_words: bool = True) -> str:
    """Clean a commit message without destroying meaningful Git/programming words."""
    if message is None:
        return ""

    text = str(message).lower()
    text = URL_PATTERN.sub(" ", text)
    text = ISSUE_PATTERN.sub(" ", text)
    text = SPECIAL_PATTERN.sub(" ", text)
    text = normalize_space(text)

    tokens = tokenize(text)
    if drop_stop_words:
        tokens = remove_stop_words(tokens)
    return " ".join(tokens)


def first_line(message: object) -> str:
    """Return the first line of a commit message."""
    if message is None:
        return ""
    return str(message).splitlines()[0].strip()

