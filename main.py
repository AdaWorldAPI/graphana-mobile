"""GraphScore Live Dashboard - Real-time Microsoft 365 Secure Score visualization."""

import os
import time
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(
    title="GraphScore Live Dashboard",
    description="Real-time Microsoft 365 Secure Score Dashboard",
    version="1.0.0",
)

# Configuration from environment variables
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID", "")
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID", "")
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET", "")

# Microsoft Graph API endpoints
TOKEN_URL = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token"
GRAPH_API_URL = "https://graph.microsoft.com/v1.0/security/secureScores"


async def get_access_token() -> str:
    """Acquire OAuth2 access token using client credentials flow."""
    if not all([AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET]):
        raise HTTPException(
            status_code=500,
            detail="Azure credentials not configured. Set AZURE_CLIENT_ID, AZURE_TENANT_ID, and AZURE_CLIENT_SECRET.",
        )

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": AZURE_CLIENT_ID,
                "client_secret": AZURE_CLIENT_SECRET,
                "scope": "https://graph.microsoft.com/.default",
            },
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to acquire access token: {response.text}",
            )

        return response.json().get("access_token", "")


async def fetch_secure_scores() -> dict[str, Any]:
    """Fetch secure scores from Microsoft Graph API."""
    start_time = time.time()
    token = await get_access_token()

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            GRAPH_API_URL,
            headers={"Authorization": f"Bearer {token}"},
            params={"$top": "1"},
        )

        fetch_time_ms = round((time.time() - start_time) * 1000, 2)

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch secure scores: {response.text}",
            )

        data = response.json()
        scores = data.get("value", [])

        if not scores:
            return {
                "current_score": 0,
                "max_score": 0,
                "percentage": 0,
                "tenant_id": AZURE_TENANT_ID[:8] + "..." if AZURE_TENANT_ID else "N/A",
                "api_timestamp": "N/A",
                "fetch_time_ms": fetch_time_ms,
                "server_time": datetime.now(timezone.utc).isoformat(),
                "controls": [],
            }

        latest = scores[0]
        current_score = latest.get("currentScore", 0)
        max_score = latest.get("maxScore", 1)
        percentage = round((current_score / max_score) * 100, 1) if max_score > 0 else 0

        return {
            "current_score": current_score,
            "max_score": max_score,
            "percentage": percentage,
            "tenant_id": latest.get("azureTenantId", "N/A")[:8] + "...",
            "api_timestamp": latest.get("createdDateTime", "N/A"),
            "fetch_time_ms": fetch_time_ms,
            "server_time": datetime.now(timezone.utc).isoformat(),
            "controls": latest.get("controlScores", [])[:10],
        }


