# GitHub Container Registry (GHCR) 배포 가이드

## 자동 배포 (GitHub Actions)

### 1. GitHub 저장소에 코드 푸시

```bash
git add .
git commit -m "Add Docker support"
git push origin main
```

### 2. GitHub Actions 자동 실행

- `main` 또는 `master` 브랜치에 푸시하면 자동으로 빌드 및 푸시
- Pull Request는 빌드만 수행 (푸시 안 함)
- 태그가 있으면 해당 태그로 이미지 생성

### 3. 이미지 확인

GitHub 저장소의 **Packages** 탭에서 이미지를 확인할 수 있습니다.

## 수동 배포

### 1. GitHub Personal Access Token 생성

1. GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. `write:packages`, `read:packages`, `delete:packages` 권한 선택
3. 토큰 생성 및 복사

### 2. 로컬에서 빌드 및 푸시

```bash
# GitHub 로그인
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# 이미지 빌드
docker build -t ghcr.io/USERNAME/REPO_NAME:latest .

# 이미지 푸시
docker push ghcr.io/USERNAME/REPO_NAME:latest
```

**Windows PowerShell:**
```powershell
# 토큰을 환경변수로 설정
$env:GITHUB_TOKEN = "your_token_here"

# 로그인
$env:GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# 빌드 및 푸시
docker build -t ghcr.io/USERNAME/REPO_NAME:latest .
docker push ghcr.io/USERNAME/REPO_NAME:latest
```

## 이미지 사용 방법

### 1. Public 패키지인 경우

```bash
docker pull ghcr.io/USERNAME/REPO_NAME:latest
docker run -d -p 5000:5000 ghcr.io/USERNAME/REPO_NAME:latest
```

### 2. Private 패키지인 경우

```bash
# GitHub 로그인
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# 이미지 풀
docker pull ghcr.io/USERNAME/REPO_NAME:latest

# 실행
docker run -d \
  -p 5000:5000 \
  -e DART_API_KEY=your_key \
  ghcr.io/USERNAME/REPO_NAME:latest
```

## 패키지 공개 설정

1. GitHub 저장소 → **Packages** 탭
2. 패키지 선택 → **Package settings**
3. **Change visibility** → **Public** 선택

## 태그 사용

### 버전 태그로 푸시

```bash
# 태그 생성
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions가 자동으로 `v1.0.0` 태그로 이미지를 생성합니다.

### 수동으로 태그 지정

```bash
docker build -t ghcr.io/USERNAME/REPO_NAME:v1.0.0 .
docker push ghcr.io/USERNAME/REPO_NAME:v1.0.0
```

## Docker Compose에서 사용

```yaml
version: '3.8'

services:
  stock-api:
    image: ghcr.io/USERNAME/REPO_NAME:latest
    ports:
      - "5000:5000"
    environment:
      - DART_API_KEY=${DART_API_KEY}
    restart: unless-stopped
```

## 문제 해결

### 인증 오류

```bash
# 토큰 확인
echo $GITHUB_TOKEN

# 다시 로그인
docker logout ghcr.io
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

### 권한 오류

- Personal Access Token에 `write:packages` 권한이 있는지 확인
- 저장소가 Private인 경우 패키지도 Private로 설정

### 이미지 찾을 수 없음

- 이미지 이름이 정확한지 확인: `ghcr.io/USERNAME/REPO_NAME:tag`
- 패키지가 Public인지 확인
- Private인 경우 로그인 필요

## CI/CD 예시

다른 서버에서 자동으로 배포하려면:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Server

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            docker pull ghcr.io/USERNAME/REPO_NAME:latest
            docker-compose up -d
```
