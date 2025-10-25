/**
 * API Configuration
 */
export interface ApiConfig {
  baseUrl: string;
  authToken?: string;
}

/**
 * Command Response from POST /command
 */
export interface CommandResponse {
  request_id: string;
  status: 'accepted';
}

/**
 * Status Response from GET /status/{id}
 */
export interface StatusResponse {
  state: 'idle' | 'executing' | 'completed' | 'failed';
  phase?: string;
  confidence?: number;
  duration_ms?: number;
  message?: string;
}

/**
 * Health Response from GET /health
 */
export interface HealthResponse {
  status: 'ok';
  api: number;
  version: string;
}

/**
 * Generic API Response for simple endpoints
 */
export interface GenericResponse {
  status: string;
  message?: string;
}

/**
 * Network Error - thrown when request fails due to network issues
 */
export class NetworkError extends Error {
  constructor(message: string, public originalError?: unknown) {
    super(message);
    this.name = 'NetworkError';
  }
}

/**
 * API Error - thrown when backend returns an error response
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public responseBody?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}
