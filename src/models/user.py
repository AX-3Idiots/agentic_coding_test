# User Model
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class User(BaseModel):
    email: str
    hashed_password: str
    created_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
