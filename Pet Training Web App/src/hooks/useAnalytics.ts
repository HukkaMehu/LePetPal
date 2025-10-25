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
// Mock Data
// ============================================================================

/**
 * Generate mock analytics data for demo purposes
 */
function generateMockAnalytics(days: number): AnalyticsData {
  const mockData: AnalyticsData = {
    timeInFrame: [],
    activityLevel: [],
    behaviors: [
      { name: 'Sit', count: 45 },
      { name: 'Stand', count: 32 },
      { name: 'Lie Down', count: 28 },
      { name: 'Fetch', count: 15 },
      { name: 'Bark', count: 8 },
    ],
    fetchSuccess: [],
    barkFrequency: [],
    skillProgress: [
      { skill: 'Sit Command', success: 42, total: 50 },
      { skill: 'Recall', success: 28, total: 35 },
      { skill: 'Training Consistency', success: days, total: 30 },
    ],
  };

  // Generate time in frame data (24 hours)
  for (let hour = 0; hour < 24; hour++) {
    const baseMinutes = hour >= 6 && hour <= 22 ? 30 : 5;
    const variance = Math.random() * 20 - 10;
    mockData.timeInFrame.push({
      hour: `${hour}:00`,
      minutes: Math.max(0, Math.round(baseMinutes + variance)),
    });
  }

  // Generate activity level data (last N days)
  const today = new Date();
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split('T')[0];
    
    const calmMinutes = Math.round(180 + Math.random() * 120);
    const activeMinutes = Math.round(60 + Math.random() * 60);
    
    mockData.activityLevel.push({
      date: dateStr,
      calm: calmMinutes,
      active: activeMinutes,
    });
  }

  // Generate fetch success data
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split('T')[0];
    
    const total = Math.round(3 + Math.random() * 5);
    const success = Math.round(total * (0.6 + Math.random() * 0.3));
    
    mockData.fetchSuccess.push({
      date: dateStr,
      success,
      total,
    });
  }

  // Generate bark frequency data (24 hours)
  for (let hour = 0; hour < 24; hour++) {
    const baseCount = hour >= 7 && hour <= 20 ? 3 : 1;
    const variance = Math.random() * 3;
    mockData.barkFrequency.push({
      hour: `${hour}:00`,
      count: Math.round(baseCount + variance),
    });
  }

  return mockData;
}

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

      try {
        // Try to fetch analytics summary from backend
        const summary = await apiClient.getAnalyticsSummary(days, userId);
        
        if (isMountedRef.current) {
          // Transform backend data to frontend format
          const adaptedData = adaptAnalytics(summary);
          setData(adaptedData);
        }
      } catch (apiError) {
        // If backend is unavailable, use mock data for demo
        console.warn('[useAnalytics] Backend unavailable, using mock data:', apiError);
        
        if (isMountedRef.current) {
          const mockData = generateMockAnalytics(days);
          setData(mockData);
        }
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
