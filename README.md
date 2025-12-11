# GraphScore Mobile

Mobile-optimized dashboard viewer for Grafana with a responsive, touch-friendly interface.

## Features

- Mobile-first responsive design
- Grafana dashboard integration
- FastAPI backend with async support
- Railway deployment ready
- Non-root container execution

## Quick Start

### Prerequisites

- Python 3.11+
- Grafana Cloud account or self-hosted Grafana instance
- API token with dashboard read permissions

### Local Development

```bash
# Clone and setup
git clone <repository-url>
cd graphana-mobile

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Grafana credentials

# Run
uvicorn main:app --reload --port 8080
```

### Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template)

**Required Environment Variables:**

| Variable | Description |
|----------|-------------|
| `GRAFANA_URL` | Grafana instance URL (e.g., `https://your-org.grafana.net`) |
| `GRAFANA_TOKEN` | Grafana API token with viewer permissions |
| `PORT` | Server port (default: 8080) |

## API Endpoints

| Endpoint | Description | Response |
|----------|-------------|----------|
| `/` | Mobile dashboard UI | HTML |
| `/api/dashboards` | List available dashboards | JSON |
| `/health` | Health check | JSON |
| `/docs` | OpenAPI documentation | HTML |

## Security

- Secrets via environment variables only
- Read-only Grafana API access
- Non-root container execution
- CORS middleware configured

## License

MIT

---

Powered by Grafana
