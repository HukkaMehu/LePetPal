# Configuration Guide

## Environment Variables

The application uses environment variables to configure connections to backend services. All environment variables must be prefixed with `VITE_` to be exposed to the client-side code.

### Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update the values in `.env` to match your environment:

### Available Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000` |
| `VITE_AI_SERVICE_URL` | AI Service base URL | `http://localhost:8001` |
| `VITE_WS_URL` | WebSocket connection URL | `ws://localhost:8000/ws` |
| `VITE_VIDEO_STREAM_URL` | Video streaming endpoint | `http://localhost:8000/video/mjpeg` |
| `VITE_DEBUG` | Enable debug logging | `false` |

### Usage in Code

Import the configuration module to access environment variables:

```typescript
import { config } from '@/config/env';

// Access configuration values
const apiUrl = config.apiBaseURL;
const wsUrl = config.wsURL;
```

### Validation

The configuration module automatically validates that all required environment variables are present when the application starts. If any required variables are missing, an error will be logged to the console.

## TypeScript Configuration

The project uses TypeScript with strict type checking enabled. Type definitions are organized in the `src/types/` directory:

- `src/types/index.ts` - Frontend data types
- `src/types/backend.ts` - Backend API response types

### Path Aliases

The TypeScript configuration includes a path alias for cleaner imports:

```typescript
// Instead of: import { config } from '../../../config/env';
// Use: import { config } from '@/config/env';
```

## Dependencies

### Production Dependencies

- **axios** - HTTP client for API requests
- **react** - UI framework
- **recharts** - Chart library for analytics
- **@radix-ui/** - UI component primitives
- **tailwindcss** - Utility-first CSS framework

### Development Dependencies

- **typescript** - TypeScript compiler
- **vite** - Build tool and dev server
- **@types/react** - React type definitions
- **@types/react-dom** - React DOM type definitions

## Project Structure

```
Pet Training Web App/
├── src/
│   ├── config/
│   │   └── env.ts           # Environment configuration
│   ├── types/
│   │   ├── index.ts         # Frontend types
│   │   └── backend.ts       # Backend API types
│   ├── components/          # React components
│   ├── lib/                 # Utility functions
│   └── styles/              # Global styles
├── .env                     # Environment variables (not in git)
├── .env.example             # Environment template
├── tsconfig.json            # TypeScript configuration
└── vite.config.ts           # Vite configuration
```

## Development

Start the development server:

```bash
npm run dev
```

Build for production:

```bash
npm run build
```

## Notes

- The `.env` file is excluded from version control via `.gitignore`
- Always use `.env.example` as a template for required variables
- Environment variables are validated on application startup
- Debug mode can be enabled by setting `VITE_DEBUG=true`
