# Devpost Project Submission: Studio Ops Copilot
**Track:** Grafana Labs Track & Google Cloud Track  
**Hackathon:** Agentic Cinema: The Blockbuster Hackathon  

---

## 📽️ Elevator Pitch
**Studio Ops Copilot** is a conversational AI infrastructure copilot for film and TV production crews. It bridges raw Grafana Cloud telemetry with human operations, using Google Gemini (via Google ADK and `google-genai`) and the official Grafana MCP server to translate complex metrics, logs, and alerts into plain-English Studio Incident Briefs with immediate next actions.

---

## 🎬 Inspiration
Film and television production is governed by unforgiving delivery deadlines: morning executive dailies, film festival DCP handoffs, and live global premieres. Behind these deadlines are massive, complex technical pipelines:
- GPU render farms running Blender, Maya, and Houdini.
- High-throughput transcode clusters crunching 4K/8K ProRes 4444 into AV1 and SMPTE DCPs.
- Low-latency live broadcast ingest paths streaming global premiere events.

These systems produce thousands of metrics, logs, and alerts in Grafana Cloud every minute. But when an overnight render queue backs up at 3:00 AM or a livestream premiere drops frames, the people who need to know first—**post-production supervisors, VFX coordinators, and live broadcast leads**—are not Site Reliability Engineers. Staring at raw PromQL queries and time-series panels under immense deadline pressure is overwhelming.

We built **Studio Ops Copilot** to eliminate this bottleneck: giving creative and operational crews a conversational, natural-language interface directly into their production infrastructure.

---

## 🛠️ What It Does

1. **Conversational Studio Operations:**
   Crew members ask questions in plain English:
   - *"Why is the overnight render queue backed up?"*
   - *"Is the premiere livestream healthy right now?"*
   - *"Show me error rates on the 4K transcode pipeline."*
   - *"List all firing alerts across our pipelines."*

2. **Real-time Grafana MCP Integration:**
   The agent actively calls the official **Grafana Model Context Protocol (MCP)** server (`grafana/mcp-grafana`) to execute:
   - `query_prometheus`: PromQL queries for queue depth, GPU VRAM usage, and frame render duration.
   - `query_loki`: LogQL queries to isolate CUDA OOM crashes, disk exhaustion, and video packet loss.
   - `list_alerts`: Instant inspection of firing Alertmanager rules.
   - `search_dashboards`: Discovery of production dashboards and panel deep-links.

3. **Plain-English Studio Incident Briefs:**
   Powered by Google Gemini, the agent synthesizes raw telemetry into an executive brief structured in 3 parts:
   - **🎬 Production Impact Status:** The real-world cinema effect (e.g. *Sequence 14 / Shot 42 final composite delayed by 3.8 hours*).
   - **📊 Telemetry & Root Cause:** Plain-language explanation of the underlying infrastructure failure (e.g. *18 worker nodes failed due to CUDA Out of Memory on 8K volumetric passes*).
   - **🛠️ Recommended Action:** 1-3 immediate operational steps for the crew (e.g. *Redirect priority queue to 48GB VRAM node pool, purge uncompressed scratch cache*).

4. **Realistic Studio Pipeline Telemetry:**
   Includes a built-in synthetic telemetry generator simulating:
   - **VFX Render Farm:** 64 GPU worker nodes, queue backlog, CUDA OOM failure rates, VRAM saturation.
   - **Premiere Livestream:** SRT ingest bitrate, dropped frames, viewer concurrency, audio-video drift.
   - **Post-Mastering Queue:** DCP transcode throughput and chunk errors.

---

## 🧠 How We Built It

- **AI & Reasoning Layer:**
  - **Google Gemini 2.5 Flash** as the core cognitive engine.
  - **Google Agent Development Kit (`google-adk`)** and the official **Google GenAI SDK (`google-genai`)** for autonomous tool calling and structured function execution.
  - Custom system persona tailored specifically to cinema technical operations and post-production workflows.
- **Observability Layer:**
  - Official **Grafana MCP Server (`grafana/mcp-grafana`)** interfacing with Grafana Cloud.
  - High-fidelity fallback MCP provider ensuring instant zero-friction demonstrations for judges.
  - Standard Prometheus `/metrics` exposition endpoint for scraping by Grafana Cloud Agent / Alloy.
- **Backend & Web Application:**
  - **FastAPI** backend in Python providing conversational streaming, scenario state toggling, and telemetry endpoints.
  - **Modern Cinematic Dark-Mode UI** featuring active pipeline telemetry gauges, incident status pills, quick diagnostic chips, and Markdown response rendering.
- **Deployment & Cloud Infrastructure:**
  - Fully containerized with **Docker** and configured for **Google Cloud Run** via `cloudbuild.yaml` and `deploy.sh`.

---

## 🏆 Non-Negotiables & Hackathon Constraints Followed

- **Strict Google AI Tooling:** Only Google Cloud AI models (Gemini) are used at runtime. No third-party LLMs or non-Google agent frameworks.
- **Approved Google Packages:** `google-genai`, `google-adk`, and `google-cloud-aiplatform` are actively imported and used in the codebase.
- **Live Grafana MCP Integration:** Actively implements the Grafana MCP server protocol to query metrics, logs, dashboards, and alerts.
- **Web Platform:** Runs as an interactive web chat application.
- **Open Source:** Licensed under the standard MIT License detectable in the root repository.

---

## 💡 What's Next for Studio Ops Copilot

- **Automated Self-Healing Remediation:** Giving the agent supervised execution capabilities to trigger Kubernetes worker restarts or route jobs via Deadline / OpenCue APIs.
- **Voice-Activated Ops in the Edit Suite:** Integrating Google Cloud Speech-to-Text and Text-to-Speech so editors in dark grading suites can check render health hands-free.
- **Predictive Render Queue Estimation:** Using Gemini multimodal capabilities to inspect storyboard complexity and forecast render times before artists submit shots to the farm.
