/**
 * Data Adapter Functions
 * 
 * Transform backend data formats to match frontend expectations.
 * These adapters ensure compatibility between the backend API responses
 * and the frontend component data structures.
 */

import {
  Event,
  EventType,
  MediaItem,
  Routine,
  RoutineStep,
  RoutineActionType,
  SystemStatus,
  DeviceStatus,
  VideoStreamType,
  AnalyticsData,
  TimeInFrameData,
  ActivityLevelData,
  BehaviorData,
  FetchSuccessData,
  BarkFrequencyData,
  SkillProgressData,
} from '../types';
import {
  BackendEvent,
  BackendRoutine,
  BackendRoutineStep,
  BackendClip,
  BackendSnapshot,
  BackendSystemStatus,
  BackendDailyMetrics,
  BackendHourlyData,
  BackendAnalyticsSummary,
  BackendStreaksResponse,
} from '../types/backend';

// ============================================================================
// Event Adapters
// ============================================================================

/**
 * Map backend event type to frontend event type
 */
function mapEventType(backendType: string): EventType {
  const typeMap: Record<string, EventType> = {
    'sit': 'sit',
    'stand': 'stand',
    'lie': 'lie',
    'lie_down': 'lie',
    'fetch': 'fetch',
    'treat': 'treat',
    'bark': 'bark',
    'pet': 'pet',
    'active': 'active',
    'calm': 'calm',
  };

  return typeMap[backendType.toLowerCase()] || 'active';
}

/**
 * Transform backend event to frontend event format
 */
export function adaptEvent(backendEvent: BackendEvent): Event {
  return {
    id: backendEvent.id,
    type: mapEventType(backendEvent.type),
    timestamp: new Date(backendEvent.ts),
    thumbnail: backendEvent.data?.thumbnail_url,
    confidence: backendEvent.data?.confidence,
    duration: backendEvent.data?.duration_ms,
  };
}

/**
 * Transform array of backend events to frontend events
 */
export function adaptEvents(backendEvents: BackendEvent[]): Event[] {
  return backendEvents.map(adaptEvent);
}

// ============================================================================
// Routine Adapters
// ============================================================================

/**
 * Map backend routine step type to frontend action type
 */
function mapRoutineActionType(backendType: string): RoutineActionType {
  const typeMap: Record<string, RoutineActionType> = {
    'pet': 'pet',
    'treat': 'treat',
    'play': 'play',
    'sit_drill': 'sit-drill',
    'sit-drill': 'sit-drill',
    'wait': 'wait',
    'fetch': 'fetch',
  };

  return typeMap[backendType.toLowerCase()] || 'wait';
}

/**
 * Transform backend routine step to frontend routine step
 */
function adaptRoutineStep(backendStep: BackendRoutineStep, index: number): RoutineStep {
  return {
    id: `step-${index}`,
    action: mapRoutineActionType(backendStep.type),
    duration: backendStep.duration,
    repeat: backendStep.params?.repeat,
  };
}

/**
 * Transform backend routine to frontend routine format
 */
export function adaptRoutine(backendRoutine: BackendRoutine): Routine {
  return {
    id: backendRoutine.id,
    name: backendRoutine.name,
    steps: backendRoutine.steps.map((step, index) => adaptRoutineStep(step, index)),
    schedule: backendRoutine.cron,
    enabled: backendRoutine.enabled,
    lastRun: backendRoutine.last_run ? new Date(backendRoutine.last_run) : undefined,
  };
}

/**
 * Transform array of backend routines to frontend routines
 */
export function adaptRoutines(backendRoutines: BackendRoutine[]): Routine[] {
  return backendRoutines.map(adaptRoutine);
}

/**
 * Map frontend action type to backend routine step type
 */
function mapActionTypeToBackend(action: RoutineActionType): string {
  const typeMap: Record<RoutineActionType, string> = {
    'pet': 'pet',
    'treat': 'treat',
    'play': 'play',
    'sit-drill': 'sit_drill',
    'wait': 'wait',
    'fetch': 'fetch',
  };

  return typeMap[action] || 'wait';
}

