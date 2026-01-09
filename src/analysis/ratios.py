"""
재무 비율 계산 모듈

주식의 다양한 재무 비율(PER, PBR, PEG, EV/EBITDA 등)을 계산합니다.

데이터 소스:
- 주가 데이터: Yahoo Finance, 네이버 증권
- 재무제표 데이터: FnGuide, DART 전자공시
"""

import logging
from typing import Optional

# 로거 설정
logger = logging.getLogger(__name__)


def calculate_per_ratio(
    stock_price: float,
    earnings_per_share: float
) -> Optional[float]:
    """
    PER (Price to Earnings Ratio, 주가수익비율) 계산 함수

    주가를 주당순이익(EPS)으로 나누어 PER을 계산합니다.

    **금융 지표 해석 가이드:**
    - PER = 주가 ÷ EPS (투자금 회수에 걸리는 연수)
    - PER 10 = 현재 수익 수준으로 10년간 벌어야 투자금 회수
    - 적정 범위: 일반적으로 10~20 (업종별 차이 있음)
    - 낮을수록: 저평가 가능성 (가치주)
    - 높을수록: 고평가 또는 고성장 기대 (성장주)
    - 음수/0: 적자 기업 (계산 불가)

    Args:
        stock_price: 현재 주가 (원)
        earnings_per_share: 주당순이익 (원)

    Returns:
        계산된 PER 값. EPS가 0이거나 음수인 경우 None 반환

    Raises:
        ValueError: 주가가 0 이하인 경우

    Examples:
        >>> calculate_per_ratio(50000, 5000)
        10.0
        >>> calculate_per_ratio(50000, 0)
        None

    Note:
        데이터 소스: 주가(네이버 증권), EPS(FnGuide 재무제표)
    """
    # 입력 데이터 검증
    if stock_price <= 0:
        logger.error(f"잘못된 주가 입력: {stock_price}. 주가는 0보다 커야 합니다.")
        raise ValueError(f"주가는 0보다 커야 합니다. 입력값: {stock_price}")

    # Division by zero 체크
    if earnings_per_share <= 0:
        logger.warning(
            f"EPS가 {earnings_per_share}로 0 이하입니다. "
            f"PER 계산 불가능 (주가: {stock_price})"
        )
        return None

    # PER 계산
    per = stock_price / earnings_per_share

    logger.info(
        f"PER 계산 완료 - 주가: {stock_price:,.0f}원, "
        f"EPS: {earnings_per_share:,.0f}원, PER: {per:.2f}"
    )

    return per


def calculate_pbr_ratio(
    stock_price: float,
    book_value_per_share: float
) -> Optional[float]:
    """
    PBR (Price to Book Ratio, 주가순자산비율) 계산 함수

    주가를 주당순자산(BPS)으로 나누어 PBR을 계산합니다.

    **금융 지표 해석 가이드:**
    - PBR = 주가 ÷ BPS (장부가치 대비 시장 평가)
    - PBR 1.0 = 주가가 순자산가치와 동일
    - PBR < 1.0 = 저평가 가능성, 청산가치보다 낮은 가격
    - PBR > 1.0 = 시장이 미래 수익성을 기대
    - 적정 범위: 1.0~3.0 (업종별 차이 큼)
    - 자산주 투자 시 중요한 지표

    Args:
        stock_price: 현재 주가 (원)
        book_value_per_share: 주당순자산 (원)

    Returns:
        계산된 PBR 값. BPS가 0 이하인 경우 None 반환

    Raises:
        ValueError: 주가가 0 이하인 경우

    Examples:
        >>> calculate_pbr_ratio(50000, 40000)
        1.25
        >>> calculate_pbr_ratio(50000, 0)
        None

    Note:
        데이터 소스: 주가(네이버 증권), BPS(FnGuide 재무상태표)
    """
    # 입력 데이터 검증
    if stock_price <= 0:
        logger.error(f"잘못된 주가 입력: {stock_price}")
        raise ValueError(f"주가는 0보다 커야 합니다. 입력값: {stock_price}")

    # Division by zero 체크
    if book_value_per_share <= 0:
        logger.warning(
            f"BPS가 {book_value_per_share}로 0 이하입니다. "
            f"PBR 계산 불가능 (자본잠식 가능성)"
        )
        return None

    # PBR 계산
    pbr = stock_price / book_value_per_share

    logger.info(
        f"PBR 계산 완료 - 주가: {stock_price:,.0f}원, "
        f"BPS: {book_value_per_share:,.0f}원, PBR: {pbr:.2f}"
    )

    return pbr


