import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.agent.copilot import copilot_agent
from backend.simulator.telemetry import telemetry_simulator
from backend.simulator.exporter import generate_prometheus_metrics_text
from backend.mcp.client import grafana_mcp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("studio-ops-copilot")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("==================================================")
    logger.info("🎬 Starting Studio Ops Copilot (Agentic Cinema)")
    logger.info(f"Gemini Model: {settings.GEMINI_MODEL}")
    logger.info(f"Gemini API Key: {'[Configured]' if settings.has_gemini_credentials else '[Demo Mode]'}")
    logger.info(f"Grafana URL: {settings.GRAFANA_URL or '[Synthetic MCP Mode]'}")
    logger.info("==================================================")
    yield
    logger.info("Shutting down Studio Ops Copilot.")

app = FastAPI(
    title="Studio Ops Copilot",
    description="Conversational AI Infrastructure Intelligence for Film & TV Production Crews",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = None

class ScenarioRequest(BaseModel):
    scenario: str

@app.get("/health")
async def health_check():
    """Health check for Cloud Run and orchestration probes."""
    return {
        "status": "healthy",
        "service": "studio-ops-copilot",
        "has_gemini": settings.has_gemini_credentials,
        "has_grafana": settings.has_grafana_credentials,
        "active_scenario": telemetry_simulator.scenario
    }

@app.post("/api/chat")
async def chat_endpoint(payload: ChatRequest):
    """
    Main conversational agent endpoint.
    Takes crew queries, calls Grafana MCP tools, and synthesizes incident briefs via Gemini.
    """
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Query message cannot be empty.")
    
    response = await copilot_agent.chat(payload.message, payload.history)
    return response

@app.get("/api/telemetry/status")
async def get_telemetry_status():
    """Returns current real-time studio telemetry and active incident state."""
    return telemetry_simulator.get_snapshot()

@app.post("/api/telemetry/scenario")
async def set_telemetry_scenario(payload: ScenarioRequest):
    """
    Allows dynamically switching active incident scenario to test different production states:
    - 'render_farm_incident': Overnight render queue backlog & CUDA OOM
    - 'livestream_incident': Premiere stream bitrate drop & dropped frames
    - 'encoding_incident': Transcode worker CPU exhaustion
    - 'all_nominal': Healthy baseline across all pipelines
    """
    telemetry_simulator.set_scenario(payload.scenario)
    return {
        "status": "updated",
        "new_scenario": telemetry_simulator.scenario,
        "snapshot": telemetry_simulator.get_snapshot()
    }

@app.get("/api/alerts")
async def get_alerts():
    """Lists current firing alerts from Grafana Alertmanager."""
    return await grafana_mcp.list_alerts()

@app.get("/api/dashboards")
async def get_dashboards():
    """Lists studio dashboards discovered in Grafana."""
    return await grafana_mcp.search_dashboards()

@app.get("/metrics")
async def get_metrics():
    """
    Standard Prometheus exposition endpoint.
    Allows Prometheus, Grafana Alloy, or Grafana Agent to scrape live studio metrics.
    """
    text_data = generate_prometheus_metrics_text()
    return PlainTextResponse(text_data, media_type="text/plain; version=0.0.4")

# Mount frontend directory for static assets
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
async def serve_index():
    """Serves the main Studio Ops Copilot web chat interface."""
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Studio Ops Copilot API is running. UI not found in frontend/."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
