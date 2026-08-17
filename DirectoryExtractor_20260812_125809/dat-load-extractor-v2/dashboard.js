const API_BASE = "http://127.0.0.1:5000";

// Global error handlers to log client-side errors to server's events.log
window.addEventListener("error", (event) => {
  fetch(`${API_BASE}/log_event`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      event_type: "CLIENT_ERROR",
      details: {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        stack: event.error ? event.error.stack : ""
      }
    })
  }).catch(() => {});
});

window.addEventListener("unhandledrejection", (event) => {
  fetch(`${API_BASE}/log_event`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      event_type: "CLIENT_UNHANDLED_REJECTION",
      details: {
        reason: String(event.reason),
        stack: event.reason && event.reason.stack ? event.reason.stack : ""
      }
    })
  }).catch(() => {});
});

let tryId = null;
let currentTab = "all"; // all, successful, skipped, failed
let currentExportScope = "all"; // all, success, skipped, failed
let allRecords = [];
let allTaskStats = [];
let lastLogTimestamp = "";
let isCrawlerRunning = false;
let lastStatusPoll = 0;
let lastDatasetPoll = 0;
let lastLogPoll = 0;
let lastDatasetSig = "";

// Cadence: fast while a crawl is live, relaxed when idle. Never zero — the
// dashboard used to stop polling entirely once it had loaded anything.
const POLL_ACTIVE_MS = 2000;
const POLL_IDLE_MS = 8000;

const $ = (id) => document.getElementById(id);

/**
 * Chrome clamps setInterval to roughly once a minute in a background tab, and
 * the crawler deliberately activates its own tabs — so the dashboard spends
 * most of a run in the background. A worker clock is not clamped that way,
 * which is what keeps the numbers moving while the crawl has focus elsewhere.
 */
function startTicker(fn, intervalMs) {
  try {
    const blob = new Blob([
      "let id=null;onmessage=function(e){" +
      "if(e.data&&e.data.stop){clearInterval(id);return;}" +
      "clearInterval(id);id=setInterval(function(){postMessage(1);},e.data.ms);};"
    ], { type: "application/javascript" });
    const worker = new Worker(URL.createObjectURL(blob));
    worker.onmessage = () => { try { fn(); } catch (e) { console.warn("tick failed:", e); } };
    worker.postMessage({ ms: intervalMs });
    return worker;
  } catch (e) {
    console.warn("Worker clock unavailable, falling back to setInterval:", e);
    setInterval(fn, intervalMs);
    return null;
  }
}

// Load data on startup and setup interval
async function initDashboard() {
  try {
    await updateStatus();
  } catch (e) {
    console.warn("Initial status poll failed:", e);
  }
  try {
    await updateDataset();
  } catch (e) {
    console.warn("Initial dataset poll failed:", e);
  }
  try {
    await updateLogs();
  } catch (e) {
    console.warn("Initial logs poll failed:", e);
  }
  
  // Worker-driven so the dashboard keeps updating while the crawler holds focus.
  startTicker(updateStatus, 1000);
  startTicker(updateDataset, 1000);
  startTicker(updateLogs, 1000);

  setupEventListeners();

  // Establish background keep-alive connection
  connectKeepAlive();
}

