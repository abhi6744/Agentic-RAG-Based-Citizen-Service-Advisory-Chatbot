from dataclasses import dataclass
import re

@dataclass
class ValidationResult:
    """Result of citation validation."""
    is_valid: bool
    unsupported_claims: list[str]
    coverage_ratio: float  # fraction of response sentences supported by context

FALLBACK_RESPONSE = (
    "I don't have sufficient verified information from official sources to answer "
    "this question confidently. Please verify your requirements directly with your "
    "nearest Akshaya Centre or the relevant official government portal:\n\n"
    "• Aadhaar: https://uidai.gov.in\n"
    "• Ration Card: https://civilsupplieskerala.gov.in\n"
    "• Scholarship: https://scholarships.gov.in\n\n"
    "Government rules, documents, and eligibility criteria can change  -  always "
    "confirm with the official source before proceeding."
)

def _extract_factual_sentences(text: str) -> list[str]:
    """Extract sentences that make factual claims (not meta-commentary or disclaimers)."""
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    factual = []
    
    # Skip sentences that are meta-commentary, greetings, or disclaimers
    skip_patterns = [
        r'^(please|kindly|note that|remember|disclaimer|important)',
        r'(verify|confirm|check with|visit).*(akshaya|official|portal|centre)',
        r'^(hello|hi|sure|certainly|of course|based on)',
        r'(may change|subject to change|can change|rules? (may|can|might))',
        r'^(here|below|following|the above)',
        r'^(I |As |This |These |According)',
        r'(retrieved context|source \d)',
    ]
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence or len(sentence) < 15:
            continue
        
        is_meta = any(
            re.search(pat, sentence, re.IGNORECASE)
            for pat in skip_patterns
        )
        
        if not is_meta:
            factual.append(sentence)
    
    return factual

def _is_claim_supported(claim: str, context_texts: list[str]) -> bool:
    """Check if a factual claim is supported by at least one context chunk."""
    claim_lower = claim.lower()
    
    # Extract key terms from the claim (nouns, numbers, specific names)
    # Simple approach: check if significant words from the claim appear in context
    claim_words = set(re.findall(r'\b\w{4,}\b', claim_lower))  # words with 4+ chars
    claim_numbers = set(re.findall(r'\b\d+[,.]?\d*\b', claim_lower))  # numbers
    
    if not claim_words:
        return True  # Very short/generic claim, let it pass
    
    for context in context_texts:
        context_lower = context.lower()
        
        # Check numbers strict match
        if claim_numbers:
            context_numbers = set(re.findall(r'\b\d+[,.]?\d*\b', context_lower))
            if not claim_numbers.issubset(context_numbers):
                continue # Numbers must match exactly for the claim to be supported by this context
        
        # Check word overlap
        context_words = set(re.findall(r'\b\w{4,}\b', context_lower))
        overlap = claim_words & context_words
        overlap_ratio = len(overlap) / len(claim_words) if claim_words else 0
        
        # If enough key words match, consider it supported
        if overlap_ratio >= 0.5:
            return True
            
    return False

def validate_response(
    llm_response: str,
    retrieved_chunks: list[dict],
) -> ValidationResult:
    """Validate that LLM response is grounded in retrieved context."""
    context_texts = [chunk["text"] for chunk in retrieved_chunks]
    
    # If no context was provided, any factual claim is unsupported
    if not context_texts:
        return ValidationResult(
            is_valid=False,
            unsupported_claims=["No context available to validate against"],
            coverage_ratio=0.0,
        )
    
    factual_sentences = _extract_factual_sentences(llm_response)
    
    if not factual_sentences:
        # Response is all meta-commentary  -  that's fine for out-of-scope or fallback
        return ValidationResult(
            is_valid=True,
            unsupported_claims=[],
            coverage_ratio=1.0,
        )
    
    unsupported = []
    supported_count = 0
    
    for sentence in factual_sentences:
        if _is_claim_supported(sentence, context_texts):
            supported_count += 1
        else:
            unsupported.append(sentence)
    
    total = len(factual_sentences)
    coverage = supported_count / total if total > 0 else 1.0
    
    # Response is valid if coverage is above threshold
    is_valid = coverage >= 0.3 and len(unsupported) <= 5
    
    return ValidationResult(
        is_valid=is_valid,
        unsupported_claims=unsupported,
        coverage_ratio=coverage,
    )
