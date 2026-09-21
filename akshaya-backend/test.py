import urllib.request
import urllib.parse
import json

data = urllib.parse.urlencode({'device_id': 'test', 'input_type': 'text', 'text': 'What documents do I need for a new ration card in Kerala?'}).encode('utf-8')
req = urllib.request.Request('http://127.0.0.1:8001/chat', data=data)
try:
    with urllib.request.urlopen(req) as f:
        print(f.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(e.read().decode('utf-8'))
