/**
 * Environment Configuration Module
 * 
 * Reads and validates environment variables for the application.
 * All environment variables must be prefixed with VITE_ to be exposed to the client.
 */

interface AppConfig {
  apiBaseURL: string;
  aiServiceURL: string;
  wsURL: string;
  videoStreamURL: string;
  debug: boolean;
}

/**
 * Validates that required environment variables are present
 */
function validateConfig(): void {
  const required = [
    'VITE_API_BASE_URL',
    'VITE_AI_SERVICE_URL',
    'VITE_WS_URL',
    'VITE_VIDEO_STREAM_URL'
  ];

  const missing = required.filter(key => !import.meta.env[key]);

  if (missing.length > 0) {
    console.error(
      `Missing required environment variables: ${missing.join(', ')}\n` +
      'Please check your .env file and ensure all required variables are set.'
    );
  }
}

/**
 * Application configuration object
 * Provides centralized access to all environment variables
 */
export const config: AppConfig = {
  apiBaseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  aiServiceURL: import.meta.env.VITE_AI_SERVICE_URL || 'http://localhost:8001',
  wsURL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',
  videoStreamURL: import.meta.env.VITE_VIDEO_STREAM_URL || 'http://localhost:8000/video/mjpeg',
  debug: import.meta.env.VITE_DEBUG === 'true',
};

// Validate configuration on module load
validateConfig();

// Log configuration in debug mode (excluding sensitive data)
if (config.debug) {
  console.log('Application Configuration:', {
    apiBaseURL: config.apiBaseURL,
    aiServiceURL: config.aiServiceURL,
    wsURL: config.wsURL,
    videoStreamURL: config.videoStreamURL,
  });
}
