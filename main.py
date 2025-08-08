from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import bcrypt
import jwt
import json
import os
from datetime import datetime, timedelta
from typing import Optional

# FastAPI 앱 초기화
app = FastAPI(
    title="FastAPI Authentication API",
    description="이메일과 비밀번호를 이용한 간단한 인증 API",
    version="1.0.0"
)

# JWT 설정
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# 보안 스키마
security = HTTPBearer()

# 사용자 데이터 파일
USERS_FILE = "users.json"

# Pydantic 모델들
class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    email: str
    created_at: str

class Token(BaseModel):
    access_token: str
    token_type: str

# 유틸리티 함수들
def load_users():
    """JSON 파일에서 사용자 데이터 로드"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    """사용자 데이터를 JSON 파일에 저장"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def hash_password(password: str) -> str:
    """비밀번호 해시 처리"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """비밀번호 검증"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict):
    """JWT 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """JWT 토큰 검증"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return email
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# API 엔드포인트들
@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "FastAPI Authentication API", "version": "1.0.0"}

@app.post("/register", response_model=UserResponse)
async def register(user: UserRegister):
    """회원가입 엔드포인트"""
    users = load_users()
    
    # 이메일 중복 확인
    if user.email in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 비밀번호 해시 처리
    hashed_password = hash_password(user.password)
    
    # 사용자 정보 저장
    users[user.email] = {
        "email": user.email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow().isoformat()
    }
    save_users(users)
    
    return UserResponse(
        email=user.email,
        created_at=users[user.email]["created_at"]
    )

@app.post("/login", response_model=Token)
async def login(user: UserLogin):
    """로그인 엔드포인트"""
    users = load_users()
    
    # 사용자 존재 확인
    if user.email not in users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # 비밀번호 검증
    if not verify_password(user.password, users[user.email]["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # JWT 토큰 생성
    access_token = create_access_token(data={"sub": user.email})
    
    return Token(access_token=access_token, token_type="bearer")

@app.get("/me", response_model=UserResponse)
async def get_current_user(current_user_email: str = Depends(verify_token)):
    """현재 사용자 정보 조회 (보호된 엔드포인트)"""
    users = load_users()
    
    if current_user_email not in users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_data = users[current_user_email]
    return UserResponse(
        email=user_data["email"],
        created_at=user_data["created_at"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
