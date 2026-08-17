let extractedText = "";
let extractedCSV = "";
let extractedJSON = "";
let extractedLoads = [];      // flat records, as the content script produced them
let extractedRecords = [];    // nested { load: {...}, extraction: {...} } records
const $ = (id) => document.getElementById(id);

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

const DEFAULT_DEEP_OPTIONS = { enabled: true, maxDepth: 3, maxClicks: 26, retries: 1 };

const DEFAULT_STATE = {
  isExtracting: false,
  isAutopilotRunning: false,
  isStopping: false,
  speedMode: "normal",
  manualProgress: null,
  autopilotProgress: null,
  deepProgress: null,
  deepOptions: { ...DEFAULT_DEEP_OPTIONS },
  activeTabs: []
};

// ── Centralized State Manager ──
async function getStoredState() {
  const data = await chrome.storage.local.get("dat_extractor_state");
  return data.dat_extractor_state || { ...DEFAULT_STATE };
}

async function updateStoredState(changes) {
  const state = await getStoredState();
  const newState = { ...state, ...changes };
  await chrome.storage.local.set({ dat_extractor_state: newState });
  return newState;
}

// ── State-driven UI sync ──
function syncUI(state) {
  // 1. Handle width for side panel
  if (window.location.search.includes('panel=true')) {
    document.body.style.width = '100%';
  }

  // 2. Active Speed Mode Button
  document.querySelectorAll(".speed-btn").forEach(btn => btn.classList.remove("active"));
  if (state.speedMode === "ultra") {
    $("speedUltra").classList.add("active");
  } else if (state.speedMode === "fast") {
    $("speedFast").classList.add("active");
  } else {
    $("speedNormal").classList.add("active");
  }

  // 2b. Deep extraction controls
  const deep = state.deepOptions || DEFAULT_DEEP_OPTIONS;
  if ($("deepOn") && $("deepOff")) {
    $("deepOn").classList.toggle("active", deep.enabled !== false);
    $("deepOff").classList.toggle("active", deep.enabled === false);
  }
  if ($("deepConfigRow")) {
    $("deepConfigRow").style.opacity = deep.enabled === false ? "0.4" : "1";
    $("deepConfigRow").style.pointerEvents = deep.enabled === false ? "none" : "auto";
  }
  if ($("deepDepth") && document.activeElement !== $("deepDepth")) $("deepDepth").value = deep.maxDepth ?? 3;
  if ($("deepClicks") && document.activeElement !== $("deepClicks")) $("deepClicks").value = deep.maxClicks ?? 26;
  if ($("deepRetries") && document.activeElement !== $("deepRetries")) $("deepRetries").value = deep.retries ?? 1;

  renderDeepProgress(state.deepProgress);

  // 3. Global Stop Button Panel Visibility
  const isCurrentlyWorking = state.isExtracting || state.isAutopilotRunning;
  if (isCurrentlyWorking && !state.isStopping) {
    $("globalStopPanel").classList.remove("hidden");
    $("globalStopBtn").removeAttribute("disabled");
    $("globalStopBtn").textContent = "Stop All Operations";
  } else if (state.isStopping) {
    $("globalStopPanel").classList.remove("hidden");
    $("globalStopBtn").setAttribute("disabled", "true");
    $("globalStopBtn").textContent = "Stopping all threads...";
  } else {
    $("globalStopPanel").classList.add("hidden");
  }

  // Disable button clicks if busy or not on DAT page
  const isBusy = state.isExtracting || state.isAutopilotRunning || state.isStopping;
  const isReadyPage = $("statusDot").classList.contains("ok");
  const isAutopilotActive = state.isAutopilotRunning && !state.isStopping;

  $("extractBtn").disabled = isBusy || !isReadyPage;

  // Resume button visibility: only if we have an active try that is not completed and we are not running
  const hasResumableSession = state.autopilotProgress && 
                             state.autopilotProgress.tryId && 
                             state.autopilotProgress.tryId !== 'Starting...' && 
                             state.autopilotProgress.status !== 'completed';

  if (hasResumableSession && !state.isAutopilotRunning && !state.isStopping) {
    $("resumeAutoBtn").classList.remove("hidden");
    $("resumeAutoBtn").disabled = !isReadyPage;
  } else {
    $("resumeAutoBtn").classList.add("hidden");
  }

  $("startAutoBtn").disabled = isBusy || !isReadyPage;
  
  if ($("stopAutoBtn")) {
    $("stopAutoBtn").disabled = !isAutopilotActive;
    if (state.isStopping) {
      $("stopAutoBtn").textContent = "Stopping...";
    } else {
      $("stopAutoBtn").textContent = "Stop";
    }
  }

  if (isBusy) {
    $("extractBtn").classList.add("disabled");
    if ($("startAutoBtn")) $("startAutoBtn").classList.add("disabled");
  } else {
    $("extractBtn").classList.remove("disabled");
    if ($("startAutoBtn")) $("startAutoBtn").classList.remove("disabled");
  }
  
  if ($("stopAutoBtn")) {
    if (isAutopilotActive) $("stopAutoBtn").classList.remove("disabled");
    else $("stopAutoBtn").classList.add("disabled");
  }

  // 4. Manual Progress Display
  if (state.isExtracting && state.manualProgress) {
    $("loadingState").classList.remove("hidden");
    $("actionPanel").classList.add("hidden");

    const { collected, target, step, maxSteps, duplicates } = state.manualProgress;
    const targetTxt = target ? ` / ~${target}` : "";
    const dupTxt = duplicates ? ` (Duplicates: ${duplicates})` : "";
    $("loadingMsg").textContent = `Extracting: ${collected}${targetTxt} loads${dupTxt} [Scroll step ${step}/${maxSteps}]`;
  } else if (!state.isExtracting) {
    $("loadingState").classList.add("hidden");
    $("actionPanel").classList.remove("hidden");
  }

  // 5. Autopilot Progress Monitor
  if (state.autopilotProgress && state.autopilotProgress.tryId) {
    $("walProgress").classList.remove("hidden");
    const stat = state.autopilotProgress;
    $("walTryId").textContent = stat.tryId ? (stat.tryId.slice(0, 8) + "…") : "-";
    $("walTryId").title = stat.tryId || "";
    
    // Status text (indicate paused if cancelled/stopped)
    let statusLabel = stat.status ? stat.status.toUpperCase() : "-";
    if (statusLabel === "CANCELLED" || statusLabel === "STOPPED") {
      statusLabel = "PAUSED / STOPPED";
    }
    $("walState").textContent = statusLabel;
    
    $("walCompleted").textContent = stat.completed || 0;
    $("walTotal").textContent = stat.total || 0;
    
    if (stat.tasks) {
      $("walPending").textContent = stat.tasks.remaining || stat.pending || 0;
      $("walInProgress").textContent = stat.tasks.running || stat.inProgress || 0;
    } else {
      $("walPending").textContent = stat.pending || 0;
      $("walInProgress").textContent = stat.inProgress || 0;
    }

    const fillPercent = stat.total > 0 ? (stat.completed / stat.total) * 100 : 0;
    const fillEl = $("walProgressBarFill");
    if (fillEl) fillEl.style.width = `${fillPercent}%`;

    // Show/hide spinning animation based on running state
    const headerSvg = $("walProgress").querySelector(".progress-header svg");
    if (headerSvg) {
      if (state.isAutopilotRunning && !state.isStopping) {
        headerSvg.style.animation = "spin 3s linear infinite";
      } else {
        headerSvg.style.animation = "none";
      }
    }

    if (stat.status === "completed") {
      $("mergeBtn").style.display = "block";
    } else {
      $("mergeBtn").style.display = "none";
    }

    // Show export options for Autopilot if we have completed batches/data
    if (stat.completed > 0) {
      $("walExportSection").classList.remove("hidden");
    } else {
      $("walExportSection").classList.add("hidden");
    }
  } else {
    $("walProgress").classList.add("hidden");
  }
}

