import re
from collections import Counter


PROMOTIONAL_WORDS = {
    "amazing", "best", "must buy", "highly recommend", "five stars",
    "perfect", "excellent", "fantastic", "wonderful", "love it",
}


def analyze_text(text: str) -> dict[str, float]:
    words = re.findall(r"\b\w+\b", text.lower())
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    unique_words = set(words)
    caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    exclamation_count = text.count("!")
    promotional_hits = sum(1 for w in PROMOTIONAL_WORDS if w in text.lower())

    return {
        "text_length": float(len(text)),
        "word_count": float(len(words)),
        "sentence_count": float(len(sentences)),
        "lexical_diversity": len(unique_words) / max(len(words), 1),
        "avg_word_length": sum(len(w) for w in words) / max(len(words), 1),
        "caps_ratio": caps_ratio,
        "exclamation_count": float(exclamation_count),
        "promotional_language": float(promotional_hits),
        "repeated_phrase_ratio": _repeated_phrase_ratio(words),
        "sentiment_proxy": _sentiment_proxy(words),
    }


def text_risk_score(features: dict[str, float]) -> float:
    score = 0.0
    if features.get("promotional_language", 0) >= 2:
        score += 0.25
    if features.get("lexical_diversity", 1) < 0.35:
        score += 0.2
    if features.get("caps_ratio", 0) > 0.3:
        score += 0.15
    if features.get("exclamation_count", 0) >= 3:
        score += 0.15
    if features.get("text_length", 0) < 20:
        score += 0.1
    if features.get("repeated_phrase_ratio", 0) > 0.3:
        score += 0.15
    return min(score, 1.0)


def _repeated_phrase_ratio(words: list[str]) -> float:
    if len(words) < 4:
        return 0.0
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)]
    counts = Counter(bigrams)
    repeated = sum(c - 1 for c in counts.values() if c > 1)
    return repeated / max(len(bigrams), 1)


def _sentiment_proxy(words: list[str]) -> float:
    positive = {"great", "good", "excellent", "love", "amazing", "perfect", "best"}
    negative = {"bad", "terrible", "awful", "hate", "worst", "poor", "disappointed"}
    pos = sum(1 for w in words if w in positive)
    neg = sum(1 for w in words if w in negative)
    total = pos + neg
    if total == 0:
        return 0.5
    return pos / total