// ── Update status, progress, and gauges ──
async function updateStatus() {
  // Deliberately NOT gated on document.hidden: the crawler activates its own
  // tabs, so the dashboard is backgrounded for most of a run.
  const now = Date.now();
  const gap = isCrawlerRunning ? POLL_ACTIVE_MS : POLL_IDLE_MS;
  if (now - lastStatusPoll < gap) return;
  lastStatusPoll = now;

  try {
    const res = await fetch(`${API_BASE}/status`);
    if (!res.ok) throw new Error("Server offline");
    
    const stat = await res.json();
    
    // Always sync tryId if returned, even if session is inactive
    if (stat.try_id) {
      tryId = stat.try_id;
      $("sessId").textContent = tryId.slice(0, 8) + "...";
      $("sessId").title = tryId;
    } else {
      $("sessId").textContent = "-";
      $("sessId").title = "";
    }

    if (!stat.active) {
      isCrawlerRunning = false;
      $("sessState").textContent = "IDLE";
      $("sessDot").className = "status-dot";
      $("sessDot").style.backgroundColor = "var(--text-disabled)";
      $("sessDot").style.boxShadow = "none";
      $("stopCrawlerBtn").classList.remove("hidden");
      $("stopCrawlerBtn").setAttribute("disabled", "true");
      $("stopCrawlerBtn").style.opacity = "0.4";
      $("stopCrawlerBtn").style.cursor = "not-allowed";
      if ($("resumeCrawlerBtn")) $("resumeCrawlerBtn").classList.add("hidden");
      return;
    }
    
    // Status text
    $("sessState").textContent = stat.status.toUpperCase();
    $("sessDot").className = "status-dot";
    if (stat.status === "in_progress") {
      isCrawlerRunning = true;
      $("sessDot").style.backgroundColor = "var(--accent)";
      $("sessDot").style.boxShadow = "var(--shadow-accent)";
      $("stopCrawlerBtn").classList.remove("hidden");
      $("stopCrawlerBtn").removeAttribute("disabled");
      $("stopCrawlerBtn").style.opacity = "1";
      $("stopCrawlerBtn").style.cursor = "pointer";
      if ($("resumeCrawlerBtn")) $("resumeCrawlerBtn").classList.add("hidden");
    } else {
      isCrawlerRunning = false;
      if (stat.status === "completed") {
        $("sessDot").style.backgroundColor = "var(--primary)";
        $("sessDot").style.boxShadow = "var(--shadow-primary)";
        $("stopCrawlerBtn").classList.remove("hidden");
        $("stopCrawlerBtn").setAttribute("disabled", "true");
        $("stopCrawlerBtn").style.opacity = "0.4";
        $("stopCrawlerBtn").style.cursor = "not-allowed";
        if ($("resumeCrawlerBtn")) $("resumeCrawlerBtn").classList.add("hidden");
      } else {
        // cancelled/stopped
        $("sessDot").style.backgroundColor = "var(--danger)";
        $("sessDot").style.boxShadow = "none";
        $("stopCrawlerBtn").classList.add("hidden");
        if ($("resumeCrawlerBtn")) {
          $("resumeCrawlerBtn").classList.remove("hidden");
          $("resumeCrawlerBtn").removeAttribute("disabled");
          $("resumeCrawlerBtn").style.opacity = "1";
          $("resumeCrawlerBtn").style.cursor = "pointer";
        }
      }
    }
    
    // Progress
    const completedBatches = stat.completed || 0;
    const totalBatches = stat.total || 0;
    const pct = totalBatches > 0 ? Math.round((completedBatches / totalBatches) * 100) : 0;
    
    $("progressPctText").textContent = `${pct}%`;
    $("progressBatchesCount").textContent = `${completedBatches} / ${totalBatches}`;
    $("progressBarFill").style.width = `${pct}%`;
    
    if (stat.tasks) {
      const completedTasks = stat.tasks.completed || 0;
      const skippedTasks = stat.tasks.skipped || 0;
      const failedTasks = stat.tasks.failed || 0;
      const totalTasks = stat.tasks.total || 0;
      const runningTasks = stat.tasks.running || 0;
      $("progressPermsCount").textContent = `${completedTasks + skippedTasks + failedTasks} / ${totalTasks}`;
      
      // Counters
      $("metricExtracted").textContent = stat.tasks.success_records || 0;
      $("metricSuccess").textContent = completedTasks;
      $("metricSuccessSub").textContent = `${completedTasks} successful combinations`;
      $("metricSkipped").textContent = skippedTasks;
      $("metricFailed").textContent = failedTasks;
      
      if ($("metricRunningTasks")) $("metricRunningTasks").textContent = runningTasks;
      if ($("metricRunningTasksSub")) $("metricRunningTasksSub").textContent = `${runningTasks} active permutations`;
    }
    
    // Concurrency
    $("metricWindows").textContent = stat.in_progress || 0;
    if ($("metricWindowsSub")) $("metricWindowsSub").textContent = `limit: ${stat.concurrency_limit || 4}`;
    
    // CPU gauge
    const cpu = stat.cpu_usage || 0;
    $("metricCpu").textContent = `${cpu}%`;
    const cpuGauge = $("cpuGauge");
    cpuGauge.style.width = `${cpu}%`;
    if (cpu > 80) {
      cpuGauge.style.backgroundColor = "var(--danger)";
    } else if (cpu > 60) {
      cpuGauge.style.backgroundColor = "var(--warning)";
    } else {
      cpuGauge.style.backgroundColor = "var(--accent)";
    }
    
    // Memory gauge
    const memory = stat.memory_usage || 0;
    $("metricMemory").textContent = `${memory}%`;
    const memGauge = $("memGauge");
    memGauge.style.width = `${memory}%`;
    if (memory > 80) {
      memGauge.style.backgroundColor = "var(--danger)";
    } else if (memory > 60) {
      memGauge.style.backgroundColor = "var(--warning)";
    } else {
      memGauge.style.backgroundColor = "var(--accent)";
    }
    
    // ETA
    $("metricEta").textContent = stat.eta || "Calculating...";
  } catch (err) {
    $("sessState").textContent = "OFFLINE";
    $("sessDot").className = "status-dot";
    $("sessDot").style.backgroundColor = "var(--danger)";
    $("sessDot").style.boxShadow = "none";
    $("stopCrawlerBtn").setAttribute("disabled", "true");
    $("stopCrawlerBtn").style.opacity = "0.4";
    $("stopCrawlerBtn").style.cursor = "not-allowed";
  }
}

