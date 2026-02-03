# Test Plan - 인증 시스템

## DB Layer Tests (backend/tests/)

### User 모델 테스트
- [x] User 생성 테스트
- [x] User ID로 조회 테스트
- [x] username으로 조회 테스트
- [x] email로 조회 테스트
- [x] User 정보 수정 테스트
- [x] User 삭제 테스트
- [x] username unique 제약조건 테스트
- [x] email unique 제약조건 테스트

### User CRUD 함수 테스트
- [x] create_user() - 정상 생성
- [x] get_user_by_id() - 존재하는 사용자
- [x] get_user_by_id() - 존재하지 않는 사용자
- [x] get_user_by_username() - 존재하는 사용자
- [x] get_user_by_username() - 존재하지 않는 사용자
- [x] get_user_by_email() - 존재하는 사용자
- [x] get_user_by_email() - 존재하지 않는 사용자
- [x] update_user() - 정상 수정
- [x] update_user() - 존재하지 않는 사용자
- [x] delete_user() - 정상 삭제
- [x] delete_user() - 존재하지 않는 사용자

---

## BE Layer Tests (backend/tests/)

### 보안 유틸리티 테스트 (test_security.py - 22 tests)
- [x] 비밀번호 해싱 테스트
- [x] 비밀번호 검증 테스트 (정상)
- [x] 비밀번호 검증 테스트 (실패)
- [x] JWT 토큰 생성 테스트
- [x] JWT 토큰 검증 테스트 (유효한 토큰)
- [x] JWT 토큰 검증 테스트 (만료된 토큰)
- [x] JWT 토큰 검증 테스트 (잘못된 토큰)

### 인증 API 엔드포인트 테스트 (test_auth_api.py - 27 tests)
- [x] POST /api/auth/register - 정상 회원가입
- [x] POST /api/auth/register - 중복 username
- [x] POST /api/auth/register - 중복 email
- [x] POST /api/auth/register - 유효성 검증 실패 (짧은 username)
- [x] POST /api/auth/register - 유효성 검증 실패 (짧은 password)
- [x] POST /api/auth/register - 유효성 검증 실패 (잘못된 email)

- [x] POST /api/auth/login - 정상 로그인 (username)
- [x] POST /api/auth/login - 정상 로그인 (email)
- [x] POST /api/auth/login - 잘못된 username
- [x] POST /api/auth/login - 잘못된 password
- [x] POST /api/auth/login - 비활성화된 계정
- [x] POST /api/auth/login - JWT 토큰 반환 확인

- [x] GET /api/auth/me - 인증된 사용자 정보 조회
- [x] GET /api/auth/me - 인증 토큰 없음 (401)
- [x] GET /api/auth/me - 잘못된 토큰 (401)
- [x] GET /api/auth/me - 만료된 토큰 (401)

### 인증 의존성 테스트 (test_auth_dependency.py - 19 tests)
- [x] get_current_user() - 유효한 토큰
- [x] get_current_user() - 토큰 없음
- [x] get_current_user() - 잘못된 토큰
- [x] get_current_user() - 존재하지 않는 사용자

---

## FE Layer Tests (frontend/src/tests/)

### API 클라이언트 테스트
- [ ] 회원가입 API 호출 테스트
- [ ] 로그인 API 호출 테스트
- [ ] 현재 사용자 정보 조회 API 호출 테스트
- [ ] API 에러 핸들링 테스트

### 회원가입 페이지 테스트
- [ ] 회원가입 폼 렌더링 테스트
- [ ] username 입력 필드 테스트
- [ ] email 입력 필드 테스트
- [ ] password 입력 필드 테스트
- [ ] 폼 유효성 검증 테스트 (클라이언트)
- [ ] 회원가입 제출 테스트 (성공)
- [ ] 회원가입 제출 테스트 (실패)
- [ ] 에러 메시지 표시 테스트

### 로그인 페이지 테스트
- [ ] 로그인 폼 렌더링 테스트
- [ ] username/email 입력 필드 테스트
- [ ] password 입력 필드 테스트
- [ ] 폼 유효성 검증 테스트
- [ ] 로그인 제출 테스트 (성공)
- [ ] 로그인 제출 테스트 (실패)
- [ ] 토큰 저장 테스트
- [ ] 로그인 후 리다이렉트 테스트

### Auth Context 테스트
- [ ] AuthProvider 렌더링 테스트
- [ ] 로그인 상태 관리 테스트
- [ ] 로그아웃 기능 테스트
- [ ] 토큰 자동 로드 테스트
- [ ] 인증 상태 변경 감지 테스트

### 보호된 라우트 테스트
- [ ] 인증된 사용자 접근 허용 테스트
- [ ] 미인증 사용자 리다이렉트 테스트
- [ ] 로딩 상태 테스트

---

## 통합 테스트 (E2E)

### 회원가입 플로우
- [ ] 회원가입 페이지 접근 → 폼 작성 → 제출 → 성공 메시지

### 로그인 플로우
- [ ] 로그인 페이지 접근 → 폼 작성 → 제출 → 토큰 저장 → 리다이렉트

### 인증 플로우
- [ ] 보호된 페이지 접근 → 로그인 리다이렉트 → 로그인 → 보호된 페이지 접근 성공

### 로그아웃 플로우
- [ ] 로그인 상태 → 로그아웃 → 토큰 삭제 → 로그인 페이지 리다이렉트

---

## 테스트 실행 방법

### DB Layer 테스트
```bash
cd backend
.venv\Scripts\activate
pytest tests/test_user_crud.py -v
```

### BE Layer 테스트
```bash
cd backend
.venv\Scripts\activate
pytest tests/test_auth_api.py -v
pytest tests/test_security.py -v
```

### FE Layer 테스트
```bash
cd frontend
npm test
```

### 전체 테스트 실행
```bash
# Backend 전체 테스트
cd backend
pytest -v

# Frontend 전체 테스트
cd frontend
npm test
```

---

## 테스트 커버리지 목표

- **DB Layer**: 100% (모든 CRUD 함수)
- **BE Layer**: 90% 이상 (핵심 인증 로직)
- **FE Layer**: 80% 이상 (주요 컴포넌트 및 플로우)
