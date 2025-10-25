"""
Daily metrics aggregation worker.

This worker aggregates events into the ai_metrics_daily table.
Calculates sit/stand/lie counts, fetch attempts/successes, time in frame, calm minutes.
Runs every hour for the current day.

Requirements: 7.1, 7.2, 7.3, 7.4, 11.1, 11.2, 11.3, 11.4
"""
import asyncio
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from uuid import UUID

from app.db.base import SessionLocal
from app.models.event import Event
from app.models.ai_metrics_daily import AIMetricsDaily


class MetricsAggregator:
    """
    Background worker that aggregates events into daily metrics.
    """
    
    def __init__(self):
        self.running = False
        self.aggregation_interval = 3600  # Run every hour (3600 seconds)
        
    async def start(self):
        """Start the metrics aggregator."""
        self.running = True
        asyncio.create_task(self._aggregation_loop())
        
    async def stop(self):
        """Stop the metrics aggregator."""
        self.running = False
        
    async def _aggregation_loop(self):
        """Main aggregation loop that runs every hour."""
        while self.running:
            try:
                await self.aggregate_current_day()
            except Exception as e:
                print(f"Error in metrics aggregation: {e}")
            
            await asyncio.sleep(self.aggregation_interval)
    
    async def aggregate_current_day(self, target_date: Optional[date] = None):
        """
        Aggregate events for the current day (or specified date) into ai_metrics_daily.
        
        Args:
            target_date: Date to aggregate. Defaults to today.
        """
        if target_date is None:
            target_date = date.today()
        
        db = SessionLocal()
        try:
            # Get all users who have events on this date
            start_of_day = datetime.combine(target_date, datetime.min.time())
            end_of_day = datetime.combine(target_date, datetime.max.time())
            
            # Query distinct user_ids with events on this date
            user_ids = db.query(Event.user_id).filter(
                and_(
                    Event.ts >= start_of_day,
                    Event.ts <= end_of_day
                )
            ).distinct().all()
            
            for (user_id,) in user_ids:
                await self._aggregate_user_day(db, user_id, target_date, start_of_day, end_of_day)
            
            db.commit()
            print(f"Aggregated metrics for {len(user_ids)} users on {target_date}")
            
        except Exception as e:
            db.rollback()
            print(f"Error aggregating metrics: {e}")
            raise
        finally:
            db.close()
    
    async def _aggregate_user_day(
        self,
        db: Session,
        user_id: UUID,
        target_date: date,
        start_of_day: datetime,
        end_of_day: datetime
    ):
        """
        Aggregate metrics for a single user on a single day.
        """
        # Query all events for this user on this day
        events = db.query(Event).filter(
            and_(
                Event.user_id == user_id,
                Event.ts >= start_of_day,
                Event.ts <= end_of_day
            )
        ).all()
        
        # Initialize metrics
        metrics = {
            "sit_count": 0,
            "stand_count": 0,
            "lie_count": 0,
            "fetch_count": 0,
            "fetch_success_count": 0,
            "treats_dispensed": 0,
            "time_in_frame_min": 0,
            "barks": 0,
            "howls": 0,
            "whines": 0,
            "calm_minutes": 0
        }
        
        # Track time in frame
        dog_detected_events = []
        
        # Process events
        for event in events:
            event_type = event.type
            
            # Count actions
            if event_type == "sit":
                metrics["sit_count"] += 1
            elif event_type == "stand":
                metrics["stand_count"] += 1
            elif event_type == "lie":
                metrics["lie_count"] += 1
            elif event_type == "fetch_return":
                metrics["fetch_count"] += 1
                metrics["fetch_success_count"] += 1
            elif event_type == "approach" and event.data and event.data.get("action") == "fetch":
                # Count fetch attempts (approach with fetch intent)
                metrics["fetch_count"] += 1
            elif event_type == "bark":
                metrics["barks"] += 1
            elif event_type == "howl":
                metrics["howls"] += 1
            elif event_type == "whine":
                metrics["whines"] += 1
            elif event_type == "dog_detected":
                dog_detected_events.append(event)
            elif event_type == "treat_dispensed":
                metrics["treats_dispensed"] += 1
        
        # Calculate time in frame (minutes)
        # Estimate based on dog_detected events
        # Assume each detection represents ~1 second of presence
        if dog_detected_events:
            # Group detections into continuous presence periods
            # If detections are within 5 seconds of each other, consider them continuous
            dog_detected_events.sort(key=lambda e: e.ts)
            
            total_seconds = 0
            last_ts = None
            
            for event in dog_detected_events:
                if last_ts is None:
                    total_seconds += 1
                else:
                    time_diff = (event.ts - last_ts).total_seconds()
                    if time_diff <= 5:
                        # Continuous presence
                        total_seconds += time_diff
                    else:
                        # Gap in presence, just count this detection
                        total_seconds += 1
                last_ts = event.ts
            
            metrics["time_in_frame_min"] = int(total_seconds / 60)
        
        # Calculate calm minutes
        # Calm periods are when dog is in frame but no high-activity actions
        # (no fetch, no bark, just sitting/lying)
        calm_events = [e for e in events if e.type in ["sit", "lie"]]
        if calm_events:
            # Estimate calm time based on sit/lie events
            # Assume each sit/lie event represents ~30 seconds of calm behavior
            metrics["calm_minutes"] = int(len(calm_events) * 0.5)
        
        # Upsert metrics into ai_metrics_daily
        existing_metric = db.query(AIMetricsDaily).filter(
            and_(
                AIMetricsDaily.user_id == user_id,
                AIMetricsDaily.date == target_date
            )
        ).first()
        
        if existing_metric:
            # Update existing record
            for key, value in metrics.items():
                setattr(existing_metric, key, value)
            existing_metric.updated_at = datetime.utcnow()
        else:
            # Create new record
            new_metric = AIMetricsDaily(
                user_id=user_id,
                date=target_date,
                **metrics
            )
            db.add(new_metric)
    
    async def aggregate_date_range(self, start_date: date, end_date: date):
        """
        Aggregate metrics for a range of dates.
        Useful for backfilling historical data.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
        """
        current_date = start_date
        while current_date <= end_date:
            await self.aggregate_current_day(current_date)
            current_date += timedelta(days=1)


# Global metrics aggregator instance
metrics_aggregator = MetricsAggregator()
