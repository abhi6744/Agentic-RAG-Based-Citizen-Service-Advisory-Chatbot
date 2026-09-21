import re
from pathlib import Path

f = Path('app/services/llm_client.py')
text = f.read_text(encoding='utf-8')

text = text.replace('self.gemini_model = "gemini-3.8-flash"', 'self.gemini_model = "gemini-1.5-flash"')
f.write_text(text, encoding='utf-8')
