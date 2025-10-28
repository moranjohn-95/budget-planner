import typer


app = typer.Typer(no_args_is_help=True, help="Budget Planner CLI")


@app.callback(invoke_without_command=True)
def _root(ctx: typer.Context) -> None:
    """Run when no subcommand is provided."""
    if ctx.invoked_subcommand is None:
        typer.echo("Budget Planner CLI is ready. Use --help or a subcommand.")


@app.command("hello")
def hello() -> None:
    """Print a confirmation that the CLI is reachable."""
    typer.echo("Budget Planner is ready!")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
