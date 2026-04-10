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


def test_validate_date_range_success(monkeypatch, tmp_path):
    """Test validation when full date range is available."""
    idx = pd.date_range("2024-02-01", "2024-03-31", freq="B", tz="UTC")
    full_df = pd.DataFrame({"Open": range(len(idx)), "Close": range(len(idx))}, index=idx)
    fake = FakeTicker(full_df)

    def fake_ticker_ctor(ticker):
        return fake

    monkeypatch.setattr("yf_cache.downloader.yf.Ticker", fake_ticker_ctor)

    d = YFinanceDataDownloader(cache_dir=str(tmp_path))
    result = d.get_data("AAPL", "2024-02-15", "2024-03-15", interval="1d", validate_date_range=True)
    
    # Should return data since validation passes
    assert not result.empty


def test_validate_date_range_partial_data(monkeypatch, tmp_path):
    """Test validation fails when only partial data is available."""
    # Stock only has data until 2024-02-20, but we request until 2024-03-15
    idx = pd.date_range("2024-02-01", "2024-02-20", freq="B", tz="UTC")
    partial_df = pd.DataFrame({"Open": range(len(idx)), "Close": range(len(idx))}, index=idx)
    fake = FakeTicker(partial_df)

    def fake_ticker_ctor(ticker):
        return fake

    monkeypatch.setattr("yf_cache.downloader.yf.Ticker", fake_ticker_ctor)

    d = YFinanceDataDownloader(cache_dir=str(tmp_path))
    result = d.get_data("AAPL", "2024-02-15", "2024-03-15", interval="1d", validate_date_range=True)
    
    # Should return empty DataFrame since validation fails
    assert result.empty


def test_validate_date_range_no_data(monkeypatch, tmp_path):
    """Test validation fails when no data is available."""
    empty_df = pd.DataFrame()
    fake = FakeTicker(empty_df)

    def fake_ticker_ctor(ticker):
        return fake

    monkeypatch.setattr("yf_cache.downloader.yf.Ticker", fake_ticker_ctor)

    d = YFinanceDataDownloader(cache_dir=str(tmp_path))
    result = d.get_data("NONEXISTENT", "2024-02-15", "2024-03-15", interval="1d", validate_date_range=True)
    
    # Should return empty DataFrame
    assert result.empty


def test_get_data_without_validation(monkeypatch, tmp_path):
    """Test that validation is skipped when validate_date_range=False."""
    # Partial data available
    idx = pd.date_range("2024-02-01", "2024-02-20", freq="B", tz="UTC")
    partial_df = pd.DataFrame({"Open": range(len(idx)), "Close": range(len(idx))}, index=idx)
    fake = FakeTicker(partial_df)

    def fake_ticker_ctor(ticker):
        return fake

    monkeypatch.setattr("yf_cache.downloader.yf.Ticker", fake_ticker_ctor)

    d = YFinanceDataDownloader(cache_dir=str(tmp_path))
    result = d.get_data("AAPL", "2024-02-15", "2024-03-15", interval="1d", validate_date_range=False)
    
    # Should return available data even though range is not fully covered
    assert not result.empty
