/**
 * Frontend Type Definitions
 * 
 * Core types used throughout the Pet Training Web App frontend
 */

// ============================================================================
// Event Types
// ============================================================================

export type EventType = 
  | 'sit' 
  | 'fetch' 
  | 'treat' 
  | 'bark' 
  | 'pet' 
  | 'active' 
  | 'calm' 
  | 'stand' 
  | 'lie';

export interface Event {
  id: string;
  type: EventType;
  timestamp: Date;
  thumbnail?: string;
  confidence?: number;
  duration?: number;
}

// ============================================================================
// Media Types
// ============================================================================

export type MediaType = 'snapshot' | 'clip';

export interface MediaItem {
  id: string;
  type: MediaType;
  url: string;
  thumbnail: string;
  timestamp: Date;
  duration?: number;
  tags: string[];
  events: Event[];
}

// ============================================================================
// Analytics Types
// ============================================================================

export interface TimeInFrameData {
  hour: string;
  minutes: number;
}

export interface ActivityLevelData {
  date: string;
  calm: number;
  active: number;
}

export interface BehaviorData {
  name: string;
  count: number;
}

export interface FetchSuccessData {
  date: string;
  success: number;
  total: number;
}

export interface BarkFrequencyData {
  hour: string;
  count: number;
}

export interface SkillProgressData {
  skill: string;
  success: number;
  total: number;
}

export interface AnalyticsData {
  timeInFrame: TimeInFrameData[];
  activityLevel: ActivityLevelData[];
  behaviors: BehaviorData[];
  fetchSuccess: FetchSuccessData[];
  barkFrequency: BarkFrequencyData[];
  skillProgress: SkillProgressData[];
}

// ============================================================================
// Routine Types
// ============================================================================

export type RoutineActionType = 
  | 'pet' 
  | 'treat' 
  | 'play' 
  | 'sit-drill' 
  | 'wait' 
  | 'fetch';

export interface RoutineStep {
  id: string;
  action: RoutineActionType;
  duration?: number;
  repeat?: number;
}

export interface Routine {
  id: string;
  name: string;
  steps: RoutineStep[];
  schedule?: string;
  enabled: boolean;
  lastRun?: Date;
}

// ============================================================================
// System Status Types
// ============================================================================

export type DeviceStatus = 'connected' | 'offline';
export type VideoStreamType = 'webrtc' | 'mjpeg';

export interface AIModels {
  detector?: string;
  actionRecognizer?: string;
  poseEstimator?: string;
  policy?: string;
}

export interface SystemStatus {
  device: DeviceStatus;
  video: VideoStreamType;
  fps: number;
  latencyMs: number;
  aiModels: AIModels;
  timestamp: string;
}

export interface TelemetryData {
  fps?: number;
  latencyMs?: number;
  cpuUsage?: number;
  memoryUsage?: number;
  timestamp: string;
}

// ============================================================================
// API Query Parameters
// ============================================================================

export interface EventQueryParams {
  startDate?: string;
  endDate?: string;
  eventType?: EventType;
  limit?: number;
  offset?: number;
}

export interface MediaQueryParams {
  type?: MediaType;
  startDate?: string;
  endDate?: string;
  tags?: string[];
  limit?: number;
  offset?: number;
}

export interface MetricsQueryParams {
  startDate?: string;
  endDate?: string;
  days?: number;
  userId?: string;
}

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface EventCreate {
  type: EventType;
  timestamp?: Date;
  data?: Record<string, any>;
}

export interface RoutineCreate {
  name: string;
  steps: Omit<RoutineStep, 'id'>[];
  schedule?: string;
  enabled?: boolean;
}

export interface RoutineUpdate {
  name?: string;
  steps?: Omit<RoutineStep, 'id'>[];
  schedule?: string;
  enabled?: boolean;
}

export interface SnapshotCreate {
  timestamp?: Date;
  note?: string;
}

export interface ModelSwitchRequest {
  detector?: string;
  actionRecognizer?: string;
  poseEstimator?: string;
  policy?: string;
}

// ============================================================================
// WebSocket Message Types
// ============================================================================

export type WebSocketMessageType = 'event' | 'overlay' | 'telemetry' | 'routine' | 'ai_detections';

export interface WebSocketMessage {
  type: WebSocketMessageType;
  event_type?: string;
  overlay_type?: string;
  timestamp?: number;
  data: any;
}

// ============================================================================
// AI Detection Types
// ============================================================================

export interface BoundingBox {
  x: number;  // normalized 0-1
  y: number;  // normalized 0-1
  w: number;  // normalized 0-1
  h: number;  // normalized 0-1
}

export interface Detection {
  class_name: string;
  confidence: number;
  box: BoundingBox;
}

export interface Keypoint {
  name: string;
  x: number;
  y: number;
  confidence: number;
}

export interface Action {
  label: string;
  probability: number;
}

export interface ObjectDetection {
  class_name: string;
  confidence: number;
  box: BoundingBox;
}

export interface AIDetectionData {
  detections: Detection[];
  keypoints?: Keypoint[];
  actions?: Action[];
  objects?: ObjectDetection[];
}

// ============================================================================
// Error Types
// ============================================================================

export class APIError extends Error {
  constructor(
    public status: number,
    message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}
