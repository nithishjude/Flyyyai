"""
FastAPI application — main entry point.

CORS is configured to allow the Next.js frontend on localhost:3000.
Tables are created on startup via SQLAlchemy metadata.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_tables
from app.routers import scans, assets


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables on startup, nothing special on shutdown."""
    create_tables()
    yield


app = FastAPI(
    title="AI Asset Discovery API",
    description=(
        "Automatically discovers AI usage across codebases and represents each "
        "finding as a structured, evidence-backed AI asset."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow the Next.js dev server and any local origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scans.router, prefix="/scans", tags=["scans"])
app.include_router(assets.router, prefix="/assets", tags=["assets"])


@app.get("/", tags=["health"])
def root():
    return {
        "service": "ai-asset-discovery-api",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}
