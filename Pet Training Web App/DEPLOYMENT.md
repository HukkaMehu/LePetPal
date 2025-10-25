# Deployment Guide

This guide provides instructions for building and deploying the Pet Training Web App to production.

## Prerequisites

- Node.js 18+ and npm installed
- Access to backend API and AI service endpoints
- Production domain/hosting configured

## Environment Variables

The application requires the following environment variables to be configured:

### Required Variables

```env
# Backend API Configuration
VITE_API_BASE_URL=https://your-backend-api.com
VITE_AI_SERVICE_URL=https://your-ai-service.com
VITE_WS_URL=wss://your-backend-api.com/ws

# Video Streaming Configuration
VITE_VIDEO_STREAM_URL=https://your-backend-api.com/video/mjpeg
```

### Optional Variables

```env
# Enable debug logging (default: false)
VITE_DEBUG=false
```

### Environment Setup

1. **Development**: Copy `.env.example` to `.env` and configure for local development
   ```bash
   cp .env.example .env
   ```

2. **Production**: Set environment variables in your hosting platform's configuration
   - For Vercel: Project Settings → Environment Variables
   - For Netlify: Site Settings → Build & Deploy → Environment
   - For AWS/Docker: Use environment variable injection or .env files

## Build Process

### Local Build

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create production build:
   ```bash
   npm run build
   ```

3. The build output will be in the `build/` directory

4. Test production build locally:
   ```bash
   npm run preview
   ```
   This will serve the production build at http://localhost:4173

### Build Output

The production build creates:
- `build/index.html` - Main HTML file
- `build/assets/` - Optimized JavaScript and CSS bundles
- All assets are fingerprinted for cache busting

## Deployment Options

### Option 1: Static Hosting (Vercel, Netlify)

#### Vercel

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Deploy:
   ```bash
   vercel --prod
   ```

3. Configure environment variables in Vercel dashboard

#### Netlify

1. Install Netlify CLI:
   ```bash
   npm install -g netlify-cli
   ```

2. Deploy:
   ```bash
   netlify deploy --prod --dir=build
   ```

3. Configure environment variables in Netlify dashboard

### Option 2: AWS S3 + CloudFront

1. Build the application:
   ```bash
   npm run build
   ```

2. Upload to S3:
   ```bash
   aws s3 sync build/ s3://your-bucket-name --delete
   ```

3. Invalidate CloudFront cache:
   ```bash
   aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
   ```

### Option 3: Docker + Nginx

1. Create `Dockerfile`:
   ```dockerfile
   FROM node:18-alpine AS builder
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci
   COPY . .
   RUN npm run build

   FROM nginx:alpine
   COPY --from=builder /app/build /usr/share/nginx/html
   COPY nginx.conf /etc/nginx/conf.d/default.conf
   EXPOSE 80
   CMD ["nginx", "-g", "daemon off;"]
   ```

2. Create `nginx.conf`:
   ```nginx
   server {
       listen 80;
       server_name _;
       root /usr/share/nginx/html;
       index index.html;

       location / {
           try_files $uri $uri/ /index.html;
       }

       location /assets {
           expires 1y;
           add_header Cache-Control "public, immutable";
       }
   }
   ```

3. Build and run:
   ```bash
   docker build -t pet-training-app .
   docker run -p 80:80 pet-training-app
   ```

### Option 4: Traditional Web Server

1. Build the application:
   ```bash
   npm run build
   ```

2. Copy `build/` directory contents to your web server's document root

3. Configure web server for SPA routing (redirect all routes to index.html)

## Backend Configuration Requirements

The backend must be configured to allow requests from the frontend domain.

### CORS Configuration

Update your FastAPI backend's CORS settings:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://your-production-domain.com",  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### WebSocket Configuration

Ensure WebSocket connections are allowed from your frontend domain:

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Verify origin if needed
    origin = websocket.headers.get("origin")
    if origin not in allowed_origins:
        await websocket.close(code=1008)
        return
    
    await websocket.accept()
    # ... rest of WebSocket logic
