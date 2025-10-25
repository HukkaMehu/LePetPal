// Mock data for the pet training app

export interface Event {
  id: string;
  type: 'sit' | 'fetch' | 'treat' | 'bark' | 'pet' | 'active' | 'calm';
  timestamp: Date;
  thumbnail?: string;
  confidence?: number;
  duration?: number;
}

export interface MediaItem {
  id: string;
  type: 'snapshot' | 'clip';
  url: string;
  thumbnail: string;
  timestamp: Date;
  duration?: number;
  tags: string[];
  events: Event[];
}

export interface AnalyticsData {
  timeInFrame: { hour: string; minutes: number }[];
  activityLevel: { date: string; calm: number; active: number }[];
  behaviors: { name: string; count: number }[];
  fetchSuccess: { date: string; success: number; total: number }[];
  barkFrequency: { hour: string; count: number }[];
  skillProgress: { skill: string; success: number; total: number }[];
}

export interface Routine {
  id: string;
  name: string;
  steps: RoutineStep[];
  schedule?: string;
  enabled: boolean;
  lastRun?: Date;
}

export interface RoutineStep {
  id: string;
  action: 'pet' | 'treat' | 'play' | 'sit-drill' | 'wait';
  duration?: number;
  repeat?: number;
}

// Generate mock events
export const generateMockEvents = (): Event[] => {
  const now = new Date();
  const events: Event[] = [];
  const types: Event['type'][] = ['sit', 'fetch', 'treat', 'bark', 'pet', 'active', 'calm'];

  for (let i = 0; i < 20; i++) {
    const timestamp = new Date(now.getTime() - i * 5 * 60 * 1000); // 5 min intervals
    events.push({
      id: `event-${i}`,
      type: types[Math.floor(Math.random() * types.length)],
      timestamp,
      confidence: Math.random() * 0.3 + 0.7, // 0.7-1.0
      duration: Math.floor(Math.random() * 30) + 5, // 5-35 seconds
    });
  }

  return events.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
};

// Generate mock media items
export const generateMockMedia = (): MediaItem[] => {
  const items: MediaItem[] = [];
  const now = new Date();

  for (let i = 0; i < 24; i++) {
    const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000); // hourly
    items.push({
      id: `media-${i}`,
      type: i % 3 === 0 ? 'clip' : 'snapshot',
      url: `https://images.unsplash.com/photo-${1560807707015 + i}`,
      thumbnail: `https://images.unsplash.com/photo-1560807707-8cc77767d783?w=400&h=300&fit=crop`,
      timestamp,
      duration: i % 3 === 0 ? Math.floor(Math.random() * 20) + 5 : undefined,
      tags: ['good-boy', 'training'].filter(() => Math.random() > 0.5),
      events: generateMockEvents().slice(0, 3),
    });
  }

  return items;
};

// Generate mock analytics data
export const generateMockAnalytics = (): AnalyticsData => {
  const hours = Array.from({ length: 24 }, (_, i) => ({
    hour: `${i}:00`,
    minutes: Math.floor(Math.random() * 45) + 5,
  }));

  const days = Array.from({ length: 7 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (6 - i));
    return {
      date: date.toLocaleDateString('en-US', { weekday: 'short' }),
      calm: Math.floor(Math.random() * 200) + 100,
      active: Math.floor(Math.random() * 150) + 50,
    };
  });

  const behaviors = [
    { name: 'Sit', count: Math.floor(Math.random() * 50) + 20 },
    { name: 'Stand', count: Math.floor(Math.random() * 60) + 30 },
    { name: 'Lie', count: Math.floor(Math.random() * 40) + 15 },
    { name: 'Fetch', count: Math.floor(Math.random() * 30) + 10 },
  ];

  const fetchData = days.map(d => ({
    date: d.date,
    success: Math.floor(Math.random() * 8) + 2,
    total: 10,
  }));

  const barkData = hours.slice(6, 22).map(h => ({
    hour: h.hour,
    count: Math.floor(Math.random() * 12),
  }));

  const skillProgress = [
    { 
      skill: 'Fetch',
      success: Math.floor(Math.random() * 20) + 65,
      total: 100
    },
    {
      skill: 'Come When Called',
      success: Math.floor(Math.random() * 15) + 70,
      total: 100
    },
    {
      skill: 'Sit on Command',
      success: Math.floor(Math.random() * 10) + 85,
      total: 100
    },
    {
      skill: 'Stay',
      success: Math.floor(Math.random() * 25) + 55,
      total: 100
    },
  ];

  return {
    timeInFrame: hours,
    activityLevel: days,
    behaviors,
    fetchSuccess: fetchData,
    barkFrequency: barkData,
    skillProgress,
  };
};

// Generate mock routines
export const generateMockRoutines = (): Routine[] => {
  return [
    {
      id: 'routine-1',
      name: 'Morning Routine',
      steps: [
        { id: 's1', action: 'treat', duration: 5 },
        { id: 's2', action: 'sit-drill', duration: 30, repeat: 3 },
        { id: 's3', action: 'pet', duration: 10 },
      ],
      schedule: '8:00 AM daily',
      enabled: true,
      lastRun: new Date(Date.now() - 3 * 60 * 60 * 1000),
    },
    {
      id: 'routine-2',
      name: 'Fetch Training',
      steps: [
        { id: 's4', action: 'play', duration: 60 },
        { id: 's5', action: 'treat', duration: 5 },
        { id: 's6', action: 'wait', duration: 30 },
      ],
      schedule: '4:00 PM Mon, Wed, Fri',
      enabled: true,
    },
    {
      id: 'routine-3',
      name: 'Evening Wind Down',
      steps: [
        { id: 's7', action: 'pet', duration: 120 },
        { id: 's8', action: 'treat', duration: 5 },
      ],
      enabled: false,
    },
  ];
};