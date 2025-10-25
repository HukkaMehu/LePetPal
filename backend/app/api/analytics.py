"""
Analytics API endpoints.

Provides endpoints for retrieving daily metrics, streaks, and badges.

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date, datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID

from app.db.base import get_db
from app.models.ai_metrics_daily import AIMetricsDaily
from app.models.event import Event


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# Pydantic models for request/response
class DailyMetricsResponse(BaseModel):
    date: date
    sit_count: int
    stand_count: int
    lie_count: int
    fetch_count: int
    fetch_success_count: int
    treats_dispensed: int
    time_in_frame_min: int
    barks: int
    howls: int
    whines: int
    calm_minutes: int
    
    class Config:
        from_attributes = True


class Badge(BaseModel):
    id: str
    name: str
    description: str
    earned_date: date
    icon: str


class StreaksResponse(BaseModel):
    sit_streak: int
    recall_streak: int
    training_streak: int
    badges: List[Badge]


@router.get("/daily", response_model=List[DailyMetricsResponse])
async def get_daily_metrics(
    from_date: date = Query(..., description="Start date (inclusive)"),
    to_date: date = Query(..., description="End date (inclusive)"),
    user_id: UUID = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Get daily metrics for a date range.
    
    Returns aggregated metrics including:
    - Sit/stand/lie counts
    - Fetch attempts and successes
    - Time in frame
    - Bark/howl/whine counts
    - Calm minutes
    """
    # Validate date range
    if from_date > to_date:
        raise HTTPException(status_code=400, detail="from_date must be before or equal to to_date")
    
    # Query metrics
    metrics = db.query(AIMetricsDaily).filter(
        and_(
            AIMetricsDaily.user_id == user_id,
            AIMetricsDaily.date >= from_date,
            AIMetricsDaily.date <= to_date
        )
    ).order_by(AIMetricsDaily.date).all()
    
    return metrics


@router.get("/streaks", response_model=StreaksResponse)
async def get_streaks(
    user_id: UUID = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Calculate training streaks and badges.
    
    Streaks:
    - Sit streak: Consecutive days with at least 5 sits
    - Recall streak: Consecutive days with at least 3 successful fetch returns
    - Training streak: Consecutive days with any training activity
    
    Badges:
    - 7-day sit streak
    - 5 perfect recall days
    - Other milestones
    """
    # Get all metrics ordered by date descending
    metrics = db.query(AIMetricsDaily).filter(
        AIMetricsDaily.user_id == user_id
    ).order_by(AIMetricsDaily.date.desc()).all()
    
    if not metrics:
        return StreaksResponse(
            sit_streak=0,
            recall_streak=0,
            training_streak=0,
            badges=[]
        )
    
    # Calculate sit streak (consecutive days with >= 5 sits)
    sit_streak = 0
    for metric in metrics:
        if metric.sit_count >= 5:
            sit_streak += 1
        else:
            break
    
    # Calculate recall streak (consecutive days with >= 3 successful fetches)
    recall_streak = 0
    for metric in metrics:
        if metric.fetch_success_count >= 3:
            recall_streak += 1
        else:
            break
    
    # Calculate training streak (consecutive days with any activity)
    training_streak = 0
    expected_date = date.today()
    for metric in metrics:
        if metric.date == expected_date:
            training_streak += 1
            expected_date -= timedelta(days=1)
        else:
            break
    
    # Calculate badges
    badges = []
    
    # 7-day sit streak badge
    if sit_streak >= 7:
        badges.append(Badge(
            id="sit_streak_7",
            name="Sit Master",
            description="7 consecutive days with 5+ sits",
            earned_date=metrics[0].date,
            icon="🏆"
        ))
    
    # 5 perfect recall days badge
    perfect_recall_days = sum(1 for m in metrics if m.fetch_success_count >= 5)
    if perfect_recall_days >= 5:
        badges.append(Badge(
            id="perfect_recall_5",
            name="Recall Champion",
            description="5 days with 5+ successful recalls",
            earned_date=metrics[0].date,
            icon="🎯"
        ))
    
    # Training dedication badge (30-day streak)
    if training_streak >= 30:
        badges.append(Badge(
            id="training_streak_30",
            name="Dedicated Trainer",
            description="30 consecutive days of training",
            earned_date=metrics[0].date,
            icon="⭐"
        ))
    
    # Calm companion badge (7 days with 30+ calm minutes)
    calm_days = sum(1 for m in metrics[:7] if m.calm_minutes >= 30)
    if calm_days >= 7:
        badges.append(Badge(
            id="calm_companion_7",
            name="Calm Companion",
            description="7 days with 30+ calm minutes",
            earned_date=metrics[0].date,
            icon="😌"
        ))
    
    return StreaksResponse(
        sit_streak=sit_streak,
        recall_streak=recall_streak,
        training_streak=training_streak,
        badges=badges
    )


@router.get("/hourly")
async def get_hourly_metrics(
    target_date: date = Query(..., description="Date to get hourly breakdown"),
    user_id: UUID = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Get hourly breakdown of events for a specific date.
    
    Returns sit/stand/lie counts bucketed by hour.
    """
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())
    
    # Query events for the day
    events = db.query(Event).filter(
        and_(
            Event.user_id == user_id,
            Event.ts >= start_of_day,
            Event.ts <= end_of_day,
            Event.type.in_(["sit", "stand", "lie", "bark"])
        )
    ).all()
    
    # Bucket events by hour
    hourly_buckets = {hour: {"sit": 0, "stand": 0, "lie": 0, "bark": 0} for hour in range(24)}
    
    for event in events:
        hour = event.ts.hour
        event_type = event.type
        if event_type in hourly_buckets[hour]:
            hourly_buckets[hour][event_type] += 1
    
    # Convert to list format
    hourly_data = [
        {
            "hour": hour,
            "sit_count": counts["sit"],
            "stand_count": counts["stand"],
            "lie_count": counts["lie"],
            "bark_count": counts["bark"]
        }
        for hour, counts in sorted(hourly_buckets.items())
    ]
    
    return {"date": target_date, "hourly_data": hourly_data}


