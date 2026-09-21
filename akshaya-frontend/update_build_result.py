import re

with open('../akshaya-backend/app/services/agentic_controller.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace _build_result
new_build_result = """def _build_result(
    assistant_msg: Message,
    conversation_id: int,
    detected_service: str | None,
    response_type: str,
    answer_data: dict,
    citations: list[dict] | None,
    confidence_score: float | None,
    confidence_level: str | None,
    verification_message: str,
    image_description: str | None,
    privacy_warning: str | None,
    image_analysis: dict | None = None,
    success: bool = True,
    status: str = "grounded_answer",
) -> dict:
    return {
        "success": success,
        "status": status if response_type == "answer" else response_type,
        "message_id": assistant_msg.id,
        "conversation_id": conversation_id,
        "response_type": response_type,
        "detected_service": detected_service,
        "answer": answer_data,
        "citations": citations,
        "confidence_score": confidence_score,
        "confidence_level": confidence_level,
        "requires_official_verification": True,
        "verification_message": verification_message,
        "image_description": image_description,
        "privacy_warning": privacy_warning,
        "image_analysis": image_analysis,
    }"""
content = re.sub(r'def _build_result\([\s\S]*?return \{[\s\S]*?"privacy_warning": privacy_warning,\n    \}', new_build_result, content)

with open('../akshaya-backend/app/services/agentic_controller.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated _build_result in agentic_controller.")
