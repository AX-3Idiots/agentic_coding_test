"""
Main FastAPI application for Counter with Data Persistence
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json
import os
import asyncio
from datetime import datetime, timezone
import time
from pathlib import Path

app = FastAPI(title="Counter Data Persistence API", version="1.0.0")

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

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)