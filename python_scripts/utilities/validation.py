"""
validation.py
-------------
Utility helpers to validate user inputs
before writing to Google Sheets.
"""

from __future__ import annotations


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
