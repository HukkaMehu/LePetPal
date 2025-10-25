'use client';

/**
 * SSEProvider - Client component that initializes SSE connection
 * 
 * This component should be placed high in the component tree to ensure
 * SSE connection is established early and maintained throughout the app lifecycle.
 * 
 * Integrates with useCommandExecution to provide request_id to SSE client for polling fallback.
 */

import { useSSEClient } from '@/lib/useSSEClient';
import { useCommandExecution } from '@/lib/useCommandExecution';
import { ReactNode, createContext, useContext, useEffect } from 'react';

interface SSEContextType {
  setRequestId: (requestId: string | null) => void;
  getConnectionStatus: () => { connected: boolean; mode: 'sse' | 'polling' | 'disconnected' };
}

const SSEContext = createContext<SSEContextType | undefined>(undefined);

interface SSEProviderProps {
  children: ReactNode;
}

export default function SSEProvider({ children }: SSEProviderProps) {
  // Initialize SSE client - this hook manages the connection lifecycle
  const { setRequestId, getConnectionStatus } = useSSEClient();
  const { registerSSEClient } = useCommandExecution();

  // Register the SSE setRequestId function with command execution hook
  useEffect(() => {
    registerSSEClient(setRequestId);
  }, [registerSSEClient, setRequestId]);

  return (
    <SSEContext.Provider value={{ setRequestId, getConnectionStatus }}>
      {children}
    </SSEContext.Provider>
  );
}

export function useSSE() {
  const context = useContext(SSEContext);
  if (context === undefined) {
    throw new Error('useSSE must be used within an SSEProvider');
  }
  return context;
}
