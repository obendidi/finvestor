import asyncio

import matplotlib.pyplot as plt
from httpx import AsyncClient
from ta.momentum import RSIIndicator

from finvestor.yahoo_finance.api.bars import get_yahoo_finance_ticker_bars

ticker = "TSLA"


async def main():
    async with AsyncClient() as client:
        bars = await get_yahoo_finance_ticker_bars(
            ticker, client=client, interval="1d", period="1y"
        )
        print(bars.df)
    rsi = RSIIndicator(bars.df["close"])
    print(rsi)
    print(rsi.rsi())
    rsi.rsi().plot()
    plt.show()


asyncio.run(main())
