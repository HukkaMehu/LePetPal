import { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { 
  Circle, 
  Camera, 
  Heart, 
  Cookie, 
  Play,
  Maximize2,
  MoreVertical,
  Wifi,
  WifiOff
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { toast } from 'sonner';
import { useSystemStatus } from '../hooks/useSystemStatus';
import { config } from '../config/env';
import { apiClient } from '../services/api';

export default function LivePage() {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingStartTime, setRecordingStartTime] = useState<Date | null>(null);
  const { status, loading: statusLoading } = useSystemStatus();

  const handleAction = async (action: 'pet' | 'treat' | 'fetch') => {
    try {
      // Send robot action command to backend
      const response = await apiClient.sendRobotAction(action);
      
      if (response.success) {
        toast.success(`${action.charAt(0).toUpperCase() + action.slice(1)} command sent`, {
          description: response.message || 'Action executed successfully',
        });
      } else {
        toast.error(`Failed to send ${action} command`, {
          description: response.message || 'Unknown error occurred',
        });
      }
    } catch (error) {
      console.error(`Error sending ${action} command:`, error);
      toast.error(`Failed to send ${action} command`, {
        description: error instanceof Error ? error.message : 'Network error occurred',
      });
    }
  };

  const handleSnapshot = async () => {
    try {
      // Create snapshot with current timestamp
      const snapshotData = {
        ts: new Date().toISOString(),
        note: null,
      };
      
      const response = await apiClient.createSnapshot(snapshotData);
      
      toast.success('Snapshot saved', {
        description: 'Added to your gallery',
      });
    } catch (error) {
      console.error('Error creating snapshot:', error);
      toast.error('Failed to save snapshot', {
        description: error instanceof Error ? error.message : 'Network error occurred',
      });
    }
  };

  const handleRecordingToggle = async () => {
    try {
      if (isRecording && recordingStartTime) {
        // Stop recording - calculate duration and create clip
        const endTime = new Date();
        const durationMs = endTime.getTime() - recordingStartTime.getTime();
        
        // Create clip with the recorded segment
        const response = await apiClient.createClip({
          start_ts: recordingStartTime.toISOString(),
          duration_ms: durationMs,
          labels: ['manual_recording'],
        });
        
        setIsRecording(false);
        setRecordingStartTime(null);
        
        toast.success('Recording stopped', {
          description: `Clip saved (${Math.round(durationMs / 1000)}s)`,
        });
      } else {
        // Start recording - track start time
        const startTime = new Date();
        setRecordingStartTime(startTime);
        setIsRecording(true);
        
        toast.info('Recording started', {
          description: 'Click Stop to save the clip',
        });
      }
    } catch (error) {
      console.error('Error toggling recording:', error);
      toast.error(`Failed to ${isRecording ? 'stop' : 'start'} recording`, {
        description: error instanceof Error ? error.message : 'Network error occurred',
      });
      
      // Reset recording state on error
      setIsRecording(false);
      setRecordingStartTime(null);
    }
  };

  // Determine video stream URL based on stream type
  const videoStreamUrl = status?.video === 'webrtc' 
    ? config.videoStreamURL.replace('/mjpeg', '/webrtc')
    : config.videoStreamURL;

  // Connection status
  const isConnected = status?.device === 'connected';
  const fps = status?.fps ?? 0;
  const latency = status?.latencyMs ?? 0;

  // Log video configuration
  console.log('[LivePage] Video config:', {
    videoStreamUrl,
    statusVideo: status?.video,
    isConnected,
    apiBaseURL: config.apiBaseURL,
    fullVideoURL: config.videoStreamURL
  });

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-border bg-card px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Connection Status */}
            <div className="flex items-center gap-2">
              {isConnected ? (
                <>
                  <Circle className="w-2 h-2 fill-primary text-primary animate-pulse" />
                  <span className="text-sm text-muted-foreground">Live</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-3 h-3 text-destructive" />
                  <span className="text-sm text-destructive">Offline</span>
                </>
              )}
            </div>
            <Separator orientation="vertical" className="h-4" />
            
            {/* Video Metrics */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">
                {fps > 0 ? `${fps} fps` : '--'}
              </span>
              <span className="text-sm text-muted-foreground">·</span>
              <span className="text-sm text-muted-foreground">
                {latency > 0 ? `${latency}ms` : '--'}
              </span>
            </div>
            
            {/* Stream Type Badge */}
            {status?.video && (
              <>
                <Separator orientation="vertical" className="h-4" />
                <Badge variant="outline" className="text-xs">
                  {status.video.toUpperCase()}
                </Badge>
              </>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant={isRecording ? 'destructive' : 'outline'}
              size="sm"
              onClick={handleRecordingToggle}
              disabled={!isConnected}
            >
              <Circle className={`w-3 h-3 mr-2 ${isRecording ? 'fill-white' : ''}`} />
              {isRecording ? 'Stop' : 'Record'}
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" disabled={!isConnected}>
                  <MoreVertical className="w-4 h-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleSnapshot}>
                  <Camera className="w-4 h-4 mr-2" />
                  Snapshot
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Maximize2 className="w-4 h-4 mr-2" />
                  Fullscreen
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>

      {/* Main content - centered */}
      <div className="flex-1 overflow-auto flex items-center justify-center p-8">
        <div className="w-full max-w-5xl space-y-6">
          {/* Video */}
          <Card className="overflow-hidden bg-black">
            <div className="aspect-video relative">
              {/* Always show video stream (even if device is "offline" for demo/testing) */}
              {status?.video === 'mjpeg' && (
                <img
                  src={videoStreamUrl}
                  alt="Live stream"
                  className="w-full h-full object-cover"
                  onLoad={() => {
                    console.log('[LivePage] MJPEG stream loaded successfully from:', videoStreamUrl);
                  }}
                  onError={(e) => {
                    console.error('[LivePage] MJPEG stream failed to load from:', videoStreamUrl);
                    console.error('[LivePage] Error details:', e);
                  }}
                />
              )}
              
              {/* WebRTC Stream - placeholder for future implementation */}
              {status?.video === 'webrtc' && (
                <div className="w-full h-full flex items-center justify-center bg-black">
                  <div className="text-center text-white">
                    <Wifi className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p className="text-sm opacity-75">WebRTC stream</p>
                    <p className="text-xs opacity-50 mt-1">Coming soon</p>
                  </div>
                </div>
              )}
              
              {/* No stream type detected - show offline message */}
              {!status?.video && (
                <div className="w-full h-full flex items-center justify-center bg-black">
                  <div className="text-center text-white">
                    {isConnected ? (
                      <>
                        <Circle className="w-12 h-12 mx-auto mb-4 opacity-50 animate-pulse" />
                        <p className="text-sm opacity-75">Connecting to stream...</p>
                      </>
                    ) : (
                      <>
                        <WifiOff className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        <p className="text-sm opacity-75">Device offline</p>
                        <p className="text-xs opacity-50 mt-1">Waiting for connection...</p>
                      </>
                    )}
                  </div>
                </div>
              )}
              
              {/* Recording indicator */}
              {isRecording && (
                <div className="absolute top-4 left-4">
                  <Badge variant="destructive" className="gap-2">
                    <Circle className="w-2 h-2 fill-white animate-pulse" />
                    Recording
                  </Badge>
                </div>
              )}
            </div>
          </Card>

          {/* Action buttons */}
          <div className="flex items-center justify-center gap-3">
            <Button
              variant="outline"
              size="lg"
              onClick={() => handleAction('pet')}
              className="gap-2"
              disabled={!isConnected}
            >
              <Heart className="w-5 h-5" />
              Pet
            </Button>
            <Button
              variant="outline"
              size="lg"
              onClick={() => handleAction('treat')}
              className="gap-2"
              disabled={!isConnected}
            >
              <Cookie className="w-5 h-5" />
              Treat
            </Button>
            <Button
              variant="outline"
              size="lg"
              onClick={() => handleAction('fetch')}
              className="gap-2"
              disabled={!isConnected}
            >
              <Play className="w-5 h-5" />
              Fetch
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
