"""
Assets router — GET /assets and GET /assets/{id}
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Asset, Evidence
from app.schemas import AssetListItem, AssetDetail, AssetListResponse

router = APIRouter()


@router.get("/", response_model=AssetListResponse)
def list_assets(
    scan_id: Optional[str] = Query(None, description="Filter by scan ID"),
    status: Optional[str] = Query(None, description="Filter by status: Discovered, Inferred, Pending Review"),
    provider: Optional[str] = Query(None, description="Filter by provider name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    List all discovered AI assets with optional filtering.
    Returns a paginated list with key summary fields.
    """
    query = db.query(Asset)

    if scan_id:
        query = query.filter(Asset.scan_id == scan_id)
    if status:
        query = query.filter(Asset.status == status)
    if provider:
        query = query.filter(Asset.provider.ilike(f"%{provider}%"))

    total = query.count()
    assets = query.offset(skip).limit(limit).all()

    return AssetListResponse(
        assets=[AssetListItem.model_validate(a) for a in assets],
        total=total,
        scan_id=scan_id,
    )


@router.get("/{asset_id}", response_model=AssetDetail)
def get_asset(asset_id: str, db: Session = Depends(get_db)):
    """
    Get full asset detail including all linked evidence records.
    Evidence is the "why" behind each discovery — the traceability chain.
    """
    asset = (
        db.query(Asset)
        .options(joinedload(Asset.evidence))
        .filter(Asset.id == asset_id)
        .first()
    )
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")

    return AssetDetail.model_validate(asset)
