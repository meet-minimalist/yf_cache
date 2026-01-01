# yf_cache

A small package to download and cache Yahoo Finance data in monthly CSV chunks.

## Installation

Install directly from GitHub:

pip install git+https://github.com/meet-minimalist/yf_cache.git

Or from source:

pip install .

## Usage

from yf_cache import YFinanceDataDownloader

# You can set the module log level at construction (e.g., 'DEBUG', 'INFO')
d = YFinanceDataDownloader(log_level='DEBUG')
df = d.get_data("AAPL", "2024-02-15", "2024-03-24", interval="1d")
print(df.head())

# Or set it later:
# d.set_log_level('INFO')

## License

MIT
