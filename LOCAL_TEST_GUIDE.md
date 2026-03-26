# 로컬 테스트 가이드라인

## 🚀 빠른 시작 (Windows 환경)

### 1. 사전 준비
```bash
# Docker Desktop 설치 확인
docker --version
docker compose version
```

### 2. 환경 설정
```powershell
# 프로젝트 디렉토리로 이동
cd AI_HealthCare_Final_Project_Template

# 환경 변수 파일 복사
copy envs\example.local.env envs\.local.env

# .env 파일 생성 (심볼릭 링크 대신 복사 권장 - Windows 호환성)
copy envs\.local.env .env
```

### 3. OAuth 설정
`envs\.local.env` 파일에서 실제 값으로 변경합니다.
OAuth 등록 방법은 `OAUTH_SETUP_GUIDE.md`를 참고하세요.

```env
KAKAO_CLIENT_ID=발급받은_REST_API_키
KAKAO_CLIENT_SECRET=발급받은_Client_Secret
NAVER_CLIENT_ID=발급받은_Client_ID
NAVER_CLIENT_SECRET=발급받은_Client_Secret
```

> OAuth 없이 테스트하려면 아래 **테스트 로그인** 섹션을 참고하세요.

### 4. 전체 서비스 실행
```bash
docker compose up -d --build

# 서비스 상태 확인
docker compose ps

# 로그 확인
docker compose logs -f
```

서비스 구성: **Redis → FastAPI → AI Worker → Nginx** (MySQL 없음)

---

## 🌐 URL 접근 동작 방식

| URL | 동작 |
|-----|------|
| `http://localhost` | 인증 X → 로그인 페이지, 인증 O → 서비스 선택 페이지 |
| `http://localhost/login.html` | 동일 (SPA fallback → index.html → React Router 처리) |
| `http://localhost/api/docs` | Swagger UI |
| `http://localhost/api/v1/health/` | 헬스체크 |

> **핵심**: `login.html`은 별도 파일이 아닙니다. Nginx가 `/login.html` 요청을 `index.html`(SPA)로 서빙하고, React Router가 인증 상태에 따라 로그인 페이지 또는 서비스 선택 페이지를 렌더링합니다.

---

## 🧪 테스트 시나리오

### 1. 기본 접근 테스트
- **메인 페이지**: http://localhost → 로그인 페이지 표시 확인
- **로그인 URL**: http://localhost/login.html → 동일하게 로그인 페이지 표시 확인
- **API 문서**: http://localhost/api/docs

### 2. OAuth 없이 테스트 로그인
브라우저 개발자 도구 콘솔에서:
```javascript
const res = await fetch('/api/v1/auth/test-login', { method: 'POST' });
const data = await res.json();
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('user_info', JSON.stringify(data.user_info));
location.reload(); // 새로고침 후 서비스 선택 페이지로 이동 확인
```

PowerShell에서:
```powershell
$response = Invoke-RestMethod -Uri "http://localhost/api/v1/auth/test-login" -Method POST
$token = $response.access_token
Write-Host "Access Token: $token"
```

### 3. 카카오/네이버 로그인 테스트
OAuth 키 설정 후 http://localhost 접속 → 카카오/네이버 버튼 클릭 → 인증 완료 후 서비스 선택 페이지 이동 확인

**OAuth 흐름:**
1. 로그인 버튼 클릭 → `localStorage`에 `oauth_provider` 저장 후 OAuth 인증 페이지로 리다이렉트
2. 인증 완료 → `http://localhost/?code=...` 로 콜백
3. `AuthContext`가 `oauth_provider` 값으로 provider 판별 → 백엔드 `/api/v1/auth/oauth/login` 호출
4. JWT 토큰 발급 → 서비스 선택 페이지로 이동

> **카카오 Redirect URI**: `http://localhost` (개발자 콘솔에 등록 필요)
> **네이버 Redirect URI**: `http://localhost` (개발자 콘솔에 등록 필요)

