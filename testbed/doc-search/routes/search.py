"""
Search route — semantic document similarity search via embeddings.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.embedding_service import search_documents

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    score_threshold: Optional[float] = 0.5


class SearchResult(BaseModel):
    doc_id: str
    title: str
    snippet: str
    similarity_score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    model_used: str
    total_results: int


@router.post("/", response_model=SearchResponse)
async def semantic_search(request: SearchRequest):
    """
    Perform semantic similarity search over the document store.
    Embeds the query using sentence-transformers and finds nearest neighbours.
    """
    try:
        results, model_name = await search_documents(
            query=request.query,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    return SearchResponse(
        query=request.query,
        results=results,
        model_used=model_name,
        total_results=len(results),
    )


@router.get("/suggest")
async def suggest_queries(prefix: str = Query(..., min_length=2)):
    """Auto-complete endpoint — not AI-powered, uses simple prefix matching."""
    suggestions = [
        s for s in ["refund policy", "return process", "account settings", "billing"]
        if s.startswith(prefix.lower())
    ]
    return {"suggestions": suggestions}
