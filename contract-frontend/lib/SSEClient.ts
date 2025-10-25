/**
 * SSEClient - Server-Sent Events client with polling fallback
 * 
 * Handles real-time command updates via SSE with automatic fallback to polling
 * when SSE is unavailable or fails. Implements exponential backoff for reconnection.
 */

import { CommandStatus } from '@/types';

type SSEClientCallback = (status: CommandStatus) => void;
type ErrorCallback = (error: string) => void;

interface SSEClientOptions {
  baseUrl: string;
  authToken?: string;
  onUpdate: SSEClientCallback;
  onError?: ErrorCallback;
  onConnectionChange?: (connected: boolean) => void;
}

export class SSEClient {
  private baseUrl: string;
  private authToken?: string;
  private onUpdate: SSEClientCallback;
  private onError?: ErrorCallback;
  private onConnectionChange?: (connected: boolean) => void;
  
  private eventSource: EventSource | null = null;
  private pollingInterval: NodeJS.Timeout | null = null;
  private currentRequestId: string | null = null;
  
  private reconnectAttempts = 0;
  private reconnectTimeouts = [500, 1000, 2000, 4000, 8000]; // Exponential backoff delays
  private reconnectTimer: NodeJS.Timeout | null = null;
  
  private isSSESupported = true;
  private isPollingMode = false;
  private isConnected = false;

  constructor(options: SSEClientOptions) {
    this.baseUrl = options.baseUrl;
    this.authToken = options.authToken;
    this.onUpdate = options.onUpdate;
    this.onError = options.onError;
    this.onConnectionChange = options.onConnectionChange;
  }

  /**
   * Connect to SSE endpoint or start polling fallback
   */
  connect(): void {
    if (this.isSSESupported && !this.isPollingMode) {
      this.connectSSE();
    } else {
      this.startPolling();
    }
  }

  /**
   * Disconnect from SSE or stop polling
   */
  disconnect(): void {
    this.disconnectSSE();
    this.stopPolling();
    this.clearReconnectTimer();
    this.isConnected = false;
    this.onConnectionChange?.(false);
  }

  /**
   * Set the current request ID for polling fallback
   */
  setRequestId(requestId: string | null): void {
    this.currentRequestId = requestId;
  }

  /**
   * Update configuration (e.g., when user changes base URL)
   */
  updateConfig(baseUrl: string, authToken?: string): void {
    const needsReconnect = this.baseUrl !== baseUrl || this.authToken !== authToken;
    
    this.baseUrl = baseUrl;
    this.authToken = authToken;
    
    if (needsReconnect && (this.eventSource || this.pollingInterval)) {
      this.disconnect();
      this.connect();
    }
  }

  /**
   * Connect to SSE /events endpoint
   */
  private connectSSE(): void {
    try {
      const url = `${this.baseUrl}/events`;
      this.eventSource = new EventSource(url);

      this.eventSource.onopen = () => {
        this.isConnected = true;
        this.reconnectAttempts = 0; // Reset backoff on successful connection
        this.onConnectionChange?.(true);
      };

      this.eventSource.addEventListener('command_update', (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data) as CommandStatus;
          this.onUpdate(data);
          
          // Stop polling if we were in fallback mode
          if (this.pollingInterval) {
            this.stopPolling();
          }
        } catch (error) {
          console.error('Failed to parse SSE event data:', error);
          this.onError?.('Failed to parse server event');
        }
      });

      this.eventSource.onerror = (error) => {
        console.error('SSE connection error:', error);
        this.isConnected = false;
        this.onConnectionChange?.(false);
        
        // Close the failed connection
        this.disconnectSSE();
        
        // Attempt reconnection with exponential backoff
        this.scheduleReconnect();
      };

    } catch (error) {
      console.error('Failed to create EventSource:', error);
      this.isSSESupported = false;
      this.startPolling();
    }
  }

  /**
   * Disconnect from SSE
   */
  private disconnectSSE(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  /**
   * Schedule reconnection with exponential backoff
   */
  private scheduleReconnect(): void {
    this.clearReconnectTimer();
    
    const delay = this.reconnectTimeouts[
      Math.min(this.reconnectAttempts, this.reconnectTimeouts.length - 1)
    ];
    
    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      
      // Try SSE first, fall back to polling if it fails repeatedly
      if (this.reconnectAttempts >= 3) {
        console.warn('SSE reconnection failed multiple times, falling back to polling');
        this.isPollingMode = true;
        this.startPolling();
      } else {
        this.connectSSE();
      }
    }, delay);
  }

  /**
   * Clear reconnection timer
   */
  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  /**
   * Start polling /status/{request_id} endpoint
   */
  private startPolling(): void {
    if (this.pollingInterval) {
      return; // Already polling
    }

    this.isPollingMode = true;
    this.isConnected = true;
    this.onConnectionChange?.(true);

    this.pollingInterval = setInterval(() => {
      if (!this.currentRequestId) {
        return; // No active command to poll
      }

      this.pollStatus(this.currentRequestId);
    }, 500); // Poll every 500ms as per requirements
  }

  /**
   * Stop polling
   */
  private stopPolling(): void {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }

  /**
   * Poll the /status/{request_id} endpoint
   */
  private async pollStatus(requestId: string): Promise<void> {
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };

      if (this.authToken) {
        headers['X-LePetPal-Token'] = this.authToken;
      }

      const response = await fetch(`${this.baseUrl}/status/${requestId}`, {
        method: 'GET',
        headers,
      });

      if (response.status === 404) {
        // Request ID not found - might be too old or invalid
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json() as CommandStatus;
      this.onUpdate(data);

      // Stop polling if command reached final state
      if (this.isFinalState(data.state)) {
        this.currentRequestId = null;
      }

    } catch (error) {
      console.error('Polling error:', error);
      this.onError?.('Failed to fetch command status');
    }
  }

  /**
   * Check if command state is final (no more updates expected)
   */
  private isFinalState(state: string): boolean {
    return ['completed', 'failed', 'timeout', 'interrupted'].includes(state);
  }

  /**
   * Get current connection status
   */
  getConnectionStatus(): { connected: boolean; mode: 'sse' | 'polling' | 'disconnected' } {
    if (!this.isConnected) {
      return { connected: false, mode: 'disconnected' };
    }
    return {
      connected: true,
      mode: this.isPollingMode ? 'polling' : 'sse',
    };
  }
}
