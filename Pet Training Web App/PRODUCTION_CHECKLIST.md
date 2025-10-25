# Production Deployment Checklist

Use this checklist to ensure all steps are completed before deploying to production.

## Pre-Deployment

### Frontend Configuration

- [ ] Create `.env.production` file with production values
- [ ] Update `VITE_API_BASE_URL` to production backend URL
- [ ] Update `VITE_AI_SERVICE_URL` to production AI service URL
- [ ] Update `VITE_WS_URL` to production WebSocket URL (use `wss://`)
- [ ] Update `VITE_VIDEO_STREAM_URL` to production video stream URL
- [ ] Set `VITE_DEBUG=false` for production
- [ ] Remove any development-only code or console.logs
- [ ] Test build locally: `npm run build`
- [ ] Test production build locally: `npm run preview`

### Backend Configuration

- [ ] Update `.env` file with production database credentials
- [ ] Add production frontend domain to `CORS_ORIGINS`
- [ ] Configure production Redis instance
- [ ] Configure production S3/MinIO credentials
- [ ] Update AI service URL to production
- [ ] Enable HTTPS/SSL certificates
- [ ] Run database migrations: `alembic upgrade head`
- [ ] Test backend health endpoint
- [ ] Verify all API endpoints are accessible

### Security

- [ ] HTTPS enabled for all services
- [ ] Secure WebSocket (WSS) configured
- [ ] CORS restricted to production domains only
- [ ] Database credentials are secure (not defaults)
- [ ] S3/MinIO access keys are secure
- [ ] Redis password configured (if exposed)
- [ ] Environment variables not in version control
- [ ] API rate limiting configured (optional)
- [ ] Security headers configured (CSP, HSTS, etc.)

### Infrastructure

- [ ] Domain name configured and DNS propagated
- [ ] SSL/TLS certificates installed and valid
- [ ] Load balancer configured (if applicable)
- [ ] CDN configured for static assets (optional)
- [ ] Firewall rules configured
- [ ] Backup strategy in place
- [ ] Monitoring and alerting configured

## Deployment

### Frontend Deployment

- [ ] Build production bundle: `npm run build`
- [ ] Verify build output in `build/` directory
- [ ] Deploy to hosting platform (Vercel/Netlify/S3/etc.)
- [ ] Configure environment variables in hosting platform
- [ ] Verify deployment URL is accessible
- [ ] Check that all assets load correctly

### Backend Deployment

- [ ] Deploy backend application
- [ ] Start all required services (database, Redis, AI service)
- [ ] Verify backend health endpoint responds
- [ ] Check backend logs for errors
- [ ] Verify WebSocket endpoint is accessible

## Post-Deployment Testing

### Basic Functionality

- [ ] Frontend loads without errors
- [ ] No console errors in browser DevTools
- [ ] All assets load (no 404 errors)
- [ ] API calls succeed (check Network tab)
- [ ] WebSocket connects successfully
- [ ] Video stream displays correctly

### Feature Testing

- [ ] **Live Page**
  - [ ] Video stream displays
  - [ ] Action buttons work (Pet, Treat, Fetch)
  - [ ] Snapshot functionality works
  - [ ] Recording functionality works
  - [ ] Video metrics display (FPS, latency)

- [ ] **Timeline/Events**
  - [ ] Events load and display
  - [ ] Real-time events appear
  - [ ] Event filtering works
  - [ ] Pagination/infinite scroll works

- [ ] **Analytics**
  - [ ] All charts display data
  - [ ] Date range selector works
  - [ ] Metrics are accurate
  - [ ] Streaks and badges display

- [ ] **Routines**
  - [ ] Routines list loads
  - [ ] Create routine works
  - [ ] Edit routine works
  - [ ] Delete routine works
  - [ ] Trigger routine works
  - [ ] Routine notifications appear

- [ ] **Gallery**
  - [ ] Clips and snapshots load
  - [ ] Media filtering works
  - [ ] Pagination works
  - [ ] Media preview/modal works
  - [ ] Download functionality works

- [ ] **Coach Chat**
  - [ ] Chat interface loads
  - [ ] Messages send successfully
  - [ ] AI responses appear
  - [ ] Streaming responses work
  - [ ] Error handling works when AI unavailable

- [ ] **Settings**
  - [ ] Model selection works
  - [ ] Device status displays
  - [ ] Settings persist correctly

### Error Handling

- [ ] Connection lost banner appears when backend offline
- [ ] Error messages display appropriately
- [ ] Loading states show during async operations
- [ ] Retry logic works for failed requests
- [ ] WebSocket reconnects after disconnect

### Performance

- [ ] Page load time is acceptable (< 3 seconds)
- [ ] Time to interactive is acceptable
- [ ] No memory leaks (check DevTools Memory tab)
- [ ] Video streaming is smooth
- [ ] Real-time updates are responsive

### Cross-Browser Testing

- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if applicable)
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

### Responsive Design

- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

## Monitoring Setup

- [ ] Error tracking configured (Sentry, Rollbar, etc.)
- [ ] Performance monitoring configured
- [ ] Uptime monitoring configured
- [ ] Log aggregation configured
- [ ] Alerts configured for critical errors
- [ ] Dashboard for key metrics

## Documentation

- [ ] Deployment documentation updated
- [ ] Environment variables documented
- [ ] Backend configuration documented
- [ ] Troubleshooting guide available
- [ ] Rollback procedure documented

## Backup and Recovery

- [ ] Database backup configured
- [ ] Media files backup configured
- [ ] Backup restoration tested
- [ ] Disaster recovery plan documented

## Communication

- [ ] Stakeholders notified of deployment
- [ ] Maintenance window communicated (if applicable)
- [ ] Support team briefed on new features
- [ ] Documentation shared with team

## Post-Deployment Monitoring (First 24 Hours)

- [ ] Monitor error rates
- [ ] Monitor API response times
- [ ] Monitor WebSocket connection stability
- [ ] Monitor video streaming performance
- [ ] Check for any user-reported issues
- [ ] Review logs for unexpected errors
- [ ] Monitor resource usage (CPU, memory, bandwidth)

## Rollback Plan

If critical issues are discovered:

- [ ] Rollback procedure documented and tested
- [ ] Previous version available for quick restore
- [ ] Database rollback plan ready (if schema changed)
- [ ] Team knows how to execute rollback

## Sign-Off

- [ ] Technical lead approval
- [ ] QA testing completed
- [ ] Product owner approval
- [ ] Deployment completed successfully
- [ ] Post-deployment verification completed

---

**Deployment Date:** _______________

**Deployed By:** _______________

**Version:** _______________

**Notes:**