def calculate_peg_ratio(
    per: float,
    earnings_growth_rate: float
) -> Optional[float]:
    """
    PEG (Price/Earnings to Growth, 주가수익성장비율) 계산 함수

    PER을 이익성장률로 나누어 성장성을 고려한 밸류에이션을 평가합니다.

    **금융 지표 해석 가이드:**
    - PEG = PER ÷ 이익성장률(%)
    - PEG < 1.0 = 성장성 대비 저평가 (매수 고려)
    - PEG = 1.0 = 적정 가격
    - PEG > 1.0 = 성장성 대비 고평가
    - PEG < 0.5 = 매우 저평가된 고성장주 가능성
    - 성장주 투자 시 PER보다 유용한 지표

    Args:
        per: PER 값
        earnings_growth_rate: 연간 이익 성장률 (%, 예: 20% = 20.0)

    Returns:
        계산된 PEG 값. 성장률이 0 이하인 경우 None 반환

    Raises:
        ValueError: PER이 0 이하인 경우

    Examples:
        >>> calculate_peg_ratio(20.0, 25.0)  # PER 20, 성장률 25%
        0.8
        >>> calculate_peg_ratio(20.0, 0)  # 성장률 0%
        None

    Note:
        데이터 소스: PER(계산값), 성장률(FnGuide 컨센서스 또는 과거 3개년 평균)
    """
    # 입력 데이터 검증
    if per <= 0:
        logger.error(f"잘못된 PER 입력: {per}")
        raise ValueError(f"PER은 0보다 커야 합니다. 입력값: {per}")

    # Division by zero 및 음수 성장률 체크
    if earnings_growth_rate <= 0:
        logger.warning(
            f"이익성장률이 {earnings_growth_rate}%로 0 이하입니다. "
            f"PEG 계산 불가능 (적자 전환 또는 역성장)"
        )
        return None

    # PEG 계산
    peg = per / earnings_growth_rate

    logger.info(
        f"PEG 계산 완료 - PER: {per:.2f}, "
        f"성장률: {earnings_growth_rate:.1f}%, PEG: {peg:.2f}"
    )

    return peg


def calculate_ev_ebitda(
    enterprise_value: float,
    ebitda: float
) -> Optional[float]:
    """
    EV/EBITDA (기업가치 대비 EBITDA 배수) 계산 함수

    기업가치(EV)를 EBITDA로 나누어 현금창출 능력 대비 가치를 평가합니다.

    **금융 지표 해석 가이드:**
    - EV/EBITDA = 기업가치 ÷ EBITDA
    - EV = 시가총액 + 순차입금 (부채 고려한 실질 기업가치)
    - EBITDA = 영업이익 + 감가상각비 (실제 현금창출력)
    - 적정 범위: 6~12배 (업종별 차이 큼)
    - PER보다 부채 고려하여 더 정확한 평가
    - 제조업, 자본집약적 산업에서 특히 유용

    Args:
        enterprise_value: 기업가치 (시가총액 + 순차입금, 원)
        ebitda: EBITDA (원)

    Returns:
        계산된 EV/EBITDA 값. EBITDA가 0 이하인 경우 None 반환

    Raises:
        ValueError: 기업가치가 0 이하인 경우

    Examples:
        >>> calculate_ev_ebitda(1000000000000, 100000000000)  # EV 1조, EBITDA 1000억
        10.0
        >>> calculate_ev_ebitda(1000000000000, -10000000000)  # 적자
        None

    Note:
        데이터 소스: 시가총액(네이버 증권), 차입금(FnGuide 재무상태표),
                    EBITDA(FnGuide 손익계산서)
    """
    # 입력 데이터 검증
    if enterprise_value <= 0:
        logger.error(f"잘못된 기업가치 입력: {enterprise_value}")
        raise ValueError(f"기업가치는 0보다 커야 합니다. 입력값: {enterprise_value}")

    # Division by zero 체크
    if ebitda <= 0:
        logger.warning(
            f"EBITDA가 {ebitda:,.0f}로 0 이하입니다. "
            f"EV/EBITDA 계산 불가능 (영업 적자)"
        )
        return None

    # EV/EBITDA 계산
    ev_ebitda_ratio = enterprise_value / ebitda

    logger.info(
        f"EV/EBITDA 계산 완료 - EV: {enterprise_value:,.0f}원, "
        f"EBITDA: {ebitda:,.0f}원, EV/EBITDA: {ev_ebitda_ratio:.2f}"
    )

    return ev_ebitda_ratio