// ── Deep extraction progress board ──
function renderDeepProgress(dp) {
  const panel = $("deepProgressPanel");
  if (!panel) return;
  if (!dp || !dp.total) {
    panel.classList.add("hidden");
    return;
  }
  panel.classList.remove("hidden");

  const set = (id, v) => { const el = $(id); if (el) el.textContent = String(v ?? 0); };
  set("dpTotal", dp.total);
  set("dpTotalB", dp.total);
  set("dpProcessed", dp.processed);
  set("dpComplete", dp.complete);
  set("dpPartial", dp.partial);
  set("dpFailed", dp.failed);
  set("dpFields", dp.fields);
  set("dpRetries2", dp.retries);

  const fill = $("dpBarFill");
  if (fill) {
    const pct = dp.total > 0 ? Math.min(100, (dp.processed / dp.total) * 100) : 0;
    fill.style.width = `${pct}%`;
  }

  const cur = $("dpCurrent");
  if (cur) {
    cur.textContent = dp.current ? `Now: ${dp.current}` : "";
    cur.title = dp.current || "";
  }

  const secs = $("dpSections");
  if (secs) {
    const list = dp.sections || [];
    secs.innerHTML = list.length
      ? list.map((s) => `<span style="color:var(--accent);">&#10003;</span> ${escapeHtml(s)}`).join("<br>")
      : "";
  }
}

/**
 * RFC-4180 CSV reader. Values may contain commas, quotes and newlines
 * (office addresses do), so a naive split would corrupt the sheet.
 */
