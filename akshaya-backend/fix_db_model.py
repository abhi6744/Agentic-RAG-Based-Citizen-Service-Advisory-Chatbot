import re
from pathlib import Path

f = Path('app/models/db_models.py')
text = f.read_text(encoding='utf-8')

old_log = '''class QueryAuditLog(Base):
    __tablename__ = "query_audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    retrieved_chunk_ids = Column(Text)  # JSON array of chunk IDs
    similarity_scores = Column(Text)  # JSON array of floats
    hallucination_check_passed = Column(Boolean)
    created_at = Column(DateTime, server_default=func.now())'''

new_log = '''class QueryAuditLog(Base):
    __tablename__ = "query_audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    retrieved_chunk_ids = Column(Text)  # JSON array of chunk IDs
    similarity_scores = Column(Text)  # JSON array of floats
    hallucination_check_passed = Column(Boolean, nullable=True)
    model_provider = Column(String, default="unknown", nullable=True)
    created_at = Column(DateTime, server_default=func.now())'''

text = text.replace(old_log, new_log)
f.write_text(text, encoding='utf-8')
