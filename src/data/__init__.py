"""데이터 수집 및 전처리 모듈"""

from src.data.fetcher import (
    StockDataFetcher,
    get_stock_price,
    get_financial_statement
)
from src.data.cache import DataCache

# 실제 API 연동 (선택적 import)
try:
    from src.data.fetcher_real import (
        RealStockDataFetcher,
        get_real_stock_price,
        get_real_financial_info
    )
    __all__ = [
        "StockDataFetcher",
        "get_stock_price",
        "get_financial_statement",
        "DataCache",
        "RealStockDataFetcher",
        "get_real_stock_price",
        "get_real_financial_info"
    ]
except ImportError:
    # yfinance가 설치되지 않은 경우
    __all__ = [
        "StockDataFetcher",
        "get_stock_price",
        "get_financial_statement",
        "DataCache"
    ]