function parseCsv(text) {
  const rows = [];
  if (!text) return rows;
  let row = [];
  let field = "";
  let inQuotes = false;

  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (inQuotes) {
      if (ch === '"') {
        if (text[i + 1] === '"') { field += '"'; i++; }
        else inQuotes = false;
      } else {
        field += ch;
      }
      continue;
    }
    if (ch === '"') { inQuotes = true; continue; }
    if (ch === ",") { row.push(field); field = ""; continue; }
    if (ch === "\n") { row.push(field); rows.push(row); row = []; field = ""; continue; }
    if (ch === "\r") continue;
    field += ch;
  }
  if (field !== "" || row.length) { row.push(field); rows.push(row); }
  return rows;
}

function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
  ));
}

// ── Load Inspector ──
// Lets Boss verify, load by load, exactly what the deep pass captured — and
// which sections it visited or failed on. This is the acceptance check.
const INSPECTOR_GROUPS = [
  ["Load Summary", "summary"],
  ["Load Details", "details"],
  ["Route", "route"],
  ["Truck / Equipment", "truck"],
  ["Rate", "rate"],
  ["Company", "company"],
  ["Contact", "contact"],
  ["Office", "office"],
  ["Additional Data", "additionalData"]
];

function inspectorLabel(rec, idx) {
  const s = rec?.load?.summary || {};
  const status = rec?.extraction?.status || "n/a";
  const marks = { complete: "✓", partial: "○", failed: "✗", pending: "…" };
  const mark = marks[status] || "·";
  const route = `${s.origin || "?"} → ${s.destination || "?"}`;
  return `${mark} #${s.listIndex ?? idx + 1}  ${route}  ·  ${s.company || "Unknown"}`;
}

function renderKeyValues(obj) {
  if (!obj || typeof obj !== "object") return `<div style="color:var(--text-disabled);">no data</div>`;
  const rows = [];
  for (const [k, v] of Object.entries(obj)) {
    if (v == null) continue;
    let display;
    if (Array.isArray(v)) {
      if (!v.length) continue;
      display = v.map((item) => (typeof item === "object" ? JSON.stringify(item) : String(item))).join("<br>");
    } else if (typeof v === "object") {
      const inner = Object.entries(v).filter(([, x]) => x != null && x !== "");
      if (!inner.length) continue;
      display = inner.map(([a, b]) => `${escapeHtml(a)}: ${escapeHtml(String(b))}`).join("<br>");
    } else {
      if (String(v).trim() === "") continue;
      display = escapeHtml(String(v));
    }
    rows.push(
      `<div style="display:flex;gap:8px;padding:2px 0;border-bottom:1px solid rgba(255,255,255,.04);">` +
      `<span style="flex:0 0 40%;color:var(--text-muted);">${escapeHtml(k)}</span>` +
      `<span style="flex:1;color:var(--text);word-break:break-word;">${display}</span></div>`
    );
  }
  if (!rows.length) return `<div style="color:var(--text-disabled);">no data captured</div>`;
  return rows.join("");
}

function renderInspectorBody(rec) {
  const body = $("inspectorBody");
  if (!body) return;
  if (!rec) {
    body.innerHTML = `<div style="color:var(--text-disabled);">Run an extraction to inspect a load.</div>`;
    return;
  }

  const parts = [];
  for (const [title, key] of INSPECTOR_GROUPS) {
    const data = rec.load ? rec.load[key] : null;
    parts.push(
      `<div style="margin-bottom:10px;">` +
      `<div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--primary);margin-bottom:4px;">${escapeHtml(title)}</div>` +
      renderKeyValues(data) + `</div>`
    );
  }

  const ex = rec.extraction;
  if (ex) {
    const meta = {
      status: ex.status,
      fieldsExtracted: ex.fieldsExtracted,
      retries: ex.retries,
      sectionsVisited: ex.sectionsVisited,
      sectionsFailed: ex.sectionsFailed,
      linksVisited: (ex.linksVisited || []).map((l) => `${l.label} (+${l.newFields})`),
      stages: (ex.stages || []).map((s) => `${s.stage}: +${s.fields} fields, ${s.clicks} reveals, ${s.durationMs}ms`),
      warnings: ex.warnings,
      errors: (ex.errors || []).map((e) => `${e.stage}: ${e.message}`)
    };
    parts.push(
      `<div style="margin-bottom:10px;">` +
      `<div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--primary);margin-bottom:4px;">Extraction Metadata</div>` +
      renderKeyValues(meta) + `</div>`
    );
  }

  body.innerHTML = parts.join("");
}

function renderInspector() {
  const panel = $("inspectorPanel");
  const select = $("inspectorSelect");
  if (!panel || !select) return;

  if (!extractedRecords.length) {
    panel.classList.add("hidden");
    return;
  }
  panel.classList.remove("hidden");

  select.innerHTML = extractedRecords
    .map((rec, i) => `<option value="${i}">${escapeHtml(inspectorLabel(rec, i))}</option>`)
    .join("");
  select.onchange = () => renderInspectorBody(extractedRecords[Number(select.value)] || null);
  renderInspectorBody(extractedRecords[0]);
}

