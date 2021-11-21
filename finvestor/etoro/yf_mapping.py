# in etoro crypto are by default converted to USD if currency is not defined
# Example:
#   BTC: BTC <-> USD
#   BTCEUR: BTC <-> EUR
# TODO: not the best way to do this, maybe keep an sqlite with etoro_name and yf_name in
# the same row for as asset

ETORO_TO_YF_TICKER_MAPPING = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "ADA": "ADA-USD",
    "BBRY": "BB",
}
