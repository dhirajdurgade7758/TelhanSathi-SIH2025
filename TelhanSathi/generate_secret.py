#!/usr/bin/env python3
"""
Generate a secure SECRET_KEY for production use.
Run: python generate_secret.py
"""
import secrets
import string

def generate_secret_key(length=50):
    """Generate a cryptographically secure random key."""
    alphabet = string.ascii_letters + string.digits + string.punctuation.replace("'", "").replace('"', '')
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == "__main__":
    secret_key = generate_secret_key()
    print("=" * 60)
    print("Generated SECRET_KEY (use in production):")
    print("=" * 60)
    print(secret_key)
    print("=" * 60)
    print("\nAdd this to your Render Environment Variables:")
    print(f"SECRET_KEY = {secret_key}")
