import sys

with open('app/routes/chat.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_return = '''    return ChatResponse(
        message_id=result["message_id"],
        conversation_id=result["conversation_id"],
        response_type=result.get("response_type", "answer"),
        detected_service=result.get("detected_service"),
        summary=result["summary"],
        documents_and_eligibility=result.get("documents_and_eligibility"),
        next_steps=result.get("next_steps"),
        citations=citations,
        confidence_score=result["confidence_score"],
        confidence_level=result["confidence_level"],
        requires_official_verification=True,
        verification_message=result.get("verification_message", ""),
        image_description=result.get("image_description"),
        privacy_warning=result.get("privacy_warning"),
        created_at=result.get("created_at", datetime.utcnow()),
    )'''

new_return = '''    return ChatResponse(
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
        privacy_warning=result.get("privacy_warning"),
        created_at=result.get("created_at", datetime.utcnow()),
    )'''

content = content.replace(old_return, new_return)

with open('app/routes/chat.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done fixing chat.py")
