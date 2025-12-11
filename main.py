"""GraphScore Mobile - Mobile Dashboard Viewer for Grafana."""

import os
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(
    title="GraphScore Mobile",
    description="Mobile-optimized dashboard viewer for Grafana",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GRAFANA_URL = os.getenv("GRAFANA_URL", "https://graphscore.grafana.net")
GRAFANA_TOKEN = os.getenv("GRAFANA_TOKEN", "")


@app.get("/", response_class=HTMLResponse)
async def root() -> HTMLResponse:
    """Serve the mobile dashboard UI."""
    return HTMLResponse("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    <title>GraphScore Mobile</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }
        .header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 24px;
        }
        .logo { font-size: 32px; }
        h1 { font-size: 24px; font-weight: 600; color: #fff; }
        .subtitle { color: #888; font-size: 14px; margin-top: 4px; }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 16px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .status-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .status-row:last-child { border-bottom: none; }
        .status-label { color: #888; font-size: 14px; }
        .status-value { font-weight: 600; }
        .status-ok { color: #00ff88; }
        .status-warn { color: #ffaa00; }
        .dashboard-list { margin-top: 20px; }
        .dashboard-item {
            background: rgba(0,212,255,0.1);
            border: 1px solid rgba(0,212,255,0.3);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .dashboard-item:hover {
            background: rgba(0,212,255,0.2);
            transform: translateY(-2px);
        }
        .dashboard-title { font-weight: 600; color: #00d4ff; }
        .dashboard-meta { font-size: 12px; color: #888; margin-top: 4px; }
        .loading { text-align: center; padding: 40px; color: #888; }
        .error { color: #ff6b6b; background: rgba(255,107,107,0.1); padding: 16px; border-radius: 12px; }
        .btn {
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            color: #fff;
            border: none;
            padding: 14px 24px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            width: 100%;
            cursor: pointer;
            margin-top: 16px;
        }
        .btn:active { transform: scale(0.98); }
    </style>
</head>
<body>
    <div class="header">
        <span class="logo">📊</span>
        <div>
            <h1>GraphScore Mobile</h1>
            <div class="subtitle">Dashboard Viewer</div>
        </div>
    </div>

    <div class="card">
        <div class="status-row">
            <span class="status-label">API Status</span>
            <span class="status-value status-ok">● Online</span>
        </div>
        <div class="status-row">
            <span class="status-label">Grafana</span>
            <span class="status-value" id="grafana-status">Checking...</span>
        </div>
        <div class="status-row">
            <span class="status-label">Dashboards</span>
            <span class="status-value" id="dashboard-count">-</span>
        </div>
    </div>

    <div class="card">
        <h3 style="margin-bottom: 16px;">Dashboards</h3>
        <div id="dashboard-list" class="loading">Loading dashboards...</div>
    </div>

    <button class="btn" onclick="loadDashboards()">Refresh</button>

    <script>
        async function loadDashboards() {
            const listEl = document.getElementById('dashboard-list');
            const statusEl = document.getElementById('grafana-status');
            const countEl = document.getElementById('dashboard-count');

            listEl.innerHTML = '<div class="loading">Loading...</div>';

            try {
                const resp = await fetch('/api/dashboards');
                const data = await resp.json();

                if (data.error) {
                    statusEl.innerHTML = '<span class="status-warn">● ' + data.error + '</span>';
                    listEl.innerHTML = '<div class="error">' + data.error + '</div>';
                    countEl.textContent = '0';
                    return;
                }

                statusEl.innerHTML = '<span class="status-ok">● Connected</span>';
                countEl.textContent = data.dashboards.length;

                if (data.dashboards.length === 0) {
                    listEl.innerHTML = '<div style="color:#888;text-align:center;padding:20px;">No dashboards yet. Create one in Grafana!</div>';
                    return;
                }

                listEl.innerHTML = data.dashboards.map(d => `
                    <div class="dashboard-item" onclick="window.open('${data.grafana_url}/d/${d.uid}', '_blank')">
                        <div class="dashboard-title">${d.title}</div>
                        <div class="dashboard-meta">${d.type || 'dashboard'} • ${d.folderTitle || 'General'}</div>
                    </div>
                `).join('');

            } catch (e) {
                statusEl.innerHTML = '<span class="status-warn">● Error</span>';
                listEl.innerHTML = '<div class="error">Failed to load: ' + e.message + '</div>';
            }
        }

        loadDashboards();
    </script>
</body>
</html>""")


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "graphscore-mobile",
        "grafana": GRAFANA_URL,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/dashboards")
async def list_dashboards() -> JSONResponse:
    """List available Grafana dashboards."""
    if not GRAFANA_TOKEN:
        return JSONResponse(
            content={"error": "Token not configured", "dashboards": [], "grafana_url": GRAFANA_URL}
        )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{GRAFANA_URL}/api/search?type=dash-db",
                headers={"Authorization": f"Bearer {GRAFANA_TOKEN}"},
            )
            if resp.status_code == 200:
                return JSONResponse(
                    content={"dashboards": resp.json(), "grafana_url": GRAFANA_URL}
                )
            return JSONResponse(
                content={
                    "error": f"Grafana returned {resp.status_code}",
                    "dashboards": [],
                    "grafana_url": GRAFANA_URL,
                }
            )
    except httpx.TimeoutException:
        return JSONResponse(
            content={"error": "Request timeout", "dashboards": [], "grafana_url": GRAFANA_URL}
        )
    except httpx.RequestError as e:
        return JSONResponse(
            content={"error": str(e), "dashboards": [], "grafana_url": GRAFANA_URL}
        )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
