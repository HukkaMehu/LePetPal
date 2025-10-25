import { useState, useRef } from 'react';
import { Event } from '../lib/mockData';
import { Scissors } from 'lucide-react';

interface TimelineProps {
  events: Event[];
  onClipRegion?: (start: number, end: number) => void;
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

export default function Timeline({ events, onClipRegion }: TimelineProps) {
  const [scrubPosition, setScrubPosition] = useState(100);
  const [clipStart, setClipStart] = useState<number | null>(null);
  const [clipEnd, setClipEnd] = useState<number | null>(null);
  const [hoveredEvent, setHoveredEvent] = useState<Event | null>(null);
  const [hoverPosition, setHoverPosition] = useState({ x: 0, y: 0 });
  const timelineRef = useRef<HTMLDivElement>(null);

  const handleScrub = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!timelineRef.current) return;
    const rect = timelineRef.current.getBoundingClientRect();
    const position = ((e.clientX - rect.left) / rect.width) * 100;
    setScrubPosition(Math.max(0, Math.min(100, position)));
  };

  const handleEventHover = (event: Event, e: React.MouseEvent) => {
    setHoveredEvent(event);
    setHoverPosition({ x: e.clientX, y: e.clientY });
  };

  const handleClipHandle = (e: React.MouseEvent, type: 'start' | 'end') => {
    e.stopPropagation();
    if (!timelineRef.current) return;
    const rect = timelineRef.current.getBoundingClientRect();
    const position = ((e.clientX - rect.left) / rect.width) * 100;
    
    if (type === 'start') {
      setClipStart(Math.max(0, Math.min(100, position)));
    } else {
      setClipEnd(Math.max(0, Math.min(100, position)));
    }
  };

  // Calculate event positions (last 60 minutes of buffer)
  const now = new Date();
  const bufferStart = new Date(now.getTime() - 60 * 60 * 1000);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-neutral-600">Playback Buffer (60min)</span>
        <div className="flex items-center gap-3 text-xs text-neutral-500">
          <span>Scrub position: -{Math.round((100 - scrubPosition) * 0.6)}min</span>
          {clipStart !== null && clipEnd !== null && (
            <span className="flex items-center gap-1">
              <Scissors className="w-3 h-3" />
              Clip: {Math.abs(clipEnd - clipStart).toFixed(0)}% selected
            </span>
          )}
        </div>
      </div>

      <div
        ref={timelineRef}
        className="relative h-20 bg-neutral-100 rounded-lg cursor-pointer overflow-hidden"
        onClick={handleScrub}
      >
        {/* Timeline background gradient */}
        <div className="absolute inset-0 bg-gradient-to-r from-neutral-200 via-neutral-100 to-neutral-50" />

        {/* Event markers */}
        {events.map((event) => {
          const eventTime = event.timestamp.getTime();
          const position = ((eventTime - bufferStart.getTime()) / (60 * 60 * 1000)) * 100;
          
          if (position < 0 || position > 100) return null;

          return (
            <button
              key={event.id}
              className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-8 h-8 hover:scale-125 transition-transform z-10"
              style={{ left: `${position}%` }}
              onMouseEnter={(e) => handleEventHover(event, e)}
              onMouseLeave={() => setHoveredEvent(null)}
              onClick={(e) => {
                e.stopPropagation();
                setScrubPosition(position);
              }}
            >
              <span className="text-xl drop-shadow-md">{eventIcons[event.type]}</span>
            </button>
          );
        })}

        {/* Clip region */}
        {clipStart !== null && clipEnd !== null && (
          <div
            className="absolute top-0 bottom-0 bg-blue-400/30 border-l-2 border-r-2 border-blue-500"
            style={{
              left: `${Math.min(clipStart, clipEnd)}%`,
              width: `${Math.abs(clipEnd - clipStart)}%`,
            }}
          />
        )}

        {/* Clip handles */}
        {clipStart !== null && (
          <div
            className="absolute top-0 bottom-0 w-1 bg-blue-500 cursor-ew-resize z-20"
            style={{ left: `${clipStart}%` }}
            onMouseDown={(e) => {
              const moveHandler = (moveE: MouseEvent) => {
                if (!timelineRef.current) return;
                const rect = timelineRef.current.getBoundingClientRect();
                const pos = ((moveE.clientX - rect.left) / rect.width) * 100;
                setClipStart(Math.max(0, Math.min(100, pos)));
              };
              const upHandler = () => {
                document.removeEventListener('mousemove', moveHandler);
                document.removeEventListener('mouseup', upHandler);
              };
              document.addEventListener('mousemove', moveHandler);
              document.addEventListener('mouseup', upHandler);
            }}
          >
            <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-3 h-8 bg-blue-500 rounded" />
          </div>
        )}
        
        {clipEnd !== null && (
          <div
            className="absolute top-0 bottom-0 w-1 bg-blue-500 cursor-ew-resize z-20"
            style={{ left: `${clipEnd}%` }}
            onMouseDown={(e) => {
              const moveHandler = (moveE: MouseEvent) => {
                if (!timelineRef.current) return;
                const rect = timelineRef.current.getBoundingClientRect();
                const pos = ((moveE.clientX - rect.left) / rect.width) * 100;
                setClipEnd(Math.max(0, Math.min(100, pos)));
              };
              const upHandler = () => {
                document.removeEventListener('mousemove', moveHandler);
                document.removeEventListener('mouseup', upHandler);
              };
              document.addEventListener('mousemove', moveHandler);
              document.addEventListener('mouseup', upHandler);
            }}
          >
            <div className="absolute top-1/2 -translate-y-1/2 translate-x-1/2 w-3 h-8 bg-blue-500 rounded" />
          </div>
        )}

        {/* Scrub indicator */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-red-500 z-30 pointer-events-none"
          style={{ left: `${scrubPosition}%` }}
        >
          <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-full mb-1 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-red-500" />
        </div>

        {/* Time markers */}
        <div className="absolute bottom-1 left-0 right-0 flex justify-between px-2 text-xs text-neutral-400 pointer-events-none">
          <span>-60min</span>
          <span>-30min</span>
          <span>Live</span>
        </div>
      </div>

      {/* Event tooltip */}
      {hoveredEvent && (
        <div
          className="fixed z-50 bg-neutral-900 text-white px-3 py-2 rounded shadow-lg text-sm pointer-events-none"
          style={{
            left: hoverPosition.x + 10,
            top: hoverPosition.y - 40,
          }}
        >
          <div className="font-medium">{hoveredEvent.type}</div>
          <div className="text-xs opacity-75">
            {hoveredEvent.timestamp.toLocaleTimeString()}
          </div>
        </div>
      )}

      {/* Clip controls */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          <button
            className="text-xs text-blue-600 hover:text-blue-700 px-2 py-1 hover:bg-blue-50 rounded"
            onClick={() => {
              if (clipStart === null) {
                setClipStart(scrubPosition - 10);
                setClipEnd(scrubPosition + 10);
              } else {
                setClipStart(null);
                setClipEnd(null);
              }
            }}
          >
            {clipStart === null ? 'Set clip region' : 'Clear clip'}
          </button>
        </div>
        <div className="text-xs text-neutral-500">
          Keyboard: B to bookmark current position
        </div>
      </div>
    </div>
  );
}
