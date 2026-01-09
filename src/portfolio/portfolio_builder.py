"""
포트폴리오 생성 모듈

여러 종목을 분석하여 최적의 포트폴리오를 구성합니다.
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from src.data.fetcher_real import RealStockDataFetcher
from src.analysis import (
    calculate_srim_value,
    calculate_fair_value_comprehensive,
    evaluate_economic_moat,
    evaluate_management_quality
)
from src.portfolio.stock_presets import get_stock_config, is_preset_available

logger = logging.getLogger(__name__)


@dataclass
class StockAnalysis:
    """종목 분석 결과"""
    ticker: str
    company_name: str
    current_price: float
    market_cap: float

    # 재무 지표
    roe: Optional[float]
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]

    # 밸류에이션
    srim_value: float
    fair_value: float
    fair_price_per_share: float

    # 평가
    upside_percent: float  # 상승여력 (%)
    judgment: str  # 저평가/적정가/고평가
    score: float  # 종합 점수 (0-100)

    # 추가 정보
    moat_count: int
    moat_strength: str
    management_score: float


class PortfolioBuilder:
    """
    포트폴리오 생성 클래스

    여러 종목을 분석하여 저평가된 종목을 찾고 포트폴리오를 구성합니다.
    """

    def __init__(self, use_cache: bool = True):
        """
        Args:
            use_cache: 데이터 캐시 사용 여부
        """
        self.fetcher = RealStockDataFetcher(use_cache=use_cache)
        logger.info("PortfolioBuilder 초기화")

    def analyze_stock(
        self,
        ticker: str,
        korean_code: bool = True,
        moat_config: Optional[Dict] = None,
        mgmt_config: Optional[Dict] = None
    ) -> Optional[StockAnalysis]:
        """
        개별 종목 분석

        Args:
            ticker: 종목 코드
            korean_code: 한국 종목코드 여부
            moat_config: 경제적 해자 설정 (dict)
            mgmt_config: 경영진 평가 설정 (dict)

        Returns:
            종목 분석 결과 (데이터 없으면 None)
        """
        try:
            # 한국 종목코드 변환
            if korean_code and not ('.' in ticker):
                ticker = f"{ticker}.KS"

            logger.info(f"종목 분석 시작: {ticker}")

            # 데이터 수집
            info = self.fetcher.fetch_financial_info(ticker)
            current_price = info['current_price']

            # 필수 데이터 체크
            if current_price == 0 or info['market_cap'] == 0:
                logger.warning(f"데이터 부족: {ticker}")
                return None

            # 자기자본 계산
            if info['pb_ratio'] and info['pb_ratio'] > 0:
                equity = info['market_cap'] / info['pb_ratio']
            elif info['book_value'] and info['shares_outstanding']:
                equity = info['book_value'] * info['shares_outstanding']
            else:
                equity = info['market_cap'] * 0.8  # 기본값

            # ROE (음수면 기본값 사용)
            roe = info.get('roe', 0.10)
            if roe is None or roe <= 0:
                roe = 0.10  # 기본값 10%
                logger.warning(f"{ticker}: ROE가 음수 또는 없음, 기본값 10% 사용")

            # S-RIM 계산 (보수적 모드 적용)
            srim_value = calculate_srim_value(equity, roe, required_return=0.08, conservative=True)

            # 질적 평가 설정 (자동 또는 수동)
            if moat_config is None or mgmt_config is None:
                # 사전 정의된 설정 가져오기
                stock_config = get_stock_config(ticker)

                if moat_config is None:
                    moat_config = stock_config['moat']
                    if is_preset_available(ticker):
                        logger.info(f"{ticker}: 사전 정의된 경제적 해자 설정 사용")
                    else:
                        logger.info(f"{ticker}: 기본 경제적 해자 설정 사용")

                if mgmt_config is None:
                    mgmt_config = stock_config['mgmt']
                    if is_preset_available(ticker):
                        logger.info(f"{ticker}: 사전 정의된 경영진 평가 사용")
                    else:
                        logger.info(f"{ticker}: 기본 경영진 평가 사용")

            moat_result = evaluate_economic_moat(**moat_config)
            mgmt_result = evaluate_management_quality(**mgmt_config)

            # PEG 계산
            peg_ratio = None
            if info['pe_ratio'] and info['pe_ratio'] > 0:
                earnings_growth = 10.0  # 기본 성장률
                peg_ratio = info['pe_ratio'] / earnings_growth

            # 최종 적정가치
            fair_value_result = calculate_fair_value_comprehensive(
                srim_value=srim_value,
                peg_ratio=peg_ratio,
                economic_moat_premium=moat_result['premium_rate'],
                management_quality_premium=mgmt_result.get('premium_rate', mgmt_result.get('net_adjustment', 0)),
                governance_risk_discount=mgmt_result.get('discount_rate', 0.0)
            )

            final_value = fair_value_result['final_value']

            # 적정 주가
            shares_outstanding = info.get('shares_outstanding', 0)
            if shares_outstanding > 0:
                fair_price = final_value / shares_outstanding
            else:
                fair_price = current_price

            # 상승여력
            upside_percent = ((fair_price - current_price) / current_price) * 100

            # 투자 판단
            if upside_percent > 20:
                judgment = "저평가"
                score = min(100, 50 + upside_percent)
            elif upside_percent < -20:
                judgment = "고평가"
                score = max(0, 50 + upside_percent)
            else:
                judgment = "적정가"
                score = 50 + (upside_percent / 2)

            # 종합 점수 조정 (해자, 경영진 고려)
            score += moat_result['moat_count'] * 5
            score += (mgmt_result['avg_score'] - 3) * 5
            score = max(0, min(100, score))

            return StockAnalysis(
                ticker=ticker,
                company_name=info['company_name'],
                current_price=current_price,
                market_cap=info['market_cap'],
                roe=roe,
                pe_ratio=info.get('pe_ratio'),
                pb_ratio=info.get('pb_ratio'),
                srim_value=srim_value,
                fair_value=final_value,
                fair_price_per_share=fair_price,
                upside_percent=upside_percent,
                judgment=judgment,
                score=score,
                moat_count=moat_result['moat_count'],
                moat_strength=moat_result['moat_strength'].name,
                management_score=mgmt_result['avg_score']
            )

        except Exception as e:
            logger.error(f"종목 분석 실패: {ticker} - {e}")
            return None

    def build_portfolio(
        self,
        tickers: List[str],
        stock_configs: Optional[Dict[str, Dict]] = None
    ) -> Dict:
        """
        포트폴리오 구성

        Args:
            tickers: 분석할 종목 리스트
            stock_configs: 종목별 설정 (moat, mgmt)

        Returns:
            dict: {
                'stocks': 종목 분석 결과 리스트,
                'recommendations': 추천 종목 (저평가),
                'summary': 요약 정보,
                'generated_at': 생성 시각
            }
        """
        logger.info(f"포트폴리오 생성 시작: {len(tickers)}개 종목")

        if stock_configs is None:
            stock_configs = {}

        # 각 종목 분석
        analyses = []
        for ticker in tickers:
            config = stock_configs.get(ticker, {})
            moat_config = config.get('moat')
            mgmt_config = config.get('mgmt')

            analysis = self.analyze_stock(
                ticker,
                korean_code=True,
                moat_config=moat_config,
                mgmt_config=mgmt_config
            )

            if analysis:
                analyses.append(analysis)

        # 점수순 정렬
        analyses.sort(key=lambda x: x.score, reverse=True)

        # 추천 종목 (저평가 + 점수 60 이상)
        recommendations = [
            a for a in analyses
            if a.judgment == "저평가" and a.score >= 60
        ]

        # 요약 정보
        total_stocks = len(analyses)
        undervalued = len([a for a in analyses if a.judgment == "저평가"])
        fair_priced = len([a for a in analyses if a.judgment == "적정가"])
        overvalued = len([a for a in analyses if a.judgment == "고평가"])

        avg_upside = sum(a.upside_percent for a in analyses) / total_stocks if total_stocks > 0 else 0

        portfolio = {
            'stocks': [asdict(a) for a in analyses],
            'recommendations': [asdict(a) for a in recommendations],
            'summary': {
                'total_stocks': total_stocks,
                'undervalued': undervalued,
                'fair_priced': fair_priced,
                'overvalued': overvalued,
                'avg_upside': avg_upside,
                'top_pick': asdict(analyses[0]) if analyses else None
            },
            'generated_at': datetime.now().isoformat()
        }

        logger.info(f"포트폴리오 생성 완료: {total_stocks}개 분석, {len(recommendations)}개 추천")

        return portfolio
