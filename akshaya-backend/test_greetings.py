import requests

url = "http://127.0.0.1:8000/chat"

print("--- Testing 'hi' ---")
response = requests.post(url, data={"text": "hi", "device_id": "test-device-2"})
res_json = response.json()
print("Response Type:", res_json.get("response_type"))
print("Summary:", res_json.get("summary"))

print("\n--- Testing 'what can you do' ---")
response = requests.post(url, data={"text": "what can you do", "device_id": "test-device-2"})
res_json = response.json()
print("Response Type:", res_json.get("response_type"))
print("Summary:", res_json.get("summary"))