// ── Deep extraction control wiring ──
async function setDeepOption(patch) {
  const state = await getStoredState();
  const next = { ...DEFAULT_DEEP_OPTIONS, ...(state.deepOptions || {}), ...patch };
  await updateStoredState({ deepOptions: next });
  syncUI(await getStoredState());
}

if ($("deepOn")) $("deepOn").addEventListener("click", () => setDeepOption({ enabled: true }));
if ($("deepOff")) $("deepOff").addEventListener("click", () => setDeepOption({ enabled: false }));
if ($("deepDepth")) {
  $("deepDepth").addEventListener("change", (e) => setDeepOption({ maxDepth: parseInt(e.target.value, 10) || 3 }));
}
if ($("deepClicks")) {
  $("deepClicks").addEventListener("change", (e) => {
    const v = parseInt(e.target.value, 10);
    setDeepOption({ maxClicks: Number.isFinite(v) ? v : 26 });
  });
}
if ($("deepRetries")) {
  $("deepRetries").addEventListener("change", (e) => {
    const v = parseInt(e.target.value, 10);
    setDeepOption({ retries: Number.isFinite(v) ? v : 1 });
  });
}

// Check if tab is on DAT One search loads page or OmniScraper tab is active
async function checkPage() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const isOmniTab = $("tabOmni") && $("tabOmni").classList.contains("active");

    if (isOmniTab) {
      $("statusDot").className = "dot ok";
      $("statusText").textContent = "Ready for OmniScraper";
      if ($("extractOmniBtn")) $("extractOmniBtn").disabled = false;
    } else if (tab?.url?.includes("dat.com")) {
      $("statusDot").className = "dot ok";
      $("statusText").textContent = "Ready on DAT One Search";

      const state = await getStoredState();
      const isBusy = state.isExtracting || state.isAutopilotRunning || state.isStopping;
      $("extractBtn").disabled = isBusy;
      if ($("startAutoBtn")) $("startAutoBtn").disabled = isBusy;
    } else {
      $("statusDot").className = "dot";
      $("statusText").textContent = "Open one.dat.com search loads first";
      $("extractBtn").disabled = true;
      if ($("startAutoBtn")) $("startAutoBtn").disabled = true;
    }
  } catch {
    $("statusText").textContent = "Cannot detect active tab";
  }
}

// Start manual extraction
async function runExtract() {
  const state = await getStoredState();
  if (state.isExtracting || state.isAutopilotRunning || state.isStopping) return;

  await chrome.storage.local.remove("manual_extracted_data");

  $("exportPanel").classList.add("hidden");
  $("resultsPanel").classList.add("hidden");
  $("errorMsg").classList.add("hidden");
  $("preview").classList.add("hidden");

  await updateStoredState({
    isExtracting: true,
    manualProgress: {
      collected: 0,
      target: 0,
      step: 0,
      maxSteps: 0,
      duplicates: 0
    }
  });

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) throw new Error("No active tab found");

    // Inject scripts manually to ensure they are loaded and up to date
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ["xlsx.full.min.js", "deep-extract.js", "content.js"],
    });
    await new Promise((r) => setTimeout(r, 200));

    // Send extraction trigger message passing the current speed mode
    const response = await chrome.tabs.sendMessage(tab.id, {
      action: "extractLoads",
      speedMode: state.speedMode,
      deep: state.deepOptions || DEFAULT_DEEP_OPTIONS
    });

    await updateStoredState({ isExtracting: false, manualProgress: null });

    if (!response?.success) {
      showError(response?.error || "Extraction was skipped or failed.");
      return;
    }

    extractedText = response.text;
    extractedCSV = response.csv;
    extractedLoads = response.loads || [];
    extractedRecords = response.records || [];
    extractedJSON = JSON.stringify({
      exportDate: new Date().toISOString(),
      criteria: response.criteria,
      loads: response.loads,
      // Nested, loss-free per-load records (summary + details + route + truck +
      // company + contact + office + rate + additionalData + extraction).
      records: response.records || null,
      summary: {
        totalExtracted: response.count,
        targetTotal: response.targetTotal,
        emptyCount: response.emptyCount,
        skipped: response.skipped,
        deep: response.deepStats || null
      }
    }, null, 2);

    renderInspector();

    await chrome.storage.local.set({
      manual_extracted_data: {
        text: extractedText,
        csv: extractedCSV,
        json: extractedJSON,
        count: response.count,
        targetTotal: response.targetTotal,
        emptyCount: response.emptyCount,
        skipped: response.skipped
      }
    });

    let label = String(response.count);
    if (response.targetTotal) {
      label =
        response.count === response.targetTotal
          ? `${response.count} ✓`
          : `${response.count} / ~${response.targetTotal}`;
    }
    $("loadCount").textContent = label;
    $("emptyCount").textContent = String(response.emptyCount || 0);
    $("skippedCount").textContent = String(response.skipped || 0);
    $("pageTotal").textContent = response.targetTotal ? `~${response.targetTotal}` : "–";

    $("resultsPanel").classList.remove("hidden");
    $("exportPanel").classList.remove("hidden");
    $("preview").classList.remove("hidden");
    $("preview").textContent =
      extractedText.slice(0, 1800) + (extractedText.length > 1800 ? "\n…" : "");

    if (response.cancelled) {
      showError("Cancelled. Partial export saved — run again if needed.");
    } else if (response.incomplete) {
      showError(
        `Scraped ${response.count} of ~${response.targetTotal} loads. ` +
        "DAT virtual scroll was recycled. Refresh DAT page and re-extract if required."
      );
    }
  } catch (err) {
    await updateStoredState({ isExtracting: false, manualProgress: null });
    showError(err.message || "Failed to communicate with content script. Refresh the tab and retry.");
  }
}

