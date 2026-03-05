# 📊 프로젝트 전체 구조 분석

## 🏗️ 아키텍처 개요
**마이크로서비스 기반 AI 헬스케어 플랫폼** - FastAPI 서버와 AI Worker가 분리된 구조

---

## 📦 핵심 컴포넌트

### 1. **FastAPI 서버** (`app/`)
사용자 인증 및 API 제공

- **apis/v1/** - REST API 엔드포인트
  - `auth_routers.py` - 회원가입/로그인/토큰 관리
  - `user_routers.py` - 사용자 정보 조회/수정
  
- **core/** - 서버 설정
  - `config.py` - 환경변수 관리 (DB, JWT, 타임존)
  - `logger.py` - 로깅 설정

- **db/** - 데이터베이스 레이어
  - `databases.py` - Tortoise ORM 설정 (MySQL 연결)
  - `migrations/` - Aerich 마이그레이션 파일

- **models/** - DB 테이블 정의
  - `users.py` - 사용자 모델

- **repositories/** - 데이터 접근 계층
  - `user_repository.py` - 사용자 CRUD

- **services/** - 비즈니스 로직
  - `auth.py` - 인증 로직
  - `jwt.py` - JWT 토큰 생성/검증
  - `users.py` - 사용자 관리

- **dtos/** - 데이터 전송 객체 (Pydantic)
  - `auth.py`, `users.py` - 요청/응답 스키마

- **utils/** - 유틸리티
  - `jwt/` - JWT 토큰 처리 백엔드
  - `security.py` - 비밀번호 해싱

- **validators/** - 입력 검증
  - `user_validators.py` - 사용자 데이터 검증

- **dependencies/** - FastAPI 의존성
  - `security.py` - 인증 의존성

- **tests/** - 테스트 코드
  - `auth_apis/` - 인증 API 테스트
  - `user_apis/` - 사용자 API 테스트
  - `conftest.py` - 테스트 설정

### 2. **AI Worker** (`ai_worker/`)
AI 모델 추론 및 학습 (현재 비어있음 - 확장 가능)

- **core/** - 워커 설정
  - `config.py` - 워커 환경변수
  - `logger.py` - 로깅 설정
- **schemas/** - 데이터 스키마
- **tasks/** - AI 작업 정의
- **main.py** - 워커 진입점 (현재 비어있음)

### 3. **인프라** (Docker Compose)
5개 서비스로 구성:

1. **MySQL** - 데이터베이스 (포트 3306)
   - UTF-8 문자셋 설정
   - 볼륨 마운트로 데이터 영속성 보장
2. **Redis** - 캐싱/메시지 브로커 (포트 6379)
   - Health check 설정
3. **FastAPI** - API 서버 (포트 8000)
   - Hot reload 지원
   - MySQL, Redis 의존성
4. **AI Worker** - AI 처리
   - 메모리 4GB 제한
   - MySQL, Redis 의존성
5. **Nginx** - 리버스 프록시 (포트 80)
   - FastAPI로 요청 전달
   - 정적 파일 서빙

---

## 🔧 기술 스택

### 백엔드
- **FastAPI** - 비동기 웹 프레임워크
- **Tortoise ORM** - 비동기 ORM (MySQL)
- **Pydantic** - 데이터 검증
- **JWT** - 인증 (PyJWT)
- **Bcrypt** - 비밀번호 해싱
- **ORJSON** - 고성능 JSON 직렬화

### AI/ML (설치 가능)
- **PyTorch, TorchVision, TorchAudio** - 딥러닝 프레임워크
- **Scikit-learn** - 머신러닝
- **Sentence-Transformers** - 임베딩 모델

### 인프라
- **Docker & Docker Compose** - 컨테이너화
- **MySQL 8.0** - 관계형 데이터베이스
- **Redis** - 인메모리 데이터베이스
- **Nginx** - 웹 서버/리버스 프록시
- **UV** - 고속 Python 패키지 관리

### 개발 도구
- **Ruff** - 린팅/포맷팅
- **Mypy** - 정적 타입 체크
- **Pytest** - 테스트 프레임워크
- **Aerich** - DB 마이그레이션
- **Coverage** - 테스트 커버리지

---

## 🔐 보안 기능

- JWT 기반 인증 (Access/Refresh Token)
- Bcrypt 비밀번호 해싱
- 환경변수 분리 (`.local.env`, `.prod.env`)
- HTTPS 지원 (Certbot 스크립트)
- Cookie 기반 토큰 저장

---

## 🚀 배포 전략

### 로컬 개발
- `docker-compose.yml` 사용
- Hot reload 지원
- 볼륨 마운트로 코드 변경 즉시 반영

### 프로덕션
- `docker-compose.prod.yml` 사용
- `scripts/deployment.sh` - Docker Hub 푸시 및 EC2 배포
- `scripts/certbot.sh` - SSL 인증서 자동 발급 (Let's Encrypt)
- 버전 태그 관리 (APP_VERSION, AI_WORKER_VERSION)

---

## 📈 현재 구현 상태

### ✅ 완료
- 사용자 인증 시스템 (회원가입/로그인/토큰)
- JWT 기반 인증 (Access/Refresh Token)
- DB 연동 (MySQL + Tortoise ORM)
- Docker 컨테이너화
- CI/CD 스크립트
- 테스트 코드 (Pytest)
- API 문서화 (Swagger UI)

### ⚠️ 미구현
- AI Worker 로직 (빈 파일)
- Redis 활용 로직
- 실제 헬스케어 기능
- 비동기 작업 큐

---

## 💡 확장 포인트

1. **AI Worker에 모델 추가**
   - `ai_worker/tasks/`에 추론 로직 구현
   - PyTorch 모델 로드 및 추론
   - Redis를 통한 작업 큐 구현

2. **API 엔드포인트 추가**
   - `app/apis/v1/`에 새 라우터 추가
   - `app/apis/v1/__init__.py`에 라우터 등록

3. **DB 모델 확장**
   - `app/models/`에 새 테이블 정의
   - `app/db/databases.py`의 TORTOISE_APP_MODELS에 추가
   - `aerich migrate` 실행

4. **Redis 캐싱**
   - 자주 조회되는 데이터 캐싱
   - 세션 관리
   - Rate limiting

5. **비동기 작업 큐**
   - Redis + Celery/RQ 통합
   - 백그라운드 작업 처리

---

## 📁 디렉토리 구조

```
.
├── ai_worker/              # AI 워커
│   ├── core/              # 설정 및 로거
│   ├── schemas/           # 데이터 스키마
│   ├── tasks/             # AI 작업
│   └── main.py            # 진입점
├── app/                   # FastAPI 서버
│   ├── apis/v1/          # API 라우터
│   ├── core/             # 서버 설정
│   ├── db/               # DB 설정 및 마이그레이션
│   ├── dependencies/     # FastAPI 의존성
│   ├── dtos/             # 요청/응답 스키마
│   ├── models/           # DB 모델
│   ├── repositories/     # 데이터 접근 계층
│   ├── services/         # 비즈니스 로직
│   ├── tests/            # 테스트 코드
│   ├── utils/            # 유틸리티
│   ├── validators/       # 입력 검증
│   └── main.py           # FastAPI 앱
├── envs/                 # 환경변수 파일
├── nginx/                # Nginx 설정
├── scripts/              # 배포 및 CI 스크립트
│   └── ci/              # 코드 품질 검사
├── docker-compose.yml    # 로컬 개발용
├── docker-compose.prod.yml # 프로덕션용
└── pyproject.toml        # 의존성 관리
```

---

## 🔄 데이터 흐름

1. **사용자 요청** → Nginx (포트 80)
2. **Nginx** → FastAPI (포트 8000)
3. **FastAPI** → MySQL (데이터 조회/저장)
4. **FastAPI** ↔ Redis (캐싱/세션)
5. **FastAPI** → AI Worker (AI 작업 요청, 향후 구현)
6. **AI Worker** ↔ Redis (작업 큐, 향후 구현)

---

## 🧪 테스트 실행

```bash
# 전체 테스트
./scripts/ci/run_test.sh

# 코드 포맷팅 검사
./scripts/ci/code_fommatting.sh

# 타입 체크
./scripts/ci/check_mypy.sh
```

---

## 📝 개발 가이드

### API 추가
1. `app/apis/v1/`에 라우터 파일 생성
2. `app/apis/v1/__init__.py`에 라우터 등록
3. DTO 정의 (`app/dtos/`)
4. 서비스 로직 구현 (`app/services/`)
5. 테스트 작성 (`app/tests/`)

### DB 모델 추가
1. `app/models/`에 Tortoise 모델 정의
2. `app/db/databases.py`의 TORTOISE_APP_MODELS에 추가
3. 마이그레이션 생성: `aerich migrate`
4. 마이그레이션 적용: `aerich upgrade`

### AI 로직 추가
1. `ai_worker/tasks/`에 작업 정의
2. `ai_worker/main.py`에서 작업 실행
3. Redis를 통한 작업 큐 구현 (선택)
