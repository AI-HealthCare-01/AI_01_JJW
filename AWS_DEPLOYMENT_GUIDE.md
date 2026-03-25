# AWS 배포 가이드라인

## 🌐 AWS 무료 티어 배포 전략

### 사전 준비 사항
- AWS 계정 (무료 티어 12개월)
- 도메인 구매 (선택사항, Gabia/GoDaddy/Route53)
- Docker Hub 계정
- SSH 키 페어 생성

## 📋 AWS 리소스 구성

### 1. EC2 인스턴스 설정
```
인스턴스 타입: t2.micro (무료 티어)
운영체제: Ubuntu 22.04 LTS
스토리지: 30GB gp3 (무료 티어)
보안 그룹: HTTP(80), HTTPS(443), SSH(22) 허용
```

### 2. 보안 그룹 규칙
```
Type        Protocol    Port Range    Source
SSH         TCP         22           0.0.0.0/0
HTTP        TCP         80           0.0.0.0/0
HTTPS       TCP         443          0.0.0.0/0
Custom TCP  TCP         8000         0.0.0.0/0 (개발용)
```

## 🚀 자동 배포 스크립트 사용

### 1. 배포 스크립트 실행
```bash
# 스크립트 실행 권한 부여
chmod +x scripts/deployment.sh

# 자동 배포 실행
./scripts/deployment.sh
```

### 2. 스크립트 입력 정보
```
1. Docker Hub 사용자명: your_dockerhub_username
2. Docker Hub Personal Access Token: your_pat_token
3. 이미지 레포지토리명: ai-healthcare
4. 배포할 서비스: 1 (FastAPI), 2 (AI-Worker), 3 (Both)
5. 이미지 태그: v1.0.0
6. SSH 키 파일명: your-key.pem
7. EC2 퍼블릭 IP: 3.34.123.456
8. HTTPS 사용 여부: y/n
9. 도메인명 (HTTPS 선택 시): yourdomain.com
```

## 🔧 수동 배포 과정

### 1. Docker 이미지 빌드 및 푸시
```bash
# API 서버 이미지 빌드
docker build -f app/Dockerfile -t your_username/ai-healthcare:app-v1.0.0 .

# AI Worker 이미지 빌드  
docker build -f ai_worker/Dockerfile -t your_username/ai-healthcare:ai-v1.0.0 .

# Docker Hub 로그인
docker login

# 이미지 푸시
docker push your_username/ai-healthcare:app-v1.0.0
docker push your_username/ai-healthcare:ai-v1.0.0
```

### 2. EC2 서버 설정
```bash
# EC2 인스턴스 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# Docker 설치
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
sudo systemctl enable docker
sudo systemctl start docker

# 프로젝트 파일 업로드 (로컬에서 실행)
scp -i your-key.pem -r . ubuntu@your-ec2-ip:~/ai-healthcare/
```

### 3. 환경 설정
```bash
# EC2에서 환경 변수 설정
cd ~/ai-healthcare
cp envs/example.prod.env envs/.prod.env
ln -sf envs/.prod.env .env

# 환경 변수 편집
nano envs/.prod.env
```

### 4. 프로덕션 환경 변수 설정
```env
# 기본 설정
ENV=prod
DEBUG=false
ALLOWED_ORIGINS=["https://yourdomain.com", "http://your-ec2-ip"]

# JWT 보안 (반드시 변경)
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256

# Redis 설정
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# OAuth 설정 (실제 값으로 변경)
KAKAO_CLIENT_ID=your_kakao_client_id
KAKAO_CLIENT_SECRET=your_kakao_client_secret
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret

# 작업 설정
TASK_RESULT_TTL=3600
MAX_WORKERS=2

# 정적 파일 경로
STATIC_DIR=/app/static
```

### 5. 프로덕션 배포
```bash
# 프로덕션 Docker Compose 실행
docker-compose -f docker-compose.prod.yml up -d --build

# 서비스 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f
```

## 🔒 SSL/HTTPS 설정

### 1. Certbot 자동 설정
```bash
# SSL 설정 스크립트 실행
chmod +x scripts/certbot.sh
./scripts/certbot.sh
```

### 2. 수동 SSL 설정
```bash
# EC2에서 Certbot 설치
sudo apt install -y certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d yourdomain.com

# 자동 갱신 설정
sudo crontab -e
# 다음 라인 추가: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 모니터링 및 관리

### 1. 서비스 상태 확인
```bash
# 컨테이너 상태
docker ps

# 리소스 사용량
docker stats

# 로그 확인
docker-compose -f docker-compose.prod.yml logs --tail=100 fastapi
docker-compose -f docker-compose.prod.yml logs --tail=100 ai-worker
```

### 2. 업데이트 배포
```bash
# 새 이미지 빌드 및 푸시 (로컬)
docker build -f app/Dockerfile -t your_username/ai-healthcare:app-v1.1.0 .
docker push your_username/ai-healthcare:app-v1.1.0

# EC2에서 업데이트
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### 3. 백업 및 복구
```bash
# Redis 데이터 백업
docker exec redis redis-cli BGSAVE

# 로그 백업
docker-compose -f docker-compose.prod.yml logs > backup-$(date +%Y%m%d).log
```

## 💰 비용 최적화

### 무료 티어 한도
- EC2 t2.micro: 월 750시간 (24/7 운영 가능)
- EBS 스토리지: 30GB
- 데이터 전송: 15GB/월 아웃바운드

### 비용 절약 팁
1. **인스턴스 최적화**: t2.micro 메모리(1GB) 한도 내에서 운영
2. **이미지 최적화**: Multi-stage Docker 빌드로 이미지 크기 최소화
3. **로그 관리**: 로그 로테이션으로 디스크 사용량 제한
4. **모니터링**: CloudWatch 기본 메트릭 활용

## 🚨 문제 해결

### 메모리 부족 (t2.micro 1GB 제한)
```bash
# 스왑 파일 생성
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 디스크 공간 부족
```bash
# Docker 정리
docker system prune -a

# 로그 정리
sudo journalctl --vacuum-time=7d
```

### 서비스 재시작
```bash
# 전체 서비스 재시작
docker-compose -f docker-compose.prod.yml restart

# 개별 서비스 재시작
docker-compose -f docker-compose.prod.yml restart fastapi
docker-compose -f docker-compose.prod.yml restart ai-worker
```

## 🎯 배포 완료 체크리스트
- [ ] EC2 인스턴스 생성 및 보안 그룹 설정
- [ ] Docker 및 Docker Compose 설치
- [ ] 환경 변수 파일 설정 (.prod.env)
- [ ] Docker 이미지 빌드 및 푸시
- [ ] 프로덕션 서비스 실행
- [ ] 도메인 연결 (선택사항)
- [ ] SSL 인증서 설정 (HTTPS)
- [ ] API 엔드포인트 접근 테스트
- [ ] 만성질환 예측 서비스 동작 확인
- [ ] 모니터링 및 로그 확인 체계 구축