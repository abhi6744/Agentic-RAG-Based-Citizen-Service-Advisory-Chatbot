import re
from pathlib import Path

f = Path('app/services/agentic_controller.py')
text = f.read_text(encoding='utf-8')

old_flow = '''    # -- Step 1: privacy filter ------------------------------------------------
    if query_text:
        privacy_result = check_privacy(query_text)
        if privacy_result.contains_sensitive_data:
            user_msg = _save_user_message(
                db, conversation.id, privacy_result.sanitized_text, image_path
            )
            assistant_msg = _save_assistant_message(
                db, conversation.id, PRIVACY_RESPONSE,
                detected_service=None, confidence_score=0.0,
                requires_verification=True,
            )
            _save_audit_log(db, assistant_msg.id, [], True)
            db.commit()
            return _build_result(
                assistant_msg, conversation.id, None, "fallback",
                PRIVACY_RESPONSE, None, None, [], 0.0, "low",
                "Please do not share sensitive information.",
                None, privacy_result.warning_message,
            )

    # -- Step 2: image description ---------------------------------------------
    if image_path and os.path.exists(image_path):
        try:
            image_description = llm.describe_image(image_path)
            query_text = f"{query_text} [Image: {image_description}]".strip()
        except Exception as e:
            image_description = f"Could not process image: {e}"'''

new_flow = '''    # -- Step 1: image description ---------------------------------------------
    if image_path and os.path.exists(image_path):
        try:
            image_description = llm.describe_image(image_path)
            query_text = f"{query_text} [Image: {image_description}]".strip()
        except Exception as e:
            image_description = f"Could not process image: {e}"

    # -- Step 2: privacy filter ------------------------------------------------
    if query_text:
        privacy_result = check_privacy(query_text)
        if privacy_result.contains_sensitive_data:
            user_msg = _save_user_message(
                db, conversation.id, privacy_result.sanitized_text, image_path
            )
            assistant_msg = _save_assistant_message(
                db, conversation.id, PRIVACY_RESPONSE,
                detected_service=None, confidence_score=0.0,
                requires_verification=True,
            )
            _save_audit_log(db, assistant_msg.id, [], True)
            db.commit()
            return _build_result(
                assistant_msg, conversation.id, None, "fallback",
                PRIVACY_RESPONSE, None, None, [], 0.0, "low",
                "Please do not share sensitive information.",
                None, privacy_result.warning_message,
            )'''

text = text.replace(old_flow, new_flow)
f.write_text(text, encoding='utf-8')
