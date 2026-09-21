import re

with open('src/app/history.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('{ label: "Scholarship", value: "scholarship" },', '{ label: "Scholarship", value: "scholarship" },\n  { label: "General", value: "general" },')

with open('src/app/history.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
