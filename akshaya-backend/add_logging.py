import re
from pathlib import Path

f = Path('app/services/llm_client.py')
text = f.read_text(encoding='utf-8')

# Let's add logging to _call_gemini and _call_openai
old_generate = '''    def generate_response(
        self,
        retrieved_chunks: list[dict],
        user_query: str,
        image_description: str | None = None,
    ) -> LLMResult:
        """Generate a grounded response using retrieved context with multi-provider fallback."""
        prompt = _build_prompt(retrieved_chunks, user_query, image_description)
        
        # 1. Try Primary Provider (Gemini) with retry backoff
        try:
            text = self._call_gemini(prompt)
            return LLMResult(text=text, success=True, error=None, model_provider="gemini")
        except Exception as e_primary:
            primary_error = f"Gemini Error: {e_primary}"
            
            # 2. Try Fallback Provider (OpenAI) once
            if self._openai_client:
                try:
                    text = self._call_openai(prompt)
                    return LLMResult(text=text, success=True, error=None, model_provider="openai")
                except Exception as e_fallback:
                    return LLMResult(
                        text="", 
                        success=False, 
                        error=f"{primary_error} | OpenAI Error: {e_fallback}", 
                        model_provider="both_failed"
                    )
            
            # If no fallback configured
            return LLMResult(
                text="", 
                success=False, 
                error=primary_error, 
                model_provider="gemini_failed"
            )'''

new_generate = '''    def generate_response(
        self,
        retrieved_chunks: list[dict],
        user_query: str,
        image_description: str | None = None,
    ) -> LLMResult:
        """Generate a grounded response using retrieved context with multi-provider fallback."""
        prompt = _build_prompt(retrieved_chunks, user_query, image_description)
        import logging
        logger = logging.getLogger("LLMClient")
        if not logger.handlers:
            logging.basicConfig(level=logging.INFO)
            
        logger.info(f"Attempting to generate response using Gemini (Primary)")
        
        # 1. Try Primary Provider (Gemini) with retry backoff
        try:
            text = self._call_gemini(prompt)
            logger.info("Gemini generation successful.")
            return LLMResult(text=text, success=True, error=None, model_provider="gemini")
        except Exception as e_primary:
            primary_error = f"Gemini Error: {e_primary}"
            logger.warning(f"Gemini generation failed: {primary_error}")
            
            # 2. Try Fallback Provider (OpenAI) once
            if self._openai_client:
                logger.info("Attempting to generate response using OpenAI (Fallback)")
                try:
                    text = self._call_openai(prompt)
                    logger.info("OpenAI generation successful.")
                    return LLMResult(text=text, success=True, error=None, model_provider="openai")
                except Exception as e_fallback:
                    logger.error(f"OpenAI generation failed: {e_fallback}")
                    return LLMResult(
                        text="", 
                        success=False, 
                        error=f"{primary_error} | OpenAI Error: {e_fallback}", 
                        model_provider="both_failed"
                    )
            
            # If no fallback configured
            logger.error("No OpenAI client configured. Exhausted all providers.")
            return LLMResult(
                text="", 
                success=False, 
                error=f"{primary_error} | Fallback Error: OpenAI API key missing.", 
                model_provider="gemini_failed"
            )'''

text = text.replace(old_generate, new_generate)

# Also let's intercept the tenacity retry logs so they are visible
if "import logging" not in text:
    text = "import logging\n" + text

old_retry = '''    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True
    )'''
new_retry = '''    from tenacity import before_sleep_log
    import logging
    logger = logging.getLogger("LLMClient")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True,
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )'''
text = text.replace(old_retry, new_retry)

f.write_text(text, encoding='utf-8')