/**
 * Transform frontend routine step to backend format
 */
function adaptRoutineStepToBackend(step: RoutineStep): BackendRoutineStep {
  return {
    type: mapActionTypeToBackend(step.action),
    duration: step.duration || 0,
    params: step.repeat ? { repeat: step.repeat } : undefined,
  };
}

/**
 * Transform frontend routine data to backend format for creation/update
 */
export function adaptRoutineToBackend(routine: any): any {
  return {
    name: routine.name,
    cron: routine.schedule || routine.cron,
    enabled: routine.enabled ?? true,
    steps: routine.steps.map(adaptRoutineStepToBackend),
  };
}

// ============================================================================
// Media Adapters
// ============================================================================

/**
 * Transform backend clip to frontend media item
 */
export function adaptClip(backendClip: BackendClip): MediaItem {
  return {
    id: backendClip.id,
    type: 'clip',
    url: backendClip.video_url || backendClip.preview_url || '',
    thumbnail: backendClip.preview_url || '',
    timestamp: new Date(backendClip.start_ts),
    duration: backendClip.duration_ms,
    tags: backendClip.labels || [],
    events: [], // Events can be fetched separately if needed
  };
}

/**
 * Transform backend snapshot to frontend media item
 */
export function adaptSnapshot(backendSnapshot: BackendSnapshot): MediaItem {
  return {
    id: backendSnapshot.id,
    type: 'snapshot',
    url: backendSnapshot.s3_uri || backendSnapshot.preview_url,
    thumbnail: backendSnapshot.preview_url || backendSnapshot.s3_uri,
    timestamp: new Date(backendSnapshot.ts),
    tags: backendSnapshot.labels || [],
    events: [], // Events can be fetched separately if needed
  };
}

/**
 * Transform arrays of backend clips and snapshots to frontend media items
 */
export function adaptMediaItems(
  backendClips: BackendClip[] = [],
  backendSnapshots: BackendSnapshot[] = []
): MediaItem[] {
  const clips = backendClips.map(adaptClip);
  const snapshots = backendSnapshots.map(adaptSnapshot);
  
  // Combine and sort by timestamp (newest first)
  return [...clips, ...snapshots].sort((a, b) => 
    b.timestamp.getTime() - a.timestamp.getTime()
  );
}

// ============================================================================
// System Status Adapters
// ============================================================================

/**
 * Transform backend system status to frontend system status
 */
export function adaptSystemStatus(backendStatus: BackendSystemStatus): SystemStatus {
  return {
    device: backendStatus.device,
    video: backendStatus.video,
    fps: backendStatus.fps,
    latencyMs: backendStatus.latencyMs,
    aiModels: {
      detector: backendStatus.aiModels?.detector || 'none',
      actionRecognizer: backendStatus.aiModels?.actionRecognizer || 'none',
      poseEstimator: backendStatus.aiModels?.poseEstimator || 'none',
      policy: backendStatus.aiModels?.policy || 'none',
    },
    timestamp: backendStatus.timestamp,
  };
}

// ============================================================================
// Analytics Adapters
// ============================================================================

/**
 * Transform backend hourly data to time in frame chart data
 */
function adaptTimeInFrame(hourlyData: BackendHourlyData[]): TimeInFrameData[] {
  return hourlyData.map(data => ({
    hour: data.hour,
    minutes: data.time_in_frame_min,
  }));
}

/**
 * Transform backend daily metrics to activity level chart data
 */
function adaptActivityLevel(dailyMetrics: BackendDailyMetrics[]): ActivityLevelData[] {
  return dailyMetrics.map(metrics => ({
    date: metrics.date,
    calm: metrics.calm_minutes,
    active: metrics.time_in_frame_min - metrics.calm_minutes,
  }));
}

/**
 * Transform backend daily metrics to behavior count data
 */
