from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Text,
    String,
)
from sqlalchemy.sql import func

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Text, unique=True)
    created_at = Column(DateTime, server_default=func.now())


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(Text, CheckConstraint("role IN ('user','assistant')"))
    text_content = Column(Text)
    image_path = Column(Text)
    input_type = Column(Text, default="text")
    detected_service = Column(Text)
    confidence_score = Column(Float)
    requires_verification = Column(Boolean)
    created_at = Column(DateTime, server_default=func.now())


class MessageSource(Base):
    __tablename__ = "message_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    source_title = Column(Text)
    source_url = Column(Text)
    authority = Column(Text)
    retrieved_date = Column(Date)


class DocumentRegistry(Base):
    __tablename__ = "document_registry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text)
    service_category = Column(
        Text,
        CheckConstraint(
            "service_category IN ('aadhaar','ration_card','scholarship')"
        ),
    )
    authority = Column(Text)
    source_url = Column(Text)
    file_path = Column(Text)
    retrieved_date = Column(Date)
    last_verified_date = Column(Date)
    chunk_count = Column(Integer)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    feedback_type = Column(
        Text, CheckConstraint("feedback_type IN ('helpful','not_helpful')")
    )
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class QueryAuditLog(Base):
    __tablename__ = "query_audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    retrieved_chunk_ids = Column(Text)  # JSON array of chunk IDs
    similarity_scores = Column(Text)  # JSON array of floats
    hallucination_check_passed = Column(Boolean, nullable=True)
    model_provider = Column(String, default="unknown", nullable=True)
    created_at = Column(DateTime, server_default=func.now())
