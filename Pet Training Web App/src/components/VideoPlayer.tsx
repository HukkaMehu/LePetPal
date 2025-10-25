import { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  Maximize, 
  Minimize, 
  PictureInPicture, 
  Camera, 
  Video,
  Play,
  Pause
} from 'lucide-react';
import { toast } from 'sonner@2.0.3';

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
  const containerRef = useRef<HTMLDivElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Mock video stream (in production, this would be WebRTC/MJPEG)
  const videoUrl = 'https://images.unsplash.com/photo-1560807707-8cc77767d783?w=1200&h=800&fit=crop';

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
      {/* Video Canvas - Using static image as placeholder for actual stream */}
      <div className="relative aspect-video">
        <img 
          src={videoUrl} 
          alt="Live stream"
          className="w-full h-full object-cover"
        />

        {/* Overlays */}
        {overlays.dogBox && (
          <div className="absolute top-1/4 left-1/3 w-1/3 h-1/2 border-2 border-green-400 rounded-lg">
            <div className="absolute -top-6 left-0 bg-green-400 text-black px-2 py-0.5 rounded text-xs">
              Dog (0.94)
            </div>
          </div>
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

      {/* Hidden video element for PiP functionality */}
      <video
        ref={videoRef}
        className="hidden"
        autoPlay
        muted
        loop
      />
    </div>
  );
}
