# AWS 배포 가이드라인 (무료 티어 기준)

## 📋 사전 준비 사항
- AWS 계정 (무료 티어 12개월)
- Docker Hub 계정
- SSH 키 페어
- 카카오/네이버 OAuth 키 (`OAUTH_SETUP_GUIDE.md` 참고)
- 도메인 (선택사항 — Gabia, GoDaddy, AWS Route53)

---

## 🖥️ AWS 리소스 구성

### EC2 인스턴스
```
인스턴스 타입: t2.micro (무료 티어, vCPU 1, RAM 1GB)
운영체제: Ubuntu 22.04 LTS
스토리지: 30GB gp3 (무료 티어)
```

> **서비스 구성**: Redis + FastAPI + AI Worker + Nginx (MySQL 없음)
> AI Worker는 메모리를 많이 사용하므로 스왑 파일 설정을 권장합니다.

### 보안 그룹 인바운드 규칙
| Type | Protocol | Port | Source |
|------|----------|------|--------|
| SSH | TCP | 22 | 내 IP |
| HTTP | TCP | 80 | 0.0.0.0/0 |
| HTTPS | TCP | 443 | 0.0.0.0/0 |

> 8000 포트는 Nginx가 프록시하므로 외부에 열 필요 없습니다.

---

## 🚀 자동 배포 스크립트

```bash
chmod +x scripts/deployment.sh
./scripts/deployment.sh
```

입력 정보:
1. Docker Hub 사용자명 / Personal Access Token
2. 이미지 레포지토리명 (예: `ai-healthcare`)
3. 배포 서비스 선택 (FastAPI / AI-Worker / Both)
4. 이미지 태그 (예: `v1.0.0`)
5. SSH 키 파일명 및 EC2 퍼블릭 IP
6. HTTPS 사용 여부 → 도메인 입력

---

## 🔧 수동 배포 과정

### 1. Docker 이미지 빌드 및 푸시 (로컬)
```bash
docker build -f app/Dockerfile -t your_username/ai-healthcare:app-v1.0.0 .
docker build -f ai_worker/Dockerfile -t your_username/ai-healthcare:ai-v1.0.0 .
docker login
docker push your_username/ai-healthcare:app-v1.0.0
docker push your_username/ai-healthcare:ai-v1.0.0
```

### 2. EC2 서버 초기 설정
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Docker 설치
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker ubuntu
sudo systemctl enable --now docker
newgrp docker
```

### 3. 프로젝트 파일 업로드 (로컬에서 실행)
```bash
# 필요한 파일만 업로드 (이미지는 Docker Hub에서 pull)
scp -i your-key.pem docker-compose.prod.yml ubuntu@your-ec2-ip:~/ai-healthcare/
scp -i your-key.pem -r nginx/ ubuntu@your-ec2-ip:~/ai-healthcare/
scp -i your-key.pem -r envs/ ubuntu@your-ec2-ip:~/ai-healthcare/
scp -i your-key.pem -r static/ ubuntu@your-ec2-ip:~/ai-healthcare/
```

### 4. 환경 변수 설정 (EC2에서)
```bash
cd ~/ai-healthcare
cp envs/example.prod.env envs/.prod.env
ln -sf envs/.prod.env .env
nano envs/.prod.env
```

### 5. 프로덕션 환경 변수 내용
```env
ENV=prod
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
TASK_RESULT_TTL=3600

# JWT (반드시 강력한 랜덤 값으로 변경)
JWT_SECRET=your-strong-random-secret-key-minimum-32-chars
JWT_ALGORITHM=HS256

# OAuth (OAUTH_SETUP_GUIDE.md 참고)
KAKAO_CLIENT_ID=발급받은_REST_API_키
KAKAO_CLIENT_SECRET=발급받은_Client_Secret
NAVER_CLIENT_ID=발급받은_Client_ID
NAVER_CLIENT_SECRET=발급받은_Client_Secret

# CORS
ALLOWED_ORIGINS=["https://yourdomain.com","http://your-ec2-ip"]

# Docker Hub
DOCKER_USER=your_dockerhub_username
DOCKER_REPOSITORY=ai-healthcare
APP_VERSION=v1.0.0
AI_WORKER_VERSION=v1.0.0
```

### 6. 배포 실행
```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps
```

---

## 🔒 SSL/HTTPS 설정

### 자동 설정 (Certbot 스크립트)
```bash
chmod +x scripts/certbot.sh
./scripts/certbot.sh
# 도메인, 이메일, SSH 키, EC2 IP 입력
```

### 수동 설정
```bash
# EC2에서
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com

# 자동 갱신
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### Nginx HTTPS 설정 전환
SSL 인증서 발급 후 `docker-compose.prod.yml`의 nginx 볼륨을 변경합니다:
```yaml
- ./nginx/prod_https.conf:/etc/nginx/conf.d/default.conf
```

### OAuth Redirect URI 업데이트
HTTPS 설정 후 카카오/네이버 개발자 콘솔에서 Redirect URI 추가:
- `https://yourdomain.com`

---

## 💰 비용 최적화 (t2.micro 1GB RAM)

### 스왑 파일 생성 (AI Worker 메모리 부족 방지 — 필수)
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 무료 티어 한도
- EC2 t2.micro: 월 750시간
- EBS: 30GB
- 데이터 전송: 15GB/월 아웃바운드

### 디스크 정리
```bash
docker system prune -a
sudo journalctl --vacuum-time=7d
```

---

## 📊 모니터링 및 관리

```bash
# 컨테이너 상태
docker compose -f docker-compose.prod.yml ps

# 리소스 사용량
docker stats

# 로그 확인
docker compose -f docker-compose.prod.yml logs --tail=100 fastapi
docker compose -f docker-compose.prod.yml logs --tail=100 ai-worker

# 서비스 재시작
docker compose -f docker-compose.prod.yml restart fastapi
```

---

## 🎯 배포 완료 체크리스트
- [ ] EC2 인스턴스 생성 및 보안 그룹 설정 (80, 443, 22 포트)
- [ ] Docker 설치 완료
- [ ] 스왑 파일 2GB 생성 (AI Worker 메모리 확보)
- [ ] `envs/.prod.env` 환경 변수 설정 (JWT_SECRET, OAuth 키 포함)
- [ ] Docker 이미지 빌드 및 Docker Hub 푸시
- [ ] `docker-compose.prod.yml`로 서비스 실행
- [ ] `http://your-ec2-ip` → 로그인 페이지 표시 확인
- [ ] 카카오/네이버 OAuth Redirect URI 등록 (`http://your-ec2-ip`)
- [ ] 도메인 연결 (선택)
- [ ] SSL 인증서 설정 (HTTPS) 및 Redirect URI 추가 등록
- [ ] 만성질환 예측 서비스 동작 확인
