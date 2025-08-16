from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, validator

class MemoCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=140, description="Memo content (1-140 characters)")
    
    @validator("content")
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        if len(v) > 140:
            raise ValueError("Content cannot exceed 140 characters")
        return v.strip()

class MemoResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MemoListResponse(BaseModel):
    memos: List[MemoResponse]
