#!/usr/bin/env python3
import requests
import json

def test_api():
    url = "http://localhost:8000/analyze"
    data = {
        "customer_id": "CUST123",
        "message": "My server is down and I cannot access my application. This is urgent as it affects our production environment."
    }
    
    try:
        print("🚀 Testing Enterprise Agent API...")
        print(f"📤 Sending request to: {url}")
        print(f"📝 Data: {json.dumps(data, indent=2)}")
        print("-" * 50)
        
        response = requests.post(url, json=data, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Response:")
            print(json.dumps(result, indent=2))
        else:
            print("❌ Error Response:")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_error_endpoint():
    url = "http://localhost:8000/test-error"
    try:
        print("\n🚀 Testing /test-error endpoint...")
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        assert response.status_code == 500, "Expected 500 error for /test-error endpoint"
        print("✅ /test-error endpoint returned 500 as expected.")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_api()
    test_error_endpoint() 