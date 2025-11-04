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


def get_role(email: str) -> str:
    """Return the role for a given email from the 'Role' worksheet.

    Expects a sheet named exactly 'Role' with a header row that includes
    'email' and 'role'. If the sheet doesn't exist or no matching row is
    found, returns 'user' by default.
    """
    try:
        email_norm = normalize_email(email)
        client = get_client()
        sheet = get_sheet(client)
        try:
            ws = sheet.worksheet("Role")
        except Exception:
            return "user"
        for row in ws.get_all_records():
            if (row.get("email", "") or "").strip().lower() == email_norm:
                return (row.get("role", "user") or "user").strip().lower()
        return "user"
    except Exception:
        # On any errors, default to least-privileged role
        return "user"


def set_role(email: str, role: str) -> None:
    """Create/update a role mapping in the 'Role' worksheet.

    If the sheet is missing, it will be created with headers ['email','role'].
    """
    email_norm = normalize_email(require_nonempty(email, "Email"))
    role_norm = (require_nonempty(role, "Role").strip().lower())
    if role_norm not in {"user", "editor"}:
        raise ValueError("Role must be 'user' or 'editor'.")

    client = get_client()
    sheet = get_sheet(client)
    try:
        ws = sheet.worksheet("Role")
    except Exception:
        ws = sheet.add_worksheet(title="Role", rows=1000, cols=2)
        ws.update("A1:B1", [["email", "role"]])

    # Try to find existing row to update
    records = ws.get_all_records()
    for idx, row in enumerate(records, start=2):  # data starts on row 2
        if (row.get("email", "") or "").strip().lower() == email_norm:
            ws.update_cell(idx, 2, role_norm)
            return
    # Append new mapping
    ws.append_row([email_norm, role_norm], value_input_option="USER_ENTERED")


def update_password_hash(email: str, new_hash: str) -> None:
    """Update the password_hash for a given email in the 'users' worksheet.

    Looks up the row by email (case-insensitive) and updates the
    password_hash column. Raises a ValueError if the user is not found
    or the sheet does not include the expected headers.
    """
    client = get_client()
    sheet = get_sheet(client)
    ws = sheet.worksheet("users")

    headers = ws.row_values(1)
    try:
        col_idx = headers.index("password_hash") + 1  # 1-based index
    except ValueError as exc:
        raise ValueError("'users' sheet missing 'password_hash' header") from exc

    target = normalize_email(email)
    records = ws.get_all_records()
    for row_idx, row in enumerate(records, start=2):
        if normalize_email(row.get("email", "")) == target:
            ws.update_cell(row_idx, col_idx, new_hash)
            return
    raise ValueError("No account found for this email.")
