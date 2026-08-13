"""
Health check route for doc-search service.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check():
    return {"status": "healthy", "service": "doc-search"}


@router.get("/ready")
async def readiness_check():
    return {"status": "ready", "vector_store": "loaded"}
