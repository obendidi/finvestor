import logging
from pathlib import Path

import anyio
import typer
from httpx import AsyncClient

from finvestor.yahoo_finance.portfolio import YFPortfolio

app = typer.Typer(help="Yahoo-finance cli helper.")
logger = logging.getLogger(__name__)


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
        help="Path to yahoo-finance exported quotes csv.",
    )
):
    async def _main():
        assert str(filepath).lower().endswith(".csv"), "Only csv files are supported."
        logger.info(f"Loading yahoo-finance portfolio from: '{filepath}'")

        async with AsyncClient() as client:
            portfolio = await YFPortfolio.load(str(filepath), client=client)
            await portfolio.summary(client=client)
        # logger.info(f"Portfolio:\n{portfolio.amount_per_asset(key='type')}")

    anyio.run(_main)