function showError(msg) {
  $("errorMsg").querySelector("span").textContent = msg;
  $("errorMsg").classList.remove("hidden");
}

function download(content, filename, mime) {
  const blob = content instanceof Blob ? content : new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
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
}

async function copy(text, btn) {
  try {
    await navigator.clipboard.writeText(text);
    const oldHtml = btn.innerHTML;
    btn.innerHTML = `<svg viewBox="0 0 24 24" style="width:16px;height:16px;stroke:var(--accent);fill:none;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg> Copied!`;
    setTimeout(() => (btn.innerHTML = oldHtml), 1500);
  } catch (err) {
    showError("Clipboard copy failed.");
  }
}

// ── Event Listeners ──
$("extractBtn").addEventListener("click", runExtract);

$("globalStopBtn").addEventListener("click", async () => {
  $("globalStopBtn").disabled = true;
  $("globalStopBtn").textContent = "Stopping all threads...";
  await updateStoredState({ isStopping: true });
  chrome.runtime.sendMessage({ action: "stopAll" }).catch(() => { });
});

if ($("stopAutoBtn")) {
  $("stopAutoBtn").addEventListener("click", async () => {
    $("stopAutoBtn").disabled = true;
    $("stopAutoBtn").textContent = "Stopping...";
    await updateStoredState({ isStopping: true });
    chrome.runtime.sendMessage({ action: "stopAll" }).catch(() => { });
  });
}

async function setSpeed(mode) {
  await updateStoredState({ speedMode: mode });
  const state = await getStoredState();
  syncUI(state);
}

$("speedNormal").addEventListener("click", () => setSpeed("normal"));
$("speedFast").addEventListener("click", () => setSpeed("fast"));
$("speedUltra").addEventListener("click", () => setSpeed("ultra"));

$("copyTextBtn").addEventListener("click", () => copy(extractedText, $("copyTextBtn")));
$("copyCSVBtn").addEventListener("click", () => copy(extractedCSV, $("copyCSVBtn")));
$("copyJsonBtn").addEventListener("click", () => copy(extractedJSON, $("copyJsonBtn")));

// Tab switching
$("tabManual").addEventListener("click", () => {
  $("tabManual").classList.add("active");
  $("tabAuto").classList.remove("active");
  $("tabOmni").classList.remove("active");
  $("viewManual").classList.remove("hidden");
  $("viewAuto").classList.add("hidden");
  $("viewOmni").classList.add("hidden");
  checkPage();
});
$("tabAuto").addEventListener("click", () => {
  $("tabAuto").classList.add("active");
  $("tabManual").classList.remove("active");
  $("tabOmni").classList.remove("active");
  $("viewAuto").classList.remove("hidden");
  $("viewManual").classList.add("hidden");
  $("viewOmni").classList.add("hidden");
  checkPage();
});
$("tabOmni").addEventListener("click", () => {
  $("tabOmni").classList.add("active");
  $("tabManual").classList.remove("active");
  $("tabAuto").classList.remove("active");
  $("viewOmni").classList.remove("hidden");
  $("viewManual").classList.add("hidden");
  $("viewAuto").classList.add("hidden");
  checkPage();
});

