"""Agentic RAG controller  -  orchestrates the full pipeline.

Flow:
1. Receive user input (text, optional image, conversation_id)
2. Privacy filter  -  scan for sensitive data
3. Image description via Gemini vision (if image present)
4. Intent classification (aadhaar | ration_card | scholarship | unsupported)
5. FAISS retrieval filtered by service category
6. Agentic decision: low confidence → rewrite + retry; still low → fallback
7. LLM generation with strict system prompt + retrieved context
8. Citation validation (hallucination guardrail)
9. Confidence scoring
10. Audit logging to SQLite
11. Return structured JSON response
"""

import json
import logging
import os
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.db_models import (
    Conversation,
    Message,
    MessageSource,
    QueryAuditLog,
    User,
)
from app.services.citation_validator import FALLBACK_RESPONSE, validate_response
from app.services.confidence_scorer import compute_confidence
from app.services.intent_classifier import classify_intent
from app.services.llm_client import get_llm_client
from app.services.privacy_filter import check_privacy
from app.services.retriever import RetrievedChunk, get_retriever

settings = get_settings()
logger = logging.getLogger(__name__)

OUT_OF_SCOPE_RESPONSE = (
    "This question is outside the scope of Akshaya Advisory. "
    "I can currently help with exactly 3 services:\n\n"
    "1. **Aadhaar Services**  -  enrolment, updates, document requirements\n"
    "2. **Ration Card Services**  -  Kerala ration card eligibility, documents, categories\n"
    "3. **Scholarship Services**  -  National Scholarship Portal eligibility and documents\n\n"
    "Please ask a question related to one of these services, or visit your nearest "
    "Akshaya Centre for assistance with other government services."
)

PRIVACY_RESPONSE = (
    "⚠️ **Privacy Alert**: Your message appears to contain sensitive personal "
    "information. For your safety, I cannot process messages containing "
    "Aadhaar numbers, OTPs, passwords, bank account details, or other "
    "sensitive data.\n\n"
    "Please rephrase your question without including any personal "
    "identification numbers or credentials. If you need identity "
    "verification, please visit your nearest Akshaya Centre in person."
)


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def _get_or_create_user(db: Session, device_id: str) -> User:
    user = db.query(User).filter(User.device_id == device_id).first()
    if not user:
        user = User(device_id=device_id)
        db.add(user)
        db.flush()
    return user


def _get_or_create_conversation(
    db: Session,
    conversation_id: int | None,
    user_id: int,
    title: str | None = None,
) -> Conversation:
    if conversation_id:
        conv = (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )
        if conv:
            return conv

    conv = Conversation(user_id=user_id, title=title or "New conversation")
    db.add(conv)
    db.flush()
    return conv


def _save_user_message(
    db: Session,
    conversation_id: int,
    text: str,
    image_path: str | None = None,
    input_type: str = "text",
) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        role="user",
        text_content=text,
        input_type=input_type,
        image_path=image_path,
    )
    db.add(msg)
    db.flush()
    return msg


def _save_assistant_message(
    db: Session,
    conversation_id: int,
    text: str,
    detected_service: str | None,
    confidence_score: float,
    requires_verification: bool,
) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        role="assistant",
        text_content=text,
        detected_service=detected_service,
        confidence_score=confidence_score,
        requires_verification=requires_verification,
    )
    db.add(msg)
    db.flush()
    return msg


def _save_sources(
    db: Session, message_id: int, chunks: list[RetrievedChunk]
) -> None:
    from datetime import date
    seen: set[str] = set()
    for chunk in chunks:
        if chunk.source_title in seen:
            continue
        seen.add(chunk.source_title)
        
        ret_date = None
        if chunk.retrieved_date:
            try:
                parts = str(chunk.retrieved_date).split("-")
                if len(parts) >= 3:
                    # just construct from datetime instead of date since date isn't imported
                    ret_date = datetime(int(parts[0]), int(parts[1]), int(parts[2])).date()
            except Exception:
                pass
                
        source = MessageSource(
            message_id=message_id,
            source_title=chunk.source_title,
            source_url=chunk.source_url,
            authority=chunk.authority,
            retrieved_date=ret_date,
        )
        db.add(source)


