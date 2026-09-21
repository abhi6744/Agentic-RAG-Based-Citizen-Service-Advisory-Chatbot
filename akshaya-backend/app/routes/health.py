from datetime import datetime, timezone
from fastapi import APIRouter
from app.schemas.common import HealthResponse
from app.services.retriever import get_retriever

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    retriever = get_retriever()
    
    # Defaults
    status = "healthy"
    message = "Service is operating normally."
    rag_loaded = retriever._loaded
    vector_count = 0
    docs_loaded = 0
    
    if rag_loaded and retriever._index is not None:
        vector_count = retriever._index.ntotal
        if retriever._metadata:
            docs_loaded = len(set(meta.get("source_title") for meta in retriever._metadata.values()))
    else:
        status = "degraded"
        message = "Run document ingestion before using /chat."
        
    return HealthResponse(
        status=status,
        service="akshaya-advisory-backend",
        timestamp=datetime.now(timezone.utc),
        rag_index_loaded=rag_loaded,
        vector_count=vector_count,
        documents_loaded=docs_loaded,
        message=message
    )