async function runExtractOmni() {
  $("exportPanel").classList.add("hidden");
  $("resultsPanel").classList.add("hidden");
  $("errorMsg").classList.add("hidden");
  $("preview").classList.add("hidden");
  $("extractOmniBtn").disabled = true;
  $("extractOmniBtn").textContent = "Extracting Page...";

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) throw new Error("No active tab found");

    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ["xlsx.full.min.js", "deep-extract.js", "content.js"],
    });
    await new Promise((r) => setTimeout(r, 200));

    const response = await chrome.tabs.sendMessage(tab.id, {
      action: "extractOmniPage"
    });

    if (!response?.success) {
      showError(response?.error || "OmniScraper failed.");
      return;
    }

    extractedText = response.text;
    extractedCSV = response.csv;
    extractedJSON = response.json;
    extractedLoads = [];
    extractedRecords = [];
    renderInspector();

    await chrome.storage.local.set({
      manual_extracted_data: {
        text: extractedText,
        csv: extractedCSV,
        json: extractedJSON,
        count: response.sections ? response.sections.reduce((acc, sec) => acc + sec.rows.length, 0) : 0,
        targetTotal: response.sections ? response.sections.length : 0,
        emptyCount: 0,
        skipped: 0
      }
    });

    $("loadCount").textContent = `${response.sections ? response.sections.reduce((acc, sec) => acc + sec.rows.length, 0) : 0} rows`;
    $("pageTotal").textContent = `${response.sections ? response.sections.length : 0} sections`;
    $("emptyCount").textContent = "0";
    $("skippedCount").textContent = "0";

    $("resultsPanel").classList.remove("hidden");
    $("exportPanel").classList.remove("hidden");
    $("preview").classList.remove("hidden");
    $("preview").textContent = extractedText.slice(0, 1800) + (extractedText.length > 1800 ? "\n…" : "");

  } catch (err) {
    showError(err.message || "Failed to extract page data.");
  } finally {
    $("extractOmniBtn").disabled = false;
    $("extractOmniBtn").textContent = "Extract Page Data";
  }
}

if ($("extractOmniBtn")) {
  $("extractOmniBtn").addEventListener("click", runExtractOmni);
}

// Fetch initial config and status
async function loadServerData() {
  try {
    const configRes = await fetch(`${API_BASE}/config`);
    if (configRes.ok) {
      const config = await configRes.json();
      if ($("cpuTabs")) $("cpuTabs").value = config.cpu_tabs || 1;
      if ($("ramBatchSize")) $("ramBatchSize").value = config.ram_batch_size || 5;
      if ($("cpuThreshold")) $("cpuThreshold").value = config.cpu_threshold || 85;
      if ($("maxRetries")) $("maxRetries").value = config.max_retries || 3;
    }

    const statRes = await fetch(`${API_BASE}/status`);
    if (statRes.ok) {
      const stat = await statRes.json();
      $("serverStatus").textContent = "Server Online";
      $("serverStatus").style.color = "var(--accent)";
      $("serverStatus").style.borderColor = "rgba(16, 185, 129, 0.2)";

      const state = await getStoredState();

      if (stat.active) {
        if (stat.status === "in_progress" && !state.isAutopilotRunning) {
          // Sync server status to local storage (self-healing)
          await updateStoredState({ 
            isAutopilotRunning: true,
            autopilotProgress: {
              tryId: stat.try_id,
              status: stat.status,
              completed: stat.completed,
              total: stat.total,
              pending: stat.pending,
              inProgress: stat.in_progress,
              lastUpdate: Date.now(),
              tasks: stat.tasks
            }
          });
        } else {
          // Sync server progress into local storage
          await updateStoredState({
            autopilotProgress: {
              tryId: stat.try_id,
              status: stat.status,
              completed: stat.completed,
              total: stat.total,
              pending: stat.pending,
              inProgress: stat.in_progress,
              lastUpdate: Date.now(),
              tasks: stat.tasks
            }
          });
        }
      } else {
        if (state.isAutopilotRunning) {
          // Stop locally since server is no longer active
          await updateStoredState({ isAutopilotRunning: false, autopilotProgress: null });
        }
        $("walProgress").classList.add("hidden");
      }
    }
  } catch (err) {
    $("serverStatus").textContent = "Server Offline (Run server.py)";
    $("serverStatus").style.color = "var(--danger)";
    $("serverStatus").style.borderColor = "rgba(244, 63, 94, 0.2)";
  }
}

if ($("saveConfigBtn")) {
  $("saveConfigBtn").addEventListener("click", async () => {
    try {
      await fetch(`${API_BASE}/config`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cpu_tabs: parseInt($("cpuTabs").value) || 1,
          ram_batch_size: parseInt($("ramBatchSize").value) || 5,
          cpu_threshold: parseInt($("cpuThreshold").value) || 85,
          max_retries: parseInt($("maxRetries").value) || 3
        })
      });
      const btn = $("saveConfigBtn");
      btn.textContent = "Saved!";
      setTimeout(() => btn.textContent = "Save Config", 1500);
    } catch (err) {
      showError("Failed to save config to server.");
    }
  });
}

if ($("mergeBtn")) {
  $("mergeBtn").addEventListener("click", async () => {
    try {
      const res = await fetch(`${API_BASE}/merge`, { method: "POST" });
      const data = await res.json();
      if (data.success) {
        showError(`Merged successfully! Saved: ${data.merged_file}`);
      } else {
        showError(data.error || "Merge failed.");
      }
    } catch (err) {
      showError("Merge failed: " + err.message);
    }
  });
}

