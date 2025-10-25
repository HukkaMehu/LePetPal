import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { BackendApiService } from '../services/api';
import type { StatusResponse } from '../types/api';

/**
 * Backend State Interface
 */
export interface BackendState {
  isConnected: boolean;
  connectionError?: string;
  currentCommand?: {
    requestId: string;
    prompt: string;
    state: 'executing' | 'completed' | 'failed';
    phase?: string;
    confidence?: number;
    duration_ms?: number;
    message?: string;
  };
  videoFeedUrl: string;
}

/**
 * Backend Context Value Interface
 */
export interface BackendContextValue {
  state: BackendState;
  sendCommand: (prompt: string) => Promise<void>;
  testConnection: () => Promise<boolean>;
  updateBackendUrl: (url: string) => void;
}

/**
 * Backend Context
 */
const BackendContext = createContext<BackendContextValue | undefined>(undefined);

/**
 * LocalStorage key for backend configuration
 */
const STORAGE_KEY = 'pet-training-backend-config';

/**
 * Status polling interval in milliseconds
 */
const POLLING_INTERVAL_MS = 500;

/**
 * Backend Provider Component
 */
export function BackendProvider({ children }: { children: React.ReactNode }) {
  // Initialize API service
  const [apiService] = useState(() => {
    // Load saved URL from localStorage
    const savedConfig = localStorage.getItem(STORAGE_KEY);
    if (savedConfig) {
      try {
        const { backendUrl } = JSON.parse(savedConfig);
        return new BackendApiService({ baseUrl: backendUrl });
      } catch {
        // If parsing fails, use default
      }
    }
    return new BackendApiService();
  });

  // State management
  const [state, setState] = useState<BackendState>({
    isConnected: false,
    videoFeedUrl: apiService.getVideoFeedUrl(),
  });

  // Polling interval ref
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Clear polling interval
   */
  const clearPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  };

  /**
   * Poll status for a command
   */
  const pollStatus = async (requestId: string, prompt: string) => {
    try {
      const status: StatusResponse = await apiService.getStatus(requestId);

      // Update state with current status
      setState((prev: BackendState) => ({
        ...prev,
        currentCommand: {
          requestId,
          prompt,
          state: status.state as 'executing' | 'completed' | 'failed',
          phase: status.phase,
          confidence: status.confidence,
          duration_ms: status.duration_ms,
          message: status.message,
        },
      }));

      // Stop polling if command is completed or failed
      if (status.state === 'completed' || status.state === 'failed') {
        clearPolling();
      }
    } catch (error) {
      // On error, stop polling and update state
      clearPolling();
      setState((prev: BackendState) => ({
        ...prev,
        currentCommand: prev.currentCommand
          ? {
              ...prev.currentCommand,
              state: 'failed',
              message: error instanceof Error ? error.message : 'Unknown error',
            }
          : undefined,
      }));
    }
  };

  /**
   * Send a command to the backend
   */
  const sendCommand = async (prompt: string): Promise<void> => {
    try {
      // Clear any existing polling
      clearPolling();

      // Send command
      const response = await apiService.sendCommand(prompt);

      // Update state with executing command
      setState((prev: BackendState) => ({
        ...prev,
        currentCommand: {
          requestId: response.request_id,
          prompt,
          state: 'executing',
        },
      }));

      // Start polling for status
      pollingIntervalRef.current = setInterval(() => {
        pollStatus(response.request_id, prompt);
      }, POLLING_INTERVAL_MS);

      // Poll immediately
      pollStatus(response.request_id, prompt);
    } catch (error) {
      // Update state with error
      setState((prev: BackendState) => ({
        ...prev,
        connectionError: error instanceof Error ? error.message : 'Failed to send command',
      }));
      throw error;
    }
  };

  /**
   * Test connection to backend
   */
  const testConnection = async (): Promise<boolean> => {
    try {
      await apiService.health();
      setState((prev: BackendState) => ({
        ...prev,
        isConnected: true,
        connectionError: undefined,
      }));
      return true;
    } catch (error) {
      setState((prev: BackendState) => ({
        ...prev,
        isConnected: false,
        connectionError: error instanceof Error ? error.message : 'Connection failed',
      }));
      return false;
    }
  };

  /**
   * Update backend URL
   */
  const updateBackendUrl = (url: string): void => {
    // Update API service config
    apiService.updateConfig({ baseUrl: url });

    // Update video feed URL
    setState((prev: BackendState) => ({
      ...prev,
      videoFeedUrl: apiService.getVideoFeedUrl(),
    }));

    // Persist to localStorage
    const config = {
      backendUrl: url,
      lastConnected: new Date().toISOString(),
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
  };

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      clearPolling();
    };
  }, []);

  const contextValue: BackendContextValue = {
    state,
    sendCommand,
    testConnection,
    updateBackendUrl,
  };

  return (
    <BackendContext.Provider value={contextValue}>
      {children}
    </BackendContext.Provider>
  );
}

/**
 * Custom hook to use Backend Context
 */
export function useBackend(): BackendContextValue {
  const context = useContext(BackendContext);
  
  if (context === undefined) {
    throw new Error('useBackend must be used within a BackendProvider');
  }
  
  return context;
}
