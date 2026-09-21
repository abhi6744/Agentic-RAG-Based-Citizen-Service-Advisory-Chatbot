import json
import re
import uuid
from pathlib import Path

BACKEND_ROOT = Path(r"C:\Users\abhin\OneDrive\Desktop\Special\akshaya-backend")
PROCESSED_DIR = BACKEND_ROOT / "data" / "processed"

# Approximate tokens as words (rough estimate: 1 token ≈ 0.75 words for English)
TARGET_CHUNK_TOKENS = 400  # target ~300-500
OVERLAP_TOKENS = 50
MIN_CHUNK_TOKENS = 50  # don't create very small chunks

def estimate_tokens(text: str) -> int:
    """Rough token estimate: count words."""
    return len(text.split())

def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences, preserving the delimiter."""
    # Split on sentence-ending punctuation followed by space or newline
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # Also split on double newlines (paragraph breaks)
    result = []
    for s in sentences:
        parts = s.split('\n\n')
        result.extend(parts)
    return [s.strip() for s in result if s.strip()]

def chunk_text(full_text: str, target_tokens: int = TARGET_CHUNK_TOKENS, 
              overlap_tokens: int = OVERLAP_TOKENS) -> list[dict]:
    """Split text into overlapping chunks at sentence boundaries."""
    sentences = split_into_sentences(full_text)
    if not sentences:
        return []
    
    chunks = []
    current_sentences = []
    current_token_count = 0
    
    for sentence in sentences:
        sentence_tokens = estimate_tokens(sentence)
        
        if current_token_count + sentence_tokens > target_tokens and current_sentences:
            # Save current chunk
            chunk_text_str = ' '.join(current_sentences)
            chunks.append({
                "text": chunk_text_str,
                "token_count": estimate_tokens(chunk_text_str)
            })
            
            # Calculate overlap: keep last N tokens worth of sentences
            overlap_sentences = []
            overlap_count = 0
            for s in reversed(current_sentences):
                s_tokens = estimate_tokens(s)
                if overlap_count + s_tokens <= overlap_tokens:
                    overlap_sentences.insert(0, s)
                    overlap_count += s_tokens
                else:
                    break
            
            current_sentences = overlap_sentences
            current_token_count = overlap_count
        
        current_sentences.append(sentence)
        current_token_count += sentence_tokens
    
    # Don't forget the last chunk
    if current_sentences:
        chunk_text_str = ' '.join(current_sentences)
        token_count = estimate_tokens(chunk_text_str)
        if token_count >= MIN_CHUNK_TOKENS or not chunks:  # Keep even small chunks if it's the only one
            chunks.append({
                "text": chunk_text_str,
                "token_count": token_count
            })
        elif chunks:
            # Merge with previous chunk if too small
            prev = chunks[-1]
            prev["text"] += ' ' + chunk_text_str
            prev["token_count"] = estimate_tokens(prev["text"])
    
    return chunks

def main():
    """Main chunking pipeline."""
    input_path = PROCESSED_DIR / "extracted_texts.json"
    output_path = PROCESSED_DIR / "chunks.jsonl"
    
    if not input_path.exists():
        print(f"ERROR: {input_path} not found. Run extract_text.py first.")
        return
    
    with open(input_path, "r", encoding="utf-8") as f:
        documents = json.load(f)
    
    print(f"Loaded {len(documents)} documents for chunking")
    
    all_chunks = []
    stats = {}  # service_category -> chunk count
    
    for doc in documents:
        if doc["extraction_status"] != "success":
            print(f"  Skipping {doc['title'][:50]} (status: {doc['extraction_status']})")
            continue
        
        service_cat = doc["service_category"]
        title = doc["title"]
        
        # Combine all pages into one text (preserving page info in chunks)
        full_text = ""
        page_breaks = []  # (char_position, page_num)
        
        for page in doc["pages"]:
            page_breaks.append((len(full_text), page["page_num"]))
            full_text += page["text"] + "\n\n"
        
        if not full_text.strip():
            continue
        
        chunks = chunk_text(full_text)
        print(f"  {title[:50]:50s} -> {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            # Determine which page this chunk starts on
            chunk_start = full_text.find(chunk["text"][:100])  # approximate
            page_num = 1
            for pos, pn in reversed(page_breaks):
                if chunk_start >= pos:
                    page_num = pn
                    break
            
            chunk_record = {
                "chunk_id": f"{service_cat}_{uuid.uuid4().hex[:8]}_{i}",
                "text": chunk["text"],
                "token_count": chunk["token_count"],
                "service_category": service_cat,
                "source_title": title,
                "source_url": doc["source_url"],
                "authority": doc["authority"],
                "retrieved_date": doc["retrieved_date"],
                "file_path": doc["file_path"],
                "page_num": page_num,
                "chunk_index": i
            }
            all_chunks.append(chunk_record)
        
        stats[service_cat] = stats.get(service_cat, 0) + len(chunks)
    
    # Save chunks
    with open(output_path, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    
    # Print summary
    print("\n" + "="*60)
    print("CHUNKING SUMMARY")
    print("="*60)
    for cat, count in sorted(stats.items()):
        print(f"  {cat:15s}: {count} chunks")
    print(f"  {'TOTAL':15s}: {len(all_chunks)} chunks")
    print(f"\nOutput saved to: {output_path}")
    
    return all_chunks

if __name__ == "__main__":
    main()
