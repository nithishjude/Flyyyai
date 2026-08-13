"""
Pydantic v2 schemas — request/response shapes for the API.
Kept separate from ORM models to maintain a clean separation between
persistence layer and API contract.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Scan schemas
# ---------------------------------------------------------------------------

class ScanCreate(BaseModel):
    repo_url: str = Field(
        ...,
        description="Local path or GitHub URL to the repository to scan",
        examples=["d:/fly/testbed", "https://github.com/org/repo"],
    )


class ScanOut(BaseModel):
    id: str
    repo_url: str
    started_at: datetime
    completed_at: Optional[datetime]
    status: str
    error_message: Optional[str] = None
    asset_count: int = 0

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Evidence schemas
# ---------------------------------------------------------------------------

class EvidenceOut(BaseModel):
    id: str
    file_path: str
    line_number: int
    signal_type: str
    matched_value: str
    snippet: str
    confidence_weight: float

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Asset schemas
# ---------------------------------------------------------------------------

class AssetListItem(BaseModel):
    """Lightweight asset representation for list views."""
    id: str
    name: str
    asset_type: str
    llm_or_model: Optional[str]
    provider: str
    application: str
    status: str
    confidence_score: float
    discovery_source: str

    model_config = {"from_attributes": True}


class AssetDetail(BaseModel):
    """Full asset detail including linked evidence records."""
    id: str
    scan_id: str
    name: str
    asset_type: str
    llm_or_model: Optional[str]
    provider: str
    location: str
    application: str
    purpose: str
    discovery_source: str
    status: str
    confidence_score: float
    evidence: List[EvidenceOut] = []

    model_config = {"from_attributes": True}


class AssetListResponse(BaseModel):
    assets: List[AssetListItem]
    total: int
    scan_id: Optional[str] = None
