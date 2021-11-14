import logging
from datetime import datetime

import pandas as pd
import pytz

from finvestor.alpaca import AlpacaClient

ETORO_DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"

logger = logging.getLogger(__name__)


def parse_etoro_datetime(etoro_datetime: str) -> datetime:
    """Parse an etoro datetime, to python datetime object with UTC timezone.

    Args:
        etoro_datetime: Etoro datetime string.

    Returns:
        datetime: dateime object with utc timezone
    """
    date = datetime.strptime(etoro_datetime, ETORO_DATETIME_FORMAT)
    return pytz.utc.localize(date)


def fill_missing_company_name(df: pd.DataFrame, client: AlpacaClient) -> pd.DataFrame:
    if not df["name"].isnull().values.any():
        return df
    valid_idx = df["name"].first_valid_index()
    if valid_idx is None:
        ticker = df["ticker"].iloc[0]
        try:
            name = client.get_asset(ticker).name
        except Exception as error:
            logger.error(error)
            return df
    else:
        name = df["name"].loc[valid_idx]
    df["name"] = df["name"].fillna(value=name)
    return df


if __name__ == "__main__":
    from finvestor.etoro.parsers import parse_etoro_account_statement

    filepath = "data/etoro-account-statement-12-1-2019-10-24-2021.xlsx"
    client = AlpacaClient()

    sheets = pd.read_excel(filepath, sheet_name=None)
    statement = parse_etoro_account_statement(sheets)
    df = statement.transactions[["ticker", "name"]]

    df = statement.transactions.groupby(["ticker"]).apply(
        lambda grp: fill_missing_company_name(grp, client)
    )
    print(df[["ticker", "name", "ISIN"]].tail(30))
