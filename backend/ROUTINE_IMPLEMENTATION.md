# Routine Builder and Scheduler Implementation

## Overview

This document describes the implementation of the routine builder and scheduler feature for the dog monitoring application.

## Requirements

- **8.1**: Allow owners to create routines by dragging steps
- **8.2**: Validate cron schedule format when saving routines
- **8.3**: Store routine steps in structured format
- **8.4**: Send notifications when scheduled routine time arrives

## Backend Components

### API Endpoints (`backend/app/api/routines.py`)

- `GET /api/routines` - List all routines with optional filtering
- `POST /api/routines` - Create a new routine with cron validation
- `GET /api/routines/{id}` - Get a specific routine
- `PUT /api/routines/{id}` - Update an existing routine
- `DELETE /api/routines/{id}` - Delete a routine
- `GET /api/routines/schedule` - Get next scheduled run times for all enabled routines
- `POST /api/routines/{id}/trigger` - Manually trigger a routine

### Routine Scheduler (`backend/app/workers/routine_scheduler.py`)

Background worker that:
- Checks for scheduled routines every minute
- Uses croniter to parse cron expressions
- Triggers notifications when routine time arrives
- Logs routine execution to events table
- Broadcasts notifications via WebSocket

### Database Model (`backend/app/models/routine.py`)

```python
class Routine:
    id: UUID
    user_id: UUID
    name: str
    cron: str  # Cron expression (5 fields)
    steps: JSONB  # Array of step objects
    enabled: bool
    created_at: timestamp
    updated_at: timestamp
```

### Step Types

- `pet` - Give affection and praise
- `treat` - Dispense a treat reward
- `play` - Interactive play session
- `sit_drill` - Practice sit command
- `fetch` - Fetch training exercise
- `wait` - Pause between steps (with duration)

## Frontend Components

### RoutineBuilder (`frontend/src/components/RoutineBuilder.tsx`)

Interactive form component with:
- Routine name input
- Cron expression builder with presets
- Drag-and-drop step ordering
- Step type selector buttons
- Duration input for wait steps
- Enable/disable toggle
- Cron validation

### RoutinesList (`frontend/src/components/RoutinesList.tsx`)

List view component with:
- Filter tabs (all/enabled/disabled)
- Routine cards showing name, schedule, and steps
- Enable/disable toggle per routine
- Edit and delete actions
- Human-readable cron display

### RoutineNotification (`frontend/src/components/RoutineNotification.tsx`)

Real-time notification component that:
- Listens for routine_notification events via WebSocket
- Displays notification banner with routine details
- Shows step preview
- Provides "Start Routine" and "Dismiss" actions

### Routines Page (`frontend/src/app/routines/page.tsx`)

Main page that:
- Shows create button
- Displays RoutineBuilder when creating/editing
- Shows RoutinesList when not editing
- Handles save/cancel actions
- Integrates RoutineNotification component

## Cron Expression Format

Format: `minute hour day month weekday`

Examples:
- `0 9 * * *` - Daily at 9:00 AM
- `0 */2 * * *` - Every 2 hours
- `0 8 * * 1-5` - Weekdays at 8:00 AM
- `0 10 * * 0,6` - Weekends at 10:00 AM

## WebSocket Events

### routine_notification

Sent when a routine's scheduled time arrives:

```json
{
  "type": "event",
  "data": {
    "event_type": "routine_notification",
    "data": {
      "routine_id": "uuid",
      "routine_name": "Morning Training",
      "scheduled_time": "2025-10-25T09:00:00Z",
      "steps": [...],
      "message": "Time for routine: Morning Training",
      "step_count": 5
    }
  }
}
```

### routine_scheduled

Logged to events table when routine is triggered:

```json
{
  "type": "routine_scheduled",
  "data": {
    "routine_id": "uuid",
    "routine_name": "Morning Training",
    "scheduled_time": "2025-10-25T09:00:00Z",
    "steps": [...],
    "step_count": 5
  }
}
```

## Usage

### Creating a Routine

1. Navigate to `/routines` page
2. Click "Create New Routine"
3. Enter routine name
4. Set cron schedule (or use preset)
5. Add steps by clicking step type buttons
6. Drag steps to reorder
7. Set duration for wait steps
8. Enable/disable routine
9. Click "Create Routine"

### Editing a Routine

1. Click edit button on routine card
2. Modify fields as needed
3. Click "Update Routine"

### Manual Trigger

Use the API endpoint for testing:

```bash
curl -X POST http://localhost:8000/api/routines/{routine_id}/trigger
```

## Dependencies

- `croniter==2.0.5` - Cron expression parsing and scheduling

## Future Enhancements

- Routine execution tracking (success/failure)
- Routine templates
- Step parameters customization
- Routine history and analytics
- Robot integration for automatic step execution
