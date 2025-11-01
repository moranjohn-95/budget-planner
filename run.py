"""
Heroku entrypoint for CI terminal (80x24).
Tiny REPL that forwards commands to the Typer app.
"""

from __future__ import annotations

import shlex

from python_scripts.budget_planner.index import app


def _dispatch(line: str) -> None:
    """
    Read a command line (e.g., 'signup') and run the Typer app
    with those arguments. Keeps the line length <80 chars.
    """
    args = shlex.split(line)
    try:
        app(
            args=args,
            prog_name="bp",
            standalone_mode=False,
        )
    except SystemExit:
        pass


def main() -> None:
    """
    Loop for interactive terminal.
    Type commands like below:
      signup
      login
      add-txn
      list-txns
      set-goal
      budget-status
      whoami
      logout
      help --help
    """
    print("Budget Planner — interactive mode")
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
