const API_BASE = "http://127.0.0.1:5000";

// tabId -> { batchId, tryId, tasks, retries, startedAt }
const activeTabs = new Map();
const lastActiveTabPerWindow = new Map(); // windowId -> tabId
let targetMaxTabs = 1;
let currentMaxTabs = 1;
let cpuThreshold = 85;
let cpuThrottled = false;
let isOrchestrating = false;

const DEFAULT_STATE = {
  isExtracting: false,
  isAutopilotRunning: false,
  isStopping: false,
  speedMode: "normal",
  manualProgress: null,
  autopilotProgress: null,
  deepProgress: null,
  deepOptions: { enabled: true, maxDepth: 3, maxClicks: 26, retries: 1 },
  activeTabs: []
};

// ── State Manager ──
// ── Task Registry Stubs (No-Op) ──
async function updateTaskStates(tasks, newState) {}
async function resetNonCompletedTasks() {}

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

// ── Event logger (writes to events.log on the server) ──
function logEvent(eventType, details) {
  fetch(`${API_BASE}/log_event`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ event_type: eventType, details })
  }).catch(() => {}); // Fire-and-forget, never block on this
}

async function fetchWithTimeout(resource, options = {}) {
  const { timeout = 8000 } = options;
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  try {
    const response = await fetch(resource, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(id);
    return response;
  } catch (err) {
    clearTimeout(id);
    throw err;
  }
}

// ── Config ──
async function fetchConfig() {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/config`);
    if (res.ok) {
      const config = await res.json();
      if (config.cpu_tabs) targetMaxTabs = Number(config.cpu_tabs);
      if (config.cpu_threshold) cpuThreshold = Number(config.cpu_threshold);
    }
  } catch (err) {
    logEvent("CONFIG_ERROR", { error: String(err) });
  }
}

// ── Inject scripts into a tab and wait for them to be ready ──
async function waitForContentScriptReady(tabId, timeoutMs = 25000) {
  const start = Date.now();
  let injectedFallback = false;

  while (Date.now() - start < timeoutMs) {
    const state = await getStoredState();
    if (!state.isAutopilotRunning || state.isStopping) {
      throw new Error("Autopilot stopped during handshake");
    }

    // Check if redirected to login page
    try {
      const tab = await chrome.tabs.get(tabId);
      if (tab?.url && (tab.url.includes("login.dat.com") || tab.url.includes("/login"))) {
        logEvent("REDIRECTED_TO_LOGIN", { tabId, url: tab.url });
        throw new Error("Redirected to login page. Please log in to DAT ONE.");
      }
    } catch (e) {
      if (e && e.message && e.message.includes("Redirected to login")) {
        throw e;
      }
    }

    try {
      const res = await chrome.tabs.sendMessage(tabId, { action: "ping" });
      if (res && res.ok) {
        logEvent("HANDSHAKE_SUCCESS", { tabId });
        return true;
      }
    } catch (e) {
      // Ignored: content script not yet loaded or listening
    }

    // Fallback: if 5 seconds have passed and still no response, try programmatic injection
    if (Date.now() - start > 5000 && !injectedFallback) {
      injectedFallback = true;
      try {
        const tab = await chrome.tabs.get(tabId);
        if (tab?.status === "complete" && !tab.url.includes("login.dat.com") && !tab.url.includes("/login")) {
          logEvent("INJECTION_FALLBACK_TRIGGERED", { tabId, url: tab.url });
          await chrome.scripting.executeScript({
            target: { tabId },
            files: ["xlsx.full.min.js", "deep-extract.js", "content.js"]
          });
        }
      } catch (err) {
        logEvent("INJECTION_FALLBACK_FAILED", { tabId, error: String(err) });
      }
    }

    await new Promise(r => setTimeout(r, 500));
  }
  throw new Error(`Handshake timeout: Content script did not respond within ${timeoutMs}ms`);
}

// ── Send batch to content script with retries ──
function sendBatchWithRetry(tabId, batchId, tryId, tasks, speedMode, attempts = 0, deepOptions = null) {
  chrome.storage.local.get("dat_extractor_state").then(async (data) => {
    const state = data.dat_extractor_state || {};
    if (state.isStopping || !state.isAutopilotRunning) {
      return;
    }

    if (attempts > 6) {
      logEvent("BATCH_SEND_FAILED", { tabId, batchId, reason: "max retries exceeded" });
      fetchWithTimeout(`${API_BASE}/reset_batch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ batch_id: batchId, try_id: tryId, reason: "message_retry_exhausted" })
      }).catch(() => {});

      // Mark tasks as pending for retry
      const tabInfo = activeTabs.get(tabId);
      if (tabInfo && tabInfo.tasks) {
        updateTaskStates(tabInfo.tasks, 'pending').catch(() => {});
      }
      activeTabs.delete(tabId);
      
      const currentActiveTabs = state.activeTabs || [];
      const index = currentActiveTabs.indexOf(tabId);
      if (index > -1) {
        currentActiveTabs.splice(index, 1);
        await updateStoredState({ activeTabs: currentActiveTabs });
        chrome.tabs.remove(tabId).catch(() => {});
      } else {
        await updateStoredState({ activeTabs: currentActiveTabs });
      }
      return;
    }

    chrome.tabs.sendMessage(tabId, {
      action: "executeBatch",
      batchId,
      tryId,
      tasks,
      speedMode,
      deep: deepOptions || state.deepOptions || DEFAULT_STATE.deepOptions
    }).then(() => {
      logEvent("BATCH_STARTED", { tabId, batchId, tryId, tasks: tasks.length, attempt: attempts });
    }).catch(() => {
      setTimeout(() => sendBatchWithRetry(tabId, batchId, tryId, tasks, speedMode, attempts + 1, deepOptions), 1500);
    });
  });
}

