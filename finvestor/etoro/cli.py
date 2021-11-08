from pathlib import Path
import os
import typer

from finvestor.etoro.io import load_etoro_account_statement
from finvestor.etoro.portfolio import get_deposits_breakdown

app = typer.Typer(help="Load and process an etoro account statement.")


@app.callback()
def main(
    filepath: Path = typer.Option(
        ...,
        "-f",
        "--file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        help="Path to etoro_account_statement.xlsx",
    )
):
    """
    Load and process an etoro account statement.
    """
    typer.secho(
        f"Loading Etoro account statement '{os.path.basename(filepath)}'...",
        fg=typer.colors.BRIGHT_GREEN,
    )
    statement = load_etoro_account_statement(filepath)
    typer.secho(
        f"Loaded Etoro account statement of user '{statement.account_summary.name}' "
        f"from '{statement.account_summary.start_date}' "
        f"to '{statement.account_summary.end_date}'",
        fg=typer.colors.BRIGHT_GREEN,
    )
    get_deposits_breakdown(statement)
