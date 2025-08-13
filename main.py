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
import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import aiofiles
from decimal import Decimal

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

# 데이터 파일들
USERS_FILE = "users.json"
TIMERS_FILE = "timers.json"
SOUNDS_DIR = "sounds"
CUSTOM_SOUNDS_DIR = "custom_sounds"
ORDERS_FILE = "orders.json"
PRODUCTS_FILE = "products.json"
ADDRESSES_FILE = "addresses.json"
PAYMENTS_FILE = "payments.json"
PAYOUTS_FILE = "payouts.json"

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
    role: UserRole = UserRole.CUSTOMER

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    email: str
    role: UserRole
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

# E-commerce related enums
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    STRIPE = "stripe"

class UserRole(str, Enum):
    CUSTOMER = "customer"
    VENDOR = "vendor"
    ADMIN = "admin"

class PayoutStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

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

# E-commerce Pydantic models
class Address(BaseModel):
    id: Optional[str] = None
    street: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(..., min_length=1, max_length=100)
    is_default: bool = False

class AddressCreate(BaseModel):
    street: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(..., min_length=1, max_length=100)
    is_default: bool = False

class Product(BaseModel):
    id: str
    vendor_email: str
    name: str
    description: str
    price: Decimal
    inventory_count: int
    category: str
    image_urls: List[str] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    price: Decimal = Field(..., gt=0)
    inventory_count: int = Field(..., ge=0)
    category: str = Field(..., min_length=1, max_length=100)
    image_urls: List[str] = []

class CartItem(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)
    price: Decimal

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    vendor_email: str

class PaymentInfo(BaseModel):
    payment_method: PaymentMethod
    token: str  # Payment processor token for security
    billing_address_id: str

class CheckoutRequest(BaseModel):
    cart_items: List[CartItem]
    shipping_address_id: str
    billing_address_id: Optional[str] = None  # If None, use shipping address
    payment_info: PaymentInfo
    guest_checkout: bool = False
    guest_email: Optional[str] = None

class Order(BaseModel):
    id: str
    customer_email: str
    items: List[OrderItem]
    subtotal: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    total_amount: Decimal
    status: OrderStatus
    payment_status: PaymentStatus
    shipping_address: Address
    billing_address: Address
    tracking_number: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

class OrderResponse(BaseModel):
    id: str
    customer_email: str
    items: List[OrderItem]
    subtotal: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    total_amount: Decimal
    status: OrderStatus
    payment_status: PaymentStatus
    shipping_address: Address
    billing_address: Address
    tracking_number: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    tracking_number: Optional[str] = None
    notes: Optional[str] = None

class Payout(BaseModel):
    id: str
    vendor_email: str
    amount: Decimal
    commission_rate: float
    platform_fee: Decimal
    net_amount: Decimal
    status: PayoutStatus
    order_ids: List[str]
    created_at: datetime
    processed_at: Optional[datetime] = None

class PayoutResponse(BaseModel):
    id: str
    vendor_email: str
    amount: Decimal
    commission_rate: float
    platform_fee: Decimal
    net_amount: Decimal
    status: PayoutStatus
    order_ids: List[str]
    created_at: datetime
    processed_at: Optional[datetime] = None

class PlatformMetrics(BaseModel):
    total_orders: int
    total_revenue: Decimal
    active_vendors: int
    active_customers: int
    orders_today: int
    revenue_today: Decimal
    pending_payouts: int
    pending_payout_amount: Decimal

class VendorStats(BaseModel):
    total_orders: int
    total_revenue: Decimal
    pending_orders: int
    completed_orders: int
    cancelled_orders: int
    average_order_value: Decimal
    top_selling_products: List[Dict[str, Any]]

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

# E-commerce data utility functions
def load_orders():
    """JSON 파일에서 주문 데이터 로드"""
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_orders(orders):
    """주문 데이터를 JSON 파일에 저장"""
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2, default=str)

def load_products():
    """JSON 파일에서 상품 데이터 로드"""
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_products(products):
    """상품 데이터를 JSON 파일에 저장"""
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2, default=str)

