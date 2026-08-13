"""
ORM Models — SQLAlchemy table definitions.

Data model:
  scans    — one scan per repo invocation
  assets   — discovered AI assets (many per scan)
  evidence — raw evidence records (many per asset)
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    String, Text, Float, Integer, ForeignKey, DateTime, Enum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    repo_url: Mapped[str] = mapped_column(Text, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("pending", "running", "completed", "failed", name="scan_status"),
        default="pending",
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    assets: Mapped[list["Asset"]] = relationship("Asset", back_populates="scan", cascade="all, delete-orphan")


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id: Mapped[str] = mapped_column(String(36), ForeignKey("scans.id"), nullable=False)

    # Core asset fields (matches PRD §5.4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    asset_type: Mapped[str] = mapped_column(Text, nullable=False)      # AI Agent / AI Application / Model Integration
    llm_or_model: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(Text, default="local")
    application: Mapped[str] = mapped_column(Text, nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    discovery_source: Mapped[str] = mapped_column(Text, default="local")  # local | GitHub | Cloud
    status: Mapped[str] = mapped_column(
        Enum("Discovered", "Inferred", "Pending Review", name="asset_status"),
        nullable=False,
    )
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)

    scan: Mapped["Scan"] = relationship("Scan", back_populates="assets")
    evidence: Mapped[list["Evidence"]] = relationship("Evidence", back_populates="asset", cascade="all, delete-orphan")


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id: Mapped[str] = mapped_column(String(36), ForeignKey("assets.id"), nullable=False)

    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, default=0)
    signal_type: Mapped[str] = mapped_column(Text, nullable=False)
    matched_value: Mapped[str] = mapped_column(Text, nullable=False)
    snippet: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_weight: Mapped[float] = mapped_column(Float, default=1.0)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="evidence")
