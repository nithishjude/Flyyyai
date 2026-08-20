"""
FastAPI application — main entry point.

CORS is configured to allow the Next.js frontend on localhost:3000, plus
any origins listed in the CORS_ORIGINS env var (comma-separated) for
deployed environments (e.g. the Vercel frontend URL).
Tables are created on startup via SQLAlchemy metadata.
"""

import os
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

# CORS — allow the Next.js dev server, local origins, and any deployed
# frontend origins listed in CORS_ORIGINS (comma-separated, e.g.
# "https://your-app.vercel.app,https://your-app-git-main.vercel.app")
_extra_origins = [
    o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        *_extra_origins,
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
