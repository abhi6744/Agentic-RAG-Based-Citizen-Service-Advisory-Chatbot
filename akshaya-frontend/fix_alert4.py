with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("  Animated,\n  LayoutAnimation,\n  Image,", "  Alert,\n  Animated,\n  LayoutAnimation,\n  Image,")

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
