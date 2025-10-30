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

from .sheets_gateway import get_client, get_sheet

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
