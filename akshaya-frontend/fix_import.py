import re

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

bad_import = """import ChatImagePreview
import DocumentImage from "../components/DocumentImage"; from "../components/ChatImagePreview";"""
good_import = """import DocumentImage from "../components/DocumentImage";
import ChatImagePreview from "../components/ChatImagePreview";"""

content = content.replace(bad_import, good_import)

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed import in index.tsx")
