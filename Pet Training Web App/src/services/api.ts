/**
 * API Client Service
 * 
 * Centralized service for all backend API communication.
 * Includes error handling, retry logic, and request/response interceptors.
 */

import { config } from '../config/env';
import {
  Event,
  EventCreate,
  EventQueryParams,
  Routine,
  RoutineCreate,
  RoutineUpdate,
  MediaQueryParams,
  MetricsQueryParams,
  SnapshotCreate,
  ModelSwitchRequest,
  APIError,
} from '../types';
import { adaptRoutineToBackend } from './adapters';
import {
  BackendEventsResponse,
  BackendRoutinesResponse,
  BackendDailyMetrics,
  BackendStreaksResponse,
  BackendAnalyticsSummary,
  BackendClipsResponse,
  BackendSnapshotsResponse,
  BackendSystemStatus,
  BackendModelsListResponse,
  BackendModelSwitchResponse,
  BackendCoachResponse,
  BackendRobotActionResponse,
  BackendErrorResponse,
} from '../types/backend';

// ============================================================================
// Configuration
// ============================================================================

interface RetryConfig {
  maxRetries: number;
  initialDelayMs: number;
  maxDelayMs: number;
  backoffMultiplier: number;
}

const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  initialDelayMs: 1000,
  maxDelayMs: 10000,
  backoffMultiplier: 2,
};

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Sleep for a specified duration
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Calculate exponential backoff delay
 */
function calculateBackoff(attempt: number, config: RetryConfig): number {
  const delay = config.initialDelayMs * Math.pow(config.backoffMultiplier, attempt);
  return Math.min(delay, config.maxDelayMs);
}

/**
 * Determine if an error is retryable
 */
function isRetryableError(status: number): boolean {
  // Retry on network errors, server errors, and rate limiting
  return status === 0 || status === 429 || (status >= 500 && status < 600);
}

/**
 * Build query string from parameters
 */
function buildQueryString(params: Record<string, any>): string {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      if (Array.isArray(value)) {
        value.forEach(v => searchParams.append(key, String(v)));
      } else {
        searchParams.append(key, String(value));
      }
    }
  });

  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : '';
}

// ============================================================================
// API Client Class
// ============================================================================

export class APIClient {
  private baseURL: string;
  private aiServiceURL: string;
  private retryConfig: RetryConfig;

  constructor(
    baseURL: string = config.apiBaseURL,
    aiServiceURL: string = config.aiServiceURL,
    retryConfig: RetryConfig = DEFAULT_RETRY_CONFIG
  ) {
    this.baseURL = baseURL.replace(/\/$/, ''); // Remove trailing slash
    this.aiServiceURL = aiServiceURL.replace(/\/$/, '');
    this.retryConfig = retryConfig;
  }

  // ==========================================================================
  // Core Request Methods
  // ==========================================================================

