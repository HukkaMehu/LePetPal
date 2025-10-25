import { useState, useEffect, useRef } from 'react';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Event, EventType } from '../types';
import { formatDistanceToNow } from 'date-fns';
import { useEvents } from '../hooks/useEvents';
import { Loader2, Filter, X } from 'lucide-react';
import { EventFeedSkeleton } from './LoadingStates';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from './ui/dropdown-menu';

interface EventFeedProps {
  events?: Event[];
  limit?: number;
  eventType?: EventType;
  showFilters?: boolean;
  showLoadMore?: boolean;
}

const eventIcons: Record<Event['type'], string> = {
  sit: '🪑',
  fetch: '🎾',
  treat: '🦴',
  bark: '🔊',
  pet: '💝',
  active: '⚡',
  calm: '😌',
  stand: '🧍',
  lie: '🛏️',
};

const eventColors: Record<Event['type'], string> = {
  sit: 'bg-blue-100 text-blue-700 border-blue-200',
  fetch: 'bg-green-100 text-green-700 border-green-200',
  treat: 'bg-amber-100 text-amber-700 border-amber-200',
  bark: 'bg-red-100 text-red-700 border-red-200',
  pet: 'bg-pink-100 text-pink-700 border-pink-200',
  active: 'bg-purple-100 text-purple-700 border-purple-200',
  calm: 'bg-teal-100 text-teal-700 border-teal-200',
  stand: 'bg-indigo-100 text-indigo-700 border-indigo-200',
  lie: 'bg-slate-100 text-slate-700 border-slate-200',
};

