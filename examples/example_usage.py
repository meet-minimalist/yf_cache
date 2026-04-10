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
    
    # Example 1: Normal usage (existing behavior)
    print("Example 1: Download without validation")
    df = downloader.get_data("AAPL", "2024-02-15", "2024-03-24", interval="1d")
    print(df.head())
    
    # Example 2: With date range validation
    print("\nExample 2: Download with date range validation")
    # This will only download if data is available for the entire range
    df_validated = downloader.get_data(
        "HDFC.NS", 
        "2004-02-15", 
        "2024-03-24", 
        interval="1d",
        validate_date_range=True
    )
    print(df_validated.head())
    
    # Example 3: Validation with a delisted stock
    print("\nExample 3: Validation with potentially delisted stock")
    # If this stock was delisted, validation will fail and return empty DataFrame
    df_delisted = downloader.get_data(
        "DELISTED_STOCK", 
        "2020-01-01", 
        "2025-12-31", 
        interval="1d",
        validate_date_range=True
    )
    if df_delisted.empty:
        print("No data - validation failed (as expected for delisted stock)")
    else:
        print(df_delisted.head())


if __name__ == "__main__":
    main()
