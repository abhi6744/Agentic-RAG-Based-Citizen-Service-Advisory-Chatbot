import re

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

bad_check = """          if (!(file instanceof File) && !(file instanceof Blob)) {
            throw new Error("Invalid file object created");
          }"""
good_check = """          if (!file) {
            throw new Error("Invalid file object created");
          }"""

content = content.replace(bad_check, good_check)

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed instanceof check")
