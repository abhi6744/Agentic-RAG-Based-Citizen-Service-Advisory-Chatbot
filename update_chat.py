import re

with open('akshaya-backend/app/routes/chat.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("from fastapi import APIRouter, Depends, File, Form, UploadFile", "from fastapi import APIRouter, Depends, File, Form, UploadFile\nfrom fastapi.responses import JSONResponse")
content = content.replace("@router.post(\"/chat\", response_model=ChatResponse)", "@router.post(\"/chat\")")

old_image_validation = """    if image and image.filename:
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
            
        upload_dir = settings.upload_dir
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        ext = os.path.splitext(image.filename)[1] or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        image_path = os.path.join(upload_dir, filename)
        
        contents = await image.read()
        with open(image_path, "wb") as f:
            f.write(contents)"""

new_image_validation = """    if image and image.filename:
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
            f.write(contents)"""

content = content.replace(old_image_validation, new_image_validation)

with open('akshaya-backend/app/routes/chat.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated chat.py backend validation")
