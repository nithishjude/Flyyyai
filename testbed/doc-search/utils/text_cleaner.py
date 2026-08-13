"""
Text cleaner utility — non-AI text pre-processing utilities.
Exists to make the codebase look realistic; the scanner should NOT flag these as AI signals.
"""

import re
import unicodedata
from typing import List


def clean_text(text: str) -> str:
    """Normalise unicode, strip control characters, collapse whitespace."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.category(c).startswith("C") or c in "\n\t")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def split_into_sentences(text: str) -> List[str]:
    """Naive sentence splitter — splits on . ! ? followed by whitespace."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def remove_stop_words(text: str, stop_words: List[str] = None) -> str:
    """Remove common stop words from text (for BM25/keyword search, not embeddings)."""
    if stop_words is None:
        stop_words = ["the", "a", "an", "is", "it", "in", "on", "at", "to", "for", "of", "and", "or"]
    words = text.lower().split()
    filtered = [w for w in words if w not in stop_words]
    return " ".join(filtered)


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> List[str]:
    """Split text into overlapping fixed-size token chunks (word-based approximation)."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks
