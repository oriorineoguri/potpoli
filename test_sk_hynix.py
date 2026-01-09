"""
SK하이닉스 백테스트 디버깅
"""

import logging
import sys
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

from src.backtest.engine import BacktestEngine

def test_sk_hynix():
    """SK하이닉스 백테스트 디버깅"""

    print("=" * 70)
    print("SK하이닉스 백테스트 디버깅")
    print("=" * 70)
    print()

    # 백테스트 엔진 생성
    engine = BacktestEngine(use_cache=True)

    # SK하이닉스, 2024-01-09 시작
    tickers = ["000660.KS"]
    start_date = datetime(2024, 1, 9)

    print(f"종목: {tickers}")
    print(f"시작일: {start_date.date()}")
    print()

    # 백테스트 실행
    result = engine.run_backtest(tickers, start_date, {})

    print()
    print("=" * 70)
    print("백테스트 결과:")
    print("=" * 70)
    print()

    if result['results']:
        for r in result['results']:
            print(f"종목: {r['ticker']}")
            print(f"회사명: {r['company_name']}")
            print(f"시작일: {r['start_date']}")
            print(f"시작가: {r['initial_price']:,.0f}원")
            print(f"적정가: {r['fair_value']:,.0f}원")
            print(f"상승여력: {r['upside_percent']:.1f}%")
            print(f"판단: {r['judgment']}")
            print()
    else:
        print("[경고] 결과 없음")

if __name__ == "__main__":
    test_sk_hynix()
