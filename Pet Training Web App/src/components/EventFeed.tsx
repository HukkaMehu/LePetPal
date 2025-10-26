import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import { Event } from '../lib/mockData';
import { formatDistanceToNow } from 'date-fns';

interface EventFeedProps {
  events: Event[];
}

const eventIcons: Record<Event['type'], string> = {
  sit: '🪑',
  fetch: '🎾',
  treat: '🦴',
  bark: '🔊',
  pet: '💝',
  active: '⚡',
  calm: '😌',
};

const eventColors: Record<Event['type'], string> = {
  sit: 'bg-blue-100 text-blue-700 border-blue-200',
  fetch: 'bg-green-100 text-green-700 border-green-200',
  treat: 'bg-amber-100 text-amber-700 border-amber-200',
  bark: 'bg-red-100 text-red-700 border-red-200',
  pet: 'bg-pink-100 text-pink-700 border-pink-200',
  active: 'bg-purple-100 text-purple-700 border-purple-200',
  calm: 'bg-teal-100 text-teal-700 border-teal-200',
};

export default function EventFeed({ events }: EventFeedProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-neutral-900">Activity Feed</h3>
      
      <ScrollArea className="h-[400px] pr-4">
        <div className="space-y-2">
          {events.map((event) => (
            <div
              key={event.id}
              className="flex items-start gap-3 p-3 bg-white rounded-lg border hover:shadow-sm transition-shadow"
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
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
