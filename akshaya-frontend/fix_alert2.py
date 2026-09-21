import sys
import re

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'import { Alert,\s*API_BASE_URL } from "../config/api";', 'import { API_BASE_URL } from "../config/api";', content)
content = re.sub(r'import {\s*Alert,\s*API_BASE_URL } from "../config/api";', 'import { API_BASE_URL } from "../config/api";', content)

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
