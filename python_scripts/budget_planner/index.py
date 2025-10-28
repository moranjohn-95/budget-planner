import typer

print(">>> Running index.py from:", __file__)

app = typer.Typer(no_args_is_help=True, help="Budget Planner CLI")


@app.command("hello")
def hello() -> None:
    """Print a simple confirmation that the CLI is reachable."""
    typer.echo("✅ Budget Planner is ready!")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
