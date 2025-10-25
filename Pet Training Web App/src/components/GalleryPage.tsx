import { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Dialog, DialogContent } from './ui/dialog';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { Play, Download, Trash2, Loader2, Filter, X } from 'lucide-react';
import { MediaItem, MediaType } from '../types';
import { formatDistanceToNow, format, subDays } from 'date-fns';
import { toast } from 'sonner';
import { useMedia } from '../hooks/useMedia';
import { GallerySkeleton } from './LoadingStates';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from './ui/dropdown-menu';
import { Input } from './ui/input';

export default function GalleryPage() {
  const [selectedItem, setSelectedItem] = useState<MediaItem | null>(null);
  const [filterType, setFilterType] = useState<MediaType | undefined>(undefined);
  const [filterStartDate, setFilterStartDate] = useState<string | undefined>(undefined);
  const [filterEndDate, setFilterEndDate] = useState<string | undefined>(undefined);
  const [filterTags, setFilterTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState<string>('');

  const { media, loading, error, total, hasMore, loadMore } = useMedia({ 
    limit: 20,
    type: filterType,
    startDate: filterStartDate,
    endDate: filterEndDate,
    tags: filterTags.length > 0 ? filterTags : undefined,
  });

  const handleDelete = (_item: MediaItem) => {
    // TODO: Implement actual delete functionality with API call
    toast.success('Deleted');
    setSelectedItem(null);
  };

  const handleDateRangeFilter = (range: 'today' | 'week' | 'month' | 'all') => {
    const now = new Date();
    const today = format(now, 'yyyy-MM-dd');
    
    switch (range) {
      case 'today':
        setFilterStartDate(today);
        setFilterEndDate(today);
        break;
      case 'week':
        setFilterStartDate(format(subDays(now, 7), 'yyyy-MM-dd'));
        setFilterEndDate(today);
        break;
      case 'month':
        setFilterStartDate(format(subDays(now, 30), 'yyyy-MM-dd'));
        setFilterEndDate(today);
        break;
      case 'all':
        setFilterStartDate(undefined);
        setFilterEndDate(undefined);
        break;
    }
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !filterTags.includes(tagInput.trim())) {
      setFilterTags([...filterTags, tagInput.trim()]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    setFilterTags(filterTags.filter(t => t !== tag));
  };

  const clearAllFilters = () => {
    setFilterType(undefined);
    setFilterStartDate(undefined);
    setFilterEndDate(undefined);
    setFilterTags([]);
  };

  const hasActiveFilters = filterType || filterStartDate || filterEndDate || filterTags.length > 0;

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-border bg-card px-6 py-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2>Gallery</h2>
            <p className="text-sm text-muted-foreground">
              {loading ? 'Loading...' : `${total} items`}
            </p>
          </div>
          <div className="flex gap-2">
            {hasActiveFilters && (
              <Button
                variant="outline"
                size="sm"
                onClick={clearAllFilters}
              >
                <X className="w-4 h-4 mr-2" />
                Clear Filters
              </Button>
            )}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <Filter className="w-4 h-4 mr-2" />
                  Filters
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>Filter by Type</DropdownMenuLabel>
                <DropdownMenuItem onClick={() => setFilterType(undefined)}>
                  All Media {!filterType && '✓'}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setFilterType('clip')}>
                  Clips Only {filterType === 'clip' && '✓'}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setFilterType('snapshot')}>
                  Snapshots Only {filterType === 'snapshot' && '✓'}
                </DropdownMenuItem>
                
                <DropdownMenuSeparator />
                <DropdownMenuLabel>Filter by Date</DropdownMenuLabel>
                <DropdownMenuItem onClick={() => handleDateRangeFilter('today')}>
                  Today
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleDateRangeFilter('week')}>
                  Last 7 Days
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleDateRangeFilter('month')}>
                  Last 30 Days
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleDateRangeFilter('all')}>
                  All Time
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {/* Active Filters Display */}
        {hasActiveFilters && (
          <div className="flex flex-wrap gap-2">
            {filterType && (
              <Badge variant="secondary" className="gap-1">
                Type: {filterType}
                <X 
                  className="w-3 h-3 cursor-pointer" 
                  onClick={() => setFilterType(undefined)}
                />
              </Badge>
            )}
            {filterStartDate && (
              <Badge variant="secondary" className="gap-1">
                From: {filterStartDate}
                <X 
                  className="w-3 h-3 cursor-pointer" 
                  onClick={() => setFilterStartDate(undefined)}
                />
              </Badge>
            )}
            {filterEndDate && (
              <Badge variant="secondary" className="gap-1">
                To: {filterEndDate}
                <X 
                  className="w-3 h-3 cursor-pointer" 
                  onClick={() => setFilterEndDate(undefined)}
                />
              </Badge>
            )}
            {filterTags.map((tag) => (
              <Badge key={tag} variant="secondary" className="gap-1">
                Tag: {tag}
                <X 
                  className="w-3 h-3 cursor-pointer" 
                  onClick={() => handleRemoveTag(tag)}
                />
              </Badge>
            ))}
          </div>
        )}

        {/* Tag Filter Input */}
        <div className="mt-4 flex gap-2">
          <Input
            placeholder="Filter by tag..."
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleAddTag();
              }
            }}
            className="max-w-xs"
          />
          <Button onClick={handleAddTag} size="sm" variant="outline">
            Add Tag Filter
          </Button>
        </div>
      </div>

      {/* Grid */}
      <div className="flex-1 overflow-auto p-6">
        {error && (
          <div className="text-center py-8">
            <p className="text-destructive">Error loading media: {error.message}</p>
          </div>
        )}

        {loading && media.length === 0 && (
          <GallerySkeleton />
        )}

        {!loading && !error && media.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No media items found</p>
          </div>
        )}

        {media.length > 0 && (
          <>
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
                    {item.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {item.tags.slice(0, 2).map((tag, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                        {item.tags.length > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{item.tags.length - 2}
                          </Badge>
                        )}
                      </div>
                    )}
                  </div>
                </Card>
              ))}
            </div>

            {/* Load More Button */}
            {hasMore && (
              <div className="flex justify-center mt-8">
                <Button
                  onClick={loadMore}
                  disabled={loading}
                  variant="outline"
                  size="lg"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    'Load More'
                  )}
                </Button>
              </div>
            )}

            {/* End of Results Message */}
            {!hasMore && media.length > 0 && (
              <div className="text-center mt-8 text-sm text-muted-foreground">
                All {total} items loaded
              </div>
            )}
          </>
        )}
      </div>

      {/* Detail dialog */}
      <Dialog open={selectedItem !== null} onOpenChange={() => setSelectedItem(null)}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          {selectedItem && (
            <div className="space-y-6">
              {/* Media Display */}
              <div className="aspect-video bg-black rounded-lg overflow-hidden">
                {selectedItem.type === 'clip' ? (
                  <video
                    src={selectedItem.url}
                    controls
                    className="w-full h-full object-contain"
                    autoPlay
                  >
                    Your browser does not support the video tag.
                  </video>
                ) : (
                  <ImageWithFallback
                    src={selectedItem.url}
                    alt={selectedItem.type}
                    className="w-full h-full object-contain"
                  />
                )}
              </div>

              {/* Metadata Section */}
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">
                        {selectedItem.type === 'clip' ? 'Video Clip' : 'Snapshot'}
                      </Badge>
                      {selectedItem.type === 'clip' && selectedItem.duration && (
                        <Badge variant="outline">
                          {selectedItem.duration}s
                        </Badge>
                      )}
                    </div>
                    <div className="text-sm space-y-1">
                      <p className="text-muted-foreground">
                        <span className="font-medium">Captured:</span>{' '}
                        {selectedItem.timestamp.toLocaleString()}
                      </p>
                      <p className="text-muted-foreground">
                        <span className="font-medium">Time ago:</span>{' '}
                        {formatDistanceToNow(selectedItem.timestamp, { addSuffix: true })}
                      </p>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => {
                        const link = document.createElement('a');
                        link.href = selectedItem.url;
                        link.download = `${selectedItem.type}-${selectedItem.id}`;
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        toast.success('Download started');
                      }}
                    >
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

                {/* Tags */}
                {selectedItem.tags.length > 0 && (
                  <div>
                    <p className="text-sm font-medium mb-2">Tags</p>
                    <div className="flex flex-wrap gap-2">
                      {selectedItem.tags.map((tag, idx) => (
                        <Badge key={idx} variant="secondary">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Associated Events */}
                {selectedItem.events.length > 0 && (
                  <div>
                    <p className="text-sm font-medium mb-2">Associated Events</p>
                    <div className="space-y-2">
                      {selectedItem.events.map((event) => (
                        <div 
                          key={event.id}
                          className="flex items-center justify-between p-3 bg-muted rounded-lg"
                        >
                          <div className="flex items-center gap-3">
                            <Badge variant="outline">{event.type}</Badge>
                            <span className="text-sm text-muted-foreground">
                              {formatDistanceToNow(event.timestamp, { addSuffix: true })}
                            </span>
                          </div>
                          {event.confidence && (
                            <span className="text-sm text-muted-foreground">
                              {Math.round(event.confidence * 100)}% confidence
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedItem.events.length === 0 && (
                  <div className="text-sm text-muted-foreground">
                    No associated events
                  </div>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
