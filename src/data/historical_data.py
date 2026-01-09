"""
과거 재무제표 데이터 조회

특정 시점의 재무제표를 조회하여 백테스트에 사용합니다.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
import yfinance as yf
import pandas as pd

from src.data.dart_api import DartApiClient

logger = logging.getLogger(__name__)


class HistoricalFinancialData:
    """과거 재무제표 데이터 조회 클래스"""

    # DART API 클라이언트 (싱글톤)
    _dart_client = None

    @classmethod
    def _get_dart_client(cls) -> DartApiClient:
        """DART API 클라이언트 가져오기 (싱글톤)"""
        if cls._dart_client is None:
            cls._dart_client = DartApiClient()
        return cls._dart_client

    @classmethod
    def get_financials_at_date(cls, ticker: str, target_date: datetime) -> Optional[Dict]:
        """
        특정 날짜 기준의 재무제표 데이터 조회

        우선순위:
        1. DART API (한국 공식 재무제표)
        2. Yahoo Finance API (폴백)

        Args:
            ticker: 종목 코드 (예: "005930.KS")
            target_date: 목표 날짜

        Returns:
            재무 데이터 딕셔너리 (없으면 None)
        """
        # 티커 정리
        clean_ticker = ticker.replace('.KS', '').replace('.KQ', '')

        # 1. DART API 시도
        logger.info(f"{ticker}: DART API로 과거 재무제표 조회 시도...")
        dart_client = cls._get_dart_client()
        dart_data = dart_client.get_financials_at_date(clean_ticker, target_date)

        if dart_data and dart_data.get('roe') is not None:
            logger.info(f"{ticker}: DART API 성공! {dart_data['year']}년 {dart_data['quarter']} 재무제표 사용")
            return dart_data

        # 2. Yahoo Finance API 폴백
        logger.warning(f"{ticker}: DART API 실패, Yahoo Finance로 폴백...")
        return cls._get_financials_from_yfinance(ticker, target_date)

    @staticmethod
    def _get_financials_from_yfinance(ticker: str, target_date: datetime) -> Optional[Dict]:
        """
        Yahoo Finance에서 재무제표 조회 (폴백용)

        Args:
            ticker: 종목 코드
            target_date: 목표 날짜

        Returns:
            재무 데이터 딕셔너리
        """
        try:
            stock = yf.Ticker(ticker)

            # 분기별 재무제표 가져오기
            quarterly_financials = stock.quarterly_financials
            quarterly_balance_sheet = stock.quarterly_balance_sheet
            quarterly_cashflow = stock.quarterly_cashflow

            if quarterly_financials is None or quarterly_financials.empty:
                logger.warning(f"{ticker}: 분기별 재무제표 데이터 없음")
                return None

            # 날짜 인덱스를 datetime으로 변환 (시간대 제거)
            if hasattr(quarterly_financials.columns, 'tz_localize'):
                quarterly_financials.columns = quarterly_financials.columns.tz_localize(None)
            if hasattr(quarterly_balance_sheet.columns, 'tz_localize'):
                quarterly_balance_sheet.columns = quarterly_balance_sheet.columns.tz_localize(None)
            if hasattr(quarterly_cashflow.columns, 'tz_localize'):
                quarterly_cashflow.columns = quarterly_cashflow.columns.tz_localize(None)

            # 목표 날짜 이전의 가장 최근 재무제표 찾기
            available_dates = quarterly_financials.columns

            # 목표 날짜 이전의 날짜만 필터링
            past_dates = [d for d in available_dates if d <= target_date]

            if not past_dates:
                logger.warning(f"{ticker}: {target_date.date()} 이전의 재무제표 데이터 없음")
                return None

            # 가장 최근 날짜 선택
            closest_date = max(past_dates)

            logger.info(f"{ticker}: {target_date.date()} 기준 → {closest_date.date()}의 재무제표 사용")

            # 재무 데이터 추출
            financials_data = {}

            # 순이익 (Net Income)
            net_income = None
            if 'Net Income' in quarterly_financials.index:
                net_income = quarterly_financials.loc['Net Income', closest_date]
            elif 'Net Income Common Stockholders' in quarterly_financials.index:
                net_income = quarterly_financials.loc['Net Income Common Stockholders', closest_date]

            # 자기자본 (Total Equity / Stockholders Equity)
            equity = None
            if quarterly_balance_sheet is not None and not quarterly_balance_sheet.empty:
                if 'Total Equity Gross Minority Interest' in quarterly_balance_sheet.index:
                    equity = quarterly_balance_sheet.loc['Total Equity Gross Minority Interest', closest_date]
                elif 'Stockholders Equity' in quarterly_balance_sheet.index:
                    equity = quarterly_balance_sheet.loc['Stockholders Equity', closest_date]
                elif 'Total Assets' in quarterly_balance_sheet.index and 'Total Liabilities Net Minority Interest' in quarterly_balance_sheet.index:
                    total_assets = quarterly_balance_sheet.loc['Total Assets', closest_date]
                    total_liabilities = quarterly_balance_sheet.loc['Total Liabilities Net Minority Interest', closest_date]
                    equity = total_assets - total_liabilities

            # 총자산 (Total Assets)
            total_assets = None
            if quarterly_balance_sheet is not None and not quarterly_balance_sheet.empty:
                if 'Total Assets' in quarterly_balance_sheet.index:
                    total_assets = quarterly_balance_sheet.loc['Total Assets', closest_date]

            # ROE 계산 (순이익 / 자기자본)
            roe = None
            if net_income is not None and equity is not None and equity > 0:
                # 연간화 (분기 데이터 * 4)
                annual_net_income = net_income * 4
                roe = annual_net_income / equity

            # 데이터 정리
            financials_data = {
                'date': closest_date,
                'net_income': float(net_income) if net_income is not None and pd.notna(net_income) else None,
                'equity': float(equity) if equity is not None and pd.notna(equity) else None,
                'total_assets': float(total_assets) if total_assets is not None and pd.notna(total_assets) else None,
                'roe': float(roe) if roe is not None and pd.notna(roe) else None
            }

            logger.info(f"{ticker} 재무 데이터: ROE={financials_data['roe']:.2%}, 자기자본={financials_data['equity']:,.0f}" if financials_data['roe'] and financials_data['equity'] else f"{ticker} 재무 데이터 조회 완료")

            return financials_data

        except Exception as e:
            logger.error(f"{ticker} 과거 재무제표 조회 실패: {e}")
            return None

    @staticmethod
    def get_shares_outstanding_at_date(ticker: str, target_date: datetime) -> Optional[float]:
        """
        특정 날짜의 발행주식수 조회

        Args:
            ticker: 종목 코드
            target_date: 목표 날짜

        Returns:
            발행주식수 (없으면 None)
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # 현재 발행주식수 (과거 데이터는 제한적)
            shares = info.get('sharesOutstanding')

            if shares:
                logger.info(f"{ticker}: 발행주식수 {shares:,.0f}주")
                return float(shares)

            return None

        except Exception as e:
            logger.error(f"{ticker} 발행주식수 조회 실패: {e}")
            return None

    @staticmethod
    def get_market_cap_at_date(ticker: str, target_date: datetime, price: float) -> Optional[float]:
        """
        특정 날짜의 시가총액 계산

        Args:
            ticker: 종목 코드
            target_date: 목표 날짜
            price: 해당 날짜의 주가

        Returns:
            시가총액 (없으면 None)
        """
        shares = HistoricalFinancialData.get_shares_outstanding_at_date(ticker, target_date)

        if shares and price:
            market_cap = shares * price
            logger.info(f"{ticker}: 시가총액 {market_cap:,.0f}원")
            return market_cap

        return None
