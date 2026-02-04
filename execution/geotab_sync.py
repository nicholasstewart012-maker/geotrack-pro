import random
from datetime import datetime
import json
import os
import sqlite3

# This script mocks the Geotab API integration but updates the REAL SQLite database
DB_PATH = "backend/maintenance.db"

def fetch_geotab_data_from_api():
    """Mocks fetching data from Geotab API for enrolled vehicles"""
    # In a real app, we would query the DB for geotab_ids first
    # For this demo, we'll simulate data for any vehicle found in the DB
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT geotab_id, name FROM vehicles")
    enrolled_vehicles = cursor.fetchall()
    conn.close()
    
    updates = []
    for gid, name in enrolled_vehicles:
        # Simulate mileage/hours increase
        updates.append({
            "geotab_id": gid,
            "name": name,
            "new_mileage": random.uniform(50, 200), # Mileage increase since last sync
            "new_hours": random.uniform(1, 5)
        })
    return updates

def sync_to_local_db(updates):
    """Updates the REAL SQLite database with new telemetry"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"[{datetime.now()}] Syncing {len(updates)} vehicles in database...")
    for u in updates:
        cursor.execute("""
            UPDATE vehicles 
            SET current_mileage = current_mileage + ?,
                current_hours = current_hours + ?,
                last_sync = ?
            WHERE geotab_id = ?
        """, (u['new_mileage'], u['new_hours'], datetime.now(), u['geotab_id']))
        print(f"  - Updated {u['name']} (+{u['new_mileage']:.1f} miles)")
    
    conn.commit()
    conn.close()
    print("Sync complete.")

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Run the backend first.")
    else:
        data = fetch_geotab_data_from_api()
        sync_to_local_db(data)
