import re
from pathlib import Path

f = Path('app/services/agentic_controller.py')
text = f.read_text(encoding='utf-8')

# The signature of _save_audit_log was already updated by the previous run?
# Let's check:
if "model_provider: str = " not in text:
    old_log = '''def _save_audit_log(
    db: Session,
    message_id: int,
    chunks: list[RetrievedChunk],
    hallucination_check_passed: bool,
) -> None:'''
    new_log = '''def _save_audit_log(
    db: Session,
    message_id: int,
    chunks: list[RetrievedChunk],
    hallucination_check_passed: bool | None,
    model_provider: str = "gemini",
) -> None:'''
    text = text.replace(old_log, new_log)
    
    old_log_args = '''        hallucination_check_passed=hallucination_check_passed,
    )'''
    new_log_args = '''        hallucination_check_passed=hallucination_check_passed,
        model_provider=model_provider,
    )'''
    text = text.replace(old_log_args, new_log_args)


start_marker = "    # -- Step 6: LLM generation ------------------------------------------------"
end_marker = "    # -- Step 8: confidence scoring --------------------------------------------"

start_idx = text.find(start_marker)
end_idx = text.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Markers not found again!")
    print("Start:", start_idx, "End:", end_idx)
else:
    new_block = '''    # -- Step 6: LLM generation ------------------------------------------------
    chunk_dicts = [
        {
            "text": c.text,
            "source_title": c.source_title,
            "source_url": c.source_url,
            "authority": c.authority,
        }
        for c in chunks
    ]

    llm_result = llm.generate_response(
        chunk_dicts, text or "", image_description
    )

    if not llm_result.success:
        print(f"LLM API Error: {llm_result.error}")
        assistant_msg = _save_assistant_message(
            db, conversation.id, "The assistant is temporarily busy. Please try again in a moment.",
            detected_service=intent.primary_service,
            confidence_score=None,
            requires_verification=True,
        )
        _save_audit_log(db, assistant_msg.id, chunks, None, llm_result.model_provider)
        db.commit()
        
        return _build_result(
            assistant_msg, conversation.id, intent.primary_service, "service_unavailable",
            "The assistant is temporarily busy. Please try again in a moment.", None, None, [], 0.0,
            "low", "", image_description, None,
        )

    llm_response = llm_result.text

    # -- Step 7: citation validation -------------------------------------------
    validation = validate_response(llm_response, chunk_dicts)

    if not validation.is_valid:
        llm_response = FALLBACK_RESPONSE
        hallucination_passed = False
    else:
        hallucination_passed = True

'''
    text = text[:start_idx] + new_block + text[end_idx:]

    # Step 10: save to database - we also need to pass the model_provider
    old_step_10 = '''    _save_audit_log(db, assistant_msg.id, chunks, hallucination_passed)'''
    new_step_10 = '''    _save_audit_log(db, assistant_msg.id, chunks, hallucination_passed, llm_result.model_provider)'''
    text = text.replace(old_step_10, new_step_10)

f.write_text(text, encoding='utf-8')
