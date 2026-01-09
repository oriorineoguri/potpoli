"""
데이터 수집 모듈 테스트
"""

import pytest
from datetime import datetime, timedelta
from src.data import (
    StockDataFetcher,
    get_stock_price,
    get_financial_statement,
    DataCache
)


class TestStockDataFetcher:
    """주식 데이터 수집 테스트"""

    def test_fetch_stock_price_basic(self):
        """기본 주가 조회 테스트"""
        # Given
        fetcher = StockDataFetcher()
        ticker = "005930"  # 삼성전자
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        # When
        prices = fetcher.fetch_stock_price(ticker, start_date, end_date)

        # Then
        assert len(prices) > 0
        assert all(p.ticker == ticker for p in prices)
        assert all(p.close > 0 for p in prices)

    def test_fetch_stock_price_default_dates(self):
        """날짜 기본값 테스트 (최근 1년)"""
        # Given
        fetcher = StockDataFetcher()

        # When: 날짜 지정 안 함
        prices = fetcher.fetch_stock_price("035720")  # 카카오

        # Then: 약 1년치 데이터 (주간 데이터이므로 ~52개)
        assert len(prices) > 40
        assert len(prices) < 60

    def test_fetch_financial_statement_annual(self):
        """연간 재무제표 조회 테스트"""
        # Given
        fetcher = StockDataFetcher()
        ticker = "005930"
        fiscal_year = 2023

        # When
        fs = fetcher.fetch_financial_statement(ticker, fiscal_year, fiscal_quarter=0)

        # Then
        assert fs.ticker == ticker
        assert fs.fiscal_year == fiscal_year
        assert fs.fiscal_quarter == 0
        assert fs.revenue > 0
        assert fs.equity > 0
        assert fs.eps > 0
        assert fs.bps > 0
        assert 0 < fs.roe < 1  # ROE는 0~1 사이 비율

    def test_fetch_financial_statement_quarterly(self):
        """분기 재무제표 조회 테스트"""
        # Given
        fetcher = StockDataFetcher()
        ticker = "035720"
        fiscal_year = 2023
        fiscal_quarter = 2  # 2분기

        # When
        fs_q = fetcher.fetch_financial_statement(ticker, fiscal_year, fiscal_quarter)
        fs_annual = fetcher.fetch_financial_statement(ticker, fiscal_year, 0)

        # Then: 분기 데이터는 연간의 약 1/4
        assert fs_q.fiscal_quarter == 2
        assert fs_q.revenue < fs_annual.revenue
        assert fs_q.revenue > fs_annual.revenue * 0.2  # 최소 20% (계절성 고려)

    def test_fetch_consensus_data(self):
        """컨센서스 데이터 조회 테스트"""
        # Given
        fetcher = StockDataFetcher()
        ticker = "005930"

        # When
        consensus = fetcher.fetch_consensus_data(ticker)

        # Then
        assert "target_price" in consensus
        assert "eps_estimate" in consensus
        assert "revenue_growth" in consensus
        assert "earnings_growth" in consensus
        assert consensus["target_price"] > 0
        assert consensus["eps_estimate"] > 0

    def test_get_stock_price_convenience_function(self):
        """주가 조회 편의 함수 테스트"""
        # Given
        ticker = "005930"

        # When
        price = get_stock_price(ticker)

        # Then
        assert price > 0
        assert isinstance(price, float)

    def test_get_financial_statement_convenience_function(self):
        """재무제표 조회 편의 함수 테스트"""
        # Given
        ticker = "005930"

        # When: 연도 지정 안 함 (최근 연도)
        fs = get_financial_statement(ticker)

        # Then
        assert fs.ticker == ticker
        assert fs.fiscal_quarter == 0  # 연간
        assert fs.equity > 0

    def test_get_financial_statement_with_year(self):
        """특정 연도 재무제표 조회"""
        # Given
        ticker = "005930"
        year = 2022

        # When
        fs = get_financial_statement(ticker, year)

        # Then
        assert fs.fiscal_year == year


class TestDataCache:
    """데이터 캐시 테스트"""

    def test_cache_set_and_get(self):
        """캐시 저장 및 조회 테스트"""
        # Given
        cache = DataCache(cache_dir="./data/test_cache")
        key = "test_key_1"
        data = {"value": 123, "name": "test"}

        # When
        cache.set(key, data)
        result = cache.get(key, ttl_seconds=60)

        # Then
        assert result is not None
        assert result["value"] == 123
        assert result["name"] == "test"

        # Cleanup
        cache.delete(key)

    def test_cache_expiration(self):
        """캐시 만료 테스트"""
        # Given
        cache = DataCache(cache_dir="./data/test_cache")
        key = "test_key_expiry"
        data = {"value": 456}

        # When
        cache.set(key, data)

        # Then: TTL 0초로 설정하면 즉시 만료
        result = cache.get(key, ttl_seconds=0)
        assert result is None  # 만료됨

        # Cleanup
        cache.delete(key)

    def test_cache_miss(self):
        """캐시 미스 테스트 (존재하지 않는 키)"""
        # Given
        cache = DataCache(cache_dir="./data/test_cache")
        key = "nonexistent_key"

        # When
        result = cache.get(key)

        # Then
        assert result is None

    def test_cache_delete(self):
        """캐시 삭제 테스트"""
        # Given
        cache = DataCache(cache_dir="./data/test_cache")
        key = "test_key_delete"
        data = {"value": 789}

        # When
        cache.set(key, data)
        assert cache.get(key) is not None  # 존재 확인

        cache.delete(key)

        # Then
        assert cache.get(key) is None  # 삭제됨

    def test_cache_clear_all(self):
        """전체 캐시 삭제 테스트"""
        # Given
        cache = DataCache(cache_dir="./data/test_cache")
        cache.set("key1", {"a": 1})
        cache.set("key2", {"b": 2})
        cache.set("key3", {"c": 3})

        # When
        count = cache.clear_all()

        # Then
        assert count >= 3
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") is None

    def test_cache_count_and_size(self):
        """캐시 개수 및 크기 조회 테스트"""
        # Given
        cache = DataCache(cache_dir="./data/test_cache")
        cache.clear_all()  # 초기화

        # When
        cache.set("test1", {"data": "test1"})
        cache.set("test2", {"data": "test2"})

        # Then
        assert cache.get_cache_count() == 2
        assert cache.get_cache_size() > 0

        # Cleanup
        cache.clear_all()

    def test_cache_with_complex_data(self):
        """복잡한 데이터 구조 캐싱 테스트"""
        # Given
        cache = DataCache(cache_dir="./data/test_cache")
        key = "complex_data"
        data = {
            "ticker": "005930",
            "financial_data": {
                "revenue": 300000000000000,
                "eps": 4500.0,
                "roe": 0.15
            },
            "prices": [50000, 51000, 52000],
            "metadata": {
                "source": "FnGuide",
                "updated_at": "2024-01-01"
            }
        }

        # When
        cache.set(key, data)
        result = cache.get(key)

        # Then
        assert result["ticker"] == "005930"
        assert result["financial_data"]["eps"] == 4500.0
        assert len(result["prices"]) == 3

        # Cleanup
        cache.delete(key)
