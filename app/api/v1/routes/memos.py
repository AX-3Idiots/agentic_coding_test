from fastapi import APIRouter, HTTPException, status
from typing import List

from app.schemas.memo import MemoCreate, MemoResponse, MemoListResponse
from app.services.memo_service import memo_service
from app.core.exceptions import MemoNotFoundError, ValidationError

router = APIRouter()

@router.post("/memos", response_model=MemoResponse, status_code=status.HTTP_201_CREATED)
async def create_memo(memo_data: MemoCreate):
    """
    Create a new memo.
    
    - **content**: Memo content (1-140 characters, required)
    """
    try:
        return memo_service.create_memo(memo_data.content)
    except ValueError as e:
        raise ValidationError(str(e))

@router.get("/memos", response_model=List[MemoResponse])
async def get_memos():
    """
    Retrieve all memos sorted by creation date (newest first).
    """
    return memo_service.get_all_memos()

@router.delete("/memos/{memo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memo(memo_id: int):
    """
    Delete a specific memo by ID.
    
    - **memo_id**: ID of the memo to delete
    """
    try:
        memo_service.delete_memo(memo_id)
    except MemoNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memo with id {memo_id} not found"
        )
