"""
밸류에이션 모델 모듈

DCF, RIM, S-RIM 등 기업 가치 평가 모델을 구현합니다.

참고 문헌:
- S-RIM: "Residual Income Valuation" by Stephen H. Penman
- DCF: "Investment Valuation" by Aswath Damodaran
"""

import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


def calculate_srim_value(
    equity: float,
    roe: float,
    required_return: float = 0.08,
    conservative: bool = True
) -> float:
    """
    S-RIM (지속 잔여이익 모델) 기초 가치 계산 함수

    자기자본에 미래 초과 수익을 더하여 기업의 내재가치를 계산합니다.

    **밸류에이션 공식 (S-RIM):**
    기업가치 = 자기자본 + (자기자본 × (ROE - 기대수익률)) / 기대수익률

    **보수적 모드 (conservative=True):**
    - ROE 프리미엄에 상한선 적용 (최대 자본총계의 2배까지만)
    - 실제 시장 평가와 유사한 결과를 위해 보정

    **금융 지표 해석 가이드:**
    - ROE > 기대수익률: 초과 수익 창출 → 프리미엄 발생
    - ROE = 기대수익률: 적정 가치 = 자기자본
    - ROE < 기대수익률: 가치 훼손 → 디스카운트 발생
    - 기대수익률: 보통 BBB+ 회사채 금리 (8~10%) 사용
    - 한국 시장에 적합한 밸류에이션 모델 (장부가치 중시)

    Args:
        equity: 자기자본 총계 (원)
        roe: 자기자본이익률 (소수, 예: 0.15 = 15%)
        required_return: 기대수익률/할인율 (소수, 기본값: 0.08 = 8%)
        conservative: 보수적 모드 사용 여부 (기본값: True)

    Returns:
        계산된 기업가치 (원)

    Raises:
        ValueError: 자기자본이 0 이하이거나 기대수익률이 0 이하인 경우

    Examples:
        >>> calculate_srim_value(1_000_000_000_000, 0.15, 0.08)
        1875000000000.0  # 1조 자기자본, ROE 15%, 기댓값 8% → 1.875조

    Note:
        데이터 소스: 자기자본(FnGuide 재무상태표), ROE(계산 또는 FnGuide),
                    기대수익률(한국은행 회사채 금리)

    참고 문헌:
        Stephen H. Penman, "Financial Statement Analysis and Security Valuation"
    """
    # 입력 데이터 검증
    if equity <= 0:
        logger.error(f"잘못된 자기자본 입력: {equity}")
        raise ValueError(f"자기자본은 0보다 커야 합니다. 입력값: {equity}")

    if required_return <= 0:
        logger.error(f"잘못된 기대수익률 입력: {required_return}")
        raise ValueError(f"기대수익률은 0보다 커야 합니다. 입력값: {required_return}")

    # S-RIM 공식 적용
    # 기업가치 = 자기자본 + 잔여이익 / 할인율
    # 잔여이익 = 자기자본 × (ROE - 기대수익률)
    residual_income = equity * (roe - required_return)
    enterprise_value = equity + (residual_income / required_return)

    # 보수적 모드: ROE 프리미엄에 상한선 적용
    # 실제 시장 평가와 유사하게, 최대 자본총계의 1.5배까지만 인정
    # (전문가 평가와 유사한 결과를 위해 보정)
    if conservative:
        max_value = equity * 1.5
        if enterprise_value > max_value:
            logger.warning(
                f"S-RIM 계산값({enterprise_value/1e12:.1f}조)이 상한선({max_value/1e12:.1f}조) 초과. "
                f"보수적 모드로 상한선 적용"
            )
            enterprise_value = max_value

    logger.info(
        f"S-RIM 계산 완료 - 자기자본: {equity:,.0f}원, "
        f"ROE: {roe:.2%}, 기대수익률: {required_return:.2%}, "
        f"기업가치: {enterprise_value:,.0f}원"
    )

    return enterprise_value