// ── Update dataset table ──
async function updateDataset() {
  if (!tryId) return;
  const now = Date.now();
  const gap = isCrawlerRunning ? POLL_ACTIVE_MS : POLL_IDLE_MS;
  if (now - lastDatasetPoll < gap) return;
  lastDatasetPoll = now;

  try {
    const res = await fetch(`${API_BASE}/dataset?try_id=${tryId}`);
    if (!res.ok) return;

    const data = await res.json();
    if (!data.success) return;

    // Re-render only when something actually changed. The signature includes the
    // row counts, not just `counts` — a missing counts field used to freeze the
    // table permanently after its first render.
    const sig = JSON.stringify(data.counts || {}) +
      `|${(data.records || []).length}|${(data.task_stats || []).length}`;
    if (sig === lastDatasetSig) {
      return;
    }
    lastDatasetSig = sig;

    allRecords = data.records || [];
    allTaskStats = data.task_stats || [];
    
    // Filter and update tabs labels
    const successfulCount = allRecords.length;
    const skippedCount = allTaskStats.filter(ts => (ts.status && ts.status.includes("skipped")) || ts.status === "skipped_zero_results").length;
    const failedCount = allTaskStats.filter(ts => ts.status === "error" || ts.status === "failed").length;
    const totalCount = successfulCount + skippedCount + failedCount;
    
    $("tabAll").textContent = `All (${totalCount})`;
    $("tabSuccessful").textContent = `Extracted (${successfulCount})`;
    $("tabSkipped").textContent = `Skipped (${skippedCount})`;
    $("tabFailed").textContent = `Failed (${failedCount})`;
    
    renderTable();
  } catch (err) {
    console.warn("Dataset load error:", err);
  }
}

// ── Filter and render records table ──
function renderTable() {
  const tbody = $("resultsTableBody");
  const searchVal = $("searchInput").value.toLowerCase();
  
  // Build combined rows to display
  let rowsToDisplay = [];
  
  // 1. Successful loads
  allRecords.forEach(r => {
    rowsToDisplay.push({
      status: "Success",
      origin: r.origin || "–",
      destination: r.destination || "–",
      age: r.age || "–",
      rate: r.rate || "–",
      rpm: r.ratePerMile || "–",
      trip: r.tripMiles ? r.tripMiles + " mi" : "–",
      company: r.company || "–",
      equipment: r.equipmentType || "–",
      docket: r.dir_docket || "–",
      dot: r.dir_dot_number || "–",
      timestamp: r.timestamp ? formatTime(r.timestamp) : "–"
    });
  });
  
  // 2. Skipped combinations
  allTaskStats.forEach(ts => {
    if ((ts.status && ts.status.includes("skipped")) || ts.status === "skipped_zero_results") {
      const statusLabel = ts.status === "skipped_zero_results" ? "Skipped (0 results)" : `Skipped (${ts.status})`;
      rowsToDisplay.push({
        status: statusLabel,
        origin: ts.origin || "–",
        destination: ts.dest || "–",
        age: "–",
        rate: "–",
        rpm: "–",
        trip: "–",
        company: "–",
        equipment: ts.eq || "–",
        docket: "–",
        dot: "–",
        timestamp: "–"
      });
    } else if (ts.status === "error" || ts.status === "failed") {
      rowsToDisplay.push({
        status: "Failed",
        origin: ts.origin || "–",
        destination: ts.dest || "–",
        age: "–",
        rate: "–",
        rpm: "–",
        trip: "–",
        company: ts.error || "Execution failed",
        equipment: ts.eq || "–",
        docket: "–",
        dot: "–",
        timestamp: "–"
      });
    }
  });

  // Filter based on tab
  if (currentTab === "successful") {
    rowsToDisplay = rowsToDisplay.filter(r => r.status === "Success");
  } else if (currentTab === "skipped") {
    rowsToDisplay = rowsToDisplay.filter(r => r.status.includes("Skipped"));
  } else if (currentTab === "failed") {
    rowsToDisplay = rowsToDisplay.filter(r => r.status === "Failed");
  }
  
  // Filter based on search input
  if (searchVal) {
    rowsToDisplay = rowsToDisplay.filter(r => 
      r.origin.toLowerCase().includes(searchVal) ||
      r.destination.toLowerCase().includes(searchVal) ||
      r.company.toLowerCase().includes(searchVal) ||
      r.equipment.toLowerCase().includes(searchVal) ||
      r.docket.toLowerCase().includes(searchVal) ||
      r.dot.toLowerCase().includes(searchVal)
    );
  }
  
  if (rowsToDisplay.length === 0) {
    tbody.innerHTML = `<tr><td colspan="12" style="text-align: center; padding: 40px; color: var(--text-disabled);">No records match criteria.</td></tr>`;
    return;
  }
  
  // Render
  tbody.innerHTML = rowsToDisplay.map(r => {
    let badgeClass = "badge-success";
    if (r.status.includes("Skipped")) badgeClass = "badge-skipped";
    else if (r.status === "Failed") badgeClass = "badge-failed";
    
    return `
      <tr>
        <td><span class="badge-status ${badgeClass}">${r.status}</span></td>
        <td><strong>${r.origin}</strong></td>
        <td><strong>${r.destination}</strong></td>
        <td>${r.age}</td>
        <td class="text-primary" style="font-weight:600;">${r.rate}</td>
        <td>${r.rpm}</td>
        <td>${r.trip}</td>
        <td>${r.company}</td>
        <td><span style="background: rgba(255,255,255,0.04); padding: 2px 6px; border-radius: 4px;">${r.equipment}</span></td>
        <td style="color: var(--primary); font-weight:600;">${r.docket}</td>
        <td>${r.dot}</td>
        <td style="color: var(--text-disabled); font-size: 11px;">${r.timestamp}</td>
      </tr>
    `;
  }).join("");
}

