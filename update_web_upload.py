import re

with open('akshaya-frontend/src/app/index.tsx', 'r', encoding='utf-8') as f:
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
    content = content.replace("export default function ChatScreen() {", helper + "\nexport default function ChatScreen() {")

old_web_upload = """        if (Platform.OS === 'web') {
          const res = await fetch(image.uri);
          const blob = await res.blob();
          const file = new File([blob], image.fileName, { type: image.mimeType });
          formData.append("image", file);
        }"""
new_web_upload = """        if (Platform.OS === 'web') {
          const file = await uriToWebFile(image.uri, image.fileName, image.mimeType);
          if (!(file instanceof File) && !(file instanceof Blob)) {
            throw new Error("Invalid file object created");
          }
          if (file.size === 0) {
            throw new Error("The uploaded file is empty.");
          }
          const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
          if (!allowedTypes.includes(file.type)) {
            throw new Error("Please upload a JPG, PNG, or WEBP document image.");
          }
          formData.append("image", file);
        }"""
content = content.replace(old_web_upload, new_web_upload)

with open('akshaya-frontend/src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated web upload logic in index.tsx")
