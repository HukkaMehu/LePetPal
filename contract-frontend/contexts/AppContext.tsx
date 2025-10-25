'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { AppConfig, CommandStatus, ConnectionStatus, Toast } from '@/types';

interface AppContextType {
  config: AppConfig;
  setConfig: (config: AppConfig) => void;
  currentCommand: CommandStatus | null;
  setCurrentCommand: (status: CommandStatus | null) => void;
  isExecuting: boolean;
  error: string | null;
  setError: (error: string | null) => void;
  connectionStatus: ConnectionStatus;
  setConnectionStatus: (status: ConnectionStatus) => void;
  toasts: Toast[];
  addToast: (message: string) => void;
  removeToast: (id: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [config, setConfigState] = useState<AppConfig>({
    baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000',
  });
  
  const [currentCommand, setCurrentCommand] = useState<CommandStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    status: 'disconnected',
  });
  const [toasts, setToasts] = useState<Toast[]>([]);

  // Load config from localStorage on mount
  useEffect(() => {
    const savedConfig = localStorage.getItem('lepetpal_config');
    if (savedConfig) {
      try {
        setConfigState(JSON.parse(savedConfig));
      } catch (e) {
        console.error('Failed to parse saved config:', e);
      }
    }
  }, []);

  // Save config to localStorage when it changes
  const setConfig = (newConfig: AppConfig) => {
    setConfigState(newConfig);
    localStorage.setItem('lepetpal_config', JSON.stringify(newConfig));
  };

  const isExecuting = currentCommand?.state === 'executing';

  // Add toast with auto-dismiss after 5 seconds
  const addToast = (message: string) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const newToast: Toast = {
      id,
      message,
      timestamp: Date.now(),
    };
    
    setToasts((prev) => [...prev, newToast]);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      removeToast(id);
    }, 5000);
  };

  // Remove toast by id
  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };

  return (
    <AppContext.Provider
      value={{
        config,
        setConfig,
        currentCommand,
        setCurrentCommand,
        isExecuting,
        error,
        setError,
        connectionStatus,
        setConnectionStatus,
        toasts,
        addToast,
        removeToast,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
