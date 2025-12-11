# 📊 GraphScore Live Dashboard

**Real-time Microsoft 365 Secure Score Dashboard** - Grafana-style visualization that pulls live data from Microsoft Graph API on every request.

## 🔥 Features

- **Live Data**: Every page load fetches fresh data from `graph.microsoft.com/v1.0/security/secureScores`
- **API Proof Banner**: Shows tenant ID, API timestamp, and fetch latency to prove real-time data
- **Grafana-Style UI**: Dark theme, responsive, mobile-optimized
- **Auto-Refresh**: Page auto-refreshes every 60 seconds
- **Zero Cache**: No caching - always live tenant data

## 🔐 Proof of Live Data

The dashboard prominently displays:
- Tenant ID (from API response)
- API Timestamp (when Microsoft computed the score)
- Fetch Time (ms to retrieve data)
- Current Server Time (UTC)

This proves the data is pulled live, not from any cache or static file.

## 🚀 Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template)

### Environment Variables Required:
```
AZURE_CLIENT_ID=your-app-client-id
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_SECRET=your-client-secret
```

## 📱 Endpoints

- `/` - Live dashboard (HTML)
- `/api/score` - JSON API with live score data
- `/health` - Health check endpoint

## 🛡️ Security

- OAuth2 client credentials flow
- No secrets in code (environment variables)
- Read-only Graph API access

---
Built for DATAGROUP SE | Powered by Microsoft Graph API
