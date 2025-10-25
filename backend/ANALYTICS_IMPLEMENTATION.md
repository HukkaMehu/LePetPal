# Analytics Implementation

This document describes the implementation of training analytics and charts (Task 11).

## Backend Components

### 1. Metrics Aggregator Worker (`app/workers/metrics_aggregator.py`)

A background worker that runs every hour to aggregate events into daily metrics.

**Features:**
- Aggregates events into `ai_metrics_daily` table
- Calculates sit/stand/lie counts
- Tracks fetch attempts and successes
- Computes time in frame based on dog detection events
- Calculates calm minutes from sit/lie events
- Runs automatically every hour for the current day
- Supports backfilling historical data

**Usage:**
```python
# Automatically started with the application
# Manual aggregation for a specific date:
await metrics_aggregator.aggregate_current_day(target_date)

# Backfill date range:
await metrics_aggregator.aggregate_date_range(start_date, end_date)
```

### 2. Analytics API Endpoints (`app/api/analytics.py`)

RESTful API endpoints for retrieving analytics data.

**Endpoints:**

#### GET `/api/analytics/daily`
Get daily metrics for a date range.

Query Parameters:
- `from_date`: Start date (YYYY-MM-DD)
- `to_date`: End date (YYYY-MM-DD)
- `user_id`: User UUID

Response:
```json
[
  {
    "date": "2025-10-25",
    "sit_count": 15,
    "stand_count": 20,
    "lie_count": 10,
    "fetch_count": 8,
    "fetch_success_count": 6,
    "treats_dispensed": 5,
    "time_in_frame_min": 120,
    "barks": 3,
    "howls": 0,
    "whines": 1,
    "calm_minutes": 45
  }
]
```

#### GET `/api/analytics/streaks`
Calculate training streaks and badges.

Query Parameters:
- `user_id`: User UUID

Response:
```json
{
  "sit_streak": 5,
  "recall_streak": 3,
  "training_streak": 7,
  "badges": [
    {
      "id": "sit_streak_7",
      "name": "Sit Master",
      "description": "7 consecutive days with 5+ sits",
      "earned_date": "2025-10-25",
      "icon": "🏆"
    }
  ]
}
```

#### GET `/api/analytics/hourly`
Get hourly breakdown of events for a specific date.

Query Parameters:
- `target_date`: Date (YYYY-MM-DD)
- `user_id`: User UUID

Response:
```json
{
  "date": "2025-10-25",
  "hourly_data": [
    {
      "hour": 0,
      "sit_count": 0,
      "stand_count": 0,
      "lie_count": 0,
      "bark_count": 0
    },
    ...
  ]
}
```

#### GET `/api/analytics/summary`
Get analytics summary for the last N days.

Query Parameters:
- `user_id`: User UUID
- `days`: Number of days (default: 7)

Response:
```json
{
  "total_sits": 105,
  "total_stands": 140,
  "total_lies": 70,
  "total_fetches": 56,
  "total_fetch_successes": 42,
  "total_time_in_frame": 840,
  "total_calm_minutes": 315,
  "best_training_hour": 14,
  "reinforcement_ratio": 0.85,
  "trends": {
    "sit_trend": 2.5,
    "fetch_trend": 1.2,
    "calm_trend": 5.0
  },
  "date_range": {
    "start": "2025-10-18",
    "end": "2025-10-25",
    "days": 7
  }
}
```

## Frontend Components

### 1. Analytics Dashboard (`components/AnalyticsDashboard.tsx`)

Main analytics dashboard with time-series visualizations using Recharts.

**Features:**
- Time in frame vs off frame area chart
- Hourly behavior counts bar chart
- Daily behavior trends line chart
- Fetch attempts vs successes bar chart
- Vocalization frequency line chart
- Date picker for hourly breakdown

**Usage:**
```tsx
import AnalyticsDashboard from "@/components/AnalyticsDashboard";

<AnalyticsDashboard 
  userId="user-uuid"
  dateRange={{ from: "2025-10-18", to: "2025-10-25" }}
/>
```

### 2. Progress Page (`components/ProgressPage.tsx`)

Training progress page with trends and correlations.

**Features:**
- Summary cards with trend indicators
- Best training hour display
- Reinforcement ratio calculation
- 7-day trendlines for key metrics
- Correlation tiles showing relationships between metrics
- Pearson correlation coefficient calculations

**Usage:**
```tsx
import ProgressPage from "@/components/ProgressPage";

<ProgressPage userId="user-uuid" days={7} />
```

### 3. Streaks and Badges (`components/StreaksAndBadges.tsx`)

Gamification component showing streaks and earned badges.

**Features:**
- Current streak cards (sit, recall, training)
- Earned badges display
- Upcoming milestones with progress bars
- Badge criteria:
  - Sit Master: 7-day sit streak
  - Recall Champion: 5 days with 5+ successful recalls
  - Dedicated Trainer: 30-day training streak
  - Calm Companion: 7 days with 30+ calm minutes

**Usage:**
```tsx
import StreaksAndBadges from "@/components/StreaksAndBadges";

<StreaksAndBadges userId="user-uuid" />
```

## Pages

### `/analytics`
Combined analytics page showing streaks, badges, and detailed charts.

### `/progress`
Progress tracking page with trends and correlations.

## Integration

The metrics aggregator is automatically started when the FastAPI application starts:

```python
# In app/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    await metrics_aggregator.start()
    yield
    await metrics_aggregator.stop()
```

The analytics router is registered with the FastAPI app:

```python
app.include_router(analytics.router)
```

## Requirements Satisfied

- **7.1**: Display time-in-frame vs off-frame metrics ✓
- **7.2**: Show sit/stand/lie counts with hourly buckets ✓
- **7.3**: Calculate and display fetch attempts vs successes ✓
- **7.4**: Track bark frequency over time ✓
- **7.5**: Provide 7-day trend analysis with best training hours ✓
- **9.1-9.4**: Training streaks and achievement badges ✓
- **11.1-11.4**: Daily metrics aggregation and analytics ✓

## Testing

To test the implementation:

1. Start the backend server
2. Generate some test events using the event processor
3. Manually trigger aggregation or wait for the hourly job
4. Access the analytics endpoints or frontend pages
5. Verify charts display correctly with real data

## Future Enhancements

- Real-time chart updates via WebSocket
- Export analytics data to CSV/PDF
- Custom date range selection
- More badge types and achievements
- Comparison with other dogs (community features)
- Training recommendations based on analytics
