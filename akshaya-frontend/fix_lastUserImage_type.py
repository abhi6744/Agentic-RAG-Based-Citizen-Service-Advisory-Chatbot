with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('filteredMessages[i].imageUri ? { uri: filteredMessages[i].imageUri,', 'filteredMessages[i].imageUri ? { uri: filteredMessages[i].imageUri as string,')

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