function adaptBehaviors(dailyMetrics: BackendDailyMetrics[]): BehaviorData[] {
  // Aggregate behavior counts across all days
  const totals = dailyMetrics.reduce(
    (acc, metrics) => ({
      sit: acc.sit + metrics.sit_count,
      stand: acc.stand + metrics.stand_count,
      lie: acc.lie + metrics.lie_count,
      fetch: acc.fetch + metrics.fetch_count,
      bark: acc.bark + metrics.barks,
    }),
    { sit: 0, stand: 0, lie: 0, fetch: 0, bark: 0 }
  );

  return [
    { name: 'Sit', count: totals.sit },
    { name: 'Stand', count: totals.stand },
    { name: 'Lie Down', count: totals.lie },
    { name: 'Fetch', count: totals.fetch },
    { name: 'Bark', count: totals.bark },
  ].filter(behavior => behavior.count > 0);
}

/**
 * Transform backend daily metrics to fetch success chart data
 */
function adaptFetchSuccess(dailyMetrics: BackendDailyMetrics[]): FetchSuccessData[] {
  return dailyMetrics.map(metrics => ({
    date: metrics.date,
    success: metrics.fetch_success_count,
    total: metrics.fetch_count,
  }));
}

/**
 * Transform backend hourly data to bark frequency chart data
 */
function adaptBarkFrequency(hourlyData: BackendHourlyData[]): BarkFrequencyData[] {
  return hourlyData.map(data => ({
    hour: data.hour,
    count: data.barks + data.howls + data.whines,
  }));
}

/**
 * Transform backend streaks to skill progress data
 */
function adaptSkillProgress(streaks: BackendStreaksResponse): SkillProgressData[] {
  return [
    {
      skill: 'Sit Command',
      success: streaks.sit_streak,
      total: Math.max(streaks.sit_streak + 3, 10), // Estimate total based on streak
    },
    {
      skill: 'Recall',
      success: streaks.recall_streak,
      total: Math.max(streaks.recall_streak + 2, 10),
    },
    {
      skill: 'Training Consistency',
      success: streaks.training_streak,
      total: Math.max(streaks.training_streak + 5, 30),
    },
  ];
}

/**
 * Transform backend analytics summary to frontend analytics data
 */
export function adaptAnalytics(backendSummary: BackendAnalyticsSummary): AnalyticsData {
  return {
    timeInFrame: adaptTimeInFrame(backendSummary.hourly_data),
    activityLevel: adaptActivityLevel(backendSummary.daily_metrics),
    behaviors: adaptBehaviors(backendSummary.daily_metrics),
    fetchSuccess: adaptFetchSuccess(backendSummary.daily_metrics),
    barkFrequency: adaptBarkFrequency(backendSummary.hourly_data),
    skillProgress: adaptSkillProgress(backendSummary.streaks),
  };
}

/**
 * Transform backend daily metrics to frontend analytics data
 * (Alternative adapter when only daily metrics are available)
 */
export function adaptAnalyticsFromMetrics(
  dailyMetrics: BackendDailyMetrics[],
  hourlyData: BackendHourlyData[] = [],
  streaks?: BackendStreaksResponse
): AnalyticsData {
  const defaultStreaks: BackendStreaksResponse = {
    sit_streak: 0,
    recall_streak: 0,
    training_streak: 0,
    badges: [],
  };

  return {
    timeInFrame: hourlyData.length > 0 ? adaptTimeInFrame(hourlyData) : [],
    activityLevel: adaptActivityLevel(dailyMetrics),
    behaviors: adaptBehaviors(dailyMetrics),
    fetchSuccess: adaptFetchSuccess(dailyMetrics),
    barkFrequency: hourlyData.length > 0 ? adaptBarkFrequency(hourlyData) : [],
    skillProgress: adaptSkillProgress(streaks || defaultStreaks),
  };
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Format date to ISO string for API requests
 */
export function formatDateForAPI(date: Date): string {
  return date.toISOString();
}

/**
 * Parse ISO date string from API response
 */
export function parseDateFromAPI(dateString: string): Date {
  return new Date(dateString);
}

/**
 * Calculate date range for analytics queries
 */
export function getDateRange(days: number): { startDate: string; endDate: string } {
  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  return {
    startDate: formatDateForAPI(startDate),
    endDate: formatDateForAPI(endDate),
  };
}
