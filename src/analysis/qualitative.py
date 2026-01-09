"""
질적 평가 모듈

경제적 해자, 경영진 역량 등 정성적 요소를 평가합니다.

참고 문헌:
- "The Little Book That Builds Wealth" by Pat Dorsey (경제적 해자)
- "Good to Great" by Jim Collins (경영진 평가)
"""

import logging
from typing import Dict
from enum import Enum

logger = logging.getLogger(__name__)


class MoatStrength(Enum):
    """경제적 해자 강도"""
    NONE = 0  # 해자 없음
    NARROW = 1  # 좁은 해자
    WIDE = 2  # 넓은 해자


def evaluate_economic_moat(
    has_brand_power: bool = False,
    has_switching_cost: bool = False,
    has_network_effect: bool = False,
    has_cost_advantage: bool = False,
    has_intangible_assets: bool = False
) -> Dict[str, any]:
    """
    경제적 해자 (Economic Moat) 평가 함수

    기업이 경쟁우위를 유지할 수 있는 구조적 장벽을 평가합니다.

    **경제적 해자 5가지 유형:**
    1. **브랜드 파워**: 독점적 브랜드 가치 (예: 애플, 코카콜라)
    2. **전환 비용**: 고객이 다른 제품으로 바꾸기 어려움 (예: SAP, Oracle)
    3. **네트워크 효과**: 사용자 많을수록 가치 증가 (예: 카카오, 네이버)
    4. **원가 우위**: 구조적 비용 이점 (예: 코스트코, 포스코)
    5. **무형 자산**: 특허, 라이선스, 규제 장벽 (예: 제약사, 통신사)

    **평가 기준:**
    - 해자 없음 (0개): 프리미엄 0%
    - 좁은 해자 (1~2개): 프리미엄 +10~15%
    - 넓은 해자 (3개 이상): 프리미엄 +20~30%

    Args:
        has_brand_power: 브랜드 파워 보유 여부
        has_switching_cost: 높은 전환 비용 여부
        has_network_effect: 네트워크 효과 존재 여부
        has_cost_advantage: 원가 우위 보유 여부
        has_intangible_assets: 무형 자산(특허 등) 보유 여부

    Returns:
        dict: {
            'moat_count': 해자 개수,
            'moat_strength': MoatStrength (NONE/NARROW/WIDE),
            'premium_rate': 권장 프리미엄율 (소수),
            'details': 상세 해자 정보
        }

    Examples:
        >>> evaluate_economic_moat(
        ...     has_brand_power=True,
        ...     has_network_effect=True,
        ...     has_switching_cost=True
        ... )
        {'moat_count': 3,
         'moat_strength': MoatStrength.WIDE,
         'premium_rate': 0.25,
         ...}

    Note:
        이 평가는 정성적 판단이 필요하므로, 사용자가 각 항목을 직접 입력해야 합니다.
        자동화를 위해서는 뉴스/공시 분석 AI를 추가로 구현해야 합니다.
    """
    # 해자 요소 집계
    moat_factors = {
        "brand_power": has_brand_power,
        "switching_cost": has_switching_cost,
        "network_effect": has_network_effect,
        "cost_advantage": has_cost_advantage,
        "intangible_assets": has_intangible_assets
    }

    moat_count = sum(moat_factors.values())

    # 해자 강도 및 프리미엄 결정
    if moat_count == 0:
        moat_strength = MoatStrength.NONE
        premium_rate = 0.0
    elif moat_count <= 2:
        moat_strength = MoatStrength.NARROW
        premium_rate = 0.125  # 12.5% (10~15% 중간값)
    else:  # 3개 이상
        moat_strength = MoatStrength.WIDE
        premium_rate = 0.25  # 25% (20~30% 중간값)

    result = {
        "moat_count": moat_count,
        "moat_strength": moat_strength,
        "premium_rate": premium_rate,
        "details": {
            k: v for k, v in moat_factors.items() if v
        }
    }

    logger.info(
        f"경제적 해자 평가 완료 - "
        f"해자 개수: {moat_count}, 강도: {moat_strength.name}, "
        f"프리미엄: +{premium_rate:.1%}"
    )

    return result


