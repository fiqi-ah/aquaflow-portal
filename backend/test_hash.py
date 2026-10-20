# backend/test_hash.py
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

password = "ChangeMe123!"
print(f"Testing password: '{password}'")

try:
    # 1. Hash it
    hashed = ph.hash(password)
    print(f"Generated Hash: {hashed[:50]}...")
    
    # 2. Verify it (Correct Password)
    try:
        ph.verify(hashed, password)
        print("✅ SUCCESS: Correct password verified.")
    except VerifyMismatchError:
        print("❌ FAIL: Correct password rejected!")

    # 3. Verify it (Wrong Password)
    try:
        ph.verify(hashed, "WrongPassword")
        print("⚠️ WARNING: Wrong password accepted! (Security Issue)")
    except VerifyMismatchError:
        print("✅ CORRECT: Wrong password rejected as expected.")

except Exception as e:
    print(f"💥 CRITICAL ERROR: {e}")