$("startAutoBtn").addEventListener("click", async () => {
  const state = await getStoredState();
  if (state.isExtracting || state.isAutopilotRunning || state.isStopping) return;

  const states = $("autoStates").value.split(/,|\n/).map(s => s.trim()).filter(Boolean);
  const equipment = $("autoEquip").value.split(/,|\n/).map(s => s.trim()).filter(Boolean);
  const loadTypes = $("autoLoadType").value.split(/,|\n/).map(s => s.trim()).filter(Boolean);

  if (states.length < 2) {
    showError("Need at least 2 states for permutations.");
    return;
  }

  // Generate permutations grouped by route (Origin & Destination)
  const permutations = [];
  for (const origin of states) {
    for (const dest of states) {
      if (origin.toLowerCase() === dest.toLowerCase()) continue;
      for (const lt of loadTypes) {
        permutations.push({ origin, dest, equipment, lt });
      }
    }
  }

  try {
    // Capture active tab URL
    const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const targetUrl = activeTab?.url?.includes("dat.com")
      ? activeTab.url
      : "https://one.dat.com/search-loads";

    // Set state in storage first to prevent race conditions
    await updateStoredState({
      isAutopilotRunning: true,
      autopilotProgress: {
        tryId: "Starting...",
        status: "in_progress",
        completed: 0,
        total: 0,
        pending: 0,
        inProgress: 0,
        lastUpdate: Date.now()
      }
    });

    const res = await fetch(`${API_BASE}/start_try`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ permutations, target_url: targetUrl })
    });

    if (!res.ok) throw new Error("Server error");

    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    // Tell background orchestrator to start immediately
    chrome.runtime.sendMessage({ action: "triggerOrchestration" });

    showError(`Started Autopilot! ${permutations.length} permutations → ${data.total_batches} batches.`);
    loadServerData();
  } catch (err) {
    await updateStoredState({ isAutopilotRunning: false, autopilotProgress: null });
    showError("Error starting auto-pilot on server: " + err.message);
  }
});

// Download reports triggers
$("downloadTxtBtn").addEventListener("click", () => {
  download(extractedText, `dat-loads-${Date.now()}.txt`, "text/plain");
});
$("downloadCsvBtn").addEventListener("click", () => {
  download(extractedCSV, `dat-loads-${Date.now()}.csv`, "text/csv");
});
$("downloadJsonBtn").addEventListener("click", () => {
  download(extractedJSON, `dat-loads-${Date.now()}.json`, "application/json");
});

