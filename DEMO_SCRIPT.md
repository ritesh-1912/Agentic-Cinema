# Studio Ops Copilot — 3-Minute Demo Video Script
**Hackathon:** Agentic Cinema: The Blockbuster Hackathon (Grafana Labs Track)  
**Total Target Duration:** 2 minutes 45 seconds (Under 3:00 minute hard limit)  
**Tone:** Professional, engaging, cinematic  

---

### [0:00 - 0:30] Introduction: The Film Studio Bottleneck
**Visual:**
- Camera on presenter or intro slide: *"Studio Ops Copilot: AI Infrastructure Intelligence for Film & TV Production"*.
- Cut to screen recording of a chaotic, raw Grafana dashboard filled with complex PromQL graphs, GPU memory heatmaps, and dense LogQL streams.

**Voiceover / Script:**
> *"In modern film and television production, deadlines are absolute. Whether it's an executive screening at 9:00 AM or a global livestream premiere, pipelines like VFX GPU render farms and 4K transcode clusters can never fail.
> 
> But when an overnight render queue backs up at 3:00 AM, the people who need to know first—post-production supervisors and VFX producers—are not SREs. Staring at raw Grafana dashboards under intense deadline pressure is nearly impossible.
> 
> That's why we built **Studio Ops Copilot**."*

---

### [0:30 - 1:15] Architecture & The Core Loop (Google Gemini + Grafana MCP)
**Visual:**
- Switch to browser showing the **Studio Ops Copilot** web interface running at `http://localhost:8080`.
- Highlight the telemetry cards at the top showing the VFX Render Farm, Premiere Livestream, and Mastering Queue.
- Point out the active alert ticker glowing red: *"[CRITICAL] RenderQueueBackpressureCritical"*.

**Voiceover / Script:**
> *"Studio Ops Copilot is a conversational AI agent powered by **Google Gemini** using the official `google-genai` and Google ADK frameworks, connected directly to Grafana Cloud via the official **Grafana Model Context Protocol (MCP) server**.
> 
> Notice our top telemetry dashboard: our VFX render farm is currently in an active incident scenario. The queue is backed up to over 1,400 frames, and 18 worker nodes have faulted.
> 
> Let's see what happens when a post-production supervisor asks a simple, natural-language question."*

---

### [1:15 - 1:55] Demo Scenario 1: Troubleshooting Overnight Render Backpressure
**Visual:**
- Click the quick diagnostic button: *"Why is the overnight render queue backed up?"*
- Show the loading state: *"Analyzing studio telemetry via Grafana MCP..."*.
- Show the tools executed badges appear: `[MCP: query_prometheus('studio_render_queue_depth')]`, `[MCP: query_loki]`, `[MCP: list_alerts]`.
- The rich Markdown response renders on screen.

**Voiceover / Script:**
> *"Watch how the agent handles this. Behind the scenes, Gemini autonomously decided to call the Grafana MCP server: querying Prometheus for queue depth and GPU memory, querying Loki for error logs, and checking active alerts.
> 
> Instead of dumping raw numbers, the agent produces an immediate **Studio Incident Brief**:
> 1. **Production Impact Status**: Shot 42 (Sequence 14) final composite delivery is at risk, delayed by ~3.8 hours.
> 2. **Telemetry & Root Cause**: 18 worker nodes dropped into FAULTED state because uncompressed 8K volumetric beauty passes triggered CUDA Out of Memory errors.
> 3. **Recommended Action**: Reroute priority jobs to the 48GB VRAM node pool, and purge the local scratch cache on worker nodes 1 through 18.
> 
> In 3 seconds, a non-technical supervisor knows exactly what's wrong and what to tell the crew."*

---

### [1:55 - 2:25] Demo Scenario 2: Live Premiere Broadcast Health
**Visual:**
- Use the scenario dropdown to switch to *"🔴 Premiere Livestream Drop (Bitrate)"*.
- Observe the top telemetry gauge update live: ingest bitrate drops to 6,450 kbps, dropped frames jump to 4.85%.
- Type or click: *"Is the premiere livestream healthy right now?"*.
- The agent calls `query_prometheus('studio_livestream_bitrate_kbps')` and `query_prometheus('studio_livestream_dropped_frames_rate')`.

**Voiceover / Script:**
> *"Now let's switch to our broadcast scenario. The studio is hosting a live global premiere with over 50,000 concurrent viewers.
> 
> We ask: 'Is the premiere livestream healthy right now?'
> 
> Studio Ops Copilot immediately queries Grafana MCP, detects that SRT ingest bitrate has collapsed to 6,450 kbps and dropped frames spiked to 4.85%. It warns the broadcast engineer with a Critical badge and recommends immediate failover to the secondary SRT-B ingest path in us-east-1."*

---

### [2:25 - 2:45] Conclusion & Compliance
**Visual:**
- Scroll down to the footer showing the Prometheus `/metrics` link and open it in a new tab to show standard Prometheus exposition.
- Show GitHub repository root with the `LICENSE` (MIT) and Google Cloud Run deployment script.

**Voiceover / Script:**
> *"Studio Ops Copilot strictly adheres to all hackathon guidelines: running exclusively on Google Cloud AI with Gemini, actively utilizing the Grafana MCP server, fully open source under the MIT License, and ready for deployment on Google Cloud Run.
> 
> With Studio Ops Copilot, every production supervisor has a 24/7 AI Site Reliability Director on their crew.
> 
> Thank you!"*
