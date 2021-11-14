import pytz

from finvestor.etoro.utils import parse_etoro_datetime


def test_parse_etoro_datetime():
    etoro_date = "31/12/1999 23:59:59"
    utc_date = parse_etoro_datetime(etoro_date)
    assert utc_date.tzinfo == pytz.utc
    assert utc_date.isoformat() == "1999-12-31T23:59:59+00:00"
