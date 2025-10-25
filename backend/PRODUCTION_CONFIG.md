# Backend Production Configuration Guide

This guide explains how to configure the backend for production deployment with the Pet Training Web App frontend.

## Environment Variables

Update your backend `.env` file with production values:

```env
# API Settings
API_V1_STR=/api
PROJECT_NAME=Dog Monitor API

# CORS - Add your production frontend domain
CORS_ORIGINS=["http://localhost:3000","https://your-frontend-domain.com"]

# Database - Use production PostgreSQL credentials
POSTGRES_USER=your_prod_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=your-db-host.com
POSTGRES_PORT=5432
POSTGRES_DB=dogmonitor_prod

# Redis - Use production Redis instance
REDIS_HOST=your-redis-host.com
REDIS_PORT=6379
REDIS_DB=0

# S3/MinIO - Use production object storage
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
S3_BUCKET_NAME=dog-monitor-prod
S3_REGION=us-east-1

# AI Service - Point to production AI service
AI_SERVICE_URL=https://ai.your-domain.com
```

## CORS Configuration

### Adding Production Frontend Domain

The backend uses the `CORS_ORIGINS` setting to control which domains can access the API.

**Option 1: Environment Variable (Recommended)**

Set the `CORS_ORIGINS` environment variable as a JSON array:

```bash
export CORS_ORIGINS='["http://localhost:3000","https://your-frontend-domain.com"]'
```

**Option 2: Update config.py**

Edit `backend/app/core/config.py`:

```python
class Settings(BaseSettings):
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",      # Development
        "http://localhost:3001",      # Development alternate
        "https://your-frontend-domain.com",  # Production
        "https://www.your-frontend-domain.com",  # Production with www
    ]
```

### Wildcard CORS (Not Recommended for Production)

If you need to allow all origins (not recommended for security):

```python
CORS_ORIGINS: List[str] = ["*"]
```

## WebSocket Configuration

WebSocket connections automatically inherit CORS settings. Ensure:

1. Production frontend uses `wss://` (secure WebSocket) instead of `ws://`
2. Backend is served over HTTPS
3. WebSocket endpoint is accessible: `wss://api.your-domain.com/ws`

### Nginx Configuration for WebSocket

If using Nginx as a reverse proxy:

```nginx
server {
    listen 443 ssl;
    server_name api.your-domain.com;

    # SSL configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # WebSocket upgrade
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # Regular API endpoints
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Video Streaming Configuration

Ensure video streaming endpoints are accessible:

### MJPEG Stream

- Endpoint: `/video/mjpeg`
- Frontend config: `VITE_VIDEO_STREAM_URL=https://api.your-domain.com/video/mjpeg`

### WebRTC (if implemented)

- Signaling endpoint: `/video/webrtc`
- Ensure STUN/TURN servers are configured for NAT traversal

## Database Migration

Before deploying to production:

1. **Backup existing data** (if upgrading)
   ```bash
   pg_dump -U postgres dogmonitor > backup.sql
   ```

2. **Run migrations**
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Verify migrations**
   ```bash
   alembic current
   ```

## Security Checklist

- [ ] HTTPS enabled for all endpoints
- [ ] Secure WebSocket (WSS) configured
- [ ] CORS origins restricted to production domains only
- [ ] Database credentials are secure and not default values
- [ ] S3/MinIO access keys are secure
- [ ] Redis is password-protected (if exposed)
- [ ] Environment variables are not committed to version control
- [ ] API rate limiting configured (if needed)
- [ ] SQL injection protection (SQLAlchemy ORM handles this)
- [ ] Input validation on all endpoints

## Testing Production Configuration

### 1. Test API Connectivity

```bash
curl https://api.your-domain.com/health
# Expected: {"status": "healthy"}
```

### 2. Test CORS

```bash
curl -H "Origin: https://your-frontend-domain.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     https://api.your-domain.com/api/events
# Should return CORS headers
```

### 3. Test WebSocket

Use a WebSocket client or browser console:

