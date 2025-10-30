"""
auth.py
-------
Authentication and password control.

Responsible for:
- Secure password hashing using bcrypt.
- User signup and login functions connected to Google Sheets.
- Fetch existing users by email.
"""

import uuid
import bcrypt
from .sheets_gateway import get_client, get_sheet
from datetime import datetime
from ..utilities.validation import (
    normalize_email,
    require_nonempty,
)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def get_user_by_email(email: str):
    """
    Retrieve a user by email from the 'users' worksheet.
    Ensure email is normalised for case-insensitive match.
    """
    client = get_client()
    sheet = get_sheet(client)
    ws = sheet.worksheet("users")

    email_norm = normalize_email(email)
    records = ws.get_all_records()
    for row in records:
        if row.get("email", "").strip().lower() == email_norm:
            return row
    return None


def signup(email: str, password: str) -> bool:
    """
    Register a new user in the 'users' worksheet.
    """
    email = normalize_email(require_nonempty(email, "Email"))
    password = require_nonempty(password, "Password")

    client = get_client()
    sheet = get_sheet(client)
    ws = sheet.worksheet("users")

    email = email.strip().lower()
    existing = get_user_by_email(email)
    if existing:
        print("Email already registered.")
        return False

    if len(password) < 6:
        print("Password must be at least 6 characters long.")
        return False

    hashed_pw = hash_password(password)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # UUID is used for greater secuirty and safety
    user_id = str(uuid.uuid4())

    ws.append_row([user_id, email, hashed_pw, created_at])
    print(f" User {email} registered successfully.")
    return True


def login(email: str, password: str) -> bool:
    """
    Authenticate a user by checking stored hash.
    """
    email = normalize_email(require_nonempty(email, "Email"))
    password = require_nonempty(password, "Password")

    user = get_user_by_email(email)
    if not user:
        print("No account found for this email.")
        return False

    if verify_password(password, user["password_hash"]):
        print("Login successful.")
        return True
    else:
        print("Incorrect password.")
        return False


def list_users(limit: int = 20) -> list[dict]:
    """
    Added to return user records from the 'users' worksheet.

    To be included:
    'user_id', 'email', 'password_hash', 'created_at'.
    """
    client = get_client()
    sheet = get_sheet(client)
    ws = sheet.worksheet("users")

    records = ws.get_all_records()
    if limit and limit > 0:
        return records[:limit]
    return records