### 4. 만성질환 예측 테스트
```powershell
# 테스트 로그인으로 토큰 획득 후 예측 API 호출
$loginResponse = Invoke-RestMethod -Uri "http://localhost/api/v1/auth/test-login" -Method POST
$token = $loginResponse.access_token

$surveyData = @{
    sex = 1; age = 35; cfam = 3; genertn = 1; house = 1; live_t = 1
    marri_1 = 1; fam_rela = 1; tins = 1; npins = 0; D_1_1 = 3; D_2_1 = 0
    M_2_yr = 0; BH9_11 = 1; BH1 = 1; BH2_61 = 1; LQ4_00 = 0; LQ1_sb = 0
    LQ2_ab = 0; AC1_yr = 0; MH1_yr = 0; MO1_wk = 0; educ = 4; EC1_1 = 1
    EC_lgw_2 = 5; BO1 = 2; BO1_1 = 0.0; BO2_1 = 0.0; BD1_11 = 0; BD2_1 = 0
    BD2_31 = 0; BD7_4 = 0.0; BD7_5 = 0.0; BA2_12 = 1.0; BA2_13 = 1.0
    BA2_14 = 1.0; BP1 = 2; BP7 = 0; BS1_1 = 3; BS12_37 = 0; BS12_1 = 0
    BS8_2 = 0; BS9_2 = 0; BS13 = 0; BE3_71 = 0; BE3_81 = 3; BE3_91 = 5
    BE3_75 = 0; BE3_85 = 2; BE8_1 = 8; BE3_31 = 5; BE5_1 = 0; HE_fh = 0
    HE_ht = 165.5; HE_wt = 60.2; HE_wc = 75.0; OR1 = 3; O_pain = 0
    O_ortho = 0; BM1_0 = 1; BM7 = 0; BM8 = 0; OR1_2 = 1; MO4_00 = 0
    BM14 = 0; E_Q_EX = 1; L_BR_FQ = 7; L_LN_FQ = 7; L_DN_FQ = 7
    L_OUT_FQ = 2; LS_VEG1 = 5; LS_VEG2 = 3; LS_FRUIT = 4; LS_1YR = 0
    LK_EDU = 0; LK_LB_CO = 1; N_DIET = 0; N_DUSUAL = 2; N_WAT_C = 6
    LF_SAFE = 1
}

$headers = @{ Authorization = "Bearer $token" }
$prediction = Invoke-RestMethod -Uri "http://localhost/api/v1/chronic/predict" `
    -Method POST `
    -Body ($surveyData | ConvertTo-Json) `
    -ContentType "application/json" `
    -Headers $headers
Write-Host ($prediction | ConvertTo-Json -Depth 3)
```

### 5. 프론트엔드 재빌드 (UI 수정 시)
```powershell
cd src
npm install
npm run build
# 빌드 결과물이 자동으로 ../static 에 생성됨 (vite.config.ts 설정)
```

---

## 🔧 문제 해결

### Docker 관련
```bash
# 컨테이너 재시작
docker compose restart

# 볼륨 포함 완전 재시작
docker compose down -v
docker compose up -d --build

# 개별 서비스 로그
docker compose logs fastapi
docker compose logs ai-worker
docker compose logs redis
docker compose logs nginx
```

### 포트 충돌
- 80 포트 사용 중: `docker-compose.yml`에서 `"8080:80"`으로 변경 후 `http://localhost:8080` 접속

### login.html 접근 시 빈 화면
- `static/index.html`이 존재하는지 확인: `dir static\index.html`
- 없다면 프론트엔드 빌드 필요: `cd src && npm install && npm run build`

### OAuth 로그인 후 로그인 페이지로 돌아오는 경우
1. 카카오/네이버 개발자 콘솔에서 Redirect URI가 `http://localhost`로 등록되어 있는지 확인
2. 브라우저 개발자 도구 → Network 탭에서 `/api/v1/auth/oauth/login` 응답 확인
3. `OAUTH_SETUP_GUIDE.md` 참고

### 네이버 로그인이 카카오 오류를 반환하는 경우
- 이전 버전의 버그입니다. 최신 코드에서는 `localStorage.oauth_provider`로 provider를 정확히 판별합니다.
- 브라우저 localStorage를 초기화 후 재시도: `localStorage.clear()`

---

## 📊 서비스 상태 확인
```bash
# Redis 연결 상태
curl http://localhost/api/v1/health/redis

# 서비스 정보
curl http://localhost/api/v1/chronic/

# 리소스 사용량
docker stats
```

---

## 🎯 테스트 완료 체크리스트
- [ ] Docker 서비스 모두 Up 상태 (`docker compose ps`)
- [ ] `http://localhost` → 로그인 페이지 표시
- [ ] `http://localhost/login.html` → 로그인 페이지 표시 (동일)
- [ ] `http://localhost/api/docs` → Swagger UI 접근
- [ ] 테스트 로그인 후 서비스 선택 페이지로 이동
- [ ] 카카오/네이버 로그인 동작 (OAuth 키 설정 시)
- [ ] 80개 피처 예측 API 응답 (30초 이내)
- [ ] 4개 질환 예측 결과 반환 (DJ8_pre, DI1_pre, DE1_pre, DI2_pre)
