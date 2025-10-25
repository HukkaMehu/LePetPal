import type {
  ApiConfig,
  CommandResponse,
  StatusResponse,
  HealthResponse,
  GenericResponse,
} from '../types/api';
import { NetworkError, ApiError } from '../types/api';

/**
 * Backend API Service
 * Encapsulates all HTTP communication with the LePetPal backend
 */
export class BackendApiService {
  private config: ApiConfig;

  constructor(config?: Partial<ApiConfig>) {
    const defaultBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
    
    this.config = {
      baseUrl: config?.baseUrl || defaultBaseUrl,
      authToken: config?.authToken,
    };
  }

  /**
   * Update the API configuration
   */
  updateConfig(config: Partial<ApiConfig>): void {
    this.config = {
      ...this.config,
      ...config,
    };
  }

  /**
   * Make a fetch request with error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.config.baseUrl}${endpoint}`;
    
    const headers: Record<string, string> = {};

    // Only add Content-Type for requests with a body
    if (options.method === 'POST' || options.method === 'PUT' || options.method === 'PATCH') {
      headers['Content-Type'] = 'application/json';
    }

    if (options.headers) {
      Object.assign(headers, options.headers);
    }

    if (this.config.authToken) {
      headers['Authorization'] = `Bearer ${this.config.authToken}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        mode: 'cors',
      });

      if (!response.ok) {
        const errorBody = await response.text();
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        
        try {
          const errorJson = JSON.parse(errorBody);
          errorMessage = errorJson.message || errorJson.error || errorMessage;
        } catch {
          // If response is not JSON, use the text or default message
          errorMessage = errorBody || errorMessage;
        }

        throw new ApiError(errorMessage, response.status, errorBody);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      // Network or other errors
      throw new NetworkError(
        'Failed to connect to backend. Please check your connection settings.',
        error
      );
    }
  }

  /**
   * GET /health - Check backend health status
   */
  async health(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health', {
      method: 'GET',
    });
  }

  /**
   * POST /command - Send a training command
   */
  async sendCommand(prompt: string, options?: Record<string, unknown>): Promise<CommandResponse> {
    return this.request<CommandResponse>('/command', {
      method: 'POST',
      body: JSON.stringify({
        prompt,
        options: options || {},
      }),
    });
  }

  /**
   * GET /status/{id} - Get command execution status
   */
  async getStatus(requestId: string): Promise<StatusResponse> {
    return this.request<StatusResponse>(`/status/${requestId}`);
  }

  /**
   * POST /dispense_treat - Dispense a treat
   */
  async dispenseTreat(durationMs?: number): Promise<GenericResponse> {
    return this.request<GenericResponse>('/dispense_treat', {
      method: 'POST',
      body: JSON.stringify({
        duration_ms: durationMs,
      }),
    });
  }

  /**
   * POST /speak - Text-to-speech
   */
  async speak(text: string): Promise<GenericResponse> {
    return this.request<GenericResponse>('/speak', {
      method: 'POST',
      body: JSON.stringify({
        text,
      }),
    });
  }

  /**
   * Get the video feed URL (MJPEG stream)
   */
  getVideoFeedUrl(): string {
    return `${this.config.baseUrl}/video_feed`;
  }
}
