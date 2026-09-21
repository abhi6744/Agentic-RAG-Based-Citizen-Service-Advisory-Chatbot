import requests
import time

url = "http://127.0.0.1:8000/chat"

queries = [
    ("What documents do I need for a new ration card in Kerala?", "ration_card"),
    ("Am I eligible for a National Scholarship if my family income is 3 lakhs?", "scholarship"),
    ("My name in Aadhaar is different from my certificate, what do I do?", "aadhaar"),
    ("What is the capital of France?", "unsupported"),
    ("What is the exact penalty fee for losing a ration card 5 times?", "fallback"),
]

for idx, (q, expected) in enumerate(queries):
    print(f"\n--- Query {idx+1}: {q} ---")
    payload = {
        "text": q,
        "device_id": f"test-device-verify"
    }
    try:
        response = requests.post(url, data=payload)
        res_json = response.json()
        print(f"Detected Service: {res_json.get('detected_service')}")
        print(f"Response Type: {res_json.get('response_type')}")
        print(f"Summary: {res_json.get('summary')}")
        
        conf = res_json.get("confidence_score")
        if conf is not None:
            if res_json.get("response_type") == "answer":
                print(f"Confidence: {conf:.2f} ({res_json.get('confidence_level')})")
            elif res_json.get("response_type") == "fallback":
                print(f"Confidence: {conf:.2f} (Fallback triggered)")
        else:
            print("Confidence: None")
        
        if res_json.get("response_type") == expected or (expected == "fallback" and conf is not None and conf < 0.4):
             print("STATUS: PASS")
        else:
             print(f"STATUS: CHECK EXPECTED {expected}")
             
        time.sleep(1)
    except Exception as e:
        print("Request failed:", e)
