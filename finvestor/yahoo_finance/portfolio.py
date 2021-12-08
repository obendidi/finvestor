import functools
import logging
import typing as tp

import attr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from httpx import AsyncClient
from pypfopt import HRPOpt
from pypfopt.efficient_frontier import EfficientCVaR, EfficientFrontier
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from tabulate import tabulate

from finvestor.schemas.transaction import Transactions
from finvestor.yahoo_finance.api.bars import get_yahoo_finance_bars
from finvestor.yahoo_finance.utils import parse_yf_csv_quotes

__all__ = "YFPortfolio"

logger = logging.getLogger(__name__)


@attr.s
class YFPortfolio:
    transactions: Transactions = attr.ib(kw_only=True)

    @classmethod
    async def load(cls, filepath: str, *, client: AsyncClient) -> "YFPortfolio":
        data = await parse_yf_csv_quotes(filepath, client=client)
        records: tp.List[tp.Any] = data.to_dict(orient="records")  # type: ignore
        transactions = Transactions.build(records)
        return cls(transactions=transactions)

    @property
    def df(self):
        return self.transactions.df

    @property
    def invested(self) -> float:
        return self.df["amount"].sum()

    @property
    def tickers(self) -> tp.List[str]:
        return list(self.df["asset_ticker"].unique())

    @property
    def weights(self) -> tp.Dict[str, float]:
        data = self.amount_per_asset(key="ticker")
        weights = {ticker: amount / self.invested for ticker, amount in data.items()}
        # Dicts preserve insertion order in Python 3.7+.
        # But it's an implementation detail:
        # https://stackoverflow.com/questions/39980323/are-dictionaries-ordered-in-python-3-6
        return {
            k: v
            for k, v in sorted(weights.items(), key=lambda item: item[1], reverse=True)
        }

    def amount_per_asset(
        self,
        key: tp.Literal[
            "ticker", "type", "market", "country", "sector", "industry"
        ] = "ticker",
    ) -> tp.Dict[str, float]:
        return self.df.groupby(f"asset_{key}", dropna=False).amount.sum().to_dict()

    def plot(self):
        # create a figure with 6 subplots
        fig, axs = plt.subplots(2, 3)
        fig.suptitle("Portfolio repartition:")
        keys = ["ticker", "type", "market", "country", "sector", "industry"]
        for k, key in enumerate(keys):
            i = int(k / 3)
            j = k % 3
            stat = self.amount_per_asset(key=key)
            data = list(stat.values())
            labels = list(stat.keys())
            autopct = (
                lambda pct: f"{pct:.1f}%\n({np.round(pct / 100.0 * np.sum(data)):.1f}$)"
            )
            axs[i, j].set_title(f"Assets per {key}")

            axs[i, j].pie(
                data,
                labels=labels,
                autopct=autopct,
                textprops=dict(color="w"),
            )

        plt.show()

    async def summary(self, *, client: AsyncClient):
        # pull last 5 years of data for all stocks in list
        logger.info(
            f"Loading 5 years historical data for {len(self.tickers)} tickers in "
            "portfolio."
        )
        data = await get_yahoo_finance_bars(
            self.tickers, client=client, interval="1d", period="5y"
        )
        dataframes: tp.List[pd.DataFrame] = []
        for ticker, bars in data.items():
            df = bars.df[["close"]].rename(columns={"close": ticker})
            df.index = df.index.strftime("%Y-%m-%d")
            dataframes.append(df)

        prices = functools.reduce(
            lambda left, right: pd.merge(left, right, on=["date"], how="outer"),
            dataframes,
        )
        prices = prices.sort_index()

        # Mean Variance Optimization
        expected_returns = mean_historical_return(prices)
        cov_matrix = CovarianceShrinkage(prices).ledoit_wolf()
        ef = EfficientFrontier(expected_returns, cov_matrix)
        ef.max_sharpe()
        var_weights = ef.clean_weights()
        expected_return, volatility, Sharpe_ratio = ef.portfolio_performance()
        logger.info("Mean Variance Optimization:")
        logger.info(f"\tExpected annual return: {expected_return*100:.2f}%")
        logger.info(f"\tAnnual volatility: {volatility*100:.2f}%")
        logger.info(f"\tSharpe ratio: {Sharpe_ratio:.2f}")

        # Hierarchical Risk Parity (HRP)
        returns = prices.pct_change().dropna()
        hrp = HRPOpt(returns)
        hrp_weights = hrp.optimize()
        expected_return, volatility, Sharpe_ratio = hrp.portfolio_performance()
        logger.info("Hierarchical Risk Parity:")
        logger.info(f"\tExpected annual return: {expected_return*100:.2f}%")
        logger.info(f"\tAnnual volatility: {volatility*100:.2f}%")
        logger.info(f"\tSharpe ratio: {Sharpe_ratio:.2f}")

        # Mean Conditional Value at Risk (mCVAR)
        ef_cvar = EfficientCVaR(expected_returns, prices.cov())
        ef_cvar.min_cvar(market_neutral=False)
        cvar_weights = ef_cvar.clean_weights()
        expected_return, cvar = ef_cvar.portfolio_performance()
        logger.info("Mean Conditional Value at Risk:")
        logger.info(f"\tExpected annual return: {expected_return*100:.2f}%")
        logger.info(f"\tConditional value at risk: {cvar*100:.2f}%")

        table = pd.DataFrame(
            [self.weights, var_weights, hrp_weights, cvar_weights]
        ).transpose()
        table.columns = ["current", "VAR", "HRP", "CVAR"]
        table[table.select_dtypes(include=["number"]).columns] *= 3
        total = table.sum()
        total.name = "Total"
        table = table.append(total.transpose())

        logger.info(tabulate(table, headers=table.columns, tablefmt="fancy_grid"))
