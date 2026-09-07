document.addEventListener("DOMContentLoaded", () => {
  const briefFeed = document.getElementById("briefFeed");
  const consoleForm = document.getElementById("consoleForm");
  const queryInput = document.getElementById("queryInput");
  const submitBtn = document.getElementById("submitBtn");
  const scenarioSelect = document.getElementById("scenarioSelect");

  // Left rail pipeline elements
  const dotRenderFarm = document.getElementById("dotRenderFarm");
  const lblRenderFarm = document.getElementById("lblRenderFarm");
  const dotLivestream = document.getElementById("dotLivestream");
  const lblLivestream = document.getElementById("lblLivestream");
  const dotTranscode = document.getElementById("dotTranscode");
  const lblTranscode = document.getElementById("lblTranscode");

  const alertCountBadge = document.getElementById("alertCountBadge");
  const alertTopMessage = document.getElementById("alertTopMessage");

  // Right rail telemetry strip elements
  const telQueueDepth = document.getElementById("telQueueDepth");
  const telNodes = document.getElementById("telNodes");
  const telVram = document.getElementById("telVram");
  const telFailedJobs = document.getElementById("telFailedJobs");
  const telFrameTime = document.getElementById("telFrameTime");
  const telBitrate = document.getElementById("telBitrate");
  const telDropped = document.getElementById("telDropped");
  const telViewers = document.getElementById("telViewers");
  const telDrift = document.getElementById("telDrift");
  const telTranscodeQueue = document.getElementById("telTranscodeQueue");
  const telTranscodeWorkers = document.getElementById("telTranscodeWorkers");
  const telTranscodeErrors = document.getElementById("telTranscodeErrors");
  const telActiveShot = document.getElementById("telActiveShot");
  const pollTimestamp = document.getElementById("pollTimestamp");

  const conversationHistory = [];

  // Update telemetry strip and pipeline indicators
  async function fetchTelemetry() {
    try {
      const res = await fetch("/api/telemetry/status");
      if (!res.ok) return;
      const data = await res.json();

      const now = new Date();
      pollTimestamp.textContent = now.toTimeString().split(" ")[0];

      // VFX Render Farm
      const rf = data.render_farm;
      telQueueDepth.textContent = Number(rf.queue_depth).toLocaleString();
      telNodes.textContent = `${rf.active_nodes} / ${rf.faulted_nodes}`;
      telVram.textContent = `${Number(rf.gpu_vram_usage_percent).toFixed(1)}%`;
      telFailedJobs.textContent = rf.failed_jobs_last_hour;
      telFrameTime.textContent = `${Number(rf.average_frame_render_time_sec).toFixed(0)}s`;
      telActiveShot.innerHTML = `<strong>Shot:</strong> ${rf.active_shot}`;

      if (rf.faulted_nodes > 5 || rf.queue_depth > 500) {
        dotRenderFarm.className = "pipeline-indicator critical";
        lblRenderFarm.textContent = "Backpressure (OOM)";
      } else {
        dotRenderFarm.className = "pipeline-indicator nominal";
        lblRenderFarm.textContent = "Nominal";
      }

      // Premiere Livestream
      const live = data.livestream_premiere;
      telBitrate.textContent = `${Number(live.ingest_bitrate_kbps).toLocaleString()} kbps`;
      telDropped.textContent = `${Number(live.dropped_frames_percent).toFixed(2)}%`;
      telViewers.textContent = Number(live.viewer_concurrency).toLocaleString();
      telDrift.textContent = `${Number(live.audio_sync_drift_ms).toFixed(1)} ms`;

      if (live.dropped_frames_percent > 1.0 || live.ingest_bitrate_kbps < 10000) {
        dotLivestream.className = "pipeline-indicator critical";
        lblLivestream.textContent = "Ingest Degraded";
      } else {
        dotLivestream.className = "pipeline-indicator nominal";
        lblLivestream.textContent = "Broadcasting";
      }

      // 4K/8K Transcode
      const enc = data.encoding_pipeline;
      telTranscodeQueue.textContent = enc.transcode_queue_length;
      telTranscodeWorkers.textContent = enc.active_workers;
      telTranscodeErrors.textContent = `${Number(enc.error_rate_percent).toFixed(2)}%`;

      if (enc.error_rate_percent > 5.0) {
        dotTranscode.className = "pipeline-indicator critical";
        lblTranscode.textContent = "Worker Exhaustion";
      } else {
        dotTranscode.className = "pipeline-indicator nominal";
        lblTranscode.textContent = "Nominal";
      }

      // Alerts
      if (data.alerts && data.alerts.length > 0) {
        alertCountBadge.className = "alert-count critical";
        alertCountBadge.textContent = `${data.alerts.length} firing`;
        alertTopMessage.textContent = `${data.alerts[0].name}: ${data.alerts[0].message}`;
      } else {
        alertCountBadge.className = "alert-count nominal";
        alertCountBadge.textContent = "0 firing";
        alertTopMessage.textContent = "All production infrastructure nominal.";
      }

    } catch (err) {
      console.warn("Failed to update telemetry:", err);
    }
  }

  setInterval(fetchTelemetry, 2000);
  fetchTelemetry();

  // Scenario selection
  scenarioSelect.addEventListener("change", async (e) => {
    try {
      await fetch("/api/telemetry/scenario", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario: e.target.value })
      });
      fetchTelemetry();
    } catch (err) {
      console.error("Scenario switch error:", err);
    }
  });

  // Render a user query panel in the feed
  function appendUserQuery(text) {
    const panel = document.createElement("div");
    panel.className = "user-query-panel";
    panel.innerHTML = `
      <div class="query-user-title">Crew Query</div>
      <div class="query-user-text">${escapeHtml(text)}</div>
    `;
    briefFeed.appendChild(panel);
    briefFeed.scrollTop = briefFeed.scrollHeight;
    return panel;
  }

  // Render an incident brief panel in the feed
  function appendIncidentBrief(answerText, toolsExecuted = [], modelTag = "", isFallback = false) {
    const panel = document.createElement("div");
    panel.className = "brief-panel";

    const isCritical = answerText.includes("CRITICAL") || answerText.includes("🔴");
    const statusText = isCritical ? "CRITICAL" : "NOMINAL";
    const statusClass = isCritical ? "critical" : "nominal";

    let toolsHtml = "";
    if (toolsExecuted && toolsExecuted.length > 0) {
      toolsHtml = `
        <div class="brief-tools-footer">
          ${toolsExecuted.map(t => `<span class="tool-badge">⚡ MCP: ${escapeHtml(t)}</span>`).join("")}
        </div>
      `;
    }

    const parsedContent = window.marked ? marked.parse(answerText) : `<p>${escapeHtml(answerText)}</p>`;
    const modelLabel = modelTag || "Gemini 2.5 Flash";

    panel.innerHTML = `
      <div class="brief-panel-header">
        <div class="header-left">
          <span class="status-pill ${statusClass}">${statusText}</span>
          <span class="brief-title">Studio Incident Brief</span>
        </div>
        <span class="brief-meta">${escapeHtml(modelLabel)} &bull; Grafana MCP</span>
      </div>
      <div class="brief-body">
        ${parsedContent}
      </div>
      ${toolsHtml}
    `;

    briefFeed.appendChild(panel);
    briefFeed.scrollTop = briefFeed.scrollHeight;
    return panel;
  }

  // Submit query
  async function submitQuery(queryText) {
    if (!queryText || !queryText.trim()) return;
    const cleanQuery = queryText.trim();

    appendUserQuery(cleanQuery);
    queryInput.value = "";
    queryInput.disabled = true;
    submitBtn.disabled = true;

    // Temporary resolution state
    const resolvingPanel = document.createElement("div");
    resolvingPanel.className = "brief-panel";
    resolvingPanel.innerHTML = `
      <div class="brief-body" style="color: var(--text-muted); font-style: italic;">
        Querying Grafana MCP server and synthesizing incident brief via Google Gemini...
      </div>
    `;
    briefFeed.appendChild(resolvingPanel);
    briefFeed.scrollTop = briefFeed.scrollHeight;

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: cleanQuery,
          history: conversationHistory
        })
      });

      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}`);
      }

      const data = await res.json();
      resolvingPanel.remove();

      appendIncidentBrief(
        data.answer,
        data.tools_executed || [],
        data.model || "Gemini 2.5 Flash",
        Boolean(data.is_fallback)
      );

      conversationHistory.push({ role: "user", content: cleanQuery });
      conversationHistory.push({ role: "assistant", content: data.answer });

    } catch (err) {
      resolvingPanel.remove();
      const errPanel = document.createElement("div");
      errPanel.className = "brief-panel";
      errPanel.innerHTML = `
        <div class="brief-panel-header">
          <span class="status-pill critical">ERROR</span>
          <span class="brief-title">Query Resolution Failed</span>
        </div>
        <div class="brief-body">
          <p>Failed to resolve telemetry query: ${escapeHtml(err.message)}</p>
          <p>Verify that the backend service and Grafana MCP transport are running.</p>
        </div>
      `;
      briefFeed.appendChild(errPanel);
    } finally {
      queryInput.disabled = false;
      submitBtn.disabled = false;
      queryInput.focus();
    }
  }

  consoleForm.addEventListener("submit", (e) => {
    e.preventDefault();
    submitQuery(queryInput.value);
  });

  document.querySelectorAll(".ops-query-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const q = btn.getAttribute("data-query");
      submitQuery(q);
    });
  });

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }
});
