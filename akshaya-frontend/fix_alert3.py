import sys

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("import { Alert, API_BASE_URL } from '../config/api';", "import { API_BASE_URL } from '../config/api';")

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
