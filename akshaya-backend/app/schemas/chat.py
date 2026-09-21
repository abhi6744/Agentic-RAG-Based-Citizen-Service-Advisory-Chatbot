from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    source_title: str
    source_url: Optional[str] = None
    authority: str
    retrieved_date: Optional[str] = None


class AnswerData(BaseModel):
    summary: str
    eligibility: list[str] = []
    documents: list[str] = []
    next_steps: list[str] = []
    where_to_go: list[str] = []
    warning: str

class ImageAnalysisData(BaseModel):
    document_type: str
    confidence: float
    sensitive_data_hidden: bool

class ChatResponse(BaseModel):
    success: bool = True
    status: str = "grounded_answer"
    message_id: int
    conversation_id: int
    response_type: str = "answer"  # "clarification" | "answer" | "fallback" | "out_of_scope" | "general" | "service_unavailable"
    detected_service: Optional[str] = None
    intent: Optional[str] = None
    answer: AnswerData
    citations: Optional[list[SourceCitation]] = []
    confidence_score: Optional[float] = None
    confidence_level: Optional[str] = None
    requires_official_verification: bool = True
    verification_message: str = (
        "Please verify current requirements with your nearest Akshaya Centre "
        "or the official government portal, as rules and documents may change."
    )
    image_description: Optional[str] = None
    image_analysis: Optional[ImageAnalysisData] = None
    privacy_warning: Optional[str] = None
    created_at: datetime


class FeedbackRequest(BaseModel):
    message_id: int
    feedback_type: str = Field(pattern=r"^(helpful|not_helpful)$")
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    status: str
    message: str


class ConversationMessage(BaseModel):
    id: int
    role: str
    text_content: Optional[str] = None
    input_type: Optional[str] = "text"
    image_path: Optional[str] = None
    detected_service: Optional[str] = None
    confidence_score: Optional[float] = None
    requires_verification: Optional[bool] = None
    sources: list[SourceCitation] = []
    created_at: datetime


class ConversationResponse(BaseModel):
    conversation_id: int
    title: Optional[str] = None
    messages: list[ConversationMessage]
    created_at: datetime


class ConversationListResponse(BaseModel):
    id: str
    title: str
    preview: str
    category: str
    categoryLabel: str
    updatedLabel: str
    messageCount: int
