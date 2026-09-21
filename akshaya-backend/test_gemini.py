import os
from app.config import get_settings
from google import genai
import traceback

settings = get_settings()
print(f"Gemini Key starts with: {settings.gemini_api_key[:10]}...")

try:
    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Say hello!"
    )
    print("Gemini Success:", response.text)
except Exception as e:
    print("Gemini Error:")
    traceback.print_exc()