def _save_audit_log(
    db: Session,
    message_id: int,
    chunks: list[RetrievedChunk],
    hallucination_check_passed: bool | None,
    model_provider: str = "grok",
) -> None:
    chunk_ids = [c.chunk_id for c in chunks]
    scores = [round(c.similarity_score, 4) for c in chunks]

    log = QueryAuditLog(
        message_id=message_id,
        retrieved_chunk_ids=json.dumps(chunk_ids),
        similarity_scores=json.dumps(scores),
        hallucination_check_passed=hallucination_check_passed,
        model_provider=model_provider,
    )
    db.add(log)


# ---------------------------------------------------------------------------
# Query rewriting (agentic retry logic)
# ---------------------------------------------------------------------------

def _rewrite_query(query: str, service: str) -> str:
    """Expand abbreviations and add service-name context."""
    service_names = {
        "aadhaar": "Aadhaar card UIDAI",
        "ration_card": "ration card Kerala civil supplies",
        "scholarship": "National Scholarship Portal NSP",
    }
    expansions = {
        "docs": "documents",
        "req": "required",
        "elig": "eligibility eligible",
        "DOB": "date of birth",
        "POI": "proof of identity",
        "POA": "proof of address",
        "POR": "proof of relationship",
        "BPL": "below poverty line",
        "APL": "above poverty line",
        "AAY": "Antyodaya Anna Yojana",
        "NSP": "National Scholarship Portal",
    }

    rewritten = query
    for abbr, expansion in expansions.items():
        if abbr.lower() in query.lower():
            rewritten += f" {expansion}"
    rewritten += f" {service_names.get(service, '')}"
    return rewritten.strip()


# ---------------------------------------------------------------------------
# Response section parser
# ---------------------------------------------------------------------------

import re

import json
import logging

def _parse_response_sections(
    response: str,
) -> dict:
    """Parse the JSON structured LLM response."""
    try:
        # Sometimes models wrap json in markdown blocks
        clean_resp = response.strip()
        if clean_resp.startswith("```json"):
            clean_resp = clean_resp[7:]
        if clean_resp.startswith("```"):
            clean_resp = clean_resp[3:]
        if clean_resp.endswith("```"):
            clean_resp = clean_resp[:-3]
            
        data = json.loads(clean_resp.strip())
        
        return {
            "summary": data.get("summary", ""),
            "eligibility": data.get("eligibility", []),
            "documents": data.get("documents", []),
            "next_steps": data.get("next_steps", []),
            "where_to_go": data.get("where_to_go", []),
            "warning": data.get("warning", "Please verify current requirements with your nearest Akshaya Centre or the official government portal.")
        }
    except Exception as e:
        logger.error(f"Failed to parse LLM JSON response: {e}\nResponse was: {response}")
        return {
            "summary": response.strip(),
            "eligibility": [],
            "documents": [],
            "next_steps": [],
            "where_to_go": [],
            "warning": "Please verify current requirements with your nearest Akshaya Centre or the official government portal."
        }


# ---------------------------------------------------------------------------
# Build a quick result dict
# ---------------------------------------------------------------------------

