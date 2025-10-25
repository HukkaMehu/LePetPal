'use client';

import { useApp } from '@/contexts/AppContext';
import { useEffect, useState } from 'react';

export default function StatusDisplay() {
  const { currentCommand, isExecuting, error } = useApp();
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [showBanner, setShowBanner] = useState(false);
  const [bannerDismissTimer, setBannerDismissTimer] = useState<NodeJS.Timeout | null>(null);

  // Duration counter - update every 100ms during execution
  useEffect(() => {
    if (!isExecuting || !currentCommand?.duration_ms) {
      setElapsedSeconds(0);
      return;
    }

    const interval = setInterval(() => {
      if (currentCommand?.duration_ms) {
        setElapsedSeconds(currentCommand.duration_ms / 1000);
      }
    }, 100);

    return () => clearInterval(interval);
  }, [isExecuting, currentCommand?.duration_ms]);

  // Final state banner - show on completed/failed/timeout/interrupted
  useEffect(() => {
    const isFinalState = currentCommand?.state && 
      ['completed', 'failed', 'timeout', 'interrupted'].includes(currentCommand.state);
    
    if (isFinalState && !isExecuting) {
      setShowBanner(true);
      
      // Auto-dismiss after 5 seconds
      const timer = setTimeout(() => {
        setShowBanner(false);
      }, 5000);
      
      setBannerDismissTimer(timer);
      
      return () => {
        if (timer) clearTimeout(timer);
      };
    }
  }, [currentCommand?.state, isExecuting]);

  // Global status chip helpers
  const getStatusChipColor = () => {
    if (error) return 'bg-red-500 text-white';
    if (isExecuting) return 'bg-blue-500 text-white';
    return 'bg-green-500 text-white';
  };

  const getStatusLabel = () => {
    if (error) return 'Error';
    if (isExecuting) return 'Executing';
    return 'Idle';
  };

  // Phase indicator helper
  const getPhaseDisplay = () => {
    if (!currentCommand?.phase) return null;
    
    const phaseLabels: Record<string, string> = {
      detect: 'Detecting ball...',
      approach: 'Approaching target...',
      grasp: 'Grasping object...',
      lift: 'Lifting object...',
      drop: 'Dropping object...',
      ready_to_throw: 'Ready to throw',
      throwing: 'Throwing...',
      returning_home: 'Returning home...',
    };
    
    return phaseLabels[currentCommand.phase] || currentCommand.phase;
  };

  // Final state banner helpers
  const getBannerColor = () => {
    if (currentCommand?.state === 'completed') return 'bg-green-500';
    return 'bg-red-500';
  };

  const getBannerMessage = () => {
    if (currentCommand?.state === 'completed') {
      return currentCommand.message || 'Command completed successfully!';
    }
    if (currentCommand?.state === 'failed') {
      return currentCommand.message || 'Command failed';
    }
    if (currentCommand?.state === 'timeout') {
      return currentCommand.message || 'Command timed out';
    }
    if (currentCommand?.state === 'interrupted') {
      return currentCommand.message || 'Command interrupted';
    }
    return currentCommand?.message || 'Unknown state';
  };

  const handleDismissBanner = () => {
    setShowBanner(false);
    if (bannerDismissTimer) {
      clearTimeout(bannerDismissTimer);
      setBannerDismissTimer(null);
    }
  };

  return (
    <>
      {/* Global status chip - positioned in top-right corner */}
      <div className="fixed top-3 right-3 sm:top-4 sm:right-4 z-50">
        <div className={`px-3 sm:px-4 py-2 rounded-full shadow-lg flex items-center gap-2 ${getStatusChipColor()}`}>
          {isExecuting && (
            <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          )}
          <span className="font-medium text-xs sm:text-sm">{getStatusLabel()}</span>
        </div>
      </div>

      {/* Final state banner */}
      {showBanner && (
        <div className="fixed top-16 sm:top-20 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-md px-4">
          <div className={`${getBannerColor()} text-white rounded-lg shadow-lg p-3 sm:p-4 flex items-center justify-between`}>
            <p className="font-medium text-sm sm:text-base">{getBannerMessage()}</p>
            <button
              onClick={handleDismissBanner}
              className="ml-3 sm:ml-4 text-white hover:text-gray-200 transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center touch-manipulation"
              aria-label="Dismiss"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Status display panel */}
      <div className="bg-white rounded-lg shadow-md p-3 sm:p-4">
        <h2 className="text-base sm:text-lg font-semibold text-gray-800 mb-3 sm:mb-4">Status</h2>
        
        {/* Phase indicator - only show during execution */}
        {isExecuting && currentCommand?.phase && (
          <div className="mb-3 sm:mb-4">
            <p className="text-xs sm:text-sm text-gray-600 mb-1">Current Phase</p>
            <p className="text-base sm:text-lg font-medium text-blue-600">{getPhaseDisplay()}</p>
          </div>
        )}

        {/* Confidence meter - only visible during detect phase */}
        {isExecuting && currentCommand?.phase === 'detect' && currentCommand?.confidence !== undefined && (
          <div className="mb-3 sm:mb-4">
            <div className="flex justify-between items-center mb-1">
              <p className="text-xs sm:text-sm text-gray-600">Confidence</p>
              <p className="text-xs sm:text-sm font-medium text-gray-800">
                {(currentCommand.confidence * 100).toFixed(0)}%
              </p>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 sm:h-3 overflow-hidden">
              <div
                className="bg-blue-500 h-full transition-all duration-300 rounded-full"
                style={{ width: `${currentCommand.confidence * 100}%` }}
              />
            </div>
          </div>
        )}

        {/* Duration counter - show during execution */}
        {isExecuting && (
          <div className="mb-3 sm:mb-4">
            <p className="text-xs sm:text-sm text-gray-600 mb-1">Elapsed Time</p>
            <p className="text-xl sm:text-2xl font-bold text-gray-800 tabular-nums">
              {elapsedSeconds.toFixed(1)}s
            </p>
          </div>
        )}

        {/* Error display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-2 sm:p-3">
            <p className="text-xs sm:text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Command message */}
        {currentCommand && !error && (
          <div className="text-xs sm:text-sm text-gray-600">
            <p>{currentCommand.message}</p>
          </div>
        )}
      </div>
    </>
  );
}
