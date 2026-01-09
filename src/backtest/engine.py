"""
백테스트 엔진

과거 데이터를 기반으로 포트폴리오 전략의 성과를 검증합니다.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import yfinance as yf

from src.data.fetcher_real import RealStockDataFetcher
from src.data.historical_data import HistoricalFinancialData
from src.portfolio.portfolio_builder import PortfolioBuilder
from src.analysis import (
    calculate_srim_value,
    calculate_fair_value_comprehensive,
    evaluate_economic_moat,
    evaluate_management_quality
)
from src.portfolio.stock_presets import get_stock_config

logger = logging.getLogger(__name__)


@dataclass
class BacktestResult:
    """백테스트 결과"""
    ticker: str
    company_name: str
    start_date: str

    # 시작 시점 데이터
    initial_price: float
    fair_value: float
    upside_percent: float
    judgment: str

    # 각 시점별 데이터
    one_month_price: Optional[float]
    one_month_return: Optional[float]

    six_month_price: Optional[float]
    six_month_return: Optional[float]

    one_year_price: Optional[float]
    one_year_return: Optional[float]

    current_price: Optional[float]
    current_return: Optional[float]

    # 추가 정보
    recommended: bool  # 저평가 추천 여부
    success: bool      # 추천이 맞았는지 (양수 수익률)


class BacktestEngine:
    """백테스트 엔진 클래스"""

    def __init__(self, use_cache: bool = True):
        """
        초기화

        Args:
            use_cache: 캐시 사용 여부
        """
        self.portfolio_builder = PortfolioBuilder(use_cache=use_cache)
        logger.info("BacktestEngine 초기화")

    def run_backtest(
        self,
        tickers: List[str],
        start_date: datetime,
        stock_configs: Optional[Dict] = None
    ) -> Dict:
        """
        백테스트 실행

        Args:
            tickers: 종목 코드 리스트
            start_date: 백테스트 시작 날짜
            stock_configs: 종목별 설정 (None이면 자동)

        Returns:
            백테스트 결과
        """
        logger.info(f"백테스트 시작: {len(tickers)}개 종목, 시작일: {start_date.date()}")

        if stock_configs is None:
            stock_configs = {}

        results = []

        for ticker in tickers:
            result = self._backtest_single_stock(
                ticker,
                start_date,
                stock_configs.get(ticker)
            )

            if result:
                results.append(result)

        # 성과 요약
        summary = self._calculate_summary(results, start_date)

        return {
            'results': [self._result_to_dict(r) for r in results],
            'summary': summary,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _backtest_single_stock(
        self,
        ticker: str,
        start_date: datetime,
        config: Optional[Dict] = None
    ) -> Optional[BacktestResult]:
        """
        개별 종목 백테스트

        Args:
            ticker: 종목 코드
            start_date: 시작 날짜
            config: 종목 설정

        Returns:
            백테스트 결과 (데이터 없으면 None)
        """
        try:
            # 한국 종목코드 변환
            if not '.' in ticker:
                ticker_symbol = f"{ticker}.KS"
            else:
                ticker_symbol = ticker

            logger.info(f"백테스트 분석: {ticker_symbol}")

            # Yahoo Finance 데이터 가져오기
            stock = yf.Ticker(ticker_symbol)

            # 시작 날짜의 주가 (전후 5일 범위에서 검색)
            start_price = self._get_price_at_date(stock, start_date)
            if start_price is None:
                logger.warning(f"{ticker_symbol}: 시작 날짜의 주가 데이터 없음")
                return None

            # 회사명
            info = stock.info
            company_name = info.get('longName', ticker)

            # 시작 날짜 기준으로 적정가치 계산 (과거 재무제표 사용)
            logger.info(f"{ticker_symbol}: {start_date.date()} 기준 재무제표 조회 중...")

            # 과거 재무제표 데이터 조회
            historical_financials = HistoricalFinancialData.get_financials_at_date(
                ticker_symbol,
                start_date
            )

            if historical_financials is None or historical_financials.get('roe') is None:
                logger.warning(f"{ticker_symbol}: 과거 재무제표 데이터 없음, 현재 데이터 사용")
                # 현재 데이터로 폴백
                moat_config = None
                mgmt_config = None
                if config:
                    moat_config = config.get('moat')
                    mgmt_config = config.get('mgmt')

                analysis = self.portfolio_builder.analyze_stock(
                    ticker,
                    korean_code=True,
                    moat_config=moat_config,
                    mgmt_config=mgmt_config
                )

                if analysis is None:
                    logger.warning(f"{ticker_symbol}: 분석 실패")
                    return None

                fair_value = analysis.fair_price_per_share
                upside_percent = analysis.upside_percent
                judgment = analysis.judgment

            else:
                # 과거 재무제표로 적정가치 계산
                logger.info(f"{ticker_symbol}: 과거 재무제표 사용 (ROE: {historical_financials['roe']:.2%})")

                # 시가총액 계산
                market_cap = HistoricalFinancialData.get_market_cap_at_date(
                    ticker_symbol,
                    start_date,
                    start_price
                )

                if market_cap is None:
                    # 발행주식수 추정 (자기자본 / PBR 가정)
                    shares = historical_financials['equity'] / start_price if historical_financials['equity'] else None
                    market_cap = shares * start_price if shares else start_price * 1000000000  # 임시값

                # 자기자본
                equity = historical_financials['equity']
                if equity is None or equity <= 0:
                    equity = market_cap * 0.3  # 임시 추정 (시총의 30%)

                # ROE
                roe = historical_financials['roe']
                if roe is None or roe <= 0:
                    roe = 0.10  # 기본값 10%
                    logger.warning(f"{ticker_symbol}: ROE 음수 또는 없음, 기본값 10% 사용")

                # S-RIM 계산 (보수적 모드 적용)
                logger.info(f"{ticker_symbol}: 자본총계 {equity:,.0f}원, ROE {roe:.2%}")
                srim_value = calculate_srim_value(equity, roe, required_return=0.08, conservative=True)
                logger.info(f"{ticker_symbol}: S-RIM 기초 가치 {srim_value:,.0f}원")

                # 경제적 해자 및 경영진 평가 설정
                stock_config = get_stock_config(ticker)
                moat_config = config.get('moat') if config else stock_config['moat']
                mgmt_config = config.get('mgmt') if config else stock_config['mgmt']

                moat_result = evaluate_economic_moat(**moat_config)
                mgmt_result = evaluate_management_quality(**mgmt_config)
                
                logger.info(f"{ticker_symbol}: 해자 프리미엄 {moat_result['premium_rate']:.1%}, 주주환원 프리미엄 {mgmt_result.get('premium_rate', 0):.1%}")

                # 종합 적정가치 계산
                peg_ratio = None  # 과거 PEG는 계산 어려움
                fair_value_result = calculate_fair_value_comprehensive(
                    srim_value=srim_value,
                    peg_ratio=peg_ratio,
                    economic_moat_premium=moat_result['premium_rate'],
                    management_quality_premium=mgmt_result.get('premium_rate', mgmt_result.get('net_adjustment', 0)),
                    governance_risk_discount=mgmt_result.get('discount_rate', 0.0)
                )

                # 주당 적정가치
                shares = HistoricalFinancialData.get_shares_outstanding_at_date(ticker_symbol, start_date)
                if shares is None or shares <= 0:
                    # 시가총액으로부터 발행주식수 추정
                    shares = market_cap / start_price
                    logger.warning(f"{ticker_symbol}: 발행주식수 추정값 사용 {shares:,.0f}주 (시총 {market_cap:,.0f}원 / 주가 {start_price:,.0f}원)")

                logger.info(f"{ticker_symbol}: 발행주식수 {shares:,.0f}주, 최종 적정 시총 {fair_value_result['final_value']:,.0f}원")
                
                fair_price_per_share = fair_value_result['final_value'] / shares
                upside_percent = ((fair_price_per_share - start_price) / start_price * 100)
                
                logger.info(f"{ticker_symbol}: 계산된 적정 주가 {fair_price_per_share:,.0f}원, 현재가 {start_price:,.0f}원, 상승여력 {upside_percent:+.1f}%")

                # 판단
                if upside_percent > 20:
                    judgment = "저평가"
                elif upside_percent < -20:
                    judgment = "고평가"
                else:
                    judgment = "적정가"

                fair_value = fair_price_per_share

                logger.info(f"{ticker_symbol}: 적정가 {fair_value:,.0f}원, 상승여력 {upside_percent:+.1f}%, 판단: {judgment}")

            # 미래 시점 주가
            one_month_later = start_date + timedelta(days=30)
            six_month_later = start_date + timedelta(days=180)
            one_year_later = start_date + timedelta(days=365)
            current = datetime.now()

            one_month_price = self._get_price_at_date(stock, one_month_later)
            six_month_price = self._get_price_at_date(stock, six_month_later)
            one_year_price = self._get_price_at_date(stock, one_year_later)
            current_price = self._get_price_at_date(stock, current)

            # 수익률 계산
            one_month_return = ((one_month_price - start_price) / start_price * 100) if one_month_price else None
            six_month_return = ((six_month_price - start_price) / start_price * 100) if six_month_price else None
            one_year_return = ((one_year_price - start_price) / start_price * 100) if one_year_price else None
            current_return = ((current_price - start_price) / start_price * 100) if current_price else None

            # 추천 여부 (저평가 판단)
            recommended = judgment == "저평가"

            # 성공 여부 (1년 수익률 기준, 없으면 현재 수익률)
            final_return = one_year_return if one_year_return is not None else current_return
            success = (final_return is not None and final_return > 0) if recommended else True

            return BacktestResult(
                ticker=ticker,
                company_name=company_name,
                start_date=start_date.strftime('%Y-%m-%d'),
                initial_price=start_price,
                fair_value=fair_value,
                upside_percent=upside_percent,
                judgment=judgment,
                one_month_price=one_month_price,
                one_month_return=one_month_return,
                six_month_price=six_month_price,
                six_month_return=six_month_return,
                one_year_price=one_year_price,
                one_year_return=one_year_return,
                current_price=current_price,
                current_return=current_return,
                recommended=recommended,
                success=success
            )

        except Exception as e:
            logger.error(f"{ticker} 백테스트 실패: {e}")
            return None

    def _get_price_at_date(
        self,
        stock: yf.Ticker,
        target_date: datetime
    ) -> Optional[float]:
        """
        특정 날짜의 주가 가져오기 (전후 5일 범위에서 검색)

        Args:
            stock: yfinance Ticker 객체
            target_date: 목표 날짜

        Returns:
            종가 (데이터 없으면 None)
        """
        try:
            # 전후 5일 범위
            start = target_date - timedelta(days=5)
            end = target_date + timedelta(days=5)

            # 데이터 가져오기
            hist = stock.history(
                start=start.strftime('%Y-%m-%d'),
                end=end.strftime('%Y-%m-%d')
            )

            if hist.empty:
                return None

            # 목표 날짜에 가장 가까운 날짜 찾기
            hist.index = hist.index.tz_localize(None)  # 시간대 제거
            closest_date = min(hist.index, key=lambda d: abs((d - target_date).days))

            return float(hist.loc[closest_date, 'Close'])

        except Exception as e:
            logger.error(f"주가 조회 실패: {e}")
            return None

    def _calculate_summary(
        self,
        results: List[BacktestResult],
        start_date: datetime
    ) -> Dict:
        """
        백테스트 성과 요약

        Args:
            results: 백테스트 결과 리스트
            start_date: 시작 날짜

        Returns:
            요약 통계
        """
        if not results:
            return {}

        # 추천 종목 (저평가)
        recommended = [r for r in results if r.recommended]

        # 각 시점별 평균 수익률
        one_month_returns = [r.one_month_return for r in results if r.one_month_return is not None]
        six_month_returns = [r.six_month_return for r in results if r.six_month_return is not None]
        one_year_returns = [r.one_year_return for r in results if r.one_year_return is not None]
        current_returns = [r.current_return for r in results if r.current_return is not None]

        # 추천 종목의 성공률
        success_rate = (sum(1 for r in recommended if r.success) / len(recommended) * 100) if recommended else 0

        return {
            'total_stocks': len(results),
            'recommended_stocks': len(recommended),
            'success_rate': round(success_rate, 1),

            'avg_one_month_return': round(sum(one_month_returns) / len(one_month_returns), 2) if one_month_returns else None,
            'avg_six_month_return': round(sum(six_month_returns) / len(six_month_returns), 2) if six_month_returns else None,
            'avg_one_year_return': round(sum(one_year_returns) / len(one_year_returns), 2) if one_year_returns else None,
            'avg_current_return': round(sum(current_returns) / len(current_returns), 2) if current_returns else None,

            'best_performer': max(results, key=lambda r: r.current_return or 0).ticker if results else None,
            'worst_performer': min(results, key=lambda r: r.current_return or 0).ticker if results else None
        }

    def _result_to_dict(self, result: BacktestResult) -> Dict:
        """백테스트 결과를 딕셔너리로 변환"""
        from dataclasses import asdict
        return asdict(result)
