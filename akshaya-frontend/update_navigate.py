import re

with open('src/components/AppDrawerContent.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("router.push(path);", "router.push(path as any);")

with open('src/components/AppDrawerContent.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Cast path to any in router.push")
