"""
Heroku entrypoint for the browser terminal.
Starts with a login/signup prompt, then drops into a simple REPL
that dispatches to the Typer CLI (bp> ...).
"""

from __future__ import annotations

import shlex

from python_scripts.budget_planner.index import app


def _dispatch(line: str) -> None:
    """Run the Typer app with the provided argument string."""
    args = shlex.split(line)
    try:
        app(args=args, prog_name="bp", standalone_mode=False)
    except SystemExit:
        # Typer/Click exits normally; suppress to keep REPL running
        pass


def onboarding() -> None:
    """Prompt user to login or sign up once at startup."""
    print("Welcome to Budget Planner")
    while True:
        try:
            choice = input("Start by typing 'login' or 'signup' [login/signup]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("")
            return
        if choice in {"login", "l"}:
            _dispatch("login")
            return
        if choice in {"signup", "s"}:
            _dispatch("signup")
            return
        print("Please enter 'login' or 'signup'.")


def main() -> None:
    """Interactive loop after onboarding."""
    onboarding()
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

        _dispatch(line)


if __name__ == "__main__":
    main()

