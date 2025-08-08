# API 테스트 가이드

## 수동 테스트

### 1. 회원가입 테스트
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

### 2. 로그인 테스트
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

### 3. 사용자 정보 조회 테스트
```bash
# 위에서 받은 토큰을 사용
curl -X GET "http://localhost:8000/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

## 자동화된 테스트

향후 pytest를 사용한 자동화된 테스트 코드를 추가할 예정입니다.

### 테스트 시나리오
1. 정상적인 회원가입 플로우
2. 중복 이메일 회원가입 시도
3. 정상적인 로그인 플로우
4. 잘못된 비밀번호로 로그인 시도
5. 유효한 토큰으로 사용자 정보 조회
6. 유효하지 않은 토큰으로 접근 시도
