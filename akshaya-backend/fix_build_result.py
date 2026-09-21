import re
from pathlib import Path

f = Path('app/services/agentic_controller.py')
text = f.read_text(encoding='utf-8')

old_def = '''def _build_result(
    assistant_msg: Message,
    conversation_id: int,
    detected_service: str | None,
    response_type: str,
    summary: str,
    docs_elig: str | None,
    next_steps: str | None,
    citations: list[dict],
    confidence_score: float,
    confidence_level: str,
    verification_message: str,
    image_description: str | None,
    privacy_warning: str | None,
) -> dict:'''

new_def = '''def _build_result(
    assistant_msg: Message,
    conversation_id: int,
    detected_service: str | None,
    response_type: str,
    summary: str,
    docs_elig: str | None,
    next_steps: str | None,
    citations: list[dict] | None,
    confidence_score: float | None,
    confidence_level: str | None,
    verification_message: str,
    image_description: str | None,
    privacy_warning: str | None,
) -> dict:'''

text = text.replace(old_def, new_def)

# Also update the return call inside the service_unavailable block
old_ret = '''        return _build_result(
            assistant_msg, conversation.id, intent.primary_service, "service_unavailable",
            "The assistant is temporarily busy. Please try again in a moment.", None, None, [], 0.0,
            "low", "", image_description, None,
        )'''
new_ret = '''        return _build_result(
            assistant_msg, conversation.id, intent.primary_service, "service_unavailable",
            "The assistant is temporarily busy. Please try again in a moment.", None, None, None, None,
            None, "", image_description, None,
        )'''
text = text.replace(old_ret, new_ret)

f.write_text(text, encoding='utf-8')
