#!/data/data/com.termux/files/usr/bin/bash

echo "=========================================="
echo "  주식 포트폴리오 API - Termux 설정"
echo "=========================================="
echo ""

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 패키지 업데이트
echo -e "${YELLOW}[1/6] 패키지 업데이트 중...${NC}"
pkg update -y && pkg upgrade -y

# 2. 필수 패키지 설치
echo -e "${YELLOW}[2/6] 필수 패키지 설치 중...${NC}"
pkg install -y python git curl

# 3. Python 패키지 관리자 업그레이드
echo -e "${YELLOW}[3/6] pip 업그레이드 중...${NC}"
pip install --upgrade pip

# 4. 저장소 클론
echo -e "${YELLOW}[4/6] GitHub에서 코드 다운로드 중...${NC}"
if [ -d "potpoli" ]; then
    echo "이미 potpoli 폴더가 있습니다. 업데이트합니다..."
    cd potpoli
    git pull
else
    git clone https://github.com/oriorineoguri/potpoli.git
    cd potpoli
fi

# 5. Python 의존성 설치
echo -e "${YELLOW}[5/6] Python 패키지 설치 중...${NC}"
echo "이 작업은 몇 분 걸릴 수 있습니다..."

# 필수 패키지만 먼저 설치
pip install flask flask-cors python-dotenv

# 나머지 패키지 설치 (선택사항)
read -p "모든 패키지를 설치하시겠습니까? (y/n): " install_all
if [ "$install_all" = "y" ]; then
    pip install -r requirements.txt
else
    echo "필수 패키지만 설치합니다..."
    pip install yfinance requests pandas numpy
fi

# 6. 환경변수 설정
echo -e "${YELLOW}[6/6] 환경변수 설정 중...${NC}"
if [ ! -f ".env" ]; then
    echo "DART_API_KEY=your_api_key_here" > .env
    echo -e "${GREEN}✓ .env 파일이 생성되었습니다.${NC}"
    echo -e "${YELLOW}⚠️  .env 파일을 수정하여 DART_API_KEY를 설정하세요!${NC}"
    echo "   nano .env"
else
    echo -e "${GREEN}✓ .env 파일이 이미 존재합니다.${NC}"
fi

# 완료 메시지
echo ""
echo -e "${GREEN}=========================================="
echo "  설정 완료!"
echo "==========================================${NC}"
echo ""
echo "다음 명령어로 서버를 실행하세요:"
echo ""
echo "  cd potpoli"
echo "  python server/api.py"
echo ""
echo "또는 백그라운드 실행:"
echo "  nohup python server/api.py > server.log 2>&1 &"
echo ""
echo "서버 주소:"
echo "  - 로컬: http://localhost:5000"
echo "  - 네트워크: http://\$(ip addr show wlan0 | grep 'inet ' | awk '{print \$2}' | cut -d/ -f1):5000"
echo ""
