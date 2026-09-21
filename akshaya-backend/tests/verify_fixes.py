import asyncio
import json
import httpx

async def run_queries():
    queries = [
        "What documents do I need for a new ration card in Kerala?",
        "i need to update my adhaar card, what all documents should i keep it with me?",
        "How do I register a new business?",
        "I have a question about my documents."
    ]
    
    url = "http://localhost:8000/chat"
    
    async with httpx.AsyncClient() as client:
        for q in queries:
            print(f"\n--- Query: {q} ---")
            try:
                resp = await client.post(url, data={"text": q, "device_id": "test_script"})
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"Response Type: {data.get('response_type')}")
                    print(f"Confidence Score: {data.get('confidence_score')}")
                    print(f"Confidence Level: {data.get('confidence_level')}")
                    print(f"Summary: {data.get('summary')}")
                else:
                    print(f"Error: {resp.status_code} - {resp.text}")
            except Exception as e:
                print(f"Request failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_queries())
