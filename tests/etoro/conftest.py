import os
from typing import Dict

import pandas as pd
import pytest


@pytest.fixture(scope="session")
def etoro_account_statement(data_dir) -> Dict[str, pd.DataFrame]:
    fake_etoro_data_path = os.path.join(data_dir, "fake-etoro-account-statement.xlsx")
    return pd.read_excel(fake_etoro_data_path, sheet_name=None)


@pytest.fixture
def etoro_account_summary_df(
    etoro_account_statement: Dict[str, pd.DataFrame]
) -> pd.DataFrame:
    return etoro_account_statement["Account Summary"]


@pytest.fixture
def etoro_financial_summary_df(
    etoro_account_statement: Dict[str, pd.DataFrame]
) -> pd.DataFrame:
    return etoro_account_statement["Financial Summary"]


@pytest.fixture
def etoro_closed_positions_df(
    etoro_account_statement: Dict[str, pd.DataFrame]
) -> pd.DataFrame:
    return etoro_account_statement["Closed Positions"]


@pytest.fixture
def etoro_account_activity_df(
    etoro_account_statement: Dict[str, pd.DataFrame]
) -> pd.DataFrame:
    return etoro_account_statement["Account Activity"]
