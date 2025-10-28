import typer


app = typer.Typer(no_args_is_help=True, help="Budget Planner")


@app.command()
def hello() -> None:
    """
    Print a simple confirmation that the CLI is reachable.
    """
    typer.echo("Budget Planner CLI is ready!")


if __name__ == "__main__":
    app()
