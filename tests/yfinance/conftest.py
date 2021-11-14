import os
from typing import Union

import pytest
from syrupy.extensions.amber import AmberSnapshotExtension


class QuoteSummarySnapshotExt(AmberSnapshotExtension):
    def get_snapshot_name(self, *, index: Union[str, int] = 0) -> str:
        """Get the snapshot name for the assertion index in a test location"""
        return "result_parse_quote_summary"

    def get_location(self, *, index: Union[str, int]) -> str:
        """Returns full location where snapshot data is stored."""
        return os.path.join(
            self._dirname, f"parsed_quote_summary.{self._file_extension}"
        )


@pytest.fixture
def quote_summary_snapshot(snapshot):
    return snapshot.use_extension(QuoteSummarySnapshotExt)


@pytest.fixture(scope="session")
def yf_scrape_response(data_dir) -> str:
    with open(os.path.join(data_dir, "yf_scrape_response.html"), "r") as file:
        return file.read()
