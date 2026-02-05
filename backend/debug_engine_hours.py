import os
import mygeotab
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

GEOTAB_SERVER = os.getenv("GEOTAB_SERVER", "my.geotab.com")
GEOTAB_USER = os.getenv("GEOTAB_USER")
GEOTAB_PASS = os.getenv("GEOTAB_PASSWORD")
GEOTAB_DB = os.getenv("GEOTAB_DATABASE")

def debug_engine():
    print(f"Connecting to {GEOTAB_DB}...")
    api = mygeotab.API(username=GEOTAB_USER, password=GEOTAB_PASS, database=GEOTAB_DB)
    api.authenticate()
    
    # 1. Get a device
    devices = api.get("Device", resultsLimit=1)
    if not devices:
        print("No devices found.")
        return
    
    device = devices[0]
    print(f"Check Device: {device['name']} (ID: {device['id']})")
    
    # 2. Try different diagnostics
    # DiagnosticEngineHoursId, DiagnosticEngineHoursWrapperId, DiagnosticEngineHoursAdjustmentId
    
    diagnostics_to_check = [
        "DiagnosticEngineHoursId", 
        "DiagnosticEngineHoursWrapperId",
        "DiagnosticEngineHoursAdjustmentId"
    ]
    
    for diag_id in diagnostics_to_check:
        print(f"\n--- Checking {diag_id} ---")
        try:
            # Look back 30 days
            now = datetime.utcnow()
            results = api.get("StatusData", search={
                "deviceSearch": {"id": device['id']},
                "diagnosticSearch": {"id": diag_id},
                "fromDate": (now - timedelta(days=30)).isoformat() + "Z",
                "take": 5 # Get a few
            })
            
            if results:
                print(f"✅ Found {len(results)} records.")
                latest = results[-1] # Usually sorted by date? No, Geotab returns oldest first usually on FromDate queries? 
                # Actually StatusData is usually time sorted.
                print(f"   Latest Value: {latest['data']} (Date: {latest['dateTime']})")
                val_seconds = latest['data']
                print(f"   In Hours: {val_seconds / 3600.0}")
            else:
                print("❌ No data found in the last 30 days.")
                
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    debug_engine()
