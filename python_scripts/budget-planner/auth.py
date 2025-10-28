"""
password hashing utilities
"""

import bcrypt
from .sheets_gateway import get_client, get_sheet
from datetime import datetime


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def get_user_by_email(email: str):
    """
    Retrieve a user record by email from the 'users' worksheet.
    """
    client = get_client()
    sheet = get_sheet(client)
    ws = sheet.worksheet("users")
    records = ws.get_all_records()

    for row in records:
        if row["email"].lower() == email.lower():
            return row
    return None


def signup(email: str, password: str) -> bool:
    """
    Register a new user in the 'users' worksheet.
    """
    client = get_client()
    sheet = get_sheet(client)
    ws = sheet.worksheet("users")

    existing = get_user_by_email(email)
    if existing:
        print("Email already registered.")
        return False

    hashed_pw = hash_password(password)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    next_id = len(ws.get_all_values())

    ws.append_row([next_id, email, hashed_pw, created_at])
    print(f"✅ User {email} registered successfully.")
    return True