def render_dashboard(data: dict[str, Any]) -> str:
    """Render Grafana-style HTML dashboard."""
    percentage = data["percentage"]
    color = "#73bf69" if percentage >= 70 else "#ff9830" if percentage >= 40 else "#f2495c"

    controls_html = ""
    for control in data.get("controls", []):
        name = control.get("controlName", "Unknown")
        score = control.get("score", 0)
        max_score = control.get("maxScore", 1)
        ctrl_pct = round((score / max_score) * 100) if max_score > 0 else 0
        ctrl_color = "#73bf69" if ctrl_pct >= 70 else "#ff9830" if ctrl_pct >= 40 else "#f2495c"
        controls_html += f"""
        <div class="control-item">
            <div class="control-name">{name}</div>
            <div class="control-bar">
                <div class="control-fill" style="width: {ctrl_pct}%; background: {ctrl_color};"></div>
            </div>
            <div class="control-score">{score}/{max_score}</div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="60">
    <title>GraphScore Live Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #111217;
            color: #d8d9da;
            min-height: 100vh;
            padding: 16px;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid #2c3235;
        }}
        .title {{ font-size: 20px; font-weight: 600; color: #fff; }}
        .live-badge {{
            background: #299c46;
            color: #fff;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        .proof-banner {{
            background: #1e1f24;
            border: 1px solid #2c3235;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 24px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
        }}
        .proof-item {{ text-align: center; }}
        .proof-label {{ font-size: 11px; color: #8e8e8e; text-transform: uppercase; letter-spacing: 0.5px; }}
        .proof-value {{ font-size: 14px; color: #73bf69; margin-top: 4px; font-family: monospace; }}
        .score-panel {{
            background: #1e1f24;
            border: 1px solid #2c3235;
            border-radius: 8px;
            padding: 32px;
            text-align: center;
            margin-bottom: 24px;
        }}
        .score-label {{ font-size: 14px; color: #8e8e8e; margin-bottom: 8px; }}
        .score-value {{
            font-size: 72px;
            font-weight: 700;
            color: {color};
            line-height: 1;
        }}
        .score-max {{ font-size: 24px; color: #8e8e8e; }}
        .progress-bar {{
            height: 8px;
            background: #2c3235;
            border-radius: 4px;
            margin-top: 24px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: {color};
            border-radius: 4px;
            transition: width 0.5s ease;
        }}
        .percentage {{ font-size: 18px; color: {color}; margin-top: 12px; }}
        .controls-panel {{
            background: #1e1f24;
            border: 1px solid #2c3235;
            border-radius: 8px;
            padding: 24px;
        }}
        .controls-title {{ font-size: 16px; font-weight: 600; margin-bottom: 16px; color: #fff; }}
        .control-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 0;
            border-bottom: 1px solid #2c3235;
        }}
        .control-item:last-child {{ border-bottom: none; }}
        .control-name {{ flex: 1; font-size: 13px; color: #d8d9da; }}
        .control-bar {{ width: 100px; height: 6px; background: #2c3235; border-radius: 3px; overflow: hidden; }}
        .control-fill {{ height: 100%; border-radius: 3px; }}
        .control-score {{ font-size: 12px; color: #8e8e8e; min-width: 50px; text-align: right; }}
        .footer {{
            text-align: center;
            margin-top: 24px;
            font-size: 12px;
            color: #5a5a5a;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">Microsoft 365 Secure Score</div>
            <div class="live-badge">LIVE</div>
        </div>

        <div class="proof-banner">
            <div class="proof-item">
                <div class="proof-label">Tenant ID</div>
                <div class="proof-value">{data['tenant_id']}</div>
            </div>
            <div class="proof-item">
                <div class="proof-label">API Timestamp</div>
                <div class="proof-value">{data['api_timestamp'][:19] if len(data['api_timestamp']) > 19 else data['api_timestamp']}</div>
            </div>
            <div class="proof-item">
                <div class="proof-label">Fetch Time</div>
                <div class="proof-value">{data['fetch_time_ms']}ms</div>
            </div>
            <div class="proof-item">
                <div class="proof-label">Server Time (UTC)</div>
                <div class="proof-value">{data['server_time'][:19]}</div>
            </div>
        </div>

        <div class="score-panel">
            <div class="score-label">Current Secure Score</div>
            <div class="score-value">{data['current_score']}<span class="score-max">/{data['max_score']}</span></div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {percentage}%;"></div>
            </div>
            <div class="percentage">{percentage}%</div>
        </div>

        <div class="controls-panel">
            <div class="controls-title">Top Control Scores</div>
            {controls_html if controls_html else '<div style="color: #8e8e8e; text-align: center; padding: 16px;">No control data available</div>'}
        </div>

        <div class="footer">
            Auto-refresh: 60 seconds | Powered by Microsoft Graph API
        </div>
    </div>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """Serve the live dashboard."""
    data = await fetch_secure_scores()
    return HTMLResponse(content=render_dashboard(data))


@app.get("/api/score")
async def api_score() -> JSONResponse:
    """Return secure score data as JSON."""
    data = await fetch_secure_scores()
    return JSONResponse(content=data)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
