/**
 * Backend API Response Type Definitions
 * 
 * Types that match the structure of responses from the FastAPI backend
 */

// ============================================================================
// Backend Event Types
// ============================================================================

export interface BackendEvent {
  id: string;
  user_id: string;
  ts: string;
  type: string;
  data: Record<string, any> | null;
  video_ts_ms: number | null;
  created_at: string;
}

export interface BackendEventsResponse {
  events: BackendEvent[];
  total: number;
  limit: number;
  offset: number;
}

// ============================================================================
// Backend Routine Types
// ============================================================================

export interface BackendRoutineStep {
  type: string;
  duration?: number;
  params?: Record<string, any>;
}

export interface BackendRoutine {
  id: string;
  user_id: string;
  name: string;
  cron: string;
  steps: BackendRoutineStep[];
  enabled: boolean;
  last_run?: string | null;
  created_at: string;
  updated_at: string;
}

// Backend returns array directly, not wrapped in object
export type BackendRoutinesResponse = BackendRoutine[];

// ============================================================================
// Backend Analytics Types
// ============================================================================

export interface BackendDailyMetrics {
  date: string;
  sit_count: number;
  stand_count: number;
  lie_count: number;
  fetch_count: number;
  fetch_success_count: number;
  treats_dispensed: number;
  time_in_frame_min: number;
  barks: number;
  howls: number;
  whines: number;
  calm_minutes: number;
}

export interface BackendHourlyData {
  hour: string;
  time_in_frame_min: number;
  barks: number;
  howls: number;
  whines: number;
}

export interface BackendBadge {
  id: string;
  name: string;
  description: string;
  earned_date: string;
  icon: string;
}

export interface BackendStreaksResponse {
  sit_streak: number;
  recall_streak: number;
  training_streak: number;
  badges: BackendBadge[];
}

export interface BackendAnalyticsSummary {
  total_events: number;
  total_training_time_min: number;
  most_common_behavior: string;
  daily_metrics: BackendDailyMetrics[];
  hourly_data: BackendHourlyData[];
  streaks: BackendStreaksResponse;
}

// ============================================================================
// Backend Media Types
// ============================================================================

export type BackendClipStatus = 'pending' | 'processing' | 'completed' | 'error';

export interface BackendClip {
  id: string;
  user_id: string;
  start_ts: string;
  duration_ms: number;
  s3_uri: string | null;
  video_url: string | null;  // Presigned URL for video download
  preview_url: string | null;
  labels: string[] | null;
  share_token: string | null;
  share_url: string | null;
  status: BackendClipStatus;
  created_at: string;
}

export interface BackendSnapshot {
  id: string;
  user_id: string;
  ts: string;
  s3_uri: string;
  preview_url: string;
  labels: string[] | null;
  note: string | null;
  created_at: string;
}

export interface BackendClipsResponse {
  clips: BackendClip[];
  total: number;
  limit: number;
  offset: number;
}

export interface BackendSnapshotsResponse {
  snapshots: BackendSnapshot[];
  total: number;
  limit: number;
  offset: number;
}

// ============================================================================
// Backend System Status Types
// ============================================================================

export interface BackendSystemStatus {
  device: 'connected' | 'offline';
  video: 'mjpeg' | 'webrtc';
  fps: number;
  latencyMs: number;
  aiModels: {
    detector?: string;
    actionRecognizer?: string;
    poseEstimator?: string;
    policy?: string;
  };
  timestamp: string;
}

// ============================================================================
// Backend Models Types
// ============================================================================

export interface BackendModel {
  name: string;
  type: 'detector' | 'action_recognizer' | 'pose_estimator' | 'policy';
  version?: string;
  description?: string;
}

export interface BackendModelsListResponse {
  available_models: BackendModel[];
  active_models: {
    detector?: string;
    action_recognizer?: string;
    pose_estimator?: string;
    policy?: string;
  };
}

export interface BackendModelSwitchResponse {
  success: boolean;
  message: string;
  active_models: {
    detector?: string;
    action_recognizer?: string;
    pose_estimator?: string;
    policy?: string;
  };
}

// ============================================================================
// Backend AI Coach Types
// ============================================================================

export interface BackendCoachRequest {
  message: string;
  context?: string;
}

export interface BackendCoachResponse {
  response: string;
  timestamp: string;
}

// ============================================================================
// Backend Robot Control Types
// ============================================================================

export interface BackendRobotActionRequest {
  action: 'pet' | 'treat' | 'fetch' | 'play';
  params?: Record<string, any>;
}

export interface BackendRobotActionResponse {
  success: boolean;
  message: string;
  action: string;
}

// ============================================================================
// Backend Error Response
// ============================================================================

export interface BackendErrorResponse {
  detail: string;
  status_code?: number;
  errors?: Array<{
    loc: string[];
    msg: string;
    type: string;
  }>;
}
