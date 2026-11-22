import sqlite3
import hashlib
import secrets
import hmac

_PBKD = 100_000

def _pbkdf2(password: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKD)
    return "pbkdf2${}${}".format(salt.hex(), dk.hex())

def _verify(password: str, stored: str) -> bool:
    try:
        algo, salt_hex, dk_hex = stored.split("$")
        if algo != "pbkdf2":
            return False
        salt = bytes.fromhex(salt_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKD)
        return hmac.compare_digest(dk.hex(), dk_hex)
    except Exception:
        return False

# New rotated owner password
NEW_OWNER_PASS = "ShahGroup_Owner_Secured_2026!#"
new_hash = _pbkdf2(NEW_OWNER_PASS)

for db in ['data/sgcc_foundation.sqlite', 'data/business_os.db']:
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT id, username, password_hash FROM users WHERE username='owner'")
    row = cur.fetchone()
    old_hash = row[2] if row else None
    
    # Check if old demo password verifies
    old_match = _verify("demo-owner-pass-0001", old_hash) if old_hash else False
    print(f"{db}: Old password matches 'demo-owner-pass-0001'? {old_match}")
    
    # Update to new secure hash
    cur.execute("UPDATE users SET password_hash=? WHERE username='owner'", (new_hash,))
    # Terminate all existing sessions for owner
    if row:
        cur.execute("DELETE FROM sessions WHERE user_id=?", (row[0],))
    conn.commit()
    
    # Verify new password
    cur.execute("SELECT password_hash FROM users WHERE username='owner'")
    verified_hash = cur.fetchone()[0]
    print(f"{db}: New password matches? {_verify(NEW_OWNER_PASS, verified_hash)}")
    print(f"{db}: Old demo password still matches? {_verify('demo-owner-pass-0001', verified_hash)}")

print("\nOwner password rotation complete.")
print(f"New Owner Password: {NEW_OWNER_PASS}")
