from typing import Optional

import typer

from finvestor import __version__
from finvestor.etoro.cli import app as etoro_app

app = typer.Typer(
    help="CLI for managing your finvestor applications.", no_args_is_help=True
)

app.add_typer(etoro_app, name="etoro", invoke_without_command=True)


def version_callback(value: bool):
    if value:
        typer.echo(f"Finvestor version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    _version: Optional[bool] = typer.Option(
        None, "-v", "--version", callback=version_callback
    )
):
    pass
