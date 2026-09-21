import re

with open('src/app/documents.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Change component name
content = content.replace("export default function MvpInfoScreen()", "export default function DocumentsScreen()")

# Change header text
content = content.replace("ENGLISH MVP SCOPE", "DOCUMENT PREPARATION")
content = content.replace("What can Akshaya Advisory help with?", "How to prepare your documents")
content = content.replace("Select a service area to begin an advisory conversation.", "Guidelines for submitting document images and gathering physical copies for your Akshaya visit.")

# Replace workflow steps with Document guidelines
old_workflow = """const workflowSteps = [
  {
    number: "01",
    icon: "chatbubble-ellipses-outline" as const,
    title: "Ask your question",
    text: "Type an English question about a selected citizen-service situation.",
  },
  {
    number: "02",
    icon: "search-outline" as const,
    title: "Find official evidence",
    text: "The backend will retrieve relevant information from curated official sources.",
  },
  {
    number: "03",
    icon: "shield-checkmark-outline" as const,
    title: "Review the guidance",
    text: "The answer will show supporting sources, confidence, and verification warnings.",
  },
];"""

new_workflow = """const workflowSteps = [
  {
    number: "01",
    icon: "camera-outline" as const,
    title: "Capture clear images",
    text: "When uploading a document for analysis, ensure good lighting and clear text. Blurry images will be rejected.",
  },
  {
    number: "02",
    icon: "eye-off-outline" as const,
    title: "Hide sensitive numbers",
    text: "Physically cover full Aadhaar numbers, passwords, and CVVs before capturing the image to protect your privacy.",
  },
  {
    number: "03",
    icon: "folder-open-outline" as const,
    title: "Organize physical copies",
    text: "Before visiting an Akshaya center, gather all original documents and keep self-attested photocopies ready.",
  },
];"""
content = content.replace(old_workflow, new_workflow)

# Replace SERVICE_CATEGORIES usage section
# We can just remove the service grid from documents.tsx or repurpose it.
# Let's remove the service grid from documents.tsx.
service_grid_regex = r'<Text\s+style=\{\[\s*styles\.sectionTitle[\s\S]*?\{SERVICE_CATEGORIES\.map\(\(category\) => \([\s\S]*?\)\)\}\s*</View>'
content = re.sub(service_grid_regex, '', content)

with open('src/app/documents.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated documents.tsx")