def load_addresses():
    """JSON 파일에서 주소 데이터 로드"""
    if os.path.exists(ADDRESSES_FILE):
        with open(ADDRESSES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_addresses(addresses):
    """주소 데이터를 JSON 파일에 저장"""
    with open(ADDRESSES_FILE, 'w', encoding='utf-8') as f:
        json.dump(addresses, f, ensure_ascii=False, indent=2, default=str)

def load_payouts():
    """JSON 파일에서 정산 데이터 로드"""
    if os.path.exists(PAYOUTS_FILE):
        with open(PAYOUTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_payouts(payouts):
    """정산 데이터를 JSON 파일에 저장"""
    with open(PAYOUTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(payouts, f, ensure_ascii=False, indent=2, default=str)

def get_user_role(email: str) -> UserRole:
    """사용자의 역할 반환"""
    users = load_users()
    if email in users:
        return UserRole(users[email].get("role", UserRole.CUSTOMER))
    return UserRole.CUSTOMER

def calculate_tax(subtotal: Decimal) -> Decimal:
    """세금 계산 (10% 고정)"""
    return subtotal * Decimal('0.10')

def calculate_shipping(subtotal: Decimal) -> Decimal:
    """배송비 계산"""
    if subtotal >= Decimal('50.00'):
        return Decimal('0.00')  # 무료배송
    return Decimal('5.99')

def process_payment(payment_info: PaymentInfo, amount: Decimal) -> bool:
    """결제 처리 (모의 구현)"""
    # 실제로는 결제 처리업체 API를 호출
    # 토큰을 사용하여 PCI DSS 준수
    if not payment_info.token or len(payment_info.token) < 10:
        return False
    
    # 모의 결제 실패 조건
    if amount > Decimal('10000.00'):  # $10,000 초과 시 실패
        return False
        
    # 90% 확률로 성공
    return random.random() > 0.1

def send_order_notification(order: Order, status_change: str = "created"):
    """주문 관련 이메일 알림 발송"""
    try:
        print(f"Sending notification: Order {order.id} - {status_change}")
        print(f"To: {order.customer_email}")
        print(f"Status: {order.status}")
        # 실제 구현에서는 이메일 서비스 API 호출
        return True
    except Exception as e:
        print(f"Failed to send notification: {e}")
        return False

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
        "role": user.role.value,
        "created_at": datetime.utcnow().isoformat()
    }
    save_users(users)
    
    return UserResponse(
        email=user.email,
        role=user.role,
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
        role=UserRole(user_data.get("role", UserRole.CUSTOMER.value)),
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

# Address Management Endpoints
@app.post("/addresses", response_model=Address)
async def create_address(address_data: AddressCreate, current_user_email: str = Depends(verify_token)):
    """사용자 주소 추가"""
    addresses = load_addresses()
    user_addresses = addresses.get(current_user_email, {})
    
    address_id = str(uuid.uuid4())
    address = Address(
        id=address_id,
        **address_data.dict()
    )
    
    # 첫 번째 주소이거나 기본 주소로 설정된 경우
    if not user_addresses or address_data.is_default:
        # 기존 기본 주소 해제
        for addr_id, addr in user_addresses.items():
            addr["is_default"] = False
        address.is_default = True
    
    user_addresses[address_id] = address.dict()
    addresses[current_user_email] = user_addresses
    save_addresses(addresses)
    
    return address

@app.get("/addresses", response_model=List[Address])
async def list_addresses(current_user_email: str = Depends(verify_token)):
    """사용자 주소 목록 조회"""
    addresses = load_addresses()
    user_addresses = addresses.get(current_user_email, {})
    
    return [Address(**addr) for addr in user_addresses.values()]

@app.get("/addresses/{address_id}", response_model=Address)
async def get_address(address_id: str, current_user_email: str = Depends(verify_token)):
    """특정 주소 조회"""
    addresses = load_addresses()
    user_addresses = addresses.get(current_user_email, {})
    
    if address_id not in user_addresses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    
    return Address(**user_addresses[address_id])

@app.put("/addresses/{address_id}", response_model=Address)
async def update_address(address_id: str, address_data: AddressCreate, current_user_email: str = Depends(verify_token)):
    """주소 수정"""
    addresses = load_addresses()
    user_addresses = addresses.get(current_user_email, {})
    
    if address_id not in user_addresses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    
    # 기본 주소로 설정하는 경우 다른 주소들 기본 해제
    if address_data.is_default:
        for addr_id, addr in user_addresses.items():
            addr["is_default"] = False
    
    updated_address = Address(
        id=address_id,
        **address_data.dict()
    )
    
    user_addresses[address_id] = updated_address.dict()
    addresses[current_user_email] = user_addresses
    save_addresses(addresses)
    
    return updated_address

@app.delete("/addresses/{address_id}")
async def delete_address(address_id: str, current_user_email: str = Depends(verify_token)):
    """주소 삭제"""
    addresses = load_addresses()
    user_addresses = addresses.get(current_user_email, {})
    
    if address_id not in user_addresses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    
    del user_addresses[address_id]
    addresses[current_user_email] = user_addresses
    save_addresses(addresses)
    
    return {"message": "Address deleted successfully"}

# Product Management Endpoints (for vendors)
@app.post("/products", response_model=Product)
async def create_product(product_data: ProductCreate, current_user_email: str = Depends(verify_token)):
    """상품 생성 (벤더 전용)"""
    user_role = get_user_role(current_user_email)
    if user_role not in [UserRole.VENDOR, UserRole.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vendor access required")
    
    products = load_products()
    product_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    product = Product(
        id=product_id,
        vendor_email=current_user_email,
        created_at=now,
        **product_data.dict()
    )
    
    products[product_id] = product.dict()
    save_products(products)
    
    return product

@app.get("/products", response_model=List[Product])
async def list_products(category: Optional[str] = None, vendor_email: Optional[str] = None):
    """상품 목록 조회 (공개)"""
    products = load_products()
    product_list = []
    
    for product_data in products.values():
        product = Product(**product_data)
        # 필터링
        if category and product.category != category:
            continue
        if vendor_email and product.vendor_email != vendor_email:
            continue
        product_list.append(product)
    
    return product_list

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """특정 상품 조회 (공개)"""
    products = load_products()
    if product_id not in products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    return Product(**products[product_id])

# Checkout Process Endpoints
@app.post("/checkout/validate-cart")
async def validate_cart(cart_items: List[CartItem], current_user_email: str = Depends(verify_token)):
    """장바구니 검증"""
    products = load_products()
    validated_items = []
    subtotal = Decimal('0.00')
    
    for item in cart_items:
        if item.product_id not in products:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                              detail=f"Product {item.product_id} not found")
        
        product = Product(**products[item.product_id])
        
        # 재고 확인
        if product.inventory_count < item.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                              detail=f"Insufficient inventory for {product.name}")
        
        # 가격 검증
        if item.price != product.price:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                              detail=f"Price mismatch for {product.name}")
        
        item_total = item.price * item.quantity
        subtotal += item_total
        
        validated_items.append({
            "product_id": item.product_id,
            "product_name": product.name,
            "quantity": item.quantity,
            "unit_price": item.price,
            "total_price": item_total,
            "vendor_email": product.vendor_email
        })
    
    tax_amount = calculate_tax(subtotal)
    shipping_amount = calculate_shipping(subtotal)
    total_amount = subtotal + tax_amount + shipping_amount
    
    return {
        "validated_items": validated_items,
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "shipping_amount": shipping_amount,
        "total_amount": total_amount
    }

@app.post("/checkout/process", response_model=OrderResponse)
async def process_checkout(checkout_request: CheckoutRequest, current_user_email: str = Depends(verify_token)):
    """결제 처리 및 주문 생성"""
    # 게스트 체크아웃 처리
    customer_email = checkout_request.guest_email if checkout_request.guest_checkout else current_user_email
    
    # 장바구니 검증
    validation_result = await validate_cart(checkout_request.cart_items, current_user_email)
    
    # 주소 검증
    addresses = load_addresses()
    
    # 배송 주소
    if checkout_request.guest_checkout:
        # 게스트의 경우 요청에서 주소 정보를 직접 받아야 함 (단순화를 위해 생략)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                          detail="Guest checkout address handling not implemented")
    else:
        user_addresses = addresses.get(current_user_email, {})
        if checkout_request.shipping_address_id not in user_addresses:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                              detail="Invalid shipping address")
        shipping_address = Address(**user_addresses[checkout_request.shipping_address_id])
    
    # 청구 주소 (없으면 배송 주소 사용)
    billing_address_id = checkout_request.billing_address_id or checkout_request.shipping_address_id
    if billing_address_id not in user_addresses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                          detail="Invalid billing address")
    billing_address = Address(**user_addresses[billing_address_id])
    
    # 결제 처리
    payment_success = process_payment(checkout_request.payment_info, validation_result["total_amount"])
    if not payment_success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                          detail="Payment processing failed")
    
    # 주문 생성
    order_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    order_items = [OrderItem(**item) for item in validation_result["validated_items"]]
    
    order = Order(
        id=order_id,
        customer_email=customer_email,
        items=order_items,
        subtotal=validation_result["subtotal"],
        tax_amount=validation_result["tax_amount"],
        shipping_amount=validation_result["shipping_amount"],
        total_amount=validation_result["total_amount"],
        status=OrderStatus.CONFIRMED,
        payment_status=PaymentStatus.COMPLETED,
        shipping_address=shipping_address,
        billing_address=billing_address,
        created_at=now
    )
    
    # 주문 저장
    orders = load_orders()
    orders[order_id] = order.dict()
    save_orders(orders)
    
    # 재고 업데이트
    products = load_products()
    for item in checkout_request.cart_items:
        products[item.product_id]["inventory_count"] -= item.quantity
    save_products(products)
    
    # 이메일 알림 발송
    send_order_notification(order, "created")
    
    return OrderResponse(**order.dict())

