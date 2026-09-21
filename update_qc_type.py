import re

with open('akshaya-frontend/src/components/QueryComposer.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace type
old_type = """export type SelectedImage = {
  uri: string;
  mimeType: string;
  fileName: string;
  width: number;
  height: number;
};"""

new_type = """export type ChatImage = {
  uri: string;
  mimeType: string;
  fileName: string;
  width?: number;
  height?: number;
  webFile?: File;
};"""
content = content.replace(old_type, new_type)

# Rename SelectedImage -> ChatImage globally in file
content = content.replace('SelectedImage', 'ChatImage')

with open('akshaya-frontend/src/components/QueryComposer.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated QueryComposer.tsx types")
