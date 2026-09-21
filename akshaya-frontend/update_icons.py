import re

with open('src/app/history.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

new_get_icon = """function getIcon(
  category: Exclude<Category, "all">,
): keyof typeof Ionicons.glyphMap {
  if (category === "aadhaar") {
    return "card-outline";
  }

  if (category === "ration_card") {
    return "fast-food-outline";
  }

  if (category === "scholarship") {
    return "school-outline";
  }

  return "documents-outline";
}"""

content = re.sub(r'function getIcon\([\s\S]*?return "documents-outline";\n\}', new_get_icon, content)

with open('src/app/history.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated getIcon()")
