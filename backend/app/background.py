import os
import re
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Scan, Asset, Evidence
from app.scanner import run_scan
from app.logger import get_logger

log = get_logger(__name__)


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


def _normalise_local_path(raw: str) -> str:
    """
    Robustly normalise a local path string that may arrive from the API with
    either forward or backward slashes.  On Windows the backslash variant is
    common, but JSON-transmitted strings sometimes contain control characters
    when naive escape handling is applied.  We sanitise by:
      1. Replacing any remaining literal backslash characters with the OS sep.
      2. Running os.path.normpath so the OS resolves the canonical form.
    """
    # Replace forward slashes with the OS path separator for uniformity,
    # then normalise (handles mixed separators, double slashes, etc.)
    normalised = os.path.normpath(raw.replace("/", os.sep))
    return normalised


def run_scan_task(scan_id: str, repo_url: str):
    """Background task to run the discovery pipeline."""
    db = SessionLocal()
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        db.close()
        return

    log.info("scan_started", scan_id=scan_id, repo_url=repo_url)
    scan.status = "running"
    db.commit()

    is_remote_url = repo_url.startswith("http://") or repo_url.startswith("https://")

    try:
        if is_remote_url:
            if not re.match(r'^https?://[\w./\-_:@]+$', repo_url):
                raise ValueError("Invalid remote URL format")

            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    subprocess.run(
                        ["git", "clone", "--depth", "1", repo_url, temp_dir],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                except subprocess.CalledProcessError as e:
                    raise Exception(f"Failed to clone repository: {e.stderr}")

                asset_records, _ = run_scan(temp_dir, discovery_source="GitHub")
                _persist_assets(db, scan, asset_records)
        else:
            normalised = _normalise_local_path(repo_url)
            log.info("scan_path_debug", raw=repr(repo_url), normalised=repr(normalised), exists=os.path.exists(normalised))
            if not os.path.exists(normalised):
                raise ValueError(f"Repository path does not exist: {normalised}")
            asset_records, _ = run_scan(normalised, discovery_source="local")
            _persist_assets(db, scan, asset_records)

        scan.status = "completed"
        scan.completed_at = datetime.now(timezone.utc)
        db.commit()

        asset_count = db.query(Asset).filter(Asset.scan_id == scan_id).count()
        log.info("scan_completed", scan_id=scan_id, repo_url=repo_url, asset_count=asset_count)

    except Exception as e:
        db.rollback()
        # Re-attach scan before modifying
        db.add(scan)
        scan.status = "failed"
        scan.error_message = str(e)
        scan.completed_at = datetime.now(timezone.utc)
        db.commit()
        log.error("scan_failed", scan_id=scan_id, error=str(e))
    finally:
        db.close()
