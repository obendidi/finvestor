import os
from pathlib import Path

import pandas as pd
import typer

from finvestor.etoro.parsers import parse_etoro_account_statement

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
    sheets = pd.read_excel(filepath, sheet_name=None)
    statement = parse_etoro_account_statement(sheets)
    typer.secho(
        f"Loaded Etoro account statement of user '{statement.account_summary.name}' "
        f"from '{statement.account_summary.start_date}' "
        f"to '{statement.account_summary.end_date}'",
        fg=typer.colors.BRIGHT_GREEN,
    )
    typer.secho(
        statement.transactions[
            [
                "ticker",
                "currency",
                "name",
                "open_date",
                "close_date",
                "open_rate",
                "close_rate",
            ]
        ].tail(50),
        fg=typer.colors.CYAN,
    )
