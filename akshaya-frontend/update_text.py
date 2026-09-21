import re

# UPDATE ACCOUNT.TSX
with open('src/app/account.tsx', 'r', encoding='utf-8') as f:
    account_content = f.read()

account_content = account_content.replace(
    'Do not enter Aadhaar numbers, OTPs, biometric details, document images, passwords, or bank information in chat.',
    'Do not enter full Aadhaar numbers, OTPs, passwords, bank information, or upload images showing sensitive biometric details in full view.'
)

with open('src/app/account.tsx', 'w', encoding='utf-8') as f:
    f.write(account_content)


# UPDATE ABOUT.TSX
with open('src/app/about.tsx', 'r', encoding='utf-8') as f:
    about_content = f.read()

about_content = about_content.replace(
    'Prototype status: the mobile frontend is complete in structure. The next stage connects FastAPI, curated official documents, RAG retrieval, citation verification, confidence scoring, and English text-to-speech.',
    'Prototype status: The application is fully integrated with the FastAPI backend, utilizing agentic RAG to provide verified answers backed by official sources. Vision capabilities evaluate documents safely.'
)

with open('src/app/about.tsx', 'w', encoding='utf-8') as f:
    f.write(about_content)

print("Updated text in account.tsx and about.tsx")
