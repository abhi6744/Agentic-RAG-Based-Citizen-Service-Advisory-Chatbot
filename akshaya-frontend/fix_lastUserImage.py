with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('let lastUserImage = undefined;', 'let lastUserImage: SelectedImage | undefined = undefined;')
content = content.replace('lastUserImage = filteredMessages[i].imageUri;', 'lastUserImage = filteredMessages[i].imageUri ? { uri: filteredMessages[i].imageUri, mimeType: filteredMessages[i].imageMimeType || "image/jpeg", fileName: filteredMessages[i].imageFileName || "upload.jpg", width: 200, height: 200 } : undefined;')

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed lastUserImage type.")
