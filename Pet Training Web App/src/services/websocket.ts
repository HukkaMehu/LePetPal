/**
 * WebSocket Service
 * 
 * Manages WebSocket connections for real-time updates from the backend.
 * Includes automatic reconnection with exponential backoff and event subscription system.
 */

import { config } from '../config/env';
import { WebSocketMessage } from '../types';

// ============================================================================
// Types
// ============================================================================

export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'reconnecting';

export type EventCallback = (data: any) => void;

interface ReconnectConfig {
  maxAttempts: number;
  initialDelayMs: number;
  maxDelayMs: number;
  backoffMultiplier: number;
}

// ============================================================================
// Configuration
// ============================================================================

const DEFAULT_RECONNECT_CONFIG: ReconnectConfig = {
  maxAttempts: 10,
  initialDelayMs: 1000,
  maxDelayMs: 30000,
  backoffMultiplier: 1.5,
};

// ============================================================================
// WebSocket Service Class
// ============================================================================

export class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectConfig: ReconnectConfig;
  private reconnectAttempts: number = 0;
  private reconnectTimeout: number | null = null;
  private connectionState: ConnectionState = 'disconnected';
  private listeners: Map<string, Set<EventCallback>> = new Map();
  private stateChangeListeners: Set<(state: ConnectionState) => void> = new Set();
  private shouldReconnect: boolean = true;

  constructor(
    url: string = config.wsURL,
    reconnectConfig: ReconnectConfig = DEFAULT_RECONNECT_CONFIG
  ) {
    this.url = url;
    this.reconnectConfig = reconnectConfig;
  }

  // ==========================================================================
  // Connection Management
  // ==========================================================================

  /**
   * Connect to the WebSocket server
   */
  connect(): void {
    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
      console.warn('[WebSocket] Already connected or connecting');
      return;
    }

    this.shouldReconnect = true;
    this.setConnectionState('connecting');

    if (config.debug) {
      console.log(`[WebSocket] Connecting to ${this.url}`);
    }

    try {
      this.ws = new WebSocket(this.url);
      this.setupEventHandlers();
    } catch (error) {
      console.error('[WebSocket] Connection error:', error);
      this.handleError(error as Event);
    }
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect(): void {
    this.shouldReconnect = false;
    
    if (this.reconnectTimeout !== null) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.ws) {
      if (config.debug) {
        console.log('[WebSocket] Disconnecting');
      }
      
      this.ws.close();
      this.ws = null;
    }

    this.setConnectionState('disconnected');
  }

  /**
   * Get current connection state
   */
  getConnectionState(): ConnectionState {
    return this.connectionState;
  }

  /**
   * Check if currently connected
   */
  isConnected(): boolean {
    return this.connectionState === 'connected' && this.ws?.readyState === WebSocket.OPEN;
  }

  // ==========================================================================
  // Event Subscription
  // ==========================================================================

  /**
   * Subscribe to a specific event type
   * Returns an unsubscribe function
   */
  subscribe(eventType: string, callback: EventCallback): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }

    this.listeners.get(eventType)!.add(callback);

    if (config.debug) {
      console.log(`[WebSocket] Subscribed to event type: ${eventType}`);
    }

    // Return unsubscribe function
    return () => this.unsubscribe(eventType, callback);
  }

  /**
   * Unsubscribe from a specific event type
   */
  unsubscribe(eventType: string, callback: EventCallback): void {
    const callbacks = this.listeners.get(eventType);
    
    if (callbacks) {
      callbacks.delete(callback);
      
      if (callbacks.size === 0) {
        this.listeners.delete(eventType);
      }

      if (config.debug) {
        console.log(`[WebSocket] Unsubscribed from event type: ${eventType}`);
      }
    }
  }

  /**
   * Subscribe to connection state changes
   */
  onStateChange(callback: (state: ConnectionState) => void): () => void {
    this.stateChangeListeners.add(callback);
    
    // Return unsubscribe function
    return () => {
      this.stateChangeListeners.delete(callback);
    };
  }

  // ==========================================================================
  // Message Sending
  // ==========================================================================

  /**
   * Send a message through the WebSocket
   */
  send(data: any): void {
    if (!this.isConnected()) {
      console.warn('[WebSocket] Cannot send message: not connected');
      return;
    }

    try {
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      this.ws!.send(message);

      if (config.debug) {
        console.log('[WebSocket] Sent message:', data);
      }
    } catch (error) {
      console.error('[WebSocket] Error sending message:', error);
    }
  }

  // ==========================================================================
  // Private Methods
  // ==========================================================================

  /**
   * Set up WebSocket event handlers
   */
  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => this.handleOpen();
    this.ws.onmessage = (event) => this.handleMessage(event);
    this.ws.onerror = (event) => this.handleError(event);
    this.ws.onclose = (event) => this.handleClose(event);
  }

  /**
   * Handle WebSocket open event
   */
  private handleOpen(): void {
    if (config.debug) {
      console.log('[WebSocket] Connected');
    }

    this.reconnectAttempts = 0;
    this.setConnectionState('connected');
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);

      if (config.debug) {
        console.log('[WebSocket] Received message:', message);
      }

      // Notify listeners based on message type
      this.notifyListeners(message);

    } catch (error) {
      console.error('[WebSocket] Error parsing message:', error);
    }
  }

  /**
   * Handle WebSocket error event
   */
  private handleError(event: Event): void {
    console.error('[WebSocket] Error:', event);
  }

  /**
   * Handle WebSocket close event
   */
  private handleClose(event: CloseEvent): void {
    if (config.debug) {
      console.log(`[WebSocket] Closed (code: ${event.code}, reason: ${event.reason})`);
    }

    this.ws = null;

    if (this.shouldReconnect) {
      this.reconnect();
    } else {
      this.setConnectionState('disconnected');
    }
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  private reconnect(): void {
    if (this.reconnectAttempts >= this.reconnectConfig.maxAttempts) {
      console.error(
        `[WebSocket] Max reconnection attempts (${this.reconnectConfig.maxAttempts}) reached. Giving up.`
      );
      this.setConnectionState('disconnected');
      return;
    }

    this.reconnectAttempts++;
    this.setConnectionState('reconnecting');

    const delay = this.calculateReconnectDelay();

    console.log(
      `[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.reconnectConfig.maxAttempts})`
    );

    this.reconnectTimeout = window.setTimeout(() => {
      this.reconnectTimeout = null;
      this.connect();
    }, delay);
  }

  /**
   * Calculate reconnection delay with exponential backoff
   */
  private calculateReconnectDelay(): number {
    const delay = this.reconnectConfig.initialDelayMs * 
      Math.pow(this.reconnectConfig.backoffMultiplier, this.reconnectAttempts - 1);
    
    return Math.min(delay, this.reconnectConfig.maxDelayMs);
  }

  /**
   * Notify all listeners for a given message
   */
  private notifyListeners(message: WebSocketMessage): void {
    // Notify listeners for the specific message type
    const typeListeners = this.listeners.get(message.type);
    if (typeListeners) {
      typeListeners.forEach(callback => {
        try {
          callback(message.data);
        } catch (error) {
          console.error(`[WebSocket] Error in listener callback for type ${message.type}:`, error);
        }
      });
    }

    // For event messages, also notify listeners for the specific event type
    if (message.type === 'event' && message.event_type) {
      const eventListeners = this.listeners.get(`event:${message.event_type}`);
      if (eventListeners) {
        eventListeners.forEach(callback => {
          try {
            callback(message.data);
          } catch (error) {
            console.error(`[WebSocket] Error in listener callback for event ${message.event_type}:`, error);
          }
        });
      }
    }

    // For overlay messages, also notify listeners for the specific overlay type
    if (message.type === 'overlay' && message.overlay_type) {
      const overlayListeners = this.listeners.get(`overlay:${message.overlay_type}`);
      if (overlayListeners) {
        overlayListeners.forEach(callback => {
          try {
            callback(message.data);
          } catch (error) {
            console.error(`[WebSocket] Error in listener callback for overlay ${message.overlay_type}:`, error);
          }
        });
      }
    }

    // Notify wildcard listeners (subscribed to '*')
    const wildcardListeners = this.listeners.get('*');
    if (wildcardListeners) {
      wildcardListeners.forEach(callback => {
        try {
          callback(message);
        } catch (error) {
          console.error('[WebSocket] Error in wildcard listener callback:', error);
        }
      });
    }
  }

  /**
   * Update connection state and notify listeners
   */
  private setConnectionState(state: ConnectionState): void {
    if (this.connectionState === state) return;

    this.connectionState = state;

    if (config.debug) {
      console.log(`[WebSocket] State changed to: ${state}`);
    }

    // Notify state change listeners
    this.stateChangeListeners.forEach(callback => {
      try {
        callback(state);
      } catch (error) {
        console.error('[WebSocket] Error in state change listener:', error);
      }
    });
  }
}

// ============================================================================
// Singleton Instance
// ============================================================================

/**
 * Default WebSocket service instance
 */
export const wsService = new WebSocketService();
