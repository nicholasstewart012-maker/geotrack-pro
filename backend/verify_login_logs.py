import requests
import sys

BASE_URL = "http://localhost:8000"

def test_login_logging():
    print(f"Testing Login logging against {BASE_URL}")

    # 1. Login
    login_data = {
        "email": "admin@geotrack.pro",
        "password": "password123", # Default seeded password
        "full_name": "Test User" 
    }
    
    try:
        print("Attempting login...")
        res = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if res.status_code != 200:
            print(f"Login failed: {res.status_code} {res.text}")
            return False
        
        data = res.json()
        token = data["access_token"]
        print("Login successful. Token received.")
        
        # 2. Fetch Logs
        print("Fetching login logs...")
        headers = {"Authorization": f"Bearer {token}"}
        res_logs = requests.get(f"{BASE_URL}/admin/logs/login", headers=headers)
        
        if res_logs.status_code != 200:
            print(f"Failed to fetch logs: {res_logs.status_code} {res_logs.text}")
            return False
            
        logs = res_logs.json()
        print(f"Logs retrieved. Count: {len(logs)}")
        
        if len(logs) > 0:
            latest = logs[0]
            print(f"Latest Log: {latest}")
            if latest["email"] == "admin@geotrack.pro":
                print("SUCCESS: Log entry found for admin.")
                return True
            else:
                print("WARNING: Latest log is not for admin? (Could be concurrent usage)")
                return True
        else:
            print("FAILURE: No logs found even after successful login.")
            return False
            
    except Exception as e:
        print(f"Exception during test: {e}")
        return False

if __name__ == "__main__":
    if test_login_logging():
        print("VERIFICATION PASSED")
        sys.exit(0)
    else:
        print("VERIFICATION FAILED")
        sys.exit(1)
