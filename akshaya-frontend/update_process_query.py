import re

with open('../akshaya-backend/app/services/agentic_controller.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace image processing block
old_img_block = """    # -- Step 1: image description ---------------------------------------------
    if image_path and os.path.exists(image_path):
        try:
            image_description = llm.describe_image(image_path)
            query_text = f"{query_text} [Image: {image_description}]".strip()
        except Exception as e:
            image_description = f"Could not process image: {e}\""""

new_img_block = """    # -- Step 1: image description ---------------------------------------------
    image_analysis_data = None
    if image_path and os.path.exists(image_path):
        try:
            image_result = llm.describe_image(image_path)
            image_description = image_result.get("description", "Unknown image")
            image_analysis_data = {
                "document_type": image_result.get("document_type", "Unknown"),
                "confidence": float(image_result.get("confidence", 0.0)),
                "sensitive_data_hidden": bool(image_result.get("sensitive_data_hidden", False))
            }
            
            if not image_result.get("success"):
                # Handle vision failure safely
                user_msg = _save_user_message(db, conversation.id, text or "", image_path, input_type=input_type)
                assistant_msg = _save_assistant_message(db, conversation.id, "Image analysis failed.", None, 0.0, True)
                db.commit()
                return _build_result(
                    assistant_msg, conversation.id, None, "fallback",
                    {
                        "summary": "I could not evaluate this image right now. Please upload a clearer document image or describe your question in text.",
                        "eligibility": [], "documents": [], "next_steps": [], "where_to_go": [],
                        "warning": "Do not upload images showing Aadhaar numbers, OTPs, passwords, bank details, or other sensitive information in full view."
                    },
                    [], 0.0, "low", "", image_description, None, image_analysis_data, False, "image_analysis_failed"
                )
                
            query_text = f"{query_text} [Image: {image_description}]".strip()
        except Exception as e:
            image_description = f"Could not process image: {e}"
            user_msg = _save_user_message(db, conversation.id, text or "", image_path, input_type=input_type)
            assistant_msg = _save_assistant_message(db, conversation.id, "Image analysis failed.", None, 0.0, True)
            db.commit()
            return _build_result(
                assistant_msg, conversation.id, None, "fallback",
                {
                    "summary": "I could not evaluate this image right now. Please upload a clearer document image or describe your question in text.",
                    "eligibility": [], "documents": [], "next_steps": [], "where_to_go": [],
                    "warning": "Do not upload images showing Aadhaar numbers, OTPs, passwords, bank details, or other sensitive information in full view."
                },
                [], 0.0, "low", "", image_description, None, None, False, "image_analysis_failed"
            )"""
            
content = content.replace(old_img_block, new_img_block)

# Also update the final return _build_result inside process_query
# It currently has: return _build_result(assistant_msg, ..., None, privacy_warning)
# Let's use regex to replace all `return _build_result(` inside process_query to pass image_analysis_data if missing.
# Well, wait, Python allows kwargs. I can just append `, image_analysis=image_analysis_data` to the final `return _build_result(...)`.

final_return = """    return _build_result(
        assistant_msg, conversation.id, detected_service,
        "answer" if is_grounded else "fallback",
        answer_data, formatted_citations,
        confidence_score, confidence_level,
        verification_msg, image_description, None
    )"""
new_final_return = """    return _build_result(
        assistant_msg, conversation.id, detected_service,
        "answer" if is_grounded else "fallback",
        answer_data, formatted_citations,
        confidence_score, confidence_level,
        verification_msg, image_description, None, image_analysis_data
    )"""
content = content.replace(final_return, new_final_return)

with open('../akshaya-backend/app/services/agentic_controller.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated process_query to handle image_analysis.")
