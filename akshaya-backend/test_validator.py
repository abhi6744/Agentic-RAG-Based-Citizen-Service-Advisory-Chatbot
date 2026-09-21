from app.services.citation_validator import validate_response, _is_claim_supported
import re

chunks = [{"text": "You need an ID proof and address proof for Aadhaar update. Accepted documents include PAN card and Voter ID."}]
context_texts = [c["text"] for c in chunks]

def test_claim(claim):
    claim_lower = claim.lower()
    claim_words = set(re.findall(r'\b\w{4,}\b', claim_lower))
    print(f"\nClaim: {claim}")
    print(f"Claim words: {claim_words}")
    
    for context in context_texts:
        context_words = set(re.findall(r'\b\w{4,}\b', context.lower()))
        overlap = claim_words & context_words
        overlap_ratio = len(overlap) / len(claim_words) if claim_words else 0
        print(f"Context words: {context_words}")
        print(f"Overlap: {overlap}")
        print(f"Ratio: {overlap_ratio:.2f}")

test_claim("To update your Aadhaar, you must provide an ID proof and address proof, such as a Voter ID or PAN card.")
test_claim("To update your Aadhaar, you must pay 500 rupees and provide a DNA sample.")