// Helper to format time
function formatTime(isoStr) {
  try {
    const d = new Date(isoStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  } catch (e) {
    return isoStr;
  }
}

// ── Update logs console ──
async function updateLogs() {
  const now = Date.now();
  const gap = isCrawlerRunning ? POLL_ACTIVE_MS : POLL_IDLE_MS;
  if (now - lastLogPoll < gap) return;
  lastLogPoll = now;

  try {
    const res = await fetch(`${API_BASE}/logs`);
    if (!res.ok) return;
    
    const logs = await res.json();
    if (!logs || logs.length === 0) return;
    
    const consoleWindow = $("consoleWindow");
    
    // Find index of first new log line based on timestamp/content match
    let startIdx = 0;
    if (lastLogTimestamp) {
      startIdx = logs.findIndex(l => l.timestamp > lastLogTimestamp);
      if (startIdx === -1) {
        // All logs are old
        return;
      }
    }
    
    // Append new logs
    const newLogs = logs.slice(startIdx);
    if (newLogs.length === 0) return;
    
    lastLogTimestamp = logs[logs.length - 1].timestamp;
    
    let htmlContent = startIdx === 0 ? "" : consoleWindow.innerHTML;
    
    newLogs.forEach(l => {
      let typeColor = "text-primary";
      if (l.event_type.includes("ALERT") || l.event_type.includes("ERROR") || l.event_type.includes("FAILED")) {
        typeColor = "text-danger";
      } else if (l.event_type.includes("SCALE") || l.event_type.includes("THRESHOLD")) {
        typeColor = "text-warning";
      } else if (l.event_type.includes("SAVED") || l.event_type.includes("COMPLETED")) {
        typeColor = "text-accent";
      }
      
      const timeStr = l.timestamp.split(' ')[1] || l.timestamp;
      
      htmlContent += `
        <div class="log-line">
          <span class="log-time">[${timeStr}]</span>
          <span class="log-type ${typeColor}">[${l.event_type}]</span>
          <span class="log-content">${JSON.stringify(l.details)}</span>
        </div>
      `;
    });
    
    consoleWindow.innerHTML = htmlContent;
    consoleWindow.scrollTop = consoleWindow.scrollHeight;
  } catch (err) {
    console.warn("Logs load error:", err);
  }
}

// ── Event listeners setup ──
function setupEventListeners() {
  // Search input
  $("searchInput").addEventListener("input", renderTable);
  
  // Tabs switching
  $("tabAll").addEventListener("click", () => switchTab("all"));
  $("tabSuccessful").addEventListener("click", () => switchTab("successful"));
  $("tabSkipped").addEventListener("click", () => switchTab("skipped"));
  $("tabFailed").addEventListener("click", () => switchTab("failed"));
  
  // Export scope options selection
  $("scopeAll").addEventListener("click", () => selectExportScope("all"));
  $("scopeSuccess").addEventListener("click", () => selectExportScope("success"));
  $("scopeSkipped").addEventListener("click", () => selectExportScope("skipped"));
  $("scopeFailed").addEventListener("click", () => selectExportScope("failed"));
  
  // Export downloads action triggers
  $("exportXlsxBtn").addEventListener("click", () => triggerExport("xlsx"));
  $("exportJsonBtn").addEventListener("click", () => triggerExport("json"));
  $("exportCsvBtn").addEventListener("click", () => triggerExport("csv"));
  $("exportTxtBtn").addEventListener("click", () => triggerExport("txt"));
  
  // Stop Crawler btn action trigger
  $("stopCrawlerBtn").addEventListener("click", async () => {
    if (confirm("Are you sure you want to stop the crawler? This will terminate all active crawl threads.")) {
      try {
        await fetch(`${API_BASE}/stop_try`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ try_id: tryId })
        });
        // Let chrome runtime stop locally too
        if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.sendMessage) {
          chrome.runtime.sendMessage({ action: "stopAll" }).catch(() => {});
        }
        updateStatus();
      } catch (err) {
        alert("Failed to stop crawler: " + err.message);
      }
    }
  });

  // Resume Crawler btn action trigger
  if ($("resumeCrawlerBtn")) {
    $("resumeCrawlerBtn").addEventListener("click", async () => {
      try {
        const res = await fetch(`${API_BASE}/resume`, { method: "POST" });
        const data = await res.json();
        if (data.success) {
          // Send message to background script to trigger orchestration
          chrome.runtime.sendMessage({ action: "triggerOrchestration" }).catch(() => {});
          updateStatus();
        } else {
          alert("Failed to resume crawler: " + data.error);
        }
      } catch (err) {
        alert("Failed to resume crawler: " + err.message);
      }
    });
  }
}

