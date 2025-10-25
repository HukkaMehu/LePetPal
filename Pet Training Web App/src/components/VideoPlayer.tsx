import { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  Maximize, 
  Minimize, 
  PictureInPicture, 
  Camera, 
  Video
} from 'lucide-react';
import { toast } from 'sonner';
import AIOverlay from './AIOverlay';

interface VideoPlayerProps {
  overlays: {
    dogBox: boolean;
    keypoints: boolean;
    objects: boolean;
    heatmap: boolean;
  };
  isRecording: boolean;
  onSnapshot: () => void;
  onClipStart: () => void;
  onClipEnd: () => void;
  isClipping: boolean;
}

export default function VideoPlayer({
  overlays,
  isRecording,
  onSnapshot,
  onClipStart,
  onClipEnd,
  isClipping,
}: VideoPlayerProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isPiP, setIsPiP] = useState(false);
  const [isPlaying, setIsPlaying] = useState(true);
  const [streamType, setStreamType] = useState<'webrtc' | 'mjpeg' | 'connecting'>('connecting');
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'failed'>('connecting');
  const [videoDimensions, setVideoDimensions] = useState({ width: 0, height: 0 });
  const containerRef = useRef<HTMLDivElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);

  // Backend URL from environment or default
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  console.log('[VideoPlayer] Component mounted, backend URL:', backendUrl);

  // Connect to video stream on mount
  useEffect(() => {
    connectWebRTC();
    
    return () => {
      // Cleanup on unmount
      if (peerConnectionRef.current) {
        peerConnectionRef.current.close();
      }
    };
  }, []);

  // Try WebRTC connection first
  const connectWebRTC = async () => {
    try {
      console.log('[VideoPlayer] Starting WebRTC connection...');
      setConnectionStatus('connecting');
      setStreamType('connecting');

      const pc = new RTCPeerConnection({
        iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
      });
      peerConnectionRef.current = pc;
      console.log('[VideoPlayer] RTCPeerConnection created');

      // Handle incoming video track
      pc.ontrack = (event) => {
        console.log('[VideoPlayer] ontrack event received:', {
          streams: event.streams.length,
          track: event.track.kind,
          videoRefExists: !!videoRef.current
        });
        
        if (videoRef.current && event.streams[0]) {
          console.log('[VideoPlayer] Setting srcObject on video element');
          videoRef.current.srcObject = event.streams[0];
          setStreamType('webrtc');
          setConnectionStatus('connected');
          toast.success('Connected via WebRTC');
          
          // Log when video starts playing and get dimensions
          videoRef.current.onloadedmetadata = () => {
            console.log('[VideoPlayer] Video metadata loaded, dimensions:', 
              videoRef.current?.videoWidth, 'x', videoRef.current?.videoHeight);
            if (videoRef.current) {
              setVideoDimensions({
                width: videoRef.current.videoWidth,
                height: videoRef.current.videoHeight
              });
            }
          };
          videoRef.current.onplay = () => {
            console.log('[VideoPlayer] Video started playing');
          };
        } else {
          console.warn('[VideoPlayer] Cannot set video stream - videoRef or stream missing');
        }
      };

      // Handle connection state changes
      pc.onconnectionstatechange = () => {
        console.log('[VideoPlayer] Connection state changed:', pc.connectionState);
        if (pc.connectionState === 'failed' || pc.connectionState === 'closed') {
          setConnectionStatus('failed');
          console.log('[VideoPlayer] Connection failed, falling back to MJPEG');
          // Fallback to MJPEG
          setTimeout(() => connectMJPEG(), 1000);
        }
      };
      
      // Log ICE connection state
      pc.oniceconnectionstatechange = () => {
        console.log('[VideoPlayer] ICE connection state:', pc.iceConnectionState);
      };

      // Create and send offer
      console.log('[VideoPlayer] Creating WebRTC offer...');
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      console.log('[VideoPlayer] Local description set');

      const url = `${backendUrl}/video/webrtc/offer?webcam=true`;
      console.log('[VideoPlayer] Sending offer to:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sdp: offer.sdp,
          type: offer.type
        })
      });

      console.log('[VideoPlayer] Offer response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('[VideoPlayer] Offer failed:', errorText);
        throw new Error(`WebRTC offer failed: ${response.status}`);
      }

      const answer = await response.json();
      console.log('[VideoPlayer] Received answer, setting remote description');
      await pc.setRemoteDescription(new RTCSessionDescription(answer));
      console.log('[VideoPlayer] Remote description set successfully');

    } catch (error) {
      console.error('[VideoPlayer] WebRTC connection failed:', error);
      setConnectionStatus('failed');
      // Fallback to MJPEG
      setTimeout(() => connectMJPEG(), 1000);
    }
  };

  // Fallback to MJPEG stream
  const connectMJPEG = () => {
    console.log('[VideoPlayer] Switching to MJPEG stream');
    setStreamType('mjpeg');
    setConnectionStatus('connecting');
    
    if (imgRef.current) {
      const url = `${backendUrl}/video/mjpeg?webcam=true`;
      console.log('[VideoPlayer] Loading MJPEG from:', url);
      imgRef.current.src = url;
      
      imgRef.current.onload = () => {
        console.log('[VideoPlayer] MJPEG stream loaded successfully');
        setConnectionStatus('connected');
        toast.info('Connected via MJPEG');
        // Get image dimensions for overlay
        if (imgRef.current) {
          setVideoDimensions({
            width: imgRef.current.naturalWidth,
            height: imgRef.current.naturalHeight
          });
        }
      };
      imgRef.current.onerror = (e) => {
        console.error('[VideoPlayer] MJPEG stream failed to load:', e);
        setConnectionStatus('failed');
        toast.error('Failed to connect to video stream');
      };
    } else {
      console.warn('[VideoPlayer] imgRef not available for MJPEG');
    }
  };

  const toggleFullscreen = async () => {
    if (!containerRef.current) return;

    try {
      if (!document.fullscreenElement) {
        await containerRef.current.requestFullscreen();
        setIsFullscreen(true);
      } else {
        await document.exitFullscreen();
        setIsFullscreen(false);
      }
    } catch (err) {
      console.error('Fullscreen error:', err);
    }
  };

  const togglePiP = async () => {
    if (!videoRef.current) return;

    try {
      if (document.pictureInPictureElement) {
        await document.exitPictureInPicture();
        setIsPiP(false);
      } else {
        await videoRef.current.requestPictureInPicture();
        setIsPiP(true);
      }
    } catch (err) {
      console.error('PiP error:', err);
    }
  };

  const handleSnapshot = () => {
    onSnapshot();
    toast.success('Snapshot saved', {
      description: 'Added to your gallery',
    });
  };

  const handleClip = () => {
    if (isClipping) {
      onClipEnd();
      toast.success('Clip saved', {
        description: 'Added to your gallery',
      });
    } else {
      onClipStart();
      toast.info('Recording clip...', {
        description: 'Click again to stop',
      });
    }
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (e.key.toLowerCase()) {
        case 's':
          handleSnapshot();
          break;
        case 'c':
          handleClip();
          break;
        case 'f':
          toggleFullscreen();
          break;
      }
    };

    window.addEventListener('keypress', handleKeyPress);
    return () => window.removeEventListener('keypress', handleKeyPress);
  }, [isClipping]);

  return (
    <div ref={containerRef} className="relative bg-black rounded-lg overflow-hidden group">
      {/* Video Stream */}
      <div className="relative aspect-video">
        {/* WebRTC Video */}
        {streamType === 'webrtc' && (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
          />
        )}
        
        {/* MJPEG Image Stream */}
        {streamType === 'mjpeg' && (
          <img
            ref={imgRef}
            alt="Live stream"
            className="w-full h-full object-cover"
          />
        )}
        
        {/* Connecting State */}
        {streamType === 'connecting' && (
          <div className="w-full h-full flex items-center justify-center bg-gray-900">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
              <p className="text-white">Connecting to camera...</p>
            </div>
          </div>
        )}
        
        {/* Connection Status Badge */}
        <div className="absolute top-4 right-4">
          <Badge variant={connectionStatus === 'connected' ? 'default' : 'destructive'}>
            {streamType === 'webrtc' && '🔴 LIVE (WebRTC)'}
            {streamType === 'mjpeg' && '🔴 LIVE (MJPEG)'}
            {streamType === 'connecting' && 'Connecting...'}
          </Badge>
        </div>

        {/* AI Detection Overlays */}
        {overlays.dogBox && videoDimensions.width > 0 && (
          <AIOverlay
            enabled={overlays.dogBox}
            videoWidth={videoDimensions.width}
            videoHeight={videoDimensions.height}
          />
        )}

        {overlays.keypoints && (
          <>
            <div className="absolute top-[30%] left-[42%] w-2 h-2 bg-blue-400 rounded-full" title="Nose" />
            <div className="absolute top-[35%] left-[38%] w-2 h-2 bg-blue-400 rounded-full" title="Ear" />
            <div className="absolute top-[35%] left-[46%] w-2 h-2 bg-blue-400 rounded-full" title="Ear" />
            <div className="absolute top-[50%] left-[40%] w-2 h-2 bg-blue-400 rounded-full" title="Shoulder" />
            <div className="absolute top-[50%] left-[44%] w-2 h-2 bg-blue-400 rounded-full" title="Shoulder" />
          </>
        )}

        {overlays.objects && (
          <>
            <div className="absolute top-[60%] left-[20%] w-12 h-12 border-2 border-yellow-400 rounded">
              <div className="absolute -top-5 left-0 bg-yellow-400 text-black px-1 py-0.5 rounded text-xs">
                Ball
              </div>
            </div>
            <div className="absolute bottom-[15%] right-[25%] w-16 h-10 border-2 border-yellow-400 rounded">
              <div className="absolute -top-5 left-0 bg-yellow-400 text-black px-1 py-0.5 rounded text-xs">
                Bowl
              </div>
            </div>
          </>
        )}

        {overlays.heatmap && (
          <div className="absolute inset-0 bg-gradient-radial from-red-500/30 via-orange-500/20 to-transparent opacity-50" />
        )}

        {/* Recording indicator */}
        {isRecording && (
          <div className="absolute top-4 left-4 flex items-center gap-2 bg-red-600 text-white px-3 py-1.5 rounded">
            <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
            <span className="text-sm">REC</span>
          </div>
        )}

        {/* Clipping indicator */}
        {isClipping && (
          <div className="absolute top-4 right-4 flex items-center gap-2 bg-blue-600 text-white px-3 py-1.5 rounded">
            <Video className="w-4 h-4" />
            <span className="text-sm">Clipping...</span>
          </div>
        )}

        {/* Control overlay */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 opacity-0 group-hover:opacity-100 transition-opacity">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="ghost"
                className="text-white hover:bg-white/20"
                onClick={handleSnapshot}
                title="Snapshot (S)"
              >
                <Camera className="w-4 h-4" />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                className="text-white hover:bg-white/20"
                onClick={handleClip}
                title="Clip (C)"
              >
                <Video className="w-4 h-4" />
              </Button>
            </div>

            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="ghost"
                className="text-white hover:bg-white/20"
                onClick={togglePiP}
                title="Picture-in-Picture"
              >
                <PictureInPicture className="w-4 h-4" />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                className="text-white hover:bg-white/20"
                onClick={toggleFullscreen}
                title="Fullscreen (F)"
              >
                {isFullscreen ? (
                  <Minimize className="w-4 h-4" />
                ) : (
                  <Maximize className="w-4 h-4" />
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>


    </div>
  );
}
