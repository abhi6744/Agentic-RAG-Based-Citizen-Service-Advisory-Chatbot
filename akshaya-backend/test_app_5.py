import requests
import time

url = "http://127.0.0.1:8000/chat"
payload = {
    "text": "What documents do I need for a new ration card in Kerala?",
    "conversation_id": "124",
    "device_id": "test-device-123"
}

for i in range(5):
    try:
        response = requests.post(url, data=payload)
        print(f"Run {i+1} Response JSON:")
        print(response.json())
        time.sleep(1)
    except Exception as e:
        print("Request failed:", e)
