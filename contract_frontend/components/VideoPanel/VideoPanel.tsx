'use client';

import { useState } from 'react';
import { useApp } from '@/contexts/AppContext';

export default function VideoPanel() {
  const { config } = useApp();
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [showOverlays, setShowOverlays] = useState(true);

  // Default video dimensions from environment or fallback to design spec defaults
  const width = process.env.NEXT_PUBLIC_DEFAULT_VIDEO_WIDTH || '1280';
  const height = process.env.NEXT_PUBLIC_DEFAULT_VIDEO_HEIGHT || '720';

  // Build video URL with all required query parameters
  const videoUrl = `${config.baseUrl}/video_feed?width=${width}&height=${height}&overlays=${showOverlays ? 1 : 0}`;

  const handleImageLoad = () => {
    setIsLoading(false);
    setHasError(false);
  };

  const handleImageError = () => {
    setIsLoading(false);
    setHasError(true);
  };

  const handleRetry = () => {
    setHasError(false);
    setIsLoading(true);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-3 sm:p-4">
      <div className="flex justify-between items-center mb-3 sm:mb-4">
        <h2 className="text-base sm:text-lg font-semibold text-gray-800">Live Video Feed</h2>
        <label className="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            checked={showOverlays}
            onChange={(e) => setShowOverlays(e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
          />
          <span className="text-xs sm:text-sm text-gray-700">Show Overlays</span>
        </label>
      </div>
      
      {/* Mobile: Full width with aspect ratio preservation */}
      {/* Desktop: Fixed max-width (640px) with aspect ratio preservation */}
      <div className="relative bg-gray-900 rounded-lg overflow-hidden aspect-video w-full md:max-w-[640px] md:mx-auto">
        {/* Loading Spinner */}
        {isLoading && !hasError && (
          <div className="absolute inset-0 flex items-center justify-center text-white">
            <div className="text-center">
              <div className="inline-block w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-3"></div>
              <p className="text-sm text-gray-400">Connecting to video stream...</p>
            </div>
          </div>
        )}

        {/* Error Overlay */}
        {hasError && (
          <div className="absolute inset-0 flex items-center justify-center text-white">
            <div className="text-center">
              <svg 
                className="w-16 h-16 mx-auto mb-3 text-red-500" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
                />
              </svg>
              <p className="text-lg font-semibold mb-2">Video Stream Unavailable</p>
              <p className="text-sm text-gray-400">Check your connection and base URL</p>
              <button
                onClick={handleRetry}
                className="mt-4 px-4 py-2 bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {/* Video Stream Image */}
        <img
          src={videoUrl}
          alt="Live video feed"
          className={`w-full h-full object-contain ${isLoading || hasError ? 'hidden' : ''}`}
          onLoad={handleImageLoad}
          onError={handleImageError}
        />
      </div>
    </div>
  );
}