// ── Main orchestrator ──
async function orchestrate() {
  if (isOrchestrating) return;
  isOrchestrating = true;

  try {
    const state = await getStoredState();

    if (!state.isAutopilotRunning || state.isStopping) {
      isOrchestrating = false;
      return;
    }

    await fetchConfig();
    if (currentMaxTabs > targetMaxTabs || (!cpuThrottled && currentMaxTabs !== targetMaxTabs)) {
      currentMaxTabs = targetMaxTabs;
    }

    const statRes = await fetchWithTimeout(`${API_BASE}/status`);
    if (!statRes.ok) throw new Error("Could not fetch status");
    const status = await statRes.json();

    if (!status.active || status.status !== "in_progress") {
      const s = await getStoredState();
      if (s.isAutopilotRunning || s.isExtracting) {
        await stopAllOperations();
      } else {
        await updateStoredState({ isAutopilotRunning: false, autopilotProgress: null });
      }
      isOrchestrating = false;
      return;
    }

    // Sync progress stats
    const autopilotProgress = {
      tryId: status.try_id,
      status: status.status,
      completed: status.completed,
      total: status.total,
      pending: status.pending,
      inProgress: status.in_progress,
      lastUpdate: Date.now(),
      cpu: status.cpu_usage,
      memory: status.memory_usage,
      eta: status.eta,
      tasks: status.tasks
    };
    await updateStoredState({ autopilotProgress });

    // Handle resource threshold limits
    const currentActiveTabs = state.activeTabs || [];

    // Determine how many new tabs can be opened based on the configured concurrency limit and currently active tabs.
    let availableSlots = Math.max(0, currentMaxTabs - currentActiveTabs.length);

    // If CPU usage is throttling, halt launching new tabs, but always allow at least 1 tab if none are active to prevent deadlock
    if (cpuThrottled && currentActiveTabs.length > 0) {
      availableSlots = 0;
    }

    if (availableSlots <= 0) {
      isOrchestrating = false;
      return;
    }

    for (let i = 0; i < availableSlots; i++) {
      const freshState = await getStoredState();
      if (!freshState.isAutopilotRunning || freshState.isStopping || cpuThrottled) {
        break;
      }

      await assignNextBatchToTab();
    }
  } catch (err) {
    logEvent("ORCHESTRATOR_ERROR", { error: String(err) });
    console.warn("Orchestration error:", err);
  } finally {
    isOrchestrating = false;
  }
}

