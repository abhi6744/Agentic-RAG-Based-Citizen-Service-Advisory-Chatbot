import sys

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Alert import
if "import { Alert" not in content and " Alert," not in content and ", Alert " not in content:
    content = content.replace('import {', 'import { Alert,', 1)

# Fix MessageBubble destructuring
content = content.replace("const { colors, isDark } = useTheme();", "const { colors } = useTheme();")
content = content.replace("const { colors, isDark } = useTheme()", "const { colors } = useTheme()")

# Fix colors properties
content = content.replace("colors.userBubble", "colors.primary")
content = content.replace("colors.botBubble", "colors.surface")
content = content.replace("colors.textOnUserBubble", '"#ffffff"')

# Fix isDark usages
content = content.replace("borderWidth: isDark ? 0 : 1", "borderWidth: 1")
content = content.replace("shadowOpacity: isDark ? 0.3 : 0.05", "shadowOpacity: 0.05")

# Also, there's another isDark in the main component maybe?
content = content.replace("isDark", "false") # Blanket replace any remaining `isDark` variable usages to false if they exist, but safely.

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed theme colors and TS errors.")