```

### Video Streaming

Ensure video streaming endpoints are accessible:
- MJPEG stream: `/video/mjpeg`
- WebRTC signaling: `/video/webrtc` (if implemented)

### API Endpoints

Verify all required endpoints are accessible:
- Events: `/api/events`
- Routines: `/api/routines`
- Analytics: `/api/analytics/*`
- Media: `/api/clips`, `/api/snapshots`
- Status: `/api/status`
- Models: `/api/models`
- Robot control: `/api/robot/*`

### AI Service Configuration

Ensure the AI service is accessible from the frontend:
- Coach endpoint: `/coach/chat`
- Streaming endpoint: `/coach/stream`

## Post-Deployment Verification

After deployment, verify the following:

1. **Frontend loads correctly**
   - Visit your production URL
   - Check browser console for errors
   - Verify all assets load (no 404s)

2. **API connectivity**
   - Open browser DevTools → Network tab
   - Verify API calls succeed (200 status)
   - Check for CORS errors

3. **WebSocket connection**
   - Verify WebSocket connects successfully
   - Check for real-time updates in the timeline

4. **Video streaming**
   - Verify live video stream displays
   - Check video metrics (FPS, latency)

5. **Feature functionality**
   - Test creating/editing routines
   - Test viewing analytics
   - Test gallery media loading
   - Test coach chat
   - Test robot controls

## Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:
1. Verify backend CORS configuration includes your frontend domain
2. Check that credentials are allowed if using authentication
3. Ensure preflight OPTIONS requests are handled

### WebSocket Connection Fails

If WebSocket fails to connect:
1. Verify WSS (secure WebSocket) is used in production
2. Check firewall/proxy settings allow WebSocket connections
3. Verify backend WebSocket endpoint is accessible

### Assets Not Loading

If CSS/JS assets fail to load:
1. Check that base URL is configured correctly in vite.config.ts
2. Verify web server is configured to serve static files
3. Check file permissions on deployed files

### Environment Variables Not Working

If environment variables aren't being read:
1. Verify variables are prefixed with `VITE_`
2. Rebuild the application after changing variables
3. Check hosting platform's environment variable configuration

## Performance Optimization

### Code Splitting

The build currently generates a single large bundle. Consider implementing code splitting:

```typescript
// Use dynamic imports for routes
const AnalyticsPage = lazy(() => import('./components/AnalyticsPage'));
const GalleryPage = lazy(() => import('./components/GalleryPage'));
```

### Caching Strategy

Configure appropriate cache headers:
- HTML: No cache or short cache (5 minutes)
- Assets (JS/CSS): Long cache (1 year) - files are fingerprinted
- API responses: Appropriate cache based on data freshness

### CDN Configuration

For optimal performance:
1. Serve static assets through a CDN
2. Enable gzip/brotli compression
3. Configure appropriate cache headers
4. Use HTTP/2 or HTTP/3

## Monitoring

Consider implementing:
- Error tracking (Sentry, Rollbar)
- Performance monitoring (Web Vitals)
- Analytics (Google Analytics, Plausible)
- Uptime monitoring (UptimeRobot, Pingdom)

## Rollback Procedure

If issues occur after deployment:

1. **Vercel/Netlify**: Use platform's rollback feature to previous deployment
2. **S3/CloudFront**: Restore previous version from S3 versioning
3. **Docker**: Revert to previous image tag
4. **Traditional hosting**: Restore from backup

## Security Considerations

1. **HTTPS**: Always use HTTPS in production
2. **Environment Variables**: Never commit sensitive data to version control
3. **API Keys**: Store API keys securely in environment variables
4. **Content Security Policy**: Consider implementing CSP headers
5. **Regular Updates**: Keep dependencies updated for security patches

## Support

For issues or questions:
- Check browser console for errors
- Review backend logs for API errors
- Verify environment variables are set correctly
- Ensure backend services are running and accessible
