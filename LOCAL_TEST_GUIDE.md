# 로컬 테스트 가이드라인

## 🚀 빠른 시작 (Windows 환경)

### 1. 사전 준비
```bash
# Docker Desktop 설치 확인
docker --version
docker-compose --version

# UV 패키지 매니저 설치 (선택사항)
# https://github.com/astral-sh/uv 에서 Windows 설치 파일 다운로드
```

### 2. 환경 설정
```bash
# 프로젝트 디렉토리로 이동
cd AI_HealthCare_Final_Project_Template

# 환경 변수 파일 복사
copy envs\example.local.env envs\.local.env

# .env 심볼릭 링크 생성 (관리자 권한 필요)
mklink .env envs\.local.env
```

### 3. OAuth 설정 (선택사항)
`envs\.local.env` 파일에서 다음 값들을 실제 값으로 변경:
```env
# 카카오 개발자 콘솔에서 발급
KAKAO_CLIENT_ID=your_kakao_client_id
KAKAO_CLIENT_SECRET=your_kakao_client_secret

# 네이버 개발자 센터에서 발급
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
```

### 4. 전체 서비스 실행
```bash
# 모든 서비스 빌드 및 실행
docker-compose up -d --build

# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f
```

## 🧪 테스트 시나리오

### 1. 기본 접근 테스트
- **메인 페이지**: http://localhost
- **API 문서**: http://localhost/api/docs
- **로그인 페이지**: http://localhost/login.html

### 2. OAuth 없이 테스트 로그인
```bash
# PowerShell에서 테스트 로그인 API 호출
$response = Invoke-RestMethod -Uri "http://localhost/api/v1/auth/test-login" -Method POST
$token = $response.access_token
echo "Access Token: $token"
```

### 3. 만성질환 예측 테스트
```bash
# 80개 피처 설문 데이터로 예측 테스트
$surveyData = @{
    sex = 1; age = 35; cfam = 3; genertn = 1; house = 1; live_t = 1;
    marri_1 = 1; fam_rela = 1; tins = 1; npins = 0; D_1_1 = 3; D_2_1 = 0;
    M_2_yr = 0; BH9_11 = 1; BH1 = 1; BH2_61 = 1; LQ4_00 = 0; LQ1_sb = 0;
    LQ2_ab = 0; AC1_yr = 0; MH1_yr = 0; MO1_wk = 0; educ = 4; EC1_1 = 1;
    EC_lgw_2 = 5; BO1 = 2; BO1_1 = 0.0; BO2_1 = 0.0; BD1_11 = 0; BD2_1 = 0;
    BD2_31 = 0; BD7_4 = 0.0; BD7_5 = 0.0; BA2_12 = 1.0; BA2_13 = 1.0;
    BA2_14 = 1.0; BP1 = 2; BP7 = 0; BS1_1 = 3; BS12_37 = 0; BS12_1 = 0;
    BS8_2 = 0; BS9_2 = 0; BS13 = 0; BE3_71 = 0; BE3_81 = 3; BE3_91 = 5;
    BE3_75 = 0; BE3_85 = 2; BE8_1 = 8; BE3_31 = 5; BE5_1 = 0; HE_fh = 0;
    HE_ht = 165.5; HE_wt = 60.2; HE_wc = 75.0; OR1 = 3; O_pain = 0;
    O_ortho = 0; BM1_0 = 1; BM7 = 0; BM8 = 0; OR1_2 = 1; MO4_00 = 0;
    BM14 = 0; E_Q_EX = 1; L_BR_FQ = 7; L_LN_FQ = 7; L_DN_FQ = 7;
    L_OUT_FQ = 2; LS_VEG1 = 5; LS_VEG2 = 3; LS_FRUIT = 4; LS_1YR = 0;
    LK_EDU = 0; LK_LB_CO = 1; N_DIET = 0; N_DUSUAL = 2; N_WAT_C = 6;
    LF_SAFE = 1
}

$prediction = Invoke-RestMethod -Uri "http://localhost/api/v1/chronic/predict" -Method POST -Body ($surveyData | ConvertTo-Json) -ContentType "application/json"
echo "예측 결과: $($prediction | ConvertTo-Json -Depth 3)"
```

### 4. 프론트엔드 빌드 (선택사항)
```bash
# src 디렉토리로 이동
cd src

# Node.js 의존성 설치
npm install

# 프로덕션 빌드
npm run build

# 빌드 결과를 static 디렉토리로 복사
xcopy /E /I /Y dist\* ..\static\
```

## 🔧 문제 해결

### Docker 관련 문제
```bash
# 컨테이너 재시작
docker-compose restart

# 볼륨 포함 완전 재시작
docker-compose down -v
docker-compose up -d --build

# 개별 서비스 로그 확인
docker-compose logs fastapi
docker-compose logs ai-worker
docker-compose logs redis
```

### 포트 충돌 문제
- 80 포트 사용 중인 경우: `docker-compose.yml`에서 `"8080:80"`으로 변경
- MySQL 3306 포트 충돌: `"3307:3306"`으로 변경

### AI 모델 파일 없음
- 현재는 더미 데이터 반환 (정상 동작)
- 실제 모델 파일은 `ai_worker/models/checkpoints/` 디렉토리에 배치

## 📊 성능 모니터링
```bash
# 리소스 사용량 확인
docker stats

# Redis 연결 상태 확인
curl http://localhost/api/v1/health/redis

# 서비스 정보 확인
curl http://localhost/api/v1/chronic/
```

## 🎯 테스트 완료 체크리스트
- [ ] Docker 서비스 모두 Up 상태
- [ ] API 문서 접근 가능 (http://localhost/api/docs)
- [ ] 로그인 페이지 로드 (http://localhost/login.html)
- [ ] 테스트 로그인 API 동작
- [ ] 80개 피처 예측 API 응답 (30초 이내)
- [ ] 4개 질환 예측 결과 반환 (DJ8_pre, DI1_pre, DE1_pre, DI2_pre)