# OAuth 서비스 등록 가이드라인

OAuth 인증을 실제로 동작시키려면 아래 플랫폼에 애플리케이션을 등록하고 발급받은 키를 환경 변수에 설정해야 합니다.

---

## 카카오 OAuth 등록

### 1. 애플리케이션 생성
1. [Kakao Developers](https://developers.kakao.com) 접속 → 로그인
2. **내 애플리케이션** → **애플리케이션 추가하기**
3. 앱 이름, 사업자명 입력 후 저장

### 2. 플랫폼 등록
1. 생성된 앱 선택 → **플랫폼** 탭
2. **Web 플랫폼 등록** 클릭
3. 사이트 도메인 입력:
   - 로컬: `http://localhost`
   - 배포: `https://yourdomain.com`

### 3. Redirect URI 등록
1. **카카오 로그인** 탭 → **활성화 설정** ON
2. **Redirect URI** 등록:
   - 로컬: `http://localhost`
   - 배포: `https://yourdomain.com`
   > ⚠️ React SPA 구조이므로 redirect_uri는 도메인 루트(`/`)로 설정합니다.
   > 콜백 코드 처리는 프론트엔드 AuthContext에서 URL 파라미터로 처리합니다.

### 4. 동의항목 설정
1. **동의항목** 탭
2. 필수 동의 항목 설정:
   - **닉네임**: 필수 동의
   - **프로필 사진**: 선택 동의
   - **카카오계정(이메일)**: 선택 동의 (비즈니스 앱 전환 시 필수 가능)

### 5. 키 확인
1. **앱 키** 탭에서 **REST API 키** 복사
2. **보안** 탭에서 **Client Secret** 생성 및 복사

---

## 네이버 OAuth 등록

### 1. 애플리케이션 생성
1. [Naver Developers](https://developers.naver.com) 접속 → 로그인
2. **Application** → **애플리케이션 등록**
3. 애플리케이션 이름 입력
4. **사용 API**: **네아로(네이버 아이디로 로그인)** 선택
5. 제공 정보 선택:
   - **이름**: 필수
   - **이메일**: 필수
   - **프로필 사진**: 선택

### 2. 환경 등록
1. **PC 웹** 선택
2. 서비스 URL 입력:
   - 로컬: `http://localhost`
   - 배포: `https://yourdomain.com`
3. Callback URL 입력:
   - 로컬: `http://localhost`
   - 배포: `https://yourdomain.com`

### 3. 키 확인
등록 완료 후 **Client ID**와 **Client Secret** 복사

---

## 환경 변수 설정

발급받은 키를 `envs/.local.env` (로컬) 또는 `envs/.prod.env` (배포)에 입력합니다.

```env
KAKAO_CLIENT_ID=발급받은_REST_API_키
KAKAO_CLIENT_SECRET=발급받은_Client_Secret
NAVER_CLIENT_ID=발급받은_Client_ID
NAVER_CLIENT_SECRET=발급받은_Client_Secret
```

설정 후 서비스 재시작:
```bash
docker-compose restart fastapi
```

---

## 로컬 테스트 시 주의사항

카카오/네이버 OAuth는 **등록된 도메인에서만 동작**합니다.

- `http://localhost`는 카카오에서 허용됩니다.
- 네이버는 `http://localhost`를 허용하지 않는 경우가 있습니다. 이 경우 `http://127.0.0.1`로 시도하거나, 테스트 로그인 API를 사용하세요.

### OAuth 없이 테스트하는 방법
```bash
# 테스트 로그인 API 호출 (OAuth 설정 불필요)
curl -X POST http://localhost/api/v1/auth/test-login
```
반환된 `access_token`을 브라우저 localStorage에 저장하면 인증된 상태로 서비스를 테스트할 수 있습니다.

```javascript
// 브라우저 개발자 도구 콘솔에서 실행
const res = await fetch('/api/v1/auth/test-login', { method: 'POST' });
const data = await res.json();
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('user_info', JSON.stringify(data.user_info));
location.reload();
```

---

## 배포 환경 Redirect URI 추가 등록

도메인을 연결한 후에는 카카오/네이버 개발자 콘솔에서 **Redirect URI를 추가 등록**해야 합니다.

| 환경 | Redirect URI |
|------|-------------|
| 로컬 | `http://localhost` |
| HTTP 배포 | `http://yourdomain.com` |
| HTTPS 배포 | `https://yourdomain.com` |
