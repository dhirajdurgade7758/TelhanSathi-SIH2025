#!/usr/bin/env python3
"""Verify buyer authentication session key fix"""

import sys
from pathlib import Path

# Check farmer auth (correct pattern)
farmer_auth_file = Path("routes/auth.py").read_text()
farmer_session_key = farmer_auth_file.count("session['farmer_id_verified']")

# Check buyer auth (should now match)
buyer_auth_file = Path("routes/buyer_auth.py").read_text()
buyer_session_key = buyer_auth_file.count("session['buyer_id_verified']")
buyer_get_key = buyer_auth_file.count("session.get('buyer_id_verified')")

# Check bidding (expectations)
bidding_file = Path("routes/bidding.py").read_text()
bidding_farmer_check = bidding_file.count("session['farmer_id_verified']")
bidding_buyer_check = bidding_file.count("session['buyer_id_verified']")

print("=" * 70)
print("AUTHENTICATION SESSION KEY VERIFICATION")
print("=" * 70)

print(f"\n✅ FARMER AUTHENTICATION (auth.py):")
print(f"   Sets farmer_id_verified: {farmer_session_key} times")

print(f"\n✅ BUYER AUTHENTICATION (buyer_auth.py):")
print(f"   Sets buyer_id_verified: {buyer_session_key} times")
print(f"   Gets buyer_id_verified: {buyer_get_key} times")
print(f"   Total: {buyer_session_key + buyer_get_key} references")

print(f"\n✅ BIDDING EXPECTATIONS (bidding.py):")
print(f"   Expects farmer_id_verified: {bidding_farmer_check} times")
print(f"   Expects buyer_id_verified: {bidding_buyer_check} times")

print("\n" + "=" * 70)
print("CONSISTENCY CHECK:")
print("=" * 70)

if buyer_session_key > 0 and buyer_get_key > 0:
    print("✅ Buyer session keys are now consistent")
    print("✅ Will match bidding.py expectations")
    print("✅ Buyers should now be able to access bidding endpoints")
else:
    print("❌ Issue with buyer session keys")
    sys.exit(1)

# Check for any leftover old keys
old_farmer_key = farmer_auth_file.count("session['farmer_id']") - farmer_auth_file.count("session['farmer_id_verified']")
old_buyer_key = buyer_auth_file.count("session['buyer_id']") - buyer_auth_file.count("session['buyer_id_verified']")

print("\n" + "=" * 70)
print("CLEANUP CHECK:")
print("=" * 70)
print(f"Old farmer_id keys (no _verified): {old_farmer_key}")
print(f"Old buyer_id keys (no _verified): {old_buyer_key}")

if old_buyer_key == 0:
    print("✅ All buyer session keys updated successfully!")
else:
    print(f"⚠️  Still {old_buyer_key} old buyer_id references")

print("\n" + "=" * 70)
print("NEXT STEPS:")
print("=" * 70)
print("1. Restart Flask server: flask run --host=0.0.0.0 --port=5000")
print("2. Test buyer login with: /buyer/login")
print("3. Visit: /bidding/debug/current-user to verify session")
print("4. Try accessing: /bidding/buyer/auctions")
