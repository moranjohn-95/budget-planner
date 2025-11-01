from typing import Optional

import typer
from . import auth
from python_scripts.services import transactions as tx
from ..services import reports
from ..utilities.constants import ALLOWED_CATEGORIES
from ..services import budgets as bud
from ..utilities.validation import require_date, require_month

app = typer.Typer(no_args_is_help=True, help="Budget Planner CLI")


@app.callback(invoke_without_command=True)
def _root(ctx: typer.Context) -> None:
    """Run when no subcommand is provided."""
    if ctx.invoked_subcommand is None:
        typer.echo("Budget Planner CLI is ready. Use --help or a subcommand.")


@app.command("signup")
def cli_signup(
    email: Optional[str] = typer.Option(
        None,
        "--email",
        prompt="Email",
        help="Email for the new account.",
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        prompt=True,
        hide_input=True,
        help="Password for the new account.",
    ),
    confirm: Optional[str] = typer.Option(
        None,
        "--confirm",
        prompt="Confirm password",
        hide_input=True,
        help="Confirm the password.",
    ),
) -> None:
    """
    Create a new user record in Google Sheets.

    Basic CLI validation:
    - Ensure password is correct and confirm it must match
    - Ensure password must be at least 6 chars
    """
    try:
        if password is None or confirm is None:
            typer.secho("Password is required.", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        if password != confirm:
            typer.secho("Passwords do not match.", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        if len(password) < 6:
            typer.secho(
                "Password must be at least 6 characters.",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)

        ok = auth.signup(email=email, password=password)
        if ok:
            typer.secho("Signup successful", fg=typer.colors.GREEN)
        else:
            typer.secho(
                "Signup failed (already signed up?)",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)
    except Exception as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("login")
def cli_login(
    email: Optional[str] = typer.Option(
        None,
        "--email",
        prompt="Email",
        help="Account email.",
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        prompt=True,
        hide_input=True,
        help="Account password.",
    ),
) -> None:
    """Verify credentials against the stored bcrypt hash."""
    try:
        ok = auth.login(email=email, password=password)
        if ok:
            typer.secho("Login successful", fg=typer.colors.GREEN)
        else:
            typer.secho(
                "Invalid email or password",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)
    except Exception as exc:
        typer.secho(f"Login failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("whoami")
def cli_whoami(
    email: Optional[str] = typer.Option(
        None,
        "--email",
        prompt="Email",
        help="Account email to look up.",
    ),
) -> None:
    """
    Show basic details for a user by email.
    """
    try:
        user = auth.get_user_by_email(email)
        if not user:
            typer.secho(
                "No account found for that email.",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)

        typer.echo(f"user_id   : {user.get('user_id')}")
        typer.echo(f"email     : {user.get('email')}")
        typer.echo(f"created_at: {user.get('created_at')}")
    except Exception as exc:
        typer.secho(f"Lookup failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("list-users")
def cli_list_users(
    limit: int = typer.Option(
        10,
        "--limit",
        help="Max number of users to display",
    )
) -> None:
    """
    Produce list of users (email + created_at).
    """
    try:
        rows = auth.list_users(limit=limit)
        if not rows:
            typer.echo("No users found.")
            return

        for row in rows:
            email = row.get("email", "")
            created = row.get("created_at", "")
            typer.echo(f"- {email} | {created}")
    except Exception as exc:
        typer.secho(f"List failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("add-txn")
def cli_add_txn(
    email: Optional[str] = typer.Option(
        None,
        "--email",
        prompt="Email",
        help="Account email to attach the transaction to.",
    ),
    date: Optional[str] = typer.Option(
        None,
        "--date",
        prompt="Date (YYYY-MM-DD)",
        help="Transaction date in YYYY-MM-DD format.",
    ),
    category: Optional[str] = typer.Option(
        None,
        "--category",
        prompt=f"Category ({', '.join(ALLOWED_CATEGORIES)})",
        help="Transaction category. Must be one of the allowed values.",
    ),
    amount: Optional[float] = typer.Option(
        None,
        "--amount",
        prompt="Amount",
        help="Transaction amount (e.g., 12.50).",
    ),
    note: Optional[str] = typer.Option(
        "",
        "--note",
        prompt="Note (optional)",
        help="Optional note for this transaction.",
    ),
) -> None:
    """
    Add a new transaction row to the 'transactions' sheet.
    """
    try:
        if amount is None:
            typer.secho("Amount is required.", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        date = require_date(date, "Date")

        txn_id = tx.add_transaction(
            email=email,
            date=date,
            category=category,
            amount=amount,
            note=note or "",
        )
        typer.secho(f"Transaction recorded: {txn_id}",
                    fg=typer.colors.GREEN)
    except Exception as exc:
        typer.secho(f"Add transaction failed: {exc}",
                    fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("list-txns")
def cli_list_txns(
    email: Optional[str] = typer.Option(
        None,
        "--email",
        help="Filter to this account's transactions.",
    ),
    date: Optional[str] = typer.Option(
        None,
        "--date",
        help="Filter by date (YYYY-MM-DD).",
    ),
    limit: int = typer.Option(
        20,
        "--limit",
        min=1,
        help="Max rows to show (default 20).",
    ),
) -> None:
    """
    Show recent transactions with optional filters.
    """
    try:
        rows = tx.list_transactions(
            email=email,
            date=date,
            limit=limit,
        )
        if not rows:
            typer.echo("No transactions found.")
            return

        # Simple table-like output, one row per line
        for r in rows:
            line = (
                f"{r.get('txn_id')} | {r.get('date')} | "
                f"{r.get('category')} | {r.get('amount')} | "
                f"{r.get('note')}"
            )
            typer.echo(line)
    except Exception as exc:
        typer.secho(f"List failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("sum-month")
def cli_sum_month(
    month: Optional[str] = typer.Option(
        None,
        "--month",
        prompt="Month (YYYY-MM)",
        help="Month to summarise, example, 2025-10.",
    ),
    email: Optional[str] = typer.Option(
        None,
        "--email",
        help="Option to filter.",
    ),
) -> None:
    """
    Print the total amount for the given month.
    Option to filter for a single account email.
    """
    try:
        total = reports.monthly_total(month=month, email=email)
        if email:
            typer.echo(f"Total for {month} ({email}): {total}")
        else:
            typer.echo(f"Total for {month}: {total}")
    except Exception as exc:
        typer.secho(f"Report failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("summary")
def cli_summary(
    email: Optional[str] = typer.Option(
        None,
        "--email",
        prompt="Email",
        help="Filter by account email.",
    ),
    date: Optional[str] = typer.Option(
        None,
        "--date",
        help="Filter by date (YYYY-MM-DD).",
    ),
) -> None:
    """
    Show total spending grouped by category.
    """
    try:
        summary = tx.summarize_by_category(email=email, date=date)
        if not summary:
            typer.echo("No transactions found.")
            raise typer.Exit(code=0)

        typer.echo("Category Summary:")
        typer.echo("-------------------")
        for cat, total in summary.items():
            typer.echo(f"{cat:15} {total:.2f}")
            continue
            typer.echo(f"{cat:15} £{total:.2f}")

    except Exception as exc:
        typer.secho(f"Summary failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("set-goal")
def cli_set_goal(
    email: Optional[str] = typer.Option(
        None,
        "--email",
        prompt="Email",
        help="Account email this goal belongs to.",
    ),
    month: Optional[str] = typer.Option(
        None,
        "--month",
        prompt="Month (YYYY-MM)",
        help="Month the goal applies to (e.g., 2025-10).",
    ),
    category: Optional[str] = typer.Option(
        None,
        "--category",
        prompt=(
            "Category (groceries, house-bills, transport, social, "
            "health, work-related, subscriptions, entertainment, "
            "savings, misc)"
        ),
        help="Budget category.",
    ),
    amount: Optional[float] = typer.Option(
        None,
        "--amount",
        prompt="Monthly goal amount",
        help="Goal amount for the month (numeric).",
    ),
) -> None:
    """
    Create or update a monthly goal for a user+month+category.
    """
    month = require_month(month)

    try:
        bid = bud.set_goal(
            email=email,
            month=month,
            category=category,
            amount=amount,
        )
        typer.secho(f"Goal saved (id: {bid})", fg=typer.colors.GREEN)
    except Exception as exc:
        typer.secho(f"Save failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("list-goals")
def cli_list_goals(
    email: Optional[str] = typer.Option(
        None,
        "--email",
        help="Filter to this account's goals.",
    ),
    month: Optional[str] = typer.Option(
        None,
        "--month",
        help="Filter by month (YYYY-MM).",
    ),
) -> None:
    """
    Show budget goals. Optional filters: --email, --month (YYYY-MM).
    """
    try:
        if month:
            month = require_month(month)

        rows = bud.list_goals(email=email, month=month)
        if not rows:
            typer.echo("No goals found.")
            return

        for r in rows:
            cat = r.get("category_norm") or r.get("category")
            goal = r.get("monthly_goal")
            user_id = r.get("user_id")
            mon = r.get("month")

            if user_id or mon:
                typer.echo(f"{cat}: {goal}  (user={user_id}, month={mon})")
            else:
                typer.echo(f"{cat}: {goal}")

    except Exception as exc:
        typer.secho(f"List failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("budget-status")
def cli_budget_status(
    email: str = typer.Option(
        "",
        "--email",
        help="Filter spend to a single account.",
    ),
    month: str = typer.Option(
        "",
        "--month",
        help="Filter by month (YYYY-MM) - optional.",
    ),
) -> None:
    """
    Compare goals to spend. Shows category, goal, spent and difference.
    """
    try:
        if month:
            month = require_month(month)

        rows = bud.goals_vs_spend(
            email=email or None,
            month=month or None,
        )
        if not rows:
            typer.echo("No goals to compare.")
            return

        typer.echo("category        goal      spent     diff")
        typer.echo("----------------------------------------")

        total_goal = 0.0
        total_spent = 0.0

        for r in rows:
            cat = str(r.get("category"))
            goal = float(r.get("goal", 0))
            spent = float(r.get("spent", 0))
            diff = float(r.get("diff", 0))

            total_goal += goal
            total_spent += spent

            line = f"{cat:14}  {goal:8.2f}  {spent:8.2f}  {diff:8.2f}"
            typer.echo(line)

        typer.echo("----------------------------------------")
        total_diff = total_goal - total_spent
        typer.echo(
            f"{'TOTAL':14}  {total_goal:8.2f}  "
            f"{total_spent:8.2f}  {total_diff:8.2f}"
        )

    except Exception as exc:
        typer.secho(f"Status failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


def main() -> None:
    """Entrypoint for the Typer app."""
    app()


if __name__ == "__main__":
    main()
