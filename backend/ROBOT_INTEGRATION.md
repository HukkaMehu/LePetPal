# Robot Integration Placeholders

This document describes the robot integration placeholder implementation for the dog monitor web application.

## Overview

The robot integration placeholders provide a clean interface for future SO-101 robot arm integration without requiring refactoring when the hardware is connected. All components are currently in "offline" mode and will be activated when the robot is connected.

## Backend API

### Commands Endpoint

**POST /api/commands**

Sends a command to the robot arm. Currently returns 501 Not Implemented.

**Request Body:**
```json
{
  "type": "pet" | "treat" | "fetch",
  "params": {
    // Optional command-specific parameters
  }
}
```

**Response (Current - Offline):**
```json
{
  "status": 501,
  "message": "Robot not connected",
  "command_id": null
}
```

**Response (Future - When Connected):**
```json
{
  "status": 200,
  "message": "Command queued",
  "command_id": "uuid-here"
}
```

### Robot Status Endpoint

**GET /api/commands/status**

Returns the current robot device status and telemetry.

**Response:**
```json
{
  "device": "offline",
  "capabilities": [],
  "last_seen": null,
  "telemetry": {
    "fps": 30,
    "temperature": 42,
    "latency_ms": 0,
    "battery_level": 0
  }
}
```

## Frontend Components

### RobotActionBar

Displays action buttons for robot commands (pet, treat, fetch).

**Props:**
- `deviceStatus`: 'connected' | 'offline'
- `onCommand`: (command: RobotCommand) => void
- `className`: string (optional)

**Features:**
- Disabled state when device is offline
- Tooltips explaining functionality
- Visual feedback for command execution
- Information banner about future functionality

**Usage:**
```tsx
import RobotActionBar from '@/components/RobotActionBar';

<RobotActionBar
  deviceStatus="offline"
  onCommand={async (cmd) => {
    const response = await fetch('/api/commands', {
      method: 'POST',
      body: JSON.stringify(cmd)
    });
  }}
/>
```

### DeviceStatus

Displays device connection status and telemetry data.

**Props:**
- `status`: 'connected' | 'offline'
- `telemetry`: { fps, temperature, latencyMs, batteryLevel } (optional)
- `className`: string (optional)

**Features:**
- Status pill with color coding
- Telemetry strip showing FPS, temperature, latency, battery
- Mock data display when offline
- Responsive grid layout

**Usage:**
```tsx
import DeviceStatus from '@/components/DeviceStatus';

<DeviceStatus
  status="offline"
  telemetry={{
    fps: 30,
    temperature: 42,
    latencyMs: 0,
    batteryLevel: 0
  }}
/>
```

### PolicySelector

Dropdown for selecting robot AI policy (replay, act, smolvla).

**Props:**
- `deviceStatus`: 'connected' | 'offline'
- `currentPolicy`: string (optional, default: 'replay')
- `onPolicyChange`: (policy: string) => void
- `className`: string (optional)

**Features:**
- Disabled when device is offline
- Three policy options with descriptions
- Visual feedback for current selection
- Helper text explaining availability

**Usage:**
```tsx
import PolicySelector from '@/components/PolicySelector';

<PolicySelector
  deviceStatus="offline"
  currentPolicy="replay"
  onPolicyChange={(policy) => {
    console.log('Policy changed to:', policy);
  }}
/>
```

## Demo Page

A demo page is available at `/robot-demo` that showcases all robot integration components.

**Features:**
- Device status display with toggle (for demo purposes)
- Robot action buttons with API integration
- Policy selector with change handling
- Integration notes and documentation

**Access:**
Navigate to `http://localhost:3000/robot-demo` to view the demo.

## Integration with Main Application

To integrate these components into the main application:

1. **Add to Live View Page:**
```tsx
import RobotActionBar from '@/components/RobotActionBar';
import DeviceStatus from '@/components/DeviceStatus';
import PolicySelector from '@/components/PolicySelector';

// In your component:
const [deviceStatus, setDeviceStatus] = useState<'connected' | 'offline'>('offline');

// Add to your layout:
<DeviceStatus status={deviceStatus} />
<RobotActionBar deviceStatus={deviceStatus} onCommand={handleCommand} />
<PolicySelector deviceStatus={deviceStatus} onPolicyChange={handlePolicyChange} />
```

2. **Connect to WebSocket for Real-time Status:**
```tsx
// Subscribe to device status updates via WebSocket
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8000/ws/ui');
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'device_status') {
      setDeviceStatus(data.data.status);
    }
  };
  
  return () => ws.close();
}, []);
```

## Future Robot Integration

When the SO-101 robot arm is connected, the following changes will be needed:

### Backend Changes:

1. **Update `/api/commands` endpoint:**
   - Remove 501 status code
   - Validate command against device capabilities
   - Dispatch to robot worker via message queue
   - Return command execution status

2. **Add robot worker service:**
   - Create background worker for robot commands
   - Implement command queue processing
   - Handle robot communication protocol
   - Report execution status back to API

3. **Update `/api/commands/status` endpoint:**
   - Return actual device connection status
   - Provide real telemetry data from robot
   - Include device capabilities list

### Frontend Changes:

1. **Update device status:**
   - Change `deviceStatus` from 'offline' to 'connected'
   - Display real telemetry data from robot
   - Enable all robot controls

2. **Enable policy switching:**
   - Connect to `/api/models/switch` endpoint
   - Handle policy change confirmations
   - Display active policy status

3. **Add command feedback:**
   - Show command execution progress
   - Display success/failure notifications
   - Handle command queue status

## Requirements Mapping

This implementation satisfies the following requirements:

- **Requirement 10.1**: Robot command placeholders with "not connected" status
- **Requirement 10.2**: Device status pill showing "offline"
- **Requirement 10.3**: Telemetry strip with mock FPS and temperature
- **Requirement 10.4**: Policy selector dropdown (disabled until connected)

## Testing

### Manual Testing:

1. Start the backend server:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

2. Start the frontend:
```bash
cd frontend
npm run dev
```

3. Navigate to `http://localhost:3000/robot-demo`

4. Test the following:
   - All robot action buttons are disabled
   - Clicking buttons shows "Robot not connected" message
   - Device status shows "Offline"
   - Telemetry displays mock data
   - Policy selector is disabled
   - Tooltips explain future functionality

### API Testing:

```bash
# Test commands endpoint
curl -X POST http://localhost:8000/api/commands \
  -H "Content-Type: application/json" \
  -d '{"type": "pet"}'

# Expected response:
# {"status": 501, "message": "Robot not connected", "command_id": null}

# Test status endpoint
curl http://localhost:8000/api/commands/status

# Expected response:
# {"device": "offline", "capabilities": [], ...}
```

## Notes

- All components are designed to work seamlessly when robot is connected
- No refactoring will be required to enable robot functionality
- The UI clearly communicates that robot features are coming soon
- Mock telemetry data provides realistic preview of future functionality
