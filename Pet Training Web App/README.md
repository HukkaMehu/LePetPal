
# Pet Training Web App

This is a code bundle for Pet Training Web App. The original project is available at https://www.figma.com/design/BauoVbfoGACz8cOI0crHPV/Pet-Training-Web-App.

## Setup

### 1. Install Dependencies

Run `npm i` to install the dependencies.

### 2. Backend Integration Configuration

The Pet Training Web App connects to the LePetPal backend API for live video streaming and command execution.

#### Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Configure the backend URL in `.env`:
   ```ini
   VITE_API_BASE_URL=http://localhost:5000
   ```

   - **Development**: Use `http://localhost:5000` (default)
   - **Production**: Set to your deployed backend URL (e.g., `https://api.yourpetpal.com`)

#### Environment Variable Usage

- `VITE_API_BASE_URL`: The base URL for the backend API
  - Used for all API requests (commands, status polling, health checks)
  - Used to construct the video feed URL (`/video_feed` endpoint)
  - Can be overridden at runtime through the Settings page in the app

**Note**: Vite environment variables are embedded at build time. If you change the `.env` file, restart the development server or rebuild the application.

### 3. Start the Backend Server

Before running the frontend, ensure the LePetPal backend is running:

```bash
cd backend
python run_backend.py
```

See `backend/README.md` for detailed backend setup instructions.

### 4. Run the Development Server

Run `npm run dev` to start the development server.

The app will be available at `http://localhost:5173`

## Runtime Configuration

You can also configure the backend URL at runtime without rebuilding:

1. Open the app in your browser
2. Navigate to the **Settings** page
3. Find the **Backend Connection** section
4. Enter your backend URL
5. Click **Test Connection** to verify connectivity

The runtime URL is saved to browser localStorage and takes precedence over the environment variable.

## Features

- **Live Video Streaming**: Real-time MJPEG video feed from your pet camera
- **Remote Commands**: Send training commands (Pet, Treat, Fetch) to the robot
- **Status Monitoring**: Track command execution status and robot state
- **Backend Configuration**: Easy setup and testing of backend connectivity

## Troubleshooting

### Cannot connect to backend

- Verify the backend server is running on the configured URL
- Check that CORS is properly configured in the backend (see `backend/README.md`)
- Test the connection using the Settings page
- Check browser console for detailed error messages

### Video stream not loading

- Ensure the backend `/video_feed` endpoint is accessible
- Verify camera hardware is connected and configured
- Check that the backend URL is correct in Settings

### Commands not executing

- Test backend connectivity in the Settings page
- Verify the backend is not in an error state
- Check backend logs for command processing errors
  