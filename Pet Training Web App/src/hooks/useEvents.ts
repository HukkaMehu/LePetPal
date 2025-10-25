/**
 * useEvents Hook
 * 
 * Custom React hook for managing events data with real-time updates.
 * Fetches events from backend API and subscribes to WebSocket for live updates.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient, wsService, adaptEvent, adaptEvents } from '../services';
import { Event, EventQueryParams } from '../types';
import { BackendEvent } from '../types/backend';

// ============================================================================
// Types
// ============================================================================

interface UseEventsOptions extends EventQueryParams {
  autoConnect?: boolean;
  pollInterval?: number;
}

interface UseEventsReturn {
  events: Event[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  addEvent: (event: Event) => void;
}

// ============================================================================
// Hook Implementation
// ============================================================================

/**
 * Hook for fetching and managing events with real-time updates
 */
export function useEvents(options: UseEventsOptions = {}): UseEventsReturn {
  const {
    autoConnect = true,
    pollInterval,
    ...queryParams
  } = options;

  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  
  const isMountedRef = useRef<boolean>(true);
  const pollTimeoutRef = useRef<number | null>(null);

  /**
   * Fetch events from the API
   */
  const fetchEvents = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.getEvents(queryParams);
      
      if (isMountedRef.current) {
        const adaptedEvents = adaptEvents(response.events);
        setEvents(adaptedEvents);
      }
    } catch (err) {
      if (isMountedRef.current) {
        setError(err as Error);
        console.error('[useEvents] Error fetching events:', err);
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  }, [queryParams.startDate, queryParams.endDate, queryParams.eventType, queryParams.limit, queryParams.offset]);

  /**
   * Add a new event to the list (used by WebSocket updates)
   */
  const addEvent = useCallback((event: Event) => {
    setEvents(prevEvents => {
      // Check if event already exists
      const exists = prevEvents.some(e => e.id === event.id);
      if (exists) {
        return prevEvents;
      }

      // Add new event at the beginning (newest first)
      const newEvents = [event, ...prevEvents];

      // If limit is set, trim the array
      if (queryParams.limit && newEvents.length > queryParams.limit) {
        return newEvents.slice(0, queryParams.limit);
      }

      return newEvents;
    });
  }, [queryParams.limit]);

  /**
   * Handle WebSocket event messages
   */
  const handleWebSocketEvent = useCallback((data: BackendEvent) => {
    try {
      const adaptedEvent = adaptEvent(data);
      
      // Apply filters if specified
      if (queryParams.eventType && adaptedEvent.type !== queryParams.eventType) {
        return;
      }

      if (queryParams.startDate && adaptedEvent.timestamp < new Date(queryParams.startDate)) {
        return;
      }

      if (queryParams.endDate && adaptedEvent.timestamp > new Date(queryParams.endDate)) {
        return;
      }

      addEvent(adaptedEvent);
    } catch (err) {
      console.error('[useEvents] Error handling WebSocket event:', err);
    }
  }, [queryParams.eventType, queryParams.startDate, queryParams.endDate, addEvent]);

  /**
   * Set up polling if pollInterval is specified
   */
  useEffect(() => {
    if (!pollInterval) return;

    const poll = async () => {
      await fetchEvents();
      
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
  }, [pollInterval, fetchEvents]);

  /**
   * Initial fetch and WebSocket subscription
   */
  useEffect(() => {
    isMountedRef.current = true;

    // Fetch initial events
    fetchEvents();

    // Subscribe to WebSocket events if autoConnect is enabled
    let unsubscribe: (() => void) | null = null;

    if (autoConnect) {
      // Connect WebSocket if not already connected
      if (!wsService.isConnected()) {
        wsService.connect();
      }

      // Subscribe to event messages
      unsubscribe = wsService.subscribe('event', handleWebSocketEvent);
    }

    // Cleanup
    return () => {
      isMountedRef.current = false;
      
      if (unsubscribe) {
        unsubscribe();
      }

      if (pollTimeoutRef.current !== null) {
        clearTimeout(pollTimeoutRef.current);
        pollTimeoutRef.current = null;
      }
    };
  }, [autoConnect, fetchEvents, handleWebSocketEvent]);

  return {
    events,
    loading,
    error,
    refetch: fetchEvents,
    addEvent,
  };
}
