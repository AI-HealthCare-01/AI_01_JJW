# 프로젝트 점검 및 구현 가이드라인
> 작성일: 2025-07-11 | 목적: 현재 상태 점검 → 목표 서비스 구현 로드맵

---

## 1. 현재 프로젝트 구조 점검

### 1-1. 전체 디렉토리 구조 (실제 현황)

```
AI_HealthCare_Final_Project_Template/
├── app/                        # FastAPI 서버
│   ├── apis/v1/
│   │   ├── auth.py             # OAuth 로그인/로그아웃/me (실제 사용 중)
│   │   ├── auth_routers.py     # JWT 기반 signup/login (미사용 - 레거시)
│   │   ├── chronic.py          # 만성질환 예측 API
│   │   ├── health.py           # 헬스체크 API
│   │   └── __init__.py         # 라우터 등록 (auth_router, chronic_router, health_router)
│   ├── core/config.py          # 환경변수 설정 (Redis, OAuth, JWT, CORS)
│   ├── db/databases.py         # Redis 연결 관리
│   ├── dependencies/auth.py    # JWT 토큰 검증 → UserInfo 반환
│   ├── services/oauth.py       # 카카오/네이버 OAuth 처리 + JWT 발급
│   ├── tests/                  # pytest 테스트 (23개)
│   └── main.py                 # FastAPI 앱 진입점 + SPA 서빙
├── ai_worker/                  # AI 추론 워커
│   ├── core/config.py          # 워커 환경변수
│   ├── models/
│   │   ├── checkpoints/        # 학습된 모델 파일 (7-fold .pth, scaler, encoder)
│   │   ├── chronic_predictor.py # 추론 로직 (80→127 피처 전처리 + 앙상블)
│   │   └── inference.py        # (미사용 추정)
│   └── main.py                 # Redis 큐 폴링 워커
├── src/                        # React + TypeScript 프론트엔드 (빌드 소스)
│   └── app/
│       ├── components/         # LoginPage, ServiceSelectPage, SurveyPage, DashboardPage
│       ├── context/AuthContext.tsx  # OAuth 인증 상태 관리
│       ├── services/api.ts     # FastAPI 연동 HTTP 클라이언트
│       └── App.tsx             # React Router 라우팅
├── static/                     # 빌드된 SPA 파일 (Nginx/FastAPI가 서빙)
├── schemas.py                  # FastAPI ↔ AI Worker 공용 Pydantic 스키마
├── docker-compose.yml          # Redis + FastAPI + AI Worker + Nginx
└── nginx/default.conf          # 리버스 프록시 + SPA fallback
```

---

### 1-2. 시스템 흐름도 (현재 구현 상태)

```
[사용자 브라우저]
      │
      │ HTTP 80포트
      ▼
[Nginx]
  ├── /api/* → FastAPI:8000 (프록시)
  ├── /assets/* → static/ (캐시)
  └── /* → static/index.html (SPA fallback)
      │
      ▼
[FastAPI :8000]
  ├── GET  /api/v1/auth/oauth/urls     → 카카오/네이버 OAuth URL 반환
  ├── POST /api/v1/auth/oauth/login    → OAuth code → JWT 발급
  ├── GET  /api/v1/auth/me             → JWT 검증 → UserInfo 반환
  ├── POST /api/v1/auth/logout         → (상태 없음, 클라이언트 토큰 삭제)
  ├── POST /api/v1/chronic/predict     → 설문 데이터 → Redis 큐 → 폴링 → 결과 반환
  ├── POST /api/v1/chronic/predict/async → 비동기 task_id 반환
  ├── GET  /api/v1/chronic/task/{id}   → task 상태 조회
  ├── GET  /api/v1/chronic/            → 서비스 정보
  └── GET  /api/v1/health/*            → 헬스체크
      │
      │ Redis 큐 (chronic_disease_prediction_queue)
      ▼
[AI Worker]
  └── brpop 대기 → task_id 수신 → ChronicDiseasePredictor.predict()
        └── 80개 피처 → OHE 인코딩 → 스케일링 → 127차원
              └── 7-fold 앙상블 → 가중 평균 → 임계값 적용
                    └── {DJ8_pre, DI1_pre, DE1_pre, DI2_pre} (0 or 1)
      │
      ▼
[Redis]
  └── task:{task_id} hash 저장 (status, result, TTL=3600s)
```

---

### 1-3. 서비스 흐름도 (현재 프론트엔드 구현 상태)

