import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.retriever import get_retriever
from app.services.llm_client import get_llm_client
from app.services.citation_validator import validate_response

def run():
    retriever = get_retriever()
    retriever.load()
    llm = get_llm_client()
    
    query = "What documents do I need for a new ration card in Kerala?"
    chunks = retriever.retrieve(query, service_category="ration_card")
    chunk_dicts = [{"text": c.text, "source_title": c.source_title, "source_url": c.source_url, "authority": c.authority} for c in chunks]
    
    print("--- GENERATING ---")
    resp = llm.generate_response(chunk_dicts, query)
    print("--- RAW LLM RESPONSE ---")
    print(resp.encode('cp1252', errors='replace').decode('cp1252'))
    
    print("--- VALIDATING ---")
    validation = validate_response(resp, chunk_dicts)
    print(f"Valid? {validation.is_valid}")
    print(f"Coverage: {validation.coverage_ratio}")
    print(f"Unsupported Claims: {validation.unsupported_claims}")

if __name__ == "__main__":
    run()
