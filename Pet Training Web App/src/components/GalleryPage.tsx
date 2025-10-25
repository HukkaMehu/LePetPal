import { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Dialog, DialogContent } from './ui/dialog';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { Play, Download, Trash2 } from 'lucide-react';
import { generateMockMedia, MediaItem } from '../lib/mockData';
import { formatDistanceToNow } from 'date-fns';
import { toast } from 'sonner@2.0.3';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';

export default function GalleryPage() {
  const [media] = useState(generateMockMedia());
  const [selectedItem, setSelectedItem] = useState<MediaItem | null>(null);

  const handleDelete = (item: MediaItem) => {
    toast.success('Deleted');
    setSelectedItem(null);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-border bg-card px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2>Gallery</h2>
            <p className="text-sm text-muted-foreground">{media.length} items</p>
          </div>
        </div>
      </div>

      {/* Grid */}
      <div className="flex-1 overflow-auto p-6">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {media.map((item) => (
            <Card
              key={item.id}
              className="overflow-hidden cursor-pointer group hover:shadow-lg transition-shadow"
              onClick={() => setSelectedItem(item)}
            >
              <div className="aspect-square relative bg-muted">
                <ImageWithFallback
                  src={item.thumbnail}
                  alt={item.type}
                  className="w-full h-full object-cover"
                />
                {item.type === 'clip' && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="w-12 h-12 rounded-full bg-white/90 flex items-center justify-center">
                      <Play className="w-6 h-6 text-foreground" />
                    </div>
                  </div>
                )}
                <Badge
                  variant="secondary"
                  className="absolute top-2 right-2"
                >
                  {item.type === 'clip' ? `${item.duration}s` : 'Photo'}
                </Badge>
              </div>
              <div className="p-3 border-t border-border">
                <p className="text-xs text-muted-foreground">
                  {formatDistanceToNow(item.timestamp, { addSuffix: true })}
                </p>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Detail dialog */}
      <Dialog open={selectedItem !== null} onOpenChange={() => setSelectedItem(null)}>
        <DialogContent className="max-w-3xl">
          {selectedItem && (
            <div className="space-y-4">
              <div className="aspect-video bg-black rounded-lg overflow-hidden">
                <ImageWithFallback
                  src={selectedItem.url}
                  alt={selectedItem.type}
                  className="w-full h-full object-contain"
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Badge variant="secondary" className="mb-2">
                    {selectedItem.type}
                  </Badge>
                  <p className="text-sm text-muted-foreground">
                    {selectedItem.timestamp.toLocaleString()}
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" variant="outline">
                    <Download className="w-4 h-4 mr-2" />
                    Download
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDelete(selectedItem)}
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Delete
                  </Button>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
