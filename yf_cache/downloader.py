import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf


logger = logging.getLogger(__name__)


class YFinanceDataDownloader:
    """Download and cache stock data from Yahoo Finance.

    Data is stored in monthly CSV files organized by ticker and interval.
    """

    def __init__(self, cache_dir: str = "yfinance_data"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_path(self, ticker: str, interval: str, year: int, month: int) -> Path:
        ticker_dir = self.cache_dir / ticker.upper() / interval
        ticker_dir.mkdir(parents=True, exist_ok=True)
        return ticker_dir / f"{year:04d}-{month:02d}.csv"

    def _get_month_range(self, year: int, month: int) -> tuple[datetime, datetime]:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        return start_date, end_date

    def _download_month_data(self, ticker: str, interval: str, year: int, month: int) -> Optional[pd.DataFrame]:
        start_date, end_date = self._get_month_range(year, month)
        cache_path = self._get_cache_path(ticker, interval, year, month)

        logger.info("Downloading %s data for %04d-%02d with interval %s", ticker, year, month, interval)

        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date + timedelta(days=1), interval=interval)

            if df.empty:
                logger.debug("No data available for %s in %04d-%02d", ticker, year, month)
                return None

            df.reset_index(inplace=True)
            # Ensure the datetime column has a consistent name
            if 'Date' not in df.columns and 'Datetime' not in df.columns:
                first_col = df.columns[0]
                df.rename(columns={first_col: 'Datetime'}, inplace=True)

            df.to_csv(cache_path, index=False)
            logger.info("Saved to %s", cache_path)
            return df

        except Exception as exc:  # pragma: no cover - network errors
            logger.error("Error downloading data for %s %04d-%02d: %s", ticker, year, month, exc)
            return None

    def _load_month_data(self, ticker: str, interval: str, year: int, month: int) -> Optional[pd.DataFrame]:
        cache_path = self._get_cache_path(ticker, interval, year, month)
        if cache_path.exists():
            logger.info("Loading cached data from %s", cache_path)
            df = pd.read_csv(cache_path)
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], utc=True)
            elif 'Datetime' in df.columns:
                df['Datetime'] = pd.to_datetime(df['Datetime'], utc=True)
            return df
        return None

    def _get_or_download_month(self, ticker: str, interval: str, year: int, month: int) -> Optional[pd.DataFrame]:
        df = self._load_month_data(ticker, interval, year, month)
        if df is None:
            df = self._download_month_data(ticker, interval, year, month)
        return df

    def get_data(self, ticker: str, start_date: "str | datetime", end_date: "str | datetime", interval: str = "1d") -> pd.DataFrame:
        """Get stock data for a date range, using cache when available."""
        # parse strings
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # make timezone-aware
        import pytz
        if start_date.tzinfo is None:
            start_date = pytz.UTC.localize(start_date)
        if end_date.tzinfo is None:
            end_date = pytz.UTC.localize(end_date)

        months_to_fetch = []
        current = datetime(start_date.year, start_date.month, 1)
        end = datetime(end_date.year, end_date.month, 1)

        while current <= end:
            months_to_fetch.append((current.year, current.month))
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1)
            else:
                current = datetime(current.year, current.month + 1, 1)

        all_data = []
        for year, month in months_to_fetch:
            df = self._get_or_download_month(ticker, interval, year, month)
            if df is not None:
                all_data.append(df)

        if not all_data:
            logger.warning("No data available for %s", ticker)
            return pd.DataFrame()

        combined_df = pd.concat(all_data, ignore_index=True)
        date_col = 'Date' if 'Date' in combined_df.columns else 'Datetime'
        if combined_df[date_col].dt.tz is None:
            combined_df[date_col] = pd.to_datetime(combined_df[date_col], utc=True)

        mask = (combined_df[date_col] >= start_date) & (combined_df[date_col] <= end_date)
        result_df = combined_df[mask].copy()
        result_df.set_index(date_col, inplace=True)

        logger.info("Retrieved %d records for %s from %s to %s", len(result_df), ticker, start_date.date(), end_date.date())
        return result_df

    def clear_cache(self, ticker: Optional[str] = None):
        import shutil
        if ticker:
            ticker_dir = self.cache_dir / ticker.upper()
            if ticker_dir.exists():
                shutil.rmtree(ticker_dir)
                logger.info("Cleared cache for %s", ticker)
        else:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(exist_ok=True)
                logger.info("Cleared all cache")
