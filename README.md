# 🎬 Studio Ops Copilot
### Conversational AI Infrastructure Intelligence for Film & TV Production Pipelines
**Submission for the Agentic Cinema: The Blockbuster Hackathon (Google Cloud + Devpost — Grafana Labs Track)**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-brightgreen.svg)](https://agentic-cinema-3r18.onrender.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-amber.svg)](https://opensource.org/licenses/MIT)
[![Google Cloud AI](https://img.shields.io/badge/Google%20AI-Gemini%20Flash%20%2F%20ADK-blue.svg)](https://ai.google.dev)
[![Grafana MCP](https://img.shields.io/badge/Grafana-MCP%20Server-orange.svg)](https://github.com/grafana/mcp-grafana)

🌐 **Live Application URL:** [https://agentic-cinema-3r18.onrender.com](https://agentic-cinema-3r18.onrender.com)

---

## 💡 The Concept

Film and television pipelines (VFX GPU render farms, 4K/8K transcode clusters, SMPTE DCP mastering, live premiere broadcast streams) generate continuous infrastructure telemetry. When an overnight render queue backs up before an executive screening, or a premiere livestream drops frames, the people who need to know first—**post-production supervisors, VFX coordinators, and live broadcast directors**—are the last to find out because they cannot decipher complex raw Grafana dashboards under intense deadline pressure.

**Studio Ops Copilot** is a conversational AI agent that bridges raw **Grafana Cloud** telemetry and human studio operations. Powered by **Google Gemini** (via `google-genai` and `google-adk`) and the official **Grafana Model Context Protocol (MCP) server (`grafana/mcp-grafana`)**, it translates technical bottlenecks (CUDA OOM thrashing, SRT bitrate drops, chunk boundary errors) into plain-English **Studio Incident Briefs** with real production impact and immediate next steps.

---

## 🏗️ Architecture

```
 ┌─────────────────────────────────────────────────────────────┐
 │                Cinema Production Crew (Web UI)              │
 │   [Post-Prod Supervisor] [VFX Lead] [Broadcast Engineer]    │
 └──────────────────────────────┬──────────────────────────────┘
                                │ HTTP / WebSocket
 ┌──────────────────────────────▼──────────────────────────────┐
 │             Studio Ops Copilot Backend (FastAPI)            │
 │                                                             │
 │  ┌───────────────────────────────────────────────────────┐  │
 │  │       Reasoning Layer (Google Gemini Flash)           │  │
 │  │         `google-genai` & Google ADK Tool Calling      │  │
 │  └───────────────────────────┬───────────────────────────┘  │
 │                              │ Tool Execution               │
 │  ┌───────────────────────────▼───────────────────────────┐  │
 │  │            Real Grafana MCP Client Bridge             │  │
 │  │   - Real MCP ClientSession (stdio transport) to       │  │
 │  │     `grafana/mcp-grafana`                             │  │
 │  │   - Tools discovered dynamically via                  │  │
 │  │     session.list_tools() at startup                   │  │
 │  │   - Tools: query_prometheus, query_loki,              │  │
 │  │            search_dashboards, list_alerts             │  │
 │  └───────────────────────────┬───────────────────────────┘  │
 └──────────────────────────────┼──────────────────────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        ▼                                               ▼
┌───────────────────────────────┐     ┌─────────────────────────────────┐
│     Grafana Cloud / Server    │     │   Synthetic Cinema Telemetry    │
│  - PromQL (Render/GPU/Stream) │     │   - VFX Render Farm (Blender)   │
│  - Alerts (Queue backpressure)│◄────┤   - Encoding Cluster (Transcode)│
│  - Dashboards & Incidents     │     │   - Live Broadcast Premiere     │
└───────────────────────────────┘     └─────────────────────────────────┘
```

📖 **Detailed Architectural Blueprint & Flowcharts:** See [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 🎯 Compliance with Hackathon Hard Constraints

| Requirement | Implementation in Studio Ops Copilot | Verification |
| :--- | :--- | :--- |
| **Google AI Tooling Only** | Powered exclusively by Gemini models using `google-genai` and `google-adk`. Zero third-party LLMs or non-Google agent frameworks. | Imported in [`backend/agent/copilot.py`](backend/agent/copilot.py) |
| **Approved Google Packages** | Actively imports and uses `google-genai`, `google-adk`, `google-cloud-aiplatform`. | Declared in [`requirements.txt`](requirements.txt) |
| **Live Grafana MCP Integration**| Connects to official `grafana/mcp-grafana` MCP server via the official Python `mcp` SDK using `ClientSession` over stdio transport. Discovers tools dynamically via `list_tools()` and calls them via `call_tool()`. | Implemented in [`backend/mcp/client.py`](backend/mcp/client.py) |
| **Web Platform** | Command-center control room UI designed for ops under pressure, served by FastAPI. | [`frontend/index.html`](frontend/index.html) |
| **Public OSS License** | Standard MIT License in repo root. | [`LICENSE`](LICENSE) |
| **Deployment** | Dockerfile and Google Cloud Run deployment scripts ready. | [`Dockerfile`](Dockerfile), [`cloudbuild.yaml`](cloudbuild.yaml) |

---

## ⚡ Key Features

1. **Natural-Language Studio Incident Briefs**: Translates raw metrics into structured briefs featuring:
   - 🎬 **Production Impact Status** (e.g. *Shot 42 delivery delayed by 3.8 hours*)
   - 📊 **Telemetry & Root Cause via Grafana MCP** (e.g. *CUDA Out of Memory on 8K volumetric passes on Node Pool B*)
   - 🛠️ **Recommended Action for Crew** (e.g. *Reroute to 48GB VRAM node pool, purge uncompressed texture cache*)
2. **Multi-Stage Studio Telemetry Simulator**:
   - **VFX Render Farm**: 64 GPU nodes, queue backlog, CUDA OOM failure rates, VRAM saturation.
   - **Premiere Livestream**: SRT/RTMP ingest bitrate, dropped frame rate, viewer concurrency, audio sync drift.
   - **4K/8K Transcoder**: ProRes 4444 XQ to AV1/SMPTE DCP queue depth and error rates.
3. **Interactive Incident Switcher**: Live dropdown to switch between active production incidents:
   - 🔴 *VFX Render Backlog (OOM)*
   - 🔴 *Premiere Livestream Drop*
   - 🟡 *Transcode Bottleneck*
   - 🟢 *All Pipelines Nominal*
4. **Prometheus Exposition Endpoint**: Exposes `/metrics` in standard Prometheus text format for scraping by Grafana Cloud Agent, Alloy, or local Prometheus.
5. **Zero-Friction Evaluation Mode**: Runs smoothly with full tool-orchestration out of the box even without cloud keys, and seamlessly connects to live Grafana Cloud and Gemini with API keys.

---

## 🚀 Quickstart

### Option 1: Local Development

```bash
# 1. Clone repository
git clone https://github.com/ritesh-1912/Agentic-Cinema.git
cd Agentic-Cinema

# 2. Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment (optional - demo mode runs without keys)
cp .env.example .env
# Edit .env and set GEMINI_API_KEY (free from https://aistudio.google.com/app/api-keys, no GCP billing needed)
# and your Grafana credentials if connecting to live Grafana Cloud.

# 4. Start the server
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload
```
Open **http://localhost:8080** in your browser.

### Option 2: Docker / Docker Compose

```bash
# Run standalone container
docker build -t studio-ops-copilot .
docker run -p 8080:8080 studio-ops-copilot

# Or run full local stack with Prometheus and Grafana
docker compose up -d
```

### Option 3: Deploy to Render.com (Recommended Free Hosting — No Credit Card)

1. Sign in to [render.com](https://render.com) using your GitHub account.
2. Click **New +** → **Web Service** → select `ritesh-1912/Agentic-Cinema`.
3. Render automatically detects the `Dockerfile` (which includes the pre-bundled `mcp-grafana` binary).
4. Select the **Free** instance type ($0/mo).
5. In **Environment Variables**, add:
   - `GEMINI_API_KEY`: Free key from [Google AI Studio](https://aistudio.google.com/app/api-keys) (no GCP billing required).
   - *(Optional)* `GRAFANA_URL` & `GRAFANA_SERVICE_ACCOUNT_TOKEN` if connecting to live Grafana Cloud.
6. Click **Create Web Service**. Your live URL will be ready at `https://<service-name>.onrender.com`.

### Option 4: Deploy to Google Cloud Run

```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 🧪 Testing

Run the automated test suite:

```bash
# Run standalone unit tests
python3 -m unittest tests/test_standalone.py

# Run full pytest suite including real MCP integration test
pytest -v tests/
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
