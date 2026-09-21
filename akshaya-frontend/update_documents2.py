import re

with open('src/app/documents.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("The application can provide", "Supported document types")
content = content.replace("Possible service identification", "JPG, PNG, and WEBP images")
content = content.replace("Eligibility information when supported", "Maximum file size: 5MB")
content = content.replace("Document checklist guidance from official sources", "Aadhaar update forms and letters")
content = content.replace("Step-by-step advisory recommendations", "Kerala Ration card applications")
content = content.replace("Citations, confidence status, and verification warnings", "Scholarship portal forms")
content = content.replace("English text-to-speech for the final response", "General identity proofs (Voter ID, PAN)")

content = content.replace("This application is advisory only. It does not approve\n            applications, submit applications automatically, perform biometric\n            verification, access private Aadhaar data, verify document\n            authenticity, confirm official identity, or replace Akshaya\n            operators and government departments.", "The vision capability is designed to identify the type of document to provide better context for your questions. It DOES NOT verify the authenticity of the document, process applications, or permanently store your uploads.")

with open('src/app/documents.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated documents.tsx capabilities section")
