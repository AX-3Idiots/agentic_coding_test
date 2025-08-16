from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes.dashboard import router as dashboard_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Simple Dashboard API"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])

@app.get("/")
async def root():
    return {"message": "Simple Dashboard API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
