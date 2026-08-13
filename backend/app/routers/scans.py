"""
Scans router — POST /scans and GET /scans/{id}
"""

import uuid
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import subprocess

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Scan, Asset, Evidence
from app.schemas import ScanCreate, ScanOut
from app.scanner import run_scan

router = APIRouter()


@router.post("/", response_model=ScanOut, status_code=201)
def create_scan(payload: ScanCreate, db: Session = Depends(get_db)):
    """
    Trigger a discovery scan against the given repo path or URL.
    Supports local filesystem paths and remote Git URLs (e.g. GitHub).
    """
    is_remote_url = payload.repo_url.startswith("http://") or payload.repo_url.startswith("https://")
    
    # Create scan record
    scan = Scan(
        id=str(uuid.uuid4()),
        repo_url=payload.repo_url,
        status="running",
        started_at=datetime.now(timezone.utc),
    )
    db.add(scan)
    db.commit()

    try:
        if is_remote_url:
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    subprocess.run(
                        ["git", "clone", "--depth", "1", payload.repo_url, temp_dir],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                except subprocess.CalledProcessError as e:
                    raise Exception(f"Failed to clone repository: {e.stderr}")
                
                # Run the discovery pipeline
                asset_records, _ = run_scan(temp_dir, discovery_source="GitHub")
                _persist_assets(db, scan, asset_records)
        else:
            repo_path = Path(payload.repo_url)
            if not repo_path.exists():
                raise HTTPException(
                    status_code=422,
                    detail=f"Repository path does not exist: {payload.repo_url}. "
                           "Please provide an absolute local path or a Git URL.",
                )
            # Run the discovery pipeline
            asset_records, _ = run_scan(str(repo_path.resolve()), discovery_source="local")
            _persist_assets(db, scan, asset_records)

        scan.status = "completed"
        scan.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(scan)

    except Exception as e:
        db.rollback()
        scan.status = "failed"
        scan.error_message = str(e)
        scan.completed_at = datetime.now(timezone.utc)
        db.commit()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

    asset_count = db.query(Asset).filter(Asset.scan_id == scan.id).count()
    result = ScanOut.model_validate(scan)
    result.asset_count = asset_count
    return result


def _persist_assets(db: Session, scan: Scan, asset_records):
    for ar in asset_records:
        asset = Asset(
            id=str(uuid.uuid4()),
            scan_id=scan.id,
            name=ar.name,
            asset_type=ar.asset_type,
            llm_or_model=ar.llm_or_model,
            provider=ar.provider,
            location=ar.location,
            application=ar.application,
            purpose=ar.purpose,
            discovery_source=ar.discovery_source,
            status=ar.status,
            confidence_score=ar.confidence_score,
        )
        db.add(asset)
        db.flush()  # Get asset.id before adding evidence

        for ev in ar.evidence:
            evidence = Evidence(
                id=str(uuid.uuid4()),
                asset_id=asset.id,
                file_path=ev.file_path,
                line_number=ev.line_number,
                signal_type=ev.signal_type,
                matched_value=ev.matched_value,
                snippet=ev.snippet,
                confidence_weight=ev.confidence_weight,
            )
            db.add(evidence)


@router.get("/{scan_id}", response_model=ScanOut)
def get_scan(scan_id: str, db: Session = Depends(get_db)):
    """Get scan status and summary by scan ID."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")

    asset_count = db.query(Asset).filter(Asset.scan_id == scan_id).count()
    result = ScanOut.model_validate(scan)
    result.asset_count = asset_count
    return result
