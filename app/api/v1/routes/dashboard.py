from fastapi import APIRouter, Query
from app.schemas.dashboard import MetricsResponse, RecentActivitiesResponse
from app.services.dashboard_service import dashboard_service

router = APIRouter()

@router.get("/dashboard/metrics", response_model=MetricsResponse)
async def get_dashboard_metrics():
    """
    Get dashboard metrics including total users, orders, revenue and growth rates.
    """
    return dashboard_service.get_metrics()

@router.get("/dashboard/recent-activities", response_model=RecentActivitiesResponse)
async def get_recent_activities(limit: int = Query(default=10, ge=1, le=50)):
    """
    Get recent activities (user signups and order creations).
    
    Args:
        limit: Number of activities to return (1-50, default: 10)
    """
    return dashboard_service.get_recent_activities(limit=limit)