  /**
   * Make an HTTP request with retry logic and error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    useAIService: boolean = false
  ): Promise<T> {
    const baseURL = useAIService ? this.aiServiceURL : this.baseURL;
    const url = `${baseURL}${endpoint}`;

    // Request interceptor - log request
    if (config.debug) {
      console.log(`[API Request] ${options.method || 'GET'} ${url}`, {
        body: options.body,
        headers: options.headers,
      });
    }

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= this.retryConfig.maxRetries; attempt++) {
      try {
        const response = await fetch(url, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...options.headers,
          },
        });

        // Response interceptor - log response
        if (config.debug) {
          console.log(`[API Response] ${response.status} ${url}`);
        }

        // Handle error responses
        if (!response.ok) {
          const error = await this.handleErrorResponse(response);

          // Retry if error is retryable and we have attempts left
          if (isRetryableError(response.status) && attempt < this.retryConfig.maxRetries) {
            const delay = calculateBackoff(attempt, this.retryConfig);
            console.warn(
              `[API Retry] Attempt ${attempt + 1}/${this.retryConfig.maxRetries} ` +
              `failed with status ${response.status}. Retrying in ${delay}ms...`
            );
            await sleep(delay);
            continue;
          }

          throw error;
        }

        // Parse successful response
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          return await response.json();
        }

        // Return empty object for non-JSON responses (e.g., 204 No Content)
        return {} as T;

      } catch (error) {
        lastError = error as Error;

        // If it's an APIError, don't retry
        if (error instanceof APIError) {
          throw error;
        }

        // Network error - retry if we have attempts left
        if (attempt < this.retryConfig.maxRetries) {
          const delay = calculateBackoff(attempt, this.retryConfig);
          console.warn(
            `[API Retry] Network error on attempt ${attempt + 1}/${this.retryConfig.maxRetries}. ` +
            `Retrying in ${delay}ms...`
          );
          await sleep(delay);
          continue;
        }
      }
    }

    // All retries exhausted
    throw new APIError(
      0,
      `Request failed after ${this.retryConfig.maxRetries} retries: ${lastError?.message}`,
      { originalError: lastError }
    );
  }

  /**
   * Handle error responses from the API
   */
  private async handleErrorResponse(response: Response): Promise<APIError> {
    let errorData: BackendErrorResponse | null = null;

    try {
      errorData = await response.json();
    } catch {
      // Failed to parse error response
    }

    // Handle different error formats
    let message: string;

    if (errorData?.detail) {
      // FastAPI validation errors return detail as an array
      if (Array.isArray(errorData.detail)) {
        message = errorData.detail
          .map((err: any) => `${err.loc?.join('.') || 'field'}: ${err.msg}`)
          .join(', ');
      } else if (typeof errorData.detail === 'string') {
        message = errorData.detail;
      } else {
        message = JSON.stringify(errorData.detail);
      }
    } else {
      message = response.statusText || 'An error occurred';
    }

    return new APIError(response.status, message, errorData);
  }

  // ==========================================================================
  // Events API
  // ==========================================================================

  /**
   * Get events with optional filtering
   */
  async getEvents(params: EventQueryParams = {}): Promise<BackendEventsResponse> {
    const queryString = buildQueryString(params);
    return this.request<BackendEventsResponse>(`/events${queryString}`);
  }

  /**
   * Create a new event
   */
  async createEvent(event: EventCreate): Promise<Event> {
    return this.request<Event>('/events', {
      method: 'POST',
      body: JSON.stringify(event),
    });
  }

  // ==========================================================================
  // Routines API
  // ==========================================================================

  /**
   * Get all routines
   */
  async getRoutines(): Promise<BackendRoutinesResponse> {
    // Backend returns array directly
    return this.request<BackendRoutinesResponse>('/routines');
  }

  /**
   * Create a new routine
   */
  async createRoutine(routine: RoutineCreate): Promise<Routine> {
    const backendRoutine = adaptRoutineToBackend(routine);
    return this.request<Routine>('/routines', {
      method: 'POST',
      body: JSON.stringify(backendRoutine),
    });
  }

  /**
   * Update an existing routine
   */
  async updateRoutine(id: string, routine: RoutineUpdate): Promise<Routine> {
    const backendRoutine = adaptRoutineToBackend(routine);
    return this.request<Routine>(`/routines/${id}`, {
      method: 'PUT',
      body: JSON.stringify(backendRoutine),
    });
  }

  /**
   * Delete a routine
   */
  async deleteRoutine(id: string): Promise<void> {
    return this.request<void>(`/routines/${id}`, {
      method: 'DELETE',
    });
  }

  /**
   * Trigger a routine manually
   */
  async triggerRoutine(id: string): Promise<void> {
    return this.request<void>(`/routines/${id}/trigger`, {
      method: 'POST',
    });
  }

  // ==========================================================================
  // Analytics API
  // ==========================================================================

  /**
   * Get daily metrics
   */
  async getDailyMetrics(params: MetricsQueryParams = {}): Promise<BackendDailyMetrics[]> {
    // Backend requires from_date, to_date, and user_id as query params
    const queryParams: Record<string, any> = {};

    if (params.startDate) {
      queryParams.from_date = params.startDate;
    }
    if (params.endDate) {
      queryParams.to_date = params.endDate;
    }
    if (params.userId) {
      queryParams.user_id = params.userId;
    }

    const queryString = buildQueryString(queryParams);
    return this.request<BackendDailyMetrics[]>(`/analytics/daily${queryString}`);
  }

