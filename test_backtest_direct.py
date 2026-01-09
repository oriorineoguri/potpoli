"""
백테스트 엔진 직접 테스트
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

def test_backtest_direct():
    """백테스트 엔진 직접 테스트"""

    print("=" * 70)
    print("백테스트 엔진 직접 테스트")
    print("=" * 70)
    print()

    # 백테스트 엔진 생성
    engine = BacktestEngine(use_cache=True)

    # 삼성전자, 2023-01-01 시작
    tickers = ["005930.KS"]
    start_date = datetime(2023, 1, 1)

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
    print(f"결과 개수: {len(result['results'])}")
    print()

    if result['results']:
        for r in result['results']:
            # 모든 키 출력 (디버깅용)
            print("결과 키:", list(r.keys()))
            print()

            # 주요 정보 출력
            for key, value in r.items():
                if isinstance(value, (int, float)) and value > 1000:
                    print(f"{key}: {value:,.0f}")
                else:
                    print(f"{key}: {value}")
            print()
    else:
        print("[경고] 결과 없음")

if __name__ == "__main__":
    test_backtest_direct()
