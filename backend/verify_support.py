import requests
import sys
import os

BASE_URL = "http://localhost:8000"

def test_support_submission():
    print(f"Testing Support Submission against {BASE_URL}")

    try:
        # Create a dummy file
        dummy_filename = "test_log.txt"
        with open(dummy_filename, "w") as f:
            f.write("This is a test log for support.")
            
        files = {
            'attachment': (dummy_filename, open(dummy_filename, 'rb'), 'text/plain')
        }
        data = {
            'issue_type': 'Test Issue',
            'impact_count': '2-5',
            'description': 'This is a test description from the verification script.',
            'user_email': 'verify@test.com'
        }
        
        print("Sending request...")
        res = requests.post(f"{BASE_URL}/support/submit", data=data, files=files)
        
        # Cleanup dummy file
        files['attachment'][1].close()
        os.remove(dummy_filename)
        
        if res.status_code != 200:
            print(f"FAILED: Status {res.status_code} {res.text}")
            return False
            
        resp_json = res.json()
        print(f"Response: {resp_json}")
        
        if resp_json.get("status") != "success":
            print("FAILED: Status not success")
            return False
            
        print("SUCCESS: Endpoint returned success.")
        return True

    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    if test_support_submission():
        print("VERIFICATION PASSED")
        sys.exit(0)
    else:
        print("VERIFICATION FAILED")
        sys.exit(1)