// High-fidelity Excel Exporter
const downloadXlsxBtn = $("downloadXlsxBtn");
if (downloadXlsxBtn) {
  downloadXlsxBtn.addEventListener("click", () => {
    if (typeof XLSX === "undefined") {
      showError("SheetJS (XLSX) library not loaded. Check popup.html dependencies.");
      return;
    }

    try {
      const exportData = JSON.parse(extractedJSON);
      
      if (exportData.source === "omni") {
        const wsRows = [];
        wsRows.push(["OMNISCRAPER PAGE REPORT"]);
        wsRows.push(["URL:", exportData.url]);
        wsRows.push(["Timestamp:", exportData.timestamp]);
        wsRows.push([]);

        exportData.sections.forEach(sec => {
          wsRows.push([sec.name.toUpperCase()]);
          sec.rows.forEach(row => {
            wsRows.push(row);
          });
          wsRows.push([]);
        });

        const ws = XLSX.utils.aoa_to_sheet(wsRows);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Page Sections Data");

        const colWidths = [];
        wsRows.forEach(r => {
          r.forEach((val, colIdx) => {
            const len = String(val || "").length;
            if (!colWidths[colIdx] || colWidths[colIdx].wch < len) {
              colWidths[colIdx] = { wch: Math.min(Math.max(len + 3, 10), 40) };
            }
          });
        });
        ws["!cols"] = colWidths;

        const wbout = XLSX.write(wb, { bookType: "xlsx", type: "array" });
        const blob = new Blob([wbout], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
        download(blob, `omni-report-${Date.now()}.xlsx`, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
        return;
      }

      const loads = exportData.loads || [];
      if (loads.length === 0) {
        showError("No loads available to export. Run extraction first.");
        return;
      }

      // The sheet is built from the CSV the content script already produced, so
      // Excel and CSV can never drift apart — deep columns included automatically.
      const table = parseCsv(extractedCSV);
      if (!table.length) {
        showError("Nothing to export — CSV payload was empty.");
        return;
      }
      const headers = table[0];
      const rows = table.slice(1);

      const wsData = [headers, ...rows];
      const ws = XLSX.utils.aoa_to_sheet(wsData);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, "DAT Extracted Loads");

      const colWidths = headers.map((h, i) => {
        let maxLen = h.length;
        rows.forEach(r => {
          const val = String(r[i] || "");
          if (val.length > maxLen) maxLen = val.length;
        });
        return { wch: Math.min(Math.max(maxLen + 3, 10), 30) };
      });
      ws["!cols"] = colWidths;

      const wbout = XLSX.write(wb, { bookType: "xlsx", type: "array" });
      const blob = new Blob([wbout], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
      download(blob, `dat-loads-report-${Date.now()}.xlsx`, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
    } catch (err) {
      showError("Excel Export Failed: " + err.message);
    }
  });
}

if ($("openDashboardBtn")) {
  $("openDashboardBtn").addEventListener("click", () => {
    chrome.tabs.create({ url: chrome.runtime.getURL("dashboard.html") });
  });
}

async function downloadAutopilotData(format) {
  const state = await getStoredState();
  const tryId = state.autopilotProgress?.tryId;
  if (!tryId) {
    showError("No active/previous autopilot session found.");
    return;
  }
  try {
    const url = `${API_BASE}/export?try_id=${tryId}&type=all&format=${format}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("Export failed on server.");
    const blob = await res.blob();
    
    let mime = "application/json";
    if (format === "csv") mime = "text/csv";
    if (format === "txt") mime = "text/plain";
    if (format === "xlsx") mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
    
    download(blob, `dat-autopilot-${tryId.slice(0, 8)}-${format}.${format}`, mime);
  } catch (err) {
    showError("Download failed: " + err.message);
  }
}

// Bind Autopilot export buttons
if ($("walDownloadTxtBtn")) {
  $("walDownloadTxtBtn").addEventListener("click", () => downloadAutopilotData("txt"));
}
if ($("walDownloadCsvBtn")) {
  $("walDownloadCsvBtn").addEventListener("click", () => downloadAutopilotData("csv"));
}
if ($("walDownloadJsonBtn")) {
  $("walDownloadJsonBtn").addEventListener("click", () => downloadAutopilotData("json"));
}
if ($("walDownloadXlsxBtn")) {
  $("walDownloadXlsxBtn").addEventListener("click", () => downloadAutopilotData("xlsx"));
}

// Bind Resume button
if ($("resumeAutoBtn")) {
  $("resumeAutoBtn").addEventListener("click", async () => {
    const state = await getStoredState();
    if (state.isExtracting || state.isAutopilotRunning || state.isStopping) return;

    try {
      const res = await fetch(`${API_BASE}/resume`, { method: "POST" });
      if (!res.ok) throw new Error("Server error");
      const data = await res.json();
      if (!data.success) throw new Error(data.error);

      await updateStoredState({
        isAutopilotRunning: true,
        isStopping: false
      });

      chrome.runtime.sendMessage({ action: "triggerOrchestration" });
      showError(`Resumed Autopilot session: ${data.try_id}`);
      loadServerData();
    } catch (err) {
      showError("Error resuming autopilot: " + err.message);
    }
  });
}

// ── Startup Initialization ──
chrome.storage.onChanged.addListener((changes, areaName) => {
  if (areaName === "local" && changes.dat_extractor_state) {
    syncUI(changes.dat_extractor_state.newValue);
  }
});

// Run initial checks and syncs
(async () => {
  const state = await getStoredState();
  syncUI(state);
  await checkPage();

  // Load persisted manual extraction data if any
  const storedManual = await chrome.storage.local.get("manual_extracted_data");
  if (storedManual.manual_extracted_data) {
    const data = storedManual.manual_extracted_data;
    extractedText = data.text;
    extractedCSV = data.csv;
    extractedJSON = data.json;

    // Recover the nested records so the inspector survives a popup reopen.
    try {
      const parsed = JSON.parse(extractedJSON || "{}");
      extractedLoads = parsed.loads || [];
      extractedRecords = parsed.records || [];
      renderInspector();
    } catch (e) {
      extractedLoads = [];
      extractedRecords = [];
    }

    let label = String(data.count);
    if (data.targetTotal) {
      label = data.count === data.targetTotal ? `${data.count} ✓` : `${data.count} / ~${data.targetTotal}`;
    }
    $("loadCount").textContent = label;
    $("emptyCount").textContent = String(data.emptyCount || 0);
    $("skippedCount").textContent = String(data.skipped || 0);
    $("pageTotal").textContent = data.targetTotal ? `~${data.targetTotal}` : "–";

    $("resultsPanel").classList.remove("hidden");
    $("exportPanel").classList.remove("hidden");
    $("preview").classList.remove("hidden");
    $("preview").textContent = extractedText.slice(0, 1800) + (extractedText.length > 1800 ? "\n…" : "");
  }

  await loadServerData();

  // Periodically refresh server data
  setInterval(loadServerData, 3000);

  // Establish background keep-alive connection
  connectKeepAlive();
})();

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
