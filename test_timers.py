import pytest
import json
import os
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from main import app, TIMERS_FILE, active_timers, scheduler, TimerStatus
import tempfile
import shutil

# Test client
client = TestClient(app)

# Test user credentials
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123"
}

@pytest.fixture(scope="function")
def auth_headers():
    """인증된 사용자의 헤더를 반환하는 fixture"""
    # 테스트 사용자 등록
    response = client.post("/register", json=TEST_USER)
    assert response.status_code in [200, 400]  # 이미 존재할 수 있음
    
    # 로그인하여 토큰 획득
    response = client.post("/login", json=TEST_USER)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def cleanup_timers():
    """테스트 후 타이머 데이터 정리"""
    yield
    # 테스트 후 정리
    active_timers.clear()
    if os.path.exists(TIMERS_FILE):
        os.remove(TIMERS_FILE)

class TestTimerCRUD:
    """타이머 CRUD 테스트"""
    
    def test_create_timer(self, auth_headers, cleanup_timers):
        """타이머 생성 테스트"""
        timer_data = {
            "label": "Test Timer",
            "duration_seconds": 300,
            "alert_sound": "chime",
            "volume": 0.8
        }
        
        response = client.post("/timers", json=timer_data, headers=auth_headers)
        assert response.status_code == 200
        
        result = response.json()
        assert result["label"] == timer_data["label"]
        assert result["duration_seconds"] == timer_data["duration_seconds"]
        assert result["remaining_seconds"] == timer_data["duration_seconds"]
        assert result["status"] == TimerStatus.CREATED
        assert result["alert_sound"] == timer_data["alert_sound"]
        assert result["volume"] == timer_data["volume"]
        assert "id" in result
        assert "created_at" in result
        assert result["user_email"] == TEST_USER["email"]
    
    def test_create_timer_invalid_data(self, auth_headers, cleanup_timers):
        """잘못된 데이터로 타이머 생성 테스트"""
        # 너무 긴 라벨
        timer_data = {
            "label": "A" * 101,  # 100자 초과
            "duration_seconds": 300
        }
        response = client.post("/timers", json=timer_data, headers=auth_headers)
        assert response.status_code == 422
        
        # 잘못된 duration
        timer_data = {
            "label": "Test",
            "duration_seconds": 0  # 0 이하
        }
        response = client.post("/timers", json=timer_data, headers=auth_headers)
        assert response.status_code == 422
        
        # 잘못된 볼륨
        timer_data = {
            "label": "Test",
            "duration_seconds": 300,
            "volume": 1.5  # 1.0 초과
        }
        response = client.post("/timers", json=timer_data, headers=auth_headers)
        assert response.status_code == 422
    
    def test_list_timers(self, auth_headers, cleanup_timers):
        """타이머 목록 조회 테스트"""
        # 타이머 2개 생성
        timer1 = {"label": "Timer 1", "duration_seconds": 60}
        timer2 = {"label": "Timer 2", "duration_seconds": 120}
        
        client.post("/timers", json=timer1, headers=auth_headers)
        client.post("/timers", json=timer2, headers=auth_headers)
        
        # 목록 조회
        response = client.get("/timers", headers=auth_headers)
        assert response.status_code == 200
        
        timers = response.json()
        assert len(timers) == 2
        assert timers[0]["label"] in ["Timer 1", "Timer 2"]
        assert timers[1]["label"] in ["Timer 1", "Timer 2"]
    
    def test_get_timer(self, auth_headers, cleanup_timers):
        """특정 타이머 조회 테스트"""
        timer_data = {"label": "Test Timer", "duration_seconds": 300}
        
        # 타이머 생성
        response = client.post("/timers", json=timer_data, headers=auth_headers)
        timer_id = response.json()["id"]
        
        # 타이머 조회
        response = client.get(f"/timers/{timer_id}", headers=auth_headers)
        assert response.status_code == 200
        
        result = response.json()
        assert result["id"] == timer_id
        assert result["label"] == timer_data["label"]
    
    def test_update_timer(self, auth_headers, cleanup_timers):
        """타이머 업데이트 테스트"""
        timer_data = {"label": "Test Timer", "duration_seconds": 300}
        
        # 타이머 생성
        response = client.post("/timers", json=timer_data, headers=auth_headers)
        timer_id = response.json()["id"]
        
        # 타이머 업데이트
        update_data = {"label": "Updated Timer", "volume": 0.5}
        response = client.put(f"/timers/{timer_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        result = response.json()
        assert result["label"] == "Updated Timer"
        assert result["volume"] == 0.5
    
    def test_delete_timer(self, auth_headers, cleanup_timers):
        """타이머 삭제 테스트"""
        timer_data = {"label": "Test Timer", "duration_seconds": 300}
        
        # 타이머 생성
        response = client.post("/timers", json=timer_data, headers=auth_headers)
        timer_id = response.json()["id"]
        
        # 타이머 삭제
        response = client.delete(f"/timers/{timer_id}", headers=auth_headers)
        assert response.status_code == 200
        
        # 삭제 확인
        response = client.get(f"/timers/{timer_id}", headers=auth_headers)
        assert response.status_code == 404

class TestTimerOperations:
    """타이머 작동 테스트"""
    
    def test_start_timer(self, auth_headers, cleanup_timers):
        """타이머 시작 테스트"""
        timer_data = {"label": "Test Timer", "duration_seconds": 300}
        
        # 타이머 생성
        response = client.post("/timers", json=timer_data, headers=auth_headers)
        timer_id = response.json()["id"]
        
        # 타이머 시작
        response = client.post(f"/timers/{timer_id}/start", headers=auth_headers)
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == TimerStatus.RUNNING
        assert "started_at" in result
        assert result["started_at"] is not None
    
    def test_pause_timer(self, auth_headers, cleanup_timers):
        """타이머 일시정지 테스트"""
        timer_data = {"label": "Test Timer", "duration_seconds": 300}
        
        # 타이머 생성 및 시작
        response = client.post("/timers", json=timer_data, headers=auth_headers)
        timer_id = response.json()["id"]
        
        client.post(f"/timers/{timer_id}/start", headers=auth_headers)
        
        # 타이머 일시정지
        response = client.post(f"/timers/{timer_id}/pause", headers=auth_headers)
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == TimerStatus.PAUSED
        assert "paused_at" in result
        assert result["paused_at"] is not None
    
    def test_stop_timer(self, auth_headers, cleanup_timers):
        """타이머 중지 테스트"""
        timer_data = {"label": "Test Timer", "duration_seconds": 300}
        
        # 타이머 생성 및 시작
        response = client.post("/timers", json=timer_data, headers=auth_headers)
        timer_id = response.json()["id"]
        
        client.post(f"/timers/{timer_id}/start", headers=auth_headers)
        
        # 타이머 중지
        response = client.post(f"/timers/{timer_id}/stop", headers=auth_headers)
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == TimerStatus.CANCELLED
        assert "completed_at" in result
    
    def test_timer_state_transitions(self, auth_headers, cleanup_timers):
        """타이머 상태 전환 테스트"""
        timer_data = {"label": "Test Timer", "duration_seconds": 60}
        
        # 타이머 생성
        response = client.post("/timers", json=timer_data, headers=auth_headers)
        timer_id = response.json()["id"]
        
        # CREATED -> RUNNING
        response = client.post(f"/timers/{timer_id}/start", headers=auth_headers)
        assert response.json()["status"] == TimerStatus.RUNNING
        
        # RUNNING -> PAUSED
        response = client.post(f"/timers/{timer_id}/pause", headers=auth_headers)
        assert response.json()["status"] == TimerStatus.PAUSED
        
        # PAUSED -> RUNNING
        response = client.post(f"/timers/{timer_id}/start", headers=auth_headers)
        assert response.json()["status"] == TimerStatus.RUNNING
        
        # RUNNING -> CANCELLED
        response = client.post(f"/timers/{timer_id}/stop", headers=auth_headers)
        assert response.json()["status"] == TimerStatus.CANCELLED

class TestSoundManagement:
    """사운드 관리 테스트"""
    
    def test_list_available_sounds(self, auth_headers):
        """사용 가능한 사운드 목록 테스트"""
        response = client.get("/sounds/available", headers=auth_headers)
        assert response.status_code == 200
        
        result = response.json()
        assert "default" in result
        assert "custom" in result
        assert isinstance(result["default"], list)
        assert isinstance(result["custom"], list)
        
        # 기본 사운드들이 포함되어 있는지 확인
        expected_sounds = ["chime", "bell", "beep", "nature", "digital"]
        for sound in expected_sounds:
            assert sound in result["default"]

class TestSystemStatus:
    """시스템 상태 테스트"""
    
    def test_get_system_status(self, auth_headers):
        """시스템 상태 조회 테스트"""
        response = client.get("/system/status", headers=auth_headers)
        assert response.status_code == 200
        
        result = response.json()
        assert "active_timers" in result
        assert "background_processing" in result
        assert "cpu_usage_percent" in result
        assert "wake_lock_active" in result
        assert "notification_permission" in result
        
        assert isinstance(result["active_timers"], int)
        assert isinstance(result["background_processing"], bool)
        assert isinstance(result["cpu_usage_percent"], (int, float))
        assert isinstance(result["wake_lock_active"], bool)
        assert isinstance(result["notification_permission"], bool)
    
    def test_notification_settings(self, auth_headers):
        """알림 설정 테스트"""
        # 기본 설정 조회
        response = client.get("/system/notifications/settings", headers=auth_headers)
        assert response.status_code == 200
        
        default_settings = response.json()
        assert "enabled" in default_settings
        assert "power_saving_mode" in default_settings
        
        # 설정 업데이트
        new_settings = {
            "enabled": False,
            "power_saving_mode": "aggressive"
        }
        response = client.post("/system/notifications/settings", json=new_settings, headers=auth_headers)
        assert response.status_code == 200
        
        # 업데이트된 설정 확인
        response = client.get("/system/notifications/settings", headers=auth_headers)
        result = response.json()
        assert result["enabled"] == False
        assert result["power_saving_mode"] == "aggressive"
    
    def test_test_notification(self, auth_headers):
        """테스트 알림 발송 테스트"""
        response = client.post("/system/test-notification", headers=auth_headers)
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "notification sent" in result["message"].lower()
    
    def test_test_sound(self, auth_headers):
        """테스트 사운드 재생 테스트"""
        response = client.post("/system/test-sound?sound=chime&volume=0.5", headers=auth_headers)
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "chime" in result["message"]

class TestAuthentication:
    """인증 테스트"""
    
    def test_unauthorized_access(self):
        """인증되지 않은 접근 테스트"""
        # 토큰 없이 타이머 생성 시도
        timer_data = {"label": "Test Timer", "duration_seconds": 300}
        response = client.post("/timers", json=timer_data)
        assert response.status_code == 403
        
        # 타이머 목록 조회 시도
        response = client.get("/timers")
        assert response.status_code == 403
    
    def test_invalid_token(self):
        """잘못된 토큰 테스트"""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.get("/timers", headers=headers)
        assert response.status_code == 401

if __name__ == "__main__":
    pytest.main([__file__, "-v"])