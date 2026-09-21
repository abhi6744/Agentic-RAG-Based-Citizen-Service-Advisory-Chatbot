import re

with open('akshaya-frontend/src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

old_fetch_handling = """      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const rawData = await response.json();"""

new_fetch_handling = """      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        body: formData,
      });

      const rawData = await response.json();

      if (!response.ok) {
        if (rawData && rawData.message) {
          throw new Error(rawData.message);
        }
        throw new Error(`API error: ${response.status}`);
      }"""

content = content.replace(old_fetch_handling, new_fetch_handling)

with open('akshaya-frontend/src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated frontend fetch handling")
