from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes.memos import router as memos_router
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Simple memo management API"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(memos_router, prefix="/api", tags=["memos"])

@app.get("/")
async def root():
    return {"message": "Simple Memo App API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
