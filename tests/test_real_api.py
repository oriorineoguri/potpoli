"""
실제 API 연동 테스트

주의: 이 테스트는 실제 API를 호출하므로 인터넷 연결이 필요합니다.
"""

import pytest
from datetime import datetime, timedelta
from src.data.fetcher_real import (
    RealStockDataFetcher,
    get_real_stock_price,
    get_real_financial_info
)


class TestRealStockDataFetcher:
    """실제 API 주가 데이터 수집 테스트"""

    @pytest.mark.integration  # 통합 테스트 마커
    def test_fetch_samsung_stock_price(self):
        """삼성전자 주가 수집 테스트"""
        # Given
        fetcher = RealStockDataFetcher(use_cache=False)
        ticker = "005930.KS"  # 삼성전자
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        # When
        prices = fetcher.fetch_stock_price(ticker, start_date, end_date)

        # Then
        assert len(prices) > 0
        assert all(p.ticker == ticker for p in prices)
        assert all(p.close > 0 for p in prices)
        # 날짜만 비교 (시간 제외)
        assert prices[0].date.date() >= start_date.date()
        assert prices[-1].date.date() <= end_date.date()

        print(f"\n✅ 삼성전자 주가 {len(prices)}개 수집 성공")
        print(f"   최신 종가: {prices[-1].close:,.0f}원")

    @pytest.mark.integration
    def test_fetch_kakao_stock_price(self):
        """카카오 주가 수집 테스트"""
        # Given
        fetcher = RealStockDataFetcher(use_cache=False)
        ticker = "035720.KS"  # 카카오
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        # When
        prices = fetcher.fetch_stock_price(ticker, start_date, end_date)

        # Then
        assert len(prices) > 0
        print(f"\n✅ 카카오 주가 {len(prices)}개 수집 성공")
        print(f"   최신 종가: {prices[-1].close:,.0f}원")

    @pytest.mark.integration
    def test_fetch_apple_stock_price(self):
        """애플(AAPL) 주가 수집 테스트 (미국 주식)"""
        # Given
        fetcher = RealStockDataFetcher(use_cache=False)
        ticker = "AAPL"  # 애플
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        # When
        prices = fetcher.fetch_stock_price(ticker, start_date, end_date)

        # Then
        assert len(prices) > 0
        assert all(p.close > 0 for p in prices)

        print(f"\n✅ 애플(AAPL) 주가 {len(prices)}개 수집 성공")
        print(f"   최신 종가: ${prices[-1].close:.2f}")

    @pytest.mark.integration
    def test_fetch_invalid_ticker(self):
        """잘못된 티커 테스트"""
        # Given
        fetcher = RealStockDataFetcher(use_cache=False)
        ticker = "INVALID_TICKER_12345"

        # When & Then
        with pytest.raises(ValueError, match="데이터를 가져올 수 없습니다"):
            fetcher.fetch_stock_price(ticker)

    @pytest.mark.integration
    def test_fetch_with_cache(self):
        """캐시 사용 테스트"""
        # Given
        fetcher = RealStockDataFetcher(use_cache=True)
        ticker = "005930.KS"
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        # When: 첫 번째 호출 (API에서 가져옴)
        prices1 = fetcher.fetch_stock_price(ticker, start_date, end_date)

        # When: 두 번째 호출 (캐시에서 가져옴)
        prices2 = fetcher.fetch_stock_price(ticker, start_date, end_date)

        # Then: 결과가 동일해야 함
        assert len(prices1) == len(prices2)
        assert prices1[0].close == prices2[0].close

        print("\n✅ 캐시 기능 정상 작동")

    @pytest.mark.integration
    def test_fetch_samsung_financial_info(self):
        """삼성전자 재무 정보 수집 테스트"""
        # Given
        fetcher = RealStockDataFetcher(use_cache=False)
        ticker = "005930.KS"

        # When
        info = fetcher.fetch_financial_info(ticker)

        # Then
        assert info['ticker'] == ticker
        assert info['market_cap'] > 0
        assert info['current_price'] > 0

        print(f"\n✅ 삼성전자 재무 정보 수집 성공")
        print(f"   회사명: {info['company_name']}")
        print(f"   시가총액: {info['market_cap']:,.0f}원")
        print(f"   현재가: {info['current_price']:,.0f}원")
        if info['pe_ratio']:
            print(f"   PER: {info['pe_ratio']:.2f}")
        if info['pb_ratio']:
            print(f"   PBR: {info['pb_ratio']:.2f}")
        if info['roe']:
            print(f"   ROE: {info['roe']:.2%}")

    @pytest.mark.integration
    def test_get_current_price(self):
        """현재 주가 조회 테스트"""
        # Given
        fetcher = RealStockDataFetcher()
        ticker = "005930.KS"

        # When
        price = fetcher.get_current_price(ticker)

        # Then
        assert price > 0
        print(f"\n✅ 삼성전자 현재가: {price:,.0f}원")

    @pytest.mark.integration
    def test_convert_korean_ticker(self):
        """한국 티커 변환 테스트"""
        # Test cases
        assert RealStockDataFetcher.convert_korean_ticker("005930") == "005930.KS"
        assert RealStockDataFetcher.convert_korean_ticker("035720") == "035720.KS"
        assert RealStockDataFetcher.convert_korean_ticker("005930.KS") == "005930.KS"
        assert RealStockDataFetcher.convert_korean_ticker("035720.KQ") == "035720.KQ"

        print("\n✅ 티커 변환 기능 정상 작동")

    @pytest.mark.integration
    def test_convenience_functions(self):
        """편의 함수 테스트"""
        # Given
        ticker = "005930"  # 삼성전자 (6자리 코드)

        # When: 주가 조회
        price = get_real_stock_price(ticker)

        # Then
        assert price > 0
        print(f"\n✅ 편의 함수 - 삼성전자 주가: {price:,.0f}원")

        # When: 재무 정보 조회
        info = get_real_financial_info(ticker)

        # Then
        assert info['market_cap'] > 0
        print(f"✅ 편의 함수 - 시가총액: {info['market_cap']:,.0f}원")


