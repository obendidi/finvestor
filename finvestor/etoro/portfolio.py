import logging

from finvestor.etoro.schemas import EtoroAccountStatement

logger = logging.getLogger(__name__)


def get_deposits_breakdown(statement: EtoroAccountStatement):
    summary_deposit = statement.account_summary.deposits
    deposits_df = statement.account_activity.loc[
        statement.account_activity["Type"] == "Deposit"
    ].filter(items=["Date", "Details", "Amount"])
    print(deposits_df)
    print(summary_deposit)
    print(deposits_df["Amount"].sum())
