"""
reports.py
----------
Report helpers for transactions.
"""

from __future__ import annotations

from typing import Optional, List
from datetime import datetime

from ..budget_planner.sheets_gateway import get_client, get_sheet
from ..budget_planner import auth
from ..services import reports

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


def monthly_total(month: str, email: Optional[str] = None) -> float:
    """
    Sum 'amount' for rows whose date starts with YYYY-MM.
    Optionally restrict to a specific email.
    """
    try:
        # Validate input format early
        datetime.strptime(month, "%Y-%m")
    except ValueError as exc:
        raise ValueError("month must be 'YYYY-MM'.") from exc

    client = get_client()
    sheet = get_sheet(client)
    ws = sheet.worksheet(TRANSACTIONS_SHEET)
    _ensure_txn_sheet(ws)

    want_user = _resolve_user_id(email)
    total = 0.0

    for row in ws.get_all_records():
        date_s = str(row.get("date", "")).strip()
        if not date_s.startswith(month):
            continue

        if want_user is not None:
            uid = str(row.get("user_id", "")).strip()
            if uid != want_user:
                continue

        try:
            amt = float(row.get("amount", 0))
        except Exception:
            continue

        total += amt

    return round(total, 2)
