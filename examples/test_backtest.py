"""
백테스트 예시 실행

2023-01-01 기준으로 주요 종목들의 백테스트를 실행합니다.
"""

import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.backtest.engine import BacktestEngine


def main():
    print("=" * 70)
    print("백테스트 예시 실행".center(70))
    print("=" * 70)
    print()

    # 백테스트 엔진 초기화
    engine = BacktestEngine(use_cache=True)

    # 분석할 종목들
    tickers = [
        "005930",  # 삼성전자
        "000660",  # SK하이닉스
        "035720",  # 카카오
        "035420",  # NAVER
    ]

    # 백테스트 시작 날짜
    start_date = datetime(2023, 1, 1)

    print(f"분석 종목: {', '.join(tickers)}")
    print(f"시작 날짜: {start_date.strftime('%Y-%m-%d')}")
    print()
    print("백테스트 실행 중...")
    print()

    # 백테스트 실행
    result = engine.run_backtest(tickers, start_date)

    # 결과 출력
    print("=" * 70)
    print("백테스트 결과".center(70))
    print("=" * 70)
    print()

    summary = result['summary']
    print(f"총 종목 수: {summary['total_stocks']}개")
    print(f"저평가 추천: {summary['recommended_stocks']}개")
    print(f"성공률: {summary['success_rate']}%")
    print()

    if summary.get('avg_one_month_return') is not None:
        print(f"1개월 평균 수익률: {summary['avg_one_month_return']:+.2f}%")
    if summary.get('avg_six_month_return') is not None:
        print(f"6개월 평균 수익률: {summary['avg_six_month_return']:+.2f}%")
    if summary.get('avg_one_year_return') is not None:
        print(f"1년 평균 수익률: {summary['avg_one_year_return']:+.2f}%")
    if summary.get('avg_current_return') is not None:
        print(f"현재까지 평균 수익률: {summary['avg_current_return']:+.2f}%")

    print()
    print("=" * 70)
    print("종목별 상세 결과".center(70))
    print("=" * 70)
    print()

    for stock in result['results']:
        print(f"[{stock['company_name']}]")
        print(f"  시작가: {stock['initial_price']:,.0f}원")
        print(f"  적정가: {stock['fair_value']:,.0f}원")
        print(f"  상승여력: {stock['upside_percent']:+.1f}%")
        print(f"  판단: {stock['judgment']}")
        print()

        if stock['one_month_return'] is not None:
            print(f"  1개월 수익률: {stock['one_month_return']:+.2f}%")
        if stock['six_month_return'] is not None:
            print(f"  6개월 수익률: {stock['six_month_return']:+.2f}%")
        if stock['one_year_return'] is not None:
            print(f"  1년 수익률: {stock['one_year_return']:+.2f}%")
        if stock['current_return'] is not None:
            print(f"  현재 수익률: {stock['current_return']:+.2f}%")

        if stock['recommended']:
            success_str = "[성공]" if stock['success'] else "[실패]"
            print(f"  추천 여부: 저평가 추천 {success_str}")

        print()

    print("=" * 70)


if __name__ == "__main__":
    main()