async function assignNextBatchToTab(existingTabId = null) {
  const state = await getStoredState();
  if (!state.isAutopilotRunning || state.isStopping) {
    if (existingTabId) {
      activeTabs.delete(existingTabId);
      const currentActiveTabs = state.activeTabs || [];
      const index = currentActiveTabs.indexOf(existingTabId);
      if (index > -1) {
        currentActiveTabs.splice(index, 1);
        await updateStoredState({ activeTabs: currentActiveTabs });
        chrome.tabs.remove(existingTabId).catch(() => {});
      } else {
        await updateStoredState({ activeTabs: currentActiveTabs });
      }
      logEvent("TAB_CLOSED_ON_STOP_REUSE", { tabId: existingTabId });
    }
    return;
  }

  if (existingTabId) {
    const currentActiveTabs = state.activeTabs || [];
    if (currentActiveTabs.length > currentMaxTabs || cpuThrottled) {
      activeTabs.delete(existingTabId);
      const index = currentActiveTabs.indexOf(existingTabId);
      if (index > -1) {
        currentActiveTabs.splice(index, 1);
        await updateStoredState({ activeTabs: currentActiveTabs });
        chrome.tabs.remove(existingTabId).catch(() => {});
      } else {
        await updateStoredState({ activeTabs: currentActiveTabs });
      }
      logEvent("TAB_CLOSED_ON_THROTTLE", {
        tabId: existingTabId,
        activeTabsCount: currentActiveTabs.length,
        limit: currentMaxTabs,
        cpuThrottled
      });
      return;
    }
  }

  const batchRes = await fetchWithTimeout(`${API_BASE}/next_batch`);
  const batchData = await batchRes.json();
  if (!batchData.success || !batchData.batch) return;

  const { try_id: tryId, batch, target_url } = batchData;

  // Re-check state to avoid race condition during network call
  const freshState = await getStoredState();
  if (!freshState.isAutopilotRunning || freshState.isStopping) {
    fetchWithTimeout(`${API_BASE}/reset_batch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ batch_id: batch.id, try_id: tryId, reason: "stop_requested_during_assign" })
    }).catch(() => {});
    return;
  }

  // Server is the single source of truth. No local registry filtering is needed.
  if (!batch.tasks || batch.tasks.length === 0) return;

  // -----------------------------------------------------------------
  // Ensure we have a valid URL before opening a new tab.
  // If the server did not provide `target_url`, we abort this batch
  // to avoid opening the generic DAT login page which triggers rate‑limits.
  // -----------------------------------------------------------------
  if (!target_url) {
    logEvent('MISSING_TARGET_URL', { batchId: batch.id, tryId: tryId });
    // Mark tasks as pending so they can be reassigned later.
    await updateTaskStates(batch.tasks, 'pending');
    return;
  }
  const tabUrl = target_url; // use the URL supplied by the server

    let tabId = existingTabId;
    if (!tabId) {
      let tab;
      try {
        tab = await chrome.tabs.create({ url: tabUrl, active: false });
      } catch (err) {
        logEvent("TAB_CREATE_FAILED", { url: tabUrl, error: String(err.message || err) });
        // Reset the batch back to pending on the server so it can be retried later
        fetchWithTimeout(`${API_BASE}/reset_batch`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ batch_id: batch.id, try_id: tryId, reason: "tab_creation_failed" })
        }).catch(() => {});
        return;
      }
      tabId = tab.id;
      const s = await getStoredState();
      const activeTabsList = s.activeTabs || [];
      activeTabsList.push(tabId);
      await updateStoredState({ activeTabs: activeTabsList });
    }


  activeTabs.set(tabId, {
    batchId: batch.id,
    tryId,
    tasks: batch.tasks,
    retries: 0,
    startedAt: Date.now()
  });

  const runLogic = async () => {
    const s = await getStoredState();
    if (!s.isAutopilotRunning || s.isStopping) {
      activeTabs.delete(tabId);
      const currentActiveTabs = s.activeTabs || [];
      const index = currentActiveTabs.indexOf(tabId);
      if (index > -1) {
        currentActiveTabs.splice(index, 1);
        await updateStoredState({ activeTabs: currentActiveTabs });
        chrome.tabs.remove(tabId).catch(() => {});
      }
      fetchWithTimeout(`${API_BASE}/reset_batch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ batch_id: batch.id, try_id: tryId, reason: "stop_requested_during_execution" })
      }).catch(() => {});
      return;
    }
    await updateTaskStates(batch.tasks, 'running');
    sendBatchWithRetry(tabId, batch.id, tryId, batch.tasks, s.speedMode, 0, s.deepOptions || DEFAULT_STATE.deepOptions);
  };

  if (existingTabId) {
    runLogic();
  } else {
    waitForContentScriptReady(tabId).then(runLogic).catch(async err => {
      logEvent("TAB_LOAD_ERROR", { tabId, batchId: batch.id, error: String(err) });
      fetchWithTimeout(`${API_BASE}/reset_batch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ batch_id: batch.id, try_id: tryId, reason: "handshake_failure" })
      }).catch(() => {});
      activeTabs.delete(tabId);
      
      const s = await getStoredState();
      const currentActiveTabs = s.activeTabs || [];
      const index = currentActiveTabs.indexOf(tabId);
      if (index > -1) {
        currentActiveTabs.splice(index, 1);
        await updateStoredState({ activeTabs: currentActiveTabs });
        chrome.tabs.remove(tabId).catch(() => {});
      }
    });
  }
}

// ── Resource Monitoring & Concurrency Scaling Loop ──
async function monitorResources() {
  const state = await getStoredState();
  if (!state.isAutopilotRunning || state.isStopping) {
    return;
  }

  try {
    await fetchConfig();
    const res = await fetch(`${API_BASE}/status`);
    if (res.ok) {
      const stat = await res.json();
      if (stat.active) {
        const cpu = stat.cpu_usage || 0;
        const memory = stat.memory_usage || 0;

        if (cpu >= cpuThreshold) {
          if (!cpuThrottled) {
            cpuThrottled = true;
            const newMax = Math.max(1, currentMaxTabs - 1);
            logEvent("CPU_THRESHOLD_EVENT", {
              cpu,
              threshold: cpuThreshold,
              message: `CPU usage has approached the configured threshold. Scaling down concurrency limit from ${currentMaxTabs} to ${newMax}.`
            });
            currentMaxTabs = newMax;
          }
        } else if (cpu < cpuThreshold - 10) { // 10% hysteresis
          if (cpuThrottled) {
            if (currentMaxTabs < targetMaxTabs) {
              const newMax = currentMaxTabs + 1;
              logEvent("SCALE_CONCURRENCY", {
                cpu,
                message: `CPU usage stabilized. Scaling up concurrency limit from ${currentMaxTabs} to ${newMax}.`
              });
              currentMaxTabs = newMax;
            }
            if (currentMaxTabs >= targetMaxTabs) {
              cpuThrottled = false;
            }
          }
        }
      }
    }
  } catch (err) {
    console.warn("Resource monitoring error:", err);
  }
}

// ── Tab Lifecycle Watchdog (Close hung tabs) ──
async function checkTabLifecycle() {
  const now = Date.now();

  // Note: Un-minimizing on watchdog has been disabled to prevent focus stealing/screen redirection.

  for (const [tabId, info] of activeTabs.entries()) {
    // 3 hours timeout (each combination has 3 hours task timeout max)
    if (now - info.startedAt > 10800000) {
      logEvent("TAB_TIMEOUT", { tabId, batchId: info.batchId, message: "Tab exceeded 3-hour limit. Force closing and resetting batch." });
      
      // Mark tasks as pending so they can be re-claimed
      if (info.tasks) {
        updateTaskStates(info.tasks, 'pending').catch(() => {});
      }

      fetchWithTimeout(`${API_BASE}/reset_batch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ batch_id: info.batchId, try_id: info.tryId, reason: "watchdog_timeout" })
      }).catch(() => {});

      activeTabs.delete(tabId);

      getStoredState().then(async (state) => {
        const currentActiveTabs = state.activeTabs || [];
        const index = currentActiveTabs.indexOf(tabId);
        if (index > -1) {
          currentActiveTabs.splice(index, 1);
          await updateStoredState({ activeTabs: currentActiveTabs });
          chrome.tabs.remove(tabId).catch(() => {});
        }
      });
    }
  }

  // Sync stored activeTabs with actual open Chrome tabs to resolve any discrepancies (e.g. manual tab closure when extension was reloaded)
  try {
    const state = await getStoredState();
    const storedActiveTabs = state.activeTabs || [];
    if (storedActiveTabs.length > 0) {
      const actualTabs = await chrome.tabs.query({});
      const actualTabIds = new Set(actualTabs.map(t => t.id));
      
      const validatedTabs = [];
      let mismatchDetected = false;
      for (const tabId of storedActiveTabs) {
        if (actualTabIds.has(tabId)) {
          validatedTabs.push(tabId);
        } else {
          mismatchDetected = true;
          logEvent("ORPHANED_TAB_DETECTED", { tabId });
          // If the tab was in activeTabs in-memory, clean it up
          if (activeTabs.has(tabId)) {
            const info = activeTabs.get(tabId);
            if (info.tasks) {
              await updateTaskStates(info.tasks, 'pending').catch(() => {});
            }
            fetchWithTimeout(`${API_BASE}/reset_batch`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ batch_id: info.batchId, try_id: info.tryId, reason: "orphaned_tab_cleanup" })
            }).catch(() => {});
            activeTabs.delete(tabId);
          }
        }
      }
      
      if (mismatchDetected) {
        await updateStoredState({ activeTabs: validatedTabs });
        logEvent("STORAGE_ACTIVE_TABS_SYNCED", { before: storedActiveTabs.length, after: validatedTabs.length });
      }
    }
  } catch (err) {
    console.warn("Error in tab lifecycle sync:", err);
  }
}

