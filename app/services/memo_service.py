from datetime import datetime
from typing import List, Optional
from app.schemas.memo import MemoResponse
from app.core.exceptions import MemoNotFoundError

class MemoService:
    def __init__(self):
        # In-memory storage for simplicity (replace with database in production)
        self._memos: List[dict] = []
        self._next_id = 1
    
    def create_memo(self, content: str) -> MemoResponse:
        memo = {
            "id": self._next_id,
            "content": content,
            "created_at": datetime.now()
        }
        self._memos.append(memo)
        self._next_id += 1
        return MemoResponse(**memo)
    
    def get_all_memos(self) -> List[MemoResponse]:
        # Sort by created_at descending (newest first)
        sorted_memos = sorted(self._memos, key=lambda x: x["created_at"], reverse=True)
        return [MemoResponse(**memo) for memo in sorted_memos]
    
    def delete_memo(self, memo_id: int) -> None:
        memo_index = None
        for i, memo in enumerate(self._memos):
            if memo["id"] == memo_id:
                memo_index = i
                break
        
        if memo_index is None:
            raise MemoNotFoundError(memo_id)
        
        self._memos.pop(memo_index)

# Global service instance
memo_service = MemoService()