function switchTab(tabId) {
  document.querySelectorAll(".filter-tab").forEach(t => t.classList.remove("active"));
  $(`tab${tabId.charAt(0).toUpperCase() + tabId.slice(1)}`).classList.add("active");
  currentTab = tabId;
  renderTable();
}

function selectExportScope(scopeId) {
  document.querySelectorAll(".export-scope-btn").forEach(b => b.classList.remove("active"));
  $(`scope${scopeId.charAt(0).toUpperCase() + scopeId.slice(1)}`).classList.add("active");
  currentExportScope = scopeId;
}

async function triggerExport(format) {
  if (!tryId) {
    alert("No active session results available to export.");
    return;
  }
  try {
    const downloadUrl = `${API_BASE}/export?try_id=${tryId}&type=${currentExportScope}&format=${format}`;
    const res = await fetch(downloadUrl);
    if (!res.ok) throw new Error("Export failed on server.");
    const blob = await res.blob();
    
    const url = URL.createObjectURL(blob);
    const filename = `dat-export-${currentExportScope}-${tryId.slice(0, 8)}-${Date.now()}.${format}`;
    if (typeof chrome !== "undefined" && chrome.downloads && chrome.downloads.download) {
      chrome.downloads.download({
        url: url,
        filename: filename,
        saveAs: true
      }, () => {
        setTimeout(() => URL.revokeObjectURL(url), 10000);
      });
    } else {
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }
  } catch (err) {
    alert("Export failed: " + err.message);
  }
}

// Start up
document.addEventListener("DOMContentLoaded", initDashboard);

// ── Background Keep-Alive Connection ──
let keepAlivePort = null;
function connectKeepAlive() {
  if (typeof chrome === "undefined" || !chrome.runtime || !chrome.runtime.connect) return;
  try {
    keepAlivePort = chrome.runtime.connect({ name: "keepAlive" });
    keepAlivePort.onDisconnect.addListener(() => {
      keepAlivePort = null;
      setTimeout(connectKeepAlive, 5000);
    });
  } catch (err) {
    console.warn("Failed to connect keep-alive port:", err);
  }
}

setInterval(() => {
  if (keepAlivePort) {
    try {
      keepAlivePort.postMessage({ ping: true });
    } catch (e) {
      keepAlivePort = null;
      connectKeepAlive();
    }
  }
}, 15000);