// ── Global STOP Operation ──
async function stopAllOperations() {
  logEvent("STOP_ALL_OPERATIONS_REQUESTED", { source: "user" });

  const state = await getStoredState();
  await updateStoredState({ isStopping: true });

  // 1. Close all active autopilot tabs registered in storage
  const tabsToClose = state.activeTabs || [];
  for (const tabId of tabsToClose) {
    try {
      await chrome.tabs.remove(tabId);
      logEvent("TAB_CLOSED_ON_STOP_STORAGE", { tabId });
    } catch (e) {}
  }

  // 1b. Close all tabs registered in the in-memory Map
  for (const tabId of activeTabs.keys()) {
    try {
      await chrome.tabs.remove(tabId);
      logEvent("TAB_CLOSED_ON_STOP_MAP", { tabId });
    } catch (e) {}
  }
  activeTabs.clear();

    // 1c. NOTE: Do NOT close tabs that the user opened manually.
    // The extension now only closes tabs it created (tracked in state.activeTabs and activeTabs map).
    // Previously we queried all DAT tabs and closed them, which could close user‑opened tabs.
    // This block has been removed to preserve user‑opened tabs.

  // 2. Cancel manual extraction on the current page if it is active
  try {
    const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (activeTab?.id) {
      chrome.tabs.sendMessage(activeTab.id, { action: "cancelExtract" }).catch(() => {});
    }
  } catch (e) {}

  // 3. Notify the server to stop the try
  try {
    const tryId = state.autopilotProgress?.tryId;
    await fetchWithTimeout(`${API_BASE}/stop_try`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ try_id: tryId })
    });
    logEvent("SERVER_STOP_TRY_SENT", { try_id: tryId });
  } catch (e) {
    console.warn("Could not contact server to stop try:", e);
  }

  // 4. Reset state to idle
  const finalState = {
    isExtracting: false,
    isAutopilotRunning: false,
    isStopping: false,
    speedMode: state.speedMode || "normal",
    manualProgress: null,
    autopilotProgress: null,
    deepProgress: state.deepProgress || null,
    deepOptions: state.deepOptions || DEFAULT_STATE.deepOptions,
    activeTabs: []
  };
  await chrome.storage.local.set({ dat_extractor_state: finalState });
  logEvent("ALL_OPERATIONS_STOPPED", {});
}

