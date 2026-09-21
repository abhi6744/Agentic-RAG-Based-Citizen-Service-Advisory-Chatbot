from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.db_models import Feedback, Message
from app.schemas.chat import FeedbackRequest, FeedbackResponse

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db),
):
    """Submit feedback for a message."""
    # Verify message exists
    message = db.query(Message).filter(Message.id == request.message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Check for existing feedback
    existing = (
        db.query(Feedback)
        .filter(Feedback.message_id == request.message_id)
        .first()
    )

    if existing:
        existing.feedback_type = request.feedback_type
        existing.comment = request.comment
    else:
        feedback = Feedback(
            message_id=request.message_id,
            feedback_type=request.feedback_type,
            comment=request.comment,
        )
        db.add(feedback)

    db.commit()

    return FeedbackResponse(
        status="success",
        message=(
            f"Feedback '{request.feedback_type}' recorded "
            f"for message {request.message_id}"
        ),
    )
