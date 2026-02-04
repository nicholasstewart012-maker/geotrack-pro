import requests
import sys

BASE_URL = "http://localhost:8000"

def test_simple_stats():
    print(f"Testing Stats Endpoint against {BASE_URL}")

    try:
        # Fetch Stats
        print("Fetching stats...")
        res = requests.get(f"{BASE_URL}/analytics/cost")
        
        if res.status_code != 200:
            print(f"Failed to fetch stats: {res.status_code} {res.text}")
            return False
            
        stats = res.json()
        print(f"Stats retrieved: {stats}")
        
        if stats['count'] == 0:
            print("WARNING: Count is 0. Database might be empty or query failed.")
        else:
            print("SUCCESS: Count is non-zero.")
            
        return True
            
    except Exception as e:
        print(f"Exception during test: {e}")
        return False

if __name__ == "__main__":
    if test_simple_stats():
        sys.exit(0)
    else:
        sys.exit(1)
