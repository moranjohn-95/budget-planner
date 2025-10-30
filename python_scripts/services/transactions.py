"""
transactions.py
---------------
Core constants for transactions sheet.

Sheet: 'transactions'
Columns:
  txn_id | user_id | date | category | amount | note | created_at
"""

from __future__ import annotations

from typing import List
import uuid
from datetime import datetime

from ..budget_planner.sheets_gateway import get_client, get_sheet

from ..budget_planner import auth

TRANSACTIONS_SHEET = "transactions"
TRANSACTIONS_HEADERS: List[str] = [
    "txn_id",
    "user_id",
    "date",
    "category",
    "amount",
    "note",
    "created_at",
]


def _ensure_txn_sheet(ws) -> None:
    """
    Ensures the transactions sheet exists with the expected headers.
    If empty, write headers. If mismatched, raise for safety.
    """
    values = ws.get_all_values()
    if not values:
        ws.append_row(TRANSACTIONS_HEADERS)
        return
    if values[0] != TRANSACTIONS_HEADERS:
        raise RuntimeError(
            "Unexpected transactions header row. "
            "Align with TRANSACTIONS_HEADERS."
        )


def _resolve_user_id(email: str) -> str:
    """
    Lookup a user_id by email
    Raise if not found.
    """
    user = auth.get_user_by_email(email)
    if not user:
        raise RuntimeError("No account found for that email.")
    return str(user.get("user_id"))


def add_transaction(
    *,
    email: str,
    date: str,
    category: str,
    amount: float,
    note: str = "",
) -> str:
    """
    Add a new transaction entry to the 'transactions' worksheet.

    Parameters:
        email:    Account email; looked up to get user_id.
        date:     YYYY-MM-DD
        category: Open text category (example 'Groceries').
        amount:   Transaction amount.
        note:     Optional note.

    Returns:
        The generated txn_id.

    Raises:
        RuntimeError: if the user cannot be found or if sheet is misconfigured.
        ValueError:   if amount is invalid.
    """
    try:
        amount = float(amount)
    except Exception as exc:
        raise ValueError("Amount must be a number.") from exc

    if amount == 0.0:
        raise ValueError("Amount cannot be zero.")

    user_id = _resolve_user_id(email)
    client = get_client()
    sheet = get_sheet(client)
    ws = sheet.worksheet(TRANSACTIONS_SHEET)

    _ensure_txn_sheet(ws)

    txn_id = str(uuid.uuid4())
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [txn_id, user_id, date, category, amount, note, created_at]

    ws.append_row(row, value_input_option="USER_ENTERED")
    return txn_id