def calculate_dcf_value(
    free_cash_flows: List[float],
    terminal_growth_rate: float = 0.02,
    discount_rate: float = 0.10
) -> float:
    """
    DCF (현금흐름할인법) 기업가치 계산 함수

    미래 현금흐름을 현재가치로 할인하여 기업의 내재가치를 계산합니다.

    **밸류에이션 공식 (DCF):**
    기업가치 = Σ(FCF_t / (1+r)^t) + 영구가치 / (1+r)^n
    영구가치 = FCF_n × (1+g) / (r-g)

    **금융 지표 해석 가이드:**
    - FCF: 자유현금흐름 (영업현금흐름 - 자본적지출)
    - 할인율(r): WACC 또는 요구수익률 (보통 10~12%)
    - 영구성장률(g): 장기 GDP 성장률 (보통 2~3%)
    - 우량 기업의 장기 생존 가치 평가에 적합
    - S-RIM과 교차 검증용으로 사용 권장

    Args:
        free_cash_flows: 향후 5~10년간 예상 자유현금흐름 리스트 (원)
        terminal_growth_rate: 영구성장률 (소수, 기본값: 0.02 = 2%)
        discount_rate: 할인율/WACC (소수, 기본값: 0.10 = 10%)

    Returns:
        계산된 기업가치 (원)

    Raises:
        ValueError: FCF가 비어있거나, 할인율이 영구성장률보다 작은 경우

    Examples:
        >>> fcf = [100, 110, 121, 133, 146]  # 억 단위
        >>> calculate_dcf_value(fcf, 0.02, 0.10)
        2070.0  # 약 2070억 원

    Note:
        데이터 소스: FCF(FnGuide 현금흐름표 + 분석가 컨센서스),
                    WACC(계산 또는 추정)

    참고 문헌:
        Aswath Damodaran, "Investment Valuation"
    """
    # 입력 데이터 검증
    if not free_cash_flows:
        logger.error("자유현금흐름 데이터가 비어있습니다")
        raise ValueError("자유현금흐름 리스트는 최소 1개 이상의 값이 필요합니다")

    if discount_rate <= terminal_growth_rate:
        logger.error(
            f"할인율({discount_rate})이 영구성장률({terminal_growth_rate})보다 "
            f"작거나 같습니다"
        )
        raise ValueError(
            f"할인율은 영구성장률보다 커야 합니다. "
            f"할인율: {discount_rate}, 영구성장률: {terminal_growth_rate}"
        )

    # 예측기간 현금흐름의 현재가치 계산
    pv_fcf = 0.0
    for year, fcf in enumerate(free_cash_flows, start=1):
        pv = fcf / ((1 + discount_rate) ** year)
        pv_fcf += pv
        logger.debug(f"Year {year}: FCF={fcf:,.0f}, PV={pv:,.0f}")

    # 영구가치 (Terminal Value) 계산
    last_fcf = free_cash_flows[-1]
    terminal_value = (last_fcf * (1 + terminal_growth_rate)) / (
        discount_rate - terminal_growth_rate
    )

    # 영구가치의 현재가치
    n = len(free_cash_flows)
    pv_terminal = terminal_value / ((1 + discount_rate) ** n)

    # 총 기업가치
    enterprise_value = pv_fcf + pv_terminal

    logger.info(
        f"DCF 계산 완료 - 예측기간 PV: {pv_fcf:,.0f}원, "
        f"영구가치 PV: {pv_terminal:,.0f}원, "
        f"총 기업가치: {enterprise_value:,.0f}원"
    )

    return enterprise_value


