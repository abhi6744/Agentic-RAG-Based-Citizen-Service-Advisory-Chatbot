import os
from app.config import get_settings
from openai import OpenAI

settings = get_settings()
print(f"OpenAI Key starts with: {settings.openai_api_key[:10]}...")

try:
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hello!"}],
        max_tokens=5
    )
    print("OpenAI Success:", response.choices[0].message.content)
except Exception as e:
    print("OpenAI Error:", e)
