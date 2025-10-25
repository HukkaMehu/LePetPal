/**
 * useSSEClient - React hook for SSE client integration
 * 
 * Manages SSEClient lifecycle and integrates with AppContext for state updates
 */

import { useEffect, useRef, useCallback } from 'react';
import { SSEClient } from './SSEClient';
import { useApp } from '@/contexts/AppContext';
import { CommandStatus } from '@/types';

export function useSSEClient() {
  const { config, setCurrentCommand, setError, setConnectionStatus, addToast } = useApp();
  const sseClientRef = useRef<SSEClient | null>(null);

  // Callback to handle command updates from SSE/polling
  const handleCommandUpdate = useCallback((status: CommandStatus) => {
    // Update UI within 100ms of receiving event (React batches updates automatically)
    setCurrentCommand(status);
  }, [setCurrentCommand]);

  // Callback to handle errors
  const handleError = useCallback((errorMessage: string) => {
    setError(errorMessage);
    addToast(errorMessage);
  }, [setError, addToast]);

  // Callback to handle connection status changes
  const handleConnectionChange = useCallback((connected: boolean) => {
    setConnectionStatus({
      status: connected ? 'connected' : 'disconnected',
    });
  }, [setConnectionStatus]);

  // Initialize SSE client when config changes
  useEffect(() => {
    if (!config.baseUrl) {
      return;
    }

    // Create new SSE client
    const client = new SSEClient({
      baseUrl: config.baseUrl,
      authToken: config.authToken,
      onUpdate: handleCommandUpdate,
      onError: handleError,
      onConnectionChange: handleConnectionChange,
    });

    // Connect to SSE endpoint
    client.connect();

    // Store reference
    sseClientRef.current = client;

    // Cleanup on unmount or config change
    return () => {
      client.disconnect();
      sseClientRef.current = null;
    };
  }, [config.baseUrl, config.authToken, handleCommandUpdate, handleError, handleConnectionChange]);

  // Function to set request ID for polling fallback
  const setRequestId = useCallback((requestId: string | null) => {
    sseClientRef.current?.setRequestId(requestId);
  }, []);

  // Function to get connection status
  const getConnectionStatus = useCallback(() => {
    return sseClientRef.current?.getConnectionStatus() || {
      connected: false,
      mode: 'disconnected' as const,
    };
  }, []);

  return {
    setRequestId,
    getConnectionStatus,
  };
}
