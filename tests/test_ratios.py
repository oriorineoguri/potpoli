"""
재무 비율 계산 모듈 테스트
"""

import pytest
from src.analysis.ratios import calculate_per_ratio


class TestCalculatePerRatio:
    """PER 계산 함수 테스트"""

    def test_normal_per_calculation(self):
        """정상적인 PER 계산 테스트"""
        # Given: 주가 50,000원, EPS 5,000원
        stock_price = 50000
        eps = 5000

        # When: PER 계산
        result = calculate_per_ratio(stock_price, eps)

        # Then: PER = 10.0
        assert result == 10.0

    def test_high_per_calculation(self):
        """높은 PER 계산 테스트 (성장주)"""
        # Given: 주가 100,000원, EPS 1,000원
        stock_price = 100000
        eps = 1000

        # When: PER 계산
        result = calculate_per_ratio(stock_price, eps)

        # Then: PER = 100.0
        assert result == 100.0

    def test_low_per_calculation(self):
        """낮은 PER 계산 테스트 (가치주)"""
        # Given: 주가 10,000원, EPS 2,000원
        stock_price = 10000
        eps = 2000

        # When: PER 계산
        result = calculate_per_ratio(stock_price, eps)

        # Then: PER = 5.0
        assert result == 5.0

    def test_zero_eps(self):
        """EPS가 0인 경우 테스트"""
        # Given: EPS = 0
        stock_price = 50000
        eps = 0

        # When: PER 계산
        result = calculate_per_ratio(stock_price, eps)

        # Then: None 반환
        assert result is None

    def test_negative_eps(self):
        """EPS가 음수인 경우 테스트 (적자 기업)"""
        # Given: EPS = -1000 (적자)
        stock_price = 50000
        eps = -1000

        # When: PER 계산
        result = calculate_per_ratio(stock_price, eps)

        # Then: None 반환
        assert result is None

    def test_zero_stock_price(self):
        """주가가 0인 경우 테스트"""
        # Given: 주가 = 0
        stock_price = 0
        eps = 5000

        # When & Then: ValueError 발생
        with pytest.raises(ValueError, match="주가는 0보다 커야 합니다"):
            calculate_per_ratio(stock_price, eps)

    def test_negative_stock_price(self):
        """주가가 음수인 경우 테스트"""
        # Given: 주가 = -10000
        stock_price = -10000
        eps = 5000

        # When & Then: ValueError 발생
        with pytest.raises(ValueError, match="주가는 0보다 커야 합니다"):
            calculate_per_ratio(stock_price, eps)

    def test_decimal_values(self):
        """소수점 값 계산 테스트"""
        # Given: 주가 50,123.45원, EPS 4,567.89원
        stock_price = 50123.45
        eps = 4567.89

        # When: PER 계산
        result = calculate_per_ratio(stock_price, eps)

        # Then: PER ≈ 10.97
        assert result is not None
        assert abs(result - 10.97) < 0.01
