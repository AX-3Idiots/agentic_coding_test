# FastAPI Authentication Server

이 프로젝트는 이메일과 비밀번호를 이용한 간단한 회원가입 및 로그인 기능을 제공하는 FastAPI 기반 API 서버입니다.

## 주요 기능

- 회원가입 ()
- 로그인 () 
- JWT 기반 인증
- 보호된 엔드포인트 ()

## 설치 및 실행

1. 의존성 설치:
```bash
pip install -r requirements.txt
```

2. 서버 실행:
```bash
uvicorn main:app --reload
```

## API 엔드포인트

-  - 회원가입
-  - 로그인  
-  - 사용자 정보 조회 (인증 필요)

## 개발 환경

- Python 3.8+
- FastAPI
- JWT 토큰 기반 인증
- bcrypt 비밀번호 해싱
