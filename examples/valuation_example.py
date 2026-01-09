"""
실전 주식 밸류에이션 예제

실제 API를 사용하여 삼성전자의 적정가치를 계산합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.fetcher_real import RealStockDataFetcher, get_real_stock_price
from src.analysis import (
    calculate_per_ratio,
    calculate_pbr_ratio,
    calculate_srim_value,
    calculate_fair_value_comprehensive,
    evaluate_economic_moat,
    evaluate_management_quality
)


def analyze_samsung_electronics():
    """
    삼성전자 종합 밸류에이션 분석

    실제 Yahoo Finance 데이터를 사용하여 S-RIM 기반 적정가치를 계산합니다.
    """
    print("=" * 70)
    print("삼성전자 종합 밸류에이션 분석".center(70))
    print("=" * 70)
    print()

    # 1단계: 실제 데이터 수집
    print("[ 1단계: 실제 데이터 수집 ]")
    print("-" * 70)

    fetcher = RealStockDataFetcher(use_cache=True)
    ticker = "005930.KS"  # 삼성전자

    # 주가 정보
    current_price = fetcher.get_current_price(ticker)
    print(f"현재 주가: {current_price:,.0f}원")

    # 재무 정보
    info = fetcher.fetch_financial_info(ticker)
    print(f"회사명: {info['company_name']}")
    print(f"시가총액: {info['market_cap']:,.0f}원 ({info['market_cap'] / 1_000_000_000_000:.1f}조원)")

    if info['roe']:
        print(f"ROE: {info['roe']:.2%}")
    if info['pe_ratio']:
        print(f"PER: {info['pe_ratio']:.2f}")
    if info['pb_ratio']:
        print(f"PBR: {info['pb_ratio']:.2f}")

    print()

    # 2단계: S-RIM 기초 가치 계산
    print("[ 2단계: S-RIM 기초 가치 계산 ]")
    print("-" * 70)

    # 자기자본 추정 (시가총액과 PBR로 역산)
    if info['pb_ratio'] and info['pb_ratio'] > 0:
        equity = info['market_cap'] / info['pb_ratio']
    else:
        # PBR이 없으면 BPS와 발행주식수로 계산
        if info['book_value'] and info['shares_outstanding']:
            equity = info['book_value'] * info['shares_outstanding']
        else:
            # 기본값 사용 (시가총액의 80%로 가정)
            equity = info['market_cap'] * 0.8

    roe = info.get('roe', 0.10)  # ROE가 없으면 10% 가정
    required_return = 0.08  # 기대수익률 8%

    srim_value = calculate_srim_value(equity, roe, required_return)

    print(f"자기자본: {equity:,.0f}원 ({equity / 1_000_000_000_000:.1f}조원)")
    print(f"ROE: {roe:.2%}")
    print(f"기대수익률: {required_return:.2%}")
    print(f"S-RIM 기초 가치: {srim_value:,.0f}원 ({srim_value / 1_000_000_000_000:.1f}조원)")
    print()

    # 3단계: 질적 평가
    print("[ 3단계: 질적 평가 ]")
    print("-" * 70)

    # 경제적 해자 평가 (삼성전자는 강력한 해자 보유)
    moat_result = evaluate_economic_moat(
        has_brand_power=True,        # 삼성 브랜드
        has_switching_cost=False,    # 스마트폰은 전환비용 낮음
        has_network_effect=False,
        has_cost_advantage=True,      # 반도체 대규모 생산
        has_intangible_assets=True    # 특허, 기술력
    )

    print(f"경제적 해자 개수: {moat_result['moat_count']}")
    print(f"해자 강도: {moat_result['moat_strength'].name}")
    print(f"해자 프리미엄: +{moat_result['premium_rate']:.1%}")
    print()

    # 경영진 평가 (삼성전자는 우수한 경영진)
    mgmt_result = evaluate_management_quality(
        transparency_score=4,         # 투명성 양호
        shareholder_return_score=4,   # 배당 꾸준히 증가
        capital_allocation_score=5,   # 반도체 투자 우수
        governance_score=3            # 지배구조는 보통
    )

    print(f"경영진 평균 점수: {mgmt_result['avg_score']:.1f}/5.0")
    print(f"경영진 프리미엄: +{mgmt_result['premium_rate']:.1%}")
    print(f"거버넌스 리스크: -{mgmt_result['discount_rate']:.1%}")
    print()

    # 4단계: 최종 적정가치 계산
    print("[ 4단계: 최종 적정가치 계산 ]")
    print("-" * 70)

    # PEG 계산 (성장률 가정: 한국 반도체 평균 10%)
    peg_ratio = None
    if info['pe_ratio']:
        earnings_growth = 10.0  # 10% 성장 가정
        peg_ratio = info['pe_ratio'] / earnings_growth
        print(f"PEG: {peg_ratio:.2f} (PER {info['pe_ratio']:.1f} / 성장률 {earnings_growth}%)")

    fair_value_result = calculate_fair_value_comprehensive(
        srim_value=srim_value,
        peg_ratio=peg_ratio,
        economic_moat_premium=moat_result['premium_rate'],
        management_quality_premium=mgmt_result['premium_rate'],
        governance_risk_discount=mgmt_result['discount_rate']
    )

    final_value = fair_value_result['final_value']
    total_adjustment = fair_value_result['total_adjustment']

    print(f"S-RIM 기초 가치: {srim_value:,.0f}원 ({srim_value / 1_000_000_000_000:.1f}조원)")
    print(f"총 조정률: {total_adjustment:+.1%}")
    print(f"  - 성장성 가산: +{fair_value_result['growth_adjustment']:.1%}")
    print(f"  - 질적 조정: {fair_value_result['quality_adjustment']:+.1%}")
    print(f"최종 적정 기업가치: {final_value:,.0f}원 ({final_value / 1_000_000_000_000:.1f}조원)")
    print()

    # 5단계: 투자 판단
    print("[ 5단계: 투자 판단 ]")
    print("=" * 70)

    market_cap = info['market_cap']
    diff_percent = ((final_value - market_cap) / market_cap) * 100

    print(f"현재 시가총액: {market_cap:,.0f}원 ({market_cap / 1_000_000_000_000:.1f}조원)")
    print(f"적정 기업가치: {final_value:,.0f}원 ({final_value / 1_000_000_000_000:.1f}조원)")
    print(f"차이: {diff_percent:+.1f}%")
    print()

    if diff_percent > 20:
        judgment = "저평가 (매수 고려)"
        color = "green"
    elif diff_percent < -20:
        judgment = "고평가 (매도 고려)"
        color = "red"
    else:
        judgment = "적정가 (보유)"
        color = "yellow"

    print(f"투자 판단: {judgment}")
    print()

    # 적정 주가 계산
    shares_outstanding = info.get('shares_outstanding', 0)
    if shares_outstanding > 0:
        fair_price_per_share = final_value / shares_outstanding
        print(f"현재 주가: {current_price:,.0f}원")
        print(f"적정 주가: {fair_price_per_share:,.0f}원")
        print(f"주가 차이: {((fair_price_per_share - current_price) / current_price * 100):+.1f}%")

    print()
    print("=" * 70)
    print("주의: 이 분석은 참고용이며, 실제 투자 판단은 본인 책임입니다.".center(70))
    print("=" * 70)


if __name__ == "__main__":
    analyze_samsung_electronics()
