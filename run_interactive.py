"""
Heroku entrypoint for the browser terminal.
Starts with a login/signup prompt, then drops into a simple REPL
that dispatches to the Typer CLI (bp> ...).
"""

from __future__ import annotations

import shlex

from python_scripts.budget_planner.index import app
import os
import difflib


# Simple ANSI helpers for headings
RESET = "\x1b[0m"
BOLD = "\x1b[1m"
CYAN = "\x1b[36m"
RED = "\x1b[31m"


GUIDE_BODY_BASE = """
- signup         Create an account
- login          Sign in
- add-txn        Add a transaction
- list-txns      Show recent transactions
- sum-month      Show monthly total
- set-goal       Set a monthly goal
- list-goals     Show your goals
- budget-status  Compare goals vs spend
- summary        Totals by category
- whoami         Show your account info
- change-password Change your password
- logout         Sign out
- exit           Leave the terminal
- menu           Show this help again
"""

# Shown only for editors
GUIDE_BODY_EDITOR = """
- list-users     List all users
- set-role       (editor) change a user's role
"""

GUIDE_EXAMPLES = """
- add-txn --date 2025-10-30 --category groceries --amount 12.50 --note "Lunch"
- list-txns --limit 20
- set-goal --month 2025-10 --category transport --amount 45
- budget-status --month 2025-10
"""

# Extra examples editors can run against other users
# (session-aware, with --email overrides)
GUIDE_EXAMPLES_EDITOR = """
- whoami --email user@example.com
- list-txns --email user@example.com --limit 10
- set-goal --email user@example.com --month 2025-10 --category groceries
  --amount 200
- budget-status --email user@example.com --month 2025-10
"""


def print_guide() -> None:
    # Show a simple banner and who is logged in.
    print(f"{BOLD}Welcome!{RESET}")
    sess = (os.environ.get("BP_EMAIL") or "").strip()
    role = (os.environ.get("BP_ROLE") or "user").strip()
    if sess:
        print(f"{BOLD}Logged in as:{RESET} {sess} (role: {role})\n")
    else:
        print("")
    title = "Things you can do"
    if role == "editor":
        title = f"{title} [Editor]"
    print(f"{BOLD}{CYAN}{title}:{RESET}")
    if role == "editor":
        print(GUIDE_BODY_BASE.rstrip())
        print(f"\n{BOLD}{CYAN}Editor commands:{RESET}")
        print(GUIDE_BODY_EDITOR.rstrip())
    else:
        print(GUIDE_BODY_BASE.rstrip())

    # Note: examples for regular users are session-bound (no --email needed).
    if role == "editor":
        print(f"\n{BOLD}{CYAN}Editor examples (per-user filters):{RESET}")
        print(GUIDE_EXAMPLES_EDITOR.rstrip())


def _dispatch(line: str) -> None:
    """Run the Typer app with the provided argument string.

    Adds a blank line before and after each command to improve readability
    when running multiple commands in the same session.
    """
    args = shlex.split(line)
    # Add an empty line so consecutive commands are easier to read.
    if line.strip():
        print("")
    try:
        app(args=args, prog_name="bp", standalone_mode=False)
    except SystemExit:
        # Typer/Click exits normally; suppress to keep REPL running
        pass
    except Exception as exc:
        # Try to suggest a command if the first token looks like a typo
        name = (args[0].strip().lower() if args else "")
        try:
            names = []
            try:
            names = [
                c.name
                for c in getattr(app, "registered_commands", [])
                if getattr(c, "name", None)
            ]
            except Exception:
                pass
            if not names:
                try:
                    names = list(getattr(app, "_command").commands.keys())
                except Exception:
                    names = []
            suggestion = difflib.get_close_matches(
                name,
                names,
                n=1,
                cutoff=0.6,
            )
        except Exception:
            suggestion = []

        if name and suggestion:
            print(
                f"{RED}Unknown command '{name}'. "
                f"Did you mean '{suggestion[0]}'?{RESET}"
            )
        else:
            # Generic friendly error
            print(f"{RED}Command error: {exc}{RESET}")
    finally:
        # Add a trailing empty line after each command.
        print("")


def onboarding() -> None:
    """Prompt user to login or sign up; only return after a successful login.

    - After a failed login, do not show the guide; print a retry hint.
    - After signup, ask the user to run 'login' next.
    """
    while True:
        try:
            choice = input(
                "Start by typing 'login' or 'signup' [login/signup]: "
            ).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("")
            return

        if choice in {"login", "l"}:
            _dispatch("login")
            if (os.environ.get("BP_EMAIL") or "").strip():
                # Logged in; proceed to guide
                return
            # Login failed: show concise retry hint and loop again
            print(
                f"{RED}Login failed. Try again or type 'signup' "
                f"to create an account.{RESET}"
            )
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
    print("Type a command (or 'help'/'--help', 'exit').\n")

    while True:
        try:
            line = input("bp> ").strip()
        except (EOFError, KeyboardInterrupt):
            # Leave the terminal if the user presses Ctrl+C or closes input.
            print("\nGoodbye!\n")
            break

        if not line:
            continue
        if line.lower() in {"exit", "quit"}:
            print("Goodbye!\n")
            break
        # Support `help` and `help <command>` like many CLIs
        try:
            parts = shlex.split(line)
        except Exception:
            parts = [line]
        if parts and parts[0].lower() in {"help", "-h", "h"}:
            if len(parts) == 1:
                _dispatch("--help")
            else:
                _dispatch(" ".join(parts[1:] + ["--help"]))
            continue
        if line.lower() in {"menu", "guide", "helpme"}:
            print_guide()
            continue

        _dispatch(line)


if __name__ == "__main__":
    main()
