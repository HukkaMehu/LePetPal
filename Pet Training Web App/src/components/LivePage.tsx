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
  MoreVertical
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { toast } from 'sonner@2.0.3';

export default function LivePage() {
  const [isRecording, setIsRecording] = useState(false);
  const videoUrl = 'https://images.unsplash.com/photo-1560807707-8cc77767d783?w=1600&h=900&fit=crop';

  const handleAction = (action: string) => {
    toast.success(`${action} command sent`);
  };

  const handleSnapshot = () => {
    toast.success('Snapshot saved');
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-border bg-card px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Circle className="w-2 h-2 fill-primary text-primary" />
              <span className="text-sm text-muted-foreground">Live</span>
            </div>
            <Separator orientation="vertical" className="h-4" />
            <span className="text-sm text-muted-foreground">30 fps · 120ms</span>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant={isRecording ? 'destructive' : 'outline'}
              size="sm"
              onClick={() => setIsRecording(!isRecording)}
            >
              <Circle className={`w-3 h-3 mr-2 ${isRecording ? 'fill-white' : ''}`} />
              {isRecording ? 'Stop' : 'Record'}
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
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
              <img
                src={videoUrl}
                alt="Live stream"
                className="w-full h-full object-cover"
              />
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
              onClick={() => handleAction('Pet')}
              className="gap-2"
            >
              <Heart className="w-5 h-5" />
              Pet
            </Button>
            <Button
              variant="outline"
              size="lg"
              onClick={() => handleAction('Treat')}
              className="gap-2"
            >
              <Cookie className="w-5 h-5" />
              Treat
            </Button>
            <Button
              variant="outline"
              size="lg"
              onClick={() => handleAction('Fetch')}
              className="gap-2"
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
