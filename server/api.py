"""
Flask API 서버

웹에서 실시간으로 포트폴리오를 구성할 수 있는 백엔드 API를 제공합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
from datetime import datetime

from src.portfolio.portfolio_builder import PortfolioBuilder
from src.backtest.engine import BacktestEngine

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask 앱 생성 (templates 폴더 경로 지정)
template_dir = project_root / 'templates'
app = Flask(__name__, template_folder=str(template_dir))
CORS(app)  # CORS 허용

# 포트폴리오 빌더 인스턴스
builder = PortfolioBuilder(use_cache=True)

# 백테스트 엔진 인스턴스
backtest_engine = BacktestEngine(use_cache=True)


@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    """
    개별 종목 분석 API

    Request Body:
        {
            "ticker": "005930",
            "moat": {
                "has_brand_power": true,
                "has_cost_advantage": true,
                ...
            },
            "mgmt": {
                "transparency_score": 4,
                "shareholder_return_score": 4,
                ...
            }
        }

    Response:
        {
            "success": true,
            "data": { StockAnalysis 데이터 }
        }
    """
    try:
        data = request.json
        ticker = data.get('ticker')

        if not ticker:
            return jsonify({
                'success': False,
                'error': '종목 코드를 입력해주세요.'
            }), 400

        moat_config = data.get('moat')
        mgmt_config = data.get('mgmt')

        logger.info(f"종목 분석 요청: {ticker}")

        # 종목 분석
        analysis = builder.analyze_stock(
            ticker,
            korean_code=True,
            moat_config=moat_config,
            mgmt_config=mgmt_config
        )

        if analysis is None:
            return jsonify({
                'success': False,
                'error': f'종목 "{ticker}"의 데이터를 가져올 수 없습니다.'
            }), 404

        from dataclasses import asdict
        return jsonify({
            'success': True,
            'data': asdict(analysis)
        })

    except Exception as e:
        logger.error(f"종목 분석 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/portfolio', methods=['POST'])
def build_portfolio():
    """
    포트폴리오 생성 API

    Request Body:
        {
            "tickers": ["005930", "000660", ...],
            "stock_configs": {
                "005930": {
                    "moat": {...},
                    "mgmt": {...}
                },
                ...
            }
        }

    Response:
        {
            "success": true,
            "data": { 포트폴리오 데이터 }
        }
    """
    try:
        data = request.json
        tickers = data.get('tickers', [])
        stock_configs = data.get('stock_configs', {})

        if not tickers:
            return jsonify({
                'success': False,
                'error': '분석할 종목을 추가해주세요.'
            }), 400

        logger.info(f"포트폴리오 생성 요청: {len(tickers)}개 종목")

        # 포트폴리오 생성
        portfolio = builder.build_portfolio(tickers, stock_configs)

        return jsonify({
            'success': True,
            'data': portfolio
        })

    except Exception as e:
        logger.error(f"포트폴리오 생성 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """
    백테스트 실행 API

    Request Body:
        {
            "tickers": ["005930", "000660", ...],
            "start_date": "2023-01-01",
            "stock_configs": {...}  // 선택사항
        }

    Response:
        {
            "success": true,
            "data": {
                "results": [...],
                "summary": {...}
            }
        }
    """
    try:
        data = request.json
        tickers = data.get('tickers', [])
        start_date_str = data.get('start_date')
        stock_configs = data.get('stock_configs', {})

        if not tickers:
            return jsonify({
                'success': False,
                'error': '분석할 종목을 추가해주세요.'
            }), 400

        if not start_date_str:
            return jsonify({
                'success': False,
                'error': '시작 날짜를 입력해주세요.'
            }), 400

        # 날짜 파싱
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                'success': False,
                'error': '날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)'
            }), 400

        # 미래 날짜 체크
        if start_date > datetime.now():
            return jsonify({
                'success': False,
                'error': '시작 날짜는 과거여야 합니다.'
            }), 400

        logger.info(f"백테스트 요청: {len(tickers)}개 종목, 시작일: {start_date_str}")

        # 백테스트 실행
        result = backtest_engine.run_backtest(tickers, start_date, stock_configs)

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        logger.error(f"백테스트 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('interactive_portfolio.html')


@app.route('/portfolio')
def portfolio_page():
    """포트폴리오 페이지"""
    return render_template('interactive_portfolio.html')


@app.route('/backtest')
def backtest_page():
    """백테스트 페이지"""
    return render_template('backtest.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'ok',
        'message': '레츠고 주식왕 API 서버가 정상 작동 중입니다.'
    })


if __name__ == '__main__':
    print("=" * 70)
    print("레츠고 주식왕 - API 서버 시작".center(70))
    print("=" * 70)
    print()
    print("서버 주소: http://localhost:5000")
    print()
    print("API 엔드포인트:")
    print("  - GET  /api/health       : 서버 상태 확인")
    print("  - POST /api/analyze      : 개별 종목 분석")
    print("  - POST /api/portfolio    : 포트폴리오 생성")
    print("  - POST /api/backtest     : 백테스트 실행")
    print()
    print("=" * 70)
    print()

    app.run(debug=True, host='0.0.0.0', port=5000)
