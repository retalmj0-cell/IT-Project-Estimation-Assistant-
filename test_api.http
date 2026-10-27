import json
import urllib.request

url = "http://127.0.0.1:8000/api/chat/"
data = {
    "message": "احسب لي مدة المشروع باستخدام طريقة PERT",
    "agent": "pert_agent",
    "parameters": {
        "optimistic": 2.0,
        "most_likely": 5.0,
        "pessimistic": 14.0
    }
}

req = urllib.request.Request(
    url,
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST'
)

print("Sending request to Django API...")
try:
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.status}")
        result_body = response.read().decode('utf-8')
        print("Response Result:")
        print(json.dumps(json.loads(result_body), indent=2, ensure_ascii=False))
except Exception as e:
    print("Error:", e)