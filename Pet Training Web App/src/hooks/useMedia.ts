/**
 * useMedia Hook
 * 
 * Custom React hook for fetching and managing media (clips and snapshots).
 * Supports pagination and filtering.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient, adaptMediaItems } from '../services';
import { MediaItem, MediaQueryParams } from '../types';

// ============================================================================
// Types
// ============================================================================

interface UseMediaOptions extends MediaQueryParams {
  autoLoad?: boolean;
}

interface UseMediaReturn {
  media: MediaItem[];
  loading: boolean;
  error: Error | null;
  hasMore: boolean;
  total: number;
  refetch: () => Promise<void>;
  loadMore: () => Promise<void>;
}

// ============================================================================
// Hook Implementation
// ============================================================================

/**
 * Hook for fetching and managing media with pagination
 */
export function useMedia(options: UseMediaOptions = {}): UseMediaReturn {
  const {
    autoLoad = true,
    type,
    startDate,
    endDate,
    tags,
    limit = 20,
    offset: initialOffset = 0,
  } = options;

  const [media, setMedia] = useState<MediaItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const [offset, setOffset] = useState<number>(initialOffset);
  const [total, setTotal] = useState<number>(0);
  const [hasMore, setHasMore] = useState<boolean>(true);
  
  const isMountedRef = useRef<boolean>(true);
  const isLoadingMoreRef = useRef<boolean>(false);

  /**
   * Fetch media from the API
   */
  const fetchMedia = useCallback(async (currentOffset: number = 0, append: boolean = false) => {
    try {
      if (!append) {
        setLoading(true);
      }
      setError(null);
      isLoadingMoreRef.current = true;

      const queryParams: MediaQueryParams = {
        type,
        startDate,
        endDate,
        tags,
        limit,
        offset: currentOffset,
      };

      // Fetch both clips and snapshots if no type filter is specified
      let allMedia: MediaItem[] = [];
      let totalCount = 0;

      if (!type || type === 'clip') {
        const clipsResponse = await apiClient.getClips({
          ...queryParams,
          type: undefined, // Remove type from query
        });
        const clips = adaptMediaItems(clipsResponse.clips, []);
        allMedia = [...allMedia, ...clips];
        totalCount += clipsResponse.total;
      }

      if (!type || type === 'snapshot') {
        const snapshotsResponse = await apiClient.getSnapshots({
          ...queryParams,
          type: undefined, // Remove type from query
        });
        const snapshots = adaptMediaItems([], snapshotsResponse.snapshots);
        allMedia = [...allMedia, ...snapshots];
        totalCount += snapshotsResponse.total;
      }

      // Sort by timestamp (newest first)
      allMedia.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());

      if (isMountedRef.current) {
        if (append) {
          setMedia(prevMedia => [...prevMedia, ...allMedia]);
        } else {
          setMedia(allMedia);
        }

        setTotal(totalCount);
        setHasMore(currentOffset + allMedia.length < totalCount);
      }
    } catch (err) {
      if (isMountedRef.current) {
        setError(err as Error);
        console.error('[useMedia] Error fetching media:', err);
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
        isLoadingMoreRef.current = false;
      }
    }
  }, [type, startDate, endDate, tags, limit]);

  /**
   * Refetch media from the beginning
   */
  const refetch = useCallback(async () => {
    setOffset(0);
    await fetchMedia(0, false);
  }, [fetchMedia]);

  /**
   * Load more media (pagination)
   */
  const loadMore = useCallback(async () => {
    if (isLoadingMoreRef.current || !hasMore) {
      return;
    }

    const newOffset = offset + limit;
    setOffset(newOffset);
    await fetchMedia(newOffset, true);
  }, [offset, limit, hasMore, fetchMedia]);

  /**
   * Initial fetch
   */
  useEffect(() => {
    isMountedRef.current = true;

    if (autoLoad) {
      fetchMedia(0, false);
    }

    return () => {
      isMountedRef.current = false;
    };
  }, [autoLoad, fetchMedia]);

  /**
   * Refetch when filter parameters change
   */
  useEffect(() => {
    if (autoLoad) {
      setOffset(0);
      fetchMedia(0, false);
    }
  }, [type, startDate, endDate, tags?.join(',')]); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    media,
    loading,
    error,
    hasMore,
    total,
    refetch,
    loadMore,
  };
}
