import re

with open('README.md', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('uvicorn app.main:app --reload --port 8000', 'uvicorn app.main:app --reload --port 8001')
content = content.replace('Gemini API (LLM)', 'Grok API (LLM)')

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated README.md")
