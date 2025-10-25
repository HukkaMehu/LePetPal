'use client';

import { useState } from 'react';
import { useApp } from '@/contexts/AppContext';
import { useCommandExecution } from '@/lib/useCommandExecution';
import { CommandPreset } from '@/types';

// Command presets mapped to exact API command strings per design spec
const COMMAND_PRESETS: CommandPreset[] = [
  {
    id: 'play_ball',
    label: 'Play with Ball',
    command: 'pick up the ball',
    description: 'Execute ball manipulation sequence',
  },
  {
    id: 'give_treat',
    label: 'Give Treat',
    command: 'get the treat',
    description: 'Dispense treat and execute retrieval',
  },
  {
    id: 'go_home',
    label: 'Go Home',
    command: 'go home',
    description: 'Return to home position (interrupt)',
  },
  {
    id: 'speak',
    label: 'Speak',
    command: 'speak',
    description: 'Send encouragement message',
  },
];

export default function CommandBar() {
  const { isExecuting } = useApp();
  const { executeCommand, retryMessage } = useCommandExecution();
  const [activeButtonId, setActiveButtonId] = useState<string | null>(null);

  const handleExecuteCommand = async (preset: CommandPreset) => {
    setActiveButtonId(preset.id);
    const requestId = await executeCommand(preset.command);
    
    // Clear active button if command failed to start
    if (!requestId) {
      setActiveButtonId(null);
    }
  };

  // Clear active button when command completes
  if (activeButtonId && !isExecuting) {
    setActiveButtonId(null);
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-3 sm:p-4">
      <h2 className="text-base sm:text-lg font-semibold text-gray-800 mb-3 sm:mb-4">Command Presets</h2>
      
      {/* Display retry message when system is busy */}
      {retryMessage && (
        <div className="mb-3 p-2 bg-yellow-50 border border-yellow-200 rounded-md text-xs sm:text-sm text-yellow-800">
          {retryMessage}
        </div>
      )}
      
      {/* Minimum 44px tap targets with 8px spacing between buttons */}
      <div className="grid grid-cols-2 gap-2 sm:gap-3">
        {COMMAND_PRESETS.map((preset) => {
          const isGoHome = preset.id === 'go_home';
          const isDisabled = isExecuting && !isGoHome;
          const isActive = activeButtonId === preset.id && isExecuting;
          
          return (
            <button
              key={preset.id}
              onClick={() => handleExecuteCommand(preset)}
              disabled={isDisabled}
              className={`
                min-h-[44px] px-3 sm:px-4 py-3 rounded-md font-medium transition-colors
                flex items-center justify-center gap-2
                text-sm sm:text-base
                ${isGoHome 
                  ? 'bg-red-600 text-white hover:bg-red-700 disabled:bg-red-300' 
                  : 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-300 disabled:text-gray-500'
                }
                disabled:cursor-not-allowed
                touch-manipulation
              `}
              title={preset.description}
            >
              {isActive && (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              )}
              {preset.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