class TestRealDataIntegration:
    """실제 데이터를 사용한 통합 테스트"""

    @pytest.mark.integration
    def test_calculate_per_with_real_data(self):
        """실제 데이터로 PER 계산 테스트"""
        from src.analysis.ratios import calculate_per_ratio

        # Given: 실제 삼성전자 데이터
        fetcher = RealStockDataFetcher()
        info = fetcher.fetch_financial_info("005930.KS")

        stock_price = info['current_price']
        eps = info.get('eps_trailing')

        # When
        if eps and eps > 0:
            per = calculate_per_ratio(stock_price, eps)

            # Then
            assert per is not None
            assert per > 0

            print(f"\n✅ 삼성전자 실제 데이터 PER 계산")
            print(f"   주가: {stock_price:,.0f}원")
            print(f"   EPS: {eps:,.0f}원")
            print(f"   PER: {per:.2f}")
        else:
            print("\n⚠️  EPS 데이터 없음 - PER 계산 생략")

    @pytest.mark.integration
    def test_valuation_with_real_data(self):
        """실제 데이터로 S-RIM 밸류에이션 테스트"""
        from src.analysis.valuation import calculate_srim_value

        # Given: 실제 삼성전자 데이터
        fetcher = RealStockDataFetcher()
        info = fetcher.fetch_financial_info("005930.KS")

        market_cap = info['market_cap']
        roe = info.get('roe')
        book_value = info.get('book_value')
        shares_outstanding = info.get('shares_outstanding')

        # 자기자본 추정 (시가총액, BPS, 주식수로 계산)
        if book_value and shares_outstanding:
            equity = book_value * shares_outstanding

            # When: S-RIM 계산
            if roe:
                srim_value = calculate_srim_value(equity, roe, required_return=0.08)

                # Then
                assert srim_value > 0

                print(f"\n✅ 삼성전자 S-RIM 밸류에이션")
                print(f"   자기자본: {equity:,.0f}원")
                print(f"   ROE: {roe:.2%}")
                print(f"   S-RIM 기업가치: {srim_value:,.0f}원")
                print(f"   실제 시가총액: {market_cap:,.0f}원")
                print(f"   차이: {((srim_value - market_cap) / market_cap * 100):+.1f}%")
            else:
                print("\n⚠️  ROE 데이터 없음 - S-RIM 계산 생략")
        else:
            print("\n⚠️  재무 데이터 부족 - S-RIM 계산 생략")
