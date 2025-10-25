/**
 * useModels Hook
 * 
 * Custom React hook for fetching available models and switching active models.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient } from '../services';
import { ModelSwitchRequest } from '../types';
import { BackendModelsListResponse, BackendModelSwitchResponse } from '../types/backend';

// ============================================================================
// Types
// ============================================================================

interface UseModelsReturn {
  availableModels: BackendModelsListResponse['available_models'];
  activeModels: BackendModelsListResponse['active_models'];
  loading: boolean;
  error: Error | null;
  switchModels: (request: ModelSwitchRequest) => Promise<BackendModelSwitchResponse>;
  refetch: () => Promise<void>;
}

// ============================================================================
// Hook Implementation
// ============================================================================

/**
 * Hook for fetching available models and managing active model selection
 */
export function useModels(): UseModelsReturn {
  const [availableModels, setAvailableModels] = useState<BackendModelsListResponse['available_models']>([]);
  const [activeModels, setActiveModels] = useState<BackendModelsListResponse['active_models']>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  
  const isMountedRef = useRef<boolean>(true);

  /**
   * Fetch models from the API
   */
  const fetchModels = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.getModels();
      
      if (isMountedRef.current) {
        setAvailableModels(response.available_models);
        setActiveModels(response.active_models);
      }
    } catch (err) {
      if (isMountedRef.current) {
        setError(err as Error);
        console.error('[useModels] Error fetching models:', err);
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  }, []);

  /**
   * Switch active models
   */
  const switchModels = useCallback(async (request: ModelSwitchRequest): Promise<BackendModelSwitchResponse> => {
    try {
      const response = await apiClient.switchModels(request);
      
      if (isMountedRef.current && response.success) {
        // Update active models with the new configuration
        setActiveModels(response.active_models);
      }
      
      return response;
    } catch (err) {
      console.error('[useModels] Error switching models:', err);
      throw err;
    }
  }, []);

  /**
   * Initial fetch
   */
  useEffect(() => {
    isMountedRef.current = true;
    fetchModels();

    return () => {
      isMountedRef.current = false;
    };
  }, [fetchModels]);

  return {
    availableModels,
    activeModels,
    loading,
    error,
    switchModels,
    refetch: fetchModels,
  };
}
