import pytest

from finvestor.etoro.parsers import (
    parse_account_summary,
    parse_etoro_account_statement,
    parse_financial_summary,
    pre_process_account_activity_df,
    pre_process_closed_positions_df,
)
from finvestor.etoro.schemas import (
    EtoroAccountStatement,
    EtoroAccountSummary,
    EtoroFinancialSummary,
)


def test_parse_account_summary(etoro_parsers_snapshot, etoro_account_summary_df):
    parsed = parse_account_summary(etoro_account_summary_df)
    assert isinstance(parsed, EtoroAccountSummary)
    assert parsed == etoro_parsers_snapshot(name="parsed_account_summary")


def test_parse_financial_summary(etoro_parsers_snapshot, etoro_financial_summary_df):
    parsed = parse_financial_summary(etoro_financial_summary_df)
    assert isinstance(parsed, EtoroFinancialSummary)
    assert parsed == etoro_parsers_snapshot(name="parsed_financial_summary")


def test_pre_process_closed_positions_df(
    etoro_parsers_snapshot, etoro_closed_positions_df
):
    df = pre_process_closed_positions_df(etoro_closed_positions_df)
    assert df.to_dict() == etoro_parsers_snapshot(
        name="pre_processed_closed_positions_df"
    )


def test_pre_process_account_activity_df(
    etoro_parsers_snapshot, etoro_account_activity_df
):
    (
        fees_df,
        deposits_df,
        withdrawals_df,
        open_df,
        closed_df,
    ) = pre_process_account_activity_df(etoro_account_activity_df)
    assert fees_df.to_dict() == etoro_parsers_snapshot(
        name="pre_processed_account_activity_df_fees"
    )
    assert deposits_df.to_dict() == etoro_parsers_snapshot(
        name="pre_processed_account_activity_df_deposits"
    )
    assert withdrawals_df.to_dict() == etoro_parsers_snapshot(
        name="pre_processed_account_activity_df_withdrawals"
    )
    assert open_df.to_dict() == etoro_parsers_snapshot(
        name="pre_processed_account_activity_df_open_positions"
    )
    assert closed_df.to_dict() == etoro_parsers_snapshot(
        name="pre_processed_account_activity_df_closed_positions"
    )


@pytest.mark.integration
def test_parse_etoro_account_statement(etoro_parsers_snapshot, etoro_account_statement):
    statement = parse_etoro_account_statement(etoro_account_statement)
    assert isinstance(statement, EtoroAccountStatement)

    assert statement.fees.to_dict() == etoro_parsers_snapshot(
        name="pre_processed_account_activity_df_fees"
    )
    assert statement.deposits.to_dict() == etoro_parsers_snapshot(
        name="pre_processed_account_activity_df_deposits"
    )
    assert statement.withdrawals.to_dict() == etoro_parsers_snapshot(
        name="pre_processed_account_activity_df_withdrawals"
    )
    assert statement.account_summary == etoro_parsers_snapshot(
        name="parsed_account_summary"
    )
    assert statement.financial_summary == etoro_parsers_snapshot(
        name="parsed_financial_summary"
    )

    assert statement.transactions.to_dict() == etoro_parsers_snapshot(
        name="parsed_etoro_account_statement_transactions"
    )