def evaluate_management_quality(
    transparency_score: int = 3,
    shareholder_return_score: int = 3,
    capital_allocation_score: int = 3,
    governance_score: int = 3
) -> Dict[str, any]:
    """
    경영진 역량 및 거버넌스 평가 함수

    경영진의 주주 친화적 경영, 투명성, 자본 배분 능력을 평가합니다.

    **평가 항목 (각 1~5점):**
    1. **투명성**: 적극적 공시, 명확한 커뮤니케이션
    2. **주주환원**: 배당, 자사주 소각, 주주가치 중시
    3. **자본배분**: ROE/ROIC 개선, 현명한 M&A
    4. **거버넌스**: 이사회 독립성, 공정한 의사결정

    **점수 기준:**
    - 1점: 매우 나쁨 (횡령, 배임, 불투명 경영)
    - 2점: 나쁨 (주주환원 부족, 일감 몰아주기)
    - 3점: 보통 (평균적 수준)
    - 4점: 좋음 (적극적 주주환원, 투명한 경영)
    - 5점: 매우 좋음 (모범적 ESG 경영)

    **프리미엄/디스카운트:**
    - 평균 4점 이상: +5~10% 프리미엄
    - 평균 3점: 보정 없음 (0%)
    - 평균 2점 이하: -20~50% 디스카운트

    Args:
        transparency_score: 투명성 점수 (1~5)
        shareholder_return_score: 주주환원 점수 (1~5)
        capital_allocation_score: 자본배분 점수 (1~5)
        governance_score: 거버넌스 점수 (1~5)

    Returns:
        dict: {
            'avg_score': 평균 점수,
            'premium_rate': 경영진 역량 프리미엄율 (양수),
            'discount_rate': 거버넌스 리스크 디스카운트율 (양수),
            'net_adjustment': 순 조정률 (프리미엄 - 디스카운트)
        }

    Examples:
        >>> evaluate_management_quality(
        ...     transparency_score=5,
        ...     shareholder_return_score=4,
        ...     capital_allocation_score=4,
        ...     governance_score=5
        ... )
        {'avg_score': 4.5,
         'premium_rate': 0.08,
         'discount_rate': 0.0,
         'net_adjustment': 0.08}

    Note:
        점수는 뉴스, 공시, 재무제표 분석을 통해 평가자가 주관적으로 부여합니다.
        향후 자동화를 위해 ESG 평가 API 또는 NLP 분석 추가 가능합니다.
    """
    # 입력 검증
    scores = [
        transparency_score,
        shareholder_return_score,
        capital_allocation_score,
        governance_score
    ]

    for score in scores:
        if not 1 <= score <= 5:
            logger.error(f"잘못된 점수 입력: {score}")
            raise ValueError(f"점수는 1~5 사이여야 합니다. 입력값: {score}")

    # 평균 점수 계산
    avg_score = sum(scores) / len(scores)

    # 프리미엄/디스카운트 결정
    if avg_score >= 4.0:
        # 우수한 경영진: +5~10% 프리미엄
        premium_rate = 0.075  # 7.5% (중간값)
        discount_rate = 0.0
    elif avg_score >= 3.0:
        # 보통 수준: 조정 없음
        premium_rate = 0.0
        discount_rate = 0.0
    elif avg_score >= 2.0:
        # 미흡한 경영진: -20% 디스카운트
        premium_rate = 0.0
        discount_rate = 0.20
    else:  # < 2.0
        # 심각한 거버넌스 리스크: -35% 디스카운트 (20~50% 중간값)
        premium_rate = 0.0
        discount_rate = 0.35

    net_adjustment = premium_rate - discount_rate

    result = {
        "avg_score": avg_score,
        "premium_rate": premium_rate,
        "discount_rate": discount_rate,
        "net_adjustment": net_adjustment,
        "scores": {
            "transparency": transparency_score,
            "shareholder_return": shareholder_return_score,
            "capital_allocation": capital_allocation_score,
            "governance": governance_score
        }
    }

    logger.info(
        f"경영진 평가 완료 - "
        f"평균 점수: {avg_score:.1f}, "
        f"순조정: {net_adjustment:+.1%} "
        f"(프리미엄 +{premium_rate:.1%}, 리스크 -{discount_rate:.1%})"
    )

    return result
