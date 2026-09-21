import json
import numpy as np
import faiss
from dataclasses import dataclass
from pathlib import Path
from sentence_transformers import SentenceTransformer
from app.config import get_settings

settings = get_settings()

@dataclass
class RetrievedChunk:
    """A retrieved chunk with metadata and similarity score."""
    chunk_id: str
    text: str
    service_category: str
    source_title: str
    source_url: str
    authority: str
    retrieved_date: str
    page_num: int
    similarity_score: float

class VectorRetriever:
    """FAISS-based vector retriever with service category filtering."""
    
    def __init__(self):
        self._index: faiss.Index | None = None
        self._metadata: dict | None = None
        self._model: SentenceTransformer | None = None
        self._loaded = False
    
    def load(self):
        """Load FAISS index, metadata, and embedding model."""
        if self._loaded:
            return
        
        index_path = settings.faiss_index_path
        metadata_path = settings.faiss_metadata_path
        
        if not Path(index_path).exists():
            raise RuntimeError(f"RAG index unavailable: {index_path} is missing. Run the ingestion pipeline before starting chat.")
            
        print(f"Loading FAISS index from {index_path}...")
        try:
            self._index = faiss.read_index(index_path)
        except Exception as e:
            raise RuntimeError(f"RAG index unavailable: failed to load {index_path}. Error: {e}")
            
        if self._index.ntotal == 0:
            raise RuntimeError(f"RAG index unavailable: {index_path} contains 0 vectors. Run the ingestion pipeline before starting chat.")
            
        print(f"  Index loaded: {self._index.ntotal} vectors")
        
        if not Path(metadata_path).exists():
            raise RuntimeError(f"RAG index unavailable: metadata {metadata_path} is missing.")
            
        print(f"Loading metadata from {metadata_path}...")
        with open(metadata_path, "r", encoding="utf-8") as md_file:
            self._metadata = json.load(md_file)
            
        if len(self._metadata) != self._index.ntotal:
            raise RuntimeError(f"RAG index unavailable: metadata count ({len(self._metadata)}) does not match FAISS index vectors ({self._index.ntotal}).")
            
        # Validate each vector ID maps to a valid chunk with required fields
        required_fields = ['service_category', 'text', 'source_title', 'source_url', 'authority']
        for i in range(self._index.ntotal):
            meta = self._metadata.get(str(i))
            if not meta:
                raise RuntimeError(f"RAG index unavailable: metadata missing for vector ID {i}.")
            for field in required_fields:
                if field not in meta or meta[field] is None:
                    raise RuntimeError(f"RAG index unavailable: chunk {i} missing required field '{field}'.")
                    
        print(f"  Metadata loaded and validated: {len(self._metadata)} entries")
        
        print(f"Loading embedding model: {settings.embedding_model}...")
        self._model = SentenceTransformer(settings.embedding_model)
        print("  Model loaded.")
        
        # Check dimensions
        expected_dim = self._model.get_sentence_embedding_dimension()
        if self._index.d != expected_dim:
            raise RuntimeError(f"RAG index unavailable: index dimension ({self._index.d}) does not match model dimension ({expected_dim}).")
            
        self._loaded = True
    
    def retrieve(
        self,
        query: str,
        service_category: str | None = None,
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        """Retrieve top-k chunks for a query, optionally filtered by service category."""
        if not self._loaded:
            self.load()
        
        k = top_k or settings.top_k_results
        
        # Encode query
        query_embedding = self._model.encode(
            [query], normalize_embeddings=True
        ).astype('float32')
        
        # Search more than needed if filtering by category
        search_k = k * 4 if service_category else k
        search_k = min(search_k, self._index.ntotal)
        
        # FAISS search
        scores, indices = self._index.search(query_embedding, search_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS sentinel for no result
                continue
            
            meta = self._metadata.get(str(idx))
            if meta is None:
                continue
            
            # Filter by service category if specified
            if service_category and meta["service_category"] != service_category:
                continue
            
            results.append(RetrievedChunk(
                chunk_id=meta["chunk_id"],
                text=meta["text"],
                service_category=meta["service_category"],
                source_title=meta["source_title"],
                source_url=meta.get("source_url", ""),
                authority=meta["authority"],
                retrieved_date=meta.get("retrieved_date", ""),
                page_num=meta.get("page_num", 0),
                similarity_score=float(score),
            ))
            
            if len(results) >= k:
                break
        
        return results
    
    def retrieve_multi_service(
        self,
        query: str,
        service_categories: list[str],
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        """Retrieve from multiple service categories and merge results."""
        k = top_k or settings.top_k_results
        all_results = []
        
        for category in service_categories:
            results = self.retrieve(query, service_category=category, top_k=k)
            all_results.extend(results)
        
        # Sort all by similarity score descending and take top-k
        all_results.sort(key=lambda x: x.similarity_score, reverse=True)
        return all_results[:k]


# Global singleton
_retriever: VectorRetriever | None = None

def get_retriever() -> VectorRetriever:
    global _retriever
    if _retriever is None:
        _retriever = VectorRetriever()
    return _retriever