```javascript
const ws = new WebSocket('wss://api.your-domain.com/ws');
ws.onopen = () => console.log('Connected');
ws.onmessage = (event) => console.log('Message:', event.data);
```

### 4. Test Video Stream

Open in browser:
```
https://api.your-domain.com/video/mjpeg
```

## Deployment Options

### Option 1: Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - CORS_ORIGINS=["https://your-frontend-domain.com"]
      - POSTGRES_HOST=db
      - REDIS_HOST=redis
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=dogmonitor
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=dogmonitor
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Option 2: Systemd Service

Create `/etc/systemd/system/dogmonitor-api.service`:

```ini
[Unit]
Description=Dog Monitor API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/dogmonitor/backend
Environment="PATH=/opt/dogmonitor/backend/venv/bin"
EnvironmentFile=/opt/dogmonitor/backend/.env
ExecStart=/opt/dogmonitor/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable dogmonitor-api
sudo systemctl start dogmonitor-api
```

## Monitoring

### Health Check Endpoint

Monitor the `/health` endpoint:

```bash
curl https://api.your-domain.com/health
```

### Logs

**Docker:**
```bash
docker logs -f backend_container
```

**Systemd:**
```bash
journalctl -u dogmonitor-api -f
```

### Database Connection Pool

Monitor database connections in PostgreSQL:

```sql
SELECT count(*) FROM pg_stat_activity WHERE datname = 'dogmonitor';
```

## Troubleshooting

### CORS Errors

**Symptom:** Browser console shows CORS errors

**Solutions:**
1. Verify frontend domain is in `CORS_ORIGINS`
2. Check that backend is returning CORS headers
3. Ensure preflight OPTIONS requests are handled
4. Restart backend after changing CORS settings

### WebSocket Connection Fails

**Symptom:** WebSocket fails to connect or disconnects immediately

**Solutions:**
1. Verify WSS (not WS) is used in production
2. Check Nginx/proxy WebSocket configuration
3. Verify firewall allows WebSocket connections
4. Check backend logs for connection errors

### Video Stream Not Loading

**Symptom:** Video player shows error or blank screen

**Solutions:**
1. Verify video endpoint is accessible
2. Check camera/video source is connected
3. Verify CORS allows video streaming
4. Check backend logs for video errors

### Database Connection Errors

**Symptom:** API returns 500 errors, logs show database connection issues

**Solutions:**
1. Verify database credentials are correct
2. Check database is running and accessible
3. Verify network connectivity to database
4. Check database connection pool settings

## Performance Optimization

### Database

- Enable connection pooling (SQLAlchemy default)
- Add indexes on frequently queried columns
- Use database query optimization

### Redis

- Use Redis for caching frequently accessed data
- Configure appropriate memory limits
- Enable persistence if needed

### API

- Enable gzip compression
- Implement rate limiting
- Use async endpoints for I/O operations
- Cache static responses

## Backup Strategy

### Database Backups

Automated daily backups:

```bash
#!/bin/bash
# /opt/scripts/backup-db.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U dogmonitor dogmonitor > /backups/dogmonitor_$DATE.sql
# Keep only last 7 days
find /backups -name "dogmonitor_*.sql" -mtime +7 -delete
```

Add to crontab:
```bash
0 2 * * * /opt/scripts/backup-db.sh
```

### Media Backups

S3 versioning and lifecycle policies:
- Enable versioning on S3 bucket
- Configure lifecycle rules for old versions
- Set up cross-region replication (optional)

## Rollback Procedure

If issues occur after deployment:

1. **Revert code:**
   ```bash
   git checkout previous-stable-tag
   docker-compose up -d --build
   ```

2. **Revert database:**
   ```bash
   alembic downgrade -1
   ```

3. **Restore from backup:**
   ```bash
   psql -U dogmonitor dogmonitor < /backups/dogmonitor_YYYYMMDD.sql
   ```

## Support

For production issues:
- Check backend logs first
- Verify all services are running (database, Redis, AI service)
- Test each component independently
- Review recent changes/deployments
