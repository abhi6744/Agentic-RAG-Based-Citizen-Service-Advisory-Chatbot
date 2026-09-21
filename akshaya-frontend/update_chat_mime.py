import re

with open('../akshaya-backend/app/routes/chat.py', 'r', encoding='utf-8') as f:
    content = f.read()

validation_code = """    # Handle image upload
    if image and image.filename:
        if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
            return ChatResponse(
                success=False,
                status="image_analysis_failed",
                message_id=-1,
                conversation_id=conversation_id or -1,
                answer={
                    "summary": "I could not evaluate this image right now. Please upload a clearer document image or describe your question in text.",
                    "eligibility": [],
                    "documents": [],
                    "next_steps": [],
                    "where_to_go": [],
                    "warning": "Please upload a JPG, PNG, or WEBP document image."
                },
                requires_official_verification=True,
                created_at=datetime.utcnow()
            )
            
        upload_dir = settings.upload_dir"""

content = content.replace("""    # Handle image upload
    if image and image.filename:
        upload_dir = settings.upload_dir""", validation_code)

with open('../akshaya-backend/app/routes/chat.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Added MIME type validation to chat route.")
