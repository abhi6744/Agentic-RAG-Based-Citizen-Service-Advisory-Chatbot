import re
from pathlib import Path

f = Path('app/models/db_models.py')
text = f.read_text(encoding='utf-8')

old_import = '''from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Text,
)'''

new_import = '''from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Text,
    String,
)'''

text = text.replace(old_import, new_import)
f.write_text(text, encoding='utf-8')
