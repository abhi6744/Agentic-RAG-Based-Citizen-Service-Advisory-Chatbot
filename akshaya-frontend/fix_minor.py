import sys
import re

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Add Alert to react-native imports if not present
if "Alert," not in content and " Alert " not in content:
    content = re.sub(r'import\s+\{([^\}]+)\}\s+from\s+[\'"]react-native[\'"]', r'import {\1, Alert} from "react-native"', content)

# Add feedbackSubmitted style
style_str = """  feedbackSubmitted: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    gap: 6,
  },"""

if "feedbackSubmitted:" not in content:
    content = content.replace("const styles = StyleSheet.create({", "const styles = StyleSheet.create({\n" + style_str)

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed Alert and styles.")
