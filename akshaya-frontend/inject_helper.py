import re

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

helper = """async function uriToWebFile(
  uri: string,
  fileName: string,
  mimeType: string,
): Promise<File> {
  const response = await fetch(uri);

  if (!response.ok) {
    throw new Error("Unable to read selected image");
  }

  const blob = await response.blob();

  if (blob.size === 0) {
    throw new Error("Selected image is empty");
  }

  return new File([blob], fileName, {
    type: mimeType || blob.type || "image/jpeg",
  });
}
"""

if "async function uriToWebFile" not in content:
    content = content.replace("export default function HomeChatScreen() {", helper + "\nexport default function HomeChatScreen() {")

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Injected uriToWebFile")
