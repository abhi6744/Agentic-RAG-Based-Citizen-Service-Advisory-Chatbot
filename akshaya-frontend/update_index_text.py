import re

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# I will just replace the exact text
content = content.replace('text: data.summary || "No summary provided.",', 'text: data.answer?.summary || "I could not generate a clear summary for this response. Please review the verified sections below or try rephrasing your question.",')

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
