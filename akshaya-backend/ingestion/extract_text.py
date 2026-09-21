import fitz  # PyMuPDF
import json
import csv
import os
import re
import urllib.parse
from pathlib import Path

BACKEND_ROOT = Path(__file__).parent.parent
RAW_DOCS_DIR = BACKEND_ROOT / "data" / "raw_documents"
OUTPUT_DIR = BACKEND_ROOT / "data" / "processed"
MANIFEST_PATH = BACKEND_ROOT / "data" / "source_manifest.csv"

def load_manifest() -> list[dict]:
    if not MANIFEST_PATH.exists():
        return []
    entries = []
    with open(MANIFEST_PATH, "r", encoding="utf-8", errors="replace") as f:
        lines = [line.strip().strip('"') for line in f if line.strip()]
        reader = csv.DictReader(lines)
        for row in reader:
            entries.append(dict(row))
    return entries

def normalize_filename(filename: str) -> str:
    name = str(filename).replace('\\', '/').split('/')[-1]
    name = urllib.parse.unquote(name)
    name = name.lower().strip()
    name = name.replace(' ', '_')
    name = name.replace('.pdf.pdf', '.pdf')
    return name

def clean_text(text: str) -> str:
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\bPage\s+\d+\s+of\s+\d+\b', '', text, flags=re.IGNORECASE)
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    return text.strip()

def extract_text_from_pdf(pdf_path: Path) -> list[dict]:
    pages = []
    try:
        doc = fitz.open(str(pdf_path))
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            cleaned = clean_text(text)
            if cleaned:
                pages.append({
                    "page_num": page_num + 1,
                    "text": cleaned
                })
        doc.close()
    except Exception as e:
        print(f"  ERROR extracting from {pdf_path}: {e}")
        return []
    return pages

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()
    
    manifest_lookup = {}
    for entry in manifest:
        norm_name = normalize_filename(entry.get("file_path", ""))
        manifest_lookup[norm_name] = entry

    results = []
    pdf_files = list(RAW_DOCS_DIR.glob("**/*.pdf"))
    
    print(f"Found {len(pdf_files)} PDF files in {RAW_DOCS_DIR}")
    
    for pdf_path in pdf_files:
        norm_pdf_name = normalize_filename(pdf_path.name)
        folder_category = pdf_path.parent.name
        
        print(f"\nProcessing: {pdf_path.name}")
        
        entry = manifest_lookup.get(norm_pdf_name)
        
        if entry:
            title = entry.get("title", pdf_path.name)
            service_category = entry.get("service_category", folder_category)
            authority = entry.get("authority", "")
            source_url = entry.get("source_url", "")
            retrieved_date = entry.get("retrieved_date", "")
            print("  [✓] Matched in manifest")
        else:
            title = pdf_path.name
            service_category = folder_category
            authority = "MISSING_METADATA"
            source_url = "MISSING_METADATA"
            retrieved_date = "MISSING_METADATA"
            print("  [!] NOT matched in manifest. Using defaults.")
            
        print(f"  Category: {service_category}")
        
        pages = extract_text_from_pdf(pdf_path)
        status = "success" if pages else "no_text_extracted"
        print(f"  Extracted {len(pages)} pages, status: {status}")
        
        results.append({
            "file_path": str(pdf_path.relative_to(BACKEND_ROOT)).replace('\\', '/'),
            "title": title,
            "service_category": service_category,
            "authority": authority,
            "source_url": source_url,
            "retrieved_date": retrieved_date,
            "pages": pages,
            "total_pages": len(pages),
            "extraction_status": status
        })
    
    output_path = OUTPUT_DIR / "extracted_texts.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    for r in results:
        print(f"  {r['service_category']:15s} | {r['total_pages']:3d} pages | {r['extraction_status']:20s} | {r['title'][:50]}")
    print(f"\nTotal documents: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r['extraction_status'] == 'success')}")

if __name__ == "__main__":
    main()
