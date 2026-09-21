import os
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.chat import ChatResponse, SourceCitation
from app.services.agentic_controller import process_query
from app.config import get_settings

settings = get_settings()
router = APIRouter()

@router.post("/chat")
async def chat_endpoint(
    device_id: str = Form(...),
    conversation_id: Optional[int] = Form(None),
    text: Optional[str] = Form(None),
    input_type: str = Form("text"),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """Process a chat message with text and/or image input."""
    image_path = None
    
    # Handle image upload
    if image and image.filename:
        contents = await image.read()
        if not contents or len(contents) == 0 or image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "status": "invalid_image",
                    "error_code": "INVALID_IMAGE",
                    "message": "The uploaded file is empty or is not a valid JPG, PNG, or WEBP image."
                }
            )
            
        upload_dir = settings.upload_dir
        os.makedirs(upload_dir, exist_ok=True)
        
        ext = os.path.splitext(image.filename)[1] or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        image_path = os.path.join(upload_dir, filename)
        
        with open(image_path, "wb") as f:
            f.write(contents)
    
    try:
        # Process through the agentic RAG pipeline
        result = await process_query(
            db=db,
            text=text,
            image_path=image_path,
            conversation_id=conversation_id,
            device_id=device_id,
            input_type=input_type,
        )
        
        # Map result to response schema
        citations = [
            SourceCitation(
                source_title=c["source_title"],
                source_url=c.get("source_url"),
                authority=c["authority"],
                retrieved_date=c.get("retrieved_date"),
            )
            for c in (result.get("citations") or [])
        ]
        
        return ChatResponse(
            success=result.get("success", True),
            status=result.get("status", "grounded_answer"),
            message_id=result["message_id"],
            conversation_id=result["conversation_id"],
            response_type=result.get("response_type", "answer"),
            detected_service=result.get("detected_service"),
            intent=result.get("intent"),
            answer=result.get("answer", {}),
            citations=citations,
            confidence_score=result.get("confidence_score"),
            confidence_level=result.get("confidence_level"),
            requires_official_verification=result.get("requires_official_verification", True),
            verification_message=result.get("verification_message", ""),
            image_description=result.get("image_description"),
            image_analysis=result.get("image_analysis"),
            privacy_warning=result.get("privacy_warning"),
            created_at=result.get("created_at", datetime.utcnow()),
        )
    finally:
        # User requirement: Delete temporary files after processing.
        # Never permanently store sensitive images by default.
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                print(f"Failed to delete temp image: {e}")
