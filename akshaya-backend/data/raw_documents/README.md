# Raw Documents

This folder holds official public source documents for Aadhaar, Kerala Ration Card, and Scholarship services.
Documents are organized into `aadhaar`, `ration_card`, and `scholarship` folders.
The `../source_manifest.csv` file provides authority, source URL, retrieval date, and category metadata.

**Rules:**
- Only official public documents must be used.
- Never place personal Aadhaar images, user-uploaded files, private data, OTPs, passwords, or bank data here.

**Ingestion:**
To extract text from these documents, run:
```bash
python -m ingestion.extract_text
```
