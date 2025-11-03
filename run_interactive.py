"""
Heroku entrypoint for the browser terminal.
Starts with a login/signup prompt, then drops into a simple REPL
that dispatches to the Typer CLI (bp> ...).
"""

from __future__ import annotations

import shlex

from python_scripts.budget_planner.index import app
import os


# Simple ANSI helpers for headings
RESET = "\x1b[0m"
BOLD = "\x1b[1m"
CYAN = "\x1b[36m"
RED = "\x1b[31m"


GUIDE_BODY = """
- signup         Create an account
- login          Sign in
- add-txn        Add a transaction
- list-txns      Show recent transactions
- set-goal       Set a monthly goal
- list-goals     Show your goals
- budget-status  Compare goals vs spend
- summary        Totals by category
- whoami         Show your account info
- logout         Sign out
- exit           Leave the terminal
- menu           Show this help again
"""

GUIDE_EXAMPLES = """
- add-txn --email you@example.com --date 2025-10-30 --category groceries --amount 12.50 --note "Lunch"
- list-txns --email you@example.com --limit 20
- set-goal --email you@example.com --month 2025-10 --category transport --amount 45
- budget-status --email you@example.com --month 2025-10
"""


def print_guide() -> None:
    print(f"{BOLD}Welcome!{RESET}")
    sess = (os.environ.get("BP_EMAIL") or "").strip()
    role = (os.environ.get("BP_ROLE") or "user").strip()
    if sess:
        print(f"{BOLD}Logged in as:{RESET} {sess} (role: {role})\n")
    else:
        print("")
    print(f"{BOLD}{CYAN}Things you can do:{RESET}")
    print(GUIDE_BODY.rstrip())
    print(f"\n{BOLD}{CYAN}Quick examples (replace with your email):{RESET}")
    print(GUIDE_EXAMPLES.rstrip())


def _dispatch(line: str) -> None:
    """Run the Typer app with the provided argument string."""
    args = shlex.split(line)
    try:
        app(args=args, prog_name="bp", standalone_mode=False)
    except SystemExit:
        # Typer/Click exits normally; suppress to keep REPL running
        pass


def onboarding() -> None:
    """Prompt user to login or sign up; only return after a successful login.

    - After a failed login, do not show the guide; print a retry hint.
    - After signup, ask the user to run 'login' next.
    """
    while True:
        try:
            choice = input("Start by typing 'login' or 'signup' [login/signup]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("")
            return

        if choice in {"login", "l"}:
            _dispatch("login")
            if (os.environ.get("BP_EMAIL") or "").strip():
                # Logged in; proceed to guide
                return
            # Login failed: show concise retry hint and loop again
            print(f"{RED}Login failed. Try again or type 'signup' to create an account.{RESET}")
            continue

        if choice in {"signup", "s"}:
            _dispatch("signup")
            # Ask user to login explicitly after signup
            print("Now type 'login' to sign in.")
            continue

        print("Please enter 'login' or 'signup'.")


def main() -> None:
    """Interactive loop after onboarding."""
    onboarding()
    print_guide()
    print("\nBudget Planner - interactive mode")
    print("Type a command (or 'help --help', 'exit').\n")

    while True:
        try:
            line = input("bp> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("")
            break

        if not line:
            continue
        if line.lower() in {"exit", "quit"}:
            break
        if line.lower() in {"menu", "guide", "helpme"}:
            print_guide()
            continue

        _dispatch(line)


if __name__ == "__main__":
    main()
