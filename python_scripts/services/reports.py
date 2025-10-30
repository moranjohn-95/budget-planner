"""
reports.py
----------
Report helpers for transactions.
"""

from __future__ import annotations

from typing import Optional, List

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
    Ensure the 'transactions' worksheet exists and headers match.
    """
    values = ws.get_all_values()
    if not values:
        ws.append_row(TRANSACTIONS_HEADERS)
        return
    if values[0] != TRANSACTIONS_HEADERS:
        raise RuntimeError(
            "Unexpected transactions header row; align with "
            "TRANSACTIONS_HEADERS."
        )


def _resolve_user_id(email: Optional[str]) -> Optional[str]:
    """
    Map an email to user_id; return None if no email filter is given.
    """
    if not email:
        return None
    user = auth.get_user_by_email(email)
    if not user:
        raise RuntimeError("No account found for that email.")
    return str(user.get("user_id"))
