"""
Module entry point for running the Budget Planner CLI as a module.

Usage:
    python -m python_scripts.budget_planner [COMMAND]
"""

from .index import app


def main() -> None:
    app()


if __name__ == "__main__":
    main()