```
브라우저 접근
    │
    ▼
App.tsx (BrowserRouter)
    │
    ├── "/" → RootRedirect
    │         ├── isLoading=true → 로딩 스피너
    │         ├── user 있음 → /select-service 리다이렉트
    │         └── user 없음 → LoginPage 렌더링
    │
    ├── "/select-service" → ServiceSelectPage
    │         └── (인증 가드 없음 ⚠️)
    │
    ├── "/survey" → SurveyPage
    │         └── (인증 가드 없음 ⚠️)
    │
    └── "/dashboard" → DashboardPage
              └── (인증 가드 없음 ⚠️)

AuthContext 흐름:
    마운트 시 URL에 ?code= 있으면 → handleOAuthCallback()
                                      → oauthLogin() API 호출
                                      → JWT 저장 (localStorage)
                                      → /select-service 이동
    URL에 code 없으면 → checkAuth()
                        → localStorage 토큰 확인
                        → /auth/me API 호출
                        → user 상태 복원
```

---

## 2. 현재 상태 점검 결과

### ✅ 정상 구현된 항목

| 항목 | 상태 | 비고 |
|------|------|------|
| 카카오 OAuth 로그인 | ✅ | `OAuthService.get_kakao_user_info()` |
| 네이버 OAuth 로그인 | ✅ | `OAuthService.get_naver_user_info()` |
| JWT 발급/검증 | ✅ | `OAuthService.create/verify_access_token()` |
| Redis 큐 기반 AI 추론 | ✅ | `chronic.py` → Redis → `ai_worker/main.py` |
| 7-fold 앙상블 모델 | ✅ | checkpoints/ 파일 존재 |
| 80개 피처 스키마 | ✅ | `schemas.py ChronicDiseaseSurveyRequest` |
| SPA 서빙 (Nginx + FastAPI) | ✅ | `nginx/default.conf` + `app/main.py` |
| 4개 질환 대시보드 UI | ✅ | `DashboardPage.tsx` |
| CI 파이프라인 | ✅ | ruff + pytest 23개 통과 |

### ❌ 미구현 / 결함 항목

| 항목 | 문제 | 위치 |
|------|------|------|
| **인증 가드 (Route Guard)** | `/select-service`, `/survey`, `/dashboard` 비인증 접근 가능 | `App.tsx` |
| **이미 로그인 시 안내 메시지** | 로그인 상태로 `/` 접근 시 메시지 없이 바로 리다이렉트 | `App.tsx RootRedirect` |
| **설문 데이터 검증 실패 처리** | 서버 400 응답 시 "서버에 데이터를 전달하는 과정에서 문제가 생겼습니다" 안내 + 초기화 미구현 | `SurveyPage.tsx handleSubmit` |
| **분석 진행중 화면** | 제출 후 `submitting=true` 상태이나 별도 전체화면 로딩 UI 없음 | `SurveyPage.tsx` |
| **레거시 라우터 충돌** | `auth_routers.py` (JWT signup/login)가 `__init__.py`에 미등록이나 파일 잔존 | `app/apis/v1/auth_routers.py` |
| **`/auth/oauth/urls` 응답 불일치** | 서버는 `{kakao, naver}` URL 문자열 반환, 클라이언트는 `kakao_client_id`, `naver_client_id` 필드 기대 | `auth.py` vs `AuthContext.tsx` |
| **`test-login` 토큰 구조 불일치** | `user_id`만 포함 → `/me` 엔드포인트 401 | `auth.py test_login()` |
| **`COOKIE_DOMAIN` 설정 누락** | `config.py`에 `COOKIE_DOMAIN` 필드 없음 (auth_routers.py에서 참조) | `app/core/config.py` |
| **프론트엔드 미빌드** | `static/` 폴더가 구버전 빌드 상태일 수 있음 | `src/` → `static/` |

---

## 3. 목표 서비스 구현을 위한 작업 목록

### Phase 1 — 인증 가드 구현 (최우선)

**목표:** 비인증 사용자의 `/select-service`, `/survey`, `/dashboard` 접근 차단

**작업 파일:** `src/app/App.tsx`

```
현재: Route에 인증 가드 없음
목표: ProtectedRoute 컴포넌트 추가
      → user 없으면 "/" (LoginPage)로 리다이렉트
      → isLoading 중이면 로딩 스피너 표시
```

**구현 방향:**
```tsx
// ProtectedRoute 컴포넌트 추가
function ProtectedRoute({ children }) {
  const { user, isLoading } = useAuth();
  if (isLoading) return <로딩 스피너>;
  if (!user) return <Navigate to="/" replace />;
  return children;
}

// 적용 대상 라우트
<Route path="/select-service" element={<ProtectedRoute><ServiceSelectPage /></ProtectedRoute>} />
<Route path="/survey" element={<ProtectedRoute><SurveyPage /></ProtectedRoute>} />
<Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
```

