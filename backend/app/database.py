"""
Database configuration — SQLAlchemy engine + session factory.
Uses connection pooling appropriate for a single-process FastAPI app.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://aiuser:aipass@localhost:5432/aiassets",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,     # Detect stale connections
    pool_size=5,
    max_overflow=10,
    echo=False,             # Set True to log SQL queries (dev only)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency — yields a DB session and ensures cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create all tables defined by ORM models. Called on app startup."""
    from app.models import Scan, Asset, Evidence  # noqa: F401 — import triggers table registration
    Base.metadata.create_all(bind=engine)
