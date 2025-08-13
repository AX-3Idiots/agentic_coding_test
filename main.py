from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
import bcrypt
import jwt
import json
import os
import asyncio
import uuid
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import aiofiles

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
TIMERS_FILE = "timers.json"
SOUNDS_DIR = "sounds"
CUSTOM_SOUNDS_DIR = "custom_sounds"

# 전역 타이머 관리
active_timers: Dict[str, Dict[str, Any]] = {}
scheduler = BackgroundScheduler()
notification_settings: Dict[str, NotificationSettings] = {}
wake_lock_active = False
cpu_usage_thread = None

# 기본 소리 파일 경로
DEFAULT_SOUNDS = {
    AlertSound.CHIME: "chime.wav",
    AlertSound.BELL: "bell.wav", 
    AlertSound.BEEP: "beep.wav",
    AlertSound.NATURE: "nature.wav",
    AlertSound.DIGITAL: "digital.wav"
}

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

# Timer-related enums and models
class TimerStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class AlertSound(str, Enum):
    CHIME = "chime"
    BELL = "bell"
    BEEP = "beep"
    NATURE = "nature"
    DIGITAL = "digital"
    CUSTOM = "custom"

class PowerSavingMode(str, Enum):
    NORMAL = "normal"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"

class TimerCreate(BaseModel):
    label: str = Field(..., min_length=1, max_length=100)
    duration_seconds: int = Field(..., gt=0, le=86400)  # Max 24 hours
    alert_sound: AlertSound = AlertSound.CHIME
    custom_sound_path: Optional[str] = None
    volume: float = Field(1.0, ge=0.0, le=1.0)

class TimerUpdate(BaseModel):
    label: Optional[str] = Field(None, min_length=1, max_length=100)
    alert_sound: Optional[AlertSound] = None
    custom_sound_path: Optional[str] = None
    volume: Optional[float] = Field(None, ge=0.0, le=1.0)

class TimerResponse(BaseModel):
    id: str
    label: str
    duration_seconds: int
    remaining_seconds: int
    status: TimerStatus
    alert_sound: AlertSound
    custom_sound_path: Optional[str]
    volume: float
    created_at: datetime
    started_at: Optional[datetime]
    paused_at: Optional[datetime]
    completed_at: Optional[datetime]
    user_email: str

class NotificationSettings(BaseModel):
    enabled: bool = True
    power_saving_mode: PowerSavingMode = PowerSavingMode.NORMAL

class SystemStatus(BaseModel):
    active_timers: int
    background_processing: bool
    cpu_usage_percent: float
    wake_lock_active: bool
    notification_permission: bool

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

