# Environment Variables Reference

This document provides a comprehensive reference for all environment variables used across the Pet Training Web App system.

## Frontend Environment Variables

All frontend environment variables must be prefixed with `VITE_` to be accessible in the application.

### Required Variables

| Variable | Description | Development Default | Production Example |
|----------|-------------|-------------------|-------------------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000` | `https://api.your-domain.com` |
| `VITE_AI_SERVICE_URL` | AI service base URL | `http://localhost:8001` | `https://ai.your-domain.com` |
| `VITE_WS_URL` | WebSocket connection URL | `ws://localhost:8000/ws` | `wss://api.your-domain.com/ws` |
| `VITE_VIDEO_STREAM_URL` | Video streaming endpoint | `http://localhost:8000/video/mjpeg` | `https://api.your-domain.com/video/mjpeg` |

### Optional Variables

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `VITE_DEBUG` | Enable debug logging | `false` | `true`, `false` |

### Frontend Configuration Files

- **Development**: `Pet Training Web App/.env`
- **Production Template**: `Pet Training Web App/.env.production.example`
- **Example**: `Pet Training Web App/.env.example`

## Backend Environment Variables

### API Settings

| Variable | Description | Default | Production Notes |
|----------|-------------|---------|-----------------|
| `API_V1_STR` | API version prefix | `/api` | Usually unchanged |
| `PROJECT_NAME` | Project name | `Dog Monitor API` | Can be customized |

### CORS Configuration

| Variable | Description | Default | Production Example |
|----------|-------------|---------|-------------------|
| `CORS_ORIGINS` | Allowed frontend origins (JSON array) | `["http://localhost:3000"]` | `["http://localhost:3000","https://your-frontend-domain.com"]` |

**Important:** Must be a valid JSON array string.

### Database Configuration

| Variable | Description | Default | Production Notes |
|----------|-------------|---------|-----------------|
| `POSTGRES_USER` | PostgreSQL username | `dogmonitor` | Use secure username |
| `POSTGRES_PASSWORD` | PostgreSQL password | `dogmonitor` | **Must change for production** |
| `POSTGRES_HOST` | PostgreSQL host | `localhost` | Production database host |
| `POSTGRES_PORT` | PostgreSQL port | `5432` | Usually unchanged |
| `POSTGRES_DB` | Database name | `dogmonitor` | Can be customized |

### Redis Configuration

| Variable | Description | Default | Production Notes |
|----------|-------------|---------|-----------------|
| `REDIS_HOST` | Redis host | `localhost` | Production Redis host |
| `REDIS_PORT` | Redis port | `6379` | Usually unchanged |
| `REDIS_DB` | Redis database number | `0` | Usually unchanged |

### S3/MinIO Configuration

| Variable | Description | Default | Production Notes |
|----------|-------------|---------|-----------------|
| `S3_ENDPOINT_URL` | S3/MinIO endpoint | `http://localhost:9000` | AWS: `https://s3.amazonaws.com` |
| `S3_ACCESS_KEY` | S3 access key | `minioadmin` | **Must change for production** |
| `S3_SECRET_KEY` | S3 secret key | `minioadmin` | **Must change for production** |
| `S3_BUCKET_NAME` | S3 bucket name | `dog-monitor` | Production bucket name |
| `S3_REGION` | S3 region | `us-east-1` | AWS region |

### AI Service Configuration

| Variable | Description | Default | Production Example |
|----------|-------------|---------|-------------------|
| `AI_SERVICE_URL` | AI service base URL | `http://localhost:8001` | `https://ai.your-domain.com` |

### Backend Configuration Files

- **Development**: `backend/.env`
- **Example**: `backend/.env.example`

## AI Service Environment Variables

### API Configuration

| Variable | Description | Default | Production Notes |
|----------|-------------|---------|-----------------|
| `OPENAI_API_KEY` | OpenAI API key | (required) | **Must be set** |
| `MODEL_NAME` | OpenAI model to use | `gpt-4` | Can use `gpt-3.5-turbo` for cost savings |

### AI Service Configuration Files

- **Development**: `ai_service/.env`
- **Example**: `ai_service/.env.example`

## Environment-Specific Configurations

### Development Environment

