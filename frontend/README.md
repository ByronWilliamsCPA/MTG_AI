# MTG AI Frontend

React + TypeScript frontend for MTG AI.

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Vitest** - Testing framework
- **Axios** - HTTP client
- **ESLint + Prettier** - Code quality

## Quick Start

```bash
# Install dependencies
npm install

# Start development server (http://localhost:3000)
npm run dev

# Run tests
npm run test

# Build for production
npm run build
```

## Development

### Prerequisites

- Node.js 22+
- Backend API running on port 8000

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server with HMR |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run test` | Run tests in watch mode |
| `npm run test:run` | Run tests once |
| `npm run test:coverage` | Run tests with coverage |
| `npm run lint` | Lint code |
| `npm run lint:fix` | Fix lint issues |
| `npm run format` | Format code with Prettier |
| `npm run typecheck` | Run TypeScript type checking |
| `npm run generate-client` | Generate API client from OpenAPI |

### API Integration

The frontend connects to the backend API. In development, Vite proxies `/api` requests to `http://localhost:8000`.

#### Generate TypeScript API Client

Generate a type-safe API client from the FastAPI OpenAPI schema:

```bash
# Make sure backend is running first
cd .. && uv run uvicorn mtg_ai.main:app &

# Generate client
npm run generate-client
```

This creates typed API functions in `src/client/`.

### Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── assets/          # Images, fonts, etc.
│   ├── client/          # Auto-generated API client
│   ├── components/      # React components
│   ├── hooks/           # Custom React hooks
│   ├── test/            # Test setup and utilities
│   ├── App.tsx          # Root component
│   ├── App.css          # Root styles
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles
├── Dockerfile           # Production Docker image
├── nginx.conf           # Production nginx config
└── vite.config.ts       # Vite configuration
```

## Docker

### Development

```bash
# From project root
docker-compose up frontend
```

### Production

```bash
# Build production image
docker build -t mtg_ai-frontend .

# Run with custom API URL
docker run -p 80:80 \
  --build-arg VITE_API_URL=https://api.example.com \
  mtg_ai-frontend
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |
| `VITE_DEBUG` | Enable debug mode | `false` |

Create `.env.local` for local overrides (gitignored).

## Testing

```bash
# Run tests in watch mode
npm run test

# Run tests once with coverage
npm run test:coverage
```

Tests use Vitest with React Testing Library.