# Timer utility functions
def load_timers():
    """JSON 파일에서 타이머 데이터 로드"""
    if os.path.exists(TIMERS_FILE):
        with open(TIMERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_timers(timers):
    """타이머 데이터를 JSON 파일에 저장"""
    with open(TIMERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(timers, f, ensure_ascii=False, indent=2, default=str)

def calculate_remaining_time(timer_data: Dict[str, Any]) -> int:
    """타이머의 남은 시간 계산"""
    if timer_data["status"] not in [TimerStatus.RUNNING, TimerStatus.PAUSED]:
        return timer_data.get("remaining_seconds", timer_data["duration_seconds"])
    
    if timer_data["status"] == TimerStatus.PAUSED:
        return timer_data.get("remaining_seconds", timer_data["duration_seconds"])
    
    # RUNNING 상태일 때
    started_at = datetime.fromisoformat(timer_data["started_at"])
    elapsed = (datetime.utcnow() - started_at).total_seconds()
    remaining = max(0, timer_data["duration_seconds"] - elapsed)
    return int(remaining)

def manage_wake_lock():
    """활성 타이머가 있을 때 wake lock 관리"""
    global wake_lock_active
    has_active_timers = any(
        timer["status"] == TimerStatus.RUNNING 
        for timer in active_timers.values()
    )
    
    if has_active_timers and not wake_lock_active:
        wake_lock_active = True
        # 실제 wake lock 구현은 플랫폼에 따라 다름
        print("Wake lock activated")
    elif not has_active_timers and wake_lock_active:
        wake_lock_active = False
        print("Wake lock released")

def send_notification(title: str, message: str, timer_id: str):
    """플랫폼별 알림 발송"""
    try:
        # plyer를 사용한 크로스 플랫폼 알림
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            timeout=10
        )
        print(f"Notification sent for timer {timer_id}: {title} - {message}")
    except Exception as e:
        print(f"Failed to send notification: {e}")

def play_alert_sound(sound_type: AlertSound, custom_path: Optional[str] = None, volume: float = 1.0):
    """알림 소리 재생"""
    try:
        if sound_type == AlertSound.CUSTOM and custom_path:
            sound_path = os.path.join(CUSTOM_SOUNDS_DIR, custom_path)
        else:
            sound_path = os.path.join(SOUNDS_DIR, DEFAULT_SOUNDS[sound_type])
        
        if os.path.exists(sound_path):
            # 백그라운드에서 소리 재생
            threading.Thread(target=_play_sound_file, args=(sound_path, volume)).start()
            print(f"Playing alert sound: {sound_path}")
        else:
            print(f"Sound file not found: {sound_path}")
    except Exception as e:
        print(f"Failed to play alert sound: {e}")

def _play_sound_file(file_path: str, volume: float):
    """실제 소리 파일 재생 (백그라운드)"""
    try:
        from pydub import AudioSegment
        from pydub.playback import play
        
        audio = AudioSegment.from_file(file_path)
        if volume != 1.0:
            audio = audio + (20 * (volume - 1))  # dB 조정
        play(audio)
    except Exception as e:
        print(f"Error playing sound file {file_path}: {e}")

def timer_completion_callback(timer_id: str):
    """타이머 완료 시 콜백 함수"""
    if timer_id not in active_timers:
        return
    
    timer_data = active_timers[timer_id]
    timer_data["status"] = TimerStatus.COMPLETED
    timer_data["completed_at"] = datetime.utcnow().isoformat()
    timer_data["remaining_seconds"] = 0
    
    # 알림 발송
    send_notification(
        title="Timer Completed!",
        message=f"'{timer_data['label']}' has finished",
        timer_id=timer_id
    )
    
    # 알림 소리 재생
    play_alert_sound(
        AlertSound(timer_data["alert_sound"]),
        timer_data.get("custom_sound_path"),
        timer_data["volume"]
    )
    
    # 영구 저장소 업데이트
    timers = load_timers()
    if timer_id in timers:
        timers[timer_id] = timer_data
        save_timers(timers)
    
    # wake lock 관리
    manage_wake_lock()
    
    print(f"Timer {timer_id} completed: {timer_data['label']}")

def get_cpu_usage() -> float:
    """현재 CPU 사용률 반환 (백그라운드 처리용)"""
    try:
        import psutil
        return psutil.cpu_percent(interval=1)
    except:
        return 0.0

def monitor_system_resources():
    """시스템 리소스 모니터링 (백그라운드 스레드)"""
    while True:
        try:
            cpu_usage = get_cpu_usage()
            if cpu_usage > 5.0:  # 5% 이상일 때 로그
                print(f"High CPU usage: {cpu_usage}%")
            time.sleep(30)  # 30초마다 체크
        except Exception as e:
            print(f"Resource monitoring error: {e}")
            time.sleep(30)

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

# Timer API endpoints
@app.post("/timers", response_model=TimerResponse)
async def create_timer(timer_data: TimerCreate, current_user_email: str = Depends(verify_token)):
    """새 타이머 생성"""
    timer_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    timer = {
        "id": timer_id,
        "label": timer_data.label,
        "duration_seconds": timer_data.duration_seconds,
        "remaining_seconds": timer_data.duration_seconds,
        "status": TimerStatus.CREATED,
        "alert_sound": timer_data.alert_sound,
        "custom_sound_path": timer_data.custom_sound_path,
        "volume": timer_data.volume,
        "created_at": now.isoformat(),
        "started_at": None,
        "paused_at": None,
        "completed_at": None,
        "user_email": current_user_email
    }
    
    # 메모리에 저장
    active_timers[timer_id] = timer
    
    # 영구 저장소에 저장
    timers = load_timers()
    timers[timer_id] = timer
    save_timers(timers)
    
    return TimerResponse(**timer)

@app.get("/timers", response_model=List[TimerResponse])
async def list_timers(current_user_email: str = Depends(verify_token)):
    """사용자의 모든 타이머 조회"""
    timers = load_timers()
    user_timers = []
    
    for timer_id, timer_data in timers.items():
        if timer_data["user_email"] == current_user_email:
            # 실시간으로 남은 시간 계산
            if timer_id in active_timers:
                remaining = calculate_remaining_time(active_timers[timer_id])
                timer_data["remaining_seconds"] = remaining
            
            user_timers.append(TimerResponse(**timer_data))
    
    return user_timers

@app.get("/timers/{timer_id}", response_model=TimerResponse)
async def get_timer(timer_id: str, current_user_email: str = Depends(verify_token)):
    """특정 타이머 조회"""
    if timer_id in active_timers:
        timer_data = active_timers[timer_id]
        if timer_data["user_email"] != current_user_email:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timer not found")
        
        # 실시간으로 남은 시간 계산
        remaining = calculate_remaining_time(timer_data)
        timer_data["remaining_seconds"] = remaining
        
        return TimerResponse(**timer_data)
    
    # 영구 저장소에서 조회
    timers = load_timers()
    if timer_id not in timers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timer not found")
    
    timer_data = timers[timer_id]
    if timer_data["user_email"] != current_user_email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timer not found")
    
    return TimerResponse(**timer_data)

@app.put("/timers/{timer_id}", response_model=TimerResponse)
async def update_timer(timer_id: str, update_data: TimerUpdate, current_user_email: str = Depends(verify_token)):
    """타이머 정보 업데이트"""
    if timer_id not in active_timers:
        timers = load_timers()
        if timer_id not in timers:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timer not found")
        active_timers[timer_id] = timers[timer_id]
    
    timer_data = active_timers[timer_id]
    if timer_data["user_email"] != current_user_email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timer not found")
    
    # RUNNING 상태의 타이머는 일부 속성만 수정 가능
    if timer_data["status"] == TimerStatus.RUNNING:
        allowed_updates = {"alert_sound", "custom_sound_path", "volume"}
        for field, value in update_data.dict(exclude_unset=True).items():
            if field in allowed_updates:
                timer_data[field] = value
    else:
        # 다른 상태에서는 모든 속성 수정 가능
        for field, value in update_data.dict(exclude_unset=True).items():
            timer_data[field] = value
    
    # 영구 저장소 업데이트
    timers = load_timers()
    timers[timer_id] = timer_data
    save_timers(timers)
    
    return TimerResponse(**timer_data)

@app.post("/timers/{timer_id}/start", response_model=TimerResponse)
async def start_timer(timer_id: str, current_user_email: str = Depends(verify_token)):
    """타이머 시작"""
    if timer_id not in active_timers:
        timers = load_timers()
        if timer_id not in timers:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timer not found")
        active_timers[timer_id] = timers[timer_id]
    
    timer_data = active_timers[timer_id]
    if timer_data["user_email"] != current_user_email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timer not found")
    
    if timer_data["status"] in [TimerStatus.COMPLETED, TimerStatus.CANCELLED]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot start completed or cancelled timer")
    
    now = datetime.utcnow()
    timer_data["status"] = TimerStatus.RUNNING
    timer_data["started_at"] = now.isoformat()
    timer_data["paused_at"] = None
    
    # 백그라운드 스케줄러에 완료 작업 등록
    completion_time = now + timedelta(seconds=timer_data["remaining_seconds"])
    scheduler.add_job(
        func=timer_completion_callback,
        trigger=DateTrigger(run_date=completion_time),
        args=[timer_id],
        id=f"timer_completion_{timer_id}",
        replace_existing=True
    )
    
    # Wake lock 관리
    manage_wake_lock()
    
    # 영구 저장소 업데이트
    timers = load_timers()
    timers[timer_id] = timer_data
    save_timers(timers)
    
    return TimerResponse(**timer_data)

@app.post("/timers/{timer_id}/pause", response_model=TimerResponse)
async def pause_timer(timer_id: str, current_user_email: str = Depends(verify_token)):
    """타이머 일시정지"""
    if timer_id not in active_timers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timer not found")
    
    timer_data = active_timers[timer_id]
    if timer_data["user_email"] != current_user_email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timer not found")
    
    if timer_data["status"] != TimerStatus.RUNNING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Timer is not running")
    
    # 남은 시간 계산 및 저장
    remaining = calculate_remaining_time(timer_data)
    timer_data["remaining_seconds"] = remaining
    timer_data["status"] = TimerStatus.PAUSED
    timer_data["paused_at"] = datetime.utcnow().isoformat()
    
    # 스케줄된 완료 작업 제거
    try:
        scheduler.remove_job(f"timer_completion_{timer_id}")
    except:
        pass
    
    # Wake lock 관리
    manage_wake_lock()
    
    # 영구 저장소 업데이트
    timers = load_timers()
    timers[timer_id] = timer_data
    save_timers(timers)
    
    return TimerResponse(**timer_data)

@app.post("/timers/{timer_id}/stop", response_model=TimerResponse)
async def stop_timer(timer_id: str, current_user_email: str = Depends(verify_token)):
    """타이머 중지"""
    if timer_id not in active_timers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timer not found")
    
    timer_data = active_timers[timer_id]
    if timer_data["user_email"] != current_user_email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timer not found")
    
    if timer_data["status"] in [TimerStatus.COMPLETED, TimerStatus.CANCELLED]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Timer already stopped")
    
    timer_data["status"] = TimerStatus.CANCELLED
    timer_data["completed_at"] = datetime.utcnow().isoformat()
    
    # 스케줄된 완료 작업 제거
    try:
        scheduler.remove_job(f"timer_completion_{timer_id}")
    except:
        pass
    
    # Wake lock 관리
    manage_wake_lock()
    
    # 영구 저장소 업데이트
    timers = load_timers()
    timers[timer_id] = timer_data
    save_timers(timers)
    
    return TimerResponse(**timer_data)

@app.delete("/timers/{timer_id}")
async def delete_timer(timer_id: str, current_user_email: str = Depends(verify_token)):
    """타이머 삭제"""
    timers = load_timers()
    if timer_id not in timers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timer not found")
    
    timer_data = timers[timer_id]
    if timer_data["user_email"] != current_user_email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timer not found")
    
    # 활성 타이머인 경우 스케줄된 작업 제거
    if timer_id in active_timers:
        try:
            scheduler.remove_job(f"timer_completion_{timer_id}")
        except:
            pass
        del active_timers[timer_id]
    
    # 영구 저장소에서 삭제
    del timers[timer_id]
    save_timers(timers)
    
    # Wake lock 관리
    manage_wake_lock()
    
    return {"message": "Timer deleted successfully"}

# Sound management endpoints
@app.post("/sounds/upload")
async def upload_sound(file: UploadFile = File(...), current_user_email: str = Depends(verify_token)):
    """커스텀 사운드 파일 업로드"""
    # 파일 형식 검증
    allowed_formats = {".mp3", ".wav", ".ogg"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Allowed: {', '.join(allowed_formats)}"
        )
    
    # 파일 크기 검증 (5MB 제한)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit"
        )
    
    # 안전한 파일명 생성
    safe_filename = f"{current_user_email}_{int(time.time())}_{file.filename}"
    file_path = os.path.join(CUSTOM_SOUNDS_DIR, safe_filename)
    
    # 디렉토리 생성
    os.makedirs(CUSTOM_SOUNDS_DIR, exist_ok=True)
    
    # 파일 저장
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    return {"message": "Sound uploaded successfully", "filename": safe_filename}