def _build_result(
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
) -> dict:
    return {
        "success": True,
        "status": "grounded_answer" if response_type == "answer" else response_type,
        "message_id": assistant_msg.id,
        "conversation_id": conversation_id,
        "response_type": response_type,
        "detected_service": detected_service,
        "answer": answer_data,
        "citations": citations or [],
        "confidence_score": confidence_score,
        "confidence_level": confidence_level,
        "requires_official_verification": True,
        "verification_message": verification_message,
        "image_description": image_description,
        "privacy_warning": privacy_warning,
        "created_at": assistant_msg.created_at or datetime.now(timezone.utc),
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def process_query(
    db: Session,
    text: str | None = None,
    image_path: str | None = None,
    conversation_id: int | None = None,
    device_id: str = "default",
    input_type: str = "text",
) -> dict:
    """Run the full agentic RAG pipeline and return a structured result dict."""
    retriever = get_retriever()
    llm = get_llm_client()

    query_text = text or ""
    image_description: str | None = None

    # -- user & conversation --------------------------------------------------
    user = _get_or_create_user(db, device_id)
    conversation = _get_or_create_conversation(
        db, conversation_id, user.id
    )

    # -- Step 1: image description ---------------------------------------------
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
            )

    # -- Step 2: privacy filter ------------------------------------------------
    if query_text:
        privacy_result = check_privacy(query_text)
        if privacy_result.contains_sensitive_data:
            user_msg = _save_user_message(
                db, conversation.id, privacy_result.sanitized_text, image_path, input_type=input_type
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
                {"summary": PRIVACY_RESPONSE, "eligibility": [], "documents": [], "next_steps": [], "where_to_go": [], "warning": "Please do not share sensitive information."}, [], 0.0, "low",
                "Please do not share sensitive information.",
                None, privacy_result.warning_message,
            )

    # save user message
    _save_user_message(db, conversation.id, text or "", image_path, input_type=input_type)

    # -- Step 3: intent classification -----------------------------------------
    intent = classify_intent(query_text)

    # Handle general conversations (Greetings, Thanks)
    if intent.primary_service == "general":
        query_lower = query_text.lower()
        if any(w in query_lower for w in ["thank", "ok", "got it", "understood"]):
            response_text = "You’re welcome! Let me know if you have another question."
        elif "help" in query_lower:
            response_text = "I currently provide guidance for Aadhaar services, Kerala ration cards, and scholarship applications. I can help explain documents, eligibility, application steps, and what to do next."
        else:
            response_text = "Hello! I’m Akshaya Advisory. I can help with Aadhaar services, Kerala ration card services, and scholarship guidance. What would you like to know?"
            
        assistant_msg = _save_assistant_message(
            db, conversation.id, response_text,
            detected_service="general_conversation", confidence_score=0.0,
            requires_verification=False,
        )
        db.commit()
        return _build_result(
            assistant_msg, conversation.id, None, "general",
            {"summary": response_text, "eligibility": [], "documents": [], "next_steps": [], "where_to_go": [], "warning": ""}, [], 0.0, "low",
            "", None, None
        )

    # Handle explicitly unsupported
    if intent.primary_service == "unsupported":
        response_text = "That is outside my current support scope. I currently help with Aadhaar services, Kerala ration cards, and scholarship guidance."
        assistant_msg = _save_assistant_message(
            db, conversation.id, response_text,
            detected_service="unsupported", confidence_score=0.0,
            requires_verification=False,
        )
        _save_audit_log(db, assistant_msg.id, [], True)
        db.commit()
        return _build_result(
            assistant_msg, conversation.id, "unsupported", "out_of_scope",
            {"summary": response_text, "eligibility": [], "documents": [], "next_steps": [], "where_to_go": [], "warning": ""}, [], 0.0, "low",
            "", image_description, None,
        )

    # Contextual Follow-up Logic
    last_detected_service = None
    if conversation_id:
        prev_msg = db.query(Message).filter(
            Message.conversation_id == conversation.id, 
            Message.role == "assistant",
            Message.detected_service.notin_(["unsupported", "general_conversation", "unknown", "None", ""])
        ).order_by(Message.created_at.desc()).first()
        if prev_msg and prev_msg.detected_service:
            last_detected_service = prev_msg.detected_service

    if intent.primary_service == "unknown":
        if last_detected_service:
            # Rewrite query with previous context
            intent.primary_service = last_detected_service
            query_text = f"For the user's {last_detected_service} issue, {query_text}"
        else:
            # Need clarification
            response_text = "I can help with that. Are you asking about Aadhaar services, a Kerala ration card, or scholarship guidance?"
            assistant_msg = _save_assistant_message(
                db, conversation.id, response_text,
                detected_service="clarification", confidence_score=0.0,
                requires_verification=False,
            )
            db.commit()
            return _build_result(
                assistant_msg, conversation.id, None, "clarification",
                {"summary": response_text, "eligibility": [], "documents": [], "next_steps": [], "where_to_go": [], "warning": ""}, [], 0.0, "low",
                "", None, None
            )

    # -- Step 4: retrieval -----------------------------------------------------
    if intent.is_multi_service and intent.secondary_service:
        categories = [intent.primary_service, intent.secondary_service]
        chunks = retriever.retrieve_multi_service(query_text, categories)
    else:
        chunks = retriever.retrieve(
            query_text, service_category=intent.primary_service
        )

    similarity_scores = [c.similarity_score for c in chunks]
    max_score = max(similarity_scores) if similarity_scores else 0.0

    # -- Step 5: agentic retry -------------------------------------------------
    # IMPORTANT: The FAISS index uses IndexFlatIP (cosine similarity for normalized vectors).
    # Therefore, higher scores mean better matches. The comparison max_score < threshold is correct.
    if max_score < settings.low_confidence_threshold:
        rewritten = _rewrite_query(query_text, intent.primary_service)
        if intent.is_multi_service and intent.secondary_service:
            retry_chunks = retriever.retrieve_multi_service(
                rewritten,
                [intent.primary_service, intent.secondary_service],
            )
        else:
            retry_chunks = retriever.retrieve(
                rewritten, service_category=intent.primary_service
            )
        retry_scores = [c.similarity_score for c in retry_chunks]
        retry_max = max(retry_scores) if retry_scores else 0.0

        if retry_max > max_score:
            chunks = retry_chunks
            similarity_scores = retry_scores
            max_score = retry_max

        # IMPORTANT: The FAISS index uses IndexFlatIP (cosine similarity for normalized vectors).
    # Therefore, higher scores mean better matches. The comparison max_score < threshold is correct.
    if max_score < settings.low_confidence_threshold:
            # Still too low  -  return safe fallback
            assistant_msg = _save_assistant_message(
                db, conversation.id, FALLBACK_RESPONSE,
                detected_service=intent.primary_service,
                confidence_score=max_score,
                requires_verification=True,
            )
            _save_audit_log(db, assistant_msg.id, chunks, True)
            db.commit()
            confidence = compute_confidence(similarity_scores)
            return _build_result(
                assistant_msg, conversation.id, intent.primary_service, "fallback",
                {"summary": FALLBACK_RESPONSE, "eligibility": [], "documents": [], "next_steps": [], "where_to_go": [], "warning": confidence.verification_message}, [], confidence.confidence_score,
                confidence.confidence_level, confidence.verification_message,
                image_description, None,
            )

    # -- Step 6: LLM generation ------------------------------------------------
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
        
        # Extract meaningful error snippet
        api_msg = "The assistant encountered an API error."
        if "403" in str(llm_result.error) or "PermissionDenied" in str(llm_result.error):
            api_msg = "API Error (403): Your API key does not have enough credits or is invalid. Please top up your account."
        elif "429" in str(llm_result.error):
            api_msg = "API Error (429): Rate limit exceeded. The model is busy right now."
        elif "AuthenticationError" in str(llm_result.error) or "401" in str(llm_result.error):
            api_msg = "API Error (401): Authentication Error! The API key you provided is invalid, deleted, or unauthorized."
        elif "BadRequestError" in str(llm_result.error) or "Incorrect API key" in str(llm_result.error):
            api_msg = "API Error (400): The API key you provided in the .env file is incorrect or invalid."
        else:
            api_msg = f"Grok API Error: {str(llm_result.error).splitlines()[0][:100]}"
            
        assistant_msg = _save_assistant_message(
            db, conversation.id, api_msg,
            detected_service=intent.primary_service,
            confidence_score=None,
            requires_verification=True,
        )
        _save_audit_log(db, assistant_msg.id, chunks, None, llm_result.model_provider)
        db.commit()
        
        return _build_result(
            assistant_msg, conversation.id, intent.primary_service, "service_unavailable",
            {"summary": api_msg, "eligibility": [], "documents": [], "next_steps": [], "where_to_go": [], "warning": ""}, [], None,
            None, "", image_description, None,
        )

    llm_response = llm_result.text

    # -- Step 7: citation validation -------------------------------------------
    validation = validate_response(llm_response, chunk_dicts)

    if not validation.is_valid:
        llm_response = FALLBACK_RESPONSE
        hallucination_passed = False
    else:
        hallucination_passed = True

    # -- Step 8: confidence scoring --------------------------------------------
    confidence = compute_confidence(
        similarity_scores, validation.coverage_ratio
    )

    # -- Step 9: parse structured sections -------------------------------------
    answer_data = _parse_response_sections(llm_response)

    # -- Step 10: save to database ---------------------------------------------
    assistant_msg = _save_assistant_message(
        db, conversation.id, llm_response,
        detected_service=intent.primary_service,
        confidence_score=confidence.confidence_score,
        requires_verification=True,
    )
    _save_sources(db, assistant_msg.id, chunks)
    _save_audit_log(db, assistant_msg.id, chunks, hallucination_passed, llm_result.model_provider)
    db.commit()

    # Build citations
    seen_sources: set[str] = set()
    citations: list[dict] = []
    for c in chunks:
        if c.source_title not in seen_sources:
            seen_sources.add(c.source_title)
            citations.append({
                "source_title": c.source_title,
                "source_url": c.source_url or "",
                "authority": c.authority,
                "retrieved_date": c.retrieved_date,
            })

    return _build_result(
        assistant_msg, conversation.id, intent.primary_service, "answer" if hallucination_passed else "fallback",
        answer_data, citations,
        confidence.confidence_score, confidence.confidence_level,
        confidence.verification_message, image_description, None,
    )
