"""
밸류에이션 모델 테스트 (S-RIM, DCF)
"""

import pytest
from src.analysis.valuation import (
    calculate_srim_value,
    calculate_dcf_value,
    calculate_fair_value_comprehensive
)


class TestSRIMValuation:
    """S-RIM 밸류에이션 테스트"""

    def test_srim_positive_excess_return(self):
        """ROE가 기대수익률보다 높은 경우 (초과 수익)"""
        # Given: 자기자본 1조, ROE 15%, 기대수익률 8%
        equity = 1_000_000_000_000
        roe = 0.15
        required_return = 0.08

        # When: S-RIM 계산
        result = calculate_srim_value(equity, roe, required_return)

        # Then: 기업가치 = 1조 + (1조 × 0.07) / 0.08 = 1.875조
        expected = equity + (equity * (roe - required_return) / required_return)
        assert abs(result - expected) < 1_000_000
        assert result > equity  # 프리미엄 발생

    def test_srim_zero_excess_return(self):
        """ROE = 기대수익률인 경우 (초과 수익 없음)"""
        # Given: ROE = 기대수익률
        equity = 2_000_000_000_000
        roe = 0.10
        required_return = 0.10

        # When
        result = calculate_srim_value(equity, roe, required_return)

        # Then: 기업가치 = 자기자본 (프리미엄 없음)
        assert abs(result - equity) < 1_000_000

    def test_srim_negative_excess_return(self):
        """ROE < 기대수익률인 경우 (가치 훼손)"""
        # Given: ROE 5%, 기대수익률 8%
        equity = 1_000_000_000_000
        roe = 0.05
        required_return = 0.08

        # When
        result = calculate_srim_value(equity, roe, required_return)

        # Then: 기업가치 < 자기자본 (디스카운트)
        assert result < equity

    def test_srim_invalid_equity(self):
        """자기자본이 0 이하인 경우 (자본잠식)"""
        with pytest.raises(ValueError, match="자기자본은 0보다 커야"):
            calculate_srim_value(-100_000_000_000, 0.10, 0.08)

    def test_srim_invalid_required_return(self):
        """기대수익률이 0 이하인 경우"""
        with pytest.raises(ValueError, match="기대수익률은 0보다 커야"):
            calculate_srim_value(1_000_000_000_000, 0.10, 0.0)


class TestDCFValuation:
    """DCF 밸류에이션 테스트"""

    def test_dcf_basic_calculation(self):
        """기본 DCF 계산 테스트"""
        # Given: 5년간 FCF (억 단위)
        fcf = [
            100_000_000_000,  # 1000억
            110_000_000_000,  # 1100억 (10% 성장)
            121_000_000_000,  # 1210억
            133_000_000_000,  # 1331억
            146_000_000_000   # 1464억
        ]
        terminal_growth = 0.02  # 2%
        discount_rate = 0.10    # 10%

        # When
        result = calculate_dcf_value(fcf, terminal_growth, discount_rate)

        # Then: 결과가 양수이고 합리적인 범위
        assert result > 0
        assert result > sum(fcf)  # 영구가치 포함하므로 합계보다 큼

    def test_dcf_high_growth_company(self):
        """고성장 기업 DCF 테스트"""
        # Given: 연 30% 고성장
        base_fcf = 50_000_000_000  # 500억
        fcf = [base_fcf * (1.3 ** i) for i in range(1, 6)]  # 5년간 30% 성장

        # When
        result = calculate_dcf_value(fcf, 0.03, 0.12)

        # Then: 마지막 FCF의 8배 이상 (고성장 프리미엄)
        # 할인율 12% - 영구성장률 3% = 9% 스프레드
        # 영구가치 배수 ≈ 1.03/0.09 ≈ 11배이지만 현재가치 할인 고려
        assert result > fcf[-1] * 8

    def test_dcf_mature_company(self):
        """성숙 기업 DCF 테스트 (저성장)"""
        # Given: 안정적 FCF (성장률 낮음)
        fcf = [200_000_000_000] * 5  # 5년간 2000억 유지

        # When
        result = calculate_dcf_value(fcf, 0.01, 0.08)

        # Then
        assert result > sum(fcf)

    def test_dcf_empty_fcf_list(self):
        """FCF 리스트가 비어있는 경우"""
        with pytest.raises(ValueError, match="최소 1개 이상의 값이 필요"):
            calculate_dcf_value([], 0.02, 0.10)

    def test_dcf_invalid_discount_rate(self):
        """할인율이 영구성장률보다 작은 경우"""
        fcf = [100_000_000_000]

        with pytest.raises(ValueError, match="할인율은 영구성장률보다 커야"):
            calculate_dcf_value(fcf, 0.10, 0.08)  # 할인율 8% < 성장률 10%

    def test_dcf_single_year_fcf(self):
        """1년치 FCF만 있는 경우"""
        # Given
        fcf = [150_000_000_000]  # 1500억

        # When
        result = calculate_dcf_value(fcf, 0.02, 0.10)

        # Then: 영구가치 기반 계산
        # TV = 1500억 × 1.02 / 0.08 = 19125억
        # PV(TV) = 19125 / 1.1 ≈ 17386억
        # PV(FCF) = 1500 / 1.1 ≈ 1364억
        # Total ≈ 18750억
        assert result > fcf[0] * 10

    def test_dcf_comparison_with_srim(self):
        """
        DCF와 S-RIM 교차 검증 테스트

        동일한 기업의 가치를 두 모델로 계산하여 유사한지 확인
        """
        # Given: 우량 기업 데이터
        equity = 5_000_000_000_000  # 자기자본 5조
        roe = 0.12
        required_return = 0.08

        # S-RIM 계산
        srim_value = calculate_srim_value(equity, roe, required_return)
        # 5조 + (5조 × 0.04 / 0.08) = 7.5조

        # DCF 계산 (유사한 FCF 가정)
        # ROE 12% → 연간 이익 6000억
        # FCF를 이익의 70%로 가정 → 4200억
        annual_profit = equity * roe
        fcf_ratio = 0.70
        base_fcf = annual_profit * fcf_ratio
        fcf = [base_fcf * (1.05 ** i) for i in range(5)]  # 5년간 5% 성장

        dcf_value = calculate_dcf_value(fcf, 0.02, 0.08)

        # Then: 두 모델의 결과가 ±30% 범위 내 (합리적 오차)
        ratio = dcf_value / srim_value
        assert 0.7 <= ratio <= 1.3, f"DCF/S-RIM 비율: {ratio:.2f} (범위 벗어남)"


