import re
from pathlib import Path

f = Path('app/main.py')
text = f.read_text(encoding='utf-8')

old_cors = '''# CORS  -  allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)'''

new_cors = '''# CORS  -  Explicit allowed origins needed because allow_credentials=True
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081", "http://127.0.0.1:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)'''

text = text.replace(old_cors, new_cors)
f.write_text(text, encoding='utf-8')
