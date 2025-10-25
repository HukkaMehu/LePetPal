"""
Routine scheduler worker.

This worker checks for scheduled routines and sends notifications when routine time arrives.
Stores routine execution history.

Requirements: 8.4
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID
from croniter import croniter

from app.db.base import SessionLocal
from app.models.routine import Routine
from app.models.event import Event
from app.core.events import broadcast_event


class RoutineScheduler:
    """
    Background worker that checks for scheduled routines and triggers notifications.
    """
    
    def __init__(self):
        self.running = False
        self.check_interval = 60  # Check every minute
        self.last_check_times: Dict[str, datetime] = {}  # Track last execution per routine
        
    async def start(self):
        """Start the routine scheduler."""
        self.running = True
        asyncio.create_task(self._scheduler_loop())
        print("Routine scheduler started")
        
    async def stop(self):
        """Stop the routine scheduler."""
        self.running = False
        print("Routine scheduler stopped")
        
    async def _scheduler_loop(self):
        """Main scheduler loop that runs every minute."""
        while self.running:
            try:
                await self.check_routines()
            except Exception as e:
                print(f"Error in routine scheduler: {e}")
            
            await asyncio.sleep(self.check_interval)
    
    async def check_routines(self):
        """
        Check all enabled routines and trigger notifications for those that should run now.
        """
        db = SessionLocal()
        try:
            # Get all enabled routines
            routines = db.query(Routine).filter(Routine.enabled == True).all()
            
            current_time = datetime.utcnow()
            
            for routine in routines:
                await self._check_routine(db, routine, current_time)
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            print(f"Error checking routines: {e}")
            raise
        finally:
            db.close()
    
    async def _check_routine(self, db: Session, routine: Routine, current_time: datetime):
        """
        Check if a routine should be triggered now.
        
        Args:
            db: Database session
            routine: Routine to check
            current_time: Current UTC time
        """
        routine_id = str(routine.id)
        
        # Get last check time for this routine
        last_check = self.last_check_times.get(routine_id)
        
        # If this is the first check, initialize with current time minus check interval
        if last_check is None:
            last_check = current_time - timedelta(seconds=self.check_interval)
            self.last_check_times[routine_id] = last_check
        
        try:
            # Parse cron expression
            cron = croniter(routine.cron, last_check)
            
            # Get next scheduled time after last check
            next_run = cron.get_next(datetime)
            
            # Check if next run time is between last check and now
            if last_check < next_run <= current_time:
                # Routine should be triggered
                await self._trigger_routine(db, routine, next_run)
                
                # Update last check time to current time
                self.last_check_times[routine_id] = current_time
            else:
                # Update last check time
                self.last_check_times[routine_id] = current_time
                
        except Exception as e:
            print(f"Error checking routine {routine.name} (ID: {routine_id}): {e}")
    
    async def _trigger_routine(self, db: Session, routine: Routine, scheduled_time: datetime):
        """
        Trigger a routine by sending notification and logging execution.
        
        Args:
            db: Database session
            routine: Routine to trigger
            scheduled_time: Scheduled execution time
        """
        print(f"Triggering routine: {routine.name} (scheduled for {scheduled_time})")
        
        # Create routine execution event
        event = Event(
            user_id=routine.user_id,
            ts=datetime.utcnow(),
            type="routine_scheduled",
            data={
                "routine_id": str(routine.id),
                "routine_name": routine.name,
                "scheduled_time": scheduled_time.isoformat(),
                "steps": routine.steps,
                "step_count": len(routine.steps)
            }
        )
        db.add(event)
        
        # Broadcast notification to WebSocket clients
        await broadcast_event("routine_notification", {
            "routine_id": str(routine.id),
            "routine_name": routine.name,
            "scheduled_time": scheduled_time.isoformat(),
            "steps": routine.steps,
            "message": f"Time for routine: {routine.name}",
            "step_count": len(routine.steps)
        })
        
        print(f"Routine notification sent: {routine.name}")
    
    async def get_next_run_times(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the next scheduled run times for all enabled routines.
        
        Args:
            limit: Maximum number of upcoming runs to return per routine
            
        Returns:
            List of dicts with routine info and next run times
        """
        db = SessionLocal()
        try:
            routines = db.query(Routine).filter(Routine.enabled == True).all()
            
            result = []
            current_time = datetime.utcnow()
            
            for routine in routines:
                try:
                    cron = croniter(routine.cron, current_time)
                    next_runs = []
                    
                    for _ in range(limit):
                        next_run = cron.get_next(datetime)
                        next_runs.append(next_run.isoformat())
                    
                    result.append({
                        "routine_id": str(routine.id),
                        "routine_name": routine.name,
                        "cron": routine.cron,
                        "next_runs": next_runs
                    })
                except Exception as e:
                    print(f"Error calculating next runs for routine {routine.name}: {e}")
            
            return result
            
        finally:
            db.close()
    
    async def trigger_routine_manually(self, routine_id: UUID):
        """
        Manually trigger a routine (for testing or immediate execution).
        
        Args:
            routine_id: ID of routine to trigger
        """
        db = SessionLocal()
        try:
            routine = db.query(Routine).filter(Routine.id == routine_id).first()
            
            if not routine:
                raise ValueError(f"Routine not found: {routine_id}")
            
            await self._trigger_routine(db, routine, datetime.utcnow())
            db.commit()
            
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()


# Global routine scheduler instance
routine_scheduler = RoutineScheduler()
