'use client';

import { useState, useEffect } from 'react';
import { useApp } from '@/contexts/AppContext';

export default function ConfigPanel() {
  const { config, setConfig, setConnectionStatus, addToast } = useApp();
  const [baseUrl, setBaseUrl] = useState(config.baseUrl);
  const [authToken, setAuthToken] = useState(config.authToken || '');
  const [isExpanded, setIsExpanded] = useState(false);
  const [urlError, setUrlError] = useState<string | null>(null);
  const [showToken, setShowToken] = useState(false);
  const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [testMessage, setTestMessage] = useState<string | null>(null);

  // Sync local state with config when it changes
  useEffect(() => {
    setBaseUrl(config.baseUrl);
    setAuthToken(config.authToken || '');
  }, [config]);

  // Validate URL format
  const validateUrl = (url: string): boolean => {
    if (!url.trim()) {
      setUrlError('Base URL is required');
      return false;
    }

    try {
      const urlObj = new URL(url);
      if (!['http:', 'https:'].includes(urlObj.protocol)) {
        setUrlError('URL must use http:// or https://');
        return false;
      }
      setUrlError(null);
      return true;
    } catch {
      setUrlError('Invalid URL format (e.g., http://192.168.1.100:5000)');
      return false;
    }
  };

  // Handle URL blur event for validation
  const handleUrlBlur = () => {
    validateUrl(baseUrl);
  };

  // Handle save button click
  const handleSave = () => {
    if (!validateUrl(baseUrl)) {
      return;
    }

    setConfig({
      baseUrl: baseUrl.trim(),
      authToken: authToken.trim() || undefined,
    });
    setTestStatus('idle');
    setTestMessage(null);
    setIsExpanded(false);
  };

  // Handle reset button click
  const handleReset = () => {
    if (confirm('Are you sure you want to clear the saved configuration?')) {
      localStorage.removeItem('lepetpal_config');
      const defaultConfig = {
        baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000',
      };
      setConfig(defaultConfig);
      setBaseUrl(defaultConfig.baseUrl);
      setAuthToken('');
      setUrlError(null);
      setTestStatus('idle');
      setTestMessage(null);
      setConnectionStatus({ status: 'disconnected' });
    }
  };

  // Test connection to backend
  const handleTestConnection = async () => {
    if (!validateUrl(baseUrl)) {
      return;
    }

    setTestStatus('testing');
    setTestMessage(null);

    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };

      if (authToken.trim()) {
        headers['X-LePetPal-Token'] = authToken.trim();
      }

      const response = await fetch(`${baseUrl.trim()}/health`, {
        method: 'GET',
        headers,
        signal: AbortSignal.timeout(5000), // 5 second timeout
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.status === 'ok') {
        setTestStatus('success');
        setTestMessage(`Connected successfully! API v${data.api}, ${data.version}`);
        setConnectionStatus({ 
          status: 'connected', 
          message: `API v${data.api}, ${data.version}` 
        });
      } else {
        setTestStatus('error');
        setTestMessage('Unexpected response from server');
        setConnectionStatus({ 
          status: 'error', 
          message: 'Unexpected response from server' 
        });
      }
    } catch (error) {
      setTestStatus('error');
      let errorMessage = 'Connection failed - unknown error';
      
      if (error instanceof Error) {
        if (error.name === 'TimeoutError') {
          errorMessage = 'Connection timeout - server not responding';
        } else if (error.message.includes('Failed to fetch')) {
          errorMessage = 'Cannot reach server - check URL and network';
        } else {
          errorMessage = `Connection failed: ${error.message}`;
        }
      }
      
      setTestMessage(errorMessage);
      setConnectionStatus({ status: 'error', message: errorMessage });
      addToast(errorMessage);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-3 sm:p-4">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex justify-between items-center text-left font-semibold text-gray-800 min-h-[44px] touch-manipulation"
      >
        <span className="text-base sm:text-lg">Configuration</span>
        <span className="text-xl">{isExpanded ? '−' : '+'}</span>
      </button>
      
      {isExpanded && (
        <div className="mt-4 space-y-4">
          {/* Base URL Input */}
          <div>
            <label htmlFor="baseUrl" className="block text-sm font-medium text-gray-700 mb-1">
              Base URL <span className="text-red-500">*</span>
            </label>
            <input
              id="baseUrl"
              type="text"
              value={baseUrl}
              onChange={(e) => {
                setBaseUrl(e.target.value);
                if (urlError) setUrlError(null);
              }}
              onBlur={handleUrlBlur}
              placeholder="http://192.168.1.100:5000"
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 ${
                urlError 
                  ? 'border-red-500 focus:ring-red-500' 
                  : 'border-gray-300 focus:ring-blue-500'
              }`}
            />
            {urlError && (
              <p className="mt-1 text-sm text-red-600">{urlError}</p>
            )}
          </div>
          
          {/* Auth Token Input */}
          <div>
            <label htmlFor="authToken" className="block text-sm font-medium text-gray-700 mb-1">
              Auth Token (Optional)
            </label>
            <div className="relative">
              <input
                id="authToken"
                type={showToken ? 'text' : 'password'}
                value={authToken}
                onChange={(e) => setAuthToken(e.target.value)}
                placeholder="Optional authentication token"
                className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="button"
                onClick={() => setShowToken(!showToken)}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                aria-label={showToken ? 'Hide token' : 'Show token'}
              >
                {showToken ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                )}
              </button>
            </div>
          </div>

          {/* Connection Status Message */}
          {testMessage && (
            <div className={`p-3 rounded-md text-sm ${
              testStatus === 'success' 
                ? 'bg-green-50 text-green-800 border border-green-200' 
                : 'bg-red-50 text-red-800 border border-red-200'
            }`}>
              {testMessage}
            </div>
          )}
          
          {/* Action Buttons - minimum 44px tap targets with 8px spacing */}
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              disabled={!!urlError}
              className="flex-1 bg-blue-600 text-white min-h-[44px] py-2 px-3 sm:px-4 rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed text-sm sm:text-base touch-manipulation"
            >
              Save
            </button>
            <button
              onClick={handleTestConnection}
              disabled={testStatus === 'testing' || !!urlError}
              className="flex-1 bg-green-600 text-white min-h-[44px] py-2 px-3 sm:px-4 rounded-md hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed text-sm sm:text-base touch-manipulation"
            >
              {testStatus === 'testing' ? 'Testing...' : 'Test Connection'}
            </button>
          </div>

          <button
            onClick={handleReset}
            className="w-full bg-gray-200 text-gray-700 min-h-[44px] py-2 px-3 sm:px-4 rounded-md hover:bg-gray-300 transition-colors text-sm sm:text-base touch-manipulation"
          >
            Reset Configuration
          </button>
        </div>
      )}
    </div>
  );
}