// ── Search Tab Active State Coordinator ──
let activeStateLockHolder = null;
const activeStateQueue = [];
let activeStateTimeoutId = null;

function processActiveStateQueue() {
  if (activeStateLockHolder !== null) {
    return;
  }
  if (activeStateQueue.length === 0) {
    return;
  }

  const nextRequest = activeStateQueue.shift();
  activeStateLockHolder = nextRequest.tabId;

  if (activeStateTimeoutId) clearTimeout(activeStateTimeoutId);
  activeStateTimeoutId = setTimeout(() => {
    if (activeStateLockHolder === nextRequest.tabId) {
      logEvent("ACTIVE_STATE_LOCK_TIMEOUT", { tabId: nextRequest.tabId });
      activeStateLockHolder = null;
      processActiveStateQueue();
    }
  }, 20000); // 20-second safety timeout

  chrome.tabs.get(nextRequest.tabId, (tab) => {
    if (chrome.runtime.lastError || !tab) {
      activeStateLockHolder = null;
      processActiveStateQueue();
      return;
    }

    chrome.windows.getLastFocused({ populate: false }, (focusedWindow) => {
      const isSameWindow = tab.windowId === focusedWindow.id;

      chrome.tabs.query({ active: true, windowId: focusedWindow.id }, (activeTabsInWindow) => {
        const activeTab = activeTabsInWindow[0];

        // Determine if the active tab in the focused window is an extension page or crawler tab
        const isExtensionPage = activeTab && activeTab.url && (activeTab.url.includes(chrome.runtime.id) || activeTab.url.includes("dashboard.html"));
        const isActiveTabCrawler = activeTab && activeTabs.has(activeTab.id);

        if (isSameWindow && activeTab && !isActiveTabCrawler && !isExtensionPage) {
          // The user is on a non-crawler tab in the active window. Skip activation to avoid stealing focus.
          logEvent("ACTIVATE_TAB_SKIPPED_USER_ACTIVE", { tabId: nextRequest.tabId, activeTabId: activeTab.id });
          nextRequest.resolve({ success: true });
          return;
        }

        // Otherwise (different window, or same window but user is on an extension page/crawler), activate the tab!
        chrome.tabs.update(nextRequest.tabId, { active: true }).then(() => {
          nextRequest.resolve({ success: true });
        }).catch((err) => {
          logEvent("ACTIVATE_TAB_FAILED", { tabId: nextRequest.tabId, error: String(err) });
          activeStateLockHolder = null;
          if (activeStateTimeoutId) clearTimeout(activeStateTimeoutId);
          nextRequest.resolve({ success: false, error: String(err) });
          processActiveStateQueue();
        });
      });
    });
  });
}

// ── Directory Scrapers Registry ──
const directoryScrapers = new Map(); // directoryTabId -> { requestTabId, url, createdAt }

function registerDirectoryScraperTab(tabId, requestTabId, url) {
  directoryScrapers.set(tabId, { requestTabId, url, createdAt: Date.now() });
  
  // Service Worker active watchdog fallback
  setTimeout(() => {
    if (directoryScrapers.has(tabId)) {
      directoryScrapers.delete(tabId);
      chrome.tabs.remove(tabId).catch(() => {});
      logEvent("DIRECTORY_TAB_FORCE_CLOSED_TIMEOUT", { tabId, url });
    }
  }, 45000);
}

function cleanUpHungDirectoryTabs() {
  const now = Date.now();
  for (const [tabId, info] of directoryScrapers.entries()) {
    if (now - info.createdAt > 45000) {
      directoryScrapers.delete(tabId);
      chrome.tabs.remove(tabId).catch(() => {});
      logEvent("DIRECTORY_TAB_FORCE_CLOSED_TIMEOUT", { tabId, url: info.url });
    }
  }
}

// Watch for automatically opened directory tabs
chrome.tabs.onCreated.addListener((tab) => {
  handlePotentialDirectoryTab(tab);
});

