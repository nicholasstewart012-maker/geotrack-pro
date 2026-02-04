import requests
import sys
import json

BASE_URL = "http://localhost:8000"

def get_detail():
    try:
        res = requests.get(f"{BASE_URL}/analytics/health")
        print(f"Status: {res.status_code}")
        try:
            print(json.dumps(res.json(), indent=2))
        except:
            print(res.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_detail()
