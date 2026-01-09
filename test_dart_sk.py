"""
SK하이닉스 DART API 테스트
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

from src.data.dart_api import DartApiClient

def test_dart_sk():
    """SK하이닉스 DART API 테스트"""

    print("=" * 70)
    print("SK하이닉스 DART API 테스트")
    print("=" * 70)
    print()

    # DART 클라이언트 생성
    client = DartApiClient()

    # SK하이닉스, 2024-01-09 기준
    ticker = "000660"
    target_date = datetime(2024, 1, 9)

    print(f"종목: {ticker}")
    print(f"기준일: {target_date.date()}")
    print()

    # 재무제표 조회
    result = client.get_financials_at_date(ticker, target_date)

    print()
    print("=" * 70)
    print("최종 결과:")
    print("=" * 70)

    if result:
        for key, value in result.items():
            if isinstance(value, float) and value > 1000:
                print(f"{key}: {value:,.0f}")
            else:
                print(f"{key}: {value}")
    else:
        print("[실패] 결과 없음")

if __name__ == "__main__":
    test_dart_sk()
