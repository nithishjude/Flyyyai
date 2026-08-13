"""
Doc Search — Semantic Document Search Service
A FastAPI service that uses sentence-transformers embeddings + FAISS for document similarity search.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routes.search import router as search_router
from routes.ingest import router as ingest_router
from routes.health import router as health_router

load_dotenv()

app = FastAPI(
    title="Doc Search API",
    description="Semantic document search powered by sentence-transformers embeddings",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router, prefix="/api/v1/search", tags=["search"])
app.include_router(ingest_router, prefix="/api/v1/ingest", tags=["ingest"])
app.include_router(health_router, prefix="/health", tags=["health"])


@app.get("/")
async def root():
    return {"service": "doc-search", "version": "1.0.0"}
