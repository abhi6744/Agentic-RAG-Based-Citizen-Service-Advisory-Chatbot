import re
from pathlib import Path

f = Path('app/routes/chat.py')
text = f.read_text(encoding='utf-8')

old_citations = '''    citations = [
        SourceCitation(
            source_title=c["source_title"],
            source_url=c.get("source_url"),
            authority=c["authority"],
            retrieved_date=c.get("retrieved_date"),
        )
        for c in result.get("citations", [])
    ]'''

new_citations = '''    citations = [
        SourceCitation(
            source_title=c["source_title"],
            source_url=c.get("source_url"),
            authority=c["authority"],
            retrieved_date=c.get("retrieved_date"),
        )
        for c in (result.get("citations") or [])
    ]'''

text = text.replace(old_citations, new_citations)
f.write_text(text, encoding='utf-8')