@router.get("/summary")
async def get_analytics_summary(
    user_id: UUID = Query(..., description="User ID"),
    days: int = Query(7, description="Number of days to include in summary"),
    db: Session = Depends(get_db)
):
    """
    Get analytics summary for the last N days.
    
    Includes:
    - Total counts for all metrics
    - Best training hour
    - Reinforcement ratio
    - Trends
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    
    # Get metrics for date range
    metrics = db.query(AIMetricsDaily).filter(
        and_(
            AIMetricsDaily.user_id == user_id,
            AIMetricsDaily.date >= start_date,
            AIMetricsDaily.date <= end_date
        )
    ).order_by(AIMetricsDaily.date).all()
    
    if not metrics:
        return {
            "total_sits": 0,
            "total_fetches": 0,
            "total_time_in_frame": 0,
            "best_training_hour": None,
            "reinforcement_ratio": 0,
            "trends": {}
        }
    
    # Calculate totals
    total_sits = sum(m.sit_count for m in metrics)
    total_stands = sum(m.stand_count for m in metrics)
    total_lies = sum(m.lie_count for m in metrics)
    total_fetches = sum(m.fetch_count for m in metrics)
    total_fetch_successes = sum(m.fetch_success_count for m in metrics)
    total_time_in_frame = sum(m.time_in_frame_min for m in metrics)
    total_calm_minutes = sum(m.calm_minutes for m in metrics)
    
    # Calculate best training hour
    # Query events to find which hour has most training activity
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    hourly_activity = db.query(
        func.extract('hour', Event.ts).label('hour'),
        func.count(Event.id).label('count')
    ).filter(
        and_(
            Event.user_id == user_id,
            Event.ts >= start_datetime,
            Event.ts <= end_datetime,
            Event.type.in_(["sit", "stand", "lie", "fetch_return"])
        )
    ).group_by('hour').order_by(func.count(Event.id).desc()).first()
    
    best_training_hour = int(hourly_activity.hour) if hourly_activity else None
    
    # Calculate reinforcement ratio (successful responses / total cues)
    # Assume cues are sit/stand/lie commands, responses are the actions
    total_cues = total_sits + total_stands + total_lies
    reinforcement_ratio = (total_cues / max(total_cues, 1)) if total_cues > 0 else 0
    
    # Calculate trends (compare first half vs second half of period)
    mid_point = len(metrics) // 2
    first_half = metrics[:mid_point] if mid_point > 0 else []
    second_half = metrics[mid_point:] if mid_point > 0 else metrics
    
    def avg_metric(metric_list, attr):
        if not metric_list:
            return 0
        return sum(getattr(m, attr) for m in metric_list) / len(metric_list)
    
    trends = {
        "sit_trend": avg_metric(second_half, "sit_count") - avg_metric(first_half, "sit_count"),
        "fetch_trend": avg_metric(second_half, "fetch_success_count") - avg_metric(first_half, "fetch_success_count"),
        "calm_trend": avg_metric(second_half, "calm_minutes") - avg_metric(first_half, "calm_minutes")
    }
    
    return {
        "total_sits": total_sits,
        "total_stands": total_stands,
        "total_lies": total_lies,
        "total_fetches": total_fetches,
        "total_fetch_successes": total_fetch_successes,
        "total_time_in_frame": total_time_in_frame,
        "total_calm_minutes": total_calm_minutes,
        "best_training_hour": best_training_hour,
        "reinforcement_ratio": reinforcement_ratio,
        "trends": trends,
        "date_range": {
            "start": start_date,
            "end": end_date,
            "days": days
        }
    }
