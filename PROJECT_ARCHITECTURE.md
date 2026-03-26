# 프로젝트 아키텍처 구성도
> 만성질환 AI 예측 서비스 — 전체 시스템 분석 문서

---

## 1. 시스템 전체 흐름도

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            Client (Browser)                             │
│                    React SPA (Vite + TypeScript)                        │
│   LoginPage / ServiceSelectPage / SurveyPage / DashboardPage           │
└────────────────────────────┬────────────────────────────────────────────┘
                             │ HTTP/HTTPS (Port 80/443)
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Nginx (Port 80)                                  │
│  - /api/*        → proxy_pass → FastAPI:8000                           │
│  - /assets/*     → static files (캐시 1년)                              │
│  - /*            → SPA fallback (index.html)                           │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     FastAPI Server (Port 8000)                          │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  app/main.py                                                      │  │
│  │  - CORS Middleware                                                │  │
│  │  - StaticFiles mount (/assets)                                   │  │
│  │  - SPA fallback route                                            │  │
│  └──────────────────────────┬───────────────────────────────────────┘  │
│                             │                                           │
│  ┌──────────────────────────▼───────────────────────────────────────┐  │
│  │  API Router  /api/v1                                              │  │
│  │  ├── /auth        (auth_router)                                  │  │
│  │  ├── /chronic     (chronic_router)                               │  │
│  │  └── /health      (health_router)                                │  │
│  └──────────────────────────┬───────────────────────────────────────┘  │
│                             │                                           │
│  ┌──────────────────────────▼───────────────────────────────────────┐  │
│  │  Dependencies / Services                                          │  │
│  │  ├── dependencies/auth.py  → get_current_user (JWT Bearer)       │  │
│  │  └── services/oauth.py     → OAuthService (Kakao / Naver)        │  │
│  └──────────────────────────┬───────────────────────────────────────┘  │
│                             │                                           │
│  ┌──────────────────────────▼───────────────────────────────────────┐  │
│  │  app/db/databases.py                                              │  │
│  │  - Redis ConnectionPool (get_redis / close_redis)                │  │
│  └──────────────────────────┬───────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────────┘
                             │ Redis LPUSH / HSET
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Redis (Port 6379)                               │
│  - chronic_disease_prediction_queue  (List, LPUSH/BRPOP)               │
│  - task:{task_id}                    (Hash, TTL=3600s)                  │
│    fields: task_id, status, data, result, error,                        │
│            created_at, completed_at                                     │
│  - AOF 영속성 (appendonly yes, appendfsync everysec)                    │
└────────────────────────────┬────────────────────────────────────────────┘
                             │ BRPOP (blocking pop)
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       AI Worker Service                                 │
│                                                                         │
│  ai_worker/main.py  →  AIWorker.run()                                  │
│  ├── connect_redis()                                                    │
│  └── while True: BRPOP → process_chronic_disease_prediction()          │
│                                                                         │
│  ai_worker/models/chronic_predictor.py  →  ChronicDiseasePredictor     │
│  ├── _load_preprocessing_artifacts()                                    │
│  │   ├── scaler.pkl          (StandardScaler)                          │
│  │   ├── encoder.joblib      (OneHotEncoder)                           │
│  │   ├── feature_columns.json                                          │
│  │   └── encoding_cols.json                                            │
│  ├── _convert_survey_to_dataframe()  (80 features → DataFrame)         │
│  ├── _preprocess_input()             (OHE + Scaling → 127-dim)         │
│  └── _inference()                   (7-fold Ensemble)                  │
│      ├── fold1_artifact.pth ~ fold7_artifact.pth                       │
│      └── Predictor (PyTorch) → 4 disease binary predictions            │
│          DJ8_pre(알레르기비염) / DI1_pre(고혈압)                         │
│          DE1_pre(당뇨병)       / DI2_pre(이상지질혈증)                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. API 엔드포인트 목록

### `/api/v1/auth` — 인증

| Method | Path | 인증 필요 | 설명 |
|--------|------|-----------|------|
| POST | `/oauth/login` | ❌ | Kakao / Naver OAuth 로그인 |
| GET | `/me` | ✅ Bearer | 현재 사용자 정보 조회 |
| POST | `/logout` | ❌ | 로그아웃 |
| POST | `/test-login` | ❌ | 테스트용 JWT 발급 |
| GET | `/oauth/urls` | ❌ | OAuth Client ID 반환 |

### `/api/v1/chronic` — 만성질환 예측

| Method | Path | 인증 필요 | 설명 |
|--------|------|-----------|------|
| POST | `/predict` | ❌ | 동기 예측 (최대 30초 폴링) |
| POST | `/predict/async` | ✅ Bearer | 비동기 예측 (Task ID 반환) |
| GET | `/task/{task_id}` | ❌ | Task 상태 조회 |
| GET | `/` | ❌ | 서비스 정보 |

### `/api/v1/health` — 헬스체크

| Method | Path | 설명 |
|--------|------|------|
| GET | `/` | 서버 상태 확인 |

---

## 3. 데이터 흐름 — 만성질환 예측 (동기)

```
Client
  │
  │  POST /api/v1/chronic/predict
  │  Body: ChronicDiseaseSurveyRequest (80 fields)
  ▼
FastAPI (chronic.py)
  │  1. uuid4() → task_id 생성
  │  2. Redis HSET task:{task_id} {status:pending, data:json}
  │  3. Redis EXPIRE task:{task_id} 3600s
  │  4. Redis LPUSH chronic_disease_prediction_queue task_id
  │  5. Polling loop (최대 30초, 0.5s 간격)
  ▼
Redis Queue
  │  BRPOP chronic_disease_prediction_queue
  ▼
AI Worker
  │  1. Redis HSET task:{task_id} status=processing
  │  2. ChronicDiseasePredictor.predict(data)
  │     - DataFrame 변환 (80 features)
  │     - OHE + StandardScaler → 127-dim
  │     - 7-fold Ensemble (softmax weighted by val_f2)
  │     - Sigmoid → threshold → binary prediction
  │  3. Redis HSET task:{task_id} {status:completed, result:json}
  ▼
FastAPI (polling 감지)
  │  status == completed → result 파싱
  ▼
Client
   Response: PredictionResponse
   {
     predictions: {DJ8_pre, DI1_pre, DE1_pre, DI2_pre},
     guidelines: null,
     surveyData: {key: "value", ...}
   }
```

---

## 4. 공유 스키마 구조 (`schemas.py`)

```
schemas.py  ← FastAPI + AI Worker 공동 사용
│
├── TaskStatus (StrEnum)
│   pending / processing / completed / failed
│
├── ChronicDiseaseSurveyRequest (BaseModel)
│   80개 필드 (인구학적 / 건강상태 / 생활습관 / 신체계측 등)
│   Range Check: sex(0-2), age(1-120) 등
│
├── PredictionResponse (BaseModel)
│   predictions: dict[str, int]   # 4개 질환 0/1
│   guidelines: Any | None
│   surveyData: dict[str, str]    # alias="surveyData"
│
├── TaskRequest / TaskResponse (BaseModel)
│   task_id, status, result, error, created_at, completed_at
│
├── OAuthProvider (StrEnum)  kakao / naver
├── OAuthRequest (BaseModel) provider, code, redirect_uri
├── UserInfo (BaseModel)     user_id, provider
└── AuthResponse (BaseModel) access_token, user_info
```

---

## 5. 인증 흐름 (OAuth 2.0 + JWT)

```
Client
  │  POST /api/v1/auth/oauth/login
  │  {provider, code, redirect_uri}
  ▼
OAuthService
  │  1. OAuth Provider (Kakao/Naver) 토큰 교환
  │  2. Provider API로 user_id 조회
  │  3. JWT 생성 (HS256, 24h 만료)
  │     payload: {user_id, provider, exp, iat}
  ▼
Client  ←  {access_token, user_info}

Protected Route 접근:
  Authorization: Bearer <access_token>
  → get_current_user() → OAuthService.verify_access_token()
  → UserInfo 반환
```

---

## 6. AI 모델 아키텍처

```
Predictor (PyTorch)
│
├── Input: 127-dim (OHE + Scaled)
├── input_norm: BatchNorm1d(127)
├── stem: Linear(127→254) + SiLU
│
├── stage1: 3× AdvancedResidualBlock(254)
│   └── BN → SiLU → Linear → Dropout → BN → SiLU → Linear → SEBlock
│
├── transition: Linear(254→42) + BN + SiLU
│
├── stage2: 2× AdvancedResidualBlock(42)
│
└── classifier: Linear(42→21) + SiLU + Dropout + Linear(21→4)
    Output: 4 logits → Sigmoid → threshold → binary

Ensemble: 7-fold, softmax(val_f2 / T=0.44) weighted averaging
```

---

## 7. 컨테이너 구성 (docker-compose.yml)

```
┌─────────────────────────────────────────────────────────┐
│                   Docker Network: ws                    │
│                                                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────┐  │
│  │  nginx   │    │ fastapi  │    │    ai-worker     │  │
│  │  :80     │───▶│  :8000   │    │  mem_limit: 4G   │  │
│  │          │    │          │    │                  │  │
│  └──────────┘    └────┬─────┘    └────────┬─────────┘  │
│                       │                   │             │
│                       └─────────┬─────────┘             │
│                                 ▼                       │
│                          ┌──────────┐                   │
│                          │  redis   │                   │
│                          │  :6379   │                   │
│                          │  AOF ON  │                   │
│                          └──────────┘                   │
└─────────────────────────────────────────────────────────┘

볼륨:
  redis_data  → Redis AOF 영속성
  ./static    → Nginx + FastAPI 공유 (SPA 빌드 결과물)
  ./schemas.py → fastapi + ai-worker 공유 마운트
```

---

## 8. 프론트엔드 구조 (`src/`)

```
src/app/
├── components/
│   ├── LoginPage.tsx         # OAuth 로그인 UI
│   ├── ServiceSelectPage.tsx # 서비스 선택
│   ├── SurveyPage.tsx        # 80문항 설문 폼
│   ├── DashboardPage.tsx     # 예측 결과 대시보드
│   └── ui/                   # shadcn/ui 컴포넌트 (40+)
├── context/
│   └── AuthContext.tsx       # JWT 토큰 전역 상태
├── services/
│   └── api.ts                # FastAPI 호출 클라이언트
├── data/
│   └── surveyQuestions.ts    # 설문 문항 정의
└── routes.ts                 # React Router 경로 정의

빌드 결과: ./static/ (FastAPI + Nginx가 서빙)
```

---

## 9. CI/CD 파이프라인 (`.github/workflows/checks.yml`)

```
Push / PR
  │
  ├── lint job
  │   ├── uv run ruff check .
  │   └── uv run ruff format --check .
  │
  ├── type-check job
  │   └── uv run mypy app/ ai_worker/
  │
  └── test job
      └── uv run pytest app/tests/ --cov

배포 (수동):
  scripts/deployment.sh
  → Docker build → Docker Hub push → SSH EC2 → docker-compose up
```

---

## 10. 디렉토리 구조 전체

```
AI_HealthCare_Final_Project_Template/
│
├── schemas.py                  ← 공유 Pydantic 스키마 (FastAPI + AI Worker)
│
├── app/                        ← FastAPI 서버
│   ├── main.py                 ← 앱 진입점, CORS, StaticFiles, SPA fallback
│   ├── apis/v1/
│   │   ├── __init__.py         ← v1_routers 집계
│   │   ├── auth.py             ← OAuth 로그인/로그아웃/JWT
│   │   ├── chronic.py          ← 만성질환 예측 (동기/비동기/폴링)
│   │   └── health.py           ← 헬스체크
│   ├── core/
│   │   ├── config.py           ← Config (pydantic-settings)
│   │   └── logger.py
│   ├── db/
│   │   └── databases.py        ← Redis ConnectionPool
│   ├── dependencies/
│   │   └── auth.py             ← get_current_user (JWT 검증)
│   ├── services/
│   │   └── oauth.py            ← OAuthService (Kakao/Naver + JWT)
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_chronic.py
│   │   ├── test_health.py
│   │   └── test_schemas.py
│   └── Dockerfile
│
├── ai_worker/                  ← AI 추론 워커
│   ├── main.py                 ← AIWorker (BRPOP 루프)
│   ├── core/
│   │   └── config.py           ← Redis 설정
│   ├── models/
│   │   ├── chronic_predictor.py ← ChronicDiseasePredictor
│   │   ├── inference.py
│   │   └── checkpoints/        ← 모델 아티팩트
│   │       ├── fold1~7_artifact.pth
│   │       ├── scaler.pkl
│   │       ├── encoder.joblib
│   │       ├── feature_columns.json
│   │       └── encoding_cols.json
│   └── Dockerfile
│
├── src/                        ← React SPA (Vite + TypeScript)
│   └── app/
│       ├── components/         ← 페이지 컴포넌트 + shadcn/ui
│       ├── context/            ← AuthContext
│       ├── services/api.ts     ← API 클라이언트
│       └── data/               ← 설문 문항 데이터
│
├── static/                     ← Vite 빌드 결과물 (서빙 대상)
│
├── nginx/
│   ├── default.conf            ← 로컬 (HTTP)
│   ├── prod_http.conf          ← 프로덕션 HTTP
│   └── prod_https.conf         ← 프로덕션 HTTPS (SSL)
│
├── envs/
│   ├── .local.env / .prod.env
│   └── example.*.env
│
├── scripts/
│   ├── ci/                     ← ruff / mypy / pytest 스크립트
│   ├── deployment.sh           ← EC2 자동 배포
│   └── certbot.sh              ← Let's Encrypt SSL
│
├── .github/workflows/checks.yml
├── docker-compose.yml
├── docker-compose.prod.yml
└── pyproject.toml              ← uv 의존성 (app / ai / dev 그룹)
```

---

## 11. 점검 결과 요약

### ✅ 정상 구현된 항목
- Redis 기반 Task Queue (LPUSH/BRPOP) + TTL(3600s) 설정
- 공유 `schemas.py` (FastAPI ↔ AI Worker 데이터 일관성)
- 7-fold Ensemble 추론 (val_f2 가중 softmax)
- OAuth 2.0 (Kakao/Naver) + JWT HS256 인증
- SPA(React) StaticFiles 서빙 + Nginx fallback
- Docker Compose 4-서비스 구성 (redis/fastapi/ai-worker/nginx)
- AOF 영속성 활성화 (`appendonly yes`)
- CI 스크립트 (ruff/mypy/pytest)

### ⚠️ 주의 사항
| 항목 | 내용 |
|------|------|
| `schemas.py` 위치 | 프로젝트 루트에 위치 — Docker 볼륨 마운트로 공유 중. 패키지화 권장 |
| `/predict` 인증 없음 | 동기 예측 엔드포인트에 인증 미적용 (Rate Limit 필요) |
| JWT Secret 기본값 | `config.py`에 하드코딩된 기본값 존재 — 반드시 환경변수로 교체 |
| `test-login` 엔드포인트 | 프로덕션 배포 전 제거 또는 ENV 조건부 비활성화 필요 |
| MySQL/ORM 제거됨 | `structure.md`에 명시된 대로 DB 없이 Redis만 사용 (무상태 설계) |
| `app/db/databases.py` | 파일명은 databases이나 실제로는 Redis 전용 — 혼동 가능 |

### ❌ 미구현 항목
| 항목 | 내용 |
|------|------|
| `ai_worker/schemas/` | 디렉토리 존재하나 `__init__.py`만 있음 (루트 schemas.py 사용 중) |
| `ai_worker/tasks/` | 디렉토리 존재하나 `__init__.py`만 있음 (main.py에 직접 구현) |
| `app/db/migrations/` | 디렉토리 존재하나 비어있음 (DB 미사용으로 불필요) |
| Health Guidelines | `PredictionResponse.guidelines` 항상 `null` 반환 |

---

> **잠재적 리스크**: `/predict` 엔드포인트 인증 부재로 인한 무제한 AI 추론 요청 가능 — DDoS 및 비용 폭증 위험.

> **권장 사항 (Best Practice)**: `schemas.py`를 `shared/schemas.py` 패키지로 이동하고, `/predict`에 Rate Limiting(slowapi 등) 또는 인증을 적용하며, `JWT_SECRET`을 반드시 환경변수로만 주입할 것.

> **현재 리스크 (Current Limitation)**: `test-login` 엔드포인트가 프로덕션에 노출될 경우 인증 우회 가능. `guidelines` 필드 미구현으로 프론트엔드 대시보드의 건강 개선 가이드 기능 비활성 상태.
