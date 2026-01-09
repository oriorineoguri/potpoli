# Termux에서 실행하기

## 방법 1: Python 직접 실행 (권장)

### 1단계: Termux 설정

```bash
# 패키지 업데이트
pkg update && pkg upgrade

# 필요한 패키지 설치
pkg install python git curl

# Python 패키지 관리자 업그레이드
pip install --upgrade pip
```

### 2단계: GitHub에서 코드 클론

```bash
# 저장소 클론
git clone https://github.com/oriorineoguri/potpoli.git
cd potpoli

# 또는 GHCR 이미지에서 코드 추출 (선택사항)
# docker pull ghcr.io/oriorineoguri/potpoli:latest
# docker create --name temp-container ghcr.io/oriorineoguri/potpoli:latest
# docker cp temp-container:/app ./
# docker rm temp-container
```

### 3단계: 의존성 설치

```bash
# requirements.txt 설치
pip install -r requirements.txt

# 또는 필수 패키지만 설치 (용량 절약)
pip install flask flask-cors yfinance requests python-dotenv pandas numpy
```

### 4단계: 환경변수 설정

```bash
# .env 파일 생성
nano .env

# 또는 echo로 생성
echo "DART_API_KEY=your_api_key_here" > .env
```

### 5단계: 서버 실행

```bash
# 서버 실행
python server/api.py

# 또는 백그라운드 실행
nohup python server/api.py > server.log 2>&1 &
```

### 6단계: 접속

- 로컬: http://localhost:5000
- 같은 WiFi 네트워크: http://[핸드폰 IP]:5000
- IP 주소 확인: `ifconfig` 또는 `ip addr`

## 방법 2: proot-distro로 Ubuntu 환경에서 Docker 실행

### 1단계: proot-distro 설치

```bash
pkg install proot-distro

# Ubuntu 설치
proot-distro install ubuntu

# Ubuntu 진입
proot-distro login ubuntu
```

### 2단계: Ubuntu 내에서 Docker 설치

```bash
# Ubuntu 환경에서
apt update
apt install -y docker.io

# Docker 서비스 시작 (root 권한 필요할 수 있음)
service docker start
```

### 3단계: GHCR 이미지 실행

```bash
# GitHub 로그인 (Personal Access Token 필요)
echo $GITHUB_TOKEN | docker login ghcr.io -u oriorineoguri --password-stdin

# 이미지 풀
docker pull ghcr.io/oriorineoguri/potpoli:latest

# 컨테이너 실행
docker run -d \
  -p 5000:5000 \
  -e DART_API_KEY=your_api_key \
  ghcr.io/oriorineoguri/potpoli:latest
```

## 방법 3: 간단한 실행 스크립트

### setup.sh 생성

```bash
#!/data/data/com.termux/files/usr/bin/bash

echo "=== Termux 설정 시작 ==="

# 패키지 업데이트
pkg update -y

# 필수 패키지 설치
pkg install -y python git

# Python 패키지 설치
pip install flask flask-cors yfinance requests python-dotenv pandas numpy

# 저장소 클론
if [ ! -d "potpoli" ]; then
    git clone https://github.com/oriorineoguri/potpoli.git
fi

cd potpoli

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo "DART_API_KEY=your_api_key_here" > .env
    echo "⚠️  .env 파일을 수정하세요!"
fi

echo "=== 설정 완료 ==="
echo "실행: cd potpoli && python server/api.py"
```

### 실행

```bash
chmod +x setup.sh
./setup.sh
```

## 네트워크 접속 설정

### 같은 WiFi에서 접속하기

1. **핸드폰 IP 확인**
```bash
ifconfig wlan0
# 또는
ip addr show wlan0
```

2. **방화벽 허용** (필요시)
```bash
# Termux에서 포트 포워딩
termux-wake-lock
```

3. **다른 기기에서 접속**
   - PC/태블릿: http://[핸드폰 IP]:5000
   - 예: http://192.168.0.100:5000

### 외부에서 접속하기 (고급)

1. **ngrok 사용** (Termux에서)
```bash
# ngrok 설치
pkg install curl
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /data/data/com.termux/files/usr/etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /data/data/com.termux/files/usr/etc/apt/sources.list.d/ngrok.list
pkg update && pkg install ngrok

# ngrok 실행
ngrok http 5000
```

2. **ngrok에서 제공하는 URL로 접속**

## 문제 해결

### 포트가 이미 사용 중인 경우

```bash
# 포트 확인
netstat -tulpn | grep 5000

# 프로세스 종료
kill -9 [PID]
```

### 메모리 부족

```bash
# 캐시 정리
pip cache purge

# 불필요한 패키지 제거
pkg autoremove
```

### Python 버전 문제

```bash
# Python 버전 확인
python --version

# Python 3.10 이상 필요
pkg install python-3.10
```

## 자동 시작 설정

### .bashrc에 추가

```bash
# ~/.bashrc 파일 편집
nano ~/.bashrc

# 다음 추가
alias start-api='cd ~/potpoli && python server/api.py &'
```

## 성능 최적화

### 경량 모드 실행

```bash
# 최소 의존성으로 실행
python -c "
import sys
sys.path.insert(0, '.')
from server.api import app
app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
"
```

## 보안 주의사항

1. **.env 파일 보호**: API 키가 포함되어 있으므로 공유하지 마세요
2. **방화벽 설정**: 외부 접속 시 적절한 보안 설정 필요
3. **HTTPS 사용**: 프로덕션 환경에서는 HTTPS 사용 권장
