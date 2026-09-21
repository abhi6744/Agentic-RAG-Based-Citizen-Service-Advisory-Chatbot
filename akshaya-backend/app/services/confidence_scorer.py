from dataclasses import dataclass

from app.config import get_settings

settings = get_settings()


@dataclass
class ConfidenceResult:
    """Confidence assessment for a response."""

    confidence_score: float  # 0.0 to 1.0
    confidence_level: str  # 'low', 'medium', 'high'
    requires_official_verification: bool  # Always True
    verification_message: str


VERIFICATION_MESSAGES = {
    "low": (
        "\u26a0\ufe0f Low confidence: The available official sources may not fully "
        "cover your question. Please verify all details at your nearest Akshaya "
        "Centre or the relevant official portal."
    ),
    "medium": (
        "This guidance is based on official sources but may not cover all "
        "aspects of your situation. Please verify current requirements with "
        "your nearest Akshaya Centre or the official portal, as government "
        "rules can change."
    ),
    "high": (
        "This guidance is well-supported by official sources. However, "
        "government rules and requirements can change \u2014 please verify "
        "current details at your nearest Akshaya Centre or the relevant "
        "official portal before proceeding."
    ),
}


def compute_confidence(
    similarity_scores: list[float],
    citation_coverage: float = 1.0,
) -> ConfidenceResult:
    """Compute confidence from retrieval scores and citation coverage."""
    if not similarity_scores:
        return ConfidenceResult(
            confidence_score=0.0,
            confidence_level="low",
            requires_official_verification=True,
            verification_message=VERIFICATION_MESSAGES["low"],
        )

    max_score = max(similarity_scores)
    avg_score = sum(similarity_scores) / len(similarity_scores)

    # Combined confidence: weighted average of max score, mean score, and coverage
    raw_confidence = 0.4 * max_score + 0.3 * avg_score + 0.3 * citation_coverage

    # Clamp to [0, 1]
    confidence_score = max(0.0, min(1.0, raw_confidence))

    # Determine level
    if confidence_score >= settings.high_confidence_threshold:
        level = "high"
    elif confidence_score >= settings.moderate_confidence_threshold:
        level = "medium"
    else:
        level = "low"

    return ConfidenceResult(
        confidence_score=round(confidence_score, 3),
        confidence_level=level,
        requires_official_verification=True,  # ALWAYS true
        verification_message=VERIFICATION_MESSAGES[level],
    )
