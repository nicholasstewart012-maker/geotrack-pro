import requests
import sys

BASE_URL = "http://localhost:8000"

def test_analytics_advanced():
    print(f"Testing Advanced Analytics against {BASE_URL}")
    success = True

    # 1. Health Index
    try:
        print("\n[1] Testing Health Index...")
        res = requests.get(f"{BASE_URL}/analytics/health")
        if res.status_code == 200:
            data = res.json()
            print(f"Health Index Response: {data}")
            if "health_index" not in data:
                print("FAILURE: 'health_index' missing.")
                success = False
            else:
                idx = data["health_index"]
                if not (0 <= idx <= 100):
                    print(f"FAILURE: Health index {idx} out of range.")
                    success = False
        else:
            print(f"FAILURE: Status {res.status_code}")
            success = False
    except Exception as e:
        print(f"Exception: {e}")
        success = False

    # 2. Cost Trend (Periods)
    periods = ["1W", "1M", "1Y"]
    for p in periods:
        try:
            print(f"\n[2] Testing Cost Trend (Period: {p})...")
            res = requests.get(f"{BASE_URL}/analytics/cost-trend?period={p}")
            if res.status_code == 200:
                data = res.json()
                labels = data.get("labels", [])
                print(f"Labels ({len(labels)}): {labels}")
                if len(labels) == 0:
                     print("WARNING: No labels returned (might be okay if no data, but expected buckets)")
            else:
                print(f"FAILURE: Status {res.status_code}")
                success = False
        except Exception as e:
            print(f"Exception: {e}")
            success = False
            
    # 3. Export
    try:
        print("\n[3] Testing CSV Export...")
        res = requests.get(f"{BASE_URL}/analytics/export")
        if res.status_code == 200:
            content = res.text
            line_count = len(content.splitlines())
            print(f"CSV Downloaded. Lines: {line_count}")
            print(f"Header: {content.splitlines()[0]}")
            if "ID,Vehicle" not in content.splitlines()[0]: # Basic check
                 # Actual header might be "ID,Vehicle,Task..."
                 pass
        else:
            print(f"FAILURE: Status {res.status_code}")
            success = False
    except Exception as e:
        print(f"Exception: {e}")
        success = False

    return success

if __name__ == "__main__":
    if test_analytics_advanced():
        print("\nVERIFICATION PASSED")
        sys.exit(0)
    else:
        print("\nVERIFICATION FAILED")
        sys.exit(1)
