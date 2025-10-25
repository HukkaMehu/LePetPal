# LePetPal Frontend Deployment Guide

## Pre-Deployment Checklist

### Development Environment
- [ ] Node.js 18+ installed
- [ ] Dependencies installed (`npm install`)
- [ ] `.env.local` configured with correct backend URL
- [ ] Development server runs without errors (`npm run dev`)
- [ ] All TypeScript checks pass (`npm run type-check`)
- [ ] Linting passes (`npm run lint`)

### Backend Integration
- [ ] Backend server is running and accessible
- [ ] Health endpoint responds: `curl http://BACKEND_URL/health`
- [ ] Video feed endpoint accessible: `http://BACKEND_URL/video_feed`
- [ ] CORS configured to allow frontend origin
- [ ] API version matches (v1)

### Browser Testing
- [ ] Tested on Chrome/Firefox (desktop)
- [ ] Tested on iOS Safari (mobile)
- [ ] Tested on Chrome for Android (mobile)
- [ ] Video stream loads correctly
- [ ] Commands execute successfully
- [ ] SSE or polling fallback works
- [ ] Mobile responsive layout verified

## Deployment Steps

### Local Network (LAN) Deployment

**Step 1: Build Production Bundle**
```bash
cd frontend
npm run build
```

**Step 2: Configure Environment**
```bash
# Edit .env.local with production backend URL
NEXT_PUBLIC_API_BASE_URL=http://192.168.1.100:5000
```

**Step 3: Start Production Server**
```bash
npm start
```

**Step 4: Find Your IP Address**
- Windows: `ipconfig` (look for IPv4 Address)
- macOS/Linux: `ifconfig` or `ip addr`

**Step 5: Access from Network**
- Open browser to `http://YOUR_IP:3000`
- Example: `http://192.168.1.50:3000`

**Step 6: Test End-to-End**
- [ ] Video stream displays
- [ ] Commands execute
- [ ] Status updates in real-time
- [ ] Mobile devices can connect

### Cloud Deployment (Vercel)

**Step 1: Install Vercel CLI**
```bash
npm install -g vercel
```

**Step 2: Login to Vercel**
```bash
vercel login
```

**Step 3: Deploy**
```bash
vercel
```

**Step 4: Configure Environment Variables**
1. Go to Vercel Dashboard → Your Project
2. Navigate to Settings → Environment Variables
3. Add: `NEXT_PUBLIC_API_BASE_URL` = `https://your-backend-url.com`
4. Redeploy if needed

**Step 5: Verify Deployment**
- [ ] Site loads at Vercel URL
- [ ] Backend connection works
- [ ] All features functional

**Note:** Backend must be publicly accessible for cloud deployment.

### Docker Deployment

**Step 1: Create Dockerfile**
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV PORT 3000
CMD ["node", "server.js"]
```

**Step 2: Update next.config.mjs**
Add to `next.config.mjs`:
```javascript
const nextConfig = {
  output: 'standalone',
};
```

**Step 3: Build Docker Image**
```bash
docker build -t lepetpal-frontend --build-arg NEXT_PUBLIC_API_BASE_URL=http://backend:5000 .
```

**Step 4: Run Container**
```bash
docker run -p 3000:3000 lepetpal-frontend
```

**Step 5: Docker Compose (Optional)**
Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  frontend:
    build:
      context: .
      args:
        NEXT_PUBLIC_API_BASE_URL: http://backend:5000
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - backend
```

## Post-Deployment Verification

### Functional Tests
- [ ] Health check: Open `http://YOUR_URL:3000`
- [ ] Video stream: Verify live feed displays
- [ ] Commands: Test each preset button
- [ ] Status updates: Verify real-time feedback
- [ ] Error handling: Test with backend offline
- [ ] Mobile: Test on phone/tablet

### Performance Tests
- [ ] Page load time < 3 seconds
- [ ] Video stream FPS ≥ 15
- [ ] Command response time < 500ms
- [ ] SSE latency < 100ms
- [ ] No memory leaks during extended use

### Security Checks
- [ ] HTTPS enabled (if public deployment)
- [ ] No sensitive data in client-side code
- [ ] CORS properly configured
- [ ] API token (if used) not exposed in logs
- [ ] No console errors in production

## Monitoring and Maintenance

### Health Monitoring
```bash
# Check if frontend is responding
curl http://YOUR_URL:3000

# Check backend connectivity from frontend
# Open browser console and check for errors
```

### Log Monitoring
- Check browser console for client-side errors
- Monitor backend logs for API errors
- Watch for SSE connection drops

### Common Issues

**Issue: Build fails**
```bash
# Clean and rebuild
npm run clean
rm -rf node_modules
npm install
npm run build
```

**Issue: Environment variables not updating**
```bash
# Rebuild after changing .env.local
npm run build
npm start
```

**Issue: Port already in use**
```bash
# Use different port
PORT=3001 npm start
```

**Issue: Out of memory during build**
```bash
# Increase Node.js memory
NODE_OPTIONS="--max-old-space-size=4096" npm run build
```

## Rollback Procedure

If deployment fails:

1. **Stop the new deployment**
```bash
# Kill the process
pkill -f "next start"
```

2. **Restore previous version**
```bash
# Checkout previous commit
git checkout <previous-commit-hash>
npm install
npm run build
npm start
```

3. **Verify rollback**
- Test critical functionality
- Check logs for errors
- Monitor for stability

## Scaling Considerations

### Horizontal Scaling
- Deploy multiple frontend instances behind load balancer
- Use sticky sessions for SSE connections
- Share backend URL across instances

### Performance Optimization
- Enable CDN for static assets
- Use Next.js Image optimization
- Implement service worker for offline support
- Add Redis for session management (if needed)

### High Availability
- Deploy to multiple regions
- Use health checks for automatic failover
- Monitor uptime with external service
- Set up alerts for downtime

## Support and Troubleshooting

### Debug Mode
Enable verbose logging:
```bash
# Development
DEBUG=* npm run dev

# Production
NODE_ENV=production DEBUG=* npm start
```

### Browser DevTools
- Network tab: Check API requests
- Console tab: Check for JavaScript errors
- Application tab: Verify localStorage
- Performance tab: Profile rendering

### Contact Information
- GitHub Issues: [Your repo URL]
- Documentation: See README.md
- Backend Issues: See backend/README.md
