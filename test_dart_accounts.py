"""
SK하이닉스 DART API 계정명 확인
"""

import logging
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

from src.data.dart_api import DartApiClient

def test_dart_accounts():
    """SK하이닉스 DART 계정명 확인"""

    client = DartApiClient()

    # SK하이닉스 2023년 연간 재무제표
    fs_data = client.get_financial_statements("00164779", 2023, "11011")

    if not fs_data:
        print("재무제표 조회 실패 - fs_data is None")
        return

    print(f"API 응답 status: {fs_data.get('status')}")
    print(f"API 응답 message: {fs_data.get('message')}")
    print()

    if "list" not in fs_data:
        print("재무제표 조회 실패 - list 키 없음")
        print(f"응답 키: {list(fs_data.keys())}")
        return

    print("=" * 70)
    print("SK하이닉스 2023년 연간 재무제표")
    print("=" * 70)
    print()

    # 전체 항목 수
    all_items = fs_data["list"]
    print(f"전체 항목 수: {len(all_items)}")

    # sj_div 분포 확인
    sj_divs = {}
    for item in all_items:
        sj_div = item.get("sj_div", "")
        sj_divs[sj_div] = sj_divs.get(sj_div, 0) + 1

    print(f"sj_div 분포: {sj_divs}")
    print()

    # 손익계산서(IS) 또는 포괄손익계산서(CIS) 필터링
    is_accounts = [item for item in all_items if item.get("sj_div") in ["IS", "CIS"]]

    print(f"손익계산서(IS/CIS) 계정 수: {len(is_accounts)}")
    print()

    # 당기순이익 관련 계정 찾기
    print("[당기순이익 관련 계정]")
    for item in is_accounts:
        account_nm = item.get("account_nm", "")
        if "순이익" in account_nm or "당기" in account_nm:
            amount = item.get("thstrm_amount", "")
            print(f"  - {account_nm}: {amount}")

    print()

if __name__ == "__main__":
    test_dart_accounts()
