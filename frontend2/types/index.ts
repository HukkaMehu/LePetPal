// Type definitions for LePetPal MVP

export type CommandState = 'idle' | 'executing' | 'completed' | 'failed' | 'timeout' | 'interrupted';

export type CommandPhase = 
  | 'detect'
  | 'approach'
  | 'grasp'
  | 'lift'
  | 'drop'
  | 'ready_to_throw'
  | 'throwing'
  | 'returning_home';

export interface CommandStatus {
  request_id: string;
  state: CommandState;
  phase?: CommandPhase;
  confidence?: number;
  message: string;
  duration_ms?: number;
}

export interface CommandPreset {
  id: string;
  label: string;
  command: string;
  description?: string;
}

export interface AppConfig {
  baseUrl: string;
  authToken?: string;
}

export interface ConnectionStatus {
  status: 'disconnected' | 'connected' | 'error';
  message?: string;
}

export interface SSEEvent {
  type: 'command_update' | 'error' | 'connected';
  data: CommandStatus | { message: string };
}

export interface Toast {
  id: string;
  message: string;
  timestamp: number;
}
