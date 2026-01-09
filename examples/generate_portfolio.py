"""
포트폴리오 생성 및 HTML 렌더링

실제 API 데이터를 사용하여 포트폴리오를 분석하고 HTML 대시보드를 생성합니다.
"""

import sys
import json
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.portfolio.portfolio_builder import PortfolioBuilder


def generate_portfolio_html():
    """포트폴리오 HTML 생성"""

    print("=" * 70)
    print("레츠고 주식왕 - 포트폴리오 생성".center(70))
    print("=" * 70)
    print()

    # 분석할 종목 리스트 (한국 대형주)
    tickers = [
        "005930",  # 삼성전자
        "000660",  # SK하이닉스
        "035720",  # 카카오
        "035420",  # NAVER
        "051910",  # LG화학
        "006400",  # 삼성SDI
        "207940",  # 삼성바이오로직스
        "068270",  # 셀트리온
    ]

    # 종목별 설정 (경제적 해자, 경영진 평가)
    stock_configs = {
        "005930": {  # 삼성전자
            "moat": {
                "has_brand_power": True,
                "has_cost_advantage": True,
                "has_intangible_assets": True,
            },
            "mgmt": {
                "transparency_score": 4,
                "shareholder_return_score": 4,
                "capital_allocation_score": 5,
                "governance_score": 3,
            }
        },
        "000660": {  # SK하이닉스
            "moat": {
                "has_cost_advantage": True,
                "has_intangible_assets": True,
            },
            "mgmt": {
                "transparency_score": 4,
                "shareholder_return_score": 3,
                "capital_allocation_score": 4,
                "governance_score": 3,
            }
        },
        "035720": {  # 카카오
            "moat": {
                "has_brand_power": True,
                "has_network_effect": True,
                "has_switching_cost": True,
            },
            "mgmt": {
                "transparency_score": 4,
                "shareholder_return_score": 3,
                "capital_allocation_score": 4,
                "governance_score": 4,
            }
        },
        "035420": {  # NAVER
            "moat": {
                "has_brand_power": True,
                "has_network_effect": True,
                "has_switching_cost": True,
            },
            "mgmt": {
                "transparency_score": 5,
                "shareholder_return_score": 3,
                "capital_allocation_score": 4,
                "governance_score": 4,
            }
        },
    }

    # 포트폴리오 생성
    print("종목 분석 중...")
    builder = PortfolioBuilder(use_cache=True)
    portfolio = builder.build_portfolio(tickers, stock_configs)

    # JSON 저장
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)

    json_file = output_dir / "portfolio_data.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=2)

    print(f"[OK] 포트폴리오 데이터 저장: {json_file}")

    # HTML 생성 (템플릿에 데이터 임베드)
    template_file = project_root / "templates" / "portfolio_dashboard.html"
    output_html = output_dir / "portfolio.html"

    if template_file.exists():
        # 템플릿 읽기
        with open(template_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # JSON 데이터를 스크립트로 임베드
        portfolio_json = json.dumps(portfolio, ensure_ascii=False, indent=2)
        data_script = f"""
    <script>
        // 임베드된 포트폴리오 데이터
        const PORTFOLIO_DATA = {portfolio_json};
    </script>
"""

        # fetch 함수를 임베드 데이터 사용하도록 수정
        html_content = html_content.replace(
            '    <script>',
            data_script + '    <script>',
            1
        )
        html_content = html_content.replace(
            'async function loadPortfolioData() {\n            try {\n                const response = await fetch(\'portfolio_data.json\');\n                const data = await response.json();\n                renderDashboard(data);',
            'async function loadPortfolioData() {\n            try {\n                // 임베드된 데이터 사용\n                const data = PORTFOLIO_DATA;\n                renderDashboard(data);'
        )

        # 수정된 HTML 저장
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"[OK] HTML 대시보드 생성: {output_html}")
    else:
        print(f"[WARNING] HTML 템플릿 없음: {template_file}")

    # 요약 출력
    print()
    print("=" * 70)
    print("포트폴리오 요약".center(70))
    print("=" * 70)
    print(f"분석 종목 수: {portfolio['summary']['total_stocks']}개")
    print(f"저평가 종목: {portfolio['summary']['undervalued']}개")
    print(f"적정가 종목: {portfolio['summary']['fair_priced']}개")
    print(f"고평가 종목: {portfolio['summary']['overvalued']}개")
    print(f"평균 상승여력: {portfolio['summary']['avg_upside']:+.1f}%")
    print()

    if portfolio['summary']['top_pick']:
        top = portfolio['summary']['top_pick']
        print(f"[TOP PICK] {top['company_name']}")
        print(f"   현재가: {top['current_price']:,.0f}원")
        print(f"   적정가: {top['fair_price_per_share']:,.0f}원")
        print(f"   상승여력: {top['upside_percent']:+.1f}%")
        print(f"   종합점수: {top['score']:.0f}/100")

    print()
    print("=" * 70)
    print(f"HTML 파일을 브라우저로 열어보세요: {output_html}")
    print("=" * 70)


if __name__ == "__main__":
    generate_portfolio_html()
