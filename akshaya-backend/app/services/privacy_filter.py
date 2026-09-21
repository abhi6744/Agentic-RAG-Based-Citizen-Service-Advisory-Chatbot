import re
from dataclasses import dataclass

@dataclass
class PrivacyCheckResult:
    """Result of privacy scanning."""
    contains_sensitive_data: bool
    warning_message: str | None
    sanitized_text: str
    detected_types: list[str]

# Aadhaar: 12 digits, possibly with spaces/dashes (e.g., 1234 5678 9012)
AADHAAR_PATTERN = re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b')
# OTP: 4-6 digit codes often preceded by "OTP" or "code"
OTP_PATTERN = re.compile(r'(?:OTP|otp|code|Code)[\s:]*\d{4,6}\b')
# Bank account numbers: 9-18 digits
BANK_ACCOUNT_PATTERN = re.compile(r'\b(?:account|a/c|ac)[\s]*(?:no|number|num)?[.:\s]*\d{9,18}\b', re.IGNORECASE)
# IFSC code
IFSC_PATTERN = re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b')
# Password mentions
PASSWORD_PATTERN = re.compile(r'(?:password|passwd|pwd)[\s:]*\S+', re.IGNORECASE)
# PAN number
PAN_PATTERN = re.compile(r'\b[A-Z]{5}\d{4}[A-Z]\b')
# Phone number (Indian 10-digit)
PHONE_PATTERN = re.compile(r'\b(?:\+91[\s-]?)?[6-9]\d{9}\b')

PATTERNS = [
    ("aadhaar_number", AADHAAR_PATTERN, "XXXX-XXXX-XXXX"),
    ("otp", OTP_PATTERN, "[OTP REDACTED]"),
    ("bank_account", BANK_ACCOUNT_PATTERN, "[ACCOUNT REDACTED]"),
    ("ifsc_code", IFSC_PATTERN, "[IFSC REDACTED]"),
    ("password", PASSWORD_PATTERN, "[PASSWORD REDACTED]"),
    ("pan_number", PAN_PATTERN, "[PAN REDACTED]"),
    ("phone_number", PHONE_PATTERN, "[PHONE REDACTED]"),
]

WARNING_MESSAGE = (
    "⚠️ Privacy Alert: Your message appears to contain sensitive personal information "
    "(such as an Aadhaar number, OTP, bank details, or password). For your safety, "
    "this information has been redacted and will NOT be sent to the AI system. "
    "Please never share sensitive personal data in this chat. "
    "If you need to verify your identity, please visit your nearest Akshaya Centre in person."
)

def check_privacy(text: str) -> PrivacyCheckResult:
    """Scan text for sensitive data patterns."""
    detected_types = []
    sanitized = text
    
    for data_type, pattern, replacement in PATTERNS:
        matches = pattern.findall(sanitized)
        if matches:
            detected_types.append(data_type)
            sanitized = pattern.sub(replacement, sanitized)
    
    contains_sensitive = len(detected_types) > 0
    
    return PrivacyCheckResult(
        contains_sensitive_data=contains_sensitive,
        warning_message=WARNING_MESSAGE if contains_sensitive else None,
        sanitized_text=sanitized,
        detected_types=detected_types,
    )
