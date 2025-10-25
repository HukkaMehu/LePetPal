# Pet Training Web App - Visual Structure

## Page Layout Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Connection Status Banner (when disconnected)                            │
│ [Reconnecting...] [Retry now]                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ Header                                                                   │
│                                                                          │
│  Dog Monitor                                    [? Keyboard Shortcuts]  │
│  AI-powered dog monitoring and training assistant                       │
│                                                                          │
│  [📹 Live View] [📊 Analytics] [🔄 Routines] [🖼️ Gallery]              │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ Main Content Area                                                        │
│                                                                          │
│  ┌─────────────────────────────────┬──────────────────────────────┐    │
│  │ LEFT COLUMN (2/3)               │ RIGHT COLUMN (1/3)           │    │
│  │                                 │                              │    │
│  │ ┌─────────────────────────────┐ │ ┌──────────────────────────┐ │    │
│  │ │                             │ │ │ Event Feed               │ │    │
│  │ │   Video Player              │ │ │ ┌──────────────────────┐ │ │    │
│  │ │   [Live Stream]             │ │ │ │ 🐕 Dog Detected      │ │ │    │
│  │ │                             │ │ │ │ 🪑 Sit               │ │ │    │
│  │ │   [Overlay Controls]        │ │ │ │ 🎾 Fetch Return      │ │ │    │
│  │ │                             │ │ │ │ 🔊 Bark              │ │ │    │
│  │ └─────────────────────────────┘ │ │ │ ...                  │ │ │    │
│  │                                 │ │ └──────────────────────┘ │ │    │
│  │ ┌─────────────────────────────┐ │ │ [Filter] [Live ●]        │ │    │
│  │ │ Timeline                    │ │ └──────────────────────────┘ │    │
│  │ │ ━━━━━━━━━━━━━━━━━━━━━━━━━━ │ │                              │    │
│  │ │ 🐕  🪑   🎾    🔊           │ │ ┌──────────────────────────┐ │    │
│  │ │ [In] [Out] [Zoom]           │ │ │ AI Coach Chat            │ │    │
│  │ └─────────────────────────────┘ │ │ ┌──────────────────────┐ │ │    │
│  │                                 │ │ │ User: How many sits? │ │ │    │
│  │ ┌─────────────────────────────┐ │ │ │                      │ │ │    │
│  │ │ Device Status               │ │ │ │ Coach: Your dog did  │ │ │    │
│  │ │ Status: ⚫ Offline          │ │ │ │ 15 sits today!       │ │ │    │
│  │ │ FPS: 30 | Temp: 42°C        │ │ │ │ [📹 0:45] [📹 1:23]  │ │ │    │
│  │ └─────────────────────────────┘ │ │ │                      │ │ │    │
│  │                                 │ │ │ [Ask a question...]  │ │ │    │
│  │ ┌─────────────────────────────┐ │ │ └──────────────────────┘ │ │    │
│  │ │ Robot Actions               │ │ └──────────────────────────┘ │    │
│  │ │ ┌───┐ ┌───┐ ┌───┐          │ │                              │    │
│  │ │ │🐾 │ │🦴 │ │🎾 │          │ │                              │    │
│  │ │ │Pet│ │Trt│ │Fch│          │ │                              │    │
│  │ │ └───┘ └───┘ └───┘          │ │                              │    │
│  │ │ (Not connected)             │ │                              │    │
│  │ └─────────────────────────────┘ │                              │    │
│  └─────────────────────────────────┴──────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ Toast Notification (bottom-right)                                       │
│ [📸 Snapshot captured!]                                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

