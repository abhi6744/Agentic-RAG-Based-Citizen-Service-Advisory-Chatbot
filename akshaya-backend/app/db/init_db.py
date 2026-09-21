import csv
import json
from datetime import date
from pathlib import Path

from app.config import get_settings
from app.db.database import Base, SessionLocal, engine
from app.models.db_models import DocumentRegistry  # noqa: F401  -  register models

# Import all models so Base.metadata knows about them
from app.models import db_models as _models  # noqa: F401


def init_database():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


def populate_document_registry():
    """Populate document_registry from source_manifest.csv and ingestion report."""
    settings = get_settings()
    kb_path = Path(settings.knowledge_base_path)
    backend_path = Path(__file__).resolve().parent.parent.parent
    manifest_path = kb_path / "source_manifest.csv"
    report_path = backend_path / "data" / "processed" / "ingestion_report.json"

    if not manifest_path.exists():
        print(f"WARNING: {manifest_path} not found, skipping registry population.")
        return

    # Load ingestion report for chunk counts
    chunk_counts: dict[str, int] = {}
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)
            chunk_counts = report.get("chunks_per_service", {})

    # Parse manifest
    entries = []
    with open(manifest_path, "r", encoding="utf-8", errors="replace") as f:
        lines = [line.strip().strip('"') for line in f if line.strip()]
        reader = csv.DictReader(lines)
        entries = list(reader)

    db = SessionLocal()
    try:
        # Clear existing entries
        db.query(DocumentRegistry).delete()

        for entry in entries:
            # Clean values
            cleaned = dict(entry)

            title = cleaned.get("title", "")
            service_category = cleaned.get("service_category", "")
            retrieved_date_str = cleaned.get("retrieved_date", "")

            # Parse date
            ret_date = None
            if retrieved_date_str:
                try:
                    parts = retrieved_date_str.split("-")
                    ret_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
                except (ValueError, IndexError):
                    pass

            doc = DocumentRegistry(
                title=title,
                service_category=service_category,
                authority=cleaned.get("authority", ""),
                source_url=cleaned.get("source_url", ""),
                file_path=cleaned.get("file_path", ""),
                retrieved_date=ret_date,
                last_verified_date=ret_date,
                chunk_count=chunk_counts.get(service_category, 0),
            )
            db.add(doc)

        db.commit()
        print(f"Document registry populated with {len(entries)} entries.")
    except Exception as e:
        db.rollback()
        print(f"ERROR populating document registry: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
    populate_document_registry()
