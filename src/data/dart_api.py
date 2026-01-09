"""
DART (전자공시시스템) API 클라이언트

금융감독원 전자공시시스템 API를 사용하여 과거 재무제표 데이터를 조회합니다.

API 키 발급: https://opendart.fss.or.kr/
"""

import logging
import requests
import zipfile
import io
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

logger = logging.getLogger(__name__)


class DartApiClient:
    """DART API 클라이언트"""

    # 주요 종목 코드 -> 기업 고유번호 매핑 (수동 설정)
    CORP_CODE_MAP = {
        "005930": "00126380",  # 삼성전자
        "000660": "00164779",  # SK하이닉스
        "035720": "00191324",  # 카카오
        "035420": "00138617",  # NAVER
        "005380": "00164742",  # 현대차
        "000270": "00119775",  # 기아
        "051910": "00164529",  # LG화학
        "006400": "00126841",  # 삼성SDI
        "207940": "00413046",  # 삼성바이오로직스
        "068270": "00232620",  # 셀트리온
        "105560": "00109317",  # KB금융
        "055550": "00101207",  # 신한지주
        "005490": "00164108",  # 포스코홀딩스
        "028260": "00164313",  # 삼성물산
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        초기화

        Args:
            api_key: DART API 키 (없으면 환경변수에서 가져옴)
        """
        self.api_key = api_key or os.getenv("DART_API_KEY")
        self.base_url = "https://opendart.fss.or.kr/api"

        if not self.api_key:
            logger.warning("DART API 키가 설정되지 않았습니다. .env 파일에 DART_API_KEY를 추가하거나 매개변수로 전달하세요.")

        logger.info(f"DartApiClient 초기화 (API 키: {'설정됨' if self.api_key else '없음'})")

    def get_corp_code(self, stock_code: str) -> Optional[str]:
        """
        종목 코드로 기업 고유번호 조회

        Args:
            stock_code: 종목 코드 (6자리, 예: "005930")

        Returns:
            기업 고유번호 (8자리)
        """
        # 매핑 테이블에서 조회
        clean_code = stock_code.replace('.KS', '').replace('.KQ', '')
        corp_code = self.CORP_CODE_MAP.get(clean_code)

        if corp_code:
            logger.info(f"{clean_code}: 기업 고유번호 {corp_code}")
            return corp_code

        logger.warning(f"{clean_code}: 기업 고유번호 매핑 없음")
        return None

    def get_financial_statements(
        self,
        corp_code: str,
        year: int,
        reprt_code: str = "11013"
    ) -> Optional[Dict]:
        """
        재무제표 조회 (단일회사 전체 재무제표)

        Args:
            corp_code: 기업 고유번호 (8자리)
            year: 사업연도 (예: 2023)
            reprt_code: 보고서 코드
                - 11013: 1분기보고서
                - 11012: 반기보고서
                - 11014: 3분기보고서
                - 11011: 사업보고서 (연간)

        Returns:
            재무제표 데이터
        """
        if not self.api_key:
            logger.error("DART API 키가 없습니다.")
            return None

        url = f"{self.base_url}/fnlttSinglAcntAll.json"

        params = {
            "crtfc_key": self.api_key,
            "corp_code": corp_code,
            "bsns_year": str(year),
            "reprt_code": reprt_code,
            "fs_div": "CFS"  # 연결재무제표 (OFS: 개별재무제표)
        }

        try:
            logger.info(f"DART API 호출: {corp_code}, {year}년, 보고서코드 {reprt_code}")

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get("status") != "000":
                logger.warning(f"DART API 오류: {data.get('message')}")
                return None

            return data

        except Exception as e:
            logger.error(f"DART API 호출 실패: {e}")
            return None

    def get_financials_at_date(
        self,
        stock_code: str,
        target_date: datetime
    ) -> Optional[Dict]:
        """
        특정 날짜 기준의 재무제표 조회

        Args:
            stock_code: 종목 코드 (6자리)
            target_date: 목표 날짜

        Returns:
            재무제표 데이터 (자기자본, 순이익, ROE 등)
        """
        # 기업 고유번호 조회
        corp_code = self.get_corp_code(stock_code)
        if not corp_code:
            return None

        # 목표 날짜 기준으로 보고서 선택
        year = target_date.year
        month = target_date.month

        # 분기 결정
        if month <= 3:
            # 전년도 4분기 (사업보고서)
            year -= 1
            reprt_code = "11011"
            quarter = "4Q"
        elif month <= 6:
            # 1분기보고서
            reprt_code = "11013"
            quarter = "1Q"
        elif month <= 9:
            # 반기보고서
            reprt_code = "11012"
            quarter = "2Q"
        else:
            # 3분기보고서
            reprt_code = "11014"
            quarter = "3Q"

        logger.info(f"{stock_code}: {target_date.date()} → {year}년 {quarter} 재무제표 조회")

        # 재무제표 조회
        fs_data = self.get_financial_statements(corp_code, year, reprt_code)

        if not fs_data or "list" not in fs_data:
            logger.warning(f"{stock_code}: {year}년 {quarter} 재무제표 없음")
            return None

        # 재무제표에서 필요한 항목 추출
        return self._parse_financial_data(fs_data["list"], year, quarter)

    def _parse_financial_data(self, fs_list: List[Dict], year: int, quarter: str) -> Optional[Dict]:
        """
        재무제표 데이터 파싱

        Args:
            fs_list: DART API 응답의 list 부분
            year: 연도
            quarter: 분기

        Returns:
            파싱된 재무제표 데이터
        """
        # 필요한 항목들
        equity = None  # 자기자본
        net_income = None  # 당기순이익
        total_assets = None  # 총자산

        logger.debug(f"DART 데이터 파싱 시작: 총 {len(fs_list)}개 항목")

        for item in fs_list:
            account_nm = item.get("account_nm", "")  # 계정명
            sj_div = item.get("sj_div", "")
            thstrm_amount = item.get("thstrm_amount", "")

            # 재무상태표 (BS)
            if sj_div == "BS":
                # 자본총계 (DART API에서는 "자본총계"로 표시됨)
                # "자본총계"만 정확히 매칭 (자산총계, 비지배지분자본총계 제외)
                if account_nm == "자본총계":
                    thstrm_amount_clean = thstrm_amount.replace(",", "")
                    if thstrm_amount_clean and thstrm_amount_clean != "-":
                        # DART API는 이미 원 단위로 제공 (단위 변환 불필요)
                        equity = float(thstrm_amount_clean)
                        logger.debug(f"자기자본 추출: {equity:,.0f}원")

                # 자산총계
                if account_nm == "자산총계":
                    thstrm_amount_clean = thstrm_amount.replace(",", "")
                    if thstrm_amount_clean and thstrm_amount_clean != "-":
                        # DART API는 이미 원 단위로 제공
                        total_assets = float(thstrm_amount_clean)
                        logger.debug(f"자산총계 추출: {total_assets:,.0f}원")

            # 손익계산서 (IS) 또는 포괄손익계산서 (CIS)
            elif sj_div in ["IS", "CIS"]:
                # 당기순이익 추출 (여러 표기 방식 지원)
                # 우선순위: "지배기업소유주에게귀속" > "당기순이익(손실)"
                is_net_income = False

                if "당기순이익" in account_nm:
                    # "지배기업소유주에게귀속되는당기순이익" 또는 "당기순이익(손실)" 매칭
                    if ("지배" in account_nm and "귀속" in account_nm and "비지배" not in account_nm):
                        is_net_income = True
                    elif account_nm == "당기순이익(손실)" or account_nm == "당기순이익":
                        is_net_income = True

                if is_net_income:
                    thstrm_amount_clean = thstrm_amount.replace(",", "")
                    if thstrm_amount_clean and thstrm_amount_clean != "-":
                        # DART API는 이미 원 단위로 제공
                        net_income = float(thstrm_amount_clean)
                        logger.debug(f"당기순이익 추출: {account_nm} = {net_income:,.0f}원")

        # ROE 계산
        roe = None
        if net_income and equity and equity > 0:
            # 분기 데이터를 연간화 (1Q/2Q/3Q는 누적이므로 4배, 4Q는 그대로)
            if quarter in ["1Q"]:
                annual_net_income = net_income * 4
            elif quarter in ["2Q"]:
                annual_net_income = net_income * 2
            elif quarter in ["3Q"]:
                annual_net_income = net_income * 4 / 3
            else:  # 4Q (연간)
                annual_net_income = net_income

            roe = annual_net_income / equity

        if equity and net_income and roe:
            logger.info(f"DART 재무 데이터: 자기자본={equity/1e12:.1f}조, 순이익={net_income/1e12:.1f}조, ROE={roe:.2%}")

        return {
            "year": year,
            "quarter": quarter,
            "equity": equity,
            "net_income": net_income,
            "total_assets": total_assets,
            "roe": roe,
            "source": "DART"
        }
