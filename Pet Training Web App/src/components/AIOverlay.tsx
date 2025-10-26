import { useEffect, useState, useRef } from 'react';
import { config } from '../config/env';
import { Detection, WebSocketMessage } from '../types';

interface AIOverlayProps {
  enabled: boolean;
  videoWidth: number;
  videoHeight: number;
}

export default function AIOverlay({ enabled, videoWidth, videoHeight }: AIOverlayProps) {
  const [detections, setDetections] = useState<Detection[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!enabled) return;

    // Connect to WebSocket for AI detections
    const wsUrl = config.wsURL;
    
    console.log('[AIOverlay] Connecting to WebSocket:', wsUrl);
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[AIOverlay] WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        
        // Listen for AI detection messages
        if (message.type === 'ai_detections' && message.data?.detections) {
          console.log('[AIOverlay] Received detections:', message.data.detections);
          setDetections(message.data.detections);
        }
      } catch (error) {
        console.error('[AIOverlay] Error parsing WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('[AIOverlay] WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('[AIOverlay] WebSocket closed');
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [enabled]);

  if (!enabled || detections.length === 0) {
    return null;
  }

  return (
    <>
      {detections.map((detection, index) => {
        // Convert normalized coordinates (0-1) to pixel coordinates
        const left = detection.box.x * videoWidth;
        const top = detection.box.y * videoHeight;
        const width = detection.box.w * videoWidth;
        const height = detection.box.h * videoHeight;

        // Choose color based on class
        const color = detection.class_name === 'person' ? 'rgb(59, 130, 246)' : 'rgb(34, 197, 94)';
        const bgColor = detection.class_name === 'person' ? 'rgba(59, 130, 246, 0.2)' : 'rgba(34, 197, 94, 0.2)';

        return (
          <div
            key={index}
            className="absolute pointer-events-none"
            style={{
              left: `${left}px`,
              top: `${top}px`,
              width: `${width}px`,
              height: `${height}px`,
              border: `2px solid ${color}`,
              backgroundColor: bgColor,
              borderRadius: '4px',
            }}
          >
            {/* Label */}
            <div
              className="absolute -top-6 left-0 px-2 py-0.5 rounded text-xs font-semibold"
              style={{
                backgroundColor: color,
                color: 'white',
              }}
            >
              {detection.class_name} {(detection.confidence * 100).toFixed(0)}%
            </div>
          </div>
        );
      })}
    </>
  );
}
