import { useEffect, useState } from 'react';
import { WifiOff } from 'lucide-react';
import { apiClient } from '../services/api';
import { Alert, AlertDescription } from './ui/alert';

interface ConnectionStatusBannerProps {
  checkIntervalMs?: number;
}

export default function ConnectionStatusBanner({ 
  checkIntervalMs = 10000 
}: ConnectionStatusBannerProps) {
  const [isOnline, setIsOnline] = useState(true);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const [isChecking, setIsChecking] = useState(false);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;
    let isMounted = true;

    const checkConnection = async () => {
      if (isChecking) return;
      
      setIsChecking(true);
      
      try {
        // Try to fetch system status to check backend connection
        await apiClient.getSystemStatus();
        
        if (isMounted) {
          setIsOnline(true);
          setReconnectAttempts(0);
        }
      } catch (error) {
        if (isMounted) {
          setIsOnline(false);
          setReconnectAttempts(prev => prev + 1);
        }
      } finally {
        if (isMounted) {
          setIsChecking(false);
        }
      }
    };

    // Initial check
    checkConnection();

    // Set up periodic checks
    intervalId = setInterval(checkConnection, checkIntervalMs);

    // Listen to browser online/offline events
    const handleOnline = () => {
      if (isMounted) {
        checkConnection();
      }
    };

    const handleOffline = () => {
      if (isMounted) {
        setIsOnline(false);
      }
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      isMounted = false;
      clearInterval(intervalId);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [checkIntervalMs, isChecking]);

  // Don't render anything if connection is good
  if (isOnline) {
    return null;
  }

  return (
    <Alert 
      variant="destructive" 
      className="fixed top-0 left-0 right-0 z-50 rounded-none border-x-0 border-t-0"
    >
      <WifiOff className="h-4 w-4" />
      <AlertDescription className="flex items-center justify-between">
        <span>
          Connection lost. Attempting to reconnect...
          {reconnectAttempts > 0 && ` (Attempt ${reconnectAttempts})`}
        </span>
        <button
          onClick={() => window.location.reload()}
          className="text-sm underline hover:no-underline"
        >
          Refresh Page
        </button>
      </AlertDescription>
    </Alert>
  );
}
