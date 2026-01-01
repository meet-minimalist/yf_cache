'''
 # @ Author: Meet Patel
 # @ Create Time: 2026-01-01 10:12:25
 # @ Modified by: Meet Patel
 # @ Modified time: 2026-01-01 10:37:42
 # @ Description:
 '''

"""yf_cache package

Provides YFinanceDataDownloader for downloading and caching Yahoo Finance data.
"""

__all__ = ["YFinanceDataDownloader", "__version__"]

__version__ = "0.1.0"

from .downloader import YFinanceDataDownloader  # noqa: F401
