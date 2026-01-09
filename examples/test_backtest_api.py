"""
백테스트 API 테스트
"""

import requests
import json

# API 서버 주소
API_URL = 'http://localhost:5000'

# 백테스트 요청
data = {
    "tickers": ["005930", "000660"],
    "start_date": "2023-01-01",
    "stock_configs": {}
}

print("백테스트 API 테스트")
print("=" * 70)
print(f"요청 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
print()
print("API 호출 중...")
print()

try:
    response = requests.post(
        f"{API_URL}/api/backtest",
        json=data,
        timeout=180
    )

    print(f"응답 상태 코드: {response.status_code}")
    print()

    result = response.json()

    if result['success']:
        print("[OK] 백테스트 성공!")
        print()
        print("요약:")
        print(json.dumps(result['data']['summary'], indent=2, ensure_ascii=False))
        print()
        print(f"종목 수: {len(result['data']['results'])}개")

        for stock in result['data']['results']:
            print()
            print(f"- {stock['company_name']}")
            print(f"  시작가: {stock['initial_price']:,.0f}원")
            print(f"  적정가: {stock['fair_value']:,.0f}원")
            print(f"  판단: {stock['judgment']}")
            if stock['current_return'] is not None:
                print(f"  현재 수익률: {stock['current_return']:+.2f}%")
    else:
        print("[FAIL] 백테스트 실패")
        print(f"오류: {result['error']}")

except requests.exceptions.RequestException as e:
    print(f"[FAIL] API 요청 실패: {e}")
except Exception as e:
    print(f"[FAIL] 오류 발생: {e}")
