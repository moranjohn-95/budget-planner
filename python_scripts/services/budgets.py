"""
budgets.py
----------
Per-user, per-month budget goals and comparisons.

Sheet: 'budget'
Columns:
  budget_id | user_id | month | category_norm | monthly_goal
"""

from __future__ import annotations

from typing import List, Dict

from ..utilities.constants import ALLOWED_CATEGORIES
from ..budget_planner.sheets_gateway import get_client, get_sheet
from . import transactions as tx

BUDGET_SHEET = "budget"
BUDGET_HEADERS: List[str] = ["category", "monthly_goal"]


def _ensure_budget_sheet(ws) -> None:
    """Create headers if sheet is empty; guard if mismatch."""
    values = ws.get_all_values()
    if not values:
        ws.append_row(BUDGET_HEADERS)
        return
    if values[0] != BUDGET_HEADERS:
        raise RuntimeError(
            "Unexpected budget header row. Align with BUDGET_HEADERS."
        )


def set_goal(*, category: str, monthly_goal: float) -> None:
    """
    Create/ update a monthly goal for a given category.
    """
    cat = (category or "").strip().lower()
    if cat not in ALLOWED_CATEGORIES:
        allowed = ", ".join(ALLOWED_CATEGORIES)
        raise ValueError(f"Invalid category '{category}'. Allowed: {allowed}")

    try:
        goal = float(monthly_goal)
    except Exception as exc:
        raise ValueError("monthly_goal must be numeric.") from exc

    client = get_client()
    sheet = get_sheet(client)
    ws = sheet.worksheet(BUDGET_SHEET)
    _ensure_budget_sheet(ws)

    rows = ws.get_all_records()
    for idx, row in enumerate(rows, start=2):
        if str(row.get("category", "")).strip().lower() == cat:
            ws.update_cell(idx, 2, goal)
            return

    ws.append_row([cat, goal], value_input_option="USER_ENTERED")


def list_goals() -> List[Dict]:
    """Return all budget goals as a list of dicts."""
    client = get_client()
    sheet = get_sheet(client)
    ws = sheet.worksheet(BUDGET_SHEET)
    _ensure_budget_sheet(ws)
    return ws.get_all_records()


def goals_vs_spend(
    *, email: str | None = None, month: str | None = None
) -> List[Dict]:
    """
    Compare goals with actual category spend.
    month: 'YYYY-MM'. If provided - filter by that month.
    """
    goals = list_goals()
    spend = tx.summarize_by_category(email=email, month=month)
    spent_by_cat = {r["category"]: float(r["total"]) for r in spend}

    rows: List[Dict] = []
    for g in goals:
        cat = str(g.get("category", "")).strip().lower()
        goal = float(g.get("monthly_goal", 0))
        spent = float(spent_by_cat.get(cat, 0))
        diff = goal - spent
        rows.append(
            {"category": cat, "goal": goal, "spent": spent, "diff": diff}
        )
    return rows
