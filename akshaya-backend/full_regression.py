import requests
import time

url = "http://127.0.0.1:8000/chat"

queries = [
    ("Phase 1 - Q1 (Ration Card)", "What documents do I need for a new ration card in Kerala?"),
    ("Phase 1 - Q2 (Scholarship)", "Am I eligible for a National Scholarship if my family income is 3 lakhs?"),
    ("Phase 1 - Q3 (Aadhaar)", "My name in Aadhaar is different from my certificate, what do I do?"),
    ("Phase 1 - Q4 (Out of scope)", "What is the capital of France?"),
    ("Phase 1 - Q5 (Obscure in-scope)", "Can I use my ration card to get a free helicopter ride in Kerala?"),
    ("Phase 1 - Q6 (Audit)", "What is the exact penalty fee for losing a ration card 5 times?"),
    ("Regression Check - Ration Card", "What documents do I need for a new ration card in Kerala?"),
    ("Greeting Check", "hi"),
    ("Out of Scope Check", "Can you write a python script for a web scraper?"),
]

print("Running Full Regression Set...\n")

for idx, (name, q) in enumerate(queries):
    print(f"--- {name} ---")
    print(f"Q: {q}")
    payload = {
        "text": q,
        "device_id": f"test-device-full-reg"
    }
    try:
        response = requests.post(url, data=payload)
        res_json = response.json()
        print(f"Detected Service: {res_json.get('detected_service')}")
        print(f"Response Type: {res_json.get('response_type')}")
        print(f"Summary: {res_json.get('summary')}")
        print("-" * 50 + "\n")
        time.sleep(1)
    except Exception as e:
        print("Request failed:", e)
        print("-" * 50 + "\n")
