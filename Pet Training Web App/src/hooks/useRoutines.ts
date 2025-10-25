/**
 * useRoutines Hook
 * 
 * Custom React hook for managing routines with CRUD operations.
 * Fetches routines from backend and subscribes to WebSocket for notifications.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient, wsService, adaptRoutine, adaptRoutines } from '../services';
import { Routine, RoutineCreate, RoutineUpdate } from '../types';
import { BackendRoutine } from '../types/backend';

// ============================================================================
// Types
// ============================================================================

interface UseRoutinesOptions {
  autoConnect?: boolean;
}

interface RoutineNotification {
  routineId: string;
  routineName: string;
  status: 'started' | 'completed';
  timestamp: Date;
}

interface UseRoutinesReturn {
  routines: Routine[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  createRoutine: (routine: RoutineCreate) => Promise<Routine>;
  updateRoutine: (id: string, routine: RoutineUpdate) => Promise<Routine>;
  deleteRoutine: (id: string) => Promise<void>;
  triggerRoutine: (id: string) => Promise<void>;
  lastNotification: RoutineNotification | null;
}

// ============================================================================
// Hook Implementation
// ============================================================================

/**
 * Hook for managing routines with CRUD operations
 */
export function useRoutines(options: UseRoutinesOptions = {}): UseRoutinesReturn {
  const { autoConnect = true } = options;

  const [routines, setRoutines] = useState<Routine[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const [lastNotification, setLastNotification] = useState<RoutineNotification | null>(null);
  
  const isMountedRef = useRef<boolean>(true);

  /**
   * Fetch routines from the API
   */
  const fetchRoutines = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.getRoutines();
      
      if (isMountedRef.current) {
        // Backend returns array directly
        const adaptedRoutines = adaptRoutines(response);
        setRoutines(adaptedRoutines);
      }
    } catch (err) {
      if (isMountedRef.current) {
        setError(err as Error);
        console.error('[useRoutines] Error fetching routines:', err);
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  }, []);

  /**
   * Create a new routine
   */
  const createRoutine = useCallback(async (routine: RoutineCreate): Promise<Routine> => {
    try {
      setError(null);

      const response = await apiClient.createRoutine(routine);
      const adaptedRoutine = adaptRoutine(response as any);
      
      if (isMountedRef.current) {
        setRoutines(prevRoutines => [...prevRoutines, adaptedRoutine]);
      }

      return adaptedRoutine;
    } catch (err) {
      if (isMountedRef.current) {
        setError(err as Error);
      }
      console.error('[useRoutines] Error creating routine:', err);
      throw err;
    }
  }, []);

  /**
   * Update an existing routine
   */
  const updateRoutine = useCallback(async (id: string, routine: RoutineUpdate): Promise<Routine> => {
    try {
      setError(null);

      const response = await apiClient.updateRoutine(id, routine);
      const adaptedRoutine = adaptRoutine(response as any);
      
      if (isMountedRef.current) {
        setRoutines(prevRoutines =>
          prevRoutines.map(r => (r.id === id ? adaptedRoutine : r))
        );
      }

      return adaptedRoutine;
    } catch (err) {
      if (isMountedRef.current) {
        setError(err as Error);
      }
      console.error('[useRoutines] Error updating routine:', err);
      throw err;
    }
  }, []);

  /**
   * Delete a routine
   */
  const deleteRoutine = useCallback(async (id: string): Promise<void> => {
    try {
      setError(null);

      await apiClient.deleteRoutine(id);
      
      if (isMountedRef.current) {
        setRoutines(prevRoutines => prevRoutines.filter(r => r.id !== id));
      }
    } catch (err) {
      if (isMountedRef.current) {
        setError(err as Error);
      }
      console.error('[useRoutines] Error deleting routine:', err);
      throw err;
    }
  }, []);

  /**
   * Trigger a routine manually
   */
  const triggerRoutine = useCallback(async (id: string): Promise<void> => {
    try {
      setError(null);

      await apiClient.triggerRoutine(id);
      
      // Update lastRun timestamp
      if (isMountedRef.current) {
        setRoutines(prevRoutines =>
          prevRoutines.map(r =>
            r.id === id ? { ...r, lastRun: new Date() } : r
          )
        );
      }
    } catch (err) {
      if (isMountedRef.current) {
        setError(err as Error);
      }
      console.error('[useRoutines] Error triggering routine:', err);
      throw err;
    }
  }, []);

  /**
   * Handle WebSocket routine notifications
   */
  const handleRoutineNotification = useCallback((data: any) => {
    try {
      // Handle routine started notification
      if (data.status === 'started' && data.routine_id) {
        setRoutines(prevRoutines => {
          const updatedRoutines = prevRoutines.map(r =>
            r.id === data.routine_id ? { ...r, lastRun: new Date() } : r
          );
          
          // Find routine name for notification
          const routine = updatedRoutines.find(r => r.id === data.routine_id);
          if (routine) {
            setLastNotification({
              routineId: data.routine_id,
              routineName: routine.name,
              status: 'started',
              timestamp: new Date(),
            });
          }
          
          return updatedRoutines;
        });
      }

      // Handle routine completed notification
      if (data.status === 'completed' && data.routine_id) {
        setRoutines(prevRoutines => {
          // Find routine name for notification
          const routine = prevRoutines.find(r => r.id === data.routine_id);
          if (routine) {
            setLastNotification({
              routineId: data.routine_id,
              routineName: routine.name,
              status: 'completed',
              timestamp: new Date(),
            });
          }
          
          return prevRoutines;
        });
      }

      // Handle routine updated notification (from another client)
      if (data.routine) {
        const adaptedRoutine = adaptRoutine(data.routine as BackendRoutine);
        setRoutines(prevRoutines => {
          const exists = prevRoutines.some(r => r.id === adaptedRoutine.id);
          if (exists) {
            return prevRoutines.map(r =>
              r.id === adaptedRoutine.id ? adaptedRoutine : r
            );
          } else {
            return [...prevRoutines, adaptedRoutine];
          }
        });
      }
    } catch (err) {
      console.error('[useRoutines] Error handling routine notification:', err);
    }
  }, []);

  /**
   * Initial fetch and WebSocket subscription
   */
  useEffect(() => {
    isMountedRef.current = true;

    // Fetch initial routines
    fetchRoutines();

    // Subscribe to WebSocket routine notifications if autoConnect is enabled
    let unsubscribe: (() => void) | null = null;

    if (autoConnect) {
      // Connect WebSocket if not already connected
      if (!wsService.isConnected()) {
        wsService.connect();
      }

      // Subscribe to routine messages
      unsubscribe = wsService.subscribe('routine', handleRoutineNotification);
    }

    // Cleanup
    return () => {
      isMountedRef.current = false;
      
      if (unsubscribe) {
        unsubscribe();
      }
    };
  }, [autoConnect, fetchRoutines, handleRoutineNotification]);

  return {
    routines,
    loading,
    error,
    refetch: fetchRoutines,
    createRoutine,
    updateRoutine,
    deleteRoutine,
    triggerRoutine,
    lastNotification,
  };
}
