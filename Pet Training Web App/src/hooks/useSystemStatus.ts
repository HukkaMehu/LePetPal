/**
 * useSystemStatus Hook
 * 
 * Custom React hook for fetching and monitoring system status.
 * Subscribes to WebSocket for real-time telemetry updates.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient, wsService, adaptSystemStatus } from '../services';
import { SystemStatus, TelemetryData } from '../types';

// ============================================================================
// Types
// ============================================================================

interface UseSystemStatusOptions {
  autoConnect?: boolean;
  pollInterval?: number;
}

interface UseSystemStatusReturn {
  status: SystemStatus | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

// ============================================================================
// Hook Implementation
// ============================================================================

/**
 * Hook for fetching and monitoring system status with real-time updates
 */
export function useSystemStatus(options: UseSystemStatusOptions = {}): UseSystemStatusReturn {
  const {
    autoConnect = true,
    pollInterval = 5000, // Poll every 5 seconds by default
  } = options;

  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  
  const isMountedRef = useRef<boolean>(true);
  const pollTimeoutRef = useRef<number | null>(null);

  /**
   * Fetch system status from the API
   */
  const fetchStatus = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.getSystemStatus();
      
      if (isMountedRef.current) {
        const adaptedStatus = adaptSystemStatus(response);
        setStatus(adaptedStatus);
      }
    } catch (err) {
      if (isMountedRef.current) {
        setError(err as Error);
        console.error('[useSystemStatus] Error fetching status:', err);
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  }, []);

  /**
   * Handle WebSocket telemetry updates
   */
  const handleTelemetryUpdate = useCallback((data: TelemetryData) => {
    try {
      setStatus(prevStatus => {
        if (!prevStatus) return prevStatus;

        // Update status with new telemetry data
        return {
          ...prevStatus,
          fps: data.fps ?? prevStatus.fps,
          latencyMs: data.latencyMs ?? prevStatus.latencyMs,
          timestamp: data.timestamp,
        };
      });
    } catch (err) {
      console.error('[useSystemStatus] Error handling telemetry update:', err);
    }
  }, []);

  /**
   * Handle WebSocket overlay updates (for device status changes)
   */
  const handleOverlayUpdate = useCallback((data: any) => {
    try {
      // Handle device connection status changes
      if (data.type === 'device_status' || data.device_connected !== undefined) {
        setStatus(prevStatus => {
          if (!prevStatus) return prevStatus;

          return {
            ...prevStatus,
            device: data.device_connected ? 'connected' : 'offline',
            timestamp: new Date().toISOString(),
          };
        });
      }

      // Handle video stream type changes
      if (data.video_stream_type) {
        setStatus(prevStatus => {
          if (!prevStatus) return prevStatus;

          return {
            ...prevStatus,
            video: data.video_stream_type,
            timestamp: new Date().toISOString(),
          };
        });
      }
    } catch (err) {
      console.error('[useSystemStatus] Error handling overlay update:', err);
    }
  }, []);

  /**
   * Set up polling
   */
  useEffect(() => {
    if (!pollInterval) return;

    const poll = async () => {
      await fetchStatus();
      
      if (isMountedRef.current) {
        pollTimeoutRef.current = window.setTimeout(poll, pollInterval);
      }
    };

    pollTimeoutRef.current = window.setTimeout(poll, pollInterval);

    return () => {
      if (pollTimeoutRef.current !== null) {
        clearTimeout(pollTimeoutRef.current);
        pollTimeoutRef.current = null;
      }
    };
  }, [pollInterval, fetchStatus]);

  /**
   * Initial fetch and WebSocket subscription
   */
  useEffect(() => {
    isMountedRef.current = true;

    // Fetch initial status
    fetchStatus();

    // Subscribe to WebSocket updates if autoConnect is enabled
    let unsubscribeTelemetry: (() => void) | null = null;
    let unsubscribeOverlay: (() => void) | null = null;

    if (autoConnect) {
      // Connect WebSocket if not already connected
      if (!wsService.isConnected()) {
        wsService.connect();
      }

      // Subscribe to telemetry messages
      unsubscribeTelemetry = wsService.subscribe('telemetry', handleTelemetryUpdate);

      // Subscribe to overlay messages for device status changes
      unsubscribeOverlay = wsService.subscribe('overlay', handleOverlayUpdate);
    }

    // Cleanup
    return () => {
      isMountedRef.current = false;
      
      if (unsubscribeTelemetry) {
        unsubscribeTelemetry();
      }

      if (unsubscribeOverlay) {
        unsubscribeOverlay();
      }

      if (pollTimeoutRef.current !== null) {
        clearTimeout(pollTimeoutRef.current);
        pollTimeoutRef.current = null;
      }
    };
  }, [autoConnect, fetchStatus, handleTelemetryUpdate, handleOverlayUpdate]);

  return {
    status,
    loading,
    error,
    refetch: fetchStatus,
  };
}
