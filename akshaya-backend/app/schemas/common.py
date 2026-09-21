from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime
    rag_index_loaded: Optional[bool] = None
    vector_count: Optional[int] = None
    documents_loaded: Optional[int] = None
    message: Optional[str] = None


class ServiceInfo(BaseModel):
    id: str
    name: str
    description: str
    sample_question: str


class ServicesResponse(BaseModel):
    services: list[ServiceInfo]
