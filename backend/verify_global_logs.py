import requests
import sys

BASE_URL = "http://localhost:8000"

def test_global_logs():
    print(f"Testing Global Logs Endpoint against {BASE_URL}")

    try:
        # Fetch Global Logs
        print("Fetching global logs...")
        res = requests.get(f"{BASE_URL}/analytics/logs")
        
        if res.status_code != 200:
            print(f"Failed to fetch logs: {res.status_code} {res.text}")
            return False
            
        logs = res.json()
        print(f"Logs retrieved. Count: {len(logs)}")
        
        if len(logs) > 0:
            first_log = logs[0]
            print(f"Sample Log: {first_log}")
            
            # Verify vehicle name is present
            if "vehicle_name" not in first_log:
                print("FAILURE: 'vehicle_name' missing from log object.")
                return False
                
            print(f"Vehicle Name: {first_log['vehicle_name']}")
        
        print("SUCCESS: Global Logs endpoint works.")
        return True
            
    except Exception as e:
        print(f"Exception during test: {e}")
        return False

if __name__ == "__main__":
    if test_global_logs():
        print("VERIFICATION PASSED")
        sys.exit(0)
    else:
        print("VERIFICATION FAILED")
        sys.exit(1)
