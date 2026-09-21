import re

with open('akshaya-frontend/src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Add import
if 'import DocumentImage' not in content:
    content = content.replace('import ChatImagePreview', 'import ChatImagePreview\nimport DocumentImage from "../components/DocumentImage";')

# Replace inline rendering
old_render = """          {message.imageUri ? (
            Platform.OS === 'web' && message.imageUri.startsWith('blob:') ? (
              <img 
                src={message.imageUri} 
                style={{ width: 200, height: 200, borderRadius: 8, marginBottom: 8, objectFit: 'cover', backgroundColor: '#E0E0E0', display: 'block' }} 
              />
            ) : (
              <Image
                source={{ uri: message.imageUri }}
                style={{ width: 200, height: 200, borderRadius: 8, marginBottom: 8, backgroundColor: '#E0E0E0' }}
                resizeMode="cover"
              />
            )
          ) : null}"""

new_render = """          {message.imageUri ? (
            <DocumentImage 
              uri={message.imageUri} 
              style={{ width: 200, height: 200, borderRadius: 8, marginBottom: 8 }} 
            />
          ) : null}"""
content = content.replace(old_render, new_render)

with open('akshaya-frontend/src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated index.tsx to use DocumentImage")
