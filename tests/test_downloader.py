'''
 # @ Author: Meet Patel
 # @ Create Time: 2026-01-01 10:13:07
 # @ Modified by: Meet Patel
 # @ Modified time: 2026-01-01 10:37:49
 # @ Description:
 '''

import pandas as pd
import pytest
import types
from datetime import datetime

from yf_cache import YFinanceDataDownloader


class FakeTicker:
    def __init__(self, data_frame):
        self._df = data_frame

    def history(self, start=None, end=None, interval=None):
        # Return a DataFrame indexed by date similar to yfinance
        return self._df


@pytest.fixture
def sample_df():
    idx = pd.DatetimeIndex(["2024-02-15", "2024-02-16", "2024-03-01"], tz="UTC")
    df = pd.DataFrame({"Open": [1, 2, 3], "Close": [1.1, 2.1, 3.1]}, index=idx)
    return df


def test_get_cache_path(tmp_path):
    d = YFinanceDataDownloader(cache_dir=str(tmp_path))
    p = d._get_cache_path("AAPL", "1d", 2024, 2)
    assert "AAPL" in str(p)
    assert p.name == "2024-02.csv"


def test_get_data_uses_fake_ticker(monkeypatch, tmp_path, sample_df):
    fake = FakeTicker(sample_df)

    def fake_ticker_ctor(ticker):
        return fake

    monkeypatch.setattr("yf_cache.downloader.yf.Ticker", fake_ticker_ctor)

    d = YFinanceDataDownloader(cache_dir=str(tmp_path))
    df = d.get_data("AAPL", "2024-02-15", "2024-03-01", interval="1d")

    # It should return rows within the date range
    assert not df.empty
    assert df.index.min().date() >= datetime(2024, 2, 15).date()
    assert df.index.max().date() <= datetime(2024, 3, 1).date()