---

### Phase 2 — 이미 로그인 시 안내 메시지 구현

**목표:** 로그인 상태로 `/` 접근 시 "이미 카카오/네이버 로그인이 되어있습니다." 메시지 표시 후 이동

**작업 파일:** `src/app/App.tsx` (RootRedirect 컴포넌트)

```
현재: user 있으면 즉시 /select-service로 Navigate
목표: user 있으면 toast 메시지 표시 후 /select-service로 이동
      메시지: "이미 {provider} 로그인이 되어있습니다."
```

**구현 방향:**
```tsx
function RootRedirect() {
  const { user, isLoading } = useAuth();
  
  useEffect(() => {
    if (user) {
      toast.info(`이미 ${user.provider === 'kakao' ? '카카오' : '네이버'} 로그인이 되어있습니다.`);
    }
  }, [user]);
  
  if (isLoading) return <로딩 스피너>;
  if (user) return <Navigate to="/select-service" replace />;
  return <LoginPage />;
}
```

---

### Phase 3 — 설문 데이터 검증 실패 처리 구현

**목표:** 서버 검증 실패 시 안내 메시지 + 설문 초기화 + 첫 문항으로 이동

**작업 파일:** `src/app/components/SurveyPage.tsx` (handleSubmit 함수)

```
현재: 에러 시 toast.error("설문 제출에 실패했습니다. 다시 시도해 주세요.")
목표: HTTP 422/400 응답 시
      → toast.error("서버에 데이터를 전달하는 과정에서 문제가 생겼습니다. 설문을 다시 진행해 주세요")
      → setAnswers({}) (전체 초기화)
      → setCurrentPage(0) (첫 문항으로 이동)
```

**구현 방향:**
```tsx
const handleSubmit = async () => {
  setSubmitting(true);
  try {
    const result = await submitSurvey(answers);
    navigate("/dashboard", { state: { result } });
  } catch (error: any) {
    // 서버 검증 실패 (422 Unprocessable Entity) 또는 400
    if (error.message?.includes('422') || error.message?.includes('400')) {
      toast.error("서버에 데이터를 전달하는 과정에서 문제가 생겼습니다. 설문을 다시 진행해 주세요");
      setAnswers({});
      setCurrentPage(0);
    } else {
      toast.error("설문 제출에 실패했습니다. 다시 시도해 주세요.");
    }
    setSubmitting(false);
  }
};
```

---

### Phase 4 — 분석 진행중 전체화면 UI 구현

**목표:** 설문 제출 후 AI 분석 중 전체화면 로딩 화면 표시

**작업 파일:** `src/app/components/SurveyPage.tsx`

```
현재: submitting=true 시 버튼 텍스트만 "분석 중..."으로 변경
목표: submitting=true 시 전체화면 오버레이 표시
      → "분석 진행중.." 텍스트 + 로딩 애니메이션
      → 배경 클릭/ESC 불가 (사용자 이탈 방지)
```

**구현 방향:**
```tsx
{submitting && (
  <div className="fixed inset-0 bg-white/90 backdrop-blur-sm z-50 flex flex-col items-center justify-center">
    <Loader2 className="h-12 w-12 animate-spin text-blue-600 mb-4" />
    <p className="text-xl text-gray-700">분석 진행중..</p>
    <p className="text-sm text-gray-500 mt-2">AI가 건강 데이터를 분석하고 있습니다</p>
  </div>
)}
```

---

### Phase 5 — OAuth URL API 응답 불일치 수정

**목표:** 서버 응답과 클라이언트 기대값 일치

**문제 상세:**
- 서버(`auth.py /auth/oauth/urls`)는 완성된 URL 문자열 반환: `{kakao: "https://...", naver: "https://..."}`
- 클라이언트(`AuthContext.tsx login()`)는 `urls.kakao_client_id`, `urls.naver_client_id` 필드 기대

**선택지 A — 서버 수정 (권장):** `/auth/oauth/urls`가 `client_id`만 반환하도록 변경
```python
# auth.py
return ORJSONResponse(content={
    "kakao_client_id": oauth_service.kakao_client_id,
    "naver_client_id": oauth_service.naver_client_id,
})
```

**선택지 B — 클라이언트 수정:** `AuthContext.tsx`에서 완성된 URL을 직접 사용
```tsx
// AuthContext.tsx login()
if (provider === 'kakao') {
  oauthUrl = urls.kakao;  // 서버가 반환한 완성 URL 사용
} else {
  const state = Math.random().toString(36).substring(2, 15);
  localStorage.setItem('oauth_state', state);
  oauthUrl = urls.naver.replace('{state}', state) + `&redirect_uri=${encodeURIComponent(redirectUri)}`;
}
```

