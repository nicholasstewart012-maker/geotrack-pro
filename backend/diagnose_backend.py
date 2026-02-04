import requests
import sys

BASE_URL = "http://localhost:8000"

def diagnose():
    print(f"Diagnosing Backend at {BASE_URL}")
    
    # 1. Test Root/Health (if exists) or a simple endpoint
    # We don't have a root endpoint, let's try /analytics/health as it is read-only
    try:
        print(" [1] Probing /analytics/health...")
        res = requests.get(f"{BASE_URL}/analytics/health")
        print(f"     Status: {res.status_code}")
        print(f"     Content: {res.text[:500]}") # First 500 chars
    except Exception as e:
        print(f"     Connection failed: {e}")

    # 2. Test Auth Me (Requires Token? No, if we want to see 401 vs 500)
    # The user screenshot showed 500 on 'me'. If we send no token, we expect 401. 
    # If we get 500 without token, the auth middleware/dependency is broken.
    try:
        print(" [2] Probing /auth/me (No Token)...")
        res = requests.get(f"{BASE_URL}/auth/me")
        print(f"     Status: {res.status_code}")
        print(f"     Content: {res.text[:500]}")
    except Exception as e:
        print(f"     Failed: {e}")

if __name__ == "__main__":
    diagnose()