class TestComprehensiveFairValue:
    """종합 적정가치 계산 테스트"""

    def test_fair_value_all_premium(self):
        """모든 가산점이 적용되는 경우"""
        # Given
        srim_value = 10_000_000_000_000  # 10조

        # When: PEG < 0.5, 해자 25%, 경영진 7.5%
        result = calculate_fair_value_comprehensive(
            srim_value=srim_value,
            peg_ratio=0.4,  # < 0.5 → +15% 가산
            economic_moat_premium=0.25,
            management_quality_premium=0.075,
            governance_risk_discount=0.0
        )

        # Then: 총 +47.5% (15 + 25 + 7.5)
        expected = srim_value * 1.475
        assert abs(result["final_value"] - expected) < 1_000_000_000

    def test_fair_value_with_discount(self):
        """거버넌스 리스크로 디스카운트되는 경우"""
        # Given
        srim_value = 5_000_000_000_000

        # When: 해자는 있지만 거버넌스 문제
        result = calculate_fair_value_comprehensive(
            srim_value=srim_value,
            peg_ratio=None,
            economic_moat_premium=0.15,
            management_quality_premium=0.0,
            governance_risk_discount=0.30  # -30%
        )

        # Then: +15% - 30% = -15%
        expected = srim_value * 0.85
        assert abs(result["final_value"] - expected) < 1_000_000_000
        assert result["final_value"] < srim_value

    def test_fair_value_no_adjustment(self):
        """보정 없는 경우"""
        # Given
        srim_value = 3_000_000_000_000

        # When: 모든 가산/감산 0
        result = calculate_fair_value_comprehensive(
            srim_value=srim_value,
            peg_ratio=1.5,  # > 0.5 → 가산 없음
            economic_moat_premium=0.0,
            management_quality_premium=0.0,
            governance_risk_discount=0.0
        )

        # Then: 가치 변화 없음
        assert abs(result["final_value"] - srim_value) < 1_000_000

    def test_fair_value_breakdown_structure(self):
        """결과 구조 검증"""
        # Given
        srim_value = 1_000_000_000_000

        # When
        result = calculate_fair_value_comprehensive(
            srim_value=srim_value,
            peg_ratio=0.3,
            economic_moat_premium=0.20,
            management_quality_premium=0.05,
            governance_risk_discount=0.10
        )

        # Then: 필수 키 존재 확인
        assert "base_value" in result
        assert "growth_adjustment" in result
        assert "quality_adjustment" in result
        assert "total_adjustment" in result
        assert "final_value" in result
        assert "breakdown" in result

        # Breakdown 상세 항목
        assert "srim_base" in result["breakdown"]
        assert "peg_premium" in result["breakdown"]
        assert "economic_moat_premium" in result["breakdown"]
        assert "management_premium" in result["breakdown"]
        assert "governance_discount" in result["breakdown"]

    def test_fair_value_invalid_srim(self):
        """잘못된 S-RIM 값"""
        with pytest.raises(ValueError, match="S-RIM 가치는 0보다 커야"):
            calculate_fair_value_comprehensive(
                srim_value=-1_000_000_000_000,
                peg_ratio=None,
                economic_moat_premium=0.0,
                management_quality_premium=0.0,
                governance_risk_discount=0.0
            )
