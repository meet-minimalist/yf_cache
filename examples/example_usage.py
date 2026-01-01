'''
 # @ Author: Meet Patel
 # @ Create Time: 2026-01-01 10:12:38
 # @ Modified by: Meet Patel
 # @ Modified time: 2026-01-01 10:38:16
 # @ Description:
 '''

"""Example usage of yf_cache package"""
from yf_cache import YFinanceDataDownloader


def main():
    downloader = YFinanceDataDownloader()
    df = downloader.get_data("AAPL", "2024-02-15", "2024-03-24", interval="1d")
    print(df.head())


if __name__ == "__main__":
    main()
