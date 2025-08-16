# Simple Memo App

간단한 메모 관리 애플리케이션입니다.

## 기능

- 메모 생성 (최대 140자)
- 메모 목록 조회 (최신순 정렬)
- 메모 삭제

## 실행 방법

1. 의존성 설치:
```bash
uv sync
```

2. 서버 실행:
```bash
uvicorn app.main:app --reload
```

3. API 문서 확인:
서버 실행 후 브라우저에서 `http://localhost:8000/docs`에 접속하여 FastAPI의 자동 생성 API 문서를 확인할 수 있습니다.

## API 엔드포인트

- `POST /api/memos` - 새 메모 생성
- `GET /api/memos` - 모든 메모 조회
- `DELETE /api/memos/{id}` - 메모 삭제
