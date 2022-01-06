import logging
import typing as tp
from enum import Enum

import anyio
import typer
from httpx import AsyncClient

from finvestor.yahoo_finance.utils import AutoValidInterval, ValidPeriod
from finvestor.yahoo_finance.bars import get_yahoo_finance_bars

from finvestor.utils.logger import setup_logging

logger = logging.getLogger("finvestor.yahoo_finance.cli")
app = typer.Typer(
    help="yahoo financial data provider.",
    no_args_is_help=True,
    invoke_without_command=True,
)


class YFEventsEnum(str, Enum):
    div = "div"
    splits = "splits"
    div_splits = "div,splits"


YFPeriodEnum = Enum(  # type: ignore
    "YFPeriodEnum",
    {f"period{i}": str(period) for i, period in enumerate(tp.get_args(ValidPeriod))},
)

YFIntervalEnum = Enum(  # type: ignore
    "YFIntervalEnum",
    {
        f"period{i+j}": str(interval)
        for i, part in enumerate(tp.get_args(AutoValidInterval))
        for j, interval in enumerate(tp.get_args(part))
    },
)


@app.callback()
def main(
    tickers: tp.List[str] = typer.Option(..., "-t", "--ticker"),
    interval: YFIntervalEnum = typer.Option("auto", "-i", "--interval"),
    period: YFPeriodEnum = typer.Option("1d", "-p", "--period"),
    prepost: bool = False,
    events: YFEventsEnum = typer.Option("div,splits"),
):
    """
    Load and process an etoro account statement.
    """

    async def _worker():
        async with AsyncClient() as client:
            return await get_yahoo_finance_bars(
                tickers,
                client=client,
                interval=interval.value,
                period=period.value,
                include_prepost=prepost,
                events=events.value,
            )

    all_bars = anyio.run(_worker)
    for ticker, bars in all_bars.items():
        logger.info(f"=> '{ticker}' bars for a period of '{period.value}': ")
        logger.info(bars.df)


if __name__ == "__main__":
    setup_logging()
    app()
