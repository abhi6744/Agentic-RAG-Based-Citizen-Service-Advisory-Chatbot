import os
import sys
from pathlib import Path

# Ensure backend root is in sys.path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.retriever import get_retriever
from app.services.intent_classifier import classify_intent

def run_diagnostics():
    queries = [
        "What documents do I need for a new ration card in Kerala?",
        "I need to update my Aadhaar card. What documents should I keep with me?",
        "What documents are required for a scholarship application?"
    ]
    
    print("Loading RAG components...")
    retriever = get_retriever()
    retriever.load()
    
    print("\n" + "="*60)
    print("RETRIEVAL DIAGNOSTICS")
    print("="*60)
    
    for query in queries:
        print(f"\nQuery: {query}")
        
        # 1. Classify intent
        intent = classify_intent(query)
        classified_service = intent.primary_service
        
        # Normalize the service category exactly as requested by user
        if classified_service in ["aadhaar", "ration_card", "scholarship"]:
            pass
        elif "ration" in classified_service.lower():
            classified_service = "ration_card"
        elif "aadhaar" in classified_service.lower():
            classified_service = "aadhaar"
        elif "scholarship" in classified_service.lower():
            classified_service = "scholarship"
            
        print(f"Classified Service: {classified_service}")
        print(f"Rewritten Query: {query}")
        
        # 2. Retrieve
        results = retriever.retrieve(query, service_category=classified_service, top_k=5)
        
        print(f"Number of Results: {len(results)}")
        if results:
            print(f"  Similarity Scores: {[f'{r.similarity_score:.3f}' for r in results]}")
            print(f"  Chunk IDs: {[r.chunk_id for r in results]}")
            print(f"  Service Categories: {[r.service_category for r in results]}")
            print(f"  Source Titles:")
            for r in results:
                print(f"    - {r.source_title}")
        else:
            print("  [!] NO RESULTS FOUND")

if __name__ == "__main__":
    run_diagnostics()
