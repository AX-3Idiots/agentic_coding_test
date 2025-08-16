from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MetricsResponse(BaseModel):
    total_users: int
    total_orders: int
    total_revenue: float
    users_growth: float
    orders_growth: float
    revenue_growth: float

class Activity(BaseModel):
    id: str
    type: str  # "user_signup" | "order_created"
    description: str
    timestamp: datetime
    user_name: Optional[str] = None
    amount: Optional[float] = None

class RecentActivitiesResponse(BaseModel):
    activities: List[Activity]
