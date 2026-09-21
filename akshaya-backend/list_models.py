import os
from app.config import get_settings
from google import genai

settings = get_settings()

try:
    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.list_models()
    for m in response:
        print(m.name)
except Exception as e:
    print("Gemini Error:", e)
