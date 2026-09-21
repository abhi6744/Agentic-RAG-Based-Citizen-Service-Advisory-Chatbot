import re
with open('app/services/agentic_controller.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replacement 1: step 9
old_step_9 = '''    # -- Step 9: parse structured sections -------------------------------------
    summary, docs_elig, next_steps = _parse_response_sections(llm_response)'''
new_step_9 = '''    # -- Step 9: parse structured sections -------------------------------------
    answer_data = _parse_response_sections(llm_response)'''
code = code.replace(old_step_9, new_step_9)

# Replacement 2: privacy
old_privacy = '''            return _build_result(
                assistant_msg, conversation.id, None, "fallback",
                PRIVACY_RESPONSE, None, None, [], 0.0, "low",
                "Please do not share sensitive information.",
                None, privacy_result.warning_message,
            )'''
new_privacy = '''            return _build_result(
                assistant_msg, conversation.id, None, "fallback",
                {"summary": PRIVACY_RESPONSE, "eligibility": [], "documents": [], "next_steps": [], "where_to_go": [], "warning": "Please do not share sensitive information."}, [], 0.0, "low",
                "Please do not share sensitive information.",
                None, privacy_result.warning_message,
            )'''
code = code.replace(old_privacy, new_privacy)

# Replacement 3: general
old_general = '''        return _build_result(
            assistant_msg, conversation.id, None, "general",
            response_text, None, None, [], 0.0, "low",
            "", None, None
        )'''
new_general = '''        return _build_result(
            assistant_msg, conversation.id, None, "general",
            {"summary": response_text, "eligibility": [], "documents": [], "next_steps": [], "where_to_go": [], "warning": ""}, [], 0.0, "low",
            "", None, None
        )'''
code = code.replace(old_general, new_general)

# Replacement 4: unsupported
old_unsupported = '''        return _build_result(
            assistant_msg, conversation.id, "unsupported", "out_of_scope",
            response_text, None, None, [], 0.0, "low",
            "", image_description, None,
        )'''
new_unsupported = '''        return _build_result(
            assistant_msg, conversation.id, "unsupported", "out_of_scope",
            {"summary": response_text, "eligibility": [], "documents": [], "next_steps": [], "where_to_go": [], "warning": ""}, [], 0.0, "low",
            "", image_description, None,
        )'''
code = code.replace(old_unsupported, new_unsupported)

# Replacement 5: clarification
old_clarification = '''            return _build_result(
                assistant_msg, conversation.id, None, "clarification",
                response_text, None, None, [], 0.0, "low",
                "", None, None
            )'''
new_clarification = '''            return _build_result(
                assistant_msg, conversation.id, None, "clarification",
                {"summary": response_text, "eligibility": [], "documents": [], "next_steps": [], "where_to_go": [], "warning": ""}, [], 0.0, "low",
                "", None, None
            )'''
code = code.replace(old_clarification, new_clarification)

# Replacement 6: low confidence fallback
old_fallback = '''            return _build_result(
                assistant_msg, conversation.id, intent.primary_service, "fallback",
                FALLBACK_RESPONSE, None, None, [], confidence.confidence_score,
                confidence.confidence_level, confidence.verification_message,
                image_description, None,
            )'''
new_fallback = '''            return _build_result(
                assistant_msg, conversation.id, intent.primary_service, "fallback",
                {"summary": FALLBACK_RESPONSE, "eligibility": [], "documents": [], "next_steps": [], "where_to_go": [], "warning": confidence.verification_message}, [], confidence.confidence_score,
                confidence.confidence_level, confidence.verification_message,
                image_description, None,
            )'''
code = code.replace(old_fallback, new_fallback)

# Replacement 7: API Error fallback
old_api_error = '''        return _build_result(
            assistant_msg, conversation.id, intent.primary_service, "service_unavailable",
            api_msg, None, None, None, None,
            None, "", image_description, None,
        )'''
new_api_error = '''        return _build_result(
            assistant_msg, conversation.id, intent.primary_service, "service_unavailable",
            {"summary": api_msg, "eligibility": [], "documents": [], "next_steps": [], "where_to_go": [], "warning": ""}, [], None,
            None, "", image_description, None,
        )'''
code = code.replace(old_api_error, new_api_error)

# Replacement 8: final return
old_final = '''    return _build_result(
        assistant_msg, conversation.id, intent.primary_service, "answer" if hallucination_passed else "fallback",
        summary, docs_elig, next_steps, citations,
        confidence.confidence_score, confidence.confidence_level,
        confidence.verification_message, image_description, None,
    )'''
new_final = '''    return _build_result(
        assistant_msg, conversation.id, intent.primary_service, "answer" if hallucination_passed else "fallback",
        answer_data, citations,
        confidence.confidence_score, confidence.confidence_level,
        confidence.verification_message, image_description, None,
    )'''
code = code.replace(old_final, new_final)

with open('app/services/agentic_controller.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done replacing.")
