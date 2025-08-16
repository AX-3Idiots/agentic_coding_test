"""
Main FastAPI application for Counter with Data Persistence
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import json
import os
import asyncio
from datetime import datetime, timezone
import time
from pathlib import Path

app = FastAPI(title="Product Catalog API", version="1.0.0")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data storage directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
COUNTER_FILE = DATA_DIR / "counter.json"
SESSION_FILE = DATA_DIR / "session.json"

# Models
class CounterData(BaseModel):
    value: int = Field(default=0, ge=-1000000, le=1000000)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = Field(default=1)

class SessionData(BaseModel):
    session_id: str
    start_time: datetime
    last_activity: datetime
    operations_count: int = 0
    increments: int = 0
    decrements: int = 0
    resets: int = 0

class CounterResponse(BaseModel):
    success: bool
    data: Optional[CounterData] = None
    message: str = ""

class SessionResponse(BaseModel):
    success: bool
    data: Optional[SessionData] = None
    message: str = ""

class BackupData(BaseModel):
    counter: CounterData
    session: SessionData
    export_timestamp: datetime
    version: int = 1

# Product Models
class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float = Field(ge=0)
    category: str
    brand: str
    in_stock: bool = True
    stock_quantity: int = Field(ge=0)
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductListResponse(BaseModel):
    success: bool
    products: List[Product]
    total: int
    page: int
    per_page: int
    total_pages: int
    message: str = ""

class ProductResponse(BaseModel):
    success: bool
    product: Optional[Product] = None
    message: str = ""

# Storage utilities
class StorageManager:
    @staticmethod
    async def save_counter(counter_data: CounterData) -> bool:
        """Save counter data with error handling and validation"""
        try:
            data = {
                "value": counter_data.value,
                "timestamp": counter_data.timestamp.isoformat(),
                "version": counter_data.version
            }
            
            # Write to temporary file first to prevent corruption
            temp_file = COUNTER_FILE.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Atomic move
            temp_file.replace(COUNTER_FILE)
            return True
        except Exception as e:
            print(f"Error saving counter data: {e}")
            return False
    
    @staticmethod
    async def load_counter() -> Optional[CounterData]:
        """Load counter data with validation and corruption recovery"""
        try:
            if not COUNTER_FILE.exists():
                return CounterData()
            
            with open(COUNTER_FILE, 'r') as f:
                data = json.load(f)
            
            # Validate and migrate data
            if not isinstance(data, dict):
                raise ValueError("Invalid data format")
            
            # Handle timestamp parsing
            timestamp_str = data.get("timestamp")
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = datetime.now(timezone.utc)
            
            counter_data = CounterData(
                value=int(data.get("value", 0)),
                timestamp=timestamp,
                version=int(data.get("version", 1))
            )
            
            return counter_data
            
        except Exception as e:
            print(f"Error loading counter data: {e}")
            # Return default counter on corruption
            return CounterData()
    
    @staticmethod
    async def save_session(session_data: SessionData) -> bool:
        """Save session data"""
        try:
            data = {
                "session_id": session_data.session_id,
                "start_time": session_data.start_time.isoformat(),
                "last_activity": session_data.last_activity.isoformat(),
                "operations_count": session_data.operations_count,
                "increments": session_data.increments,
                "decrements": session_data.decrements,
                "resets": session_data.resets
            }
            
            temp_file = SESSION_FILE.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            temp_file.replace(SESSION_FILE)
            return True
        except Exception as e:
            print(f"Error saving session data: {e}")
            return False
    
    @staticmethod
    async def load_session() -> Optional[SessionData]:
        """Load session data"""
        try:
            if not SESSION_FILE.exists():
                return None
            
            with open(SESSION_FILE, 'r') as f:
                data = json.load(f)
            
            session_data = SessionData(
                session_id=data["session_id"],
                start_time=datetime.fromisoformat(data["start_time"].replace('Z', '+00:00')),
                last_activity=datetime.fromisoformat(data["last_activity"].replace('Z', '+00:00')),
                operations_count=data.get("operations_count", 0),
                increments=data.get("increments", 0),
                decrements=data.get("decrements", 0),
                resets=data.get("resets", 0)
            )
            
            return session_data
            
        except Exception as e:
            print(f"Error loading session data: {e}")
            return None

# Global storage manager
storage = StorageManager()

# Sample product data - in a real app, this would be in a database
SAMPLE_PRODUCTS = [
    Product(
        id=1,
        name="Wireless Bluetooth Headphones",
        description="High-quality wireless headphones with noise cancellation and 30-hour battery life.",
        price=99.99,
        category="Electronics",
        brand="AudioTech",
        stock_quantity=25,
        image_url="https://via.placeholder.com/300x300/007ACC/FFFFFF?text=Headphones"
    ),
    Product(
        id=2,
        name="Smartphone Case",
        description="Durable protective case for smartphones with wireless charging compatibility.",
        price=24.99,
        category="Accessories",
        brand="ProtectGear",
        stock_quantity=50,
        image_url="https://via.placeholder.com/300x300/28A745/FFFFFF?text=Phone+Case"
    ),
    Product(
        id=3,
        name="Wireless Charging Pad",
        description="Fast wireless charging pad compatible with all Qi-enabled devices.",
        price=39.99,
        category="Electronics",
        brand="ChargeFast",
        stock_quantity=15,
        image_url="https://via.placeholder.com/300x300/FFC107/000000?text=Charger"
    ),
    Product(
        id=4,
        name="Bluetooth Speaker",
        description="Portable Bluetooth speaker with 360-degree sound and waterproof design.",
        price=79.99,
        category="Electronics",
        brand="SoundWave",
        stock_quantity=8,
        in_stock=True,
        image_url="https://via.placeholder.com/300x300/DC3545/FFFFFF?text=Speaker"
    ),
    Product(
        id=5,
        name="Laptop Stand",
        description="Adjustable aluminum laptop stand for improved ergonomics and cooling.",
        price=45.99,
        category="Accessories",
        brand="ErgoDesk",
        stock_quantity=20,
        image_url="https://via.placeholder.com/300x300/6C757D/FFFFFF?text=Laptop+Stand"
    ),
    Product(
        id=6,
        name="USB-C Hub",
        description="Multi-port USB-C hub with HDMI, USB 3.0, and SD card reader.",
        price=34.99,
        category="Electronics",
        brand="ConnectAll",
        stock_quantity=0,
        in_stock=False,
        image_url="https://via.placeholder.com/300x300/17A2B8/FFFFFF?text=USB+Hub"
    ),
    Product(
        id=7,
        name="Mechanical Keyboard",
        description="RGB mechanical gaming keyboard with tactile switches and programmable keys.",
        price=129.99,
        category="Electronics",
        brand="GameType",
        stock_quantity=12,
        image_url="https://via.placeholder.com/300x300/6F42C1/FFFFFF?text=Keyboard"
    ),
    Product(
        id=8,
        name="Wireless Mouse",
        description="Ergonomic wireless mouse with precision tracking and long battery life.",
        price=29.99,
        category="Electronics",
        brand="ClickMaster",
        stock_quantity=30,
        image_url="https://via.placeholder.com/300x300/E83E8C/FFFFFF?text=Mouse"
    ),
    Product(
        id=9,
        name="Monitor Stand",
        description="Adjustable monitor stand with storage space and cable management.",
        price=59.99,
        category="Accessories",
        brand="ViewPerfect",
        stock_quantity=10,
        image_url="https://via.placeholder.com/300x300/20C997/FFFFFF?text=Monitor+Stand"
    ),
    Product(
        id=10,
        name="Webcam HD",
        description="1080p HD webcam with auto-focus and built-in microphone for video calls.",
        price=49.99,
        category="Electronics",
        brand="StreamClear",
        stock_quantity=18,
        image_url="https://via.placeholder.com/300x300/FD7E14/FFFFFF?text=Webcam"
    ),
]

# API Endpoints
@app.get("/api/counter", response_model=CounterResponse)
async def get_counter():
    """Get current counter value and load on application start"""
    counter_data = await storage.load_counter()
    if counter_data is None:
        counter_data = CounterData()
    
    return CounterResponse(
        success=True,
        data=counter_data,
        message="Counter loaded successfully"
    )

@app.post("/api/counter/increment", response_model=CounterResponse)
async def increment_counter():
    """Increment counter with auto-save"""
    start_time = time.time()
    
    counter_data = await storage.load_counter()
    if counter_data is None:
        counter_data = CounterData()
    
    counter_data.value += 1
    counter_data.timestamp = datetime.now(timezone.utc)
    
    # Save with performance tracking
    saved = await storage.save_counter(counter_data)
    
    # Update session stats
    session_data = await storage.load_session()
    if session_data:
        session_data.increments += 1
        session_data.operations_count += 1
        session_data.last_activity = datetime.now(timezone.utc)
        await storage.save_session(session_data)
    
    elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
    
    if not saved:
        raise HTTPException(status_code=500, detail="Failed to save counter data")
    
    return CounterResponse(
        success=True,
        data=counter_data,
        message=f"Counter incremented and saved in {elapsed_time:.1f}ms"
    )

@app.post("/api/counter/decrement", response_model=CounterResponse)
async def decrement_counter():
    """Decrement counter with auto-save"""
    start_time = time.time()
    
    counter_data = await storage.load_counter()
    if counter_data is None:
        counter_data = CounterData()
    
    counter_data.value -= 1
    counter_data.timestamp = datetime.now(timezone.utc)
    
    saved = await storage.save_counter(counter_data)
    
    # Update session stats
    session_data = await storage.load_session()
    if session_data:
        session_data.decrements += 1
        session_data.operations_count += 1
        session_data.last_activity = datetime.now(timezone.utc)
        await storage.save_session(session_data)
    
    elapsed_time = (time.time() - start_time) * 1000
    
    if not saved:
        raise HTTPException(status_code=500, detail="Failed to save counter data")
    
    return CounterResponse(
        success=True,
        data=counter_data,
        message=f"Counter decremented and saved in {elapsed_time:.1f}ms"
    )

@app.post("/api/counter/reset", response_model=CounterResponse)
async def reset_counter():
    """Reset counter to 0 with auto-save"""
    start_time = time.time()
    
    counter_data = CounterData(value=0, timestamp=datetime.now(timezone.utc))
    saved = await storage.save_counter(counter_data)
    
    # Update session stats
    session_data = await storage.load_session()
    if session_data:
        session_data.resets += 1
        session_data.operations_count += 1
        session_data.last_activity = datetime.now(timezone.utc)
        await storage.save_session(session_data)
    
    elapsed_time = (time.time() - start_time) * 1000
    
    if not saved:
        raise HTTPException(status_code=500, detail="Failed to save counter data")
    
    return CounterResponse(
        success=True,
        data=counter_data,
        message=f"Counter reset and saved in {elapsed_time:.1f}ms"
    )

@app.get("/api/session", response_model=SessionResponse)
async def get_session():
    """Get current session data"""
    session_data = await storage.load_session()
    
    return SessionResponse(
        success=True,
        data=session_data,
        message="Session data retrieved"
    )

@app.post("/api/session/start", response_model=SessionResponse)
async def start_session():
    """Start a new session"""
    import uuid
    
    now = datetime.now(timezone.utc)
    session_data = SessionData(
        session_id=str(uuid.uuid4()),
        start_time=now,
        last_activity=now
    )
    
    saved = await storage.save_session(session_data)
    
    if not saved:
        raise HTTPException(status_code=500, detail="Failed to save session data")
    
    return SessionResponse(
        success=True,
        data=session_data,
        message="New session started"
    )

@app.get("/api/backup/export")
async def export_backup():
    """Export counter and session data as JSON"""
    counter_data = await storage.load_counter()
    session_data = await storage.load_session()
    
    if counter_data is None:
        counter_data = CounterData()
    
    if session_data is None:
        # Create a basic session for export
        import uuid
        now = datetime.now(timezone.utc)
        session_data = SessionData(
            session_id=str(uuid.uuid4()),
            start_time=now,
            last_activity=now
        )
    
    backup_data = BackupData(
        counter=counter_data,
        session=session_data,
        export_timestamp=datetime.now(timezone.utc)
    )
    
    return {
        "success": True,
        "data": backup_data.model_dump_json(indent=2),
        "filename": f"counter_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    }

@app.post("/api/backup/import")
async def import_backup(backup_json: str):
    """Import counter and session data from JSON"""
    try:
        backup_data = json.loads(backup_json)
        
        # Validate backup data structure
        if not isinstance(backup_data, dict):
            raise ValueError("Invalid backup format")
        
        if "counter" not in backup_data or "session" not in backup_data:
            raise ValueError("Missing required backup data")
        
        # Validate and create counter data
        counter_dict = backup_data["counter"]
        counter_data = CounterData(
            value=int(counter_dict.get("value", 0)),
            timestamp=datetime.fromisoformat(
                counter_dict.get("timestamp", datetime.now(timezone.utc).isoformat()).replace('Z', '+00:00')
            ),
            version=int(counter_dict.get("version", 1))
        )
        
        # Validate and create session data
        session_dict = backup_data["session"]
        session_data = SessionData(
            session_id=str(session_dict.get("session_id", "")),
            start_time=datetime.fromisoformat(
                session_dict.get("start_time", datetime.now(timezone.utc).isoformat()).replace('Z', '+00:00')
            ),
            last_activity=datetime.fromisoformat(
                session_dict.get("last_activity", datetime.now(timezone.utc).isoformat()).replace('Z', '+00:00')
            ),
            operations_count=int(session_dict.get("operations_count", 0)),
            increments=int(session_dict.get("increments", 0)),
            decrements=int(session_dict.get("decrements", 0)),
            resets=int(session_dict.get("resets", 0))
        )
        
        # Save the imported data
        counter_saved = await storage.save_counter(counter_data)
        session_saved = await storage.save_session(session_data)
        
        if not counter_saved or not session_saved:
            raise HTTPException(status_code=500, detail="Failed to save imported data")
        
        return {
            "success": True,
            "message": "Backup imported successfully",
            "counter_value": counter_data.value,
            "session_id": session_data.session_id
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

# Product API Endpoints
@app.get("/api/products", response_model=ProductListResponse)
async def get_products(
    q: Optional[str] = None,  # search query
    category: Optional[str] = None,  # filter by category
    brand: Optional[str] = None,  # filter by brand
    in_stock: Optional[bool] = None,  # filter by stock availability
    min_price: Optional[float] = None,  # price range filter
    max_price: Optional[float] = None,  # price range filter
    page: int = 1,  # page number (1-based)
    per_page: int = 10  # items per page
):
    """Get products with search, filtering, and pagination"""
    try:
        # Start with all products
        filtered_products = SAMPLE_PRODUCTS.copy()
        
        # Apply search filter
        if q:
            q_lower = q.lower()
            filtered_products = [
                p for p in filtered_products 
                if q_lower in p.name.lower() or q_lower in p.description.lower()
            ]
        
        # Apply category filter
        if category:
            filtered_products = [p for p in filtered_products if p.category.lower() == category.lower()]
        
        # Apply brand filter
        if brand:
            filtered_products = [p for p in filtered_products if p.brand.lower() == brand.lower()]
        
        # Apply stock filter
        if in_stock is not None:
            filtered_products = [p for p in filtered_products if p.in_stock == in_stock]
        
        # Apply price filters
        if min_price is not None:
            filtered_products = [p for p in filtered_products if p.price >= min_price]
        
        if max_price is not None:
            filtered_products = [p for p in filtered_products if p.price <= max_price]
        
        # Calculate pagination
        total = len(filtered_products)
        total_pages = (total + per_page - 1) // per_page  # Ceiling division
        
        # Validate page number
        if page < 1:
            page = 1
        if page > total_pages and total_pages > 0:
            page = total_pages
        
        # Apply pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_products = filtered_products[start_idx:end_idx]
        
        return ProductListResponse(
            success=True,
            products=paginated_products,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            message=f"Found {total} products"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")

@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """Get a single product by ID"""
    try:
        product = next((p for p in SAMPLE_PRODUCTS if p.id == product_id), None)
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
        
        return ProductResponse(
            success=True,
            product=product,
            message="Product retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching product: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)