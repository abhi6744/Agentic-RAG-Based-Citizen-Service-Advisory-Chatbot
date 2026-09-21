import re

with open('../akshaya-backend/app/routes/chat.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add os.remove(image_path) in a finally block
new_block = """    finally:
        # User requirement: Delete temporary files after processing.
        # Never permanently store sensitive images by default.
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                print(f"Failed to delete temp image: {e}")"""

# We need to wrap the process_query and return in a try block.
old_process = """    # Process through the agentic RAG pipeline
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
    )"""

new_process = """    try:
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
""" + new_block

content = content.replace(old_process, new_process)

with open('../akshaya-backend/app/routes/chat.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated chat.py to delete temp files.")
