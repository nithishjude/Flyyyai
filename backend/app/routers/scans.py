"""
Scans router — POST /scans and GET /scans/{id}
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Scan
from app.schemas import ScanCreate, ScanOut, ScanListResponse
from app.background import run_scan_task

router = APIRouter()


@router.post("/", response_model=ScanOut, status_code=202)
def create_scan(
    payload: ScanCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger a discovery scan against the given repo path or URL.
    Runs asynchronously in the background.
    """
    scan = Scan(
        id=str(uuid.uuid4()),
        repo_url=payload.repo_url,
        status="pending",
        started_at=datetime.now(timezone.utc),
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    background_tasks.add_task(run_scan_task, scan.id, payload.repo_url)

    result = ScanOut.model_validate(scan)
    result.asset_count = 0
    return result


@router.get("/", response_model=ScanListResponse)
def list_scans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all scans ordered by newest first."""
    query = db.query(Scan).order_by(Scan.started_at.desc())
    total = query.count()
    scans = query.options(selectinload(Scan.assets)).offset(skip).limit(limit).all()
    
    results = []
    for s in scans:
        out = ScanOut.model_validate(s)
        out.asset_count = len(s.assets)
        results.append(out)
        
    return ScanListResponse(scans=results, total=total)


@router.get("/{scan_id}", response_model=ScanOut)
def get_scan(scan_id: str, db: Session = Depends(get_db)):
    """Get scan status and summary by scan ID."""
    scan = db.query(Scan).options(selectinload(Scan.assets)).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")

    result = ScanOut.model_validate(scan)
    result.asset_count = len(scan.assets)
    return result


@router.delete("/{scan_id}", status_code=204)
def delete_scan(scan_id: str, db: Session = Depends(get_db)):
    """Delete a scan and all its assets/evidence."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")
        
    db.delete(scan)
    db.commit()

