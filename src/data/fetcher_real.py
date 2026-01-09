"""
실제 API를 사용한 주식 데이터 수집 모듈

yfinance를 사용하여 Yahoo Finance에서 실제 주가 데이터를 수집합니다.

데이터 소스:
- 주가: Yahoo Finance (yfinance 라이브러리)
- 재무제표: Yahoo Finance (제한적)

참고:
- 한국 주식: 티커 뒤에 .KS (KOSPI) 또는 .KQ (KOSDAQ) 추가
  예: 삼성전자 = "005930.KS", 카카오 = "035720.KS"
"""

import logging
import yfinance as yf
import pandas as pd
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from src.data.fetcher import StockPrice, FinancialStatement
from src.data.cache import DataCache

logger = logging.getLogger(__name__)


class RealStockDataFetcher:
    """
    실제 API를 사용한 주식 데이터 수집 클래스

    yfinance를 통해 Yahoo Finance API로부터 실제 데이터를 수집합니다.

    **API Rate Limit:**
    - Yahoo Finance는 공개 API로 제한이 있을 수 있습니다
    - 캐시 사용을 권장합니다
    - 과도한 요청 시 IP 차단 가능성 있음
    """

    def __init__(
        self,
        use_cache: bool = True,
        cache_dir: str = "./data/cache"
    ):
        """
        Args:
            use_cache: 캐시 사용 여부
            cache_dir: 캐시 디렉토리 경로
        """
        self._use_cache = use_cache
        self._cache = DataCache(cache_dir) if use_cache else None
        logger.info(f"RealStockDataFetcher 초기화 (캐시: {use_cache})")

    def fetch_stock_price(
        self,
        ticker: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[StockPrice]:
        """
        실제 주가 데이터 수집 (Yahoo Finance)

        Args:
            ticker: 종목 코드
                   - 한국 주식: "005930.KS" (삼성전자), "035720.KS" (카카오)
                   - 미국 주식: "AAPL" (애플), "MSLA" (테슬라)
            start_date: 시작 날짜 (None이면 최근 1년)
            end_date: 종료 날짜 (None이면 오늘)

        Returns:
            주가 데이터 리스트

        Raises:
            ValueError: 티커가 잘못되었거나 데이터를 가져올 수 없는 경우

        Examples:
            >>> fetcher = RealStockDataFetcher()
            >>> prices = fetcher.fetch_stock_price("005930.KS")  # 삼성전자
            >>> len(prices) > 0
            True
        """
        # 기본값 설정
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=365)

        # 캐시 키 생성
        cache_key = f"stock_price_{ticker}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"

        # 캐시 확인
        if self._use_cache:
            cached_data = self._cache.get(cache_key, ttl_seconds=3600)  # 1시간
            if cached_data is not None:
                logger.info(f"캐시에서 주가 데이터 로드: {ticker}")
                return [StockPrice(**item) for item in cached_data]

        logger.info(
            f"Yahoo Finance에서 주가 수집: {ticker} "
            f"({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})"
        )

        try:
            # yfinance로 데이터 수집
            stock = yf.Ticker(ticker)
            df = stock.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d')
            )

            if df.empty:
                logger.error(f"데이터 없음: {ticker} (티커가 올바른지 확인하세요)")
                raise ValueError(
                    f"티커 '{ticker}'의 데이터를 가져올 수 없습니다. "
                    f"한국 주식은 '.KS' 또는 '.KQ'를 추가하세요. "
                    f"(예: 005930.KS)"
                )

            # DataFrame을 StockPrice 리스트로 변환
            prices = []
            for date_index, row in df.iterrows():
                # timezone 정보 제거 (naive datetime으로 변환)
                date_obj = date_index.to_pydatetime()
                if date_obj.tzinfo is not None:
                    date_obj = date_obj.replace(tzinfo=None)

                prices.append(StockPrice(
                    ticker=ticker,
                    date=date_obj,
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=int(row['Volume'])
                ))

            logger.info(f"주가 데이터 {len(prices)}개 수집 완료")

            # 캐시에 저장
            if self._use_cache:
                cache_data = [asdict(p) for p in prices]
                # datetime을 문자열로 변환 (JSON 직렬화)
                for item in cache_data:
                    item['date'] = item['date'].isoformat()
                self._cache.set(cache_key, cache_data)

            return prices

        except Exception as e:
            logger.error(f"주가 수집 실패: {ticker} - {e}")
            raise

    def fetch_financial_info(
        self,
        ticker: str
    ) -> Dict:
        """
        기업 재무 정보 수집 (Yahoo Finance)

        Yahoo Finance는 제한적인 재무 정보를 제공합니다.
        더 상세한 재무제표가 필요하면 FnGuide 또는 DART API 사용을 권장합니다.

        Args:
            ticker: 종목 코드

        Returns:
            dict: 재무 정보
                - market_cap: 시가총액
                - pe_ratio: PER
                - pb_ratio: PBR
                - dividend_yield: 배당수익률
                - beta: 베타
                - 52week_high/low: 52주 최고가/최저가

        Examples:
            >>> fetcher = RealStockDataFetcher()
            >>> info = fetcher.fetch_financial_info("005930.KS")
            >>> info['market_cap'] > 0
            True
        """
        # 캐시 키
        cache_key = f"financial_info_{ticker}"

        # 캐시 확인
        if self._use_cache:
            cached_data = self._cache.get(cache_key, ttl_seconds=86400)  # 24시간
            if cached_data is not None:
                logger.info(f"캐시에서 재무 정보 로드: {ticker}")
                return cached_data

        logger.info(f"Yahoo Finance에서 재무 정보 수집: {ticker}")

        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # 주요 정보 추출
            financial_data = {
                "ticker": ticker,
                "company_name": info.get('longName', 'N/A'),
                "market_cap": info.get('marketCap', 0),
                "current_price": info.get('currentPrice', 0),
                "pe_ratio": info.get('trailingPE', None),
                "forward_pe": info.get('forwardPE', None),
                "pb_ratio": info.get('priceToBook', None),
                "dividend_yield": info.get('dividendYield', 0),
                "beta": info.get('beta', None),
                "52week_high": info.get('fiftyTwoWeekHigh', 0),
                "52week_low": info.get('fiftyTwoWeekLow', 0),
                "avg_volume": info.get('averageVolume', 0),
                "shares_outstanding": info.get('sharesOutstanding', 0),
                "eps_trailing": info.get('trailingEps', None),
                "book_value": info.get('bookValue', None),
                "revenue": info.get('totalRevenue', None),
                "profit_margin": info.get('profitMargins', None),
                "operating_margin": info.get('operatingMargins', None),
                "roe": info.get('returnOnEquity', None),
                "debt_to_equity": info.get('debtToEquity', None)
            }

            logger.info(f"재무 정보 수집 완료: {ticker}")

            # 캐시에 저장
            if self._use_cache:
                self._cache.set(cache_key, financial_data)

            return financial_data

        except Exception as e:
            logger.error(f"재무 정보 수집 실패: {ticker} - {e}")
            raise

    def get_current_price(self, ticker: str) -> float:
        """
        현재 주가 조회

        Args:
            ticker: 종목 코드

        Returns:
            현재 주가 (원 또는 달러)

        Examples:
            >>> fetcher = RealStockDataFetcher()
            >>> price = fetcher.get_current_price("005930.KS")
            >>> price > 0
            True
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            current_price = info.get('currentPrice', 0)

            if current_price == 0:
                # 최근 종가로 대체
                history = stock.history(period="1d")
                if not history.empty:
                    current_price = float(history['Close'].iloc[-1])

            logger.info(f"현재 주가: {ticker} = {current_price:,.0f}")
            return current_price

        except Exception as e:
            logger.error(f"현재 주가 조회 실패: {ticker} - {e}")
            raise

    @staticmethod
    def convert_korean_ticker(code: str) -> str:
        """
        한국 종목코드를 Yahoo Finance 티커로 변환

        Args:
            code: 6자리 종목코드 (예: "005930")

        Returns:
            Yahoo Finance 티커 (예: "005930.KS")

        Examples:
            >>> RealStockDataFetcher.convert_korean_ticker("005930")
            '005930.KS'
            >>> RealStockDataFetcher.convert_korean_ticker("035720")
            '035720.KS'
        """
        # 이미 .KS 또는 .KQ가 붙어있으면 그대로 반환
        if code.endswith('.KS') or code.endswith('.KQ'):
            return code

        # 기본적으로 KOSPI (.KS) 사용
        # KOSDAQ 종목은 사용자가 명시적으로 .KQ를 붙여야 함
        return f"{code}.KS"


# 편의 함수
def get_real_stock_price(ticker: str, korean_code: bool = True) -> float:
    """
    실제 주가 조회 (편의 함수)

    Args:
        ticker: 종목 코드
        korean_code: 한국 종목코드인 경우 True (자동 변환)

    Returns:
        현재 주가

    Examples:
        >>> price = get_real_stock_price("005930")  # 삼성전자
        >>> price > 0
        True
    """
    fetcher = RealStockDataFetcher()

    if korean_code and not ('.' in ticker):
        ticker = RealStockDataFetcher.convert_korean_ticker(ticker)

    return fetcher.get_current_price(ticker)


def get_real_financial_info(ticker: str, korean_code: bool = True) -> Dict:
    """
    실제 재무 정보 조회 (편의 함수)

    Args:
        ticker: 종목 코드
        korean_code: 한국 종목코드인 경우 True

    Returns:
        재무 정보 딕셔너리

    Examples:
        >>> info = get_real_financial_info("005930")
        >>> info['market_cap'] > 0
        True
    """
    fetcher = RealStockDataFetcher()

    if korean_code and not ('.' in ticker):
        ticker = RealStockDataFetcher.convert_korean_ticker(ticker)

    return fetcher.fetch_financial_info(ticker)
