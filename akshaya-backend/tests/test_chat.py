import sys
import asyncio
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.db.database import get_db, engine
from app.models.db_models import Base
from app.services.agentic_controller import process_query
from app.services.retriever import get_retriever

Base.metadata.create_all(bind=engine)

async def run():
    get_retriever().load()
    db = next(get_db())
    query = "What documents do I need for a new ration card in Kerala?"
    print(f"Query: {query}")
    result = await process_query(db, text=query, image_path=None, conversation_id=None, device_id="test")
    print(f"Confidence Level: {result['confidence_level']}")
    print(f"Confidence Score: {result['confidence_score']}")
    print(f"Summary: {result['summary']}")
    
if __name__ == "__main__":
    asyncio.run(run())
