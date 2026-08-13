"""
Health check route — non-AI endpoint to add realistic noise to the codebase.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check():
    return {"status": "healthy", "service": "support-portal"}


@router.get("/ready")
async def readiness_check():
    return {"status": "ready"}
