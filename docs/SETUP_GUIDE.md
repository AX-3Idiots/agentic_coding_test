# 개발 환경 설정 가이드

## 1. Python 환경 설정

### 가상환경 생성 및 활성화
```bash
# venv 사용
python -m venv fastapi-auth-env
source fastapi-auth-env/bin/activate  # Linux/Mac
# fastapi-auth-env\Scriptsctivate  # Windows

# 또는 conda 사용
conda create -n fastapi-auth python=3.9
conda activate fastapi-auth
```

### 의존성 설치
```bash
pip install -r requirements.txt
```

## 2. 서버 실행

### 개발 서버 실행
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 프로덕션 서버 실행
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 3. API 문서 확인

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 4. 환경 변수 설정

프로덕션 환경에서는 다음 환경 변수를 설정하세요:
```bash
export SECRET_KEY="your-super-secret-key-here"
export ACCESS_TOKEN_EXPIRE_HOURS="24"
```

## 5. 데이터 파일

사용자 데이터는 `users.json` 파일에 저장됩니다. 
이 파일은 자동으로 생성되며, 개발 중에는 수동으로 삭제하여 초기화할 수 있습니다.

## 6. 로그 확인

uvicorn은 기본적으로 콘솔에 로그를 출력합니다. 
프로덕션 환경에서는 적절한 로깅 설정을 추가하는 것을 권장합니다.
