from typing import Optional

import typer
import os
import re
from . import auth
from python_scripts.services import transactions as tx
from ..services import reports
from ..utilities.constants import ALLOWED_CATEGORIES
from ..services import budgets as bud
from ..utilities.validation import require_date, require_month


# Output styling helpers for clearer sections
def header(text: str) -> None:
    typer.secho(text, fg=typer.colors.CYAN, bold=True)


def sep(width: int = 40) -> None:
    typer.secho("-" * width, fg=typer.colors.BRIGHT_BLACK)


def session_role() -> str:
    """Return the current session role (editor/user), defaulting to user."""
    return (os.environ.get("BP_ROLE") or "user").strip().lower() or "user"


def resolve_email_for_action(arg_email: Optional[str], *, require_login: bool = True) -> str:
    """Resolve which email a command should act on.

    - For editors: if --email is provided, use it; otherwise use the session email.
    - For users: require the session email and block cross-user actions.
    """
    role = session_role()
    if role == "editor":
        if arg_email:
            return _norm_email(arg_email) or ""
        return _session_email(None, require=require_login) or ""
    # Regular user path
    return _session_email(arg_email, require=require_login) or ""


def require_role(expected: str) -> None:
    """Exit with an error unless the session role matches expected."""
    role = session_role()
    if role != (expected or "").strip().lower():
        typer.secho(
            f"This action requires role '{expected}'. Your role is '{role}'.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)


# Input normalization helpers
def _normalize_month(value: Optional[str]) -> Optional[str]:
    """Coerce common month formats to YYYY-MM before strict validation."""
    if not value:
        return value
    raw = value.strip().replace("/", "-").replace(".", "-")
    m = re.match(r"^(\d{4})-(\d{1,2})$", raw)
    if m:
        mm = int(m.group(2))
        if 1 <= mm <= 12:
            return f"{m.group(1)}-{mm:02d}"
    m2 = re.match(r"^(\d{4})(\d{2})$", raw)
    if m2:
        mm = int(m2.group(2))
        if 1 <= mm <= 12:
            return f"{m2.group(1)}-{mm:02d}"
    return value


def _normalize_date(value: Optional[str]) -> Optional[str]:
    """Coerce common date formats to YYYY-MM-DD before strict validation.

    Accepts:
      - YYYY-M-D, YYYY-MM-D, YYYY-M-DD
      - YYYY/MM/DD, YYYY.MM.DD
      - YYYYMMDD (8 digits)
    """
    if not value:
        return value
    raw = value.strip().replace("/", "-").replace(".", "-")
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", raw)
    if m:
        mm = int(m.group(2))
        dd = int(m.group(3))
        if 1 <= mm <= 12 and 1 <= dd <= 31:
            return f"{m.group(1)}-{mm:02d}-{dd:02d}"
    m2 = re.match(r"^(\d{4})(\d{2})(\d{2})$", raw)
    if m2:
        mm = int(m2.group(2))
        dd = int(m2.group(3))
        if 1 <= mm <= 12 and 1 <= dd <= 31:
            return f"{m2.group(1)}-{mm:02d}-{dd:02d}"
    return value


def _norm_email(value: str | None) -> str | None:
    """Lower/trim an email for consistent comparison."""
    if value is None:
        return None
    return value.strip().lower()


def _session_email(
    arg_email: str | None,
    *,
    require: bool,
    prompt_if_missing: bool = False,
) -> str | None:
    """
    Fix the effective email for this process.

    - If BP_EMAIL is set:
        * If arg_email is given and different -> exit with error.
        * Otherwise return BP_EMAIL.
    - If BP_EMAIL is not set:
        * If arg_email is given -> return it.
        * If require=True and arg_email missing -> prompt once.
        * If require=False and arg_email missing -> return None.
    """
    sess = _norm_email(os.environ.get("BP_EMAIL"))
    arg = _norm_email(arg_email)

    if sess:
        if arg and arg != sess:
            # Let callers catch SystemExit to print a friendly message.
            raise typer.Exit(code=1)
        return sess

    if arg:
        return arg

    if require:
        if prompt_if_missing:
            return _norm_email(typer.prompt("Email"))
        # Require an authenticated session; do not prompt here
        typer.secho("Please login first (bp> login).", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    return None


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
        None, "--email", prompt="Email", help="Account email."
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        prompt=True,
        hide_input=True,
        help="Account password.",
    ),
) -> None:
    """Verify credentials and set a per-process session email."""
    try:
        ok = auth.login(email=email, password=password)
        if ok:
            norm = _norm_email(email) or ""
            os.environ["BP_EMAIL"] = norm
            try:
                role = auth.get_role(norm)
            except Exception:
                role = "user"
            os.environ["BP_ROLE"] = role
            typer.secho(f"Login successful (role: {role}).", fg=typer.colors.GREEN)
        else:
            typer.secho("Invalid email or password.", fg=typer.colors.RED)
            raise typer.Exit(code=1)
    except Exception as exc:
        typer.secho(f"Login failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("whoami")
def cli_whoami(
    email: Optional[str] = typer.Option(
        None, "--email", help="Account email to look up."
    ),
) -> None:
    """Show basic details for the current session (or given email)."""
    try:
        # Allow editor to inspect another account via --email
        resolved = resolve_email_for_action(email, require_login=True)
        user = auth.get_user_by_email(resolved or "")
        if not user:
            typer.secho(
                "No account found for that email.",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)

        typer.echo(f"user_id   : {user.get('user_id')}")
        typer.echo(f"email     : {user.get('email')}")
        typer.echo(f"created_at: {user.get('created_at')}")
    except SystemExit:
        sess = _norm_email(os.environ.get("BP_EMAIL"))
        typer.secho(
            f"You are logged in as '{sess}'. Cannot use a different --email.",
            fg=typer.colors.RED,
        )
        raise
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
        require_role("editor")
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
    """Add a new transaction row to the 'transactions' sheet."""
    try:
        if amount is None:
            typer.secho("Amount is required.", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        resolved = resolve_email_for_action(email, require_login=True)

        date = _normalize_date(date)
        date = require_date(date)

        txn_id = tx.add_transaction(
            email=resolved or "",
            date=date,
            category=category,
            amount=amount,
            note=note or "",
        )
        typer.secho(f"Transaction recorded: {txn_id}", fg=typer.colors.GREEN)

    except SystemExit:
        sess = _norm_email(os.environ.get("BP_EMAIL"))
        typer.secho(
            f"You are logged in as '{sess}'. Cannot use a different --email.",
            fg=typer.colors.RED,
        )
        raise
    except Exception as exc:
        typer.secho(f"Add transaction failed: {exc}", fg=typer.colors.RED)
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
    """Show recent transactions with optional filters."""
    try:
        # Editor can pass --email to inspect another account
        resolved = resolve_email_for_action(email, require_login=True)

        header("Transactions")
        typer.secho("txn_id | date | category | amount | note", fg=typer.colors.CYAN, bold=True)
        sep(70)

        # Validate date if provided
        if date:
            date = _normalize_date(date)
            date = require_date(date)

        rows = tx.list_transactions(
            email=resolved,
            date=date,
            limit=limit,
        )
        if not rows:
            typer.echo("No transactions found.")
            return

        for r in rows:
            line = (
                f"{r.get('txn_id')} | {r.get('date')} | "
                f"{r.get('category')} | {r.get('amount')} | "
                f"{r.get('note')}"
            )
            typer.echo(line)
    except SystemExit:
        sess = _norm_email(os.environ.get("BP_EMAIL"))
        typer.secho(
            f"You are logged in as '{sess}'. Cannot use a different --email.",
            fg=typer.colors.RED,
        )
        raise
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
        # Validate month and enforce session email
        month = _normalize_month(month)
        month = require_month(month)
        resolved = resolve_email_for_action(email, require_login=True)

        header("Monthly Total")
        sep(40)
        total = reports.monthly_total(month=month, email=resolved)
        if resolved:
            typer.echo(f"Total for {month} ({resolved}): {total}")
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
        resolved = resolve_email_for_action(email, require_login=True)
        if date:
            date = _normalize_date(date)
            date = require_date(date)
        summary = tx.summarize_by_category(email=resolved, date=date)
        if not summary:
            typer.echo("No transactions found.")
            raise typer.Exit(code=0)

        header("Category Summary")
        sep(40)
        for cat, total in summary.items():
            typer.echo(f"{cat:15} {total:.2f}")
            typer.echo(f"{cat:15} £{total:.2f}")

    except Exception as exc:
        typer.secho(f"Summary failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("set-goal")
def cli_set_goal(
    email: Optional[str] = typer.Option(
        None,
        "--email",
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
    try:
        if month:
            month = _normalize_month(month)
            month = require_month(month)

        # Editor can pass --email to set goals for another account
        resolved = resolve_email_for_action(email, require_login=True)

        bid = bud.set_goal(
            email=resolved or "",
            month=month,
            category=category,
            amount=amount,
        )
        typer.secho(f"Goal saved (id: {bid})", fg=typer.colors.GREEN)
    except SystemExit:
        sess = _norm_email(os.environ.get("BP_EMAIL"))
        typer.secho(
            f"You are logged in as '{sess}'. Cannot use a different --email.",
            fg=typer.colors.RED,
        )
        raise
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
            month = _normalize_month(month)
            month = require_month(month)

        resolved = resolve_email_for_action(email, require_login=True)

        rows = bud.list_goals(email=resolved, month=month)
        if not rows:
            typer.echo("No goals found.")
            return

        header("Goals")
        typer.secho("category | monthly_goal", fg=typer.colors.CYAN, bold=True)
        sep(40)

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
    Enforces the logged-in session email; month is optional.
    """
    try:
        if month:
            month = _normalize_month(month)
            month = require_month(month)

        # Enforce session email; block cross-user status checks
        resolved = resolve_email_for_action(email or None, require_login=True)

        rows = bud.goals_vs_spend(
            email=resolved or None,
            month=month or None,
        )
        if not rows:
            typer.echo("No goals to compare.")
            return

        header("Budget Status")
        typer.secho("category        goal      spent     diff", fg=typer.colors.CYAN, bold=True)
        sep(40)

        total_goal = 0.0
        total_spent = 0.0

        for r in rows:
            cat = str(r.get("category"))
            goal = float(r.get("goal", 0))
            spent = float(r.get("spent", 0))
            diff = float(r.get("diff", 0))

            total_goal += goal
            total_spent += spent

            diff_text = f"{diff:8.2f}"
            diff_colored = (
                typer.style(diff_text, fg=typer.colors.GREEN)
                if diff >= 0
                else typer.style(diff_text, fg=typer.colors.RED)
            )

            typer.echo(f"{cat:14}  {goal:8.2f}  {spent:8.2f}  {diff_colored}")

        sep(40)
        total_diff = total_goal - total_spent
        total_diff_text = f"{total_diff:8.2f}"
        total_diff_colored = (
            typer.style(total_diff_text, fg=typer.colors.GREEN)
            if total_diff >= 0
            else typer.style(total_diff_text, fg=typer.colors.RED)
        )
        typer.echo(
            f"{'TOTAL':14}  {total_goal:8.2f}  {total_spent:8.2f}  {total_diff_colored}"
        )

    except SystemExit:
        sess = _norm_email(os.environ.get("BP_EMAIL"))
        typer.secho(
            f"You are logged in as '{sess}'. Cannot use a different --email.",
            fg=typer.colors.RED,
        )
        raise
    except Exception as exc:
        typer.secho(f"Status failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("logout")
def cli_logout() -> None:
    """Clear the current session email."""
    if os.environ.pop("BP_EMAIL", None):
        typer.secho("Logged out.", fg=typer.colors.GREEN)
    else:
        typer.echo("No active session.")


@app.command("set-role")
def cli_set_role(
    target_email: Optional[str] = typer.Option(
        None,
        "--email",
        prompt="Email to change",
        help="Account email to assign a role to.",
    ),
    role: Optional[str] = typer.Option(
        None,
        "--role",
        prompt="Role (user/editor)",
        help="Role to assign (user or editor).",
    ),
) -> None:
    """Assign a role to an account (editor-only)."""
    try:
        require_role("editor")

        if not target_email:
            raise typer.BadParameter("--email is required")
        role_norm = (role or "").strip().lower()
        if role_norm not in {"user", "editor"}:
            raise typer.BadParameter("--role must be 'user' or 'editor'")

        auth.set_role(target_email, role_norm)
        typer.secho(
            f"Set role for {target_email.strip().lower()} to {role_norm}.",
            fg=typer.colors.GREEN,
        )
    except typer.BadParameter as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("change-password")
def cli_change_password(
    current_password: Optional[str] = typer.Option(
        None,
        "--current",
        prompt=True,
        hide_input=True,
        help="Your current password.",
    ),
    new_password: Optional[str] = typer.Option(
        None,
        "--new",
        prompt="New password",
        hide_input=True,
        help="Your new password.",
    ),
    confirm_password: Optional[str] = typer.Option(
        None,
        "--confirm",
        prompt="Confirm new password",
        hide_input=True,
        help="Confirm the new password.",
    ),
) -> None:
    """Change password for the logged-in account."""
    try:
        # Require login and act on the session email only
        email = resolve_email_for_action(None, require_login=True)

        if not current_password:
            raise typer.BadParameter("Current password is required")
        if not new_password or not confirm_password:
            raise typer.BadParameter("New password and confirmation are required")
        if new_password != confirm_password:
            typer.secho("Passwords do not match.", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        if len(new_password) < 6:
            typer.secho("Password must be at least 6 characters.", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        user = auth.get_user_by_email(email)
        if not user:
            typer.secho("No account found for this email.", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        if not auth.verify_password(current_password, user.get("password_hash", "")):
            typer.secho("Current password is incorrect.", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        new_hash = auth.hash_password(new_password)
        auth.update_password_hash(email, new_hash)
        typer.secho("Password updated.", fg=typer.colors.GREEN)
    except typer.BadParameter as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except Exception as exc:
        typer.secho(f"Change password failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


def main() -> None:
    """Entrypoint for the Typer app."""
    app()


if __name__ == "__main__":
    main()



