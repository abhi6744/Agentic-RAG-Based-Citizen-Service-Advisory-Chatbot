import re
from pathlib import Path

f = Path('app/services/citation_validator.py')
text = f.read_text(encoding='utf-8')

old_check = '''    for context in context_texts:
        context_lower = context.lower()
        
        # Check word overlap
        context_words = set(re.findall(r'\\b\\w{4,}\\b', context_lower))
        overlap = claim_words & context_words
        overlap_ratio = len(overlap) / len(claim_words) if claim_words else 0
        
        # If enough key words match, consider it supported
        if overlap_ratio >= 0.2:
            return True
            
    return False'''

new_check = '''    for context in context_texts:
        context_lower = context.lower()
        
        # Check numbers strict match
        if claim_numbers:
            context_numbers = set(re.findall(r'\\b\\d+[,.]?\\d*\\b', context_lower))
            if not claim_numbers.issubset(context_numbers):
                continue # Numbers must match exactly for the claim to be supported by this context
        
        # Check word overlap
        context_words = set(re.findall(r'\\b\\w{4,}\\b', context_lower))
        overlap = claim_words & context_words
        overlap_ratio = len(overlap) / len(claim_words) if claim_words else 0
        
        # If enough key words match, consider it supported
        if overlap_ratio >= 0.5:
            return True
            
    return False'''

text = text.replace(old_check, new_check)
f.write_text(text, encoding='utf-8')
