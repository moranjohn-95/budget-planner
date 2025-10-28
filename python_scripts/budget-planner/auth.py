"""
password hashing utilities
"""

import bcrypt
from .sheets_gateway import get_client, get_sheet


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
