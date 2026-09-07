document.addEventListener("DOMContentLoaded", () => {
  const messagesList = document.getElementById("messagesList");
  const chatForm = document.getElementById("chatForm");
  const queryInput = document.getElementById("queryInput");
  const sendBtn = document.getElementById("sendBtn");
  const scenarioSelect = document.getElementById("scenarioSelect");

  // Telemetry elements
  const valQueueDepth = document.getElementById("valQueueDepth");
  const valNodes = document.getElementById("valNodes");
  const valVram = document.getElementById("valVram");
  const valActiveShot = document.getElementById("valActiveShot");
  const renderStatusDot = document.getElementById("renderStatusDot");

  const valBitrate = document.getElementById("valBitrate");
  const valDropped = document.getElementById("valDropped");
  const valViewers = document.getElementById("valViewers");
  const liveStatusDot = document.getElementById("liveStatusDot");

  const valTranscodeQueue = document.getElementById("valTranscodeQueue");
  const valTranscodeWorkers = document.getElementById("valTranscodeWorkers");
  const valTranscodeErrors = document.getElementById("valTranscodeErrors");
  const transcodeStatusDot = document.getElementById("transcodeStatusDot");

  const alertsTicker = document.getElementById("alertsTicker");
  const alertTickerText = document.getElementById("alertTickerText");

  // Conversation history array
  const conversationHistory = [];

  // Poll Telemetry every 2 seconds
  async function updateTelemetry() {
    try {
      const res = await fetch("/api/telemetry/status");
      if (!res.ok) return;
      const data = await res.json();

      const rf = data.render_farm;
      valQueueDepth.textContent = Number(rf.queue_depth).toLocaleString();
      valNodes.textContent = `${rf.active_nodes} / ${rf.faulted_nodes}`;
      valVram.textContent = `${Number(rf.gpu_vram_usage_percent).toFixed(1)}%`;
      valActiveShot.textContent = `Shot: ${rf.active_shot}`;

      if (rf.faulted_nodes > 5 || rf.queue_depth > 500) {
        renderStatusDot.className = "status-indicator critical";
      } else {
        renderStatusDot.className = "status-indicator";
      }

      const live = data.livestream_premiere;
      valBitrate.textContent = `${Number(live.ingest_bitrate_kbps).toLocaleString()} kbps`;
      valDropped.textContent = `${Number(live.dropped_frames_percent).toFixed(2)}%`;
      valViewers.textContent = Number(live.viewer_concurrency).toLocaleString();

      if (live.dropped_frames_percent > 1.0 || live.ingest_bitrate_kbps < 10000) {
        liveStatusDot.className = "status-indicator critical";
      } else {
        liveStatusDot.className = "status-indicator";
      }

      const enc = data.encoding_pipeline;
      valTranscodeQueue.textContent = enc.transcode_queue_length;
      valTranscodeWorkers.textContent = enc.active_workers;
      valTranscodeErrors.textContent = `${Number(enc.error_rate_percent).toFixed(2)}%`;

      if (enc.error_rate_percent > 5.0) {
        transcodeStatusDot.className = "status-indicator warning";
      } else {
        transcodeStatusDot.className = "status-indicator";
      }

      // Alerts
      if (data.alerts && data.alerts.length > 0) {
        alertsTicker.style.display = "flex";
        const topAlert = data.alerts[0];
        alertTickerText.textContent = `[${topAlert.severity}] ${topAlert.name}: ${topAlert.message}`;
      } else {
        alertTickerText.textContent = "All production infrastructure nominal. No active alerts.";
        alertsTicker.style.background = "rgba(46, 160, 67, 0.1)";
        alertsTicker.style.borderColor = "rgba(46, 160, 67, 0.3)";
        alertsTicker.style.color = "#56d364";
      }
    } catch (err) {
      console.warn("Failed to fetch telemetry:", err);
    }
  }

  setInterval(updateTelemetry, 2000);
  updateTelemetry();

  // Switch Scenario
  scenarioSelect.addEventListener("change", async (e) => {
    const newScenario = e.target.value;
    try {
      await fetch("/api/telemetry/scenario", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario: newScenario })
      });
      updateTelemetry();
    } catch (err) {
      console.error("Failed to switch scenario:", err);
    }
  });

  // Append a message bubble to the chat
  function appendMessage(sender, text, isUser = false, toolsExecuted = [], modelTag = "") {
    const bubble = document.createElement("div");
    bubble.className = `message-bubble ${isUser ? "user-bubble" : "agent-bubble"}`;

    const header = document.createElement("div");
    header.className = "bubble-header";

    const senderSpan = document.createElement("span");
    senderSpan.className = "sender-name";
    senderSpan.textContent = isUser ? "👤 Post Supervisor" : "🎬 Studio Ops Copilot";

    const tagSpan = document.createElement("span");
    tagSpan.className = "model-tag";
    tagSpan.textContent = modelTag || (isUser ? "Console Query" : "Gemini 2.5 Flash");

    header.appendChild(senderSpan);
    header.appendChild(tagSpan);
    bubble.appendChild(header);

    const content = document.createElement("div");
    content.className = "bubble-content";
    if (window.marked && !isUser) {
      content.innerHTML = marked.parse(text);
    } else {
      content.textContent = text;
    }
    bubble.appendChild(content);

    if (toolsExecuted && toolsExecuted.length > 0) {
      const toolsDiv = document.createElement("div");
      toolsDiv.className = "tools-called-badge";
      toolsExecuted.forEach((tool) => {
        const tag = document.createElement("span");
        tag.className = "tool-tag";
        tag.textContent = `⚡ MCP: ${tool}`;
        toolsDiv.appendChild(tag);
      });
      bubble.appendChild(toolsDiv);
    }

    messagesList.appendChild(bubble);
    messagesList.scrollTop = messagesList.scrollHeight;
    return bubble;
  }

  // Handle Query Submission
  async function submitQuery(queryText) {
    if (!queryText || !queryText.trim()) return;
    const cleanQuery = queryText.trim();

    appendMessage("User", cleanQuery, true);
    queryInput.value = "";
    queryInput.disabled = true;
    sendBtn.disabled = true;

    // Loading placeholder
    const loadingBubble = appendMessage("Agent", "*Analyzing studio telemetry via Grafana MCP...*", false);

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
      loadingBubble.remove();

      appendMessage(
        "Agent",
        data.answer,
        false,
        data.tools_executed || [],
        data.model || "Gemini 2.5 Flash"
      );

      conversationHistory.push({ role: "user", content: cleanQuery });
      conversationHistory.push({ role: "assistant", content: data.answer });
    } catch (err) {
      loadingBubble.remove();
      appendMessage("Agent", `⚠️ **Error communicating with Copilot backend**: ${err.message}`, false);
    } finally {
      queryInput.disabled = false;
      sendBtn.disabled = false;
      queryInput.focus();
    }
  }

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    submitQuery(queryInput.value);
  });

  // Quick Query Chips
  document.querySelectorAll(".query-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const q = chip.getAttribute("data-query");
      submitQuery(q);
    });
  });
});
