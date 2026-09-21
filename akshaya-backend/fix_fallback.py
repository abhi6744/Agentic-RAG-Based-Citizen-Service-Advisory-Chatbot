import re
from pathlib import Path

f = Path('app/services/agentic_controller.py')
text = f.read_text(encoding='utf-8')

old_err = '''    except Exception as e:
        print(f"LLM API Error: {e}")
        assistant_msg = _save_assistant_message(
            db, conversation.id, "The AI service is currently experiencing high demand and is unavailable. Please try again later.",
            detected_service=intent.primary_service,
            confidence_score=max_score,
            requires_verification=True,
        )
        db.commit()
        confidence = compute_confidence(similarity_scores, 1.0)
        return _build_result(
            assistant_msg, conversation.id, intent.primary_service, "fallback",
            "The AI service is currently experiencing high demand and is unavailable. Please try again later.", None, None, [], confidence.confidence_score,
            confidence.confidence_level, confidence.verification_message,
            image_description, None,
        )'''

new_err = '''    except Exception as e:
        print(f"LLM API Error: {e}")
        assistant_msg = _save_assistant_message(
            db, conversation.id, "The AI service is currently experiencing high demand and is unavailable. Please try again later.",
            detected_service=intent.primary_service,
            confidence_score=max_score,
            requires_verification=True,
        )
        _save_sources(db, assistant_msg.id, chunks)
        _save_audit_log(db, assistant_msg.id, chunks, False)
        db.commit()
        
        # Build citations for fallback so user still gets sources
        seen_sources = set()
        citations = []
        for c in chunks:
            if c.source_title not in seen_sources:
                seen_sources.add(c.source_title)
                citations.append({
                    "source_title": c.source_title,
                    "source_url": c.source_url or "",
                    "authority": c.authority,
                    "retrieved_date": c.retrieved_date,
                })
                
        confidence = compute_confidence(similarity_scores, 1.0)
        return _build_result(
            assistant_msg, conversation.id, intent.primary_service, "fallback",
            "The AI service is currently experiencing high demand and is unavailable. Please try again later.", None, None, citations, confidence.confidence_score,
            confidence.confidence_level, confidence.verification_message,
            image_description, None,
        )'''

text = text.replace(old_err, new_err)
f.write_text(text, encoding='utf-8')