// Track active tabs to prevent directory tabs from stealing focus
chrome.tabs.onActivated.addListener((activeInfo) => {
  const tabId = activeInfo.tabId;
  const windowId = activeInfo.windowId;

  const info = directoryScrapers.get(tabId);
  if (info) {
    // Only deflect focus back if the tab was created less than 1.5 seconds ago (prevent focus stealing on auto-open)
    const elapsed = Date.now() - info.createdAt;
    if (elapsed < 1500) {
      const lastActiveTabId = lastActiveTabPerWindow.get(windowId);
      if (lastActiveTabId && lastActiveTabId !== tabId) {
        chrome.tabs.update(lastActiveTabId, { active: true }).catch(() => {});
      }
    }
  } else {
    lastActiveTabPerWindow.set(windowId, tabId);
  }
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url) {
    handlePotentialDirectoryTab(tab);

    // If this is a tracked directory scraper tab, and it got redirected to login
    if (directoryScrapers.has(tabId)) {
      const url = changeInfo.url;
      if (url.includes("login.dat.com") || url.includes("/login")) {
        const scraperInfo = directoryScrapers.get(tabId);
        logEvent("DIRECTORY_TAB_REDIRECTED_TO_LOGIN", { tabId, url });
        
        // Notify the search tab that directory scrape failed
        chrome.tabs.sendMessage(scraperInfo.requestTabId, {
          action: "directoryScrapedDone",
          url: scraperInfo.url,
          data: null,
          error: "Redirected to login"
        }).catch(() => {});

        directoryScrapers.delete(tabId);
        chrome.tabs.remove(tabId).catch(() => {});
      }
    }
  }
});

function handlePotentialDirectoryTab(tab) {
  if (directoryScrapers.has(tab.id)) return;
  const url = tab.url || tab.pendingUrl;
  if (!url || (!url.includes("directory.dat.com") && !url.includes("/offices/"))) return;

  const requestTabId = tab.openerTabId;
  if (requestTabId && activeTabs.has(requestTabId)) {
    // Register it with watchdog tracking
    registerDirectoryScraperTab(tab.id, requestTabId, url);
    logEvent("AUTO_DIRECTORY_TAB_REGISTERED", { tabId: tab.id, openerTabId: requestTabId, url });

    // If the tab is active on creation, immediately restore focus to the last active tab
    if (tab.active) {
      const lastActiveTabId = lastActiveTabPerWindow.get(tab.windowId);
      if (lastActiveTabId && lastActiveTabId !== tab.id) {
        chrome.tabs.update(lastActiveTabId, { active: true }).catch(() => {});
      } else if (requestTabId !== tab.id) {
        chrome.tabs.update(requestTabId, { active: true }).catch(() => {});
      }
    }
  } else {
    logEvent("AUTO_DIRECTORY_TAB_IGNORED_NO_OPENER", { tabId: tab.id, url });
  }
}


