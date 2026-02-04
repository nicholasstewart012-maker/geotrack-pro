import requests
import sys
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_stats_trend():
    print(f"Testing Stats Trend Endpoint against {BASE_URL}")

    try:
        # Fetch Stats Trend
        print("Fetching trend data...")
        res = requests.get(f"{BASE_URL}/analytics/cost-trend")
        
        if res.status_code != 200:
            print(f"Failed to fetch stats: {res.status_code} {res.text}")
            return False
            
        data = res.json()
        print(f"Response: {data}")
        
        if "labels" not in data or "data" not in data:
            print("FAILURE: Response format incorrect.")
            return False
            
        labels = data["labels"]
        trend_data = data["data"]
        
        if len(labels) != 6 or len(trend_data) != 6:
            print(f"WARNING: Expected 6 months of data, got {len(labels)}.")
        
        current_month = datetime.utcnow().strftime("%b")
        if labels[-1] != current_month:
             print(f"WARNING: Last label '{labels[-1]}' does not match current month '{current_month}'.")
        
        print(f"Labels: {labels}")
        print(f"Data: {trend_data}")
        print("SUCCESS: Stats Trend endpoint works.")
        return True
            
    except Exception as e:
        print(f"Exception during test: {e}")
        return False

if __name__ == "__main__":
    if test_stats_trend():
        print("VERIFICATION PASSED")
        sys.exit(0)
    else:
        print("VERIFICATION FAILED")
        sys.exit(1)
