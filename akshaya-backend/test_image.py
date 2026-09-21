import requests
from PIL import Image

# Create a dummy image
img = Image.new('RGB', (100, 100), color = 'red')
img.save('test_image.jpg')

url = "http://127.0.0.1:8000/chat"
files = {'image': open('test_image.jpg', 'rb')}
data = {'text': 'what is this document', 'device_id': 'test-1'}

print("Sending image...")
response = requests.post(url, data=data, files=files)
print(response.json())
