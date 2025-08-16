# CLAUDE.md - Simple Memo App Backend Development Guide

## 프로젝트 개요

이 프로젝트는 간단한 메모 관리 기능을 제공하는 FastAPI 백엔드 애플리케이션입니다. 사용자는 최대 140자의 메모를 생성, 조회, 삭제할 수 있습니다.

## 아키텍처 설계 및 컴포넌트 설명

### 1. 프로젝트 구조

```
app/
├── main.py                     # FastAPI 애플리케이션 진입점
├── api/                        # API 라우터 계층
│   └── v1/                     # API 버전 관리
│       ├── routes/             # 엔드포인트 정의
│       │   └── memos.py        # 메모 관련 라우터
│       └── dependencies.py     # 공통 의존성 (향후 확장용)
├── core/                       # 핵심 설정 및 유틸리티
│   ├── config.py               # 애플리케이션 설정
│   └── exceptions.py           # 커스텀 예외 및 핸들러
├── schemas/                    # Pydantic 모델 (요청/응답)
│   └── memo.py                 # 메모 스키마 정의
├── services/                   # 비즈니스 로직 계층
│   └── memo_service.py         # 메모 서비스 로직
└── tests/                      # 테스트 파일 (향후 확장용)
```

### 2. 생성된 핵심 컴포넌트와 설계 이유

#### 2.1 계층화된 아키텍처 (Layered Architecture)

**Why (왜):**
- 관심사의 분리(Separation of Concerns)를 통해 코드의 유지보수성과 테스트 가능성을 향상
- 각 계층이 명확한 책임을 가져 코드 변경 시 영향 범위를 최소화
- 향후 데이터베이스 연동, 인증, 캐싱 등의 기능 추가 시 확장성 확보

**What (무엇):**
- **API Layer** (`app/api/`): HTTP 요청/응답 처리, 라우팅, 입력 검증
- **Service Layer** (`app/services/`): 비즈니스 로직, 데이터 처리 규칙
- **Schema Layer** (`app/schemas/`): 데이터 검증 및 직렬화/역직렬화
- **Core Layer** (`app/core/`): 설정, 예외 처리, 공통 유틸리티

#### 2.2 중앙화된 예외 처리 시스템 (`app/core/exceptions.py`)

**Why (왜):**
- 일관된 에러 응답 형식으로 클라이언트 개발자의 예측 가능성 향상
- 비즈니스 로직에서 HTTP 상태 코드에 대한 의존성 제거
- 로깅, 모니터링 등의 횡단 관심사를 중앙에서 처리 가능

**What (무엇):**
- `MemoNotFoundError`: 메모를 찾을 수 없을 때 발생하는 도메인 예외
- `ValidationError`: 입력 검증 실패 시 발생하는 예외
- `setup_exception_handlers()`: FastAPI 전역 예외 핸들러 등록 함수

#### 2.3 Pydantic 기반 데이터 검증 (`app/schemas/memo.py`)

**Why (왜):**
- 런타임 타입 검증으로 데이터 무결성 보장
- API 문서 자동 생성으로 개발 생산성 향상
- 명확한 입력/출력 스키마로 클라이언트-서버 간 계약 정의

**What (무엇):**
- `MemoCreate`: 메모 생성 요청 스키마 (140자 제한, 빈 문자열 검증)
- `MemoResponse`: 메모 응답 스키마 (id, content, created_at 포함)
- `MemoListResponse`: 메모 목록 응답 스키마 (향후 페이징 등 확장 가능)

#### 2.4 서비스 계층 패턴 (`app/services/memo_service.py`)

**Why (왜):**
- 비즈니스 로직을 HTTP 계층에서 분리하여 재사용성 향상
- 단위 테스트 작성이 용이한 순수 함수 형태로 로직 구현
- 향후 데이터베이스 연동 시 인터페이스 변경 없이 구현체만 교체 가능

**What (무엇):**
- `MemoService`: 메모 CRUD 작업을 담당하는 서비스 클래스
- 인메모리 저장소를 사용하여 데이터베이스 없이도 동작 가능
- 전역 싱글톤 인스턴스로 상태 관리 (개발 단계에서 간단한 구현)

#### 2.5 API 버전 관리 (`app/api/v1/`)

**Why (왜):**
- API 하위 호환성 유지하면서 새로운 기능 추가 가능
- 클라이언트가 점진적으로 새 버전으로 마이그레이션 할 수 있는 유연성 제공
- 장기적인 API 진화 전략 수립 가능

**What (무엇):**
- `/api/v1/` 경로 구조로 버전 명시
- 향후 v2, v3 등 새 버전 추가 시 기존 v1 유지 가능
- 각 버전별로 독립적인 라우터와 의존성 관리

### 3. 확장 가능성

#### 3.1 데이터베이스 연동
- `app/models/` 디렉토리에 SQLAlchemy 모델 추가
- `app/services/memo_service.py`에서 데이터베이스 세션 의존성 주입
- `app/core/database.py`에 데이터베이스 연결 설정 추가

#### 3.2 인증/인가
- `app/core/security.py`에 JWT 토큰 처리 로직 추가
- `app/api/v1/dependencies.py`에 인증 의존성 함수 구현
- 사용자별 메모 격리를 위한 User 모델 및 관계 설정

#### 3.3 테스트 커버리지
- `tests/` 디렉토리에 단위 테스트 및 통합 테스트 추가
- pytest fixtures를 활용한 테스트 데이터 관리
- API 엔드포인트별 테스트 케이스 작성

## 개발 가이드라인

### 1. 코드 스타일
- Ruff를 사용한 코드 포맷팅 및 린팅
- 타입 힌트 필수 사용
- Docstring을 통한 API 문서화

### 2. 에러 처리
- 비즈니스 로직에서는 도메인 예외 발생
- HTTP 계층에서 적절한 상태 코드로 변환
- 사용자 친화적인 에러 메시지 제공

### 3. 성능 고려사항
- 비동기 처리를 위한 async/await 패턴 사용
- 향후 데이터베이스 쿼리 최적화 고려
- 메모리 사용량 모니터링 (현재 인메모리 저장소 사용)

이 아키텍처는 간단한 메모 애플리케이션으로 시작하여 점진적으로 복잡한 기능을 추가할 수 있도록 설계되었습니다.
