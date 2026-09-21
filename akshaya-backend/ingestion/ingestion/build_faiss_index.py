import json
import numpy as np
import faiss
from pathlib import Path

BACKEND_ROOT = Path(r"C:\Users\abhin\OneDrive\Desktop\Special\akshaya-backend")
PROCESSED_DIR = BACKEND_ROOT / "data" / "processed"
VECTOR_DIR = BACKEND_ROOT / "data" / "vector_store"

def main():
    """Build FAISS index from embeddings and chunk metadata."""
    embeddings_path = VECTOR_DIR / "embeddings.npy"
    chunks_path = PROCESSED_DIR / "chunks.jsonl"
    
    if not embeddings_path.exists():
        print(f"ERROR: {embeddings_path} not found. Run generate_embeddings.py first.")
        return
    if not chunks_path.exists():
        print(f"ERROR: {chunks_path} not found. Run chunk_documents.py first.")
        return
    
    # Load embeddings
    embeddings = np.load(str(embeddings_path)).astype('float32')
    print(f"Loaded embeddings: {embeddings.shape}")
    
    # Load chunks for metadata
    chunks = []
    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))
    
    assert len(chunks) == embeddings.shape[0], \
        f"Mismatch: {len(chunks)} chunks but {embeddings.shape[0]} embeddings"
    
    # Build FAISS index using IndexFlatIP (Inner Product = cosine similarity for normalized vectors)
    # We use IndexFlatIP because our embeddings are already L2-normalized by sentence-transformers
    # with normalize_embeddings=True, so inner product = cosine similarity
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    
    print(f"FAISS index built: {index.ntotal} vectors, dimension {dimension}")
    print(f"Index type: IndexFlatIP (cosine similarity via normalized inner product)")
    
    # Save FAISS index
    index_path = VECTOR_DIR / "faiss_index.index"
    faiss.write_index(index, str(index_path))
    print(f"Index saved to: {index_path}")
    
    # Build metadata mapping: vector_id -> chunk metadata
    metadata = {}
    for i, chunk in enumerate(chunks):
        metadata[str(i)] = {
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "service_category": chunk["service_category"],
            "source_title": chunk["source_title"],
            "source_url": chunk["source_url"],
            "authority": chunk["authority"],
            "retrieved_date": chunk["retrieved_date"],
            "page_num": chunk["page_num"],
            "chunk_index": chunk["chunk_index"]
        }
    
    metadata_path = VECTOR_DIR / "faiss_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"Metadata saved to: {metadata_path}")
    
    # Also keep chunks.jsonl as human-readable backup (copy to vector_store)
    import shutil
    shutil.copy2(str(chunks_path), str(VECTOR_DIR / "chunks.jsonl"))
    print(f"Chunks backup copied to: {VECTOR_DIR / 'chunks.jsonl'}")
    
    # Generate ingestion report
    service_counts = {}
    for chunk in chunks:
        cat = chunk["service_category"]
        service_counts[cat] = service_counts.get(cat, 0) + 1
    
    report = {
        "total_chunks": len(chunks),
        "chunks_per_service": service_counts,
        "embedding_dimension": dimension,
        "index_type": "IndexFlatIP",
        "embedding_model": "all-MiniLM-L6-v2",
        "documents_processed": len(set(c["source_title"] for c in chunks)),
        "failed_documents": [],
        "index_path": str(index_path),
        "metadata_path": str(metadata_path)
    }
    
    report_path = PROCESSED_DIR / "ingestion_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "="*60)
    print("INGESTION REPORT")
    print("="*60)
    print(f"  Total chunks: {report['total_chunks']}")
    for cat, count in sorted(service_counts.items()):
        print(f"  {cat:15s}: {count} chunks")
    print(f"  Documents processed: {report['documents_processed']}")
    print(f"  Embedding dimension: {dimension}")
    print(f"  Index type: IndexFlatIP (cosine similarity)")
    print(f"  Report saved to: {report_path}")

if __name__ == "__main__":
    main()
