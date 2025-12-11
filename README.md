# GraphScore Live Dashboard

Real-time Microsoft 365 Secure Score Dashboard with Grafana-style visualization that pulls live data from Microsoft Graph API on every request.

## Features

- **Live Data**: Every page load fetches fresh data from Microsoft Graph API
- **API Proof Banner**: Shows tenant ID, API timestamp, and fetch latency
- **Grafana-Style UI**: Dark theme, responsive, mobile-optimized
- **Auto-Refresh**: Page auto-refreshes every 60 seconds
- **Zero Cache**: No caching - always live tenant data

## Proof of Live Data

The dashboard displays real-time proof:

- Tenant ID (from API response)
- API Timestamp (when Microsoft computed the score)
- Fetch Time (milliseconds to retrieve data)
- Server Time (current UTC time)

## Quick Start

### Prerequisites

- Python 3.11+
- Azure AD application with `SecurityEvents.Read.All` permission
- Microsoft 365 tenant

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
# Edit .env with your Azure credentials

# Run
uvicorn main:app --reload --port 8080
```

### Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template)

**Required Environment Variables:**

| Variable | Description |
|----------|-------------|
| `AZURE_CLIENT_ID` | Azure AD application (client) ID |
| `AZURE_TENANT_ID` | Azure AD directory (tenant) ID |
| `AZURE_CLIENT_SECRET` | Azure AD client secret |

## API Endpoints

| Endpoint | Description | Response |
|----------|-------------|----------|
| `/` | Live dashboard | HTML |
| `/api/score` | Score data | JSON |
| `/health` | Health check | JSON |

## Security

- OAuth2 client credentials flow
- Secrets via environment variables only
- Read-only Microsoft Graph API access
- Non-root container execution
- No credential caching

## Architecture

```
Request -> FastAPI -> Azure AD (OAuth2) -> Microsoft Graph API -> Response
```

## License

MIT

---

Powered by Microsoft Graph API
