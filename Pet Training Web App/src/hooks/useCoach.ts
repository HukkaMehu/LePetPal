/**
 * useCoach Hook
 * 
 * Custom React hook for interacting with the AI coach service.
 * Supports both regular and streaming responses, maintains chat history.
 */

import { useState, useCallback, useRef } from 'react';
import { apiClient } from '../services';

// ============================================================================
// Types
// ============================================================================

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface UseCoachOptions {
  maxHistoryLength?: number;
  useStreaming?: boolean;
}

interface UseCoachReturn {
  messages: ChatMessage[];
  loading: boolean;
  error: Error | null;
  sendMessage: (message: string, context?: string) => Promise<void>;
  clearHistory: () => void;
  isStreaming: boolean;
}

// ============================================================================
// Hook Implementation
// ============================================================================

/**
 * Hook for interacting with the AI coach
 */
export function useCoach(options: UseCoachOptions = {}): UseCoachReturn {
  const {
    maxHistoryLength = 50,
    useStreaming = true,
  } = options;

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  
  const messageIdCounterRef = useRef<number>(0);
  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * Generate a unique message ID
   */
  const generateMessageId = useCallback((): string => {
    messageIdCounterRef.current += 1;
    return `msg-${Date.now()}-${messageIdCounterRef.current}`;
  }, []);

  /**
   * Add a message to the chat history
   */
  const addMessage = useCallback((role: 'user' | 'assistant', content: string) => {
    const message: ChatMessage = {
      id: generateMessageId(),
      role,
      content,
      timestamp: new Date(),
    };

    setMessages(prevMessages => {
      const newMessages = [...prevMessages, message];
      
      // Trim history if it exceeds max length
      if (newMessages.length > maxHistoryLength) {
        return newMessages.slice(newMessages.length - maxHistoryLength);
      }
      
      return newMessages;
    });

    return message;
  }, [generateMessageId, maxHistoryLength]);

  /**
   * Update the last assistant message (used for streaming)
   */
  const updateLastMessage = useCallback((content: string) => {
    setMessages(prevMessages => {
      if (prevMessages.length === 0) return prevMessages;

      const lastMessage = prevMessages[prevMessages.length - 1];
      if (lastMessage.role !== 'assistant') return prevMessages;

      return [
        ...prevMessages.slice(0, -1),
        { ...lastMessage, content },
      ];
    });
  }, []);

  /**
   * Send a message to the AI coach (streaming version)
   */
  const sendMessageStreaming = useCallback(async (message: string, context?: string) => {
    try {
      setLoading(true);
      setError(null);
      setIsStreaming(true);

      // Add user message to history
      addMessage('user', message);

      // Create placeholder for assistant response
      const assistantMessageId = generateMessageId();
      setMessages(prevMessages => [
        ...prevMessages,
        {
          id: assistantMessageId,
          role: 'assistant',
          content: '',
          timestamp: new Date(),
        },
      ]);

      // Stream the response
      let fullResponse = '';
      
      for await (const chunk of apiClient.streamCoachMessage(message, context)) {
        fullResponse += chunk;
        updateLastMessage(fullResponse);
      }

      setIsStreaming(false);
    } catch (err) {
      setError(err as Error);
      console.error('[useCoach] Error sending message (streaming):', err);

      // Add error message
      addMessage('assistant', 'Sorry, I encountered an error. The AI service may be unavailable. Please try again later.');
      
      setIsStreaming(false);
    } finally {
      setLoading(false);
    }
  }, [addMessage, generateMessageId, updateLastMessage]);

  /**
   * Send a message to the AI coach (non-streaming version)
   */
  const sendMessageNonStreaming = useCallback(async (message: string, context?: string) => {
    try {
      setLoading(true);
      setError(null);

      // Add user message to history
      addMessage('user', message);

      // Send message and wait for response
      const response = await apiClient.sendCoachMessage(message, context);

      // Add assistant response to history
      addMessage('assistant', response.response);
    } catch (err) {
      setError(err as Error);
      console.error('[useCoach] Error sending message:', err);

      // Add error message
      addMessage('assistant', 'Sorry, I encountered an error. The AI service may be unavailable. Please try again later.');
    } finally {
      setLoading(false);
    }
  }, [addMessage]);

  /**
   * Send a message to the AI coach
   */
  const sendMessage = useCallback(async (message: string, context?: string) => {
    // Cancel any ongoing streaming
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    if (useStreaming) {
      await sendMessageStreaming(message, context);
    } else {
      await sendMessageNonStreaming(message, context);
    }
  }, [useStreaming, sendMessageStreaming, sendMessageNonStreaming]);

  /**
   * Clear chat history
   */
  const clearHistory = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearHistory,
    isStreaming,
  };
}
