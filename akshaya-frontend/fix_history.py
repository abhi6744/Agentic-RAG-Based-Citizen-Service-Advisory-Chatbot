import sys

with open('src/app/history.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('{ label: "Ration Card", value: "documents" },', '{ label: "Ration Card", value: "ration_card" },')
content = content.replace('{ label: "Scholarship", value: "documents" },', '{ label: "Scholarship", value: "scholarship" },')
content = content.replace('{ label: "Aadhaar", value: "aadhaar_update" },', '{ label: "Aadhaar", value: "aadhaar" },')

content = content.replace('| "aadhaar_update"', '| "aadhaar"')
content = content.replace('| "identity_mismatch"', '| "ration_card"')
content = content.replace('| "passport_support"', '| "scholarship"')
content = content.replace('| "documents";', '| "general";')

with open('src/app/history.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
