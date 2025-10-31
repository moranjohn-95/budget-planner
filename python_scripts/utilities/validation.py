"""
validation.py
-------------
Utility helpers to validate user inputs
before writing to Google Sheets.
"""

from __future__ import annotations

import re


def require_nonempty(value: str, field_name: str) -> str:
    """Ensure a string field is not empty or any whitespace."""
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty.")
    return value.strip()


def require_positive(value: float, field_name: str) -> float:
    """Ensure a numeric field is greater than zero."""
    if value <= 0:
        raise ValueError(f"{field_name} must be positive.")
    return value


def normalize_email(email: str) -> str:
    """Normalize email string by trimming and lowering case."""
    return require_nonempty(email, "Email").lower()


_MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
_DATE_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")


def is_valid_month(value: str) -> bool:
    """Return True if value matches YYYY-MM."""
    return bool(_MONTH_RE.match((value or "").strip()))


def require_month(value: str, name: str = "Month") -> str:
    """Return month if valid else raise ValueError."""
    v = (value or "").strip()
    if not is_valid_month(v):
        raise ValueError(f"{name} must be YYYY-MM (e.g., 2025-10).")
    return v


def is_valid_date(value: str) -> bool:
    """Return True if value matches YYYY-MM-DD (basic check)."""
    return bool(_DATE_RE.match((value or "").strip()))


def require_date(value: str, name: str = "Date") -> str:
    """Return date if valid else raise ValueError."""
    v = (value or "").strip()
    if not is_valid_date(v):
        raise ValueError(f"{name} must be YYYY-MM-DD (e.g., 2025-10-30).")
    return v
