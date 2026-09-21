import requests
import json

url = "http://127.0.0.1:8000/chat"

print("--- Query 1: Text Only ---")
payload1 = {
    "text": "Am I eligible for a National Scholarship, and what documents are needed?",
    "device_id": "test-device-reg-1"
}
try:
    res1 = requests.post(url, data=payload1)
    print("Response JSON:")
    print(json.dumps(res1.json(), indent=2))
except Exception as e:
    print("Failed:", e)


print("\n--- Query 2: Image ---")
payload2 = {
    "text": "which document is this",
    "device_id": "test-device-reg-2"
}
try:
    # Use the test image created earlier
    files = {'image': open('test_image.jpg', 'rb')}
    res2 = requests.post(url, data=payload2, files=files)
    print("Response JSON:")
    print(json.dumps(res2.json(), indent=2))
except Exception as e:
    print("Failed:", e)
