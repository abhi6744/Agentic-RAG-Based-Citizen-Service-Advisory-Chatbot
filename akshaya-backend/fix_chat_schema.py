import re
from pathlib import Path

f = Path('app/schemas/chat.py')
text = f.read_text(encoding='utf-8')

old_schema = '''class ChatResponse(BaseModel):
    message_id: int
    conversation_id: int
    response_type: str = "answer"  # "clarification" | "answer" | "fallback" | "out_of_scope" | "general"
    detected_service: Optional[str] = None
    summary: str
    documents_and_eligibility: Optional[str] = None
    next_steps: Optional[str] = None
    citations: list[SourceCitation] = []
    confidence_score: float = Field(ge=0.0, le=1.0)
    confidence_level: str = Field(description="low, medium, or high")
    requires_official_verification: bool = True
    verification_message: str = (
        "Please verify current requirements with your nearest Akshaya Centre "
        "or the official government portal, as rules and documents may change."
    )
    image_description: Optional[str] = None
    privacy_warning: Optional[str] = None
    created_at: datetime'''

new_schema = '''class ChatResponse(BaseModel):
    message_id: int
    conversation_id: int
    response_type: str = "answer"  # "clarification" | "answer" | "fallback" | "out_of_scope" | "general" | "service_unavailable"
    detected_service: Optional[str] = None
    summary: str
    documents_and_eligibility: Optional[str] = None
    next_steps: Optional[str] = None
    citations: Optional[list[SourceCitation]] = []
    confidence_score: Optional[float] = None
    confidence_level: Optional[str] = None
    requires_official_verification: bool = True
    verification_message: str = (
        "Please verify current requirements with your nearest Akshaya Centre "
        "or the official government portal, as rules and documents may change."
    )
    image_description: Optional[str] = None
    privacy_warning: Optional[str] = None
    created_at: datetime'''

text = text.replace(old_schema, new_schema)
f.write_text(text, encoding='utf-8')
