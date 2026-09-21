import re

with open('../akshaya-backend/app/routes/chat.py', 'r', encoding='utf-8') as f:
    content = f.read()

if "image_analysis=result.get(" not in content:
    content = content.replace('image_description=result.get("image_description"),', 'image_description=result.get("image_description"),\n        image_analysis=result.get("image_analysis"),')
    
    with open('../akshaya-backend/app/routes/chat.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added image_analysis to ChatResponse mapping.")