  /**
   * Get streaks and badges
   */
  async getStreaks(userId: string = '00000000-0000-0000-0000-000000000000'): Promise<BackendStreaksResponse> {
    return this.request<BackendStreaksResponse>(`/analytics/streaks?user_id=${userId}`);
  }

  /**
   * Get analytics summary
   */
  async getAnalyticsSummary(days: number = 7, userId: string = '00000000-0000-0000-0000-000000000000'): Promise<BackendAnalyticsSummary> {
    return this.request<BackendAnalyticsSummary>(`/analytics/summary?days=${days}&user_id=${userId}`);
  }

  // ==========================================================================
  // Media API
  // ==========================================================================

  /**
   * Get video clips
   */
  async getClips(params: MediaQueryParams = {}): Promise<BackendClipsResponse> {
    const queryString = buildQueryString(params);
    return this.request<BackendClipsResponse>(`/clips${queryString}`);
  }

  /**
   * Get snapshots
   */
  async getSnapshots(params: MediaQueryParams = {}): Promise<BackendSnapshotsResponse> {
    const queryString = buildQueryString(params);
    return this.request<BackendSnapshotsResponse>(`/snapshots${queryString}`);
  }

  /**
   * Create a snapshot
   */
  async createSnapshot(data: SnapshotCreate): Promise<any> {
    return this.request<any>('/snapshots', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Create a video clip
   */
  async createClip(data: { start_ts: string; duration_ms: number; labels?: string[] }): Promise<any> {
    return this.request<any>('/clips', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Delete a video clip
   */
  async deleteClip(id: string): Promise<void> {
    return this.request<void>(`/clips/${id}`, {
      method: 'DELETE',
    });
  }

  /**
   * Delete a snapshot
   */
  async deleteSnapshot(id: string): Promise<void> {
    return this.request<void>(`/snapshots/${id}`, {
      method: 'DELETE',
    });
  }

  // ==========================================================================
  // Status API
  // ==========================================================================

  /**
   * Get system status
   */
  async getSystemStatus(): Promise<BackendSystemStatus> {
    return this.request<BackendSystemStatus>('/status');
  }

  // ==========================================================================
  // Models API
  // ==========================================================================

  /**
   * Get available and active models
   */
  async getModels(): Promise<BackendModelsListResponse> {
    return this.request<BackendModelsListResponse>('/models');
  }

  /**
   * Switch active models
   */
  async switchModels(request: ModelSwitchRequest): Promise<BackendModelSwitchResponse> {
    return this.request<BackendModelSwitchResponse>('/models/switch', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // ==========================================================================
  // Robot Control API
  // ==========================================================================

  /**
   * Send a robot action command
   */
  async sendRobotAction(action: 'pet' | 'treat' | 'fetch' | 'play', params?: Record<string, any>): Promise<BackendRobotActionResponse> {
    return this.request<BackendRobotActionResponse>('/robot/action', {
      method: 'POST',
      body: JSON.stringify({ action, params }),
    });
  }

  // ==========================================================================
  // AI Coach API
  // ==========================================================================

  /**
   * Send a message to the AI coach
   */
  async sendCoachMessage(message: string, context?: string): Promise<BackendCoachResponse> {
    return this.request<BackendCoachResponse>(
      '/coach/chat',
      {
        method: 'POST',
        body: JSON.stringify({ message, context }),
      },
      true // Use AI service URL
    );
  }

  /**
   * Stream a message to the AI coach (for real-time responses)
   */
  async *streamCoachMessage(message: string, context?: string): AsyncGenerator<string> {
    const url = `${this.aiServiceURL}/coach/stream`;

    if (config.debug) {
      console.log(`[API Stream] POST ${url}`, { message, context });
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, context }),
    });

    if (!response.ok) {
      const error = await this.handleErrorResponse(response);
      throw error;
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new APIError(500, 'Failed to get response stream reader');
    }

    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        yield chunk;
      }
    } finally {
      reader.releaseLock();
    }
  }
}

// ============================================================================
// Singleton Instance
// ============================================================================

/**
 * Default API client instance
 */
export const apiClient = new APIClient();
