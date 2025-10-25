/**
 * useAnalytics Hook
 * 
 * Custom React hook for fetching and managing analytics data.
 * Fetches daily metrics, streaks, and summary data from the backend.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient, adaptAnalytics, getDateRange } from '../services';
import { AnalyticsData } from '../types';

// ============================================================================
// Types
// ============================================================================

interface UseAnalyticsOptions {
  days?: number;
  userId?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface UseAnalyticsReturn {
  data: AnalyticsData | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

// ============================================================================
// Hook Implementation
// ============================================================================

/**
 * Hook for fetching and managing analytics data
 */
export function useAnalytics(options: UseAnalyticsOptions = {}): UseAnalyticsReturn {
  const {
    days = 7,
    userId = '00000000-0000-0000-0000-000000000000', // Default test user ID
    autoRefresh = false,
    refreshInterval = 60000, // 1 minute default
  } = options;

  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  
  const isMountedRef = useRef<boolean>(true);
  const refreshTimeoutRef = useRef<number | null>(null);

  /**
   * Fetch analytics data from the API
   */
  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch analytics summary which includes all necessary data
      const summary = await apiClient.getAnalyticsSummary(days, userId);
      
      if (isMountedRef.current) {
        // Transform backend data to frontend format
        const adaptedData = adaptAnalytics(summary);
        setData(adaptedData);
      }
    } catch (err) {
      if (isMountedRef.current) {
        setError(err as Error);
        console.error('[useAnalytics] Error fetching analytics:', err);
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  }, [days, userId]);

  /**
   * Set up auto-refresh if enabled
   */
  useEffect(() => {
    if (!autoRefresh) return;

    const refresh = async () => {
      await fetchAnalytics();
      
      if (isMountedRef.current) {
        refreshTimeoutRef.current = window.setTimeout(refresh, refreshInterval);
      }
    };

    refreshTimeoutRef.current = window.setTimeout(refresh, refreshInterval);

    return () => {
      if (refreshTimeoutRef.current !== null) {
        clearTimeout(refreshTimeoutRef.current);
        refreshTimeoutRef.current = null;
      }
    };
  }, [autoRefresh, refreshInterval, fetchAnalytics]);

  /**
   * Initial fetch
   */
  useEffect(() => {
    isMountedRef.current = true;

    fetchAnalytics();

    return () => {
      isMountedRef.current = false;
      
      if (refreshTimeoutRef.current !== null) {
        clearTimeout(refreshTimeoutRef.current);
        refreshTimeoutRef.current = null;
      }
    };
  }, [fetchAnalytics]);

  return {
    data,
    loading,
    error,
    refetch: fetchAnalytics,
  };
}