# Customer Order Tracking Endpoints
@app.get("/orders", response_model=List[OrderResponse])
async def list_customer_orders(
    status: Optional[OrderStatus] = None,
    current_user_email: str = Depends(verify_token)
):
    """고객 주문 내역 조회"""
    orders = load_orders()
    customer_orders = []
    
    for order_data in orders.values():
        order = Order(**order_data)
        if order.customer_email == current_user_email:
            # 상태 필터링
            if status and order.status != status:
                continue
            customer_orders.append(OrderResponse(**order.dict()))
    
    # 생성일 기준 내림차순 정렬
    customer_orders.sort(key=lambda x: x.created_at, reverse=True)
    return customer_orders

@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order_details(order_id: str, current_user_email: str = Depends(verify_token)):
    """특정 주문 상세 정보 조회"""
    orders = load_orders()
    if order_id not in orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    order = Order(**orders[order_id])
    if order.customer_email != current_user_email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    return OrderResponse(**order.dict())

@app.post("/orders/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(order_id: str, current_user_email: str = Depends(verify_token)):
    """주문 취소 (배송 전만 가능)"""
    orders = load_orders()
    if order_id not in orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    order_data = orders[order_id]
    order = Order(**order_data)
    
    if order.customer_email != current_user_email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # 취소 가능한 상태 확인
    if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PROCESSING]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                          detail="Order cannot be cancelled at this stage")
    
    # 주문 상태 변경
    order_data["status"] = OrderStatus.CANCELLED.value
    order_data["updated_at"] = datetime.utcnow().isoformat()
    orders[order_id] = order_data
    save_orders(orders)
    
    # 재고 복원
    products = load_products()
    for item in order.items:
        if item.product_id in products:
            products[item.product_id]["inventory_count"] += item.quantity
    save_products(products)
    
    # 알림 발송
    updated_order = Order(**order_data)
    send_order_notification(updated_order, "cancelled")
    
    return OrderResponse(**order_data)