## Analytics Tab Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Analytics Dashboard                                                      │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Time in Frame vs Off Frame                                       │   │
│  │ ┌─────────────────────────────────────────────────────────────┐ │   │
│  │ │     ╱╲                                                       │ │   │
│  │ │    ╱  ╲      ╱╲                                             │ │   │
│  │ │   ╱    ╲    ╱  ╲                                            │ │   │
│  │ │  ╱      ╲  ╱    ╲                                           │ │   │
│  │ └─────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────┐  ┌──────────────────────────┐           │
│  │ Sit/Stand/Lie Counts     │  │ Fetch Success Rate       │           │
│  │ ┌──────────────────────┐ │  │ ┌──────────────────────┐ │           │
│  │ │ ▓▓▓ ▓▓▓ ▓▓▓         │ │  │ │ Attempts: 12         │ │           │
│  │ │ ▓▓▓ ▓▓▓ ▓▓▓         │ │  │ │ Success: 9           │ │           │
│  │ │ ▓▓▓ ▓▓▓ ▓▓▓         │ │  │ │ Rate: 75%            │ │           │
│  │ └──────────────────────┘ │  │ └──────────────────────┘ │           │
│  └──────────────────────────┘  └──────────────────────────┘           │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Streaks & Badges                                                 │   │
│  │ 🏆 7-Day Sit Streak  🎯 5 Perfect Recall Days  ⭐ Calm Master   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Routines Tab Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Training Routines                                                        │
│                                                                          │
│  [+ Create New Routine]                    [All] [Enabled] [Disabled]  │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Morning Training Session                          [✓ Enabled]   │   │
│  │ Schedule: Every day at 8:00 AM                                   │   │
│  │ Steps: 🐾 Pet → 🪑 Sit Drill → 🦴 Treat → 🎾 Fetch             │   │
│  │ Next run: Tomorrow at 8:00 AM                                    │   │
│  │ [Edit] [Delete]                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Evening Calm Time                                 [  Disabled]   │   │
│  │ Schedule: Every day at 7:00 PM                                   │   │
│  │ Steps: 🐾 Pet → ⏱️ Wait → 🐾 Pet                               │   │
│  │ [Edit] [Delete]                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Gallery Tab Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Media Gallery                                                            │
│                                                                          │
│  [Snapshots] [Clips]                                                    │
│                                                                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                      │
│  │ [IMG]   │ │ [IMG]   │ │ [IMG]   │ │ [IMG]   │                      │
│  │         │ │         │ │         │ │         │                      │
│  │ 10:30AM │ │ 11:45AM │ │ 2:15PM  │ │ 4:30PM  │                      │
│  │ [Share] │ │ [Share] │ │ [Share] │ │ [Share] │                      │
│  │ [Delete]│ │ [Delete]│ │ [Delete]│ │ [Delete]│                      │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘                      │
│                                                                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                      │
│  │ [IMG]   │ │ [IMG]   │ │ [IMG]   │ │ [IMG]   │                      │
│  │         │ │         │ │         │ │         │                      │
│  │ 5:00PM  │ │ 6:20PM  │ │ 7:45PM  │ │ 8:15PM  │                      │
│  │ [Share] │ │ [Share] │ │ [Share] │ │ [Share] │                      │
│  │ [Delete]│ │ [Delete]│ │ [Delete]│ │ [Delete]│                      │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘                      │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
Home (page.tsx)
├── ConnectionStatusBanner
│   └── Shows when WebSocket disconnected
│
├── Header
│   ├── Title & Description
│   ├── KeyboardShortcutsHelp
│   └── Navigation Tabs
│
└── Main Content (Tab-based)
    │
    ├── Live View Tab
    │   ├── Left Column
    │   │   ├── VideoPlayer
    │   │   │   ├── Video stream (WebRTC/MJPEG)
    │   │   │   ├── Canvas overlay layer
    │   │   │   └── Playback controls
    │   │   ├── Timeline
    │   │   │   ├── Scrubber
    │   │   │   ├── Event markers
    │   │   │   ├── Clip in/out handles
    │   │   │   └── Zoom/pan controls
    │   │   ├── DeviceStatus
    │   │   │   ├── Status pill
    │   │   │   └── Telemetry strip
    │   │   └── RobotActionBar
    │   │       ├── Pet button
    │   │       ├── Treat button
    │   │       └── Fetch button
    │   │
    │   └── Right Column
    │       ├── EventFeed
    │       │   ├── Event list
    │       │   ├── Filter controls
    │       │   └── Connection status
    │       └── CoachChat
    │           ├── Message history
    │           ├── Input field
    │           └── Timestamp links
    │
    ├── Analytics Tab
    │   └── AnalyticsDashboard
    │       ├── Time-series charts
    │       ├── Behavior counts
    │       ├── Fetch success rate
    │       └── Streaks & badges
    │
    ├── Routines Tab
    │   └── RoutinesList
    │       ├── Routine cards
    │       ├── Enable/disable toggles
    │       └── Edit/delete actions
    │
    └── Gallery Tab
        └── Gallery
            ├── Tab switcher (Snapshots/Clips)
            ├── Media grid
            └── Share/delete actions

Toast Notification (global)
KeyboardShortcutsHint (global)
```

## Data Flow

```
WebSocket Connection
    ↓
Event Received
    ↓
Added to events array
    ↓
    ├─→ EventFeed (displays event)
    ├─→ Timeline (shows marker)
    └─→ CoachChat (context for questions)

User Clicks Event
    ↓
handleEventClick()
    ↓
setCurrentVideoTime()
    ↓
Timeline updates scrubber position

User Presses 'S' Key
    ↓
VideoPlayer keyboard handler
    ↓
onSnapshot() callback
    ↓
handleSnapshot()
    ↓
showToast("📸 Snapshot captured!")

User Clicks Timeline Marker
    ↓
onEventClick() callback
    ↓
handleEventClick()
    ↓
setCurrentVideoTime()
    ↓
showToast("⏩ Jumped to Xs")

Coach Chat Timestamp Click
    ↓
onTimestampClick() callback
    ↓
setCurrentVideoTime()
    ↓
showToast("⏩ Jumped to Xs")
```

## Responsive Breakpoints

```
Mobile (< 640px)
├── Single column layout
├── Stacked components
├── Full-width video
└── Scrollable tabs

Tablet (640px - 1024px)
├── 2-column layout on Live View
├── Video + Timeline stacked
├── Event Feed + Coach Chat stacked
└── Full-width other tabs

Desktop (> 1024px)
├── 3-column layout on Live View
├── Video + Timeline (2/3 width)
├── Event Feed + Coach Chat (1/3 width)
└── Centered content on other tabs
```

## State Management

```javascript
// Global State
activeTab: 'live' | 'analytics' | 'routines' | 'gallery'
events: Event[]
currentVideoTime: number
videoDuration: number
connectionStatus: ConnectionStatus
toastMessage: string | null

// WebSocket Hook
useWebSocket({
  url: WS_URL,
  onEvent: (event) => setEvents([event, ...events])
})

// Callbacks
handleSnapshot()
handleClipMark(timestamp)
handleBookmark(timestamp)
handleEventClick(event)
handleTimelineSeek(timeMs)
handleRobotCommand(command)
showToast(message)
```

This structure provides a complete, integrated experience while maintaining clean separation of concerns and component reusability.
