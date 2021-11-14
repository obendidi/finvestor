from typing import Dict, Tuple

import pandas as pd

from finvestor.etoro.schemas import (
    EtoroAccountStatement,
    EtoroAccountSummary,
    EtoroFinancialSummary,
)
from finvestor.etoro.utils import ETORO_DATETIME_FORMAT


def parse_etoro_account_statement(
    etoro_account_statement_sheets: Dict[str, pd.DataFrame],
) -> EtoroAccountStatement:
    """Parse an etoro account statement sheets loaded using pd.read_excel(...).

    Args:
        etoro_account_statement_sheets (Dict[str, pd.DataFrame]): Dict with sheets
            ass pandas dataframe, and sheet names as keys

    Returns:
        EtoroAccountStatement
    """

    closed_positions_df = pre_process_closed_positions_df(
        etoro_account_statement_sheets["Closed Positions"]
    )
    (
        fees_df,
        deposits_df,
        withdrawals_df,
        account_activity_open_positions_df,
        account_activity_closed_positions_df,
    ) = pre_process_account_activity_df(
        etoro_account_statement_sheets["Account Activity"]
    )

    assert len(closed_positions_df) == len(
        account_activity_closed_positions_df
    ), "Invalid or corrupt data."

    all_closed = closed_positions_df.merge(
        account_activity_closed_positions_df, on="position_id"
    )

    transaction = account_activity_open_positions_df.merge(
        all_closed.drop(
            columns=["amount", "date", "invested", "realized_equity", "open_date"],
            errors="ignore",
        ),
        on=("position_id", "details"),
        how="left",
        suffixes=("_open", "_close"),
    )
    transaction[["ticker", "currency"]] = transaction["details"].str.split(
        "/", n=1, expand=True
    )
    transaction = transaction.drop(columns=["details"], errors="ignore")
    ordered_columns = list(transaction.columns[-2:]) + list(transaction.columns[:-2])
    transaction = transaction[ordered_columns]
    transaction["position_id"] = transaction["position_id"].astype("int64")
    transaction["open_date"] = pd.to_datetime(
        transaction["open_date"], format=ETORO_DATETIME_FORMAT, utc=True
    )
    transaction["close_date"] = pd.to_datetime(
        transaction["close_date"], format=ETORO_DATETIME_FORMAT, utc=True
    )

    return EtoroAccountStatement(
        account_summary=parse_account_summary(
            etoro_account_statement_sheets["Account Summary"]
        ),
        financial_summary=parse_financial_summary(
            etoro_account_statement_sheets["Financial Summary"]
        ),
        transactions=transaction,
        fees=fees_df,
        deposits=deposits_df,
        withdrawals=withdrawals_df,
    )


def parse_account_summary(df: pd.DataFrame) -> EtoroAccountSummary:
    """Parse the account summary object from pandas dataframe.

    Args:
        df: pandas dataframe of 'Account Summary' sheet loaded from etoro account
            statement xlsx

    Returns:
        EtoroAccountSummary
    """
    # apply some preprocessing
    df = (
        df.melt(id_vars=["Details"])
        .drop("variable", axis=1)
        .dropna()
        .drop(df.index[[0, 8, 20]])
    )
    return EtoroAccountSummary(**dict(zip(df.Details, df.value)))


def parse_financial_summary(df: pd.DataFrame) -> EtoroFinancialSummary:
    """Load the financial summary object from pandas dataframe.

    Args:
        df: pandas dataframe of 'Financial Summary' sheet loaded from etoro account
            statement xlsx

    Returns:
        EtoroFinancialSummary
    """
    # apply some preprocessing
    df = df.drop("Tax\nRate", axis=1).dropna()
    return EtoroFinancialSummary(**dict(zip(df.Name, df["Amount\nin USD"])))


def pre_process_account_activity_df(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Pre-process the account activity sheet from etoro account statement.

    -> Drop the column 'NWA', no information about it yet.
    -> Transform column names to lower string and replace spaces with '_'
    -> Split dataframe into:
        - fees dataframe
        - deposits dataframe
        - withdrawals dataframe
        - open positions dataframe
        - closed positions dataframe
    -> Convert all values of column 'type' to upper case (Buy -> BUY, Sell -> SELL)

    Args:
        df: The account activity dataframe.

    Returns:
        Tuple[fees_df, deposits_df, withdrawals_df, open_df, closed_df]
    """

    # drop NWA clumn: don't what it means :)
    df = df.drop(columns=["NWA"], errors="ignore")
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # extract all gees into a seprate dataframe
    fees_df = df[(df.type == "Adjustment") | (df.type == "Rollover Fee")]

    deposits_df = df[df.type == "Deposit"]
    deposits_df = deposits_df.drop(columns=["type", "position_id"], errors="ignore")

    withdrawals_df = df[
        (df.type == "Withdraw Fee")
        | (df.type == "Withdraw Request")
        | (df.type == "Withdraw Fee Cancelled")
        | (df.type == "Withdraw Request Cancelled")
    ]
    withdrawals_df = withdrawals_df.drop(
        columns=["details", "position_id"], errors="ignore"
    )

    open_df = df[df.type == "Open Position"]
    open_df = open_df.drop(columns=["type", "realized_equity_change"], errors="ignore")
    open_df = open_df.rename(columns={"amount": "invested", "date": "open_date"})

    closed_df = df[df.type == "Profit/Loss of Trade"]
    closed_df = closed_df.drop(columns=["type"], errors="ignore")
    return fees_df, deposits_df, withdrawals_df, open_df, closed_df


def pre_process_closed_positions_df(df: pd.DataFrame) -> pd.DataFrame:
    """Pre-process the closed positions sheet from etoro account statement.

    -> Split the 'Action' column into 'type' (Buy or Sell) and 'name'
        (full name of the company)
    -> Drop the columns: 'Copied From', 'Type', 'Notes', 'Action'
    -> Transform column names to lower string and replace spaces with '_'
    -> rename some columns:
        - stop_lose_rate: stop_loss_rate
        - amount: invested
        - isin: ISIN
    -> Convert all values of column 'type' to upper case (Buy -> BUY, Sell -> SELL)

    Args:
        df: The closed positions sheet as a pandas dataframe.

    Returns:
        pd.DataFrame
    """
    # split string by first space, to get type of transacation (BUY/SELL) and
    # company name
    df[["type", "name"]] = df["Action"].str.split(" ", n=1, expand=True)

    # drop unnecessary columns
    df = df.drop(columns=["Copied From", "Type", "Notes", "Action"], errors="ignore")

    # convert column names to lower case and replace spaces with '_'
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # rename some columns to be clearer or fix typos
    df = df.rename(
        columns={
            "stop_lose_rate": "stop_loss_rate",
            "amount": "invested",
            "isin": "ISIN",
        }
    )

    # convert column 'type' to uper case (Buy -> BUY, Sell -> SELL)
    df["type"] = df["type"].str.upper()

    return df