@app.get("/sounds/available")
async def list_available_sounds(current_user_email: str = Depends(verify_token)):
    """사용 가능한 사운드 목록 조회"""
    sounds = {
        "default": [sound.value for sound in AlertSound if sound != AlertSound.CUSTOM],
        "custom": []
    }
    
    # 커스텀 사운드 파일 목록
    if os.path.exists(CUSTOM_SOUNDS_DIR):
        for filename in os.listdir(CUSTOM_SOUNDS_DIR):
            if filename.startswith(f"{current_user_email}_"):
                sounds["custom"].append(filename)
    
    return sounds

# System status and settings endpoints
@app.get("/system/status", response_model=SystemStatus)
async def get_system_status(current_user_email: str = Depends(verify_token)):
    """시스템 상태 조회"""
    active_count = len([t for t in active_timers.values() if t["status"] == TimerStatus.RUNNING])
    cpu_usage = get_cpu_usage()
    
    return SystemStatus(
        active_timers=active_count,
        background_processing=scheduler.running,
        cpu_usage_percent=cpu_usage,
        wake_lock_active=wake_lock_active,
        notification_permission=True  # 실제 구현에서는 시스템 확인 필요
    )

@app.post("/system/notifications/settings")
async def update_notification_settings(settings: NotificationSettings, current_user_email: str = Depends(verify_token)):
    """알림 설정 업데이트"""
    notification_settings[current_user_email] = settings
    return {"message": "Notification settings updated", "settings": settings}

