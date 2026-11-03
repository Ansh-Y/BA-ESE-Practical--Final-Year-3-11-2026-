from __future__ import annotations

import re

STOPWORDS = {
    "the", "and", "with", "but", "are", "was", "were", "this", "that", "for", "its", "it",
    "is", "a", "an", "of", "to", "in", "on", "after", "within", "feels", "bit", "too", "be",
    "out", "how", "very", "all", "from",
}
POSITIVE_WORDS = {
    "good", "great", "excellent", "love", "fast", "easy", "comfortable", "durable",
    "happy", "amazing", "perfect", "nice",
}
NEGATIVE_WORDS = {
    "bad", "poor", "broken", "slow", "worst", "hate", "cheap", "disappointed",
    "defective", "late", "slippery", "dented",
}

_TOKEN_RE = re.compile(r"[a-z]+")


def tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if len(t) > 2 and t not in STOPWORDS]


def sentiment_score(tokens: list[str]) -> float:
    positive = sum(t in POSITIVE_WORDS for t in tokens)
    negative = sum(t in NEGATIVE_WORDS for t in tokens)
    if positive + negative == 0:
        return 0.0
    return round((positive - negative) / (positive + negative), 3)


def sentiment_label(score: float) -> str:
    if score > 0.2:
        return "Positive"
    if score < -0.2:
        return "Negative"
    return "Neutral"
