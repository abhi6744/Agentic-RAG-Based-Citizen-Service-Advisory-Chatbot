import requests

url = "http://127.0.0.1:8000/chat"
payload = {
    "text": "What documents do I need for a new ration card in Kerala?",
    "conversation_id": "test-session-123",
    "device_id": "test-device-123"
}
try:
    response = requests.post(url, json=payload)
    print("Response Code:", response.status_code)
    print("Response JSON:")
    print(response.json())
except Exception as e:
    print("Request failed:", e)
