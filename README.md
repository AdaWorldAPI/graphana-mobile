# GraphScore Mobile

Mobile-optimized dashboard viewer for Grafana.

## Features

- 📱 Mobile-first responsive design
- 📊 Grafana dashboard integration
- ⚡ FastAPI backend
- 🚀 Railway deployment ready

## Deployment

Deploys automatically via Railway on push to main.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Mobile dashboard UI |
| `/health` | Health check |
| `/api/dashboards` | List available dashboards |
| `/docs` | OpenAPI documentation |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GRAFANA_URL` | Grafana instance URL |
| `GRAFANA_TOKEN` | Grafana API token |
| `PORT` | Server port (default: 8080) |
