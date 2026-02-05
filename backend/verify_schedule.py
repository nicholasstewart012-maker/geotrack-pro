import requests

API_BASE = "http://localhost:8000/api"

def test_schedule_update():
    # 1. Get a vehicle (which creates a default schedule)
    print("Fetching vehicles...")
    res = requests.get(f"{API_BASE}/vehicles")
    if not res.ok:
        print("Failed to fetch vehicles")
        return

    vehicles = res.json()
    if not vehicles:
        print("No vehicles found. Create one first.")
        return

    v = vehicles[0]
    print(f"Testing with Vehicle: {v['name']} (ID: {v['id']})")

    # 2. Get Schedules
    res = requests.get(f"{API_BASE}/schedules/{v['id']}")
    schedules = res.json()
    if not schedules:
        print("No schedules found.")
        return

    s = schedules[0]
    print(f"Current Schedule: ID={s['id']}, Interval={s['interval_value']}")

    # 3. Update Schedule
    new_interval = s['interval_value'] + 500
    print(f"Updating interval to {new_interval}...")
    
    res = requests.put(f"{API_BASE}/schedules/{s['id']}", json={
        "interval_value": new_interval
    })
    
    if res.ok:
        print("✅ Update successful")
    else:
        print(f"❌ Update failed: {res.text}")
        return

    # 4. Verify
    res = requests.get(f"{API_BASE}/schedules/{v['id']}")
    updated_s = res.json()[0]
    print(f"New Interval: {updated_s['interval_value']}")
    
    if updated_s['interval_value'] == new_interval:
        print("✅ Verification Passed!")
    else:
        print("❌ Verification Failed: Value mismatch")

if __name__ == "__main__":
    try:
        test_schedule_update()
    except Exception as e:
        print(f"Test failed: {e}")
