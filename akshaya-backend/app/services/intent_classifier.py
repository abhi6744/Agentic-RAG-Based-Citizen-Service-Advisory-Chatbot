from dataclasses import dataclass
import re

@dataclass
class IntentResult:
    """Result of intent classification."""
    primary_service: str  # 'aadhaar' | 'ration_card' | 'scholarship' | 'unsupported' | 'general'
    secondary_service: str | None
    confidence: float
    is_multi_service: bool
    intent_type: str = "service_information"

# Keywords and phrases associated with each service
SERVICE_KEYWORDS: dict[str, list[tuple[str, float]]] = {
    "aadhaar": [
        ("aadhaar", 3.0), ("aadhar", 3.0), ("adhar", 2.5), ("aadhar card", 3.5),
        ("uid", 2.0), ("uidai", 3.0), ("unique identification", 3.0),
        ("biometric", 2.0), ("biometric update", 2.5),
        ("enrolment", 1.5), ("enrollment", 1.5),
        ("demographic update", 2.5), ("name correction", 1.5),
        ("address update", 1.5), ("dob correction", 2.0),
        ("date of birth correction", 2.0),
        ("proof of identity", 2.0), ("poi", 1.5),
        ("proof of address", 2.0), ("poa", 1.5),
        ("proof of relationship", 2.0), ("por", 1.5),
        ("proof of date of birth", 2.0), ("podb", 1.5),
        ("identity document", 1.5), ("id proof", 1.5),
        ("address proof", 1.5),
        ("e-aadhaar", 3.0), ("maadhaar", 3.0),
        ("name change aadhaar", 3.5), ("name mismatch", 1.5),
        ("iris", 1.0), ("fingerprint", 1.5),
    ],
    "ration_card": [
        ("ration card", 3.5), ("ration", 2.5), ("rationcard", 3.0),
        ("bpl", 2.5), ("apl", 2.0), ("aay", 2.5),
        ("below poverty line", 3.0), ("above poverty line", 2.5),
        ("antyodaya", 3.0), ("antyodaya anna yojana", 3.5),
        ("civil supplies", 3.0), ("civil supply", 2.5),
        ("food security", 2.0), ("public distribution", 2.5),
        ("pds", 2.0), ("fair price shop", 2.5),
        ("kro", 2.0), ("kerala ration", 3.0),
        ("food grain", 1.5), ("rice card", 2.0),
        ("family card", 1.5), ("new ration card", 3.5),
        ("ration card eligibility", 3.5),
        ("income certificate", 1.5), ("village officer", 1.5),
        ("tahsildar", 1.5), ("taluk", 1.0),
    ],
    "scholarship": [
        ("scholarship", 3.5), ("scholarships", 3.5),
        ("nsp", 3.0), ("national scholarship", 3.5),
        ("national scholarship portal", 4.0),
        ("pre-matric", 3.0), ("post-matric", 3.0),
        ("pre matric", 2.5), ("post matric", 2.5),
        ("top class", 2.0), ("merit cum means", 3.0),
        ("minority scholarship", 3.5), ("obc scholarship", 3.0),
        ("sc scholarship", 3.0), ("st scholarship", 3.0),
        ("income limit", 1.5), ("income ceiling", 2.0),
        ("family income", 1.5), ("annual income", 1.5),
        ("tuition fee", 1.5), ("fee reimbursement", 2.0),
        ("student", 1.0), ("education", 0.8),
        ("50000", 1.0), ("50,000", 1.0),
        ("scholarship amount", 2.5), ("scholarship eligibility", 3.0),
        ("renewal", 1.0), ("fresh application", 1.5),
    ],
}

OUT_OF_SCOPE_INDICATORS = [
    "capital of", "weather", "recipe", "movie", "song", "cricket",
    "football", "stock", "bitcoin", "crypto", "joke", "poem",
    "write me", "tell me a story", "who is the president",
    "prime minister", "election", "news", "sports",
    "python code", "javascript", "programming", "cook"
]

GREETINGS = [
    "hi", "hello", "good morning", "good evening", "good afternoon",
    "hey", "what can you help with", "what can you help with?", 
    "who are you", "who are you?", "what can you do", "what can you do?", 
    "help", "what is this", "what is this?", "how are you", "how are you?",
    "how are u", "how are u?", "how r u", "how r you"
]

THANKS = [
    "thanks", "thank you", "okay", "got it", "ok", "understood", "bye"
]

def _classify_intent_type(query: str) -> str:
    """Classify the specific conversational intent."""
    query = query.lower()
    if any(k in query for k in ["eligibility", "eligible", "who can", "can i apply"]):
        return "eligibility"
    if any(k in query for k in ["document", "proof", "what to carry", "what should i carry", "certificate"]):
        return "required_documents"
    if any(k in query for k in ["apply", "application process", "how to"]):
        return "application_process"
    if any(k in query for k in ["next", "do now", "proceed"]):
        return "next_steps"
    if any(k in query for k in ["where", "location", "office", "submit", "visit", "go"]):
        return "location_or_submission"
    if any(k in query for k in ["status", "follow up"]):
        return "status_or_follow_up"
    if any(k in query for k in ["correction", "mismatch", "wrong", "change"]):
        return "correction_or_mismatch"
    return "service_information"

def classify_intent(query: str) -> IntentResult:
    """Classify user query into a service category and intent."""
    query_lower = query.lower().strip()
    
    # Normalize common typos
    typo_map = {
        r"\b(adhaar|aadhar|adhar)\b": "aadhaar",
        r"\b(ration crad|ration)\b": "ration card",
        r"\b(scholorship|scolarship)\b": "scholarship"
    }
    for pattern, repl in typo_map.items():
        query_lower = re.sub(pattern, repl, query_lower)

    # Check for general conversational intents
    if query_lower in GREETINGS or query_lower in THANKS or query_lower.strip('.,?!') in GREETINGS or query_lower.strip('.,?!') in THANKS:
        return IntentResult(
            primary_service="general",
            secondary_service=None,
            confidence=1.0,
            is_multi_service=False,
            intent_type="general_conversation"
        )
    
    # Check for obvious out-of-scope queries
    for indicator in OUT_OF_SCOPE_INDICATORS:
        if indicator in query_lower:
            return IntentResult(
                primary_service="unsupported",
                secondary_service=None,
                confidence=0.9,
                is_multi_service=False,
                intent_type="unsupported"
            )
    
    # Score each service
    scores: dict[str, float] = {}
    for service, keywords in SERVICE_KEYWORDS.items():
        score = 0.0
        for keyword, weight in keywords:
            if keyword.lower() in query_lower:
                score += weight
        scores[service] = score
    
    # Sort by score descending
    sorted_services = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    top_service, top_score = sorted_services[0]
    second_service, second_score = sorted_services[1]
    
    intent_type = _classify_intent_type(query_lower)
    
    # If no keywords matched at all, classify as unknown
    if top_score == 0:
        return IntentResult(
            primary_service="unknown",
            secondary_service=None,
            confidence=0.0,
            is_multi_service=False,
            intent_type=intent_type
        )
    
    # Check if query spans two services
    is_multi = second_score > 0 and second_score >= top_score * 0.5
    confidence = min(top_score / 5.0, 1.0)
    
    return IntentResult(
        primary_service=top_service,
        secondary_service=second_service if is_multi else None,
        confidence=confidence,
        is_multi_service=is_multi,
        intent_type=intent_type
    )
