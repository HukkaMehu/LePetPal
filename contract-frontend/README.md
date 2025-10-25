# LePetPal Frontend

Next.js 14 web application for controlling the LePetPal AI pet robotics system.

## Features

- Live MJPEG video streaming with overlay controls
- Command preset buttons (Play with Ball, Give Treat, Go Home, Speak)
- Real-time status display with command execution feedback
- Configuration panel for API base URL and authentication
- Responsive design with Tailwind CSS
- React Context for global state management

## Getting Started

### Prerequisites

- Node.js 18+ or higher
- npm (comes with Node.js) or yarn
- Backend server running (see backend/README.md)

### Installation

1. Clone the repository and navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

### Configuration

1. Copy the example environment file:
```bash
cp .env.local.example .env.local
```

2. Edit `.env.local` and configure your backend API URL:
```env
# For local development
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000

# For LAN deployment (replace with your backend server IP)
# NEXT_PUBLIC_API_BASE_URL=http://192.168.1.100:5000
```

**Environment Variables:**
- `NEXT_PUBLIC_API_BASE_URL` (required): Backend API base URL
- `NEXT_PUBLIC_DEFAULT_VIDEO_WIDTH` (optional): Default video width in pixels (default: 1280)
- `NEXT_PUBLIC_DEFAULT_VIDEO_HEIGHT` (optional): Default video height in pixels (default: 720)
- `NEXT_PUBLIC_SSE_RECONNECT_MAX_DELAY` (optional): Max SSE reconnection delay in ms (default: 8000)

### Development

Start the development server:
```bash
npm run dev
```

