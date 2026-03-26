# Vibe Log — Refined Summary
> 최초 작성: 2025-01-06 | 최종 갱신: 2025-07-11

---

## 1. 아키텍처 전환 (MySQL → Redis)
**시점:** 2025-01-06 초기 구축

MySQL/Tortoise ORM 기반 구조를 완전히 제거하고 Redis 중심 아키텍처로 전환.

| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| DB | MySQL + Tortoise ORM + Aerich | 제거 |
| 서비스 통신 | 동기 DB 쿼리 | Redis Task Queue (Polling) |
| 스키마 공유 | 없음 | `schemas.py` (FastAPI ↔ AI Worker 공용) |
| API 경로 | 미통일 | `/api/v1` 접두사 통일 |

**핵심 결정:** AI Worker와 API 서버를 Redis 큐로 완전 분리 → 독립적 스케일링 가능

---

## 2. 만성질환 예측 서비스 구현
**시점:** 2025-01-06

전체 예측 파이프라인 구축: OAuth 인증 → 80개 피처 설문 → AI 추론 → 대시보드

- **스키마:** `ChronicDiseaseSurveyRequest` (80개 피처, 엄격한 Range/Type 검증)
- **예측 대상:** 알레르기비염(`DJ8_pre`), 고혈압(`DI1_pre`), 당뇨병(`DE1_pre`), 이상지질혈증(`DI2_pre`)
- **파이프라인:** 80개 입력 피처 → 127개 전처리 피처 → 7-fold 앙상블 → 4개 이진 예측
- **피처 검증:** `feature_validation.py` 스크립트로 스키마 ↔ AI Worker 피처 순서 일치 확인

---

## 3. OAuth 인증 시스템 구축 및 버그 수정
**시점:** 2025-01-06 ~ 2025-07-11 (반복 수정)

카카오/네이버 OAuth 인증 흐름 구현 중 발생한 주요 버그와 해결 이력.

| 버그 | 원인 | 해결 |
|------|------|------|
| 네이버 code를 카카오 API에 전송 | `provider` 판별을 React state로 처리 → 비동기 경쟁 조건 | `localStorage.oauth_provider` 기반 판별로 교체 |
| 카카오 동의 페이지 강제 노출 | `scope=profile_nickname` 요청 + 앱 필수 동의항목 충돌 | scope 제거, `/v2/user/me` → `/v1/user/access_token_info`로 대체 |
| 만료된 code 재사용 | 새로고침 시 URL의 code 파라미터 재전송 | 콜백 진입 즉시 `window.history.replaceState`로 code 제거 |
| useEffect 경쟁 조건 | `checkAuth`와 콜백 useEffect 동시 실행 | `isHandlingCallback` ref 플래그로 실행 순서 제어 |
| redirectUri 이중 인코딩 | `encodeURIComponent` 중복 적용 | `window.location.origin + '/'` 고정값 사용 |

---

## 4. CI/CD 파이프라인 구축 및 오류 수정
**시점:** 2025-07-11

GitHub Actions 3개 job 모두 통과 상태 달성.

### 4-1. Ruff Lint (`ruff check .`) — 141개 오류 수정
| 규칙 | 내용 |
|------|------|
| W291/W292/W293 | 후행 공백, 파일 끝 개행 누락 |
| I001 | import 정렬 (stdlib → third-party → local) |
| F401 | 미사용 import 제거 (`asyncio`, `Optional`, `Depends` 등) |
| UP035/UP006 | `typing.Dict` → `dict` 현대 문법 교체 |
| B904 | `except` 블록 내 `raise ... from e` 패턴 적용 |
| F821 | `ORJSONResponse` 미정의 참조 → import 추가 |
| N815 | `surveyData` mixedCase → `survey_data + alias="surveyData"` |
| C901 | `main()` 복잡도 초과 → 헬퍼 함수 분리 |

### 4-2. Ruff Format (`ruff format . --check`) — 9개 파일 포맷 불일치
`uv run ruff format .` 한 번 실행으로 전체 해결.

### 4-3. Pytest (`pytest app/tests`) — exit code 5 (테스트 0개)
`app/tests/` 디렉토리 신규 생성, 23개 테스트 작성.

| 파일 | 테스트 수 | 커버 범위 |
|------|-----------|-----------|
| `test_health.py` | 3 | `/health/`, `/health/redis` 정상/실패 |
| `test_auth.py` | 8 | test-login, logout, oauth-urls, 토큰 검증 |
| `test_chronic.py` | 3 | 서비스 정보, task 조회 404/200 |
| `test_schemas.py` | 9 | Pydantic 검증 (TaskStatus, UserInfo, Survey 등) |

---

## 5. 인프라 및 배포 설정
**시점:** 2025-01-06

- **Docker Compose:** MySQL 제거, Redis + FastAPI + AI Worker + Nginx + Certbot 구성
- **Nginx:** SPA fallback 라우팅, `/login.html` 명시적 location 블록
- **환경 변수:** `envs/.local.env` / `envs/.prod.env` 분리, MySQL 관련 변수 전체 제거
- **배포 대상:** AWS EC2 t2.micro (무료 티어), `scripts/deployment.sh` 자동화
- **SSL:** `scripts/certbot.sh`로 Let's Encrypt 인증서 자동 발급

---

## 6. 현재 상태 및 잔존 리스크

### ✅ CI 통과 상태
```
ruff check .        → All checks passed!
ruff format --check → 35 files already formatted
pytest app/tests    → 23 passed
```

### ⚠️ 잔존 리스크
| 항목 | 내용 |
|------|------|
| AI 모델 체크포인트 | 파일 부재 시 더미 데이터 반환 (운영 전 배치 필요) |
| `test-login` 토큰 | `user_id`만 포함 → `/me` 엔드포인트 401 반환 (OAuth 토큰과 구조 불일치) |
| `/chronic/predict` | AI Worker 폴링 로직으로 통합 테스트 미작성 |
| scikit-learn 버전 | 학습(1.7.2) ↔ 서빙(1.8.0) 불일치 경고 — 모델 재학습 권장 |
| t2.micro 메모리 | 1GB 제약으로 동시 사용자 수 제한 가능 |

### 📋 배포 전 체크리스트
- [ ] `envs/.prod.env`에 실제 OAuth Client ID/Secret 설정
- [ ] `JWT_SECRET` 프로덕션 값으로 교체
- [ ] AI 모델 체크포인트 파일(`checkpoints/`) 서버 배치
- [ ] 카카오/네이버 개발자 콘솔 Redirect URI 등록
- [ ] `cd src && npm run build`로 프론트엔드 최신 빌드
