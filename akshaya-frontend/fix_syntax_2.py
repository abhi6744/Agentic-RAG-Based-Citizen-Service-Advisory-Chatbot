import re

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'key=\{ig-\}', r'key={`elig-${idx}`}', content)

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed syntax errors again.")
