from typing import Optional

import typer
from . import auth

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
) -> None:
    """Create a new user record in Google Sheets."""
    try:
        ok = auth.signup(email=email, password=password)
        if ok:
            typer.secho("Signup successful", fg=typer.colors.GREEN)
        else:
            typer.secho(
                "Signup failed (maybe email exists?)",
                fg=typer.colors.RED,
            )
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


def main() -> None:
    """Entrypoint for the Typer app."""
    app()


if __name__ == "__main__":
    main()
