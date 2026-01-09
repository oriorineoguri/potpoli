# 레츠고 주식왕 (Stock Portfolio Optimizer)

## 프로젝트 개요

이 프로젝트는 최적의 주식 포트폴리오를 짜도록 도와주는 주식 시뮬레이터입니다.
해당 어플리케이션은 현재 시장에 따라 앞으로 유망한 회사들을 기준으로 포트폴리오를 짜줍니다.
해당되는 회사들의 재무재표를 보고 PER, PBR, EV/EBITDA, DCF, RIM, S-RIM, 경제적 해자, 경영진의 역량, 성장성(PEG) 등을 확인하여 적정가치액을 판단합니다.
적정가치액보다 낮은 회사들에 대하여 포트폴리오를 구성하도록 합니다.
과거 기준으로 포트폴리오를 대입하여, 그 때 당시의 적정가치액에 따라 매도/매매를 하도록 합니다.
그 때의 수익률이 어느정도 되는지까지 알려주도록 합니다.

---

## 코딩 컨벤션

### 언어 및 표준
- **Python 3.10+** 사용
- **PEP 8** 스타일 가이드 준수
- Type hints 적극 활용 (typing 모듈)

### 네이밍 규칙
- 함수명: `snake_case` (예: `calculate_per_ratio`, `get_financial_data`)
- 클래스명: `PascalCase` (예: `StockAnalyzer`, `PortfolioOptimizer`)
- 변수명: `snake_case` (예: `stock_price`, `company_name`)
- 상수명: `UPPER_SNAKE_CASE` (예: `MAX_PORTFOLIO_SIZE`, `DEFAULT_RISK_FREE_RATE`)
- Private 메서드/변수: `_leading_underscore` (예: `_calculate_intrinsic_value`)

