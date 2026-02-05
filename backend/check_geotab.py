import os
import mygeotab
from dotenv import load_dotenv

load_dotenv()

GEOTAB_SERVER = os.getenv("GEOTAB_SERVER", "my.geotab.com")
GEOTAB_USER = os.getenv("GEOTAB_USER")
GEOTAB_PASS = os.getenv("GEOTAB_PASSWORD")
GEOTAB_DB = os.getenv("GEOTAB_DATABASE")

def check_connection():
    print(f"Checking Geotab connection for server: {GEOTAB_SERVER}...")
    
    if not GEOTAB_USER or not GEOTAB_PASS or not GEOTAB_DB:
        print("❌ Error: Missing credentials in .env file.")
        print("Please ensure GEOTAB_USER, GEOTAB_PASSWORD, and GEOTAB_DATABASE are set.")
        return

    try:
        # Note: server argument is deprecated in some versions but useful if auto-discovery fails
        # authenticate() usually handles routing.
        api = mygeotab.API(username=GEOTAB_USER, password=GEOTAB_PASS, database=GEOTAB_DB)
        api.authenticate()
        print(f"✅ Successfully authenticated as {GEOTAB_USER}!")
        
        # Try a simple fetch
        print("   Fetching devices...")
        devices = api.get("Device", search={"groups": [{"id": "GroupCompanyId"}]}) # Search for all company devices
        if not devices:
             devices = api.get("Device") # Fallback to all accessible devices

        print(f"✅ Found {len(devices)} devices.")
        for d in devices[:5]:
            print(f"   - {d.get('name', 'Unknown')} (Serial: {d.get('serialNumber', 'N/A')}, ID: {d['id']})")
        
        if len(devices) > 5:
            print(f"   ... and {len(devices) - 5} more.")
            
    except mygeotab.AuthenticationException as e:
        print(f"❌ Authentication Failed: {e}")
        print("Please check your username, password, and database name.")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    check_connection()
