/**
 * useCommandExecution - Hook for executing commands with retry logic
 * 
 * Implements:
 * - Task 17.1: POST to /command endpoint with command string
 * - Task 17.2: 409 busy retry with exponential backoff (500ms, 1s, 2s with jitter)
 * - Task 17.3: Error handling for 400, 500, and network errors
 * 
 * Requirements: 6.2, 7.3, 7.5
 */

import { useCallback, useRef, useState } from 'react';
import { useApp } from '@/contexts/AppContext';

const MAX_RETRY_ATTEMPTS = 5;
const RETRY_DELAYS = [500, 1000, 2000]; // Base delays in ms for exponential backoff

// Add jitter to prevent thundering herd
function addJitter(delay: number): number {
  return delay + Math.random() * 200;
}

// Sleep utility for retry delays
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function useCommandExecution() {
  const { config, setCurrentCommand, setError, addToast } = useApp();
  const sseSetRequestIdRef = useRef<((requestId: string | null) => void) | null>(null);
  const [retryMessage, setRetryMessage] = useState<string | null>(null);

  // Register the SSE setRequestId function
  const registerSSEClient = useCallback((setRequestId: (requestId: string | null) => void) => {
    sseSetRequestIdRef.current = setRequestId;
  }, []);

  // Execute a command with retry logic
  const executeCommand = useCallback(async (command: string): Promise<string | null> => {
    let attempt = 0;
    
    try {
      setError(null);
      setRetryMessage(null);
      
      while (attempt < MAX_RETRY_ATTEMPTS) {
        try {
          const headers: HeadersInit = {
            'Content-Type': 'application/json',
          };
          
          // Use X-LePetPal-Token header per design spec
          if (config.authToken) {
            headers['X-LePetPal-Token'] = config.authToken;
          }

          const response = await fetch(`${config.baseUrl}/command`, {
            method: 'POST',
            headers,
            body: JSON.stringify({ command }),
          });

          // Task 17.2: Handle 409 busy with retry
          if (response.status === 409) {
            attempt++;
            
            if (attempt >= MAX_RETRY_ATTEMPTS) {
              throw new Error('System is busy. Please try again later or use Go Home to interrupt.');
            }
            
            // Calculate delay with exponential backoff and jitter
            const delayIndex = Math.min(attempt - 1, RETRY_DELAYS.length - 1);
            const baseDelay = RETRY_DELAYS[delayIndex];
            const delayWithJitter = addJitter(baseDelay);
            
            // Display retry message
            setRetryMessage(`System busy, retrying in ${Math.round(delayWithJitter / 1000)}s... (attempt ${attempt}/${MAX_RETRY_ATTEMPTS})`);
            
            await sleep(delayWithJitter);
            continue; // Retry the request
          }

          // Task 17.3: Handle 400 validation errors
          if (response.status === 400) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Invalid command parameters');
          }

          // Task 17.3: Handle 500 server errors
          if (response.status === 500) {
            throw new Error('Server error. Please try again later.');
          }

          // Handle other error status codes
          if (!response.ok) {
            throw new Error(`Command failed: ${response.statusText}`);
          }

          // Success - parse response and extract request_id
          const data = await response.json();
          const requestId = data.request_id;
          
          // Clear retry message on success
          setRetryMessage(null);
          
          // Task 17.1: Update global state with request_id and executing status
          setCurrentCommand({
            request_id: requestId,
            state: 'executing',
            message: 'Command started',
          });

          // Notify SSE client of the new request ID for polling fallback
          if (sseSetRequestIdRef.current) {
            sseSetRequestIdRef.current(requestId);
          }

          return requestId;
          
        } catch (err) {
          // Task 17.3: Handle network errors
          if (err instanceof TypeError && err.message.includes('fetch')) {
            throw new Error('Connection failed. Please check your network and backend URL.');
          }
          
          // Re-throw other errors (400, 500, etc.)
          throw err;
        }
      }
      
      // Should not reach here, but handle edge case
      throw new Error('Maximum retry attempts reached');
      
    } catch (err) {
      setRetryMessage(null);
      const errorMessage = err instanceof Error ? err.message : 'Failed to execute command';
      setError(errorMessage);
      addToast(errorMessage);
      return null;
    }
  }, [config.baseUrl, config.authToken, setCurrentCommand, setError, addToast]);

  return {
    executeCommand,
    registerSSEClient,
    retryMessage,
  };
}
