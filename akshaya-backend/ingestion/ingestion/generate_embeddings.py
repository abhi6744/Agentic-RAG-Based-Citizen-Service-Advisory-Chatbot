import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

BACKEND_ROOT = Path(r"C:\Users\abhin\OneDrive\Desktop\Special\akshaya-backend")
PROCESSED_DIR = BACKEND_ROOT / "data" / "processed"
VECTOR_DIR = BACKEND_ROOT / "data" / "vector_store"
MODEL_NAME = "all-MiniLM-L6-v2"

def main():
    chunks_path = PROCESSED_DIR / "chunks.jsonl"
    if not chunks_path.exists():
        print(f"ERROR: {chunks_path} not found. Run chunk_documents.py first.")
        return
    
    # Load chunks
    chunks = []
    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))
    
    print(f"Loaded {len(chunks)} chunks")
    print(f"Loading embedding model: {MODEL_NAME}...")
    
    model = SentenceTransformer(MODEL_NAME)
    
    # Extract texts for embedding
    texts = [chunk["text"] for chunk in chunks]
    
    print(f"Generating embeddings for {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    
    # Save embeddings as numpy array
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)
    embeddings_path = VECTOR_DIR / "embeddings.npy"
    np.save(str(embeddings_path), embeddings)
    
    print(f"Embeddings shape: {embeddings.shape}")
    print(f"Embeddings saved to: {embeddings_path}")
    print(f"Embedding dimension: {embeddings.shape[1]}")
    
    return embeddings

if __name__ == "__main__":
    main()
