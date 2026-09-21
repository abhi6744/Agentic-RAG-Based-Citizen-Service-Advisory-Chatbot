import fitz  # PyMuPDF
import json
import csv
import os
import re
from pathlib import Path

KNOWLEDGE_BASE = Path(r"C:\Users\abhin\OneDrive\Desktop\Special\akshaya-knowledge-base")
BACKEND_ROOT = Path(r"C:\Users\abhin\OneDrive\Desktop\Special\akshaya-backend")
OUTPUT_DIR = BACKEND_ROOT / "data" / "processed"

def load_manifest() -> list[dict]:
    """Load source_manifest.csv from knowledge base."""
    manifest_path = KNOWLEDGE_BASE / "source_manifest.csv"
    entries = []
    with open(manifest_path, "r", encoding="utf-8", errors="replace") as f:
        # The CSV has quoted rows - strip the outer quotes before reading
        lines = [line.strip().strip('"') for line in f if line.strip()]
        reader = csv.DictReader(lines)
        for row in reader:
            entries.append(dict(row))
    return entries

def find_pdf_file(manifest_file_path: str) -> Path | None:
    """Find the actual PDF file, handling .pdf.pdf double extension."""
    # Try exact path first
    exact = KNOWLEDGE_BASE / manifest_file_path
    if exact.exists():
        return exact
    # Try with .pdf.pdf
    double_ext = KNOWLEDGE_BASE / (manifest_file_path + ".pdf")
    if double_ext.exists():
        return double_ext
    # Try replacing .pdf with .pdf.pdf
    if manifest_file_path.endswith(".pdf"):
        double = KNOWLEDGE_BASE / (manifest_file_path[:-4] + ".pdf.pdf")
        if double.exists():
            return double
    return None

def clean_text(text: str) -> str:
    """Clean extracted text: normalize whitespace, remove noise."""
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Normalize whitespace within lines
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove page number patterns like "Page 1 of 10" or standalone numbers
    text = re.sub(r'\bPage\s+\d+\s+of\s+\d+\b', '', text, flags=re.IGNORECASE)
    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    # Remove empty lines at start/end
    text = text.strip()
    return text

def extract_text_from_pdf(pdf_path: Path) -> list[dict]:
    """Extract text from each page of a PDF."""
    pages = []
    try:
        doc = fitz.open(str(pdf_path))
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            cleaned = clean_text(text)
            if cleaned:  # Only include pages with actual content
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
    """Main extraction pipeline."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    manifest = load_manifest()
    print(f"Loaded {len(manifest)} entries from source_manifest.csv")
    
    results = []
    for entry in manifest:
        file_path = entry.get("file_path", "")
        title = entry.get("title", "")
        service_category = entry.get("service_category", "")
        
        print(f"\nProcessing: {title}")
        print(f"  Category: {service_category}")
        print(f"  Manifest path: {file_path}")
        
        pdf_path = find_pdf_file(file_path)
        if pdf_path is None:
            print(f"  WARNING: File not found!")
            results.append({
                "file_path": file_path,
                "title": title,
                "service_category": service_category,
                "authority": entry.get("authority", ""),
                "source_url": entry.get("source_url", ""),
                "retrieved_date": entry.get("retrieved_date", ""),
                "pages": [],
                "total_pages": 0,
                "extraction_status": "file_not_found"
            })
            continue
        
        print(f"  Found at: {pdf_path}")
        pages = extract_text_from_pdf(pdf_path)
        
        status = "success" if pages else "no_text_extracted"
        print(f"  Extracted {len(pages)} pages, status: {status}")
        
        results.append({
            "file_path": file_path,
            "title": title,
            "service_category": service_category,
            "authority": entry.get("authority", ""),
            "source_url": entry.get("source_url", ""),
            "retrieved_date": entry.get("retrieved_date", ""),
            "pages": pages,
            "total_pages": len(pages),
            "extraction_status": status
        })
    
    # Save results
    output_path = OUTPUT_DIR / "extracted_texts.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    for r in results:
        print(f"  {r['service_category']:15s} | {r['total_pages']:3d} pages | {r['extraction_status']:20s} | {r['title'][:50]}")
    print(f"\nTotal documents: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r['extraction_status'] == 'success')}")
    print(f"Output saved to: {output_path}")

if __name__ == "__main__":
    main()
