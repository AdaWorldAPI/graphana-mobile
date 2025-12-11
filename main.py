"""
Ada Graphana Mobile - Grafana Dashboard for Mobile
FastAPI backend serving mobile-optimized Grafana dashboards
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI(title="Ada Graphana Mobile", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GRAFANA_URL = os.getenv("GRAFANA_URL", "")
GRAFANA_TOKEN = os.getenv("GRAFANA_TOKEN", "")

@app.get("/")
async def root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Ada Graphana Mobile</title>
        <style>
            body { font-family: system-ui; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
            h1 { color: #00d4ff; }
            .status { background: #16213e; padding: 15px; border-radius: 8px; margin: 10px 0; }
            .ok { border-left: 4px solid #00ff88; }
            a { color: #00d4ff; }
        </style>
    </head>
    <body>
        <h1>🌸 Ada Graphana Mobile</h1>
        <div class="status ok">
            <strong>Status:</strong> Online<br>
            <strong>Version:</strong> 1.0.0
        </div>
        <p>Endpoints:</p>
        <ul>
            <li><a href="/health">/health</a> - Health check</li>
            <li><a href="/api/dashboards">/api/dashboards</a> - List dashboards</li>
            <li><a href="/docs">/docs</a> - API Documentation</li>
        </ul>
    </body>
    </html>
    """)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ada-graphana-mobile"}

@app.get("/api/dashboards")
async def list_dashboards():
    if not GRAFANA_URL or not GRAFANA_TOKEN:
        return {"error": "Grafana not configured", "dashboards": []}
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GRAFANA_URL}/api/search?type=dash-db",
                headers={"Authorization": f"Bearer {GRAFANA_TOKEN}"},
                timeout=10.0
            )
            return {"dashboards": resp.json()}
    except Exception as e:
        return {"error": str(e), "dashboards": []}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
