# TODO List

## Feature: 사용자 인증 (로그인/회원가입)

### DB Layer (db-agent)
- [x] User 모델 생성
  - [x] id (Primary Key)
  - [x] username (Unique, 필수)
  - [x] email (Unique, 필수)
  - [x] password_hash (필수)
  - [x] created_at (자동 생성)
  - [x] updated_at (자동 갱신)
  - [x] is_active (기본값: True)
- [x] User CRUD 함수 작성
  - [x] create_user() - 사용자 생성
  - [x] get_user_by_username() - username으로 조회
  - [x] get_user_by_email() - email으로 조회
  - [x] get_user_by_id() - id로 조회
  - [x] update_user() - 사용자 정보 수정
- [x] DB 마이그레이션/테이블 생성 확인

### BE Layer (be-agent)
- [x] 인증 관련 스키마 정의
  - [x] UserCreate (회원가입 요청)
  - [x] UserLogin (로그인 요청)
  - [x] UserResponse (응답)
  - [x] Token (JWT 토큰 응답)
- [x] 비밀번호 해싱 유틸리티
  - [x] hash_password() 함수
  - [x] verify_password() 함수
- [x] JWT 토큰 유틸리티
  - [x] create_access_token() 함수
  - [x] verify_token() 함수
- [x] 인증 API 엔드포인트
  - [x] POST /api/auth/register - 회원가입
  - [x] POST /api/auth/login - 로그인
  - [x] GET /api/auth/me - 현재 사용자 정보 조회
  - [ ] POST /api/auth/logout - 로그아웃 (선택사항)
- [x] 인증 미들웨어/의존성
  - [x] get_current_user() - 토큰 검증 및 사용자 조회

### FE Layer (fe-agent)
- [x] 회원가입 페이지 (`/register`)
  - [x] 회원가입 폼 컴포넌트
  - [x] username, email, password 입력 필드
  - [x] 폼 유효성 검증 (클라이언트)
  - [x] 회원가입 API 호출
  - [x] 성공/실패 메시지 표시
- [x] 로그인 페이지 (`/login`)
  - [x] 로그인 폼 컴포넌트
  - [x] username/email, password 입력 필드
  - [x] 폼 유효성 검증
  - [x] 로그인 API 호출
  - [x] JWT 토큰 저장 (localStorage/cookie)
  - [x] 성공 시 리다이렉트
- [x] 인증 상태 관리
  - [x] Auth Context/Provider 생성
  - [x] 로그인 상태 전역 관리
  - [ ] 토큰 자동 갱신 (선택사항)
- [x] 보호된 라우트 구현
  - [x] 인증 확인 HOC/컴포넌트
  - [x] 미인증 시 로그인 페이지로 리다이렉트
- [x] 네비게이션/헤더 업데이트
  - [x] 로그인/회원가입 버튼
  - [x] 로그인 후 사용자 정보 표시
  - [x] 로그아웃 버튼

---

## 작업 순서 권장
1. **DB Layer** → User 모델 및 CRUD 작성
2. **BE Layer** → 인증 API 구현
3. **FE Layer** → UI 및 API 연동

## 참고사항
- 비밀번호는 반드시 해싱하여 저장 (bcrypt 또는 passlib 사용)
- JWT 토큰은 환경변수로 SECRET_KEY 관리
- CORS 설정 확인 필요
- HTTPS 사용 권장 (프로덕션)
