import os
from typing import Dict, Union

import pandas as pd
import pytest
from syrupy.extensions.amber import AmberSnapshotExtension


class EtoroParsersSnapshotExt(AmberSnapshotExtension):
    def get_snapshot_name(self, *, index: Union[str, int] = 0) -> str:
        """Get the snapshot name for the assertion index in a test location"""
        assert isinstance(index, str)
        return index


@pytest.fixture
def etoro_parsers_snapshot(snapshot):
    return snapshot.use_extension(EtoroParsersSnapshotExt)


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
