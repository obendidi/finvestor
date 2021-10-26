from datetime import datetime

import pandas as pd
from pydantic import BaseModel, Field, validator


class EtoroAccountSummary(BaseModel):
    name: str = Field(..., alias="Name")
    username: str = Field(..., alias="Username")
    currency: str = Field(..., alias="Currency")
    created_at: datetime = Field(..., alias="Date Created")
    start_date: datetime = Field(..., alias="Start Date")
    end_date: datetime = Field(..., alias="End Date")

    @validator("created_at", "start_date", "end_date", pre=True)
    def parse_dates(cls, value):
        return datetime.strptime(value, "%d/%m/%Y %H:%M:%S")

    initial_realised_equity: float = Field(..., alias="Beginning Realized Equity")
    initial_unrealised_equity: float = Field(..., alias="Beginning Unrealized Equity")
    deposits: float = Field(..., alias="Deposits")
    refunds: float = Field(..., alias="Refunds")
    credits: float = Field(..., alias="Credits")
    adjustments: float = Field(..., alias="Adjustments")
    withdrawals: float = Field(..., alias="Withdrawals")
    realised_profit_loss: float = Field(
        ..., alias="Profit or Loss (Closed positions only)"
    )
    rollover_fees: float = Field(..., alias="Rollover Fees")
    withdrawal_fees: float = Field(..., alias="Withdrawal Fees")
    final_realised_equity: float = Field(..., alias="Ending Realized Equity")
    final_unrealised_equity: float = Field(..., alias="Ending Unrealized Equity")


class EtoroFinancialSummary(BaseModel):
    cfd_profit_loss: float = Field(..., alias="CFDs (Profit or Loss)")
    crypto_profit_loss: float = Field(..., alias="Crypto (Profit or Loss)")
    stocks_profit_loss: float = Field(..., alias="Stocks (Profit or Loss)")
    etf_profit_loss: float = Field(..., alias="ETFs (Profit or Loss)")
    stock_dividends_profit: float = Field(..., alias="Stock Dividends (Profit)", ge=0)
    cfd_dividends_profit_loss: float = Field(
        ..., alias="CFD Dividends (Profit or Loss)"
    )
    refunds: float = Field(..., alias="Income from Refunds")
    cfd_commissions: float = Field(..., alias="Commissions (spread) on CFDs")
    crypto_commissions: float = Field(..., alias="Commissions (spread) on Crypto")
    etf_commissions: float = Field(..., alias="Commissions (spread) on ETFs")
    fees: float = Field(..., alias="Fees")


class EtoroAccountStatement(BaseModel):
    account_summary: EtoroAccountSummary
    financial_summary: EtoroFinancialSummary
    closed_positions: pd.DataFrame
    account_activity: pd.DataFrame

    class Config:
        arbitrary_types_allowed = True
