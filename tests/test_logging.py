'''
 # @ Author: Meet Patel
 # @ Create Time: 2026-01-01 10:24:47
 # @ Modified by: Meet Patel
 # @ Modified time: 2026-01-01 10:37:35
 # @ Description:
 '''

import logging
from yf_cache import YFinanceDataDownloader


def test_set_log_level(tmp_path):
    d = YFinanceDataDownloader(cache_dir=str(tmp_path), log_level='DEBUG')
    # module logger should be set to DEBUG
    import yf_cache.downloader as mod
    assert mod.logger.level == logging.DEBUG


def test_set_log_level_invalid():
    d = YFinanceDataDownloader()
    try:
        d.set_log_level('NOT_A_LEVEL')
        assert False, "Expected ValueError for invalid level"
    except ValueError:
        pass