// ── Message listener ──
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  cleanUpHungDirectoryTabs();
  if (request.action === "logToServer") {
    logEvent(request.eventType, request.details);
    sendResponse({ ok: true });
    return;
  }

  // Progress relays from the content script. Written to storage so every open
  // surface (popup, side panel, dashboard) re-renders from a single source.
  if (request.action === "extractProgress") {
    updateStoredState({
      manualProgress: {
        collected: request.collected,
        target: request.target,
        step: request.step,
        maxSteps: request.maxSteps,
        duplicates: request.duplicates
      }
    }).catch(() => {});
    sendResponse({ ok: true });
    return;
  }

  if (request.action === "deepProgress") {
    updateStoredState({ deepProgress: { ...request.stats, lastUpdate: Date.now() } }).catch(() => {});
    sendResponse({ ok: true });
    return;
  }



  if (request.action === "requestActiveState") {
    const tabId = sender?.tab?.id;
    if (!tabId) {
      sendResponse({ success: false, error: "No sender tab" });
      return;
    }
    new Promise((resolve) => {
      activeStateQueue.push({ tabId, resolve });
      processActiveStateQueue();
    }).then((res) => {
      sendResponse(res);
    });
    return true; // Keep message channel open for async response
  }

  if (request.action === "releaseActiveState") {
    const tabId = sender?.tab?.id;
    if (tabId === activeStateLockHolder) {
      activeStateLockHolder = null;
      if (activeStateTimeoutId) {
        clearTimeout(activeStateTimeoutId);
        activeStateTimeoutId = null;
      }
      sendResponse({ success: true });
      setTimeout(processActiveStateQueue, 100);
    } else {
      sendResponse({ success: false, error: "Not holding the lock" });
    }
    return;
  }

  if (request.action === "openAndScrapeDirectory") {
    const requestTabId = sender?.tab?.id;
    if (!requestTabId) {
      sendResponse({ ok: false, error: "No sender tab" });
      return;
    }
    chrome.tabs.create({ url: request.url, active: false }).then((newTab) => {
      registerDirectoryScraperTab(newTab.id, requestTabId, request.url);
      logEvent("DIRECTORY_TAB_CREATED", { tabId: newTab.id, url: request.url });
    }).catch((err) => {
      logEvent("DIRECTORY_TAB_CREATE_FAILED", { error: String(err) });
    });
    sendResponse({ ok: true });
    return;
  }

  if (request.action === "directoryDataScraped") {
    const tabId = sender?.tab?.id;
    if (tabId) {
      const scraperInfo = directoryScrapers.get(tabId);
      if (scraperInfo) {
        chrome.tabs.sendMessage(scraperInfo.requestTabId, {
          action: "directoryScrapedDone",
          url: scraperInfo.url,
          data: request.success ? request.data : null
        }).catch(() => {});
        directoryScrapers.delete(tabId);
        chrome.tabs.remove(tabId).catch(() => {});
        logEvent("DIRECTORY_TAB_CLOSED", { tabId, url: request.url || scraperInfo.url, success: request.success });
      } else {
        // Broadcast fallback to all active extraction tabs
        for (const activeTabId of activeTabs.keys()) {
          chrome.tabs.sendMessage(activeTabId, {
            action: "directoryScrapedDone",
            url: request.url,
            data: request.success ? request.data : null
          }).catch(() => {});
        }
      }
    }
    sendResponse({ ok: true });
    return;
  }

  if (request.action === "batchCompleted") {
    const tabId = sender?.tab?.id;
    const tabInfo = activeTabs.get(tabId);
    const { batchId, tryId, results, taskStats } = request;

    logEvent("BATCH_RESULTS_RECEIVED", {
      tabId,
      batchId,
      tryId,
      count: results?.length ?? 0
    });

    fetchWithTimeout(`${API_BASE}/complete_batch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        batch_id: batchId,
        try_id: tryId,
        results: results || [],
        task_stats: taskStats || []
      })
    })
      .then(r => r.json())
      .then(async data => {
        if (data.success) {
          logEvent("BATCH_SAVED", { batchId, tryId, all_completed: data.all_completed });
        }
      })
      .catch(err => logEvent("COMPLETE_BATCH_ERROR", { batchId, error: String(err) }))
      .finally(async () => {
        if (tabId != null) {
          // Capture tasks before cleaning up
          const completedTasks = tabInfo?.tasks || [];
          if (completedTasks.length) {
            await updateTaskStates(completedTasks, 'completed').catch(() => {});
          }

          // Delete from activeTabs since this batch is completed
          activeTabs.delete(tabId);

          // Clean up local storage state and close the tab if we created it
          const s = await getStoredState();
          const currentActiveTabs = s.activeTabs || [];
          const index = currentActiveTabs.indexOf(tabId);
          if (index > -1) {
            currentActiveTabs.splice(index, 1);
            await updateStoredState({ activeTabs: currentActiveTabs });
            chrome.tabs.remove(tabId).catch(() => {});
            logEvent("TAB_CLOSED_AFTER_COMPLETION", { tabId, batchId });
          } else {
            logEvent("REUSED_TAB_KEPT_OPEN_AFTER_COMPLETION", { tabId, batchId });
          }
        }

        // Trigger next orchestration after all tab state cleanups are completely finished!
        const s = await getStoredState();
        if (s.isAutopilotRunning && !s.isStopping) {
          orchestrate();
        }
      });

    sendResponse({ ok: true });
    return true; // async
  }

  if (request.action === "triggerOrchestration") {
    const sourceLabel = sender?.tab ? "dashboard" : "popup";
    logEvent("ORCHESTRATION_TRIGGERED", { source: sourceLabel });
    updateStoredState({ isAutopilotRunning: true, isStopping: false }).then(() => {
      resetNonCompletedTasks().then(() => {
        orchestrate();
      }).catch(() => {
        orchestrate();
      });
    }).catch(() => {
      orchestrate();
    });
    sendResponse({ ok: true });
    return true;
  }

  if (request.action === "stopAll") {
    stopAllOperations().then(() => sendResponse({ ok: true }));
    return true;
  }
});

// ── Recovery on tab closed unexpectedly ──
chrome.tabs.onRemoved.addListener(async (tabId) => {
  // Clean up active state lock & queue if the removed tab was holding the lock or waiting in queue
  if (tabId === activeStateLockHolder) {
    activeStateLockHolder = null;
    if (activeStateTimeoutId) {
      clearTimeout(activeStateTimeoutId);
      activeStateTimeoutId = null;
    }
    processActiveStateQueue();
  }
  const queueIdx = activeStateQueue.findIndex(r => r.tabId === tabId);
  if (queueIdx > -1) {
    activeStateQueue.splice(queueIdx, 1);
  }

  if (directoryScrapers.has(tabId)) {
    const scraperInfo = directoryScrapers.get(tabId);
    logEvent("DIRECTORY_TAB_CLOSED_PREMATURELY", { tabId, url: scraperInfo.url });
    chrome.tabs.sendMessage(scraperInfo.requestTabId, {
      action: "directoryScrapedDone",
      url: scraperInfo.url,
      data: null
    }).catch(() => {});
    directoryScrapers.delete(tabId);
  }

  // Always check and remove from stored activeTabs to prevent zombie slots
  const s = await getStoredState();
  const currentActiveTabs = s.activeTabs || [];
  const index = currentActiveTabs.indexOf(tabId);
  if (index > -1) {
    currentActiveTabs.splice(index, 1);
    await updateStoredState({ activeTabs: currentActiveTabs });
    logEvent("TAB_REMOVED_FROM_STORAGE", { tabId, remaining: currentActiveTabs.length });
  }

  if (activeTabs.has(tabId)) {
    const info = activeTabs.get(tabId);
    logEvent("TAB_CLOSED_UNEXPECTEDLY", { tabId, batchId: info.batchId, tryId: info.tryId });
    
    // Mark tasks as pending so they can be re-claimed by another tab
    if (info.tasks) {
      await updateTaskStates(info.tasks, 'pending').catch(() => {});
    }

    fetchWithTimeout(`${API_BASE}/reset_batch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ batch_id: info.batchId, try_id: info.tryId, reason: "tab_closed_unexpectedly" })
    }).catch(() => {});

    activeTabs.delete(tabId);

    if (s.isAutopilotRunning && !s.isStopping) {
      setTimeout(orchestrate, 2000);
    }
  }
});

