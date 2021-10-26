import pandas as pd

from finvestor.etoro.schemas import (
    EtoroAccountStatement,
    EtoroAccountSummary,
    EtoroFinancialSummary,
)


def load_etoro_account_statement(filepath: str) -> EtoroAccountStatement:
    """Load an etoro account statement xlsx file.

    Args:
        filepath (str): path to xlsx file.
        can also be: bytes, ExcelFile, xlrd.Book, path object, or file-like object

    Returns:
        EtoroAccountStatement
    """
    all_sheets = pd.read_excel(filepath, sheet_name=None)
    return EtoroAccountStatement(
        account_summary=parse_account_summary(all_sheets["Account Summary"]),
        financial_summary=parse_financial_summary(all_sheets["Financial Summary"]),
        closed_positions=all_sheets["Closed Positions"],
        account_activity=all_sheets["Account Activity"],
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
