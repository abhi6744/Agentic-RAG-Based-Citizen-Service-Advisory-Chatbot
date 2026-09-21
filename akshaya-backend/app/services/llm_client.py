import logging
import base64
import os
from dataclasses import dataclass
from typing import Optional
from openai import OpenAI
from app.config import get_settings
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger("LLMClient")
logger.setLevel(logging.INFO)

@dataclass
class LLMResult:
    text: str
    success: bool
    error: Optional[str]
    model_provider: str

class GrokClient:
    def __init__(self):
        settings = get_settings()
        
        if settings.grok_api_key and settings.grok_api_key.startswith("gsk_"):
            # User provided a Groq (groq.com) key instead of Grok (xAI)
            self.grok_model = "qwen/qwen3.8-27b"
            self.grok_vision_model = "qwen/qwen3.8-27b"
            self.client = OpenAI(
                api_key=settings.grok_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
        elif settings.grok_api_key:
            # Standard xAI Grok key
            self.grok_model = "grok-2-latest"
            self.grok_vision_model = "grok-2-vision-latest"
            self.client = OpenAI(
                api_key=settings.grok_api_key,
                base_url="https://api.x.ai/v1"
            )
        else:
            self.client = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        before_sleep=lambda retry_state: logger.warning(
            f"Retrying Grok call in {retry_state.next_action.sleep} seconds as it raised {type(retry_state.outcome.exception()).__name__}: {retry_state.outcome.exception()}."
        )
    )
    def _call_grok(self, prompt: str, json_mode: bool = False) -> str:
        if not self.client:
            raise Exception("Grok API key not configured")
        
        logger.info(f"Generating with model: {self.grok_model}")
        kwargs = {
            "model": self.grok_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
            
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    def generate_response(
        self, retrieved_chunks: list[dict], query: str, image_description: str | None = None
    ) -> LLMResult:
        try:
            logger.info("Attempting Grok generation")
            
            context_text = "\n\n".join(
                f"Source: {c['source_title']}\nContent: {c['text']}"
                for c in retrieved_chunks
            )
            
            prompt = f"""You are an Akshaya Advisory assistant.
Use the provided context to answer the query. You must follow these strict rules:

Return valid JSON only. Do not use HTML tags, Markdown bullet markers, Markdown headings, code fences, or explanatory text outside the JSON object.

Each list item must be a clean plain-text sentence. Do not return <ul>, <ol>, <li>, <strong>, <b>, <p>, <br>, or any other HTML tags.

Use the exact JSON schema below:
{{
  "summary": "Short plain-text summary.",
  "eligibility": ["Clean plain-text eligibility condition."],
  "documents": ["Clean plain-text document requirement."],
  "next_steps": ["Clean plain-text next step."],
  "where_to_go": ["Clean plain-text location or submission guidance."],
  "warning": "Please verify current requirements with your nearest Akshaya Centre or the official government portal."
}}

Keep all existing grounding rules:
1. Use only retrieved official source context.
2. Do not invent eligibility or document requirements.
3. Include the official-verification warning.
4. Use empty arrays `[]` when a field is not supported by retrieved context.

Context:
{context_text}

Query: {query}
"""
            if image_description:
                prompt += f"\nImage context provided by user: {image_description}"
                
            text = self._call_grok(prompt, json_mode=True)
            return LLMResult(
                text=text,
                success=True,
                error=None,
                model_provider="grok"
            )
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            error_msg = f"Grok Error: {str(e)}\nTraceback:\n{tb}"
            logger.error(error_msg)
            return LLMResult(
                text="",
                success=False,
                error=error_msg,
                model_provider="grok_failed"
            )

    def describe_image(self, image_path: str) -> dict:
        try:
            if not os.path.exists(image_path):
                return {"description": "Image file not found.", "document_type": "Unknown", "confidence": 0.0, "sensitive_data_hidden": False, "success": False}
                
            import mimetypes
            import json
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type:
                mime_type = "image/jpeg"
                
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
            prompt = """
            Analyze this document image carefully.
            Identify the type of this document if visually clear (e.g., Aadhaar card, Ration card, Scholarship document, etc.).
            Extract relevant non-sensitive fields to help answer the user's query.
            CRITICAL PRIVACY RULE: Do NOT repeat or output full Aadhaar numbers, OTPs, passwords, bank account numbers, or biometric information. Mask them.
            If the image is unclear or not a supported document, state that clearly.
            
            Return your response STRICTLY as a valid JSON object with the following schema:
            {
                "description": "Your detailed description with masked sensitive fields",
                "document_type": "Aadhaar document | Ration Card | Scholarship document | Unknown",
                "confidence": 0.9,
                "sensitive_data_hidden": true
            }
            """
            
            logger.info("Describing image with Grok Vision...")
            response = self.client.chat.completions.create(
                model=self.grok_vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=400,
                temperature=0.1
            )
            raw_content = response.choices[0].message.content
            parsed = json.loads(raw_content)
            parsed["success"] = True
            return parsed
        except Exception as e:
            logger.error(f"Image description failed: {e}")
            return {"description": f"[Image description failed: {e}]", "document_type": "Unknown", "confidence": 0.0, "sensitive_data_hidden": False, "success": False}

def get_llm_client() -> GrokClient:
    return GrokClient()
