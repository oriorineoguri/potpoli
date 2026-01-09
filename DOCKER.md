# Docker 배포 가이드

## 빠른 시작

### 1. Docker 이미지 빌드

```bash
docker build -t stock-portfolio-api .
```

### 2. Docker 컨테이너 실행

#### 방법 1: docker run 사용

```bash
docker run -d \
  --name stock-portfolio-api \
  -p 5000:5000 \
  -e DART_API_KEY=your_api_key_here \
  -v $(pwd)/data:/app/data \
  stock-portfolio-api
```

#### 방법 2: docker-compose 사용 (권장)

```bash
# .env 파일에 DART_API_KEY 설정 확인
docker-compose up -d
```

### 3. 서버 접속

- 로컬: http://localhost:5000
- 외부: http://[서버 IP 주소]:5000

## 환경변수 설정

`.env` 파일에 다음 변수를 설정하세요:

```env
DART_API_KEY=your_dart_api_key
PORT=5000
HOST=0.0.0.0
DEBUG=True
```

## Docker Compose 명령어

```bash
# 컨테이너 시작
docker-compose up -d

# 컨테이너 중지
docker-compose stop

# 컨테이너 중지 및 제거
docker-compose down

# 로그 확인
docker-compose logs -f

# 컨테이너 재시작
docker-compose restart

# 이미지 재빌드
docker-compose build --no-cache
```

## Docker 명령어

```bash
# 컨테이너 실행
docker run -d --name stock-portfolio-api -p 5000:5000 stock-portfolio-api

# 컨테이너 중지
docker stop stock-portfolio-api

# 컨테이너 제거
docker rm stock-portfolio-api

# 로그 확인
docker logs -f stock-portfolio-api

# 컨테이너 내부 접속
docker exec -it stock-portfolio-api bash

# 이미지 제거
docker rmi stock-portfolio-api
```

## 포트 변경

다른 포트를 사용하려면:

```bash
# docker-compose.yml에서 ports 수정
ports:
  - "8080:5000"  # 호스트:컨테이너

# 또는 docker run 사용
docker run -d -p 8080:5000 stock-portfolio-api
```

## 볼륨 마운트

데이터 캐시를 영구 저장하려면:

```bash
docker run -d \
  -v $(pwd)/data:/app/data \
  stock-portfolio-api
```

## 문제 해결

### 포트가 이미 사용 중인 경우

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID [PID] /F

# Linux/Mac
lsof -i :5000
kill -9 [PID]
```

### 컨테이너가 시작되지 않는 경우

```bash
# 로그 확인
docker logs stock-portfolio-api

# 컨테이너 상태 확인
docker ps -a
```

### 환경변수가 적용되지 않는 경우

`.env` 파일이 올바른 위치에 있는지 확인하고, docker-compose.yml에서 volumes 설정을 확인하세요.

## 프로덕션 배포

프로덕션 환경에서는:

1. `DEBUG=False`로 설정
2. HTTPS 사용 (nginx 리버스 프록시)
3. 환경변수는 Docker secrets 또는 환경변수로 관리
4. 로그 관리 설정

```yaml
# docker-compose.prod.yml 예시
version: '3.8'
services:
  stock-api:
    build: .
    environment:
      - DEBUG=False
      - PORT=5000
    restart: always
```
