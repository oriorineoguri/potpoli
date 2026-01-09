"""
단순화된 적정가치 계산 모듈

moneyvalue.txt의 계산식:
1. S-RIM: 적정 시총 = 자본총계 + [자본총계 * (ROE-0.08)/0.08]
2. 성장성 보정: PEG < 1이면 결과값에 1.2 곱하기
3. 질적 평가: 경제적 해자와 주주환원으로 5~10% 가감
4. 최종: 적정 시총 / 발행주식수 = 적정 주가, 현재가 대비 상승 여력 % 표시
"""

import logging
from typing import Dict, Optional

from src.analysis.ratios import calculate_peg_ratio as calculate_peg_ratio_from_ratios

logger = logging.getLogger(__name__)


def calculate_fair_value_simple(
    equity: float,
    roe: float,
    peg_ratio: Optional[float] = None,
    has_moat: bool = False,
    good_shareholder_return: bool = False,
    shares_outstanding: float = 1.0,
    current_price: Optional[float] = None
) -> Dict:
    """
    moneyvalue.txt 기준 적정가치 계산

    Args:
        equity: 자본총계 (원)
        roe: ROE (소수, 예: 0.15 = 15%)
        peg_ratio: PEG 비율 (선택, PER과 예상 이익성장률로 계산)
        has_moat: 경제적 해자 유무
        good_shareholder_return: 주주환원 정책 우수 여부
        shares_outstanding: 발행주식수
        current_price: 현재 주가 (원, 상승 여력 계산용)

    Returns:
        dict: {
            'fair_market_cap': 적정 시가총액,
            'fair_price_per_share': 적정 주가,
            'upside_percent': 현재가 대비 상승 여력 (%),
            'details': 계산 상세
        }
    """

    # ROE 검증
    if roe is None or roe <= 0:
        logger.warning(f"ROE가 음수 또는 없음 (ROE: {roe}). 적정가치 계산 불가")
        return None

    if roe <= 0.08:
        logger.warning(f"ROE({roe:.2%})가 요구수익률(8%) 이하. 적정가치 계산 불가")
        return None

    # 1. S-RIM 계산
    # 적정 시총 = 자본총계 + [자본총계 * (ROE-0.08)/0.08]
    srim_market_cap = equity + (equity * (roe - 0.08) / 0.08)

    logger.info(f"S-RIM 계산: {srim_market_cap:,.0f}원 (자본총계: {equity:,.0f}, ROE: {roe:.2%})")

    # 2. 성장성 보정: PEG < 1이면 결과값에 1.2 곱하기
    growth_multiplier = 1.0
    if peg_ratio is not None and peg_ratio < 1.0:
        growth_multiplier = 1.2
        logger.info(f"성장성 보정: PEG {peg_ratio:.2f} < 1.0 → 1.2배 적용")

    market_cap_after_growth = srim_market_cap * growth_multiplier

    # 3. 질적 평가: 경제적 해자와 주주환원 정책으로 5~10% 내외로 가감
    quality_adjustment = 0.0

    if has_moat and good_shareholder_return:
        # 둘 다 있으면 +10%
        quality_adjustment = 0.10
        logger.info("경제적 해자 + 주주환원 정책 우수: +10%")
    elif has_moat:
        # 해자만 있으면 +7.5%
        quality_adjustment = 0.075
        logger.info("경제적 해자 있음: +7.5%")
    elif good_shareholder_return:
        # 주주환원만 우수하면 +5%
        quality_adjustment = 0.05
        logger.info("주주환원 정책 우수: +5%")
    else:
        # 둘 다 없으면 -5%
        quality_adjustment = -0.05
        logger.info("해자/주주환원 없음: -5%")

    final_market_cap = market_cap_after_growth * (1 + quality_adjustment)

    logger.info(f"질적 평가 적용: {quality_adjustment:+.1%} → 최종 시총: {final_market_cap:,.0f}원")

    # 4. 최종: 적정 시가총액 / 발행주식수 = 적정 주가
    fair_price_per_share = final_market_cap / shares_outstanding

    logger.info(f"주당 적정가: {fair_price_per_share:,.0f}원 (발행주식수: {shares_outstanding:,.0f}주)")

    # 5. 현재가 대비 상승 여력 계산
    upside_percent = None
    if current_price is not None and current_price > 0:
        upside_percent = ((fair_price_per_share - current_price) / current_price) * 100
        logger.info(f"현재가 대비 상승 여력: {upside_percent:+.2f}% (현재가: {current_price:,.0f}원)")

    result = {
        'fair_market_cap': final_market_cap,
        'fair_price_per_share': fair_price_per_share,
        'upside_percent': upside_percent,
        'details': {
            'srim_market_cap': srim_market_cap,
            'growth_multiplier': growth_multiplier,
            'quality_adjustment': quality_adjustment,
            'peg_ratio': peg_ratio,
            'has_moat': has_moat,
            'good_shareholder_return': good_shareholder_return,
            'current_price': current_price
        }
    }

    return result


# PEG 계산은 ratios.py의 calculate_peg_ratio 함수를 사용
# 이 모듈에서는 calculate_peg_ratio_from_ratios로 import하여 사용
calculate_peg_ratio = calculate_peg_ratio_from_ratios
