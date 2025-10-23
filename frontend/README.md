# CodeOps Agent Dashboard

A modern React + TailwindCSS dashboard for the CodeOps Agent backend system.

## Features

- **System Health Monitoring** - Real-time backend health status
- **Metrics Overview** - Success rates, latency, and token usage
- **Run History Table** - Recent agent runs with detailed information
- **Context Lookup Panel** - FAISS-powered semantic search for commit contexts

## Tech Stack

- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **Axios** - HTTP client for API communication

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend server running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The dashboard will be available at `http://localhost:5173`

### Building for Production

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## API Integration

The dashboard connects to the following backend endpoints:

- `GET /health` - System health check
- `GET /metrics` - System metrics
- `GET /agent/runs` - Recent agent runs
- `GET /context?commit_sha=...` - Context retrieval
- `GET /context/stats` - Context store statistics
- `GET /context/query?query_text=...` - Semantic search

## Components

### HealthCard
Displays real-time system health with auto-refresh every 30 seconds.

### MetricsCard  
Shows system metrics including total runs, success rate, and average latency.

### RunsTable
Table view of recent agent runs with verdict, latency, and plan information.

### ContextPanel
Interactive panel for context lookup and semantic search using FAISS.

## Styling

The dashboard uses a dark theme with:
- Gray-900 background
- Gray-800 cards with rounded corners
- Green/red status indicators
- Responsive grid layout
- Modern typography and spacing

## Development

The project uses Vite for fast development with:
- Hot Module Replacement (HMR)
- TypeScript support (if needed)
- Optimized builds
- Modern ES modules