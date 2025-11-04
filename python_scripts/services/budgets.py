"""
budgets.py
----------
Per-user, per-month budget goals and comparisons.

Sheet: 'budget'
Columns:
  budget_id | user_id | month | category_norm | monthly_goal
"""

from __future__ import annotations

import uuid
from typing import List, Dict

from ..utilities.constants import ALLOWED_CATEGORIES
from collections import defaultdict
from ..budget_planner.sheets_gateway import get_client, get_sheet
from ..budget_planner import auth
from . import transactions as tx
from ..utilities.validation import require_month

BUDGET_SHEET = "budget"
BUDGET_HEADERS: List[str] = [
    "budget_id",
    "user_id",
    "month",
    "category_norm",
    "monthly_goal",
]


def _ensure_budget_sheet(ws) -> None:
    """Create headers if sheet is empty; guard if mismatch."""
    # Make sure the sheet uses the expected header row.
    values = ws.get_all_values()
    if not values:
        ws.append_row(BUDGET_HEADERS)
        return
    if values[0] != BUDGET_HEADERS:
        raise RuntimeError(
            "Unexpected budget header row. Align with BUDGET_HEADERS."
        )


def set_goal(
    *, email: str, month: str, category: str, amount: float
) -> str:
    """
    update a goal for (user_id, month and category_norm).
    Returns the budget_id.
    """
    # Keep categories consistent (lowercase) and only allow known ones.
    cat_norm = (category or "").strip().lower()
    if cat_norm not in ALLOWED_CATEGORIES:
        allowed = ", ".join(ALLOWED_CATEGORIES)
        raise ValueError(f"Invalid category '{category}'. Allowed: {allowed}")

    month = require_month(month)

    try:
        goal = float(amount)
    except Exception as exc:
        raise ValueError("Amount must be numeric.") from exc
    if goal <= 0.0:
        raise ValueError("Amount must be greater than zero.")

    user = auth.get_user_by_email(email)
    if not user:
        raise RuntimeError("No account found for that email.")
    user_id = str(user.get("user_id"))

    client = get_client()
    sheet = get_sheet(client)
    ws = sheet.worksheet(BUDGET_SHEET)
    _ensure_budget_sheet(ws)

    # If a matching row already exists, update it; else append a new row.
    rows = ws.get_all_records()

    for idx, row in enumerate(rows, start=2):
        if (
            str(row.get("user_id")) == user_id
            and str(row.get("month")) == month
            and str(row.get("category_norm")) == cat_norm
        ):

            ws.update_cell(idx, 5, goal)
            return str(row.get("budget_id")) or "updated"

    budget_id = str(uuid.uuid4())
    ws.append_row(
        [budget_id, user_id, month, cat_norm, goal],
        value_input_option="USER_ENTERED",
    )
    return budget_id


def list_goals(
    *, email: str | None = None, month: str | None = None
) -> List[Dict]:
    """
    Return goals. Optional filters:
    - email
    - month
    """
    client = get_client()
    sheet = get_sheet(client)
    ws = sheet.worksheet(BUDGET_SHEET)
    _ensure_budget_sheet(ws)
    rows = ws.get_all_records()

    if email:
        user = auth.get_user_by_email(email)
        if not user:
            return []
        user_id = str(user.get("user_id"))
        rows = [r for r in rows if str(r.get("user_id")) == user_id]

    if month:
        rows = [r for r in rows if str(r.get("month")) == month]

    return rows


def goals_vs_spend(
    *, email: str, month: str | None
) -> List[Dict]:
    """
    Compare goals with actual spend for a user and month.
    """
    if month:
        month = require_month(month)

    # Get this user's goals (optionally for a specific month).
    goals = list_goals(email=email, month=month)

    # Gather this user's spend by category to compare with goals.
    rows = tx.list_transactions(email=email)
    spent_by_cat = defaultdict(float)
    for r in rows:
        date_s = str(r.get("date", "")).strip()
        if month and not date_s.startswith(month):
            continue
        cat = str(
            r.get("category")
            or r.get("category_norm")
            or ""
        ).strip().lower()
        try:
            amt = float(r.get("amount", 0) or 0)
        except Exception:
            continue
        spent_by_cat[cat] += amt

    rows: List[Dict] = []
    for g in goals:
        cat = str(g.get("category_norm", "")).strip().lower()
        goal = float(g.get("monthly_goal", 0))
        spent = float(spent_by_cat.get(cat, 0.0))
        diff = goal - spent
        rows.append(
            {"category": cat, "goal": goal, "spent": spent, "diff": diff}
        )
    return rows