```bash
# Frontend (.env)
VITE_API_BASE_URL=http://localhost:8000
VITE_AI_SERVICE_URL=http://localhost:8001
VITE_WS_URL=ws://localhost:8000/ws
VITE_VIDEO_STREAM_URL=http://localhost:8000/video/mjpeg
VITE_DEBUG=true

# Backend (.env)
CORS_ORIGINS=["http://localhost:3000"]
POSTGRES_HOST=localhost
REDIS_HOST=localhost
S3_ENDPOINT_URL=http://localhost:9000
AI_SERVICE_URL=http://localhost:8001
```

### Production Environment

```bash
# Frontend (.env.production)
VITE_API_BASE_URL=https://api.your-domain.com
VITE_AI_SERVICE_URL=https://ai.your-domain.com
VITE_WS_URL=wss://api.your-domain.com/ws
VITE_VIDEO_STREAM_URL=https://api.your-domain.com/video/mjpeg
VITE_DEBUG=false

# Backend (.env)
CORS_ORIGINS=["https://your-frontend-domain.com","https://www.your-frontend-domain.com"]
POSTGRES_HOST=prod-db-host.com
POSTGRES_PASSWORD=secure_random_password
REDIS_HOST=prod-redis-host.com
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY=prod_access_key
S3_SECRET_KEY=prod_secret_key
AI_SERVICE_URL=https://ai.your-domain.com
```

## Security Best Practices

### DO NOT

- ❌ Commit `.env` files to version control
- ❌ Use default passwords in production
- ❌ Expose API keys in frontend code
- ❌ Use `CORS_ORIGINS=["*"]` in production
- ❌ Share production credentials in documentation

### DO

- ✅ Use `.env.example` files as templates (without sensitive values)
- ✅ Store production secrets in secure secret management systems
- ✅ Use strong, randomly generated passwords
- ✅ Rotate credentials regularly
- ✅ Restrict CORS to specific domains
- ✅ Use environment-specific configurations

## Setting Environment Variables

### Local Development

1. Copy example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values

3. Restart application to load new values

### Production Hosting Platforms

#### Vercel

1. Go to Project Settings → Environment Variables
2. Add each variable with its value
3. Select environment (Production/Preview/Development)
4. Redeploy to apply changes

#### Netlify

1. Go to Site Settings → Build & Deploy → Environment
2. Add each variable with its value
3. Redeploy to apply changes

#### Docker

Use environment variables in `docker-compose.yml`:

```yaml
services:
  backend:
    environment:
      - POSTGRES_HOST=db
      - REDIS_HOST=redis
      - CORS_ORIGINS=["https://your-domain.com"]
```

Or use `.env` file:

```yaml
services:
  backend:
    env_file:
      - .env
```

#### Systemd Service

Use `EnvironmentFile` in service file:

```ini
[Service]
EnvironmentFile=/path/to/.env
```

## Troubleshooting

### Frontend Variables Not Working

**Problem:** Environment variables are undefined in the application

**Solutions:**
1. Ensure variables are prefixed with `VITE_`
2. Restart dev server after changing `.env`
3. Rebuild application: `npm run build`
4. Check `import.meta.env.VITE_VARIABLE_NAME` syntax

### Backend Variables Not Loading

**Problem:** Backend uses default values instead of `.env` values

**Solutions:**
1. Ensure `.env` file is in the correct directory (`backend/`)
2. Check file permissions (must be readable)
3. Verify variable names match exactly (case-sensitive)
4. Restart backend application

### CORS Errors Despite Configuration

**Problem:** CORS errors persist after adding domain to `CORS_ORIGINS`

**Solutions:**
1. Verify JSON array format: `["domain1","domain2"]`
2. Include protocol: `https://` not just `domain.com`
3. Check for trailing slashes (should not have them)
4. Restart backend after changing CORS settings

### Database Connection Fails

**Problem:** Backend cannot connect to database

**Solutions:**
1. Verify database is running
2. Check `POSTGRES_HOST`, `POSTGRES_PORT` are correct
3. Verify credentials are correct
4. Check network connectivity
5. Verify database exists: `POSTGRES_DB`

## Validation

### Frontend Variables

Check loaded variables in browser console:

```javascript
console.log('API URL:', import.meta.env.VITE_API_BASE_URL);
console.log('WS URL:', import.meta.env.VITE_WS_URL);
```

### Backend Variables

Check loaded settings in Python:

```python
from app.core.config import settings
print(f"CORS Origins: {settings.CORS_ORIGINS}")
print(f"Database URL: {settings.DATABASE_URL}")
```

## References

- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)
