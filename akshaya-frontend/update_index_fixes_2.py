import re

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix speech reading - more aggressive regex
content = re.sub(r'\(answer\?\.documents\?\.join\("\. "\) \|\| data\.documents_and_eligibility \|\| ""\)', r'(answer?.documents?.join(". ") || "")', content)
content = re.sub(r'\(answer\?\.next_steps\?\.join\("\. "\) \|\| data\.next_steps \|\| ""\)', r'(answer?.next_steps?.join(". ") || "")', content)

# Fix welcome message - find exact string
content = re.sub(r'summary: "Welcome to Akshaya Advisory\.",', r'answer: { summary: "Welcome to Akshaya Advisory.", eligibility: [], documents: [], next_steps: [], where_to_go: [], warning: "" },', content)

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Aggressive fixes applied.")
