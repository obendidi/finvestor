from finvestor.etoro.parsers import (
    parse_account_summary,
    parse_financial_summary,
    pre_process_closed_positions_df,
    pre_process_account_activity_df,
)
from finvestor.etoro.schemas import EtoroAccountSummary, EtoroFinancialSummary


def test_parse_account_summary(snapshot, etoro_account_summary_df):
    parsed = parse_account_summary(etoro_account_summary_df)
    assert isinstance(parsed, EtoroAccountSummary)
    assert parsed == snapshot


def test_parse_financial_summary(snapshot, etoro_financial_summary_df):
    parsed = parse_financial_summary(etoro_financial_summary_df)
    assert isinstance(parsed, EtoroFinancialSummary)
    assert parsed == snapshot


def test_pre_process_closed_positions_df(snapshot, etoro_closed_positions_df):
    df = pre_process_closed_positions_df(etoro_closed_positions_df)
    assert df.to_dict() == snapshot


def test_pre_process_account_activity_df(snapshot, etoro_account_activity_df):
    fees_df, deposits_df, open_df, closed_df = pre_process_account_activity_df(
        etoro_account_activity_df
    )
    assert fees_df.to_dict() == snapshot(name="fees")
    assert deposits_df.to_dict() == snapshot(name="deposits")
    assert open_df.to_dict() == snapshot(name="open_positions")
    assert closed_df.to_dict() == snapshot(name="closed_positions")
