import requests
import pyotp
import time
import sys

BASE_URL = "http://localhost:8000/api/v1"
import uuid
USER_ID = str(uuid.uuid4())

def log(msg):
    print(f"[TEST] {msg}")

def fail(msg):
    print(f"[FAIL] {msg}")
    sys.exit(1)

def test_provision():
    log("Testing Provisioning...")
    response = requests.post(f"{BASE_URL}/authenticator/provision", json={
        "user_id": USER_ID,
        "display_name": "Test User",
        "issuer": "TestIssuer"
    })
    if response.status_code != 200:
        fail(f"Provision failed: {response.text}")
    
    data = response.json()
    log("Provision successful")
    return data

def test_verify_setup(provision_token, secret):
    log("Testing Verify Setup...")
    totp = pyotp.TOTP(secret)
    code = totp.now()
    
    response = requests.post(f"{BASE_URL}/authenticator/verify-setup", json={
        "provision_token": provision_token,
        "code": code
    })
    
    if response.status_code != 200:
        fail(f"Verify Setup failed: {response.text}")
    
    if not response.json().get("verified"):
        fail("Verify Setup returned verified=false")
        
    log("Verify Setup successful")

def test_verify_login(secret):
    log("Testing Verify Login...")
    totp = pyotp.TOTP(secret)
    code = totp.now()
    
    response = requests.post(f"{BASE_URL}/authenticator/verify", json={
        "user_id": USER_ID,
        "code": code
    })
    
    if response.status_code != 200:
        fail(f"Verify Login failed: {response.text}")
        
    if not response.json().get("verified"):
        fail("Verify Login returned verified=false")
        
    log("Verify Login successful")

def test_rate_limit(secret):
    log("Testing Rate Limit...")
    # Intentionally fail 6 times
    for i in range(6):
        response = requests.post(f"{BASE_URL}/authenticator/verify", json={
            "user_id": USER_ID,
            "code": "000000"
        })
        if i == 5:
            if response.status_code == 429:
                log("Rate Limit successful (got 429)")
                return
            else:
                fail(f"Expected 429, got {response.status_code}")
    fail("Rate Limit failed (did not get 429)")

def test_backup_codes():
    log("Testing Backup Codes...")
    # Wait for rate limit to expire? No, backup codes are separate endpoint usually, 
    # but verify-backup might share rate limit? 
    # Our implementation checks rate limit on /verify, not /verify-backup explicitly in the code I wrote?
    # Let's check auth.py. verify_backup_code does NOT call rate_limit_service.check_rate_limit.
    # So we can proceed.
    
    response = requests.post(f"{BASE_URL}/authenticator/backup-codes/generate", json={
        "user_id": USER_ID
    })
    if response.status_code != 200:
        fail(f"Generate Backup Codes failed: {response.text}")
        
    codes = response.json().get("backup_codes")
    if not codes or len(codes) != 10:
        fail("Did not receive 10 backup codes")
        
    log("Generated backup codes")
    
    # Verify one
    code = codes[0]
    response = requests.post(f"{BASE_URL}/authenticator/verify-backup", json={
        "user_id": USER_ID,
        "backup_code": code
    })
    
    if response.status_code != 200:
        fail(f"Verify Backup failed: {response.text}")
        
    if not response.json().get("verified"):
        fail("Verify Backup returned verified=false")
        
    log("Verify Backup successful")
    
    # Verify same code again (should fail)
    response = requests.post(f"{BASE_URL}/authenticator/verify-backup", json={
        "user_id": USER_ID,
        "backup_code": code
    })
    if response.json().get("verified"):
        fail("Reusing backup code succeeded (should fail)")
        
    log("Backup code reuse prevention successful")

def test_disable():
    log("Testing Disable...")
    response = requests.post(f"{BASE_URL}/authenticator/disable", json={
        "user_id": USER_ID
    })
    if response.status_code != 200:
        fail(f"Disable failed: {response.text}")
        
    # Verify login should fail now
    response = requests.post(f"{BASE_URL}/authenticator/verify", json={
        "user_id": USER_ID,
        "code": "123456"
    })
    if response.status_code != 404:
        fail(f"Verify after disable should return 404, got {response.status_code}")
        
    log("Disable successful")

def main():
    try:
        data = test_provision()
        secret = data['secret_base32']
        token = data['provision_token']
        
        test_verify_setup(token, secret)
        test_verify_login(secret)
        test_backup_codes()
        # Rate limit test might block user for 5 mins, so do it last or skip if we want to disable
        # test_rate_limit(secret) 
        # Actually rate limit is on /verify, so it won't affect /disable
        test_rate_limit(secret)
        
        # Wait for rate limit window? Or just disable.
        # Disable endpoint doesn't check rate limit.
        test_disable()
        
        log("ALL TESTS PASSED")
    except Exception as e:
        fail(f"Exception: {e}")

if __name__ == "__main__":
    main()
