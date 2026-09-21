import asyncio
import httpx

async def run_qa_tests():
    url = "http://localhost:8000/chat"
    
    queries = [
        # 1. Direct, well-formed
        "What documents do I need for a new ration card in Kerala?",
        "Am I eligible for a National Scholarship, and what documents are needed?",
        "My name in Aadhaar doesn't match my certificate - how do I update it?",
        
        # 2. Misspelled/informal
        "adhar card update",
        "ration crad list",
        "scholorship documents",
        
        # 3. Spans two services
        "I need my Aadhaar updated before applying for a scholarship",
        
        # 4. Out-of-scope
        "How do I register a business?",
        
        # 5. In-scope-sounding but unanswerable
        "What is the exact processing time for an Aadhaar update in days?",
        
        # 6. Very short
        "help",
        "documents?",
        
        # 7. Rambling
        "I was walking down the street yesterday and I realized that my ID was completely wrong because the spelling of my last name is totally messed up. Anyway, my question is what documents do I need to fix my Aadhaar card name?",
    ]

    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, q in enumerate(queries):
            print(f"\\n--- [{i+1}] Query: {q} ---")
            try:
                resp = await client.post(url, data={"text": q, "device_id": "qa_tester_1"})
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"Type: {data.get('response_type')}")
                    print(f"Service: {data.get('detected_service')}")
                    print(f"Conf: {data.get('confidence_score')} ({data.get('confidence_level')})")
                    print(f"Citations: {len(data.get('citations', []))}")
                    print(f"Summary: {data.get('summary')[:100]}...")
                else:
                    print(f"Error: {resp.status_code} - {resp.text}")
            except Exception as e:
                print(f"Request failed: {e}")
            await asyncio.sleep(6) # avoid 503 if possible

if __name__ == "__main__":
    asyncio.run(run_qa_tests())
