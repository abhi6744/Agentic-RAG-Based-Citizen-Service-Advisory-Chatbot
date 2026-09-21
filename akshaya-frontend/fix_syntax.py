import sys

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("key={doc-}", "key={`doc-${idx}`}")
content = content.replace("key={ig-}", "key={`elig-${idx}`}")
content = content.replace("key={step-}", "key={`step-${idx}`}")
content = content.replace("key={loc-}", "key={`loc-${idx}`}")
content = content.replace("fetch({API_URL}/feedback", "fetch(`${API_URL}/feedback`")

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed syntax errors.")