The application will be available at [http://localhost:3000](http://localhost:3000)

**Development Features:**
- Hot module replacement (HMR) for instant updates
- TypeScript type checking
- ESLint for code quality
- Detailed error messages in browser

### Production Build

1. Build the optimized production bundle:
```bash
npm run build
```

2. Start the production server:
```bash
npm start
```

The production server runs on port 3000 by default. To use a different port:
```bash
PORT=8080 npm start
```

**Production Optimizations:**
- Minified JavaScript and CSS
- Optimized images and assets
- Server-side rendering (SSR)
- Static page generation where applicable

### Linting

Run ESLint to check code quality:
```bash
npm run lint
```

## Deployment Options

### Option 1: Local Network (LAN) Deployment

For hackathon demos or home use:

1. Build the production bundle:
```bash
npm run build
```

2. Start the server:
```bash
npm start
```

3. Find your local IP address:
   - **Windows**: `ipconfig` (look for IPv4 Address)
   - **macOS/Linux**: `ifconfig` or `ip addr` (look for inet address)

4. Access from other devices on the same network:
   - Open browser to `http://YOUR_IP:3000`
   - Example: `http://192.168.1.50:3000`

### Option 2: Vercel Deployment

Deploy to Vercel for cloud hosting:

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
vercel
```

3. Follow the prompts to link your project

4. Set environment variables in Vercel dashboard:
   - Go to Project Settings → Environment Variables
   - Add `NEXT_PUBLIC_API_BASE_URL` with your backend URL

**Note:** For Vercel deployment, your backend must be publicly accessible or you'll need to deploy the backend to a cloud service as well.

### Option 3: Docker Deployment

Create a `Dockerfile` in the frontend directory:

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/next.config.mjs ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
```

Build and run:
```bash
docker build -t lepetpal-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_BASE_URL=http://backend:5000 lepetpal-frontend
```

## Browser Compatibility

### Supported Browsers

The LePetPal frontend is compatible with modern browsers that support ES2020 features:

**Desktop:**
- Chrome 90+ (recommended)
- Firefox 88+
- Safari 14+
- Edge 90+

**Mobile:**
- iOS Safari 14+
- Chrome for Android 90+
- Samsung Internet 14+

### Required Browser Features

- **Server-Sent Events (SSE)**: For real-time command updates
  - Fallback: Automatic polling if SSE not supported
- **ES2020**: Modern JavaScript features (optional chaining, nullish coalescing)
- **Fetch API**: For HTTP requests
- **LocalStorage**: For configuration persistence
- **CSS Grid & Flexbox**: For responsive layout

### Known Limitations

- **Internet Explorer**: Not supported (IE 11 and below)
- **Older Mobile Browsers**: May have degraded experience on browsers older than 2020
- **SSE Limitations**: Some corporate firewalls may block SSE connections (polling fallback activates automatically)

### Testing Recommendations

Test the application on:
1. Primary development browser (Chrome/Firefox recommended)
2. Target mobile devices (iOS Safari and Chrome for Android)
3. Any specific browsers your users will use

## npm Scripts Reference

- `npm run dev` - Start development server with hot reload on port 3000
- `npm run build` - Create optimized production build in `.next` directory
- `npm start` - Start production server (requires `npm run build` first)
- `npm run lint` - Run ESLint code quality checks
- `npm run type-check` - Run TypeScript type checking without emitting files
- `npm run clean` - Remove build cache and artifacts

## Quick Start Guide

**For First-Time Setup:**

1. Ensure backend is running (see `backend/README.md`)
2. Install dependencies: `npm install`
3. Copy environment file: `cp .env.local.example .env.local`
4. Edit `.env.local` with your backend URL
5. Start development: `npm run dev`
6. Open browser to `http://localhost:3000`

**For Demo/Production:**

1. Build: `npm run build`
2. Start: `npm start`
3. Access from network: `http://YOUR_IP:3000`

## Troubleshooting

### Build Errors

**Issue:** `npm run build` fails with module errors
- **Solution:** Delete `node_modules` and `.next`, then run `npm install` again

**Issue:** TypeScript errors during build
- **Solution:** Run `npm run type-check` to see detailed errors

### Runtime Errors

**Issue:** "Failed to fetch" or CORS errors
- **Solution:** Verify backend URL in `.env.local` is correct and backend is running
- **Solution:** Check backend CORS configuration allows your frontend origin

**Issue:** Video stream not loading
- **Solution:** Verify backend `/video_feed` endpoint is accessible
- **Solution:** Check browser console for specific error messages
- **Solution:** Try disabling overlays in the video panel

**Issue:** SSE connection failing
- **Solution:** Application automatically falls back to polling
- **Solution:** Check browser console for SSE error details
- **Solution:** Some networks/firewalls block SSE - polling fallback will work

**Issue:** Commands not executing
- **Solution:** Check backend logs for errors
- **Solution:** Verify API base URL is configured correctly
- **Solution:** Test backend health endpoint: `curl http://YOUR_BACKEND_URL/health`

### Development Issues

**Issue:** Hot reload not working
- **Solution:** Restart dev server with `npm run dev`
- **Solution:** Clear Next.js cache with `npm run clean`

**Issue:** Port 3000 already in use
- **Solution:** Kill existing process or use different port: `PORT=3001 npm run dev`

## Performance Tips

- **Production builds** are significantly faster than development mode
- **Video quality** can be adjusted in the ConfigPanel to reduce bandwidth
- **Disable overlays** if video stream performance is poor
- **Use wired connection** for best video streaming performance
- **Close unused browser tabs** to free up resources for video rendering

## Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── layout.tsx         # Root layout with AppProvider
│   ├── page.tsx           # Main page with component layout
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── ConfigPanel/       # API configuration UI
│   ├── VideoPanel/        # Video stream display
│   ├── CommandBar/        # Command preset buttons
│   └── StatusDisplay/     # Command status feedback
├── contexts/              # React Context providers
│   └── AppContext.tsx     # Global app state
├── types/                 # TypeScript type definitions
│   └── index.ts           # Shared types
└── .env.local            # Environment variables
```

## Component Overview

### ConfigPanel
- Collapsible configuration panel
- Base URL and auth token inputs
- Persists settings to localStorage

### VideoPanel
- Displays MJPEG stream from backend
- Toggle overlays on/off
- Error handling with retry

### CommandBar
- Four preset command buttons
- Disables non-interrupt commands during execution
- Go Home always available as interrupt

### StatusDisplay
- Shows current command state (Idle/Executing/Completed/Error)
- Displays phase, confidence, and duration
- Color-coded status indicators

### AppContext
- Global state management with React Context
- Manages config, current command, and errors
- localStorage persistence for configuration

## Requirements Mapping

This implementation satisfies:
- **Requirement 6.1**: Configuration panel with base URL and auth token
- **Requirement 6.2**: Command preset buttons
- **Requirement 6.3**: Button disabling during execution
- **Requirement 6.4**: Global status indicator
- **Requirement 6.5**: Success/failure messaging
- **Requirement 10**: Mobile responsive design with touch-friendly buttons
