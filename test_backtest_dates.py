"""
백테스트 날짜별 비교 테스트
2023-01-01과 2024-01-01의 재무제표와 적정가가 다른지 확인
"""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:5000"

def test_backtest_dates():
    """다른 날짜로 백테스트 실행 후 적정가 비교"""

    print("=" * 70)
    print("백테스트 날짜별 비교 테스트")
    print("=" * 70)
    print()

    # 테스트 데이터
    ticker = "005930.KS"
    dates = ["2023-01-01", "2024-01-01"]

    results = {}

    for date in dates:
        print(f"\n{'=' * 70}")
        print(f"테스트: {date}")
        print(f"{'=' * 70}")

        # 백테스트 요청
        response = requests.post(
            f"{API_URL}/api/backtest",
            json={
                "tickers": [ticker],
                "start_date": date,
                "stock_configs": {}
            }
        )

        if response.status_code == 200:
            data = response.json()

            if data.get('success') and data.get('data', {}).get('results'):
                result = data['data']['results'][0]

                print(f"\n종목: {result['ticker']}")
                print(f"시작일: {result['start_date']}")
                print(f"시작가: {result['initial_price']:,.0f}원")
                print(f"\n[밸류에이션]")
                print(f"적정가: {result['fair_value']:,.0f}원")
                print(f"상승여력: {result['upside_percent']:.1f}%")
                print(f"판단: {result['judgment']}")

                results[date] = result
            else:
                print(f"[오류] 백테스트 결과 없음")
        else:
            print(f"[오류] API 호출 실패: {response.status_code}")

    # 비교
    if len(results) == 2:
        print(f"\n{'=' * 70}")
        print("날짜별 비교")
        print(f"{'=' * 70}")

        date1, date2 = dates
        result1 = results[date1]
        result2 = results[date2]

        print(f"\n[{date1}]")
        print(f"  시작가: {result1['initial_price']:,.0f}원")
        print(f"  적정가: {result1['fair_value']:,.0f}원")
        print(f"  상승여력: {result1['upside_percent']:.1f}%")

        print(f"\n[{date2}]")
        print(f"  시작가: {result2['initial_price']:,.0f}원")
        print(f"  적정가: {result2['fair_value']:,.0f}원")
        print(f"  상승여력: {result2['upside_percent']:.1f}%")

        print(f"\n[차이]")
        fv_diff = ((result2['fair_value'] - result1['fair_value']) / result1['fair_value']) * 100
        upside_diff = result2['upside_percent'] - result1['upside_percent']

        print(f"  적정가 변화: {fv_diff:+.1f}%")
        print(f"  상승여력 변화: {upside_diff:+.1f}%p")

        if abs(fv_diff) > 1:
            print(f"\n[성공] 적정가가 날짜에 따라 변경됨!")
        else:
            print(f"\n[경고] 적정가 변화가 거의 없음 (재무제표가 동일할 가능성)")

if __name__ == "__main__":
    test_backtest_dates()
