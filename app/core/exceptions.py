from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class MemoNotFoundError(Exception):
    def __init__(self, memo_id: int):
        self.memo_id = memo_id
        super().__init__(f"Memo with id {memo_id} not found")

class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(MemoNotFoundError)
    async def memo_not_found_handler(request: Request, exc: MemoNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": f"Memo with id {exc.memo_id} not found"}
        )
    
    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=400,
            content={"detail": exc.message}
        )
