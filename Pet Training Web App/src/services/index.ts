/**
 * Services Module
 * 
 * Central export point for all service layer modules
 */

export { APIClient, apiClient } from './api';
export { WebSocketService, wsService } from './websocket';
export type { ConnectionState, EventCallback } from './websocket';
export {
  adaptEvent,
  adaptEvents,
  adaptRoutine,
  adaptRoutines,
  adaptClip,
  adaptSnapshot,
  adaptMediaItems,
  adaptSystemStatus,
  adaptAnalytics,
  adaptAnalyticsFromMetrics,
  formatDateForAPI,
  parseDateFromAPI,
  getDateRange,
} from './adapters';