// ── Loops ──
setInterval(orchestrate, 5000);
setInterval(monitorResources, 3000);
setInterval(checkTabLifecycle, 10000);

// ── Startup & Install Event Initialization ──
async function initBackground() {
  // Populate last active tabs per window on startup
  try {
    const tabs = await chrome.tabs.query({ active: true });
    for (const tab of tabs) {
      lastActiveTabPerWindow.set(tab.windowId, tab.id);
    }
  } catch (err) {}

  const state = await getStoredState();
  
  // 1. Clean up any leftover tabs in storage to prevent leaks/zombies
  if (state.activeTabs && state.activeTabs.length > 0) {
    for (const tabId of state.activeTabs) {
      try {
        await chrome.tabs.remove(tabId);
        logEvent("TAB_CLEANED_ON_STARTUP", { tabId });
      } catch (e) {}
    }
  }

  // Always reset activeTabs storage to empty on startup
  await updateStoredState({ activeTabs: [] });

  // 1b. Clean up task registry
  await resetNonCompletedTasks().catch(() => {});

  // 2. Fetch server status to see if there is an active session
  try {
    const res = await fetchWithTimeout(`${API_BASE}/status`);
    if (res.ok) {
      const status = await res.json();
      if (status.active && status.status === "in_progress") {
        logEvent("AUTO_RESUME_ON_STARTUP", { try_id: status.try_id });
        
        // Clean up orphaned in-progress batches on startup/reload
        try {
          await fetchWithTimeout(`${API_BASE}/resume`, { method: "POST" });
        } catch (e) {
          console.warn("Could not contact server to resume during initialization:", e);
        }
        
        // Restore state and start orchestrating
        const autopilotProgress = {
          tryId: status.try_id,
          status: status.status,
          completed: status.completed,
          total: status.total,
          pending: status.pending,
          inProgress: status.in_progress,
          lastUpdate: Date.now(),
          cpu: status.cpu_usage,
          memory: status.memory_usage,
          eta: status.eta,
          tasks: status.tasks
        };
        
        await chrome.storage.local.set({
          dat_extractor_state: {
            isExtracting: false,
            isAutopilotRunning: true,
            isStopping: false,
            speedMode: state.speedMode || "normal",
            manualProgress: null,
            autopilotProgress: autopilotProgress,
            deepProgress: null,
            deepOptions: state.deepOptions || DEFAULT_STATE.deepOptions,
            activeTabs: []
          }
        });
        
        // Initialize currentMaxTabs to whatever config is on server
        await fetchConfig();
        currentMaxTabs = targetMaxTabs;
        
        // Start orchestrating immediately
        setTimeout(orchestrate, 2000);
        return;
      } else {
        // Server explicitly idle/inactive, reset state to completely idle at startup
        const cleanState = {
          isExtracting: false,
          isAutopilotRunning: false,
          isStopping: false,
          speedMode: state.speedMode || "normal",
          manualProgress: null,
          autopilotProgress: null,
          deepProgress: null,
          deepOptions: state.deepOptions || DEFAULT_STATE.deepOptions,
          activeTabs: []
        };
        await chrome.storage.local.set({ dat_extractor_state: cleanState });
      }
    }
  } catch (e) {
    console.warn("Could not check server status on startup:", e);
  }

  // Configure Side Panel behavior to open on action click
  if (chrome.sidePanel && chrome.sidePanel.setPanelBehavior) {
    chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch((err) => {
      console.warn("Could not set panel behavior:", err);
    });
  }
}

// Register install and startup listeners
chrome.runtime.onInstalled.addListener(initBackground);
chrome.runtime.onStartup.addListener(initBackground);

// Execute initialization immediately for reloads
initBackground();

// ── Background Keep-Alive Listener ──
chrome.runtime.onConnect.addListener((port) => {
  if (port.name === "keepAlive") {
    port.onMessage.addListener(() => {
      // Ping message received to keep worker alive
    });
  }
});

// ── Un-minimize window containing scraper/dashboard on focus change ──
// Disabled to prevent browser from stealing focus/redirecting main screen when minimized.
