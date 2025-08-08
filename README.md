# FastAPI Authentication API

이 프로젝트는 이메일과 비밀번호를 이용한 간단한 회원가입 및 로그인 기능을 제공하는 FastAPI 기반 API 서버입니다.

## 주요 기능

- **회원가입**: 이메일과 비밀번호로 새 계정 생성
- **로그인**: 인증 후 JWT 토큰 발급
- **보호된 엔드포인트**: JWT 토큰 기반 사용자 정보 조회

## API 엔드포인트

### 인증 관련
- `POST /register` - 회원가입
- `POST /login` - 로그인
- `GET /me` - 현재 사용자 정보 조회 (JWT 토큰 필요)

## 기술 스택

- **FastAPI**: 고성능 웹 프레임워크
- **bcrypt**: 비밀번호 해시 처리
- **PyJWT**: JWT 토큰 생성 및 검증
- **uvicorn**: ASGI 서버

## 실행 방법

1. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```

2. 서버 실행:
   ```bash
   uvicorn main:app --reload
   ```

3. API 문서 확인: http://localhost:8000/docs

## 데이터 저장

개발용으로 사용자 정보는 JSON 파일에 임시 저장됩니다.
프로덕션 환경에서는 적절한 데이터베이스를 사용하세요.

## 보안 고려사항

- 비밀번호는 bcrypt로 해시 처리
- JWT 토큰에는 민감한 정보 포함하지 않음
- 토큰 만료 시간 설정 (기본 24시간)
