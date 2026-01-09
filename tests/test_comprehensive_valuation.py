"""
종합 밸류에이션 통합 테스트

S-RIM 기반 4단계 적정가치 계산 모델의 전체 파이프라인을 테스트합니다.
"""

import pytest
from src.analysis import (
    calculate_per_ratio,
    calculate_pbr_ratio,
    calculate_peg_ratio,
    calculate_srim_value,
    calculate_fair_value_comprehensive,
    evaluate_economic_moat,
    evaluate_management_quality
)


class TestComprehensiveValuation:
    """종합 밸류에이션 통합 테스트"""

    def test_complete_valuation_pipeline_growth_stock(self):
        """
        성장주 완전 밸류에이션 테스트

        시나리오: AI 반도체 기업 A사
        - 자기자본: 5조 원
        - ROE: 18%
        - PER: 25, EPS: 4,000원 → 주가 100,000원
        - 이익성장률: 30%
        - 경제적 해자: 넓음 (특허, 브랜드, 기술력)
        - 경영진: 우수
        """
        # 1단계: S-RIM 기초 가치 계산
        equity = 5_000_000_000_000  # 5조 원
        roe = 0.18
        required_return = 0.08

        srim_value = calculate_srim_value(equity, roe, required_return)

        # 예상값: 5조 + (5조 × (0.18 - 0.08)) / 0.08 = 5조 + 6.25조 = 11.25조
        assert abs(srim_value - 11_250_000_000_000) < 1_000_000_000  # 10억 오차 허용

        # 2단계: 성장성 평가 (PEG)
        stock_price = 100_000
        eps = 4_000
        per = calculate_per_ratio(stock_price, eps)
        assert per == 25.0

        earnings_growth_rate = 30.0  # 30%
        peg = calculate_peg_ratio(per, earnings_growth_rate)
        assert abs(peg - 0.833) < 0.01  # PEG < 1.0 → 저평가

        # 3단계: 질적 평가
        # 경제적 해자: 특허 + 브랜드 + 기술력 = 넓은 해자
        moat_result = evaluate_economic_moat(
            has_brand_power=True,
            has_intangible_assets=True,  # 특허
            has_cost_advantage=True  # 기술 우위
        )
        assert moat_result["moat_count"] == 3
        assert moat_result["premium_rate"] == 0.25  # +25%

        # 경영진: 우수 (평균 4.5점)
        mgmt_result = evaluate_management_quality(
            transparency_score=5,
            shareholder_return_score=4,
            capital_allocation_score=4,
            governance_score=5
        )
        assert mgmt_result["avg_score"] == 4.5
        assert mgmt_result["premium_rate"] == 0.075  # +7.5%

        # 4단계: 최종 적정가치 계산
        fair_value_result = calculate_fair_value_comprehensive(
            srim_value=srim_value,
            peg_ratio=peg,  # < 0.5이면 추가 가산
            economic_moat_premium=moat_result["premium_rate"],
            management_quality_premium=mgmt_result["premium_rate"],
            governance_risk_discount=mgmt_result["discount_rate"]
        )

        # 예상 최종가치: 11.25조 × (1 + 0.25 + 0.075) = 11.25조 × 1.325 = 14.9조
        expected_final_value = srim_value * 1.325
        assert abs(fair_value_result["final_value"] - expected_final_value) < 1_000_000_000

        # 검증: 최종 가치가 기초 가치보다 높아야 함 (프리미엄)
        assert fair_value_result["final_value"] > srim_value

    def test_complete_valuation_pipeline_value_stock(self):
        """
        가치주 완전 밸류에이션 테스트

        시나리오: 전통 제조업 B사
        - 자기자본: 2조 원
        - ROE: 8% (기대수익률과 동일)
        - PER: 5, PBR: 0.8
        - 성장률: 거의 없음
        - 경제적 해자: 좁음 (일부 원가 우위)
        - 경영진: 보통
        """
        # 1단계: S-RIM 기초 가치
        equity = 2_000_000_000_000  # 2조 원
        roe = 0.08
        required_return = 0.08

        srim_value = calculate_srim_value(equity, roe, required_return)

        # ROE = 기대수익률 → 기업가치 = 자기자본 = 2조
        assert abs(srim_value - equity) < 1_000_000

        # 2단계: PBR 확인
        stock_price = 20_000
        bps = 25_000  # PBR 0.8
        pbr = calculate_pbr_ratio(stock_price, bps)
        assert abs(pbr - 0.8) < 0.01  # PBR < 1.0 → 저평가 (안전마진)

        # 3단계: 질적 평가
        moat_result = evaluate_economic_moat(
            has_cost_advantage=True  # 원가 우위만 있음
        )
        assert moat_result["moat_count"] == 1
        assert moat_result["premium_rate"] == 0.125  # +12.5%

        mgmt_result = evaluate_management_quality(
            transparency_score=3,
            shareholder_return_score=3,
            capital_allocation_score=3,
            governance_score=3
        )
        assert mgmt_result["avg_score"] == 3.0
        assert mgmt_result["net_adjustment"] == 0.0  # 보통 수준

        # 4단계: 최종 가치
        fair_value_result = calculate_fair_value_comprehensive(
            srim_value=srim_value,
            peg_ratio=None,  # 성장주 아님
            economic_moat_premium=moat_result["premium_rate"],
            management_quality_premium=mgmt_result["premium_rate"],
            governance_risk_discount=mgmt_result["discount_rate"]
        )

        # 예상: 2조 × (1 + 0.125) = 2.25조
        expected_final_value = srim_value * 1.125
        assert abs(fair_value_result["final_value"] - expected_final_value) < 1_000_000

    def test_complete_valuation_pipeline_risky_stock(self):
        """
        리스크 있는 기업 밸류에이션 테스트

        시나리오: 거버넌스 문제가 있는 C사
        - 자기자본: 1조 원
        - ROE: 12%
        - 경제적 해자: 없음
        - 경영진: 불투명 경영, 주주환원 부족
        """
        # 1단계: S-RIM
        equity = 1_000_000_000_000
        roe = 0.12
        required_return = 0.08

        srim_value = calculate_srim_value(equity, roe, required_return)

        # 1조 + (1조 × (0.12 - 0.08)) / 0.08 = 1조 + 0.5조 = 1.5조
        assert abs(srim_value - 1_500_000_000_000) < 1_000_000

        # 3단계: 질적 평가 - 해자 없음
        moat_result = evaluate_economic_moat()
        assert moat_result["moat_count"] == 0
        assert moat_result["premium_rate"] == 0.0

        # 경영진: 나쁨 (평균 2점)
        mgmt_result = evaluate_management_quality(
            transparency_score=2,
            shareholder_return_score=2,
            capital_allocation_score=2,
            governance_score=2
        )
        assert mgmt_result["avg_score"] == 2.0
        assert mgmt_result["discount_rate"] == 0.20  # -20% 디스카운트

        # 4단계: 최종 가치 (큰 폭 할인)
        fair_value_result = calculate_fair_value_comprehensive(
            srim_value=srim_value,
            peg_ratio=None,
            economic_moat_premium=0.0,
            management_quality_premium=0.0,
            governance_risk_discount=0.20
        )

        # 예상: 1.5조 × (1 - 0.20) = 1.2조
        expected_final_value = srim_value * 0.8
        assert abs(fair_value_result["final_value"] - expected_final_value) < 1_000_000

        # 거버넌스 리스크로 인해 가치 하락
        assert fair_value_result["final_value"] < srim_value