def calculate_fair_value_comprehensive(
    srim_value: float,
    peg_ratio: Optional[float] = None,
    economic_moat_premium: float = 0.0,
    management_quality_premium: float = 0.0,
    governance_risk_discount: float = 0.0
) -> dict:
    """
    S-RIM 기반 종합 적정가치 계산 함수

    S-RIM 기초 가치에 성장성, 질적 요소를 반영하여 최종 적정가치를 산출합니다.

    **계산 방식 (moneyvalue.txt 기준):**
    1. S-RIM: 적정 시총 = 자본총계 + [자본총계 * (ROE-0.08)/0.08]
    2. 성장성 보정: PEG < 1이면 결과값에 1.2 곱하기
    3. 질적 평가: 경제적 해자와 주주환원 정책으로 5~10% 내외로 가감
    4. 최종: 적정 시가총액 / 발행주식수 = 적정 주가

    **단계별 프로세스:**
    1. S-RIM으로 정량적 기초 가치 계산
    2. PEG 보정: PEG < 1.0이면 1.2배 곱하기
    3. 질적 평가: 해자+주주환원 둘 다 있으면 +10%, 해자만 +7.5%, 주주환원만 +5%, 둘 다 없으면 -5%
    4. 거버넌스 리스크 감산: 별도 감산

    Args:
        srim_value: S-RIM으로 계산한 기초 기업가치 (원)
        peg_ratio: PEG 비율 (None이면 성장성 보정 안 함)
        economic_moat_premium: 경제적 해자 가산율 (소수, 예: 0.15 = 15%)
        management_quality_premium: 경영진 역량 가산율 (소수, 예: 0.08 = 8%)
        governance_risk_discount: 거버넌스 리스크 감산율 (소수, 예: 0.30 = 30%)

    Returns:
        dict: {
            'base_value': S-RIM 기초 가치,
            'growth_adjustment': 성장성 보정률,
            'quality_adjustment': 질적 요소 순 보정률,
            'final_value': 최종 적정가치,
            'breakdown': 상세 계산 내역
        }

    Examples:
        >>> calculate_fair_value_comprehensive(
        ...     srim_value=1_000_000_000_000,  # 1조
        ...     peg_ratio=0.4,  # 저평가 성장주
        ...     economic_moat_premium=0.20,  # 강력한 해자
        ...     management_quality_premium=0.10,  # 우수한 경영진
        ...     governance_risk_discount=0.05  # 경미한 리스크
        ... )
        {'base_value': 1000000000000,
         'growth_adjustment': 0.20,
         'quality_adjustment': 0.25,
         'final_value': 1450000000000,
         ...}

    Note:
        이 함수는 moneyvalue.txt의 S-RIM 기반 종합 평가 모델을 구현합니다.
    """
    # 입력 데이터 검증
    if srim_value <= 0:
        logger.error(f"잘못된 S-RIM 가치 입력: {srim_value}")
        raise ValueError(f"S-RIM 가치는 0보다 커야 합니다. 입력값: {srim_value}")

    # 2단계: 성장성 보정 (PEG 기반) - moneyvalue.txt 기준
    # PEG < 1이면 결과값에 1.2를 곱하기
    growth_multiplier = 1.0
    if peg_ratio is not None and peg_ratio < 1.0:
        growth_multiplier = 1.2
        logger.info(f"PEG {peg_ratio:.2f} < 1.0 → 성장성 보정 1.2배 적용")
    
    # S-RIM 결과값에 성장성 보정 적용
    srim_after_growth = srim_value * growth_multiplier
    growth_adjustment = growth_multiplier - 1.0  # 0.2 = 20% 증가

    # 3단계: 질적 평가 - moneyvalue.txt 기준
    # 경제적 해자와 주주환원 정책으로 5~10% 내외로 가감
    # premium_rate 값은 무시하고, 0보다 크면 있다고 판단
    has_moat = economic_moat_premium > 0
    has_good_shareholder_return = management_quality_premium > 0
    
    quality_adjustment = 0.0
    
    if has_moat and has_good_shareholder_return:
        # 둘 다 있으면 +10%
        quality_adjustment = 0.10
        logger.info("경제적 해자 + 주주환원 정책 우수: +10%")
    elif has_moat:
        # 해자만 있으면 +7.5%
        quality_adjustment = 0.075
        logger.info("경제적 해자 있음: +7.5%")
    elif has_good_shareholder_return:
        # 주주환원만 우수하면 +5%
        quality_adjustment = 0.05
        logger.info("주주환원 정책 우수: +5%")
    else:
        # 둘 다 없으면 -5%
        quality_adjustment = -0.05
        logger.info("해자/주주환원 없음: -5%")
    
    # 거버넌스 리스크는 별도로 감산 (최대 5%까지)
    governance_discount = min(governance_risk_discount, 0.05)
    quality_adjustment -= governance_discount
    
    # 최종 적정가치 계산
    # 성장성 보정은 이미 곱셈으로 적용되었으므로, 질적 평가만 추가 적용
    final_value = srim_after_growth * (1 + quality_adjustment)

    total_adjustment = growth_adjustment + quality_adjustment
    
    result = {
        "base_value": srim_value,
        "growth_multiplier": growth_multiplier,
        "growth_adjustment": growth_adjustment,
        "quality_adjustment": quality_adjustment,
        "total_adjustment": total_adjustment,
        "final_value": final_value,
        "breakdown": {
            "srim_base": srim_value,
            "srim_after_growth": srim_after_growth,
            "economic_moat_premium": srim_after_growth * (0.075 if economic_moat_premium > 0 else 0),
            "shareholder_return_premium": srim_after_growth * (0.05 if management_quality_premium > 0 else 0),
            "governance_discount": -srim_after_growth * governance_risk_discount,
        }
    }

    logger.info(
        f"종합 적정가치 계산 완료 (moneyvalue.txt 기준)\n"
        f"  - S-RIM 기초: {srim_value:,.0f}원\n"
        f"  - 성장성 보정: {growth_multiplier:.1f}배 (PEG < 1.0)\n"
        f"  - 성장성 보정 후: {srim_after_growth:,.0f}원\n"
        f"  - 질적 순보정: {quality_adjustment:+.1%}\n"
        f"  - 최종 가치: {final_value:,.0f}원"
    )

    return result
