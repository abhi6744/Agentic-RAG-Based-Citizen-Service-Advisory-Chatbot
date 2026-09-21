import re

with open('akshaya-frontend/src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('SelectedImage', 'ChatImage')

with open('akshaya-frontend/src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated index.tsx imports")
