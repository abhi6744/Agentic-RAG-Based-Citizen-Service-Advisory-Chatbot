import re

with open('../akshaya-backend/app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_category = """        # detect category
        category = "all"
        category_label = "General"
        if latest_user_msg and latest_user_msg.detected_service:
            if "aadhaar" in latest_user_msg.detected_service.lower():
                category = "aadhaar_update"
                category_label = "Aadhaar"
            elif "ration" in latest_user_msg.detected_service.lower():
                category = "documents" # Using generic documents category or maybe we should adapt history.tsx
                category_label = "Ration Card"
            elif "scholarship" in latest_user_msg.detected_service.lower():
                category = "documents"
                category_label = "Scholarship" """

new_category = """        # detect category
        category = "general"
        category_label = "General"
        if latest_user_msg and latest_user_msg.detected_service:
            if "aadhaar" in latest_user_msg.detected_service.lower():
                category = "aadhaar"
                category_label = "Aadhaar"
            elif "ration" in latest_user_msg.detected_service.lower():
                category = "ration_card"
                category_label = "Ration Card"
            elif "scholarship" in latest_user_msg.detected_service.lower():
                category = "scholarship"
                category_label = "Scholarship" """

content = content.replace(old_category, new_category)

with open('../akshaya-backend/app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated categories in main.py")
