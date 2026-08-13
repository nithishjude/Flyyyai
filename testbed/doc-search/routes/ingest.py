"""
Ingest route — accepts documents and adds them to the vector store.
"""

from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.embedding_service import ingest_document

router = APIRouter()


class Document(BaseModel):
    doc_id: str
    title: str
    content: str
    metadata: dict = {}


class IngestResponse(BaseModel):
    doc_id: str
    status: str
    chunks_indexed: int


@router.post("/document", response_model=IngestResponse)
async def ingest_single_document(document: Document):
    """
    Embed a document and add it to the FAISS vector store.
    """
    try:
        chunks = await ingest_document(
            doc_id=document.doc_id,
            title=document.title,
            content=document.content,
            metadata=document.metadata,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

    return IngestResponse(doc_id=document.doc_id, status="indexed", chunks_indexed=chunks)


@router.post("/batch")
async def ingest_batch(documents: List[Document]):
    """Batch ingest multiple documents."""
    results = []
    for doc in documents:
        try:
            chunks = await ingest_document(
                doc_id=doc.doc_id,
                title=doc.title,
                content=doc.content,
                metadata=doc.metadata,
            )
            results.append({"doc_id": doc.doc_id, "status": "indexed", "chunks": chunks})
        except Exception as e:
            results.append({"doc_id": doc.doc_id, "status": "error", "error": str(e)})
    return {"results": results}
