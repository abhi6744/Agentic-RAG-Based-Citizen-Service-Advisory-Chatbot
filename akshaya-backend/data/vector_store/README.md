# Vector Store

This folder holds generated FAISS artifacts such as `faiss_index.index`, `faiss_metadata.json`, and chunk backups.
It is intentionally ignored because generated vector indexes can be large and can be reliably reproduced from raw documents.

**Build Instructions:**
To rebuild the embeddings and FAISS index from the processed chunks, run:
```bash
python -m ingestion.generate_embeddings
python -m ingestion.build_faiss_index
```
