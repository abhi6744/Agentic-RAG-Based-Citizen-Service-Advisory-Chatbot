from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.init_db import init_database, populate_document_registry
from app.models.db_models import Conversation, Message, MessageSource
from app.services.whisper_service import transcribe_audio_file
from app.routes import chat, feedback, health, services
from app.schemas.chat import (
    ConversationMessage,
    ConversationResponse,
    ConversationListResponse,
    SourceCitation,
)
from app.services.retriever import get_retriever


from app.config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    # Startup
    print("Initializing database...")
    settings = get_settings()
    has_grok = bool(settings.grok_api_key)
    print(f"Startup Config Check: GROK_API_KEY loaded: {has_grok}")
    print(f"Startup Config Check: Grok Model Configured: grok-2-latest")
    init_database()
    populate_document_registry()

    print("Loading vector retriever...")
    retriever = get_retriever()
    retriever.load()

    print("Akshaya Advisory backend ready.")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="Akshaya Advisory API",
    description=(
        "Agentic RAG-based citizen-service advisory chatbot "
        "for Akshaya Centres, Kerala"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(feedback.router, tags=["Feedback"])
app.include_router(services.router, tags=["Services"])

from fastapi.responses import FileResponse
import os

app_settings = get_settings()
os.makedirs(app_settings.upload_dir, exist_ok=True)

@app.post("/transcribe", tags=["Audio"])
async def transcribe_audio(audio: UploadFile = File(...)):
    import shutil
    import uuid
    # Save temp audio file
    ext = audio.filename.split('.')[-1] if '.' in audio.filename else 'wav'
    temp_path = os.path.join(app_settings.upload_dir, f"{uuid.uuid4()}.{ext}")
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
        
    try:
        transcript = transcribe_audio_file(temp_path)
        return {"text": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/uploads/{filename}", tags=["Uploads"])
async def get_upload(filename: str):
    file_path = os.path.join(app_settings.upload_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@app.get(
    "/conversations",
    response_model=list[ConversationListResponse],
    tags=["Conversations"],
)
def list_conversations(
    device_id: str = "default",
    db: Session = Depends(get_db),
):
    """List all conversations for a user/device."""
    from app.models.db_models import User
    user = db.query(User).filter(User.device_id == device_id).first()
    if not user:
        return []
    
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )
    
    result = []
    for c in convs:
        # Get latest message for preview and count
        msgs = db.query(Message).filter(Message.conversation_id == c.id).order_by(Message.created_at.desc()).all()
        if not msgs:
            continue
            
        first_user_msg = next((m for m in reversed(msgs) if m.role == 'user'), None)
        latest_user_msg = next((m for m in msgs if m.role == 'user'), None)
        preview_text = latest_user_msg.text_content if latest_user_msg else "Image uploaded"
        
        # detect category
        category = "all"
        category_label = "General"
        if latest_user_msg and latest_user_msg.detected_service:
            if "aadhaar" in latest_user_msg.detected_service.lower():
                category = "aadhaar_update"
                category_label = "Aadhaar"
            elif "ration" in latest_user_msg.detected_service.lower():
                category = "documents" # Using generic documents category or maybe we should adapt history.tsx
                category_label = "Ration Card"
            elif "scholarship" in latest_user_msg.detected_service.lower():
                category = "documents"
                category_label = "Scholarship"
                
        # Format date
        # Very simple date label logic
        updated_label = c.created_at.strftime("%b %d, %Y")
        
        result.append(ConversationListResponse(
            id=str(c.id),
            title=c.title or (first_user_msg.text_content[:30] + "..." if first_user_msg and first_user_msg.text_content else "Conversation"),
            preview=preview_text[:50] + ("..." if len(preview_text) > 50 else ""),
            category=category,
            categoryLabel=category_label,
            updatedLabel=updated_label,
            messageCount=len(msgs)
        ))
    return result



@app.get(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
    tags=["Conversations"],
)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    """Get full message history for a conversation."""
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )

    msg_list = []
    for msg in messages:
        sources = (
            db.query(MessageSource)
            .filter(MessageSource.message_id == msg.id)
            .all()
        )
        source_citations = [
            SourceCitation(
                source_title=s.source_title,
                source_url=s.source_url,
                authority=s.authority,
                retrieved_date=(
                    str(s.retrieved_date) if s.retrieved_date else None
                ),
            )
            for s in sources
        ]

        msg_list.append(
            ConversationMessage(
                id=msg.id,
                role=msg.role,
                text_content=msg.text_content,
                input_type=msg.input_type,
                image_path=os.path.basename(msg.image_path) if msg.image_path else None,
                detected_service=msg.detected_service,
                confidence_score=msg.confidence_score,
                requires_verification=msg.requires_verification,
                sources=source_citations,
                created_at=msg.created_at,
            )
        )

    return ConversationResponse(
        conversation_id=conv.id,
        title=conv.title,
        messages=msg_list,
        created_at=conv.created_at,
    )
