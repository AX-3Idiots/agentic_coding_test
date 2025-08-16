from typing import List
from datetime import datetime, timedelta
from app.schemas.dashboard import MetricsResponse, RecentActivitiesResponse, Activity
import random
import uuid

class DashboardService:
    """
    Dashboard service for handling business logic.
    In a real application, this would interact with a database.
    For now, it returns mock data.
    """
    
    def get_metrics(self) -> MetricsResponse:
        """Get dashboard metrics with mock data"""
        # Mock data - in real app, this would query the database
        return MetricsResponse(
            total_users=1250,
            total_orders=3420,
            total_revenue=125000.50,
            users_growth=12.5,
            orders_growth=8.3,
            revenue_growth=15.2
        )
    
    def get_recent_activities(self, limit: int = 10) -> RecentActivitiesResponse:
        """Get recent activities with mock data"""
        # Mock data - in real app, this would query the database
        activities = []
        
        for i in range(limit):
            activity_type = random.choice(["user_signup", "order_created"])
            timestamp = datetime.now() - timedelta(hours=random.randint(1, 72))
            
            if activity_type == "user_signup":
                activity = Activity(
                    id=str(uuid.uuid4()),
                    type=activity_type,
                    description=f"New user registered",
                    timestamp=timestamp,
                    user_name=f"User{random.randint(1000, 9999)}"
                )
            else:
                amount = round(random.uniform(10.0, 500.0), 2)
                activity = Activity(
                    id=str(uuid.uuid4()),
                    type=activity_type,
                    description=f"Order created",
                    timestamp=timestamp,
                    user_name=f"User{random.randint(1000, 9999)}",
                    amount=amount
                )
            
            activities.append(activity)
        
        # Sort by timestamp descending
        activities.sort(key=lambda x: x.timestamp, reverse=True)
        
        return RecentActivitiesResponse(activities=activities)

dashboard_service = DashboardService()
