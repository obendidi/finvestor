from typing import Dict

import pandas as pd
import pytest


@pytest.fixture
def etoro_account_summary_df() -> pd.DataFrame:
    raw_data = {
        "Details": {
            0: "Name",
            1: "Name",
            2: "Username",
            3: "Currency",
            4: "Date Created",
            5: "Start Date",
            6: "End Date",
            7: None,
            8: "Account Summary (USD)",
            9: "Beginning Realized Equity",
            10: "Deposits",
            11: "Refunds",
            12: "Credits",
            13: "Adjustments",
            14: "Profit or Loss (Closed positions only)",
            15: "Rollover Fees",
            16: "Withdrawals",
            17: "Withdrawal Fees",
            18: "Ending Realized Equity",
            19: None,
            20: "Unrealized Account Summary*",
            21: "Beginning Unrealized Equity",
            22: "Ending Unrealized Equity",
            23: "*Unrealized Equity value is updated once a day",
            24: None,
            25: "eToro (Euro....",
            26: None,
            27: None,
            28: "Notes:   This report data ......... ",
        },
        "Unnamed: 1": {
            0: "Totals",
            1: "John Doe",
            2: "apes_together_strong",
            3: "USD",
            4: "01/01/1999 10:28:13",
            5: "01/01/1998 00:00:00",
            6: "01/01/1999 23:59:59",
            7: None,
            8: "Totals",
            9: "0.00",
            10: "123456.789 ",
            11: "0.00",
            12: "0.00",
            13: "9.87",
            14: "987654.321 ",
            15: "1.17",
            16: "10000.00",
            17: "30.00",
            18: "1101079.94 ",
            19: None,
            20: "Totals",
            21: "0.00",
            22: "1103079.94 ",
            23: None,
            24: None,
            25: None,
            26: None,
            27: None,
            28: None,
        },
    }
    return pd.DataFrame(raw_data)


@pytest.fixture
def etoro_financial_summary_df() -> pd.DataFrame:
    raw_data = {
        "Name": {
            0: "CFDs (Profit or Loss)",
            1: "Crypto (Profit or Loss)",
            2: "Stocks (Profit or Loss)",
            3: "ETFs (Profit or Loss)",
            4: "Stock Dividends (Profit)",
            5: "CFD Dividends (Profit or Loss)",
            6: "Income from Refunds",
            7: "Commissions (spread) on CFDs",
            8: "Commissions (spread) on Crypto",
            9: "Commissions (spread) on Stocks",
            10: "Commissions (spread) on ETFs",
            11: "Fees",
        },
        "Amount\nin USD": {
            0: 7654.0,
            1: 8.8,
            2: 98000.321,
            3: 0.0,
            4: 6.49,
            5: 3.45,
            6: 2.6,
            7: 60.87,
            8: 2.01,
            9: 0.04,
            10: 0.0,
            11: 8.77,
        },
        "Tax\nRate": {
            0: 0.0,
            1: 0.0,
            2: 0.0,
            3: 0.0,
            4: 0.0,
            5: 0.0,
            6: 0.0,
            7: 0.0,
            8: 0.0,
            9: 0.0,
            10: 0.0,
            11: 0.0,
        },
    }
    return pd.DataFrame(raw_data)


@pytest.fixture
def etoro_account_statement_sheets(
    etoro_account_summary_df: pd.DataFrame,
    etoro_fiNonecial_summary_df: pd.DataFrame,
) -> Dict[str, pd.DataFrame]:
    return {
        "Account Summary": etoro_account_summary_df,
        "FiNonecial Summary": etoro_fiNonecial_summary_df,
    }
