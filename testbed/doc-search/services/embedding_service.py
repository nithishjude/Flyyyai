"""
Embedding Service — wraps sentence-transformers for semantic search.
This is the AI integration for doc-search. The scanner should detect:
  - `from sentence_transformers import SentenceTransformer` (LIBRARY_IMPORT signal)
  - model name string "all-MiniLM-L6-v2" (MODEL_NAME_STRING signal)
  - `HF_TOKEN` env var reference (ENV_VAR_KEY signal)
  - faiss usage (LIBRARY_IMPORT signal)
"""

import os
from typing import List, Tuple, Dict, Any, Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Model name is explicit — scanner should pick this up as MODEL_NAME_STRING
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
HF_TOKEN = os.environ.get("HF_TOKEN")

# Hugging Face endpoint (used for hosted inference, optional)
HF_INFERENCE_ENDPOINT = "https://api-inference.huggingface.co/models/"

# Load model at module init time for reuse across requests
_model: Optional[SentenceTransformer] = None
_index: Optional[faiss.IndexFlatL2] = None
_doc_store: Dict[int, Dict[str, Any]] = {}
_embedding_dim = 384  # all-MiniLM-L6-v2 output dim


def _get_model() -> SentenceTransformer:
    """Lazy-load the sentence-transformers model."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def _get_index() -> faiss.IndexFlatL2:
    """Lazy-init the FAISS index."""
    global _index
    if _index is None:
        _index = faiss.IndexFlatL2(_embedding_dim)
    return _index


async def ingest_document(
    doc_id: str,
    title: str,
    content: str,
    metadata: Dict[str, Any],
) -> int:
    """
    Embed a document's content and add it to the FAISS index.

    Returns the number of chunks indexed.
    """
    model = _get_model()
    index = _get_index()

    # Simple chunking: split on double newlines
    chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
    if not chunks:
        chunks = [content]

    embeddings = model.encode(chunks, normalize_embeddings=True)
    embeddings_np = np.array(embeddings).astype("float32")

    start_idx = index.ntotal
    index.add(embeddings_np)

    for i, chunk in enumerate(chunks):
        _doc_store[start_idx + i] = {
            "doc_id": doc_id,
            "title": title,
            "snippet": chunk[:300],
            "metadata": metadata,
        }

    return len(chunks)


async def search_documents(
    query: str,
    top_k: int = 5,
    score_threshold: float = 0.5,
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Embed a query and retrieve the most similar document chunks.

    Returns:
        Tuple of (list of result dicts, model name used)
    """
    model = _get_model()
    index = _get_index()

    if index.ntotal == 0:
        return [], EMBEDDING_MODEL

    query_embedding = model.encode([query], normalize_embeddings=True)
    query_np = np.array(query_embedding).astype("float32")

    k = min(top_k, index.ntotal)
    distances, indices = index.search(query_np, k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue
        # Convert L2 distance to similarity score (approximate cosine for normalised vecs)
        score = float(1 - dist / 2)
        if score < score_threshold:
            continue
        doc = _doc_store.get(idx, {})
        results.append({
            "doc_id": doc.get("doc_id", "unknown"),
            "title": doc.get("title", "Untitled"),
            "snippet": doc.get("snippet", ""),
            "similarity_score": round(score, 4),
        })

    return results, EMBEDDING_MODEL
