# Test cases for authentication API
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    """루트 엔드포인트 테스트"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "FastAPI Authentication Server is running!"}

def test_register_user():
    """회원가입 테스트"""
    response = client.post(
        "/register",
        json={"email": "test@example.com", "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "created_at" in data

def test_register_duplicate_email():
    """중복 이메일 회원가입 테스트"""
    # 첫 번째 회원가입
    client.post(
        "/register",
        json={"email": "duplicate@example.com", "password": "password123"}
    )
    
    # 중복 이메일로 두 번째 회원가입 시도
    response = client.post(
        "/register",
        json={"email": "duplicate@example.com", "password": "password456"}
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login_success():
    """로그인 성공 테스트"""
    # 먼저 회원가입
    client.post(
        "/register",
        json={"email": "login@example.com", "password": "loginpassword"}
    )
    
    # 로그인 시도
    response = client.post(
        "/login",
        json={"email": "login@example.com", "password": "loginpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    """잘못된 로그인 정보 테스트"""
    response = client.post(
        "/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]