@app.get("/system/notifications/settings", response_model=NotificationSettings)
async def get_notification_settings(current_user_email: str = Depends(verify_token)):
    """알림 설정 조회"""
    return notification_settings.get(current_user_email, NotificationSettings())

@app.post("/system/test-notification")
async def test_notification(current_user_email: str = Depends(verify_token)):
    """테스트 알림 발송"""
    send_notification(
        title="Test Notification",
        message="This is a test notification from your timer app",
        timer_id="test"
    )
    return {"message": "Test notification sent"}

@app.post("/system/test-sound")
async def test_sound(sound: AlertSound = AlertSound.CHIME, volume: float = 1.0, current_user_email: str = Depends(verify_token)):
    """테스트 사운드 재생"""
    play_alert_sound(sound, None, volume)
    return {"message": f"Test sound played: {sound.value}"}

# Application lifecycle management
@app.on_event("startup")
async def startup_event():
    """앱 시작 시 초기화"""
    # 스케줄러 시작
    if not scheduler.running:
        scheduler.start()
        print("Background scheduler started")
    
    # 기존 타이머 복원
    timers = load_timers()
    current_time = datetime.utcnow()
    
    for timer_id, timer_data in timers.items():
        if timer_data["status"] == TimerStatus.RUNNING:
            # 실행 중이던 타이머의 남은 시간 확인
            started_at = datetime.fromisoformat(timer_data["started_at"])
            elapsed = (current_time - started_at).total_seconds()
            remaining = max(0, timer_data["duration_seconds"] - elapsed)
            
            if remaining > 0:
                # 타이머가 아직 완료되지 않음
                timer_data["remaining_seconds"] = int(remaining)
                active_timers[timer_id] = timer_data
                
                # 완료 작업 다시 스케줄링
                completion_time = current_time + timedelta(seconds=remaining)
                scheduler.add_job(
                    func=timer_completion_callback,
                    trigger=DateTrigger(run_date=completion_time),
                    args=[timer_id],
                    id=f"timer_completion_{timer_id}",
                    replace_existing=True
                )
                print(f"Restored running timer: {timer_id} ({remaining:.1f}s remaining)")
            else:
                # 타이머가 이미 완료되었어야 함
                timer_data["status"] = TimerStatus.COMPLETED
                timer_data["completed_at"] = current_time.isoformat()
                timer_data["remaining_seconds"] = 0
                print(f"Completed overdue timer: {timer_id}")
    
    # 업데이트된 타이머 데이터 저장
    save_timers(timers)
    
    # 리소스 모니터링 스레드 시작
    global cpu_usage_thread
    if cpu_usage_thread is None or not cpu_usage_thread.is_alive():
        cpu_usage_thread = threading.Thread(target=monitor_system_resources, daemon=True)
        cpu_usage_thread.start()
        print("Resource monitoring thread started")
    
    # 사운드 디렉토리 생성
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    os.makedirs(CUSTOM_SOUNDS_DIR, exist_ok=True)
    
    print("Timer application initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """앱 종료 시 정리"""
    # 활성 타이머들의 현재 상태 저장
    timers = load_timers()
    for timer_id, timer_data in active_timers.items():
        if timer_data["status"] == TimerStatus.RUNNING:
            # 남은 시간 계산 및 저장
            remaining = calculate_remaining_time(timer_data)
            timer_data["remaining_seconds"] = remaining
        
        timers[timer_id] = timer_data
    
    save_timers(timers)
    
    # 스케줄러 종료
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("Background scheduler stopped")
    
    print("Timer application shutdown completed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