export default function EventFeed({ 
  events: propEvents, 
  limit: initialLimit = 50, 
  eventType: propEventType,
  showFilters = true,
  showLoadMore = true,
}: EventFeedProps) {
  // Filter state
  const [selectedEventTypes, setSelectedEventTypes] = useState<Set<EventType>>(new Set());
  const [dateRange, setDateRange] = useState<{ start?: string; end?: string }>({});
  const [currentLimit, setCurrentLimit] = useState(initialLimit);

  // Determine if we should use filters
  const useFilters = !propEvents && showFilters;
  const activeEventType = propEventType || (selectedEventTypes.size === 1 ? Array.from(selectedEventTypes)[0] : undefined);

  // Use hook to fetch events if not provided via props
  const { events: fetchedEvents, loading, error } = useEvents({
    limit: currentLimit,
    eventType: activeEventType,
    startDate: dateRange.start,
    endDate: dateRange.end,
    autoConnect: !propEvents, // Only auto-connect if events not provided
  });

  // Use prop events if provided, otherwise use fetched events
  let events = propEvents || fetchedEvents;

  // Apply client-side filtering if multiple event types selected
  if (!propEvents && selectedEventTypes.size > 1) {
    events = events.filter(e => selectedEventTypes.has(e.type));
  }

  // Track new events for highlighting
  const [newEventIds, setNewEventIds] = useState<Set<string>>(new Set());
  const prevEventsRef = useRef<Event[]>([]);

  // Detect new events and highlight them briefly
  useEffect(() => {
    if (events.length > prevEventsRef.current.length) {
      const prevIds = new Set(prevEventsRef.current.map(e => e.id));
      const newIds = events.filter(e => !prevIds.has(e.id)).map(e => e.id);
      
      if (newIds.length > 0) {
        setNewEventIds(new Set(newIds));
        
        // Remove highlight after 3 seconds
        const timer = setTimeout(() => {
          setNewEventIds(new Set());
        }, 3000);
        
        return () => clearTimeout(timer);
      }
    }
    
    prevEventsRef.current = events;
  }, [events]);

  // Handle event type filter toggle
  const toggleEventType = (type: EventType) => {
    setSelectedEventTypes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(type)) {
        newSet.delete(type);
      } else {
        newSet.add(type);
      }
      return newSet;
    });
  };

  // Handle date range filter
  const setDateRangeFilter = (days?: number) => {
    if (!days) {
      setDateRange({});
      return;
    }

    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - days);

    setDateRange({
      start: start.toISOString(),
      end: end.toISOString(),
    });
  };

  // Clear all filters
  const clearFilters = () => {
    setSelectedEventTypes(new Set());
    setDateRange({});
    setCurrentLimit(initialLimit);
  };

  // Load more events
  const loadMore = () => {
    setCurrentLimit(prev => prev + 50);
  };

  const hasActiveFilters = selectedEventTypes.size > 0 || dateRange.start || dateRange.end;

  const allEventTypes: EventType[] = ['sit', 'fetch', 'treat', 'bark', 'pet', 'active', 'calm', 'stand', 'lie'];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-neutral-900">Activity Feed</h3>
        
        {useFilters && (
          <div className="flex items-center gap-2">
            {hasActiveFilters && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
                className="h-8 text-xs"
              >
                <X className="w-3 h-3 mr-1" />
                Clear
              </Button>
            )}
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="h-8">
                  <Filter className="w-3 h-3 mr-2" />
                  Filter
                  {hasActiveFilters && (
                    <Badge variant="secondary" className="ml-2 h-4 px-1 text-xs">
                      {selectedEventTypes.size || (dateRange.start ? '1' : '0')}
                    </Badge>
                  )}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>Event Types</DropdownMenuLabel>
                {allEventTypes.map(type => (
                  <DropdownMenuCheckboxItem
                    key={type}
                    checked={selectedEventTypes.has(type)}
                    onCheckedChange={() => toggleEventType(type)}
                  >
                    <span className="mr-2">{eventIcons[type]}</span>
                    {type}
                  </DropdownMenuCheckboxItem>
                ))}
                
                <DropdownMenuSeparator />
                <DropdownMenuLabel>Date Range</DropdownMenuLabel>
                <DropdownMenuCheckboxItem
                  checked={!dateRange.start}
                  onCheckedChange={() => setDateRangeFilter()}
                >
                  All time
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                  checked={dateRange.start !== undefined && dateRange.end !== undefined}
                  onCheckedChange={() => setDateRangeFilter(1)}
                >
                  Last 24 hours
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                  checked={false}
                  onCheckedChange={() => setDateRangeFilter(7)}
                >
                  Last 7 days
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                  checked={false}
                  onCheckedChange={() => setDateRangeFilter(30)}
                >
                  Last 30 days
                </DropdownMenuCheckboxItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        )}
      </div>
      
      <ScrollArea className="h-[400px] pr-4">
        {loading && !propEvents && (
          <EventFeedSkeleton />
        )}

        {error && !propEvents && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-neutral-500">
              <p className="text-sm">Failed to load events</p>
              <p className="text-xs mt-1">{error.message}</p>
            </div>
          </div>
        )}

        {!loading && events.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-neutral-500">
              <p className="text-sm">No events yet</p>
              <p className="text-xs mt-1">Events will appear here as they happen</p>
            </div>
          </div>
        )}

        <div className="space-y-2">
          {events.map((event) => {
            const isNew = newEventIds.has(event.id);
            return (
              <div
                key={event.id}
                className={`flex items-start gap-3 p-3 bg-white rounded-lg border hover:shadow-sm transition-all duration-300 ease-in-out ${
                  isNew ? 'ring-2 ring-primary/50 animate-in fade-in slide-in-from-top-2' : ''
                }`}
              >
              <div className="w-16 h-12 bg-neutral-100 rounded flex items-center justify-center text-2xl flex-shrink-0">
                {eventIcons[event.type]}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2 mb-1">
                  <Badge
                    variant="outline"
                    className={`${eventColors[event.type]} text-xs`}
                  >
                    {event.type}
                  </Badge>
                  <span className="text-xs text-neutral-500 whitespace-nowrap">
                    {formatDistanceToNow(event.timestamp, { addSuffix: true })}
                  </span>
                </div>
                
                <div className="flex items-center gap-3 text-xs text-neutral-600">
                  {event.confidence && (
                    <span>{Math.round(event.confidence * 100)}% confidence</span>
                  )}
                  {event.duration && <span>{event.duration}s duration</span>}
                </div>
              </div>
            </div>
            );
          })}
        </div>

        {/* Load More Button */}
        {!propEvents && showLoadMore && events.length >= currentLimit && !loading && (
          <div className="flex justify-center pt-4">
            <Button
              variant="outline"
              size="sm"
              onClick={loadMore}
              disabled={loading}
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
      </ScrollArea>
    </div>
  );
}
