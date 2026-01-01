"""yf_cache package

Provides YFinanceDataDownloader for downloading and caching Yahoo Finance data.
"""

__all__ = ["YFinanceDataDownloader", "__version__"]

__version__ = "0.1.0"

from .downloader import YFinanceDataDownloader  # noqa: F401