### 코드 스타일
- 들여쓰기: **4 spaces** (탭 금지)
- 세미콜론: 사용하지 않음
- 따옴표: **큰따옴표(")** 우선 사용
- 최대 라인 길이: **88자** (Black 포맷터 기준)
- Import 순서: 표준 라이브러리 → 서드파티 → 로컬 모듈

---

## 빌드 & 테스트

### 설치
```bash
# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (Mac/Linux)
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 빌드
```bash
# 코드 포맷팅 (Black)
black src/

# 린트 검사 (Flake8)
flake8 src/ --max-line-length=88

# 타입 체크 (mypy)
mypy src/
```

### 테스트
```bash
# 모든 테스트 실행
pytest

# 커버리지와 함께 테스트
pytest --cov=src --cov-report=html

# 특정 모듈만 테스트
pytest tests/test_valuation.py

# 백테스트 실행
python -m src.backtest --start-date 2020-01-01 --end-date 2023-12-31
```

---

## ❌ 절대 금지

- ❌ **하드코딩된 API 키나 비밀번호** - 환경변수(.env)를 사용할 것
- ❌ **재무 데이터 무단 스크래핑** - 공식 API 또는 허가된 데이터 소스만 사용
- ❌ **실제 금융 조언 제공** - "투자 권유"가 아닌 "분석 도구"로만 제시
- ❌ **에러 처리 생략** - 모든 외부 API 호출 및 파일 I/O에 예외 처리 필수
- ❌ **Division by zero** - PER, PBR 등 비율 계산 시 분모 0 체크 필수
- ❌ **전역 변수 남용** - 설정값은 config.py에 상수로 정의
- ❌ **print() 디버깅** - 로깅(logging) 모듈 사용
- ❌ **타입 힌트 없는 public 함수** - 모든 public 함수에 타입 힌트 필수

---

## ✅ 필수 사항

- ✅ **모든 함수에 Docstring 작성** (Google 스타일 또는 NumPy 스타일)
- ✅ **재무 계산 로직에 대한 단위 테스트** - 각 밸류에이션 메서드마다 테스트 케이스 작성
- ✅ **데이터 검증(Validation)** - 입력 데이터의 유효성 체크 (음수 주가, 누락 데이터 등)
- ✅ **로깅 시스템** - INFO/WARNING/ERROR 레벨로 주요 이벤트 기록
- ✅ **환경 변수 사용** - API 키, DB 연결 정보 등은 .env 파일로 관리
- ✅ **코드 변경 시 테스트 통과** - pytest 전체 성공 후 커밋
- ✅ **금융 용어 주석** - 복잡한 재무 공식에는 설명 주석 추가
- ✅ **금융 지표 해석 가이드** - 각 재무 비율의 의미와 적정 범위를 Docstring에 명시 (예: PER 10 = 투자금 회수 10년, 일반적으로 10-20이 적정)
- ✅ **데이터 소스 명시** - 각 데이터를 어디서 가져왔는지 주석으로 기록
- ✅ **밸류에이션 공식 출처** - DCF, RIM 등 복잡한 모델은 참고 문헌이나 공식 출처 명시

---

## 아키텍처

### 디렉토리 구조
```
레츠고-주식왕/
├── src/
│   ├── data/                    # 데이터 수집 및 전처리
│   │   ├── fetcher.py          # 주가/재무제표 데이터 수집
│   │   ├── preprocessor.py     # 데이터 정제 및 변환
│   │   └── cache.py            # 데이터 캐싱 로직
│   ├── analysis/                # 재무 분석 및 밸류에이션
│   │   ├── valuation.py        # DCF, RIM, S-RIM 계산
│   │   ├── ratios.py           # PER, PBR, PEG, EV/EBITDA 계산
│   │   ├── moat_analyzer.py    # 경제적 해자 분석
│   │   └── management.py       # 경영진 역량 분석
│   ├── portfolio/               # 포트폴리오 최적화
│   │   ├── optimizer.py        # 포트폴리오 최적화 알고리즘
│   │   ├── rebalancer.py       # 리밸런싱 전략
│   │   └── risk_manager.py     # 리스크 관리
│   ├── backtest/                # 백테스트 시뮬레이션
│   │   ├── engine.py           # 백테스트 엔진
│   │   ├── strategy.py         # 매매 전략
│   │   └── performance.py      # 성과 측정 (샤프비율, MDD 등)
│   ├── ui/                      # 사용자 인터페이스
│   │   ├── dashboard.py        # Streamlit 대시보드
│   │   └── reports.py          # 리포트 생성
│   └── utils/                   # 유틸리티
│       ├── config.py           # 설정 파일
│       ├── logger.py           # 로깅 설정
│       └── validators.py       # 데이터 검증
├── tests/
│   ├── test_valuation.py
│   ├── test_portfolio.py
│   └── test_backtest.py
├── data/                        # 로컬 데이터 저장소
│   ├── raw/                    # 원본 데이터
│   └── processed/              # 가공된 데이터
├── docs/                        # 문서
├── requirements.txt             # 패키지 의존성
├── .env.example                 # 환경변수 예시
└── README.md
```

### 주요 모듈
- **DataFetcher**: 주가 및 재무제표 데이터 수집 (Yahoo Finance, FnGuide API 등)
- **ValuationEngine**: DCF, RIM, S-RIM 등 밸류에이션 모델 구현
- **PortfolioOptimizer**: 최적 포트폴리오 구성 (마코위츠 모델, 켈리 기준 등)
- **BacktestEngine**: 과거 데이터로 전략 백테스트 및 성과 분석
- **RiskManager**: 리스크 관리 (VaR, CVaR, 최대 낙폭 등)

### 데이터 흐름
```
1. 데이터 수집 (fetcher)
   → 2. 전처리 (preprocessor)
   → 3. 재무 분석 (valuation, ratios)
   → 4. 포트폴리오 구성 (optimizer)
   → 5. 백테스트 (backtest engine)
   → 6. 결과 시각화 (dashboard)
```

---

## 참고 문서

- `/docs/valuation-models.md` - DCF, RIM, S-RIM 모델 설명
- `/docs/financial-ratios.md` - PER, PBR, PEG, EV/EBITDA 계산 방법
- `/docs/api-endpoints.md` - 외부 API 사용 가이드
- [PEP 8 스타일 가이드](https://pep8.org/)
- [Pandas 문서](https://pandas.pydata.org/docs/)
- [QuantLib 문서](https://www.quantlib.org/) - 금융 계산 라이브러리
- [가치투자 바이블](https://www.example.com) - 밸류에이션 이론

---

## 추가 정보

### 기술 스택
- **언어**: Python 3.10+
- **데이터 분석**: pandas, numpy, scipy
- **시각화**: matplotlib, plotly, seaborn
- **웹 프레임워크**: Streamlit (대시보드)
- **데이터베이스**: SQLite (로컬), PostgreSQL (프로덕션)
- **테스트**: pytest, pytest-cov
- **포맷팅**: black, isort
- **린터**: flake8, mypy

### 외부 API
- Yahoo Finance API - 주가 데이터
- FnGuide API - 재무제표 데이터
- DART (전자공시) API - 공시 정보
- 컴퍼니가이드 (FnGuide)
- 네이버 페이 증권 (종목분석 탭)

### 주의사항
- 모든 금융 데이터는 **참고용**이며 투자 판단은 사용자 책임
- 실시간 데이터가 아닌 **종가 기준 데이터** 사용
- 백테스트 결과는 과거 성과이며 미래 수익을 보장하지 않음
- API Rate Limit 준수 (요청 제한 확인)

### 개발 환경
- Python 버전: 3.10 이상
- OS: Windows 10/11, macOS 12+, Ubuntu 20.04+
- 메모리: 최소 8GB RAM (대용량 데이터 처리 시)

---

## 면책 조항
본 소프트웨어는 교육 및 연구 목적으로 제작되었습니다.
실제 투자에 사용 시 발생하는 손실에 대해 개발자는 책임을 지지 않습니다.
투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다.
