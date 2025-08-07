# AI Collaboration Guidelines for FastAPI Authentication Server

## 프로젝트 개요
이 프로젝트는 FastAPI를 사용한 간단한 인증 서버입니다. 이메일/비밀번호 기반 회원가입, 로그인, JWT 토큰 인증을 제공합니다.

## 개발 규칙

### 1. 코드 품질 기준
- 모든 함수와 클래스에는 docstring을 작성해야 합니다
- Type hints를 반드시 사용해야 합니다
- PEP 8 스타일 가이드를 준수해야 합니다

### 2. 보안 고려사항
- 비밀번호는 반드시 bcrypt로 해시화해야 합니다
- JWT SECRET_KEY는 환경변수로 관리해야 합니다 (프로덕션 환경)
- 민감한 정보는 로그에 출력하지 않아야 합니다

### 3. API 설계 원칙
- RESTful API 설계 원칙을 따릅니다
- 적절한 HTTP 상태 코드를 사용합니다
- 에러 응답은 일관된 형식을 유지합니다

### 4. 테스트 요구사항
- 새로운 엔드포인트 추가 시 반드시 테스트 코드를 작성해야 합니다
- 성공 케이스와 실패 케이스 모두 테스트해야 합니다
- 테스트 커버리지는 80% 이상을 유지해야 합니다

### 5. 문서화
- API 변경사항은 README.md에 반영해야 합니다
- 새로운 기능 추가 시 사용 예시를 포함해야 합니다

## 협업 워크플로우

### 브랜치 전략
- : 프로덕션 준비 코드
- : 새로운 기능 개발
- : 버그 수정

### 커밋 메시지 규칙
-  새로운 기능 추가
-  버그 수정
-  문서 수정
-  테스트 코드 추가/수정
-  코드 리팩토링

## 향후 개선 계획
1. 데이터베이스 연동 (SQLite → PostgreSQL)
2. 이메일 인증 기능 추가
3. 비밀번호 재설정 기능
4. 사용자 프로필 관리
5. API 레이트 리미팅
6. 로깅 및 모니터링 시스템

## 개발 환경 설정
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scriptsctivate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn main:app --reload

# 테스트 실행
pytest tests/
```