> **권장:** 선택지 A (서버에서 client_id만 반환, 클라이언트에서 URL 조립)

---

### Phase 6 — 레거시 파일 정리

**목표:** 미사용 코드 제거로 혼란 방지

| 파일 | 조치 |
|------|------|
| `app/apis/v1/auth_routers.py` | 삭제 (JWT signup/login 레거시, OAuth로 대체됨) |
| `app/apis/v1/user_routers.py` | 내용 확인 후 삭제 또는 통합 |
| `ai_worker/models/inference.py` | 내용 확인 후 삭제 또는 통합 |
| `app/db/databases.py` | MySQL 관련 잔존 코드 있으면 제거 |

---

### Phase 7 — 프론트엔드 재빌드 및 배포 준비

**목표:** `src/` 변경사항을 `static/`에 반영

```bash
cd src
npm install
npm run build
# → static/ 폴더 갱신됨
```

**확인 사항:**
- `static/index.html` 존재 여부
- `static/assets/` JS/CSS 번들 최신화 여부

---

## 4. 작업 우선순위 요약

| 순서 | 작업 | 중요도 | 예상 난이도 |
|------|------|--------|------------|
| 1 | Phase 1: 인증 가드 (ProtectedRoute) | 🔴 Critical | 낮음 |
| 2 | Phase 5: OAuth URL API 불일치 수정 | 🔴 Critical | 낮음 |
| 3 | Phase 2: 이미 로그인 안내 메시지 | 🟡 High | 낮음 |
| 4 | Phase 3: 설문 검증 실패 처리 | 🟡 High | 낮음 |
| 5 | Phase 4: 분석 진행중 전체화면 UI | 🟡 High | 낮음 |
| 6 | Phase 6: 레거시 파일 정리 | 🟢 Medium | 낮음 |
| 7 | Phase 7: 프론트엔드 재빌드 | 🔴 Critical | 낮음 |

---

## 5. 배포 전 최종 체크리스트

### 환경변수 설정 (`envs/.prod.env`)
- [ ] `KAKAO_CLIENT_ID` — 카카오 개발자 콘솔에서 발급
- [ ] `KAKAO_CLIENT_SECRET` — 카카오 개발자 콘솔에서 발급
- [ ] `NAVER_CLIENT_ID` — 네이버 개발자 콘솔에서 발급
- [ ] `NAVER_CLIENT_SECRET` — 네이버 개발자 콘솔에서 발급
- [ ] `JWT_SECRET` — 안전한 랜덤 문자열로 교체
- [ ] `ALLOWED_ORIGINS` — 실제 도메인 추가

### OAuth 콘솔 설정
- [ ] 카카오 개발자 콘솔 → Redirect URI 등록: `https://도메인/`
- [ ] 네이버 개발자 콘솔 → Redirect URI 등록: `https://도메인/`

### 빌드 및 파일 확인
- [ ] `cd src && npm run build` 실행 → `static/` 갱신
- [ ] `ai_worker/models/checkpoints/` 파일 7개 존재 확인

### 서비스 기동 확인
- [ ] `docker-compose up -d --build` 정상 실행
- [ ] `http://localhost/api/docs` Swagger UI 접근 가능
- [ ] `http://localhost/` 로그인 페이지 표시
- [ ] 카카오/네이버 로그인 → `/select-service` 이동
- [ ] 설문 80개 완료 → 분석 → 대시보드 표시

---

## 6. 잠재적 리스크 및 권장 사항

**잠재적 리스크:** OAuth Redirect URI 불일치 시 로그인 전체 불가 — 콘솔 등록값과 코드의 `window.location.origin + '/'` 값이 정확히 일치해야 함.

**권장 사항 (Best Practice):**
- `ProtectedRoute` 구현 시 `isLoading` 상태를 반드시 처리하여 깜빡임(flash) 방지
- JWT 만료 시 자동 로그아웃 처리를 `api.ts` apiClient에 401 인터셉터로 추가 권장
- AI Worker 체크포인트 파일은 Docker 이미지에 포함하지 말고 볼륨 마운트로 관리

**현재 제한사항 (Current Limitations):**
- `t2.micro` 1GB 메모리 — AI Worker + FastAPI 동시 실행 시 OOM 위험
- scikit-learn 학습(1.7.2) ↔ 서빙(1.8.0) 버전 불일치 — 모델 재학습 또는 버전 고정 필요
- 로그아웃이 서버 상태 없이 클라이언트 토큰 삭제만 수행 — JWT 블랙리스트 미구현
