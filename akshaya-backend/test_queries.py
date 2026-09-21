import json
from fastapi.testclient import TestClient
from app.main import app

def run_tests():
    print("Initializing TestClient (this will trigger lifespan and load models)...")
    with TestClient(app) as client:
        print("Server is up. Running verification queries...\n")
        
        queries = [
            ("1. Ration Card", "What documents do I need for a new ration card in Kerala?"),
            ("2. Scholarship", "Am I eligible for a National Scholarship if my family income is 3 lakhs?"),
            ("3. Aadhaar", "My name in Aadhaar is different from my certificate, what do I do?"),
            ("4. Out of scope", "What is the capital of France?"),
            ("5. Obscure in-scope", "Can I use my ration card to get a free helicopter ride in Kerala?"),
        ]
        
        for name, q in queries:
            print(f"=== {name} ===")
            print(f"Q: {q}")
            response = client.post("/chat", data={"text": q, "device_id": "test_script"})
            if response.status_code == 200:
                data = response.json()
                print(f"Service: {data.get('detected_service')}")
                print(f"Confidence: {data.get('confidence_level')} ({data.get('confidence_score')})")
                print(f"Summary: {data.get('summary')}")
                print(f"Sources: {[c['source_title'] for c in data.get('citations', [])]}")
            else:
                print(f"Error: {response.status_code} - {response.text}")
            print()

        # 6. Confirm query_audit_log table populated correctly
        print("=== 6. Audit Log Check ===")
        # We can query the database directly or just check if it worked
        from app.db.database import SessionLocal
        from app.models.db_models import QueryAuditLog
        
        db = SessionLocal()
        logs = db.query(QueryAuditLog).all()
        print(f"Total audit logs found: {len(logs)}")
        if len(logs) > 0:
            print(f"Last log hallucination check passed: {logs[-1].hallucination_check_passed}")
            print(f"Last log chunk IDs: {logs[-1].retrieved_chunk_ids}")
        db.close()

if __name__ == "__main__":
    run_tests()
