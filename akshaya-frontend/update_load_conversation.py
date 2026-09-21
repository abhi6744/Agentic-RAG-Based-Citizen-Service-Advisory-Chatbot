import re

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('summary: msg.text_content, // the actual message since we don\'t have all parsed parts', 'answer: { summary: msg.text_content || "", eligibility: [], documents: [], next_steps: [], where_to_go: [], warning: "" },')

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed loadConversation summary.")
