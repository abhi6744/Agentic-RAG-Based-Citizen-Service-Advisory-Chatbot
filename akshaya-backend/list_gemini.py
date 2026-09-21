import os
from app.config import get_settings
import requests

settings = get_settings()
try:
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={settings.gemini_api_key}"
    r = requests.get(url)
    models = r.json()
    print("Available models:")
    for m in models.get('models', []):
        if 'gemini' in m.get('name', '').lower():
            print(f"- {m['name']}")
except Exception as e:
    print(e)