@app.post("/orders/{order_id}/return", response_model=OrderResponse)
async def request_return(order_id: str, current_user_email: str = Depends(verify_token)):
    """반품 요청 (배송 완료 후만 가능)"""
    orders = load_orders()
    if order_id not in orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    order_data = orders[order_id]
    order = Order(**order_data)
    
    if order.customer_email != current_user_email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # 반품 가능한 상태 확인
    if order.status != OrderStatus.DELIVERED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                          detail="Returns are only available for delivered orders")
    
    # 배송 완료 후 7일 이내만 반품 가능
    if order.delivered_at:
        delivered_date = datetime.fromisoformat(order.delivered_at)
        days_since_delivery = (datetime.utcnow() - delivered_date).days
        if days_since_delivery > 7:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                              detail="Return period has expired (7 days from delivery)")
    
    # 주문 상태 변경
    order_data["status"] = OrderStatus.RETURNED.value
    order_data["updated_at"] = datetime.utcnow().isoformat()
    orders[order_id] = order_data
    save_orders(orders)
    
    # 알림 발송
    updated_order = Order(**order_data)
    send_order_notification(updated_order, "return_requested")
    
    return OrderResponse(**order_data)

# Vendor Order Management Endpoints
@app.get("/vendor/orders", response_model=List[OrderResponse])
async def list_vendor_orders(
    status: Optional[OrderStatus] = None,
    current_user_email: str = Depends(verify_token)
):
    """벤더 주문 관리 - 해당 벤더 상품이 포함된 주문 조회"""
    user_role = get_user_role(current_user_email)
    if user_role not in [UserRole.VENDOR, UserRole.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vendor access required")
    
    orders = load_orders()
    vendor_orders = []
    
    for order_data in orders.values():
        order = Order(**order_data)
        
        # 이 벤더의 상품이 포함된 주문인지 확인
        has_vendor_product = any(item.vendor_email == current_user_email for item in order.items)
        if not has_vendor_product and user_role != UserRole.ADMIN:
            continue
        
        # 상태 필터링
        if status and order.status != status:
            continue
        
        vendor_orders.append(OrderResponse(**order.dict()))
    
    # 생성일 기준 내림차순 정렬
    vendor_orders.sort(key=lambda x: x.created_at, reverse=True)
    return vendor_orders

@app.post("/vendor/orders/{order_id}/update-status", response_model=OrderResponse)
async def update_order_status(
    order_id: str, 
    status_update: OrderStatusUpdate,
    current_user_email: str = Depends(verify_token)
):
    """주문 상태 업데이트 (벤더/관리자 전용)"""
    user_role = get_user_role(current_user_email)
    if user_role not in [UserRole.VENDOR, UserRole.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vendor access required")
    
    orders = load_orders()
    if order_id not in orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    order_data = orders[order_id]
    order = Order(**order_data)
    
    # 벤더인 경우 자신의 상품이 포함된 주문만 수정 가능
    if user_role == UserRole.VENDOR:
        has_vendor_product = any(item.vendor_email == current_user_email for item in order.items)
        if not has_vendor_product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # 상태 업데이트
    order_data["status"] = status_update.status.value
    order_data["updated_at"] = datetime.utcnow().isoformat()
    
    if status_update.tracking_number:
        order_data["tracking_number"] = status_update.tracking_number
    
    if status_update.status == OrderStatus.SHIPPED and not order_data.get("shipped_at"):
        order_data["shipped_at"] = datetime.utcnow().isoformat()
    
    if status_update.status == OrderStatus.DELIVERED and not order_data.get("delivered_at"):
        order_data["delivered_at"] = datetime.utcnow().isoformat()
    
    orders[order_id] = order_data
    save_orders(orders)
    
    # 알림 발송
    updated_order = Order(**order_data)
    send_order_notification(updated_order, f"status_changed_to_{status_update.status.value}")
    
    return OrderResponse(**order_data)

@app.get("/vendor/stats", response_model=VendorStats)
async def get_vendor_stats(current_user_email: str = Depends(verify_token)):
    """벤더 판매 통계"""
    user_role = get_user_role(current_user_email)
    if user_role not in [UserRole.VENDOR, UserRole.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vendor access required")
    
    orders = load_orders()
    vendor_orders = []
    total_revenue = Decimal('0.00')
    
    # 벤더의 주문들 수집
    for order_data in orders.values():
        order = Order(**order_data)
        vendor_items = [item for item in order.items if item.vendor_email == current_user_email]
        
        if vendor_items:
            vendor_orders.append(order)
            # 해당 벤더 상품 매출 계산
            for item in vendor_items:
                total_revenue += item.total_price
    
    # 통계 계산
    total_orders = len(vendor_orders)
    pending_orders = len([o for o in vendor_orders if o.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PROCESSING]])
    completed_orders = len([o for o in vendor_orders if o.status == OrderStatus.DELIVERED])
    cancelled_orders = len([o for o in vendor_orders if o.status == OrderStatus.CANCELLED])
    
    average_order_value = total_revenue / total_orders if total_orders > 0 else Decimal('0.00')
    
    # 인기 상품 Top 5 (단순화)
    product_sales = {}
    for order in vendor_orders:
        for item in order.items:
            if item.vendor_email == current_user_email:
                if item.product_id not in product_sales:
                    product_sales[item.product_id] = {"name": item.product_name, "quantity": 0, "revenue": Decimal('0.00')}
                product_sales[item.product_id]["quantity"] += item.quantity
                product_sales[item.product_id]["revenue"] += item.total_price
    
    top_selling_products = sorted(
        [{"product_id": pid, **stats} for pid, stats in product_sales.items()],
        key=lambda x: x["quantity"],
        reverse=True
    )[:5]
    
    return VendorStats(
        total_orders=total_orders,
        total_revenue=total_revenue,
        pending_orders=pending_orders,
        completed_orders=completed_orders,
        cancelled_orders=cancelled_orders,
        average_order_value=average_order_value,
        top_selling_products=top_selling_products
    )

# Automated Payout System
@app.get("/vendor/payouts", response_model=List[PayoutResponse])
async def list_vendor_payouts(current_user_email: str = Depends(verify_token)):
    """벤더 정산 내역 조회"""
    user_role = get_user_role(current_user_email)
    if user_role not in [UserRole.VENDOR, UserRole.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vendor access required")
    
    payouts = load_payouts()
    vendor_payouts = []
    
    for payout_data in payouts.values():
        payout = Payout(**payout_data)
        if payout.vendor_email == current_user_email or user_role == UserRole.ADMIN:
            vendor_payouts.append(PayoutResponse(**payout.dict()))
    
    # 생성일 기준 내림차순 정렬
    vendor_payouts.sort(key=lambda x: x.created_at, reverse=True)
    return vendor_payouts

@app.post("/admin/process-payouts")
async def process_pending_payouts(current_user_email: str = Depends(verify_token)):
    """대기 중인 정산 처리 (관리자 전용)"""
    user_role = get_user_role(current_user_email)
    if user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    orders = load_orders()
    payouts = load_payouts()
    
    # 벤더별 완료된 주문 수집
    vendor_earnings = {}
    commission_rate = 0.10  # 10% 수수료
    
    for order_data in orders.values():
        order = Order(**order_data)
        if order.status == OrderStatus.DELIVERED and order.payment_status == PaymentStatus.COMPLETED:
            
            # 이미 정산된 주문인지 확인
            order_already_paid = any(
                order.id in payout_data.get("order_ids", []) 
                for payout_data in payouts.values()
            )
            
            if not order_already_paid:
                for item in order.items:
                    vendor_email = item.vendor_email
                    if vendor_email not in vendor_earnings:
                        vendor_earnings[vendor_email] = {
                            "total_amount": Decimal('0.00'),
                            "order_ids": []
                        }
                    
                    vendor_earnings[vendor_email]["total_amount"] += item.total_price
                    if order.id not in vendor_earnings[vendor_email]["order_ids"]:
                        vendor_earnings[vendor_email]["order_ids"].append(order.id)
    
    # 정산 생성
    created_payouts = []
    for vendor_email, earnings in vendor_earnings.items():
        if earnings["total_amount"] > Decimal('0.00'):
            payout_id = str(uuid.uuid4())
            platform_fee = earnings["total_amount"] * Decimal(str(commission_rate))
            net_amount = earnings["total_amount"] - platform_fee
            
            payout = Payout(
                id=payout_id,
                vendor_email=vendor_email,
                amount=earnings["total_amount"],
                commission_rate=commission_rate,
                platform_fee=platform_fee,
                net_amount=net_amount,
                status=PayoutStatus.PENDING,
                order_ids=earnings["order_ids"],
                created_at=datetime.utcnow()
            )
            
            payouts[payout_id] = payout.dict()
            created_payouts.append(payout)
    
    save_payouts(payouts)
    
    return {
        "message": f"Created {len(created_payouts)} payouts",
        "payouts": [PayoutResponse(**payout.dict()) for payout in created_payouts]
    }

@app.post("/admin/approve-payout/{payout_id}")
async def approve_payout(payout_id: str, current_user_email: str = Depends(verify_token)):
    """정산 승인 (관리자 전용)"""
    user_role = get_user_role(current_user_email)
    if user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    payouts = load_payouts()
    if payout_id not in payouts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payout not found")
    
    payout_data = payouts[payout_id]
    if payout_data["status"] != PayoutStatus.PENDING.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                          detail="Only pending payouts can be approved")
    
    # 정산 상태 변경
    payout_data["status"] = PayoutStatus.COMPLETED.value
    payout_data["processed_at"] = datetime.utcnow().isoformat()
    payouts[payout_id] = payout_data
    save_payouts(payouts)
    
    # 실제로는 결제 처리업체 API를 호출하여 송금 처리
    print(f"Payout processed: ${payout_data['net_amount']} to {payout_data['vendor_email']}")
    
    return {"message": "Payout approved and processed", "payout": PayoutResponse(**payout_data)}

# Administrator Platform Monitoring
@app.get("/admin/metrics", response_model=PlatformMetrics)
async def get_platform_metrics(current_user_email: str = Depends(verify_token)):
    """플랫폼 전체 지표 조회 (관리자 전용)"""
    user_role = get_user_role(current_user_email)
    if user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    orders = load_orders()
    users = load_users()
    payouts = load_payouts()
    
    # 전체 주문 통계
    total_orders = len(orders)
    total_revenue = Decimal('0.00')
    
    # 오늘 주문 통계
    today = datetime.utcnow().date()
    orders_today = 0
    revenue_today = Decimal('0.00')
    
    for order_data in orders.values():
        order = Order(**order_data)
        if order.payment_status == PaymentStatus.COMPLETED:
            total_revenue += order.total_amount
            
            # 오늘 주문인지 확인
            order_date = order.created_at.date()
            if order_date == today:
                orders_today += 1
                revenue_today += order.total_amount
    
    # 사용자 통계
    active_vendors = len([user for user in users.values() if user.get("role") == UserRole.VENDOR.value])
    active_customers = len([user for user in users.values() if user.get("role") == UserRole.CUSTOMER.value])
    
    # 정산 통계
    pending_payouts = len([p for p in payouts.values() if p["status"] == PayoutStatus.PENDING.value])
    pending_payout_amount = sum(
        Decimal(str(p["net_amount"])) for p in payouts.values() 
        if p["status"] == PayoutStatus.PENDING.value
    )
    
    return PlatformMetrics(
        total_orders=total_orders,
        total_revenue=total_revenue,
        active_vendors=active_vendors,
        active_customers=active_customers,
        orders_today=orders_today,
        revenue_today=revenue_today,
        pending_payouts=pending_payouts,
        pending_payout_amount=pending_payout_amount
    )

@app.get("/admin/users")
async def list_all_users(
    role: Optional[UserRole] = None,
    current_user_email: str = Depends(verify_token)
):
    """모든 사용자 목록 조회 (관리자 전용)"""
    user_role = get_user_role(current_user_email)
    if user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    users = load_users()
    user_list = []
    
    for email, user_data in users.items():
        user_role_enum = UserRole(user_data.get("role", UserRole.CUSTOMER.value))
        
        # 역할 필터링
        if role and user_role_enum != role:
            continue
        
        user_list.append({
            "email": email,
            "role": user_role_enum.value,
            "created_at": user_data["created_at"]
        })
    
    return {"users": user_list}

@app.post("/admin/users/{user_email}/update-role")
async def update_user_role(
    user_email: str,
    new_role: UserRole,
    current_user_email: str = Depends(verify_token)
):
    """사용자 역할 변경 (관리자 전용)"""
    admin_role = get_user_role(current_user_email)
    if admin_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    users = load_users()
    if user_email not in users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    users[user_email]["role"] = new_role.value
    save_users(users)
    
    return {"message": f"User {user_email} role updated to {new_role.value}"}

@app.get("/admin/orders", response_model=List[OrderResponse])
async def list_all_orders(
    status: Optional[OrderStatus] = None,
    vendor_email: Optional[str] = None,
    current_user_email: str = Depends(verify_token)
):
    """모든 주문 조회 (관리자 전용)"""
    user_role = get_user_role(current_user_email)
    if user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    orders = load_orders()
    all_orders = []
    
    for order_data in orders.values():
        order = Order(**order_data)
        
        # 상태 필터링
        if status and order.status != status:
            continue
        
        # 벤더 필터링
        if vendor_email:
            has_vendor_product = any(item.vendor_email == vendor_email for item in order.items)
            if not has_vendor_product:
                continue
        
        all_orders.append(OrderResponse(**order.dict()))
    
    # 생성일 기준 내림차순 정렬
    all_orders.sort(key=lambda x: x.created_at, reverse=True)
    return all_orders

# Health Check Endpoint
@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

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
