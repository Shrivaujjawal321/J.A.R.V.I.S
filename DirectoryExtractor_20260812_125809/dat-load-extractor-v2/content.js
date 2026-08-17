// DAT Load Extractor V2.3 — all rows including empty; bounded scroll; speed optimized
(() => {
  // visibility/RAF bypass is now handled natively via inject-bypass.js in MAIN world
  let directoryCache = new Map();
  const originalSet = Map.prototype.set;

  // Function to serialize and save the directory cache to storage
  function saveDirectoryCacheToStorage() {
    try {
      const obj = Object.fromEntries(directoryCache.entries());
      chrome.storage.local.set({ directoryCache: obj }).catch(() => { });
    } catch (e) {
      console.error("[DAT Extractor] Error saving directory cache to storage:", e);
    }
  }

  // Hook set method to automatically persist to chrome.storage.local
  directoryCache.set = function (key, value) {
    const res = originalSet.call(this, key, value);
    saveDirectoryCacheToStorage();
    return res;
  };

  // Load persisted directory cache from chrome.storage.local on startup
  chrome.storage.local.get("directoryCache").then((data) => {
    if (data.directoryCache) {
      try {
        let count = 0;
        let cleaned = false;
        const cleanedCache = {};
        for (const [k, v] of Object.entries(data.directoryCache)) {
          const docket = v ? (v.docket || v.dir_docket) : null;
          const dotNumber = v ? (v.dot_number || v.dir_dot_number) : null;
          if (v && (docket || dotNumber)) {
            originalSet.call(directoryCache, k, v);
            cleanedCache[k] = v;
            count++;
          } else {
            cleaned = true;
          }
        }
        console.log(`[DAT Extractor] Loaded ${count} directory entries from storage.`);
        if (cleaned) {
          console.log(`[DAT Extractor] Cleaned invalid/empty entries from directory cache in local storage.`);
          chrome.storage.local.set({ directoryCache: cleanedCache }).catch(() => { });
        }
      } catch (e) {
        console.error("[DAT Extractor] Error parsing directory cache from storage:", e);
      }
    }
  }).catch((err) => {
    console.error("[DAT Extractor] Failed to load directory cache:", err);
  });

  function simulateClick(el) {
    if (!el) return;
    try {
      const rect = el.getBoundingClientRect();
      const clientX = rect.left + rect.width / 2 || 100;
      const clientY = rect.top + rect.height / 2 || 100;
      const screenX = window.screenX + clientX;
      const screenY = window.screenY + clientY;

      const downOpts = {
        bubbles: true,
        cancelable: true,
        composed: true,
        view: window,
        detail: 1,
        clientX,
        clientY,
        screenX,
        screenY,
        button: 0,
        buttons: 1,
        pointerId: 1,
        isPrimary: true
      };

      const upOpts = {
        ...downOpts,
        buttons: 0
      };

      el.dispatchEvent(new PointerEvent('pointerdown', downOpts));
      el.dispatchEvent(new MouseEvent('mousedown', downOpts));

      if (typeof el.focus === 'function') {
        try { el.focus(); } catch (err) { }
      }

      el.dispatchEvent(new PointerEvent('pointerup', upOpts));
      el.dispatchEvent(new MouseEvent('mouseup', upOpts));

      if (typeof el.click === 'function') {
        el.click();
      } else {
        const clickEvent = new MouseEvent('click', upOpts);
        el.dispatchEvent(clickEvent);
      }
    } catch (e) {
      console.warn("[DAT Extractor] Click simulation failed, falling back to standard click:", e);
      try { el.click(); } catch (err) { }
    }
  }

  const MAX_POSITIONS = 180;

  window.__DAT_EXTRACTOR_V2_CANCEL__ = false;

  // Helper to normalize relative and protocol-relative URLs
  function normalizeUrl(url) {
    if (!url) return url;
    if (url.startsWith('//')) {
      return window.location.protocol + url;
    }
    if (!url.startsWith('http')) {
      const base = window.location.origin;
      return base + (url.startsWith('/') ? '' : '/') + url;
    }
    return url;
  }

  // Document-level click interceptor to catch any directory links opening in new tabs
  document.addEventListener('click', (event) => {
    const anchor = event.target.closest('a');
    if (anchor && anchor.target === '_blank') {
      const href = anchor.getAttribute('href');
      if (href && (href.includes("directory.dat.com") || href.includes("/offices/") || href.includes("/directory/") || href.includes("/profile/"))) {
        if (document.documentElement.getAttribute('data-dat-directory-scraping-active') === 'true') {
          event.preventDefault();
          event.stopImmediatePropagation();
          const absoluteUrl = normalizeUrl(href);
          chrome.runtime.sendMessage({ action: "openAndScrapeDirectory", url: absoluteUrl });
        }
      }
    }
  }, true); // Capture phase to preempt other click handlers

  // Custom Event Listener to intercept window.open from the MAIN world
  window.addEventListener("DAT_OPEN_BACKGROUND_TAB", (e) => {
    const url = e.detail?.url;
    if (url) {
      const absoluteUrl = normalizeUrl(url);
      chrome.runtime.sendMessage({ action: "openAndScrapeDirectory", url: absoluteUrl });
    }
  });

  let scrollWaitMs = 220;
  let scrollStepRatio = 0.6;
  let skeletonMaxWaitMs = 3000;
  let autocompleteWaitMs = 1500;
  let selectWaitMs = 1000;

  function setSpeedMode(mode) {
    if (mode === "ultra") {
      scrollWaitMs = 60;
      scrollStepRatio = 0.85;
      skeletonMaxWaitMs = 800;
      autocompleteWaitMs = 400;
      selectWaitMs = 300;
    } else if (mode === "fast") {
      scrollWaitMs = 120;
      scrollStepRatio = 0.7;
      skeletonMaxWaitMs = 1500;
      autocompleteWaitMs = 800;
      selectWaitMs = 500;
    } else { // normal
      scrollWaitMs = 250;
      scrollStepRatio = 0.5;
      skeletonMaxWaitMs = 3000;
      autocompleteWaitMs = 1500;
      selectWaitMs = 1000;
    }
    console.log(`[DAT Extractor] Speed mode set: ${mode}. Wait: ${scrollWaitMs}ms, Step ratio: ${scrollStepRatio}, Skeleton wait: ${skeletonMaxWaitMs}ms`);
  }

  // ── Deep extraction settings ──────────────────────────────────────
  // The deep pass opens each load's detail drawer and walks every tab, accordion
  // and sub-panel behind it. It is on by default; turn it off to get exactly the
  // old summary-only behaviour back.
  let deepMode = true;
  let deepMaxClicks = 26;
  let deepMaxDepth = 3;
  let deepRetries = 1; // one retry per load for transient failures

  const DEEP = () => window.__DAT_DEEP__;

  const deepStats = {
    total: 0,
    processed: 0,
    complete: 0,
    partial: 0,
    failed: 0,
    fields: 0,
    retries: 0,
    current: "",
    sections: []
  };

  function resetDeepStats(total) {
    deepStats.total = total || 0;
    deepStats.processed = 0;
    deepStats.complete = 0;
    deepStats.partial = 0;
    deepStats.failed = 0;
    deepStats.fields = 0;
    deepStats.retries = 0;
    deepStats.current = "";
    deepStats.sections = [];
  }

  function setDeepOptions(opts) {
    if (!opts || typeof opts !== "object") return;
    if (typeof opts.enabled === "boolean") deepMode = opts.enabled;
    if (Number.isFinite(opts.maxClicks)) deepMaxClicks = Math.max(0, Math.min(80, opts.maxClicks));
    if (Number.isFinite(opts.maxDepth)) deepMaxDepth = Math.max(1, Math.min(6, opts.maxDepth));
    if (Number.isFinite(opts.retries)) deepRetries = Math.max(0, Math.min(3, opts.retries));
    if (!DEEP() && deepMode) {
      console.warn("[DAT Extractor] deep-extract.js not loaded — deep mode disabled for this run.");
      deepMode = false;
    }
    console.log(`[DAT Extractor] Deep mode: ${deepMode ? "ON" : "OFF"} (depth ${deepMaxDepth}, max ${deepMaxClicks} reveals/load)`);
  }

  function reportDeepProgress() {
    try {
      chrome.runtime.sendMessage({
        action: "deepProgress",
        stats: { ...deepStats, sections: deepStats.sections.slice(-8) }
      }).catch(() => { });
    } catch (e) { }
  }

  function isCancelledNow() {
    return !!(window.__DAT_EXTRACTOR_V2_CANCEL__ || window.__DAT_AUTO_PILOT_STOP__);
  }

  // Company names come from the page; never inject them into the overlay raw.
  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => (
      { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
    ));
  }

  // Listen for storage changes to cancel extraction instantly if STOP is clicked
  try {
    chrome.storage.onChanged.addListener((changes, areaName) => {
      if (areaName === "local" && changes.dat_extractor_state) {
        const state = changes.dat_extractor_state.newValue;
        if (state && state.isStopping) {
          window.__DAT_EXTRACTOR_V2_CANCEL__ = true;
          window.__DAT_AUTO_PILOT_STOP__ = true;
          console.log("[DAT Extractor] STOP signal received. Cancelling...");
        }
      }
    });
  } catch (e) {
    console.warn("Storage listener failed:", e);
  }

  function txt(el) {
    return el ? el.textContent.trim() : "";
  }

  let sleepWorker = null;
  let nextSleepId = 0;
  const sleepResolves = new Map();

  function initSleepWorker() {
    if (sleepWorker) return;
    try {
      const blob = new Blob([
        `self.onmessage = function(e) {
          const { id, ms } = e.data;
          setTimeout(() => {
            self.postMessage({ id });
          }, ms);
        };`
      ], { type: 'application/javascript' });
      const url = URL.createObjectURL(blob);
      sleepWorker = new Worker(url);
      sleepWorker.onmessage = function(e) {
        const { id } = e.data;
        const resolve = sleepResolves.get(id);
        if (resolve) {
          sleepResolves.delete(id);
          resolve();
        }
      };
      console.log("[DAT Extractor] Sleep Worker initialized successfully.");
    } catch (err) {
      console.warn("[DAT Extractor] Failed to initialize Sleep Worker:", err);
    }
  }

  function sleep(ms) {
    initSleepWorker();
    if (sleepWorker) {
      return new Promise((resolve) => {
        const id = nextSleepId++;
        sleepResolves.set(id, resolve);
        sleepWorker.postMessage({ id, ms });
      });
    } else {
      return new Promise((resolve) => setTimeout(resolve, ms));
    }
  }

  function logToServer(eventType, details = {}) {
    try {
      chrome.runtime.sendMessage({
        action: "logToServer",
        eventType,
        details
      }).catch(() => { });
    } catch (e) { }
  }

  function isBlank(v) {
    const s = String(v ?? "").trim();
    return !s || s === "–" || s === "-" || s === "—";
  }

  function isElementVisible(el) {
    if (!el) return false;
    try {
      const style = window.getComputedStyle(el);
      if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
        return false;
      }
      if (document.hidden) {
        return true;
      }
      const rect = el.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    } catch (e) {
      return false;
    }
  }

  function norm(value) {
    const s = String(value ?? "").trim().toLowerCase().replace(/\s+/g, " ");
    if (s === "–" || s === "-" || s === "—" || s === "null" || s === "undefined") return "";
    return s;
  }

  function parseTotalResults(criteria) {
    const raw = String(criteria?.totalResults || "").replace(/,/g, "");
    const m = raw.match(/(\d+)/);
    return m ? parseInt(m[1], 10) : null;
  }

  function findPostingId(row) {
    for (const name of ["data-posting-id", "data-match-id", "data-asset-id"]) {
      const v = row.getAttribute(name);
      if (v && v.length > 2) return v;
    }
    for (const el of row.querySelectorAll("a[href]")) {
      const m = (el.getAttribute("href") || "").match(
        /(?:posting|match|load|asset)[s]?[\/=]([a-zA-Z0-9_-]{4,})/i
      );
      if (m) return m[1];
    }
    return "";
  }

  function getStableLoadKey(load) {
    if (load.postingId) return `posting:${load.postingId}`;
    return [
      norm(load.origin),
      norm(load.destination),
      norm(load.tripMiles),
      norm(load.rate),
      norm(load.ratePerMile),
      norm(load.deadheadOrigin),
      norm(load.deadheadDest),
      norm(load.company),
      norm(load.equipmentType),
    ].join("|");
  }

  function scoreLoad(load) {
    return Object.values(load).filter((v) => v && v !== "–" && v !== "").length;
  }

  function getLoadRows() {
    let rows = document.querySelectorAll(".row-container[id^='table-row-']");
    if (rows.length) return rows;
    return document.querySelectorAll("[id^='table-row-']");
  }

  function getScrollViewport() {
    // 1. Try to find viewport from the actual load row (most accurate, avoids matching sidebar/drawer viewports)
    const row = getLoadRows()[0];
    if (row) {
      const cdkAncestor = row.closest("cdk-virtual-scroll-viewport, .cdk-virtual-scroll-viewport");
      if (cdkAncestor) return cdkAncestor;

      let p = row.parentElement;
      while (p && p !== document.body) {
        const style = getComputedStyle(p);
        const overflowY = style.overflowY || "";
        const overflow = style.overflow || "";
        if (
          overflowY === "auto" || 
          overflowY === "scroll" || 
          overflow === "auto" || 
          overflow === "scroll"
        ) {
          return p;
        }
        if (p.scrollHeight > p.clientHeight + 10) {
          return p;
        }
        p = p.parentElement;
      }
      
      // Fallback: check class/tag containing 'viewport' or 'scroll' on ancestors
      let p2 = row.parentElement;
      while (p2 && p2 !== document.body) {
        const tagName = p2.tagName.toLowerCase();
        const className = typeof p2.className === "string" ? p2.className.toLowerCase() : "";
        if (
          tagName.includes("viewport") || 
          tagName.includes("scroll") || 
          className.includes("viewport") || 
          className.includes("scroll")
        ) {
          return p2;
        }
        p2 = p2.parentElement;
      }

      // Ultimate fallback: grandparent of row (usually row -> content-wrapper -> viewport)
      if (row.parentElement && row.parentElement.parentElement && row.parentElement.parentElement !== document.body) {
        return row.parentElement.parentElement;
      }
    }

    // 2. Global query fallback if no rows are present yet
    const cdk = document.querySelector("cdk-virtual-scroll-viewport") || 
                document.querySelector(".cdk-virtual-scroll-viewport");
    if (cdk) return cdk;

    return document.documentElement;
  }

  function measureRowHeight(viewport) {
    const row = getLoadRows()[0];
    if (row) {
      const h = row.getBoundingClientRect().height;
      if (h > 16) return Math.ceil(h);
    }
    const wrapper = viewport?.querySelector?.(".cdk-virtual-scroll-content-wrapper");
    if (wrapper?.children.length >= 2) {
      const gap = wrapper.children[1].offsetTop - wrapper.children[0].offsetTop;
      if (gap > 16) return gap;
    }
    return 48;
  }

  function getMaxScrollTop(viewport, targetTotal, rowHeight) {
    const fromEl = Math.max(0, viewport.scrollHeight - viewport.clientHeight);
    const fromCount = Math.max(0, (targetTotal || 0) * rowHeight);
    return Math.max(fromEl, fromCount);
  }

  function setScrollTop(viewport, top, targetTotal, rowHeight) {
    const maxTop = getMaxScrollTop(viewport, targetTotal, rowHeight);
    const targetTop = Math.min(Math.max(0, top), maxTop);
    viewport.scrollTop = targetTop;
    viewport.dispatchEvent(new Event('scroll', { bubbles: true }));
    if (viewport === document.documentElement) {
      window.scrollTo(0, targetTop);
      window.dispatchEvent(new Event('scroll'));
    }
  }

  async function scrollToPosition(viewport, targetScroll, targetTotal, rowHeight) {
    const clientHeight = viewport.clientHeight || 500;
    const step = clientHeight * 0.8 || 400;
    let current = viewport.scrollTop;
    
    if (targetScroll > current) {
      // Scrolling down incrementally
      while (current < targetScroll) {
        current = Math.min(targetScroll, current + step);
        setScrollTop(viewport, current, targetTotal, rowHeight);
        await sleep(80);
        
        // If scroll top didn't change (clamped), wait a bit more for scroller to expand
        if (Math.abs(viewport.scrollTop - current) > 100) {
          await sleep(120);
        }
      }
    } else if (targetScroll < current) {
      // Scrolling up incrementally
      while (current > targetScroll) {
        current = Math.max(targetScroll, current - step);
        setScrollTop(viewport, current, targetTotal, rowHeight);
        await sleep(80);
      }
    }
  }

  /** Only skip skeleton placeholders — empty/locked rows are still exported */
  function isSkeletonRow(row) {
    return !!row.querySelector(".dat-table-row-loader, .animated-background");
  }

  function isEmptyLoad(load) {
    return (
      isBlank(load.origin) &&
      isBlank(load.destination) &&
      isBlank(load.rate) &&
      isBlank(load.tripMiles)
    );
  }

  function rowTextSnippet(row) {
    return (row.innerText || "").replace(/\s+/g, " ").trim().slice(0, 100);
  }

  function getCaptureKey(row, load, scrollTop, visibleIdx) {
    if (load.postingId) return `posting:${load.postingId}`;
    const stable = getStableLoadKey(load);
    if (!isEmptyLoad(load)) return `data:${stable}`;
    return `empty:${scrollTop}:${visibleIdx}:${row.id || ""}:${rowTextSnippet(row)}`;
  }

  function extractLoadFromRow(row) {
    const load = {
      postingId: findPostingId(row),
      timestamp: new Date().toISOString()
    };

    // Helper to find elements by sub-strings in their class names or attributes
    function queryRobust(selectors, dataAttrs, classPart) {
      for (const sel of selectors) {
        const el = row.querySelector(sel);
        if (el) return el;
      }
      for (const attr of dataAttrs) {
        const el = row.querySelector(`[${attr}]`);
        if (el) return el;
      }
      if (classPart) {
        const el = row.querySelector(`[class*="${classPart}"], [class*="${classPart.toLowerCase()}"], [class*="${classPart.toUpperCase()}"]`);
        if (el) return el;
      }
      return null;
    }

    // ── 1. AGE EXTRACTION ──
    const ageEl = queryRobust(
      ['[data-test="load-age-cell"]', '.age', '.time-post', '.load-age'],
      ['data-test*="age"', 'data-test*="time"'],
      'age'
    );
    load.age = txt(ageEl);
    if (!load.age) {
      // Fallback: search text nodes for patterns like "1m", "15s", "2h", "new"
      const allSpans = row.querySelectorAll('span, div');
      for (const span of allSpans) {
        const t = txt(span);
        if (t === "new" || t.match(/^(?:[1-9]\d*[smhd])$/i)) {
          load.age = t;
          break;
        }
      }
    }
    if (!load.age) load.age = "–";

    // ── 2. RATE & RATE-PER-MILE EXTRACTION ──
    const rateCell = queryRobust(
      ['[data-test="load-rate-cell"]', '.rate-cell', '.price-cell', '.offer-cell'],
      ['data-test*="rate"', 'data-test*="price"', 'data-test*="offer"'],
      'rate'
    );
    load.rate = "–";
    load.ratePerMile = "–";

    if (rateCell) {
      const offerEl = rateCell.querySelector(".offer") || rateCell.querySelector('[class*="offer"]') || rateCell.querySelector('span');
      load.rate = offerEl ? txt(offerEl) : "–";
      const rpmEl = rateCell.querySelector(".calculated-rate span") || rateCell.querySelector('[class*="calculated"]') || rateCell.querySelector('span:nth-child(2)');
      load.ratePerMile = rpmEl && txt(rpmEl) ? txt(rpmEl) : "–";
    }

    // Fallback: parse all elements for currency patterns
    if (load.rate === "–" || load.rate === "") {
      const allTexts = Array.from(row.querySelectorAll('span, div, a')).map(el => txt(el)).filter(Boolean);
      const ratesFound = allTexts.filter(t => t.startsWith('$') && t.length > 1);
      for (const r of ratesFound) {
        if (r.includes('.')) {
          load.ratePerMile = r;
        } else {
          load.rate = r;
        }
      }
    }

    // ── 3. TRIP MILES EXTRACTION ──
    const tripCell = queryRobust(
      ['[data-test="load-trip-cell"]', '.trip-cell', '.miles-cell', '.distance-cell'],
      ['data-test*="trip"', 'data-test*="miles"', 'data-test*="distance"'],
      'trip'
    );
    const tripEl = tripCell?.querySelector("a") || tripCell?.querySelector('span') || tripCell;
    load.tripMiles = tripEl ? txt(tripEl).replace(/\s*mi\s*/gi, "").trim() : "–";
    if (load.tripMiles === "–" || isNaN(parseInt(load.tripMiles.replace(/,/g, '')))) {
      // Fallback: search for numbers followed by "mi"
      const allSpans = row.querySelectorAll('span, div, a');
      for (const span of allSpans) {
        const t = txt(span);
        const m = t.match(/^(\d+(?:,\d+)?)\s*mi$/i);
        if (m) {
          load.tripMiles = m[1];
          break;
        }
      }
    }

    // ── 4. ORIGIN / DESTINATION CITY-STATE EXTRACTION ──
    const originEl = queryRobust(
      ['[data-test="load-origin-cell"]', '.origin-cell', '.pickup-cell', '.from-cell'],
      ['data-test*="origin"', 'data-test*="pickup"'],
      'origin'
    );
    load.origin = "–";
    if (originEl) {
      const cs = originEl.querySelector(".city-state-container") || originEl.querySelector('[class*="city-state"]') || originEl;
      const city = cs.querySelector(".truncate") || cs.querySelector('[class*="truncate"]') || cs.querySelector('span:first-child');
      const state = cs.querySelector(".state") || cs.querySelector('[class*="state"]') || cs.querySelector('span:last-child');
      load.origin = city && state ? `${txt(city)}, ${txt(state)}` : txt(cs);
    }

    const destEl = queryRobust(
      ['[data-test="load-destination-cell"]', '.destination-cell', '.delivery-cell', '.to-cell'],
      ['data-test*="destination"', 'data-test*="dest"', 'data-test*="delivery"'],
      'destination'
    );
    load.destination = "–";
    if (destEl) {
      const cs = destEl.querySelector(".city-state-container") || destEl.querySelector('[class*="city-state"]') || destEl;
      const city = cs.querySelector(".truncate") || cs.querySelector('[class*="truncate"]') || cs.querySelector('span:first-child');
      const state = cs.querySelector(".state") || cs.querySelector('[class*="state"]') || cs.querySelector('span:last-child');
      load.destination = city && state ? `${txt(city)}, ${txt(state)}` : txt(cs);
    }

    // Advanced fallbacks for Origin and Destination if still "–"
    if (load.origin === "–" || load.destination === "–") {
      const csMatches = [];
      const allElements = row.querySelectorAll('span, div');
      for (const el of allElements) {
        const t = txt(el);
        // Matches e.g. "Chicago, IL" or "New York, NY"
        if (t.match(/^[A-Za-z\s.\-]{2,},\s*[A-Z]{2}$/)) {
          if (!csMatches.includes(t)) csMatches.push(t);
        }
      }
      if (csMatches.length >= 1 && load.origin === "–") load.origin = csMatches[0];
      if (csMatches.length >= 2 && load.destination === "–") load.destination = csMatches[1];
    }

    // ── 5. DEADHEAD ORIGIN / DESTINATION EXTRACTION ──
    const dhoEl = queryRobust(
      ['[data-test="load-dho-cell"]', '.dho-cell', '.deadhead-origin-cell'],
      ['data-test*="dho"', 'data-test*="deadhead-origin"'],
      'dho'
    );
    load.deadheadOrigin = dhoEl ? txt(dhoEl) : "";

    const dhdEl = queryRobust(
      ['[data-test="load-dhd-cell"]', '.dhd-cell', '.deadhead-destination-cell'],
      ['data-test*="dhd"', 'data-test*="deadhead-dest"'],
      'dhd'
    );
    load.deadheadDest = dhdEl ? txt(dhdEl) : "";

    // ── 6. COMPANY, EQUIPMENT TYPE, WEIGHT, LENGTH, LOAD TYPE EXTRACTION ──
    const compSmall = queryRobust(
      [
        ".cell-company-small .cell-container-small",
        ".cell-company .cell-container-small",
        ".cell-company-small",
        ".cell-company",
        '[data-test="load-company-cell"]'
      ],
      ['data-test*="company"'],
      'company'
    );

    load.equipmentType = "–";
    load.weight = "–";
    load.length = "–";
    load.loadType = "–";
    load.company = "–";
    load.truckType = "";

    // Extract independent equipment cell
    const eqCell = queryRobust(
      ['[data-test="load-eq-cell"]', '.equipment-cell', '.eq-cell'],
      ['data-test*="eq"'],
      'equipment'
    );
    if (eqCell && !isBlank(txt(eqCell))) {
      load.equipmentType = txt(eqCell);
    }

    if (compSmall) {
      // Equipment type from company container sub-spans
      if (load.equipmentType === "–") {
        const eqType = compSmall.querySelector(".equipment-type") || compSmall.querySelector('[class*="equipment"]');
        if (eqType) load.equipmentType = txt(eqType);
      }

      // Weight, length, load type values
      const infoDiv = compSmall.querySelector(".info-container > div") || compSmall.querySelector('[class*="info-container"] > div');
      if (infoDiv) {
        const parts = [];
        infoDiv.querySelectorAll("span").forEach((s) => {
          const t = txt(s);
          if (t && t !== "|" && !s.classList.contains("pipe")) parts.push(t);
        });
        load.weight = parts[1] || "–";
        load.length = parts[2] || "–";
        load.loadType = parts[3] || "–";
      } else {
        const weightEl = queryRobust(['[data-test="load-weight-cell"]'], [], 'weight');
        if (weightEl) load.weight = txt(weightEl);
        const lengthEl = queryRobust(['[data-test="load-length-cell"]'], [], 'length');
        if (lengthEl) load.length = txt(lengthEl);
      }

      // Company name
      const compEl =
        compSmall.querySelector(".company") ||
        compSmall.querySelector('[class*="company-name"]') ||
        compSmall.querySelector('[class*="company"]') ||
        compSmall.querySelector('a') ||
        compSmall.querySelector('span:not(.equipment-type)');

      if (compEl) {
        let name = txt(compEl);
        if (compEl === compSmall) {
          const firstSpan = compSmall.querySelector("span:not(.equipment-type)");
          name = firstSpan ? txt(firstSpan) : name.split("\n")[0].trim();
        }
        load.company = name;
      }

      // Fallback searches for company name
      if (load.company === "–" || !load.company) {
        const children = compSmall.querySelectorAll("span, div, a");
        for (const child of children) {
          const t = txt(child);
          if (t && t.length > 2 && !t.includes("mi") && !t.includes("lbs") && !t.includes("$") && !t.match(/^\d+$/)) {
            load.company = t;
            break;
          }
        }
      }
    }

    // Robust Company fallback (scan all text nodes for enterprise shape)
    if (load.company === "–" || !load.company) {
      const allSpans = row.querySelectorAll("span, div, a");
      for (const span of allSpans) {
        const t = txt(span);
        if (t.match(/\b(inc|llc|corp|logistics|transport|brokerage|broker|services|solutions|group|shipping|freight)\b/i)) {
          load.company = t;
          break;
        }
      }
    }

    // Factoring Logo
    const factoringLogo = row.querySelector(".factoring-logo") || row.querySelector('[class*="factoring"]') || row.querySelector('[class*="factor"]');
    load.factoring = factoringLogo ? "Yes" : "No";

    load.referenceId = "";
    load.pickupDate = "";
    load.pickupTime = "";
    load.deliveryTime = "";
    load.phone = "";
    load.email = "";
    load.companyLocation = "";

    // ── 7. EXPANDED DETAIL EXTRACTION ──
    const detail = row.querySelector(".table-row-detail") || row.querySelector('[class*="detail"]');
    if (detail) {
      load.isExpanded = true;
      const eqContainer = detail.querySelector('[data-test="details-container"]') || detail.querySelector('[class*="details-container"]');
      if (eqContainer) {
        const labels = eqContainer.querySelectorAll(".equipment-label .data-label") || eqContainer.querySelectorAll('[class*="label"]');
        const values = eqContainer.querySelectorAll(".equipment-data .data-item") || eqContainer.querySelectorAll('[class*="data"]');
        labels.forEach((lbl, i) => {
          const key = txt(lbl);
          const val = values[i] ? txt(values[i]) : "";
          if (key.includes("Load")) load.loadType = val || load.loadType;
          if (key.includes("Truck")) load.truckType = val;
          if (key.includes("Length")) load.length = val || load.length;
          if (key.includes("Weight")) load.weight = val || load.weight;
          if (key.includes("Reference")) load.referenceId = val;
        });
      }

      const dateEl = detail.querySelector(".date") || detail.querySelector('[class*="date"]');
      if (dateEl) load.pickupDate = txt(dateEl);

      const hourEls = detail.querySelectorAll(".hours") || detail.querySelectorAll('[class*="hours"]');
      if (hourEls.length >= 1) load.pickupTime = txt(hourEls[0]);
      if (hourEls.length >= 2) load.deliveryTime = txt(hourEls[1]);

      const phoneEl = detail.querySelector(".contacts__phone") || detail.querySelector('[class*="phone"]');
      if (phoneEl) load.phone = txt(phoneEl);

      const emailEl = detail.querySelector(".contacts__email a") || detail.querySelector('[class*="email"]') || detail.querySelector('a[href^="mailto:"]');
      if (emailEl) load.email = txt(emailEl);

      const compDetail = detail.querySelector('[data-test="company-details-container"]') || detail.querySelector('[class*="company-details"]');
      if (compDetail) {
        const compName = compDetail.querySelector(".company-details") || compDetail.querySelector('[class*="name"]');
        if (compName) load.company = txt(compName);
        const compEmail = compDetail.querySelector('a[href^="mailto:"]');
        if (compEmail) load.email = load.email || txt(compEmail);

        compDetail.querySelectorAll(".city-spacing, span").forEach((cs) => {
          const t = txt(cs);
          if (cs.classList.contains("light-text") || cs.className.includes("spacing") || t.includes(',')) {
            load.companyLocation = t;
          }
        });
      }
    }

    load.isEmpty = isEmptyLoad(load);
    load.rowStatus = load.isEmpty ? "Empty" : "Active";
    return load;
  }

  function extractSearchCriteria() {
    const criteria = {};
    const originInput = document.querySelector('[data-test="origin-input"]');
    const destInput = document.querySelector('[data-test="destination-input"]');
    const dhoInput = document.querySelector('[data-test="dho-input"]');
    const dhdInput = document.querySelector('[data-test="dhd-input"]');
    const resultsEl = document.querySelector('[data-test="results-counter"] span');
    const similarEl = document.querySelector('[data-test="similar-results-counter"] span');

    criteria.origin = originInput?.value || "Anywhere";
    criteria.destination = destInput?.value || "Anywhere";
    criteria.deadheadOrigin = dhoInput?.value || "";
    criteria.deadheadDest = dhdInput?.value || "";
    criteria.equipment = [];
    document.querySelectorAll("mat-chip").forEach((c) => {
      const t = txt(c).replace("cancel", "").trim();
      if (t) criteria.equipment.push(t);
    });
    criteria.totalResults = resultsEl ? txt(resultsEl) : "";
    criteria.similarResults = similarEl ? txt(similarEl) : "";
    return criteria;
  }

  let progressEl = null;

  function showProgress(collected, target, step, maxSteps, duplicates = 0) {
    try {
      chrome.runtime.sendMessage({
        action: "extractProgress",
        collected,
        target: target || 0,
        step,
        maxSteps,
        duplicates
      }).catch(() => { });
    } catch (e) { }

    if (!progressEl) {
      progressEl = document.createElement("div");
      progressEl.id = "dat-extractor-v2-progress";
      progressEl.style.cssText = [
        "position:fixed", "bottom:20px", "right:20px", "z-index:2147483647",
        "background:#0f766e", "color:#fff", "padding:14px 18px", "border-radius:10px",
        "font:600 13px system-ui,sans-serif", "box-shadow:0 8px 24px rgba(0,0,0,.35)",
        "max-width:280px",
      ].join(";");
      const msg = document.createElement("div");
      msg.id = "dat-v2-progress-msg";
      progressEl.appendChild(msg);
      const cancelBtn = document.createElement("button");
      cancelBtn.textContent = "Cancel";
      cancelBtn.style.cssText =
        "display:block;margin-top:8px;padding:6px 12px;border:none;border-radius:6px;cursor:pointer;font-weight:600;";
      cancelBtn.onclick = () => {
        window.__DAT_EXTRACTOR_V2_CANCEL__ = true;
        cancelBtn.textContent = "Cancelling…";
      };
      progressEl.appendChild(cancelBtn);
      document.body.appendChild(progressEl);
    }
    const targetTxt = target ? ` / ~${target}` : "";
    const dupTxt = duplicates ? `\nDuplicates: ${duplicates}` : "";
    progressEl.querySelector("#dat-v2-progress-msg").textContent =
      `Extracting: ${collected}${targetTxt} loads${dupTxt}\nScroll ${step}/${maxSteps}`;
  }

  function removeProgress() {
    if (progressEl) {
      progressEl.remove();
      progressEl = null;
    }
  }

  async function waitForRows() {
    if (document.hidden) {
      // In background tabs, requestAnimationFrame is suspended/throttled.
      // Use setTimeout directly to prevent the script from freezing.
      await sleep(scrollWaitMs + 150);
    } else {
      await new Promise((r) => {
        const t = setTimeout(() => r(), scrollWaitMs + 200); // safety fallback
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            clearTimeout(t);
            r();
          });
        });
      });
      await sleep(scrollWaitMs);
    }
  }

  function collectFromDom(byKey, stats, scrollTop) {
    const rows = getLoadRows(); // Natural DOM tree order - no visual sorting!

    rows.forEach((row, visibleIdx) => {
      try {
        if (isSkeletonRow(row)) {
          stats.skippedSkeleton += 1;
          return;
        }

        const rect = row.getBoundingClientRect();
        if (rect.height < 1 && rect.width < 1) return;

        // --- DOM Caching System ---
        const postingId = findPostingId(row);
        const textSig = row.textContent.slice(0, 100);

        let load;
        if (row.__extractedLoad && row.__extractedLoadPostingId === postingId && row.__extractedLoadTextSig === textSig) {
          load = row.__extractedLoad;
        } else {
          load = extractLoadFromRow(row);
          row.__extractedLoad = load;
          row.__extractedLoadPostingId = postingId;
          row.__extractedLoadTextSig = textSig;
        }

        const key = getCaptureKey(row, load, scrollTop, visibleIdx);
        load._captureKey = key;
        load._scrollTop = scrollTop;

        if (!byKey.has(key)) {
          byKey.set(key, load);
        } else if (scoreLoad(load) > scoreLoad(byKey.get(key))) {
          byKey.set(key, load);
        }
      } catch (e) {
        console.warn("DAT V2:", e);
      }
    });
  }

  function deduplicateLoads(loads) {
    const map = new Map();
    for (const load of loads) {
      const key = load._captureKey || getStableLoadKey(load);
      if (!map.has(key)) {
        map.set(key, load);
      } else if (scoreLoad(load) > scoreLoad(map.get(key))) {
        map.set(key, load);
      }
    }
    return Array.from(map.values());
  }

  function isNoResultsPresent() {
    if (getLoadRows().length > 0) {
      return false;
    }
    if (document.querySelector('.no-results') ||
      document.querySelector('[data-test="no-results"]') ||
      document.querySelector('.no-loads') ||
      document.querySelector('.empty-state') ||
      document.querySelector('[class*="no-results"]') ||
      document.querySelector('[class*="no-loads"]')) {
      return true;
    }
    const text = document.body.textContent.toLowerCase();
    return text.includes("no results found") ||
      text.includes("no loads found") ||
      text.includes("0 results") ||
      text.includes("0 loads");
  }

  function hasSkeletonRows() {
    if (isNoResultsPresent()) return false; // Not loading if "no results" is clearly visible
    const rows = getLoadRows();
    if (rows.length === 0) {
      // Check if there is an active mat-spinner or visible skeleton row loaders
      const spinner = document.querySelector('mat-spinner, .mat-spinner, .dat-table-row-loader, .animated-background, [class*="spinner"]');
      if (spinner && isElementVisible(spinner)) {
        return true;
      }
      return false; // No rows and no active spinner, assume idle
    }
    for (const r of rows) {
      if (isSkeletonRow(r)) return true;
    }
    return false;
  }

  async function waitForSkeletonsToLoad(maxWaitMs = null) {
    const limit = maxWaitMs !== null ? maxWaitMs : skeletonMaxWaitMs;
    const start = Date.now();
    while (Date.now() - start < limit) {
      if (window.__DAT_EXTRACTOR_V2_CANCEL__) return false;
      if (isNoResultsPresent()) return false;
      if (!hasSkeletonRows()) {
        return true; // All loaded
      }
      await sleep(150);
    }
    return false; // Timed out
  }

  async function extractAllLoads() {
    window.__DAT_EXTRACTOR_V2_CANCEL__ = false;
    const criteria = extractSearchCriteria();
    const targetTotal = parseTotalResults(criteria);
    let viewport = getScrollViewport();
    let rowHeight = measureRowHeight(viewport);

    const hasRows = getLoadRows().length > 0;
    if (!hasRows && (targetTotal === 0 || isNoResultsPresent())) {
      return {
        criteria,
        loads: [],
        targetTotal: 0,
        skipped: 0,
        emptyCount: 0,
        scrollSteps: 0,
        incomplete: false,
        cancelled: false,
      };
    }

    const byKey = new Map();
    const stats = { skippedSkeleton: 0, scrollSteps: 0 };

    const clientHeight = viewport.clientHeight || 500;
    // Scroll step ratio dynamically configured by speed mode
    const scrollStep = Math.max(rowHeight * 4, Math.floor(clientHeight * scrollStepRatio));

    let currentScrollTop = 0;
    let reachedEnd = false;
    let stepCount = 0;
    let lastSize = 0;
    let stepsWithoutProgress = 0;

    // Estimate steps for the progress indicator
    const estimatedScrollHeight = targetTotal ? (targetTotal * rowHeight) : (viewport.scrollHeight || 1000);
    const estimatedSteps = Math.max(5, Math.ceil(estimatedScrollHeight / scrollStep) + 1);

    // Initial capture at the top
    setScrollTop(viewport, 0, targetTotal, rowHeight);
    await waitForRows();
    
    // Re-resolve viewport and row height now that rows are loaded!
    viewport = getScrollViewport();
    rowHeight = measureRowHeight(viewport);
    
    await waitForSkeletonsToLoad();
    collectFromDom(byKey, stats, 0);
    stats.scrollSteps += 1;
    stepCount += 1;

    let currentLoads = deduplicateLoads(Array.from(byKey.values()));
    let duplicates = byKey.size - currentLoads.length;
    showProgress(currentLoads.length, targetTotal, stepCount, estimatedSteps, duplicates);

    const MAX_SCROLL_STEPS = 500;
    while (!window.__DAT_EXTRACTOR_V2_CANCEL__ && !reachedEnd && stepCount < MAX_SCROLL_STEPS) {
      if (targetTotal && currentLoads.length >= targetTotal) {
        break;
      }

      // Re-resolve viewport dynamically
      viewport = getScrollViewport();

      // Sync with actual scroll top to prevent currentScrollTop from running away
      currentScrollTop = viewport.scrollTop;

      const maxScrollTop = getMaxScrollTop(viewport, targetTotal, rowHeight);

      // If we are at the absolute bottom of the current scroll height
      const maxScrollable = viewport.scrollHeight - viewport.clientHeight;
      if (currentScrollTop >= maxScrollable - 5) {
        // Wait for potential dynamic load/expansion of content
        let heightIncreased = false;
        const currentHeight = viewport.scrollHeight;
        for (let w = 0; w < 10; w++) {
          await sleep(150);
          if (viewport.scrollHeight > currentHeight + 5) {
            heightIncreased = true;
            break;
          }
        }

        if (!heightIncreased) {
          // Double check if there are loading skeletons or rows that haven't fully rendered
          await waitForRows();
          await waitForSkeletonsToLoad(1500);

          // Re-verify if scroll height is still not increased after loading wait
          if (viewport.scrollHeight <= currentHeight + 5) {
            // Truly reached the end of the lists
            reachedEnd = true;
            break;
          }
        }
      }

      if (currentScrollTop >= maxScrollTop - 5) {
        reachedEnd = true;
        break;
      }

      let nextScrollTop = currentScrollTop + scrollStep;
      if (nextScrollTop >= maxScrollTop) {
        nextScrollTop = maxScrollTop;
      }

      if (nextScrollTop === currentScrollTop) {
        reachedEnd = true;
        break;
      }

      // Set scroll position
      currentScrollTop = nextScrollTop;

      // Set scroll top with retries if viewport scroll doesn't update (dynamic verification)
      let actualScrollTop = currentScrollTop;
      for (let retry = 0; retry < 4; retry++) {
        setScrollTop(viewport, currentScrollTop, targetTotal, rowHeight);
        await sleep(60);
        if (Math.abs(viewport.scrollTop - currentScrollTop) < 5 || viewport.scrollTop >= maxScrollTop - 5) {
          actualScrollTop = viewport.scrollTop;
          break;
        }
        await sleep(120);
      }

      await waitForRows();
      await waitForSkeletonsToLoad();
      collectFromDom(byKey, stats, Math.round(actualScrollTop));

      currentLoads = deduplicateLoads(Array.from(byKey.values()));
      duplicates = byKey.size - currentLoads.length;

      // ── HYBRID VIRTUAL SCROLL RE-HYDRATION (Micro-scroll if stuck) ──
      if (currentLoads.length === lastSize) {
        stepsWithoutProgress++;
        if (stepsWithoutProgress >= 3) {
          // Perform micro-scroll up and down to trigger Angular change detection and re-hydrate cells
          setScrollTop(viewport, Math.max(0, actualScrollTop - 15), targetTotal, rowHeight);
          await sleep(150);
          setScrollTop(viewport, actualScrollTop, targetTotal, rowHeight);
          await sleep(150);
          collectFromDom(byKey, stats, Math.round(actualScrollTop));
          currentLoads = deduplicateLoads(Array.from(byKey.values()));
          duplicates = byKey.size - currentLoads.length;
          stepsWithoutProgress = 0;
        }
      } else {
        stepsWithoutProgress = 0;
      }
      lastSize = currentLoads.length;

      stats.scrollSteps += 1;
      stepCount += 1;
      showProgress(currentLoads.length, targetTotal, stepCount, estimatedSteps, duplicates);
    }

    let finalLoads = deduplicateLoads(Array.from(byKey.values()));

    // Enrich with directory details if not cancelled
    if (!window.__DAT_EXTRACTOR_V2_CANCEL__) {
      await enrichLoadsWithDirectoryData(finalLoads);
    }

    removeProgress();
    setScrollTop(viewport, 0, targetTotal, rowHeight);

    finalLoads.forEach((ld, i) => {
      ld.listIndex = i + 1;
    });

    return {
      criteria,
      loads: finalLoads,
      targetTotal: targetTotal || finalLoads.length,
      skipped: stats.skippedSkeleton,
      emptyCount: finalLoads.filter((l) => l.isEmpty).length,
      scrollSteps: stats.scrollSteps,
      incomplete: targetTotal ? (finalLoads.length < targetTotal && !reachedEnd) : false,
      cancelled: window.__DAT_EXTRACTOR_V2_CANCEL__,
    };
  }

  /** Render the deep-extracted detail for one load into the text report. */
  function appendDeepText(lines, ld) {
    const D = DEEP();
    if (!D || !ld.deep) return;
    const deep = ld.deep;
    const put = (label, value, pad = 16) => {
      const v = D.valueOrNull(value);
      if (v === null) return;
      lines.push(`│    ${String(label + ":").padEnd(pad)}${v}`);
    };

    const r = deep.rate || {};
    if (Object.values(r).some((v) => v != null && v !== "")) {
      lines.push(`│  RATE (detail)`);
      put("Total", r.rateTotal);
      put("Total trip", r.totalTrip);
      put("Rate/mile", r.ratePerMile);
      put("Total cost", r.totalCost);
      put("Spot rate", r.spotRate ? `${r.spotRate}${r.spotRatePerMile ? ` (${r.spotRatePerMile}/mi)` : ""}` : null);
      put("Spot basis", r.spotRateBasis);
      put("Market", r.rateMarket);
      put("Range", r.rateRange);
      put("Range/mile", r.rateRangePerMileLow && r.rateRangePerMileHigh ? `${r.rateRangePerMileLow} - ${r.rateRangePerMileHigh}` : null);
      put("Contract rate", r.contractRate || r.contractRateNote);
      put("Line haul", r.lineHaul);
      put("Fuel", r.fuelCost);
      put("Tolls", r.tolls);
      put("Detention", r.detention);
      put("Accessorials", r.accessorials);
    }

    const rt = deep.route || {};
    const stops = rt.stops || [];
    if (stops.length || rt.totalMiles || rt.routeText) {
      lines.push(`│  ROUTE (detail)`);
      put("Total miles", rt.totalMiles);
      put("Route", rt.routeText);
      stops.forEach((s, idx) => {
        const dh = s.deadheadMiles != null ? ` [DH ${s.deadheadMiles}]` : "";
        const when = [s.date, s.time].filter(Boolean).join(" ");
        lines.push(`│      ${idx + 1}. ${s.location}${dh}${when ? ` — ${when}` : ""}`);
      });
    }

    const t = deep.truck || {};
    if (Object.values(t).some((v) => v != null && v !== "")) {
      lines.push(`│  TRUCK / EQUIPMENT (detail)`);
      put("Truck", t.truckType);
      put("Equipment", t.equipmentType);
      put("Trailer", t.trailerType);
      put("Length", t.length);
      put("Weight", t.weight);
      put("Capacity", t.capacity);
      put("Dimensions", t.dimensions);
      put("Requirements", t.specialRequirements);
    }

    const d = deep.details || {};
    if (Object.values(d).some((v) => v != null && v !== "")) {
      lines.push(`│  LOAD (detail)`);
      put("Load ID", d.loadId);
      put("Load number", d.loadNumber);
      put("Load type", d.loadType);
      put("Status", d.loadStatus);
      put("Commodity", d.commodity);
      put("Reference ID", d.referenceId);
      put("Pickup", [d.pickupDate, d.pickupTime].filter(Boolean).join(" "));
      put("Delivery", [d.deliveryDate, d.deliveryTime].filter(Boolean).join(" "));
      put("Notes", d.notes);
    }

    const c = deep.company || {};
    if (Object.values(c).some((v) => v != null && v !== "")) {
      lines.push(`│  COMPANY (detail)`);
      put("Name", c.name);
      put("DBA", c.dbaName);
      put("MC number", c.mcNumber);
      put("Docket", c.docket);
      put("DOT number", c.dotNumber);
      put("Credit score", c.creditScore);
      put("Days to pay", c.daysToPay);
      put("Company type", c.companyType || c.entityType);
      put("Operating", c.operatingStatus);
      put("Insurance", c.insuranceCarrier);
      put("Coverage to", c.insuranceCoverageTo);
      put("Rating", c.rating);
    }

    const ct = deep.contact || {};
    if ((ct.emails || []).length || (ct.phones || []).length || ct.name) {
      lines.push(`│  CONTACT (detail)`);
      put("Name", ct.name);
      put("Title", ct.title);
      put("Phone", ct.phone);
      put("Mobile", ct.mobile);
      put("Fax", ct.fax);
      put("Email", ct.email);
      put("Website", ct.website);
      if ((ct.emails || []).length > 1) put("All emails", ct.emails.join("; "));
      if ((ct.phones || []).length > 1) put("All phones", ct.phones.join("; "));
    }

    const o = deep.office || {};
    const addr = o.address || {};
    if (o.name || o.addressRaw || o.phone || addr.city) {
      lines.push(`│  OFFICE`);
      put("Name", o.name);
      put("Address", o.addressRaw);
      put("Line 1", addr.line1);
      put("Line 2", addr.line2);
      put("City", addr.city);
      put("State", addr.state);
      put("ZIP", addr.zip);
      put("Country", addr.country);
      put("Phone", o.phone);
      put("Fax", o.fax);
      put("Email", o.email);
      put("Hours", o.hours);
    }

    const extra = deep.additionalData || {};
    const extraKeys = Object.keys(extra);
    if (extraKeys.length) {
      lines.push(`│  ADDITIONAL DATA (${extraKeys.length} unmapped fields)`);
      extraKeys.slice(0, 25).forEach((k) => put(k, extra[k], 24));
      if (extraKeys.length > 25) lines.push(`│      …and ${extraKeys.length - 25} more (see JSON export)`);
    }

    const ex = ld.extraction;
    if (ex) {
      lines.push(`│  EXTRACTION`);
      put("Status", ex.status);
      put("Fields", String(ex.fieldsExtracted ?? 0));
      put("Sections", (ex.sectionsVisited || []).join(", "));
      if ((ex.sectionsFailed || []).length) put("Failed", ex.sectionsFailed.join(", "));
      if (ex.retries) put("Retries", String(ex.retries));
      if ((ex.errors || []).length) put("Errors", ex.errors.map((e) => `${e.stage}: ${e.message}`).join(" | "));
    }
  }

  // ── Export format (matches main.py FIELD_PATTERNS) ──
  function formatOutput(criteria, loads, meta) {
    const lines = [];
    lines.push("═══════════════════════════════════════════════════════════════════");
    lines.push("          DAT ONE TMS — LOAD SEARCH RESULTS EXPORT (V2)");
    lines.push("═══════════════════════════════════════════════════════════════════");
    lines.push(`Exported: ${new Date().toLocaleString()}`);
    lines.push("");
    lines.push("── SEARCH CRITERIA ─────────────────────────────────────────────");
    lines.push(`  Origin:        ${criteria.origin}`);
    lines.push(`  Destination:   ${criteria.destination}`);
    if (criteria.equipment.length) lines.push(`  Equipment:     ${criteria.equipment.join(", ")}`);
    lines.push(`  Total Results: ${criteria.totalResults || loads.length}`);
    if (meta.skipped) lines.push(`  Skipped rows:  ${meta.skipped} (loading skeletons only)`);
    if (meta.emptyCount) lines.push(`  Empty rows:    ${meta.emptyCount}`);
    lines.push("");
    lines.push(`── LOADS (${loads.length} extracted) ──────────────────────────────────────`);
    lines.push("");

    for (const ld of loads) {
      const n = ld.listIndex;
      lines.push(`┌─ LOAD #${n} ${ld.isEmpty ? "[EMPTY]" : ""} ─────────────────────────────────────`);
      lines.push(`│  Status:         ${ld.rowStatus || "Active"}`);
      lines.push(`│  ROUTE`);
      lines.push(`│    Origin:        ${ld.origin}`);
      lines.push(`│    Destination:   ${ld.destination}`);
      lines.push(`│    Trip:          ${ld.tripMiles} mi`);
      if (ld.deadheadOrigin) lines.push(`│    DH-Origin:     ${ld.deadheadOrigin}`);
      if (ld.deadheadDest) lines.push(`│    DH-Dest:       ${ld.deadheadDest}`);
      lines.push(`│  PRICING`);
      lines.push(`│    Age:           ${ld.age}`);
      lines.push(`│    Rate:          ${ld.rate}`);
      lines.push(`│    Rate/Mile:     ${ld.ratePerMile}`);
      lines.push(`│  EQUIPMENT`);
      lines.push(`│    Type:          ${ld.equipmentType || "–"}`);
      if (ld.truckType) lines.push(`│    Truck:         ${ld.truckType}`);
      lines.push(`│    Weight:        ${ld.weight || "–"}`);
      lines.push(`│    Length:        ${ld.length || "–"}`);
      lines.push(`│    Load Type:     ${ld.loadType || "–"}`);
      if (ld.referenceId) lines.push(`│    Reference ID:  ${ld.referenceId}`);
      lines.push(`│    Factoring:     ${ld.factoring}`);
      lines.push(`│  COMPANY`);
      lines.push(`│    Name:          ${ld.company || "–"}`);
      if (ld.companyLocation) lines.push(`│    Location:      ${ld.companyLocation}`);
      if (ld.pickupDate || ld.pickupTime || ld.deliveryTime) {
        lines.push(`│  SCHEDULE`);
        if (ld.pickupDate) lines.push(`│    Pickup Date:   ${ld.pickupDate}`);
        if (ld.pickupTime) lines.push(`│    Pickup Time:   ${ld.pickupTime}`);
        if (ld.deliveryTime) lines.push(`│    Delivery Time: ${ld.deliveryTime}`);
      }
      if (ld.phone) lines.push(`│    Phone:         ${ld.phone}`);
      if (ld.email) lines.push(`│    Email:         ${ld.email}`);
      appendDeepText(lines, ld);
      lines.push(`│`);
      lines.push(`└─────────────────────────────────────────────────────────────`);
      lines.push("");
    }

    lines.push("═══════════════════════════════════════════════════════════════════");
    lines.push("                          END OF EXPORT");
    lines.push("═══════════════════════════════════════════════════════════════════");
    return lines.join("\n");
  }

  const CSV_COLUMNS = [
    ["Load No", (ld) => ld.listIndex],
    ["Status", (ld) => ld.rowStatus || ""],
    ["Origin", (ld) => ld.origin],
    ["Destination", (ld) => ld.destination],
    ["Trip", (ld) => ld.tripMiles],
    ["DH-Origin", (ld) => ld.deadheadOrigin],
    ["DH-Dest", (ld) => ld.deadheadDest],
    ["Age", (ld) => ld.age],
    ["Rate", (ld) => ld.rate],
    ["Rate/Mile", (ld) => ld.ratePerMile],
    ["Equipment", (ld) => ld.equipmentType],
    ["Truck", (ld) => ld.truckType],
    ["Weight", (ld) => ld.weight],
    ["Length", (ld) => ld.length],
    ["Load Type", (ld) => ld.loadType],
    ["Reference ID", (ld) => ld.referenceId],
    ["Factoring", (ld) => ld.factoring],
    ["Pickup Date", (ld) => ld.pickupDate],
    ["Pickup Time", (ld) => ld.pickupTime],
    ["Delivery Time", (ld) => ld.deliveryTime],
    ["Phone", (ld) => ld.phone],
    ["Email", (ld) => ld.email],
    ["Company", (ld) => ld.company],
    ["Company Location", (ld) => ld.companyLocation],
    ["Docket", (ld) => ld.dir_docket || ""],
    ["DotNumber", (ld) => ld.dir_dot_number || ""],
    ["EntityType", (ld) => ld.dir_gen_entity_type || ""],
    ["CoverageTo", (ld) => ld.dir_active_ins_coverage_to || ""],
    ["CreditScore", (ld) => ld.dir_credit_score || ""],
    ["InsuranceCarrier", (ld) => ld.dir_active_ins_carrier || ""],
  ];

  /**
   * Summary columns always come first and never change position, so existing
   * downstream sheets keep working. Deep columns are appended when any load in
   * the set actually carries deep data.
   */
  function getExportColumns(loads) {
    const D = DEEP();
    if (!D || !Array.isArray(loads) || !loads.some((l) => l && l.deep)) return CSV_COLUMNS;
    const deepCols = D.DEEP_COLUMNS.map(([header, path]) => [header, (ld) => D.deepValue(ld, path)]);
    return [...CSV_COLUMNS, ...deepCols];
  }

  function formatCSV(loads) {
    const esc = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const columns = getExportColumns(loads);
    const header = columns.map(([h]) => h).join(",");
    const rows = loads.map((ld) =>
      columns.map(([, fn]) => esc(fn(ld))).join(",")
    );
    return [header, ...rows].join("\n");
  }

  /** Nested, loss-free JSON records (section 22 of the spec). */
  function buildExportRecords(loads) {
    const D = DEEP();
    if (!D) return null;
    try {
      return loads.map((ld) => D.toExportRecord(ld));
    } catch (e) {
      console.warn("[DAT Extractor] Could not build nested export records:", e);
      return null;
    }
  }

  // ── Auto-Pilot Automation ──
  window.__DAT_AUTO_PILOT_STOP__ = false;
  window.__DAT_AUTO_PILOT_PAUSED__ = false;

  let autoPilotUI = null;

  function updateApStatus(text) {
    const el = document.getElementById("ap-status");
    if (el) {
      el.textContent = text;
    }
    console.log(`[AutoPilot Status]: ${text}`);
  }

  function createAutoPilotUI() {
    const existing = document.getElementById("dat-auto-pilot-ui");
    if (existing) {
      existing.remove();
      document.querySelector("#dat-auto-pilot-ui").remove()
    }

    autoPilotUI = document.createElement("div");
    autoPilotUI.id = "dat-auto-pilot-ui";
    autoPilotUI.style.cssText = [
      "position:fixed", "top:20px", "right:20px", "z-index:2147483647",
      "background:#0f172a", "color:#e2e8f0", "padding:16px 20px", "border-radius:12px",
      "font:13px system-ui,sans-serif", "box-shadow:0 10px 30px rgba(0,0,0,.5)",
      "max-width:320px", "border:1px solid #334155",
      "user-select:none"
    ].join(";");

    autoPilotUI.innerHTML = `
      <div id="ap-drag-handle" style="font-weight:600;font-size:15px;margin-bottom:8px;color:#14b8a6;cursor:grab;">Auto-Pilot Crawler</div>
      <div id="ap-status" style="margin-bottom:12px;font-size:12px;color:#94a3b8;">Initializing...</div>
      <div id="ap-stats" style="margin-bottom:16px;background:#1e293b;padding:10px;border-radius:6px;font-size:12px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;"><span>Permutation:</span> <strong id="ap-perm">0 / 0</strong></div>
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;"><span>Total Loads:</span> <strong id="ap-loads">0</strong></div>
        <div style="display:flex;justify-content:space-between;"><span>Current:</span> <strong id="ap-current" style="text-align:right;max-width:180px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">-</strong></div>
      </div>
      <div style="display:flex;gap:8px;">
        <button id="ap-pause-btn" style="flex:1;padding:8px;border:none;border-radius:6px;background:#334155;color:#fff;cursor:pointer;font-weight:600;">Pause</button>
        <button id="ap-stop-btn" style="flex:1;padding:8px;border:none;border-radius:6px;background:#b91c1c;color:#fff;cursor:pointer;font-weight:600;">Stop & Save CSV</button>
      </div>
    `;

    document.body.appendChild(autoPilotUI);

    const dragHandle = document.getElementById("ap-drag-handle");
    let isDragging = false, dragStartX, dragStartY, initialX, initialY;

    dragHandle.onmousedown = (e) => {
      isDragging = true;
      dragStartX = e.clientX;
      dragStartY = e.clientY;
      const rect = autoPilotUI.getBoundingClientRect();
      initialX = rect.left;
      initialY = rect.top;
      dragHandle.style.cursor = "grabbing";

      const onMouseMove = (ev) => {
        if (!isDragging) return;
        const dx = ev.clientX - dragStartX;
        const dy = ev.clientY - dragStartY;
        autoPilotUI.style.left = (initialX + dx) + "px";
        autoPilotUI.style.top = (initialY + dy) + "px";
        autoPilotUI.style.right = "auto";
      };

      const onMouseUp = () => {
        isDragging = false;
        dragHandle.style.cursor = "grab";
        document.removeEventListener("mousemove", onMouseMove);
        document.removeEventListener("mouseup", onMouseUp);
      };

      document.addEventListener("mousemove", onMouseMove);
      document.addEventListener("mouseup", onMouseUp);
    };

    document.getElementById("ap-pause-btn").onclick = (e) => {
      window.__DAT_AUTO_PILOT_PAUSED__ = !window.__DAT_AUTO_PILOT_PAUSED__;
      e.target.textContent = window.__DAT_AUTO_PILOT_PAUSED__ ? "Resume" : "Pause";
      e.target.style.background = window.__DAT_AUTO_PILOT_PAUSED__ ? "#d97706" : "#334155";
      if (window.__DAT_AUTO_PILOT_PAUSED__) {
        updateApStatus("Paused. Click Resume to continue.");
      } else {
        updateApStatus("Resuming automation...");
      }
    };

    document.getElementById("ap-stop-btn").onclick = () => {
      window.__DAT_AUTO_PILOT_STOP__ = true;
      updateApStatus("Stopping... (Waiting for current search to finish)");
    };
  }

  function updateAutoPilotUI(permStr, currentIdx, totalPerms, totalLoads) {
    if (!autoPilotUI) return;
    document.getElementById("ap-perm").textContent = `${currentIdx} / ${totalPerms}`;
    document.getElementById("ap-loads").textContent = totalLoads;
    document.getElementById("ap-current").textContent = permStr;
    document.getElementById("ap-current").title = permStr;
    updateApStatus("Extracting results...");
  }

  function findInputByQuery(searchTerm) {
    const term = searchTerm.toLowerCase();
    const selectors = [
      `[data-test="${term}-input"]`,
      `[data-test*="${term}"]`,
      `input[placeholder*="${searchTerm}"]`,
      `input[placeholder*="${term}"]`,
      `input[aria-label*="${searchTerm}"]`,
      `input[aria-label*="${term}"]`,
      `input[id*="${term}"]`,
      `input[name*="${term}"]`
    ];
    for (const sel of selectors) {
      try {
        const el = document.querySelector(sel);
        if (el && el.tagName === 'INPUT') return el;
      } catch (e) {}
    }
    const labels = Array.from(document.querySelectorAll('mat-label, label, .mat-form-field-label, span, div'));
    for (const label of labels) {
      const text = label.textContent.trim().toLowerCase();
      if (text === term || (text.includes(term) && text.length < 50)) {
        const container = label.closest('mat-form-field, .input-container, .form-field, div');
        if (container) {
          const input = container.querySelector('input');
          if (input) return input;
        }
        const parent = label.parentElement;
        if (parent) {
          const input = parent.querySelector('input');
          if (input) return input;
        }
      }
    }
    return findInputByLabel(searchTerm);
  }

  function findInputByLabel(labelText) {
    const labels = Array.from(document.querySelectorAll('mat-label, label, .mat-form-field-label, span'));
    const label = labels.find(l => l.textContent.toLowerCase().includes(labelText.toLowerCase()));
    if (label) {
      const formField = label.closest('mat-form-field') || label.closest('.input-container');
      if (formField) {
        return formField.querySelector('input');
      }
    }
    return null;
  }

  async function clearInput(input) {
    const parent = input.closest('mat-form-field') || input.closest('.input-container') || input.parentElement;
    if (parent) {
      const clearIcons = parent.querySelectorAll('mat-icon, button');
      for (const icon of clearIcons) {
        if (icon.textContent.includes('close') || icon.textContent.includes('cancel') || icon.getAttribute('aria-label') === 'Clear') {
          icon.click();
          await sleep(200);
        }
      }
    }
    input.focus();
    input.select();
    document.execCommand('delete'); // Triggers native Angular updates

    const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set;
    if (nativeSetter) nativeSetter.call(input, '');
    else input.value = '';

    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
    await sleep(300);
  }

  // Simulate typing into an input character by character so Angular detects changes
  function simulateTyping(input, text) {
    input.focus();
    input.dispatchEvent(new Event('focus', { bubbles: true }));
    input.dispatchEvent(new Event('focusin', { bubbles: true }));
    input.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    input.select(); // Ensure we overwrite if anything is left

    // Check if the input is actually focused in the document.
    // If not, we cannot use execCommand because it will write to the wrong element!
    const isFocused = (document.activeElement === input);

    // Try native command first if focused (works best with Angular/React)
    if (isFocused && document.execCommand('insertText', false, text)) {
      input.dispatchEvent(new Event('input', { bubbles: true }));
    } else {
      // Fallback: set value character by character (safest when focus fails)
      const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set;
      // Clear existing value first
      if (nativeSetter) nativeSetter.call(input, '');
      else input.value = '';

      for (const char of text) {
        // Keydown event
        input.dispatchEvent(new KeyboardEvent('keydown', { key: char, code: `Key${char.toUpperCase()}`, bubbles: true }));

        // Set value
        if (nativeSetter) nativeSetter.call(input, input.value + char);
        else input.value = input.value + char;

        // Input and keyup events
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new KeyboardEvent('keyup', { key: char, code: `Key${char.toUpperCase()}`, bubbles: true }));
      }
    }
    input.dispatchEvent(new Event('change', { bubbles: true }));
  }

  async function setAutocompleteValue(testId, value) {
    const term = testId.split('-')[0];
    const input = findInputByQuery(term);
    if (!input) return false;

    // Dispatch focus and click events to trigger autocomplete component activation
    input.focus();
    input.dispatchEvent(new Event('focus', { bubbles: true }));
    input.dispatchEvent(new Event('focusin', { bubbles: true }));
    input.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    await sleep(selectWaitMs / 3);

    await clearInput(input);

    // Focus and click again before typing
    input.focus();
    input.dispatchEvent(new Event('focus', { bubbles: true }));
    input.dispatchEvent(new Event('focusin', { bubbles: true }));
    input.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    await sleep(selectWaitMs / 3);

    // Type the value character by character
    simulateTyping(input, value);

    // Dynamically wait up to 4 seconds for mat-option dropdown options to appear in the DOM
    const startOpt = Date.now();
    let options = [];
    while (Date.now() - startOpt < 4000) {
      options = document.querySelectorAll("mat-option");
      if (options.length > 0) {
        await sleep(100); // short settle delay
        options = document.querySelectorAll("mat-option"); // refresh options reference
        break;
      }
      await sleep(100);
    }

    // Look for and click the matching autocomplete option
    if (options.length > 0) {
      // First pass: exact match
      for (const opt of options) {
        const optText = opt.textContent.trim().toLowerCase();
        if (optText === value.toLowerCase()) {
          opt.click();
          await sleep(selectWaitMs / 2);
          input.blur();
          input.dispatchEvent(new Event('blur', { bubbles: true }));
          input.dispatchEvent(new Event('focusout', { bubbles: true }));
          return true;
        }
      }

      // Second pass: contains / starts-with / similar
      for (const opt of options) {
        const optText = opt.textContent.trim().toLowerCase();
        if (optText.includes(value.toLowerCase()) || value.toLowerCase().includes(optText)) {
          opt.click();
          await sleep(selectWaitMs / 2);
          input.blur();
          input.dispatchEvent(new Event('blur', { bubbles: true }));
          input.dispatchEvent(new Event('focusout', { bubbles: true }));
          return true;
        }
      }

      // Fallback: select first option
      options[0].click();
      await sleep(selectWaitMs / 2);
      input.blur();
      input.dispatchEvent(new Event('blur', { bubbles: true }));
      input.dispatchEvent(new Event('focusout', { bubbles: true }));
      return true;
    }

    // Keyboard Fallback (if overlay options are not found in the DOM due to background throttling)
    console.log(`[DAT Extractor] No mat-option elements visible in DOM for autocomplete. Triggering keyboard fallback (ArrowDown + Enter)...`);

    // Dispatch ArrowDown to select/highlight first option in the dropdown list
    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', code: 'ArrowDown', bubbles: true }));
    await sleep(200);
    input.dispatchEvent(new KeyboardEvent('keyup', { key: 'ArrowDown', code: 'ArrowDown', bubbles: true }));
    await sleep(300);

    // Dispatch Enter to confirm selection
    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
    await sleep(150);
    input.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', bubbles: true }));
    await sleep(300);

    input.blur();
    input.dispatchEvent(new Event('blur', { bubbles: true }));
    input.dispatchEvent(new Event('focusout', { bubbles: true }));
    return true; // Return true as we attempted keyboard fallback selection
  }

  // Map of user-friendly equipment names to DAT dropdown labels
  const EQUIPMENT_LABEL_MAP = {
    "vans (standard)": "Vans (Standard)",
    "flatbeds": "Flatbeds",
    "reefers": "Reefers",
    "conestogas": "Conestogas",
    "containers": "Containers",
    "decks (specialized)": "Decks (Specialized)",
    "decks (standard)": "Decks (Standard)",
    "dry bulk": "Dry Bulk",
    "hazardous materials": "Hazardous Materials",
    "other equipment": "Other Equipment",
    "tankers": "Tankers",
    "vans (specialized)": "Vans (Specialized)",
    // Short codes
    "v": "Vans (Standard)",
    "f": "Flatbeds",
    "r": "Reefers",
    "n": "Conestogas",
    "c": "Containers",
    "k": "Decks (Specialized)",
    "d": "Decks (Standard)",
    "b": "Dry Bulk",
    "z": "Hazardous Materials",
    "o": "Other Equipment",
    "t": "Tankers",
    "s": "Vans (Specialized)",
  };

  async function setEquipmentType(value) {
    // 1. Clear ALL existing chips by clicking their cancel icons
    let cleared = false;
    for (let attempt = 0; attempt < 3; attempt++) {
      const chips = document.querySelectorAll('mat-chip, mat-chip-row');
      if (chips.length === 0) { cleared = true; break; }
      for (const chip of chips) {
        const cancelIcon = chip.querySelector('[matChipRemove], .mat-mdc-chip-remove, mat-icon, button');
        if (cancelIcon) {
          cancelIcon.click();
        } else {
          chip.click(); // Fallback
        }
        await sleep(200);
      }
      await sleep(300);
    }

    // 2. Resolve the label
    const searchLabel = EQUIPMENT_LABEL_MAP[value.toLowerCase()] || value;

    // 3. Type into the equipment input
    let input = document.querySelector('[data-test="equipment-type-dropdown"]');
    if (!input) {
      input = findInputByLabel('equipment') ||
        document.querySelector('input[placeholder*="Equipment"]') ||
        document.querySelector('input[placeholder*="equipment"]');
    }

    // Safety check: if fallback inputs are matched, make sure they are not origin/destination fields
    if (!input) {
      const candidates = document.querySelectorAll('mat-chip-grid input, mat-chip-list input, mat-form-field input, input');
      for (const cand of candidates) {
        const dataTest = cand.getAttribute('data-test') || '';
        const placeholder = cand.getAttribute('placeholder') || '';
        const name = cand.getAttribute('name') || '';

        // Skip explicitly matched origin/destination inputs
        if (dataTest.includes('origin') || dataTest.includes('destination') || dataTest.includes('dest')) continue;
        if (placeholder.toLowerCase().includes('origin') || placeholder.toLowerCase().includes('destination') || placeholder.toLowerCase().includes('dest')) continue;
        if (name.toLowerCase().includes('origin') || name.toLowerCase().includes('destination') || name.toLowerCase().includes('dest')) continue;

        // Ensure the input's container is equipment-related
        const container = cand.closest('mat-form-field') || cand.closest('.input-container') || cand.parentElement;
        if (container && (
          container.textContent.toLowerCase().includes('equipment') ||
          container.innerHTML.toLowerCase().includes('equipment') ||
          container.innerHTML.toLowerCase().includes('eq-cell')
        )) {
          input = cand;
          break;
        }
      }
    }

    if (!input) {
      console.error("AutoPilot: Could not find equipment input");
      // Don't completely fail, return true so loop continues. The previous equipment will just be used.
      return true;
    }

    input.focus();
    input.dispatchEvent(new Event('focus', { bubbles: true }));
    input.dispatchEvent(new Event('focusin', { bubbles: true }));
    input.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    await sleep(selectWaitMs / 3);

    // Type the first few characters to trigger autocomplete
    const searchTerm = searchLabel.split(/[\s(,]/)[0]; // e.g. "Vans", "Flatbeds", etc.
    simulateTyping(input, searchTerm);

    // Dynamically wait up to 4 seconds for mat-option dropdown options to appear in the DOM
    const startOpt = Date.now();
    let options = [];
    while (Date.now() - startOpt < 4000) {
      options = document.querySelectorAll('mat-option');
      if (options.length > 0) {
        await sleep(100); // short settle delay
        options = document.querySelectorAll('mat-option'); // refresh options reference
        break;
      }
      await sleep(100);
    }

    // 4. Click the matching mat-option from the dropdown
    let clicked = false;

    if (options.length > 0) {
      // First pass: exact match
      for (const opt of options) {
        const optText = opt.textContent.trim().toLowerCase();
        if (optText === searchLabel.toLowerCase()) {
          opt.click();
          clicked = true;
          console.log("AutoPilot: Selected equipment (exact match):", opt.textContent.trim());
          break;
        }
      }

      // Second pass: label match
      if (!clicked) {
        for (const opt of options) {
          const optText = opt.textContent.trim().toLowerCase();
          if (optText.includes(searchLabel.toLowerCase())) {
            opt.click();
            clicked = true;
            console.log("AutoPilot: Selected equipment (label match):", opt.textContent.trim());
            break;
          }
        }
      }

      // Third pass: term/fallback match
      if (!clicked) {
        for (const opt of options) {
          const optText = opt.textContent.trim().toLowerCase();
          if (optText.includes(searchTerm.toLowerCase()) || optText.startsWith(searchTerm.toLowerCase().charAt(0))) {
            opt.click();
            clicked = true;
            console.log("AutoPilot: Selected equipment (fallback match):", opt.textContent.trim());
            break;
          }
        }
      }

      if (!clicked) {
        console.warn("AutoPilot: Guessed equipment option for:", searchLabel);
        options[0].click();
        clicked = true;
      }
    } else {
      // Keyboard Fallback (if overlay options are not found in the DOM due to background throttling)
      console.log(`[DAT Extractor] No mat-option elements visible in DOM for equipment. Triggering keyboard fallback (ArrowDown + Enter)...`);

      // Dispatch ArrowDown to select/highlight first option in the dropdown list
      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', code: 'ArrowDown', bubbles: true }));
      await sleep(200);
      input.dispatchEvent(new KeyboardEvent('keyup', { key: 'ArrowDown', code: 'ArrowDown', bubbles: true }));
      await sleep(300);

      // Dispatch Enter to confirm selection
      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
      await sleep(150);
      input.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', bubbles: true }));
      await sleep(300);
      clicked = true;
    }

    await sleep(selectWaitMs / 2);
    if (input) {
      input.blur();
      input.dispatchEvent(new Event('blur', { bubbles: true }));
      input.dispatchEvent(new Event('focusout', { bubbles: true }));
    }

    // As long as there are chips now, it counts as success
    const newChips = document.querySelectorAll('mat-chip, mat-chip-row');
    return newChips.length > 0 || clicked;
  }

  async function setLoadType(value) {
    const selects = document.querySelectorAll('mat-select');
    let targetSelect = null;
    for (const sel of selects) {
      const text = sel.textContent.trim().toLowerCase();
      if (text.includes("full") || text.includes("partial") || text.includes("load type") || text.includes("both")) {
        targetSelect = sel;
        break;
      }
    }
    if (!targetSelect && selects.length > 0) targetSelect = selects[0];

    if (targetSelect) {
      targetSelect.focus();
      targetSelect.dispatchEvent(new Event('focus', { bubbles: true }));
      targetSelect.dispatchEvent(new Event('focusin', { bubbles: true }));
      targetSelect.dispatchEvent(new MouseEvent('click', { bubbles: true }));
      await sleep(selectWaitMs);

      const options = document.querySelectorAll('mat-option');
      let found = false;

      if (options.length > 0) {
        for (const opt of options) {
          const text = opt.textContent.trim().toLowerCase();
          if (text.includes(value.toLowerCase()) ||
            (value.toLowerCase().includes("full & partial") && text.includes("both")) ||
            (value.toLowerCase().includes("both") && text.includes("full & partial"))) {
            opt.click();
            found = true;
            break;
          }
        }
        if (!found) {
          options[options.length - 1].click();
          found = true;
        }
      } else {
        // Keyboard Fallback (if overlay options are not found in the DOM due to background throttling)
        console.log(`[DAT Extractor] No mat-option elements visible in DOM for load type. Triggering keyboard fallback (ArrowDown + Enter)...`);

        // Dispatch ArrowDown to highlight option
        targetSelect.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', code: 'ArrowDown', bubbles: true }));
        await sleep(200);
        targetSelect.dispatchEvent(new KeyboardEvent('keyup', { key: 'ArrowDown', code: 'ArrowDown', bubbles: true }));
        await sleep(300);

        // Dispatch Enter to select
        targetSelect.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
        await sleep(150);
        targetSelect.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', bubbles: true }));
        await sleep(300);
        found = true;
      }

      await sleep(selectWaitMs / 2);
      return found;
    }
    return false;
  }

  // Wait for the search button to become enabled
  async function waitForSearchButtonEnabled(maxWaitMs = 10000) {
    const start = Date.now();
    while (Date.now() - start < maxWaitMs) {
      const btn = document.querySelector('[data-test="search-button"]') || 
                  Array.from(document.querySelectorAll('button')).find(el => {
                    const t = el.textContent.trim().toLowerCase();
                    return t.includes('search') || t.includes('find');
                  });
      if (btn && !btn.disabled && !btn.classList.contains('mat-button-disabled')) {
        return true;
      }
      if (document.activeElement && document.activeElement.blur) {
        document.activeElement.blur();
      }
      await sleep(300);
    }
    return false;
  }

  async function clickSearch() {
    // Wait for button to be enabled
    updateApStatus("Waiting for Search button to enable...");
    const enabled = await waitForSearchButtonEnabled(10000);

    const btn = document.querySelector('[data-test="search-button"]') || 
                Array.from(document.querySelectorAll('button')).find(el => {
                  const t = el.textContent.trim().toLowerCase();
                  return t.includes('search') || t.includes('find');
                });
    if (!btn) {
      console.error("AutoPilot: Search button not found in DOM");
      return false;
    }

    if (enabled) {
      // Button is enabled, click it normally
      btn.click();
      console.log("AutoPilot: Clicked search button (enabled)");
      return true;
    }

    console.warn("AutoPilot: Search button still disabled. Form is invalid. Failing search click.");
    return false;
  }

  // Wait for the old results to clear and new results to start loading
  async function waitForNewResults(maxWaitMs = 15000, oldFirstId = null, oldCount = null) {
    const start = Date.now();
    let sawLoading = false;
    while (Date.now() - start < maxWaitMs) {
      if (window.__DAT_EXTRACTOR_V2_CANCEL__) break;
      const spinner = document.querySelector('mat-spinner');
      if (hasSkeletonRows() || (spinner && isElementVisible(spinner))) {
        sawLoading = true;
        break;
      }

      // If no spinner, check if state changed instantly (fast cache/API)
      const currentCriteria = extractSearchCriteria();
      const currentCount = currentCriteria.totalResults;
      const currentRows = getLoadRows();
      const currentFirstId = currentRows.length > 0 ? findPostingId(currentRows[0]) : null;

      const countChanged = (currentCount !== oldCount) && currentCount !== "";
      const idChanged = (currentFirstId !== oldFirstId) && currentFirstId !== null;
      const noResults = document.querySelector('.no-results') || document.querySelector('[data-test="no-results"]');

      if (countChanged || idChanged || noResults) {
        break;
      }

      await sleep(200);
    }

    if (sawLoading) {
      // Wait for skeletons to disappear
      await waitForSkeletonsToLoad(20000);
    }

    await sleep(1000); // Give Angular a moment to render everything
  }

  async function startAutoPilot(config) {
    window.__DAT_AUTO_PILOT_STOP__ = false;
    window.__DAT_AUTO_PILOT_PAUSED__ = false;
    createAutoPilotUI();

    const { states, equipment, loadTypes } = config;
    const permutations = [];

    for (const origin of states) {
      for (const dest of states) {
        if (origin.toLowerCase() === dest.toLowerCase()) continue;
        for (const eq of equipment) {
          for (const lt of loadTypes) {
            permutations.push({ origin, dest, eq, lt });
          }
        }
      }
    }

    if (permutations.length === 0) {
      updateApStatus("No valid permutations found.");
      return;
    }

    let allExtractedLoads = [];
    let skippedPerms = 0;
    const totalPerms = permutations.length;

    for (let i = 0; i < totalPerms; i++) {
      while (window.__DAT_AUTO_PILOT_PAUSED__) {
        if (window.__DAT_AUTO_PILOT_STOP__) break;
        await sleep(500);
      }
      if (window.__DAT_AUTO_PILOT_STOP__) break;

      const p = permutations[i];
      const permStr = `${p.origin} -> ${p.dest} | ${p.eq} | ${p.lt}`;
      updateAutoPilotUI(permStr, i + 1, totalPerms, allExtractedLoads.length);

      // === STEP 1: Fill form fields ===
      updateApStatus("Setting origin...");
      await setAutocompleteValue("origin-input", p.origin);
      await sleep(1000);

      updateApStatus("Setting destination...");
      await setAutocompleteValue("destination-input", p.dest);
      await sleep(1000);

      updateApStatus("Setting equipment type...");
      const eqOk = await setEquipmentType(p.eq);
      await sleep(1000);
      if (!eqOk) {
        console.warn("AutoPilot: Skipping permutation, could not set equipment:", p.eq);
        updateApStatus(`Skipped (equipment: ${p.eq})`);
        skippedPerms++;
        await sleep(1000);
        continue;
      }

      updateApStatus("Setting load type...");
      await setLoadType(p.lt);
      await sleep(1000);

      // === PRE-SEARCH STATE ===
      const preSearchRows = getLoadRows();
      const preSearchFirstId = preSearchRows.length > 0 ? findPostingId(preSearchRows[0]) : null;
      const preSearchCriteria = extractSearchCriteria();
      const preSearchCount = preSearchCriteria.totalResults;

      // === STEP 2: Click search ===
      updateApStatus("Clicking search...");
      const clicked = await clickSearch();
      if (!clicked) {
        updateApStatus(`Search button failed for: ${permStr}`);
        console.warn("AutoPilot: Search button failed for:", permStr);
        skippedPerms++;
        await sleep(2000);
        continue;
      }

      // === STEP 3: Wait for new results to load ===
      updateApStatus("Waiting for results to load...");
      await waitForNewResults(15000, preSearchFirstId, preSearchCount);

      // === STEP 4: Extract ===
      updateApStatus("Extracting results...");
      try {
        const result = await extractAllLoads();
        const loadCount = result.loads.length;
        // Tag loads with their permutation context
        const mappedLoads = result.loads.map(ld => ({
          ...ld,
          _apOrigin: p.origin,
          _apDest: p.dest,
          _apEq: p.eq,
          _apLt: p.lt
        }));
        allExtractedLoads.push(...mappedLoads);
        updateAutoPilotUI(permStr, i + 1, totalPerms, allExtractedLoads.length);
        console.log(`AutoPilot: ${permStr} => ${loadCount} loads (total: ${allExtractedLoads.length})`);
      } catch (err) {
        console.error("AutoPilot extraction error:", err);
        updateApStatus(`Extract error: ${err.message}`);
      }

      updateApStatus("Waiting before next search...");
      await sleep(1500);
    }

    updateApStatus("Automation Complete. Ready to Export.");

    // Remove old pause/stop buttons, show export buttons
    document.getElementById("ap-pause-btn").style.display = "none";
    document.getElementById("ap-stop-btn").textContent = "Close Panel";
    document.getElementById("ap-stop-btn").onclick = () => {
      if (autoPilotUI) autoPilotUI.remove();
      autoPilotUI = null;
    };

    if (allExtractedLoads.length > 0) {
      allExtractedLoads.forEach((ld, i) => ld.listIndex = i + 1);

      const apStats = document.getElementById("ap-stats");
      apStats.innerHTML = `
        <div style="margin-bottom:8px;font-weight:600;font-size:13px;color:#14b8a6;">Extraction Complete: ${allExtractedLoads.length} loads</div>
        <div style="display:flex;flex-wrap:wrap;gap:6px;">
          <button id="ap-exp-csv" style="padding:8px;border:none;border-radius:4px;background:#0d9488;color:#fff;cursor:pointer;font-size:12px;flex:1;font-weight:600;">CSV</button>
          <button id="ap-exp-json" style="padding:8px;border:none;border-radius:4px;background:#0d9488;color:#fff;cursor:pointer;font-size:12px;flex:1;font-weight:600;">JSON</button>
          <button id="ap-exp-txt" style="padding:8px;border:none;border-radius:4px;background:#0d9488;color:#fff;cursor:pointer;font-size:12px;flex:1;font-weight:600;">TXT</button>
          <button id="ap-exp-xlsx" style="padding:8px;border:none;border-radius:4px;background:#0284c7;color:#fff;cursor:pointer;font-size:12px;flex:1;font-weight:600;">Excel</button>
        </div>
      `;

      const apCols = [
        ["Search Origin", (ld) => ld._apOrigin],
        ["Search Dest", (ld) => ld._apDest],
        ["Search Equipment", (ld) => ld._apEq],
        ["Search Load Type", (ld) => ld._apLt]
      ];
      const allCols = [...apCols, ...getExportColumns(allExtractedLoads)];

      const downloadFile = (content, filename, type) => {
        const blob = new Blob([content], { type });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(a.href);
      };

      document.getElementById("ap-exp-csv").onclick = () => {
        const esc = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
        const header = allCols.map(([h]) => h).join(",");
        const rows = allExtractedLoads.map((ld) =>
          allCols.map(([, fn]) => esc(fn(ld))).join(",")
        );
        downloadFile([header, ...rows].join("\n"), `dat-autopilot-${Date.now()}.csv`, "text/csv");
      };

      document.getElementById("ap-exp-json").onclick = () => {
        downloadFile(JSON.stringify(allExtractedLoads, null, 2), `dat-autopilot-${Date.now()}.json`, "application/json");
      };

      document.getElementById("ap-exp-txt").onclick = () => {
        const txtContent = formatOutput({ origin: "AutoPilot", destination: "All", equipment: [] }, allExtractedLoads, {});
        downloadFile(txtContent, `dat-autopilot-${Date.now()}.txt`, "text/plain");
      };

      document.getElementById("ap-exp-xlsx").onclick = () => {
        if (typeof XLSX === "undefined") {
          alert("SheetJS (XLSX) library not found in extension context.");
          return;
        }
        try {
          const headers = [
            "postingId", "timestamp", "age", "rate", "ratePerMile", "tripMiles",
            "origin", "destination", "deadheadOrigin", "deadheadDest", "equipmentType",
            "weight", "length", "loadType", "company", "truckType", "factoring",
            "referenceId", "pickupDate", "pickupTime", "deliveryTime", "phone",
            "email", "companyLocation", "isEmpty", "rowStatus", "_captureKey",
            "listIndex", "_apOrigin", "_apDest", "_apEq", "_apLt",
            "Docket", "DotNumber", "EntityType", "CoverageTo", "CreditScore", "InsuranceCarrier"
          ];
          const wsData = [headers];
          allExtractedLoads.forEach(ld => {
            const rowData = {};
            headers.forEach(k => {
              if (k === "Docket") rowData[k] = ld.dir_docket;
              else if (k === "DotNumber") rowData[k] = ld.dir_dot_number;
              else if (k === "EntityType") rowData[k] = ld.dir_gen_entity_type;
              else if (k === "CoverageTo") rowData[k] = ld.dir_active_ins_coverage_to;
              else if (k === "CreditScore") rowData[k] = ld.dir_credit_score;
              else if (k === "InsuranceCarrier") rowData[k] = ld.dir_active_ins_carrier;
              else rowData[k] = ld[k];
            });
            wsData.push(headers.map(k => (typeof rowData[k] === "boolean") ? rowData[k] : (rowData[k] ?? "")));
          });
          const ws = XLSX.utils.aoa_to_sheet(wsData);
          const wb = XLSX.utils.book_new();
          XLSX.utils.book_append_sheet(wb, ws, "Loads");
          const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
          downloadFile(wbout, `dat-autopilot-${Date.now()}.xlsx`, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
        } catch (e) {
          console.error(e);
          alert("Excel export failed: " + e.message);
        }
      };
    } else {
      document.getElementById("ap-stats").innerHTML = `<div style="color:#ef4444;font-weight:600;">No loads extracted.</div>`;
    }
  }

  // Per-task timeout wrapper — prevents getting stuck on any single combination
  function withTimeout(promise, ms, label) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error(`Timeout after ${ms}ms: ${label}`)), ms);
      promise.then(
        val => { clearTimeout(timer); resolve(val); },
        err => { clearTimeout(timer); reject(err); }
      );
    });
  }

  async function waitForSearchFormLoaded(timeoutMs = 30000) {
    console.log("[DAT Extractor] Waiting for search form inputs to become available in DOM...");
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      if (window.__DAT_EXTRACTOR_V2_CANCEL__ || window.__DAT_AUTO_PILOT_STOP__) {
        throw new Error("Autopilot stopped during search form initialization");
      }
      const input = findInputByQuery("origin");
      if (input) {
        console.log("[DAT Extractor] Search form loaded successfully.");
        return true;
      }
      if (window.location.href.includes("/login") || document.querySelector('input[type="password"]')) {
        throw new Error("Redirected to login page. Please ensure you are logged in to DAT ONE.");
      }
      await sleep(500);
    }
    throw new Error("Timeout waiting for search form to load in the DOM.");
  }

  async function executeBatch(tasks) {
    let allExtractedLoads = [];
    const taskStats = [];
    const TASK_TIMEOUT_MS = 10800000; // 3 hours (10800000 ms)

    await waitForSearchFormLoaded();

    for (let i = 0; i < tasks.length; i++) {
      // Check STOP signal between every task
      if (window.__DAT_EXTRACTOR_V2_CANCEL__ || window.__DAT_AUTO_PILOT_STOP__) {
        console.log(`[Batch] STOP signal detected, exiting after ${i} tasks`);
        break;
      }

      const p = tasks[i];
      console.log(`[Batch] Setting route once for Task ${i + 1}/${tasks.length}: ${p.origin} -> ${p.dest} [Load Type: ${p.lt}]`);

      let activeStateAcquired = false;
      const releaseLock = async () => {
        if (activeStateAcquired) {
          activeStateAcquired = false;
          await releaseActiveState().catch(() => {});
        }
      };

      const acquireLock = async () => {
        if (!activeStateAcquired) {
          try {
            await requestActiveState();
            activeStateAcquired = true;
          } catch (e) {
            console.warn("Failed to acquire active state:", e);
          }
        }
      };

      let routeSetupOk = true;
      let routeSetupError = "";

      try {
        // Set Origin, Destination, and Load Type once for this route combination
        try {
          await acquireLock();
          const originOk = await setAutocompleteValue("origin-input", p.origin);
          if (!originOk) throw new Error("Failed to set origin autocomplete");
          await sleep(selectWaitMs / 2);

          const destOk = await setAutocompleteValue("destination-input", p.dest);
          if (!destOk) throw new Error("Failed to set destination autocomplete");
          await sleep(selectWaitMs / 2);

          const ltOk = await setLoadType(p.lt);
          if (!ltOk) throw new Error("Failed to set load type");
          await sleep(selectWaitMs / 2);
        } catch (err) {
          console.error(`[Batch] Error setting route inputs for ${p.origin} -> ${p.dest}`, err);
          routeSetupOk = false;
          routeSetupError = err.message || "Unknown error";
          await releaseLock();
        }

        // Handle both grouped array configurations and legacy single eq parameters
        const eqList = Array.isArray(p.equipment) ? p.equipment : (p.eq ? [p.eq] : []);

        // Loop through each equipment class sequentially on the same page
        for (let eqIdx = 0; eqIdx < eqList.length; eqIdx++) {
          // Check STOP signal
          if (window.__DAT_EXTRACTOR_V2_CANCEL__ || window.__DAT_AUTO_PILOT_STOP__) break;

          const eq = eqList[eqIdx];
          const permStr = `${p.origin} -> ${p.dest} | ${eq} | ${p.lt}`;
          console.log(`[Batch] Processing Equipment ${eqIdx + 1}/${eqList.length}: ${permStr}`);

          const stat = { origin: p.origin, dest: p.dest, eq: eq, lt: p.lt, records: 0, status: "pending" };

          if (!routeSetupOk) {
            stat.status = "skipped_route_setup_failed";
            stat.error = routeSetupError;
            taskStats.push(stat);
            continue;
          }

          try {
            // Wrap the entire task in a timeout so we never get stuck
            await withTimeout((async () => {
              // Ensure we have active state before setting equipment type
              await acquireLock();

              // === STEP 1: Select Equipment Type ===
              const eqOk = await setEquipmentType(eq);
              await sleep(selectWaitMs / 2);
              if (!eqOk) {
                console.warn(`[Batch] Skipping — could not set equipment: ${eq}`);
                stat.status = "skipped_equipment";
                await releaseLock();
                return; // exit the async wrapper, continue loop
              }

              // === PRE-SEARCH STATE ===
              const preSearchRows = getLoadRows();
              const preSearchFirstId = preSearchRows.length > 0 ? findPostingId(preSearchRows[0]) : null;
              const preSearchCriteria = extractSearchCriteria();
              const preSearchCount = preSearchCriteria.totalResults;

              // === STEP 2: Click search ===
              const clicked = await clickSearch();
              
              // Release focus lock immediately after clickSearch so other tabs can setup their inputs
              await releaseLock();

              if (!clicked) {
                console.warn(`[Batch] Search button failed for: ${permStr}`);
                stat.status = "skipped_search_failed";
                return;
              }

              // === STEP 3: Wait for new results to load ===
              await waitForNewResults(15000, preSearchFirstId, preSearchCount);

              // === FAST SKIP: No results or "no results" page ===
              if (isNoResultsPresent()) {
                console.log(`[Batch] Skipping ${permStr} — "no results" detected`);
                stat.status = "skipped_zero_results";
                return;
              }

              const postSearchCriteria = extractSearchCriteria();
              const targetTotal = parseTotalResults(postSearchCriteria);
              if (targetTotal === 0 || postSearchCriteria.totalResults === "0") {
                console.log(`[Batch] Skipping ${permStr} — 0 results found`);
                stat.status = "skipped_zero_results";
                return;
              }

              // === STEP 4: Extract ===
              const result = await extractAllLoads();
              const mappedLoads = result.loads.map(ld => ({
                ...ld,
                _apOrigin: p.origin,
                _apDest: p.dest,
                _apEq: eq,
                _apLt: p.lt
              }));
              allExtractedLoads.push(...mappedLoads);
              stat.records = result.loads.length;
              stat.status = "completed";
            })(), TASK_TIMEOUT_MS, permStr);

          } catch (err) {
            // Timeout or any other error — log it and MOVE ON to the next task
            console.error(`[Batch] Task failed/timed out: ${permStr}`, err.message);
            if (stat.status === "pending") {
              stat.status = err.message.startsWith("Timeout") ? "skipped_timeout" : "error";
              stat.error = err.message;
            }
          } finally {
            await releaseLock();
          }

          taskStats.push(stat);
          // Short pause between tasks
          await sleep(Math.min(selectWaitMs, 500));
        }
      } finally {
        await releaseLock();
      }
    }
    return { loads: allExtractedLoads, taskStats: taskStats };
  }

  function extractOmniPageData() {
    const sections = [];
    
    function isVisible(el) {
      if (!el) return false;
      const style = window.getComputedStyle(el);
      return style.display !== 'none' && style.visibility !== 'hidden' && el.offsetHeight > 0;
    }

    const headingElements = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, .c-title-2, .c-title-3, .c-title-4'));
    const parsedContainers = new Set();

    function extractRowsFromElement(element) {
      const rows = [];
      const tableRows = Array.from(element.querySelectorAll('tr'));
      if (tableRows.length > 0) {
        tableRows.forEach(tr => {
          if (!isVisible(tr)) return;
          const cells = Array.from(tr.querySelectorAll('td, th'))
            .map(td => td.textContent.strip ? td.textContent.trim().replace(/\s+/g, ' ') : td.innerText.trim().replace(/\s+/g, ' '))
            .filter(Boolean);
          if (cells.length > 0) rows.push(cells);
        });
        return rows;
      }

      const itemSelectors = [
        '.c-plan-grid-cell_row', 
        '.c-plan-transfers_row', 
        'li', 
        '[class*="-item"]', 
        '[class*="_row"]',
        '[class*="-row"]'
      ];
      
      let items = [];
      for (const sel of itemSelectors) {
        const found = Array.from(element.querySelectorAll(sel));
        if (found.length > 0) {
          items = found.filter(el => isVisible(el));
          break;
        }
      }

      if (items.length > 0) {
        items.forEach(item => {
          const subRows = Array.from(item.querySelectorAll('.c-plan-transfers_row, li'));
          if (subRows.length > 0 && subRows.length < item.querySelectorAll('*').length) {
            const directTexts = [];
            Array.from(item.childNodes).forEach(node => {
              if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
                directTexts.push(node.textContent.trim().replace(/\s+/g, ' '));
              } else if (node.nodeType === Node.ELEMENT_NODE && !node.matches('.c-plan-transfers_row, li') && !node.querySelector('.c-plan-transfers_row, li')) {
                const txt = node.textContent.trim().replace(/\s+/g, ' ');
                if (txt) directTexts.push(txt);
              }
            });
            if (directTexts.length > 0) rows.push([directTexts.join(' ')]);
            
            subRows.forEach(sr => {
              const cells = Array.from(sr.querySelectorAll('div, span, p'))
                .filter(el => el.children.length === 0 && el.textContent.trim())
                .map(el => el.textContent.trim().replace(/\s+/g, ' '));
              if (cells.length > 0) rows.push(cells);
            });
            return;
          }

          const leaves = [];
          const childElements = Array.from(item.children).filter(el => isVisible(el) && el.textContent.trim());
          if (childElements.length >= 2) {
            childElements.forEach(child => {
              const subLeaves = Array.from(child.querySelectorAll('*'))
                .filter(el => el.children.length === 0 && el.textContent.trim())
                .map(el => el.textContent.trim().replace(/\s+/g, ' '));
              if (subLeaves.length > 0) {
                leaves.push(subLeaves.join(' '));
              } else if (child.textContent.trim()) {
                leaves.push(child.textContent.trim().replace(/\s+/g, ' '));
              }
            });
          } else {
            const leafNodes = Array.from(item.querySelectorAll('*'))
              .filter(el => el.children.length === 0 && el.textContent.trim())
              .map(el => el.textContent.trim().replace(/\s+/g, ' '));
            if (leafNodes.length > 0) {
              leaves.push(...leafNodes);
            } else {
              leaves.push(item.textContent.trim().replace(/\s+/g, ' '));
            }
          }

          const cleanLeaves = [];
          leaves.forEach(lf => {
            if (cleanLeaves.length === 0 || cleanLeaves[cleanLeaves.length - 1] !== lf) {
              cleanLeaves.push(lf);
            }
          });

          if (cleanLeaves.length > 0) {
            rows.push(cleanLeaves);
          }
        });
        return rows;
      }

      const blocks = Array.from(element.querySelectorAll('p, div, span'))
        .filter(el => el.children.length === 0 && el.textContent.trim() && isVisible(el));
      
      blocks.forEach(b => {
        const text = b.textContent.trim().replace(/\s+/g, ' ');
        if (text) rows.push([text]);
      });

      return rows;
    }

    headingElements.forEach(heading => {
      if (!isVisible(heading)) return;
      const title = heading.textContent.trim().replace(/\s+/g, ' ');
      if (title.length < 2 || title.length > 80) return;

      let container = heading.parentElement;
      while (container && container !== document.body) {
        const style = window.getComputedStyle(container);
        const isCard = container.classList.contains('cc-card') || 
                       container.classList.contains('c-plan-grid-cell') ||
                       container.tagName === 'SECTION' ||
                       container.tagName === 'ARTICLE' ||
                       container.id === 'rate-match-hero' ||
                       style.borderWidth !== '0px' ||
                       style.boxShadow !== 'none' ||
                       (style.backgroundColor !== 'rgba(0, 0, 0, 0)' && style.backgroundColor !== 'transparent');
        
        if (isCard) break;
        container = container.parentElement;
      }

      if (!container || container === document.body) {
        container = heading.parentElement;
      }

      if (parsedContainers.has(container)) return;
      parsedContainers.add(container);

      const rawRows = extractRowsFromElement(container);
      const cleanRows = rawRows.filter(r => {
        if (r.length === 0) return false;
        if (r.length === 1 && r[0].toLowerCase() === title.toLowerCase()) return false;
        return true;
      });

      if (cleanRows.length > 0) {
        sections.push({
          name: title,
          rows: cleanRows
        });
      }
    });

    let textOut = `============================================================\n`;
    textOut += `OMNISCRAPER EXTRACTION - ${new Date().toLocaleString()}\n`;
    textOut += `URL: ${window.location.href}\n`;
    textOut += `============================================================\n\n`;

    const csvRows = [["Section", "Data Column 1", "Data Column 2", "Data Column 3", "Data Column 4"]];

    sections.forEach(sec => {
      textOut += `\n[ SECTION: ${sec.name} ]\n`;
      textOut += `-`.repeat(sec.name.length + 12) + `\n`;
      sec.rows.forEach(row => {
        textOut += `  • ` + row.join(' | ') + `\n`;
        const paddedRow = [sec.name, ...row];
        while (paddedRow.length < 5) paddedRow.push("");
        csvRows.push(paddedRow.slice(0, 5));
      });
      textOut += `\n`;
    });

    const csvOut = csvRows.map(r => r.map(c => `"${c.replace(/"/g, '""')}"`).join(',')).join('\n');
    const jsonOut = JSON.stringify({
      source: "omni",
      url: window.location.href,
      timestamp: new Date().toISOString(),
      sections: sections
    }, null, 2);

    return {
      sections: sections,
      text: textOut,
      csv: csvOut,
      json: jsonOut
    };
  }

  chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
    if (request.action === "ping") {
      sendResponse({ ok: true });
      return;
    }

    if (request.action === "extractOmniPage") {
      (async () => {
        try {
          const result = extractOmniPageData();
          sendResponse({
            success: true,
            sections: result.sections,
            text: result.text,
            csv: result.csv,
            json: result.json
          });
        } catch (err) {
          sendResponse({ success: false, error: err.message });
        }
      })();
      return true;
    }

    if (request.action === "cancelExtract") {
      window.__DAT_EXTRACTOR_V2_CANCEL__ = true;
      sendResponse({ ok: true });
      return;
    }

    if (request.action === "executeBatch") {
      (async () => {
        try {
          setSpeedMode(request.speedMode || "normal");
          setDeepOptions(request.deep);
          const { loads, taskStats } = await executeBatch(request.tasks);
          chrome.runtime.sendMessage({
            action: "batchCompleted",
            batchId: request.batchId,
            tryId: request.tryId,
            results: loads,
            taskStats: taskStats
          });
        } catch (err) {
          console.error("Batch Error:", err);
          const failedStats = request.tasks.map(p => {
            const eqList = Array.isArray(p.equipment) ? p.equipment : (p.eq ? [p.eq] : []);
            return eqList.map(eq => ({
              origin: p.origin,
              dest: p.dest,
              eq: eq,
              lt: p.lt,
              records: 0,
              status: "failed",
              error: err.message || "Batch initialization failed"
            }));
          }).flat();

          chrome.runtime.sendMessage({
            action: "batchCompleted",
            batchId: request.batchId,
            tryId: request.tryId,
            results: [],
            taskStats: failedStats
          });
        }
      })();
      sendResponse({ success: true });
      return true;
    }

    if (request.action === "startAutoPilot") {
      // Legacy single-tab auto pilot - can be removed or kept for backwards compatibility
      // startAutoPilot(request.config).catch(err => console.error("AutoPilot Error:", err));
      sendResponse({ success: true, message: "Use the new distributed autopilot via popup" });
      return true;
    }

    if (request.action === "extractLoads") {
      (async () => {
        try {
          setSpeedMode(request.speedMode || "normal");
          setDeepOptions(request.deep);
          const result = await extractAllLoads();
          const { criteria, loads, targetTotal, skipped, incomplete, cancelled } = result;
          const text = formatOutput(criteria, loads, {
            skipped: result.skipped,
            emptyCount: result.emptyCount,
          });
          const csv = formatCSV(loads);
          sendResponse({
            success: true,
            text,
            csv,
            loads,
            records: buildExportRecords(loads),
            deepStats: deepMode ? { ...deepStats } : null,
            count: loads.length,
            criteria,
            targetTotal,
            skipped: result.skipped,
            emptyCount: result.emptyCount,
            scrollSteps: result.scrollSteps,
            incomplete,
            cancelled,
          });
        } catch (err) {
          removeProgress();
          sendResponse({ success: false, error: err.message });
        }
      })();
      return true;
    }
  });
  // ── DAT Directory Scraper Helpers ──
  function getValByLabel(labelText, container = document) {
    if (!container) container = document;
    const elements = Array.from(container.querySelectorAll('div, span, label, td, th, p, a, h4, li, dd, dt'));
    for (const el of elements) {
      const text = el.textContent.trim().replace(/\s+/g, ' ');
      if (text.toLowerCase() === labelText.toLowerCase() ||
        text.toLowerCase() === labelText.toLowerCase() + ':') {

        // Try grid-cell association first
        const gridVal = getValFromGrid(el, container);
        if (gridVal) return cleanVal(gridVal);

        let sib = el.nextElementSibling;
        if (sib && sib.textContent.trim()) {
          return cleanVal(sib.textContent.trim());
        }

        let parent = el.parentElement;
        if (parent) {
          let psib = parent.nextElementSibling;
          if (psib && psib.textContent.trim()) {
            return cleanVal(psib.textContent.trim());
          }

          let pparent = parent.parentElement;
          if (pparent && pparent.children.length > 1) {
            const idx = Array.from(pparent.children).indexOf(parent);
            if (idx !== -1 && idx < pparent.children.length - 1) {
              let nextVal = pparent.children[idx + 1].textContent.trim();
              if (nextVal) return cleanVal(nextVal);
            }
          }

          const children = Array.from(parent.children);
          const elIdx = children.indexOf(el);
          if (elIdx !== -1 && elIdx < children.length - 1) {
            let nextVal = children[elIdx + 1].textContent.trim();
            if (nextVal) return cleanVal(nextVal);
          }
        }
      }
    }

    for (const el of elements) {
      const text = el.textContent.trim().replace(/\s+/g, ' ');
      if (text.toLowerCase().startsWith(labelText.toLowerCase() + ':')) {
        return cleanVal(text.substring(labelText.length + 1));
      }
      if (text.toLowerCase().startsWith(labelText.toLowerCase() + ' ') && text.length > labelText.length + 2) {
        const parts = text.substring(labelText.length).trim();
        if (parts) return cleanVal(parts);
      }
    }
    return "";
  }

  function findSectionContainer(headingText) {
    const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, div, span, legend, header, section'));
    for (const h of headings) {
      let text = h.textContent.trim().replace(/\s+/g, ' ').toLowerCase();
      // Clean up material icons / extra icons text to match correctly
      h.querySelectorAll('mat-icon, .material-icons, icon').forEach(ico => {
        const icoTxt = ico.textContent.trim().toLowerCase();
        if (icoTxt) {
          text = text.replace(icoTxt, '').trim().replace(/\s+/g, ' ');
        }
      });
      if (text === headingText.toLowerCase() || text.replace(':', '') === headingText.toLowerCase()) {
        let parent = h.parentElement;
        for (let i = 0; i < 5; i++) {
          if (parent && (
            parent.classList.contains('card') ||
            parent.classList.contains('panel') ||
            parent.tagName === 'SECTION' ||
            parent.tagName === 'FIELDSET' ||
            parent.className.includes('container') ||
            parent.className.includes('section') ||
            parent.className.includes('block') ||
            parent.className.includes('card') ||
            parent.className.includes('group')
          )) {
            return parent;
          }
          if (parent) parent = parent.parentElement;
        }
        return h.parentElement;
      }
    }
    return null;
  }

  function extractDirectoryDetails() {
    const dirData = {
      docket: "",
      dot_number: "",
      entity_type: "",
      coverage_to: "",
      credit_score: "",
      insurance_carrier: ""
    };

    // Find main/fallback fields
    dirData.docket = getValByLabel("Docket") || getValByLabel("MC/MX/FF Number");
    dirData.dot_number = getValByLabel("DOT Number") || getValByLabel("USDOT Number");
    dirData.credit_score = getValByLabel("Credit score");

    // General Information
    const genContainer = findSectionContainer("General Information");
    if (genContainer) {
      if (!dirData.docket) dirData.docket = getValByLabel("Docket", genContainer);
      if (!dirData.dot_number) dirData.dot_number = getValByLabel("DOT Number", genContainer);
      dirData.entity_type = getValByLabel("Entity type", genContainer);
    }

    // DOT Authority & Insurance
    const dotContainer = findSectionContainer("DOT Authority & Insurance");
    if (dotContainer) {
      dirData.coverage_to = getValByLabel("Coverage to", dotContainer);
      dirData.insurance_carrier = getValByLabel("Insurance carrier", dotContainer);
    }

    // Credit Profile
    const creditContainer = findSectionContainer("Credit Profile");
    if (creditContainer) {
      if (!dirData.credit_score) dirData.credit_score = getValByLabel("Credit score", creditContainer);
    }

    return dirData;
  }

  async function waitPageLoaded(selector, timeoutMs = 8000) {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      if (window.location.href.includes("/login") || document.querySelector('input[type="password"]')) {
        return false;
      }
      const el = document.querySelector(selector);
      if (el && el.textContent.trim().length > 0) {
        return true;
      }
      if (document.body.textContent.includes("Office Information") || document.body.textContent.includes("General Information")) {
        return true;
      }
      await sleep(200);
    }
    return false;
  }

  function isCompanySimilar(nameA, nameB) {
    const a = norm(nameA);
    const b = norm(nameB);
    if (!a || !b) return false;
    if (a === b) return true;
    if (a.startsWith(b) || b.startsWith(a)) return true;
    // Remove "inc", "llc", "corp", etc. and check if one contains the other
    const clean = (s) => s.replace(/\b(inc|llc|corp|co|company|logistics|transport|services|group|solutions|freight)\b/g, "").trim();
    const ca = clean(a);
    const cb = clean(b);
    if (!ca || !cb) return false;
    if (ca === cb || ca.startsWith(cb) || cb.startsWith(ca) || ca.includes(cb) || cb.includes(ca)) return true;
    return false;
  }

  function isLoadMatchingRow(load, rowLoad) {
    const rowPostingId = rowLoad.postingId;
    if (load.postingId && rowPostingId) {
      return load.postingId === rowPostingId;
    }

    // Match origin and destination strictly
    if (norm(load.origin) !== norm(rowLoad.origin)) return false;
    if (norm(load.destination) !== norm(rowLoad.destination)) return false;

    // Company name matching (flexible/similarity-based)
    if (!isCompanySimilar(load.company, rowLoad.company)) return false;

    // Compare trip miles if both have valid numeric strings
    const m1 = parseInt(String(load.tripMiles || "").replace(/\D/g, ""), 10);
    const m2 = parseInt(String(rowLoad.tripMiles || "").replace(/\D/g, ""), 10);
    if (!isNaN(m1) && !isNaN(m2) && m1 !== m2) return false;

    // Compare equipment type by their first letter (e.g., 'v' matches 'vans (standard)')
    const eq1 = norm(load.equipmentType || "")[0];
    const eq2 = norm(rowLoad.equipmentType || "")[0];
    if (eq1 && eq2 && eq1 !== eq2) return false;

    return true;
  }

  function findRowForLoad(load) {
    const rows = getLoadRows();
    const loadKey = getStableLoadKey(load);

    for (const row of rows) {
      if (isSkeletonRow(row)) continue;

      const rowPostingId = findPostingId(row);
      if (load.postingId && rowPostingId === load.postingId) {
        return row;
      }

      // Fallback: match by stable key
      let rowLoad;
      const textSig = row.textContent.slice(0, 100);
      if (row.__extractedLoad && row.__extractedLoadPostingId === rowPostingId && row.__extractedLoadTextSig === textSig) {
        rowLoad = row.__extractedLoad;
      } else {
        rowLoad = extractLoadFromRow(row);
      }

      if (getStableLoadKey(rowLoad) === loadKey || isLoadMatchingRow(load, rowLoad)) {
        return row;
      }
    }
    return null;
  }

  function cleanVal(val) {
    if (!val) return "";
    let s = val.trim();
    // Strip trailing/leading material icon text words
    s = s.replace(/\b(launch|done|close|check|edit|info|error|warning|arrow_forward|open_in_new)\b/gi, "");
    // Strip trailing digit followed by launch/done pattern
    s = s.replace(/\d?\s*(launch|done|close|check)\s*$/i, "");
    s = s.replace(/\s+/g, " ");
    return s.trim();
  }

  function findDetailsDrawer() {
    const selectors = [
      '[data-test*="details-container"]',
      '[data-test*="details-drawer"]',
      '[class*="load-details"]',
      '[class*="detail-drawer"]',
      '.load-details-drawer',
      '.detail-drawer',
      '.mat-drawer-end',
      'mat-drawer[position="end"]',
      'mat-drawer',
      '.mat-drawer'
    ];
    const isBackground = document.hidden;
    const maxDrawerWidth = window.innerWidth * 0.7 || 800;

    // Helper to find the absolute outer container of the details panel
    const getOuterDrawer = (el) => {
      if (!el) return null;
      // Walk up to the closest mat-drawer or major layout container
      const outer = el.closest('mat-drawer, .mat-drawer, [data-test*="details-container"], [class*="load-details-drawer"]');
      return outer || el;
    };

    const isValidDrawer = (drawer) => {
      if (!drawer) return false;
      // Details drawer should not contain main search inputs or load rows.
      // Relax conditions to allow drawers that may contain occasional hidden elements.
      if (drawer.querySelector('[data-test="origin-input"], [data-test="destination-input"], [data-test="search-button"]')) {
        // If it contains any of the primary search inputs, it's likely not the details drawer.
        return false;
      }
      // Allow drawers that have a company profile or known detail sections.
      if (drawer.querySelector('.company-profile, [class*="company-profile"], .load-details-drawer, .detail-drawer')) {
        return true;
      }
      // Fallback: ensure it does not look like a table row container.
      if (drawer.querySelector('.row-container, [id^="table-row-"]')) {
        return false;
      }
      return true;
    };

    for (const sel of selectors) {
      try {
        const elements = Array.from(document.querySelectorAll(sel));
        for (const el of elements) {
          if (isElementVisible(el)) {
            if (!isBackground) {
              if (el.clientWidth <= 200 || el.clientWidth >= maxDrawerWidth) {
                continue;
              }
              const rect = el.getBoundingClientRect();
              if (rect.left < 150) {
                continue;
              }
            }

            const text = el.textContent.toLowerCase();
            if (text.includes('load details') || text.includes('contact') || text.includes('safety') || text.includes('docket') || text.includes('view in directory') || text.includes('company')) {
              if (!el.querySelector('nav') && !el.id?.includes('menu') && !text.includes('search trucks') && !text.includes('my trucks') && !text.includes('private network')) {
                const drawer = getOuterDrawer(el);
                if (isValidDrawer(drawer)) return drawer;
              }
            }
          }
        }
      } catch (e) { }
    }

    const fallbackSelectors = [
      '[data-test*="details-container"]',
      '[data-test*="details-drawer"]',
      '.load-details-drawer',
      '.detail-drawer',
      '.mat-drawer-end',
      'mat-drawer[position="end"]',
      '.company-profile',
      '[class*="company-profile"]'
    ];
    for (const sel of fallbackSelectors) {
      try {
        const el = document.querySelector(sel);
        if (el && isValidDrawer(el)) return el;
      } catch (e) { }
    }

    const divs = Array.from(document.querySelectorAll('div, section, aside'));
    for (const el of divs) {
      try {
        if (isElementVisible(el)) {
          if (!isBackground) {
            if (el.clientWidth <= 150 || el.clientWidth >= 800) continue;
            const rect = el.getBoundingClientRect();
            if (rect.left < 150) continue;
          }
          const txt = el.textContent.toLowerCase();
          if ((txt.includes('load details') || txt.includes('view in directory') || txt.includes('company')) &&
            (txt.includes('rate') || txt.includes('docket') || txt.includes('safety') || txt.includes('contact')) &&
            !el.querySelector('nav') &&
            !el.id?.includes('menu') &&
            !txt.includes('search trucks') &&
            !txt.includes('my trucks')) {
            const drawer = getOuterDrawer(el);
            if (isValidDrawer(drawer)) return drawer;
          }
        }
      } catch (e) { }
    }
    return null;
  }

  function closeDetailsDrawer(drawerEl) {
    if (!drawerEl) return;
    
    // 1. Try finding close button by visual coordinates relative to the drawer container (extremely robust)
    let closeBtn = null;
    try {
      const elements = Array.from(drawerEl.querySelectorAll('button, [role="button"], mat-icon, svg, a, div'));
      const drawerRect = drawerEl.getBoundingClientRect();
      closeBtn = elements.find(el => {
        const rect = el.getBoundingClientRect();
        const relativeTop = rect.top - drawerRect.top;
        const relativeRight = drawerRect.right - rect.right;
        const relativeLeft = rect.left - drawerRect.left;
        // The close button sits near top-right/top-left and is relatively compact
        return (relativeTop >= 0 && relativeTop < 85) && (relativeLeft < 85 || relativeRight < 85) && rect.width > 10 && rect.width < 80 && rect.height > 10 && rect.height < 80;
      });
    } catch (e) {
      console.log("[DAT Extractor] Error in visual close button heuristic (expected in background tabs):", e);
    }

    // 2. Fall back to textual and selector-based heuristics
    if (!closeBtn) {
      closeBtn = drawerEl.querySelector('button[aria-label*="Close"i]') ||
                 drawerEl.querySelector('button[aria-label*="Back"i]') ||
                 drawerEl.querySelector('[data-test*="close"i]') ||
                 drawerEl.querySelector('button[class*="close"i]') ||
                 drawerEl.querySelector('[class*="close"i]') ||
                 drawerEl.querySelector('mat-icon[class*="close"i]') ||
                 drawerEl.querySelector('button[title*="Close"i]') ||
                 drawerEl.querySelector('[data-testid*="close"i]') ||
                 Array.from(drawerEl.querySelectorAll('button, [role="button"], mat-icon, span, a, div, svg')).find(el => {
                   const t = el.textContent.trim().toLowerCase();
                   const aria = (el.getAttribute('aria-label') || '').toLowerCase();
                   const title = (el.getAttribute('title') || '').toLowerCase();
                   const dataTest = (el.getAttribute('data-test') || '').toLowerCase();
                   const cls = (el.getAttribute('class') || '').toLowerCase();
                   
                   const isCloseText = t === 'close' || t === 'x' || t === 'cancel' || t === 'clear' || 
                                       t === 'arrow_back' || t === 'arrow_forward' || 
                                       t === 'chevron_right' || t === 'chevron_left' || 
                                       t === 'keyboard_arrow_right';
                   
                   const hasCloseAttr = aria.includes('close') || aria.includes('back') || aria === 'x' || aria.includes('chevron') || aria.includes('arrow') || aria.includes('dismiss') ||
                                        title.includes('close') || title.includes('back') || title.includes('dismiss') ||
                                        dataTest.includes('close') || dataTest.includes('dismiss') ||
                                        cls.includes('close') || cls.includes('dismiss') || cls.includes('back-btn') || cls.includes('backbutton');
                                        
                   return isCloseText || hasCloseAttr;
                 });
    }

    // Click parent button if we found nested elements (e.g. nested mat-icon or svg)
    if (closeBtn) {
      const parentButton = closeBtn.closest('button, [role="button"], a');
      if (parentButton && drawerEl.contains(parentButton)) {
        closeBtn = parentButton;
      }
    }

    if (closeBtn) {
      console.log("[DAT Extractor] Clicking close button in details drawer.");
      simulateClick(closeBtn);
    } else {
      console.log("[DAT Extractor] Close button not found in details drawer, dispatching Escape key.");
    }

    // Always dispatch Escape key to multiple targets to guarantee drawer dismissal
    const escTargets = [document.activeElement, drawerEl, document.body, document, window];
    const escEvent = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true, cancelable: true });
    escTargets.forEach(t => {
      if (t) {
        try { t.dispatchEvent(escEvent); } catch(err) {}
      }
    });

    // Backdrop click fallback
    const backdrop = document.querySelector('.mat-drawer-backdrop') || 
                     document.querySelector('.mat-sidenav-backdrop') ||
                     document.querySelector('[class*="backdrop"]');
    if (backdrop && isElementVisible(backdrop)) {
      console.log("[DAT Extractor] Clicking backdrop to close details drawer.");
      try {
        simulateClick(backdrop);
      } catch (err) {}
    }
  }

  // ── Deep detail traversal ─────────────────────────────────────────

  /**
   * The cell to click to open a row's details drawer.
   * Route/rate/age cells open the drawer; the company link does not (it stops
   * propagation and navigates instead), so it is deliberately never chosen.
   */
  function pickRowClickTarget(row) {
    return row.querySelector('.route-container') ||
      row.querySelector('.cell-route') ||
      row.querySelector('[class*="route"]') ||
      row.querySelector('.cell-rate') ||
      row.querySelector('[class*="rate"]') ||
      row.querySelector('.cell-age') ||
      row.querySelector('[class*="age"]') ||
      row;
  }

  // Markers of the sections a complete load-detail view contains. Live logs
  // showed findDetailsDrawer() locking onto just the Equipment card
  // ("EquipmentLoadFullTruckVanLength53 ftWeight20,652 lbsReference ID27B6"),
  // so Rate, Trip, Contact and Company were never even in scope.
  const DETAIL_MARKERS = [
    /\bequipment\b/i, /\btruck\b/i, /\bweight\b/i, /\blength\b/i,
    /\brate\b/i, /\bspot\b/i, /\bmarket\b/i, /\btrip\b/i,
    /\bcontact\b/i, /\bcompany\b/i, /\bcommodity\b/i, /\breference id\b/i,
    /\bview route\b/i, /\bfactoring\b/i, /\bmc\s*#?\d/i
  ];

  function detailScore(el) {
    if (!el) return 0;
    const t = (el.textContent || "");
    if (!t || t.length < 20) return 0;
    let n = 0;
    for (const re of DETAIL_MARKERS) if (re.test(t)) n++;
    return n;
  }

  /**
   * Resolve the smallest element that holds the WHOLE detail view.
   * Starts from every plausible seed (the drawer heuristic, the row's inline
   * detail, the row's siblings) and climbs while climbing keeps revealing more
   * sections — then stops before it swallows the results table or the page.
   */
  function resolveDetailSurface(matchedRow) {
    const seeds = [];
    const push = (el) => { if (el && !seeds.includes(el)) seeds.push(el); };

    push(findDetailsDrawer());
    if (matchedRow) {
      push(matchedRow.querySelector('.table-row-detail'));
      push(matchedRow.querySelector('[data-test="details-container"]'));
      push(matchedRow.querySelector('[class*="row-detail"]'));
      push(matchedRow.nextElementSibling);
      push(matchedRow.parentElement?.querySelector('.table-row-detail'));
    }
    // Anything on the page that looks like an opened detail panel.
    try {
      document.querySelectorAll(
        '.table-row-detail,[data-test*="details-container"],[class*="load-detail"],[class*="detail-panel"],mat-drawer[position="end"]'
      ).forEach(push);
    } catch (e) { }

    let best = null;
    let bestScore = 1; // require at least 2 distinct sections

    for (const seed of seeds) {
      if (!seed || seed.nodeType !== 1) continue;
      let node = seed;
      let hops = 0;
      while (node && node !== document.body && hops < 8) {
        // Never climb into something that contains the results table itself.
        const rowsInside = node.querySelectorAll('.row-container,[id^="table-row-"]').length;
        if (rowsInside > 1) break;
        const score = detailScore(node);
        if (score > bestScore) { bestScore = score; best = node; }
        // A node containing the search form is far too high up.
        if (node.querySelector('[data-test="origin-input"],[data-test="search-button"]')) break;
        node = node.parentElement;
        hops++;
      }
    }
    return best;
  }

  /** Does the open drawer belong to this load? */
  function drawerMatchesLoad(drawerEl, load) {
    if (!drawerEl) return false;
    const drawerText = (drawerEl.textContent || "").toLowerCase();
    if (drawerText.trim().length < 60) return false;
    const companyLower = String(load.company || "").toLowerCase();
    if (!companyLower || companyLower === "–") {
      // No company to match on — fall back to origin/destination.
      const o = norm(load.origin);
      const d = norm(load.destination);
      return !!(o && d && drawerText.includes(o) && drawerText.includes(d));
    }
    const firstWord = companyLower.split(/[\s\/]/)[0];
    return drawerText.includes(companyLower) ||
      (firstWord.length > 2 && drawerText.includes(firstWord)) ||
      isCompanySimilar(load.company, drawerText);
  }

  /**
   * Open (or switch) the details drawer for a load and wait until it has rendered.
   * Returns the drawer element, or null if it never opened.
   */
  async function openDrawerForLoad(load, matchedRow) {
    const D = DEEP();
    let drawerEl = findDetailsDrawer();
    if (drawerMatchesLoad(drawerEl, load)) return drawerEl;

    const waitMs = document.hidden ? 7000 : 4500;
    const targets = [pickRowClickTarget(matchedRow), matchedRow];

    for (const target of targets) {
      if (!target) continue;
      if (isCancelledNow()) return null;
      try { target.scrollIntoView({ block: "center", behavior: "auto" }); } catch (e) { }
      await sleep(250);
      simulateClick(target);

      drawerEl = await D.waitFor(() => {
        const d = findDetailsDrawer();
        return drawerMatchesLoad(d, load) ? d : null;
      }, waitMs, 200);

      if (drawerEl) {
        // Let the async panels inside finish before anything is read.
        await D.waitForStable(drawerEl, { quietMs: 260, timeoutMs: document.hidden ? 4000 : 3000 });
        return resolveDetailSurface(matchedRow) || drawerEl;
      }
    }

    // The row may expand inline without any element the drawer heuristic likes.
    const surface = resolveDetailSurface(matchedRow);
    if (surface) {
      await D.waitForStable(surface, { quietMs: 260, timeoutMs: 2500 });
      return surface;
    }

    // Last resort: accept any drawer that rendered, even if the company text
    // did not match — partial data beats none, and it is flagged as partial.
    drawerEl = findDetailsDrawer();
    if (drawerEl && (drawerEl.textContent || "").trim().length > 120) {
      await D.waitForStable(drawerEl, { quietMs: 260, timeoutMs: 2500 });
      return drawerEl;
    }
    return null;
  }

  /**
   * Deep-extract one load: open its drawer, traverse every revealed section,
   * merge the result into the record. Failures are recorded, never thrown —
   * load #7 failing must not stop load #8.
   */
  async function deepExtractLoadDetail(load, matchedRow) {
    const D = DEEP();
    if (!D) return false;

    for (let attempt = 0; attempt <= deepRetries; attempt++) {
      if (isCancelledNow()) return false;
      try {
        const drawerEl = await openDrawerForLoad(load, matchedRow);
        if (!drawerEl) throw new Error("details drawer did not open");

        // The row scraper runs during the scroll pass while every row is still
        // collapsed, so its .table-row-detail branch never fired — which is why
        // truckType / referenceId / pickup times / phone / email came back empty
        // on every one of the 60k records captured so far. Re-read the row now
        // that it is expanded, and keep whichever value is non-blank.
        try {
          delete matchedRow.__extractedLoad;
          const expanded = extractLoadFromRow(matchedRow);
          for (const [k, v] of Object.entries(expanded)) {
            if (k.startsWith("_") || k === "timestamp") continue;
            if (!isBlank(v) && isBlank(load[k])) load[k] = v;
          }
        } catch (e) {
          logToServer("DEEP_ROW_REREAD_FAILED", { company: load.company, error: e.message });
        }

        const result = await D.extractSurface(drawerEl, {
          ids: D.loadIdentifiers(load),
          maxClicks: deepMaxClicks,
          maxDepth: deepMaxDepth,
          sectionTimeoutMs: document.hidden ? 3200 : 2500,
          isCancelled: isCancelledNow
        });

        D.applySurfaceToLoad(load, result, "detailDrawer");

        const secs = result.meta?.sectionsVisited || [];
        if (secs.length) {
          deepStats.sections = Array.from(new Set([...deepStats.sections, ...secs])).slice(-40);
        }
        logToServer("DEEP_DETAIL_OK", {
          company: load.company,
          fields: result.meta?.fieldsExtracted || 0,
          clicks: result.meta?.clicks || 0,
          sections: secs.length,
          usedNetwork: !!result.meta?.usedNetwork
        });
        return true;
      } catch (err) {
        const isLast = attempt === deepRetries;
        if (!isLast) {
          if (load.extraction) load.extraction.retries = (load.extraction.retries || 0) + 1;
          deepStats.retries++;
          // Reset the surface before retrying — a half-open drawer is the usual cause.
          const stale = findDetailsDrawer();
          if (stale) { closeDetailsDrawer(stale); await sleep(400); }
          continue;
        }
        D.applySurfaceToLoad(load, null, "detailDrawer");
        if (load.extraction) {
          load.extraction.errors.push({ stage: "detailExtraction", message: err.message || String(err) });
        }
        logToServer("DEEP_DETAIL_FAILED", { company: load.company, error: err.message || String(err) });
        return false;
      }
    }
    return false;
  }

  /** Merge the office/company schema scraped from a directory tab into a load. */
  function applyDirectoryDeep(load, dirDetails) {
    const D = DEEP();
    if (!D || !dirDetails || !dirDetails.__deep) return;
    try {
      D.applySurfaceToLoad(load, {
        schema: dirDetails.__deep,
        meta: dirDetails.__deepMeta || { sectionsVisited: [], sectionsFailed: [], warnings: [], errors: [] }
      }, "directoryPage");
    } catch (e) {
      logToServer("DEEP_DIRECTORY_MERGE_FAILED", { company: load.company, error: e.message });
    }
  }

  /** Keep only the company/office subtrees when caching directory data per company. */
  function trimDeepForCache(deepSchema) {
    if (!deepSchema) return null;
    return {
      company: deepSchema.company || null,
      office: deepSchema.office || null,
      contact: deepSchema.contact || null,
      additionalData: deepSchema.additionalData || {}
    };
  }

  async function clickCompanyTab(drawerEl) {
    if (!drawerEl) return false;
    const selectors = [
      '[role="tab"]',
      '.mat-tab-label',
      '.mat-mdc-tab',
      '.tab',
      'button',
      'a',
      'span',
      'div'
    ];

    const targetTexts = ["company", "broker", "carrier", "company details", "directory"];

    // 1. Strict match loop
    for (const sel of selectors) {
      try {
        const elements = Array.from(drawerEl.querySelectorAll(sel));
        for (const el of elements) {
          const txt = el.textContent.trim().toLowerCase();
          if (txt.length > 35) continue; // Avoid matching large containers

          if (targetTexts.some(t => txt === t || txt.replace(/\s+/g, '') === t)) {
            const rect = el.getBoundingClientRect();
            if (isElementVisible(el) || (rect.width === 0 && rect.height === 0)) {
              console.log(`[DAT Extractor] Clicking Company/Broker tab via ${sel}: "${el.textContent.trim()}"`);
              logToServer("DIRECTORY_TAB_CLICK", { tabText: el.textContent.trim(), selector: sel });
              simulateClick(el);

              const wrapper = el.closest('[role="tab"], button, a, .mat-tab-label, .mat-mdc-tab');
              if (wrapper && wrapper !== el) {
                simulateClick(wrapper);
              }

              await sleep(1000); // Wait for transition and data loading
              return true;
            }
          }
        }
      } catch (err) { }
    }

    // 2. Loose match loop (handles "Broker MC123456", "Broker details", etc.)
    for (const sel of selectors) {
      try {
        const elements = Array.from(drawerEl.querySelectorAll(sel));
        for (const el of elements) {
          const txt = el.textContent.trim().toLowerCase();
          if (txt.length > 35) continue; // Avoid matching large containers

          if (targetTexts.some(t => txt.includes(t))) {
            const rect = el.getBoundingClientRect();
            if (isElementVisible(el) || (rect.width === 0 && rect.height === 0)) {
              console.log(`[DAT Extractor] Clicking Company/Broker tab (loose) via ${sel}: "${el.textContent.trim()}"`);
              logToServer("DIRECTORY_TAB_CLICK_LOOSE", { tabText: el.textContent.trim(), selector: sel });
              simulateClick(el);

              const wrapper = el.closest('[role="tab"], button, a, .mat-tab-label, .mat-mdc-tab');
              if (wrapper && wrapper !== el) {
                simulateClick(wrapper);
              }

              await sleep(1000); // Wait for transition and data loading
              return true;
            }
          }
        }
      } catch (err) { }
    }
    return false;
  }

  function getValFromGrid(labelEl, container) {
    const classes = Array.from(labelEl.classList);

    // 1. Check for standard format fields-grid__cell--XYZ and fields-grid__cell--XYZ--label
    for (const c of classes) {
      if (c.endsWith('--label') || c.includes('-label') || c.includes('__label')) {
        const valClass = c.replace('--label', '').replace('-label', '').replace('__label', '');
        // Ignore generic classes to prevent matching the first grid cell in the container
        const lowerVal = valClass.toLowerCase();
        if (lowerVal === 'fields-grid__cell' || lowerVal === 'fields-grid' || lowerVal === 'grid__cell' || lowerVal === 'cell' || lowerVal === 'label' || lowerVal === 'value' || lowerVal === 'field-label' || lowerVal === 'field-value' || lowerVal === 'field') {
          continue;
        }
        const valEl = container.querySelector(`.${valClass}:not(.${c})`);
        if (valEl) return valEl.textContent.trim();
      }
    }

    // 2. Fallback prefix check
    const fieldClass = classes.find(c => c.startsWith('fields-grid__cell--') && !c.endsWith('--label'));
    if (fieldClass) {
      if (fieldClass !== 'fields-grid__cell') {
        const valEl = container.querySelector(`.${fieldClass}:not(.fields-grid__cell--label)`);
        if (valEl) return valEl.textContent.trim();
      }
    }

    return null;
  }

  function getValByLabelInline(labelText, container = document) {
    if (!container) container = document;
    const elements = Array.from(container.querySelectorAll('div, span, label, td, th, p, a, h4, li, dd, dt'));

    for (const el of elements) {
      const text = el.textContent.trim().replace(/\s+/g, ' ');
      if (text.toLowerCase() === labelText.toLowerCase() ||
        text.toLowerCase() === labelText.toLowerCase() + ':') {

        // 1. Try grid-cell association
        const gridVal = getValFromGrid(el, container);
        if (gridVal) return cleanVal(gridVal);

        // 2. Try sibling
        let sib = el.nextElementSibling;
        if (sib && sib.textContent.trim()) {
          return cleanVal(sib.textContent.trim());
        }

        // 3. Try parent sibling or parent child index
        let parent = el.parentElement;
        if (parent) {
          let psib = parent.nextElementSibling;
          if (psib && psib.textContent.trim()) {
            return cleanVal(psib.textContent.trim());
          }

          let pparent = parent.parentElement;
          if (pparent && pparent.children.length > 1) {
            const idx = Array.from(pparent.children).indexOf(parent);
            if (idx !== -1 && idx < pparent.children.length - 1) {
              let nextVal = pparent.children[idx + 1].textContent.trim();
              if (nextVal) return cleanVal(nextVal);
            }
          }

          const children = Array.from(parent.children);
          const elIdx = children.indexOf(el);
          if (elIdx !== -1 && elIdx < children.length - 1) {
            let nextVal = children[elIdx + 1].textContent.trim();
            if (nextVal) return cleanVal(nextVal);
          }
        }
      }
    }

    // Fallback: startsWith
    for (const el of elements) {
      const text = el.textContent.trim().replace(/\s+/g, ' ');
      if (text.toLowerCase().startsWith(labelText.toLowerCase() + ':')) {
        return cleanVal(text.substring(labelText.length + 1));
      }
      if (text.toLowerCase().startsWith(labelText.toLowerCase() + ' ') && text.length > labelText.length + 2) {
        const parts = text.substring(labelText.length).trim();
        if (parts) return cleanVal(parts);
      }
    }

    return "";
  }

  function findSectionContainerInline(headingText, container = document) {
    const headings = Array.from(container.querySelectorAll('h2, h3, h4, div, span, legend, h1, h5, header'));
    for (const h of headings) {
      const text = h.textContent.trim().toLowerCase();
      if (text === headingText.toLowerCase()) {
        let parent = h.parentElement;
        for (let i = 0; i < 5; i++) {
          if (parent && (
            parent.classList.contains('card') ||
            parent.classList.contains('panel') ||
            parent.tagName === 'SECTION' ||
            parent.tagName === 'FIELDSET' ||
            parent.className.includes('container') ||
            parent.className.includes('section') ||
            parent.className.includes('block') ||
            parent.className.includes('card') ||
            parent.className.includes('group')
          )) {
            return parent;
          }
          if (parent) parent = parent.parentElement;
        }
        return h.parentElement;
      }
    }
    return null;
  }

  function extractDirectoryDetailsInline(profileEl) {
    const dirData = {
      docket: "",
      dot_number: "",
      entity_type: "",
      coverage_to: "",
      credit_score: "",
      insurance_carrier: ""
    };

    dirData.docket = getValByLabelInline("Docket", profileEl) || getValByLabelInline("MC/MX/FF Number", profileEl);
    dirData.dot_number = getValByLabelInline("DOT Number", profileEl) || getValByLabelInline("USDOT Number", profileEl);
    dirData.credit_score = getValByLabelInline("Credit score", profileEl);

    const genContainer = findSectionContainerInline("General Information", profileEl);
    if (genContainer) {
      if (!dirData.docket) dirData.docket = getValByLabelInline("Docket", genContainer);
      if (!dirData.dot_number) dirData.dot_number = getValByLabelInline("DOT Number", genContainer);
      dirData.entity_type = getValByLabelInline("Entity type", genContainer);
    }

    const dotContainer = findSectionContainerInline("DOT Authority & Insurance", profileEl);
    if (dotContainer) {
      dirData.coverage_to = getValByLabelInline("Coverage to", dotContainer);
      dirData.insurance_carrier = getValByLabelInline("Insurance carrier", dotContainer);
    }

    const creditContainer = findSectionContainerInline("Credit Profile", profileEl);
    if (creditContainer) {
      if (!dirData.credit_score) dirData.credit_score = getValByLabelInline("Credit score", creditContainer);
    }
    return dirData;
  }

  async function enrichLoadsWithDirectoryData(loads) {
    console.log(`[DAT Extractor] Enriching ${loads.length} loads with directory details...`);
    logToServer("DIRECTORY_ENRICHMENT_START", { totalLoads: loads.length, deepMode });
    resetDeepStats(loads.filter((l) => !l.isEmpty).length);
    reportDeepProgress();
    
    document.documentElement.setAttribute('data-dat-directory-scraping-active', 'true');
    try {
      let viewport = getScrollViewport();
      let rowHeight = measureRowHeight(viewport);

      // Reset scroll to top before enrichment starts
      setScrollTop(viewport, 0, loads.length, rowHeight);
      await sleep(1000);

    for (let i = 0; i < loads.length; i++) {
      if (window.__DAT_EXTRACTOR_V2_CANCEL__ || window.__DAT_AUTO_PILOT_STOP__) {
        console.log("[DAT Extractor] Directory enrichment cancelled.");
        logToServer("DIRECTORY_ENRICHMENT_CANCELLED");
        break;
      }

      try {
        const load = loads[i];
        if (load.isEmpty) continue;

        // Company-level directory data is cacheable; per-load detail never is.
        // When the cache hits we skip the directory tab but still open the drawer.
        let skipDirectory = false;
        let hasValidCache = false;
        let cachedDetails = null;
        if (load.company && directoryCache.has(load.company)) {
          cachedDetails = directoryCache.get(load.company);
          if (cachedDetails) {
            hasValidCache = true;
          }
        }

        if (hasValidCache) {
          const docketVal = cachedDetails.docket || cachedDetails.dir_docket || "";
          const dotNumberVal = cachedDetails.dot_number || cachedDetails.dir_dot_number || "";
          const entityTypeVal = cachedDetails.entity_type || cachedDetails.dir_gen_entity_type || "";
          const coverageToVal = cachedDetails.coverage_to || cachedDetails.dir_active_ins_coverage_to || "";
          const creditScoreVal = cachedDetails.credit_score || cachedDetails.dir_credit_score || "";
          const insCarrierVal = cachedDetails.insurance_carrier || cachedDetails.dir_active_ins_carrier || "";

          load.dir_docket = docketVal;
          load.dir_dot_number = dotNumberVal;
          load.dir_gen_entity_type = entityTypeVal;
          load.dir_active_ins_coverage_to = coverageToVal;
          load.dir_credit_score = creditScoreVal;
          load.dir_active_ins_carrier = insCarrierVal;

          load.docket = docketVal;
          load.dot_number = dotNumberVal;
          load.entity_type = entityTypeVal;
          load.coverage_to = coverageToVal;
          load.credit_score = creditScoreVal;
          load.insurance_carrier = insCarrierVal;

          load.directoryData = {
            docket: docketVal,
            dot_number: dotNumberVal,
            entity_type: entityTypeVal,
            coverage_to: coverageToVal,
            credit_score: creditScoreVal,
            insurance_carrier: insCarrierVal
          };

          applyDirectoryDeep(load, cachedDetails);

          console.log(`[DAT Extractor] Successfully enriched directory from cache for ${load.company}`);
          logToServer("DIRECTORY_CACHE_HIT", { company: load.company });
          if (progressEl) {
            progressEl.querySelector("#dat-v2-progress-msg").innerHTML =
              `Directory Scraping: ${i + 1} / ${loads.length} loads (Cache Hit)<br>` +
              `<span style="font-size:11px;color:#cbd5e1;">Current: ${escapeHtml(load.company || "Unknown Company")}</span>`;
          }
          // The rate, route, trip and contact panels are per-load, so the drawer
          // still has to be opened even though the company data is already known.
          if (!deepMode) continue;
          skipDirectory = true;
        }

        // Re-resolve viewport and row height dynamically now that we need to scroll/scrape
        viewport = getScrollViewport();
        rowHeight = measureRowHeight(viewport);

        logToServer("DIRECTORY_LOAD_START", { index: i + 1, company: load.company, origin: load.origin, destination: load.destination });

        // Update progress display
        if (progressEl) {
          progressEl.querySelector("#dat-v2-progress-msg").innerHTML =
            `Directory Scraping: ${i + 1} / ${loads.length} loads<br>` +
            `<span style="font-size:11px;color:#cbd5e1;">Current: ${escapeHtml(load.company || "Unknown Company")}</span>`;
        }

        let activeStateAcquired = false;
        const activeStateReleaseListener = () => {
          activeStateAcquired = false;
          releaseActiveState().catch(() => {});
        };
        window.addEventListener("DAT_ACTIVE_STATE_RELEASED", activeStateReleaseListener);

        try {
          await requestActiveState();
          activeStateAcquired = true;

          // Check if the row is already visible in the DOM before doing any scrolling
          let matchedRow = findRowForLoad(load);
          if (matchedRow && isSkeletonRow(matchedRow)) {
            matchedRow = null; // force scrolling/reload if it's currently a skeleton placeholder
          }

          let targetScroll = 0;
          if (!matchedRow) {
            // Calculate target scroll position: try using the exact scroll top when it was captured first
            targetScroll = (typeof load._scrollTop === 'number')
              ? load._scrollTop
              : Math.max(0, Math.floor(i * rowHeight - viewport.clientHeight / 2));

            // Scroll and poll until the row is rendered in the DOM (prevents skipping due to background tab throttling)
            const startScrollWait = Date.now();
            const maxScrollWait = document.hidden ? 12000 : 5000; // 12 seconds timeout in background tabs, 5s in foreground
            
            while (Date.now() - startScrollWait < maxScrollWait) {
              await scrollToPosition(viewport, targetScroll, loads.length, rowHeight);
              await sleep(document.hidden ? 400 : 200);
              matchedRow = findRowForLoad(load);
              if (matchedRow && !isSkeletonRow(matchedRow)) {
                break;
              }
            }

            if (matchedRow && isSkeletonRow(matchedRow)) {
              await waitForSkeletonsToLoad(document.hidden ? 3000 : 2000);
              matchedRow = findRowForLoad(load);
            }

            if (!matchedRow) {
              // RECOVERY: If details drawer is open, it resizes the viewport and shifts virtual scroll offsets.
              // Close the drawer and try scrolling to targetScroll again.
              const drawerEl = findDetailsDrawer();
              if (drawerEl) {
                logToServer("DIRECTORY_RECOVERY_CLOSE_DRAWER", { company: load.company });
                closeDetailsDrawer(drawerEl);
                await sleep(400); // wait for drawer transition
                
                // Re-scroll and poll again
                const startRetryWait = Date.now();
                while (Date.now() - startRetryWait < 4000) {
                  await scrollToPosition(viewport, targetScroll, loads.length, rowHeight);
                  await sleep(document.hidden ? 400 : 200);
                  matchedRow = findRowForLoad(load);
                  if (matchedRow && !isSkeletonRow(matchedRow)) {
                    break;
                  }
                }
                if (matchedRow && isSkeletonRow(matchedRow)) {
                  await waitForSkeletonsToLoad(document.hidden ? 3000 : 2000);
                  matchedRow = findRowForLoad(load);
                }
              }
            }

            if (!matchedRow) {
              // Fallback: try scrolling slightly up/down locally to trigger virtual scroll render
              const offsets = [-rowHeight, rowHeight, -rowHeight * 2, rowHeight * 2];
              for (const offset of offsets) {
                setScrollTop(viewport, Math.max(0, targetScroll + offset), loads.length, rowHeight);
                await sleep(document.hidden ? 450 : 250);
                matchedRow = findRowForLoad(load);
                if (matchedRow) break;
              }
            }
          }

          if (!matchedRow) {
            console.log(`[DAT Extractor] Could not find row element for load: ${load.company} to ${load.destination}. Skipping and moving to next row element.`);
            logToServer("DIRECTORY_ROW_NOT_FOUND", { company: load.company, origin: load.origin, destination: load.destination });
            if (deepMode && DEEP()) {
              DEEP().applySurfaceToLoad(load, null, "detailDrawer");
              if (load.extraction) {
                load.extraction.errors.push({ stage: "rowLookup", message: "row not found in virtual scroll" });
              }
            }
            continue;
          }

        // ── DEEP DETAIL PASS ──
        // Open the drawer and harvest everything behind it before any directory
        // work, so the detail data is captured even if the directory step fails.
        if (deepMode && DEEP()) {
          deepStats.current = `${load.company || "Unknown"} · ${load.origin} → ${load.destination}`;
          reportDeepProgress();
          if (progressEl) {
            progressEl.querySelector("#dat-v2-progress-msg").innerHTML =
              `Deep extraction: ${i + 1} / ${loads.length} loads<br>` +
              `<span style="font-size:11px;color:#cbd5e1;">${escapeHtml(deepStats.current)}</span>`;
          }
          await deepExtractLoadDetail(load, matchedRow);

          // Provisional roll-up so the progress panel moves in real time; the
          // authoritative pass runs once the directory stage has also finished.
          DEEP().finalizeExtraction(load, ["detailDrawer"]);
          deepStats.processed++;
          const provisional = load.extraction?.status;
          if (provisional === "complete") deepStats.complete++;
          else if (provisional === "partial") deepStats.partial++;
          else deepStats.failed++;
          deepStats.fields += load.extraction?.fieldsExtracted || 0;
          reportDeepProgress();
        }

        if (skipDirectory) continue;

        // ── OPTIMIZATION: Check if the row itself has a directory button/link ──
        let rowDirBtn = findDirectoryButton(matchedRow);
        let rowDirUrl = null;
        if (rowDirBtn) {
          if (rowDirBtn.tagName === 'A' && rowDirBtn.getAttribute('href')) {
            rowDirUrl = rowDirBtn.getAttribute('href');
            if (rowDirUrl && !rowDirUrl.startsWith('http')) {
              const base = window.location.origin;
              rowDirUrl = base + (rowDirUrl.startsWith('/') ? '' : '/') + rowDirUrl;
            }
          }
        }

        if (rowDirBtn && (rowDirUrl || rowDirBtn.tagName === 'A' || rowDirBtn.tagName === 'BUTTON' || rowDirBtn.tagName === 'SPAN' || rowDirBtn.tagName === 'DIV')) {
          console.log(`[DAT Extractor] Found directory link directly on row for ${load.company}. URL=${rowDirUrl || 'auto-detect'}`);
          logToServer("DIRECTORY_ROW_LINK_FOUND", { company: load.company, url: rowDirUrl || "auto-detect" });

          logToServer("DIRECTORY_SCRAPE_CALL", { company: load.company, url: rowDirUrl || "auto-detect" });
          const dirDetails = await scrapeDirectoryPage(rowDirUrl, rowDirBtn);
          logToServer("DIRECTORY_SCRAPE_RESULT", { company: load.company, success: !!dirDetails });

          if (dirDetails) {
            const docketVal = dirDetails.docket || dirDetails.dir_docket || "";
            const dotNumberVal = dirDetails.dot_number || dirDetails.dir_dot_number || "";
            const entityTypeVal = dirDetails.entity_type || dirDetails.dir_gen_entity_type || "";
            const coverageToVal = dirDetails.coverage_to || dirDetails.dir_active_ins_coverage_to || "";
            const creditScoreVal = dirDetails.credit_score || dirDetails.dir_credit_score || "";
            const insCarrierVal = dirDetails.insurance_carrier || dirDetails.dir_active_ins_carrier || "";

            load.dir_docket = docketVal;
            load.dir_dot_number = dotNumberVal;
            load.dir_gen_entity_type = entityTypeVal;
            load.dir_active_ins_coverage_to = coverageToVal;
            load.dir_credit_score = creditScoreVal;
            load.dir_active_ins_carrier = insCarrierVal;

            load.docket = docketVal;
            load.dot_number = dotNumberVal;
            load.entity_type = entityTypeVal;
            load.coverage_to = coverageToVal;
            load.credit_score = creditScoreVal;
            load.insurance_carrier = insCarrierVal;

            load.directoryData = {
              docket: docketVal,
              dot_number: dotNumberVal,
              entity_type: entityTypeVal,
              coverage_to: coverageToVal,
              credit_score: creditScoreVal,
              insurance_carrier: insCarrierVal
            };

            applyDirectoryDeep(load, dirDetails);
            if (dirDetails.__deep) load.directoryData.__deep = trimDeepForCache(dirDetails.__deep);

            if (load.company) {
              directoryCache.set(load.company, load.directoryData);
            }
            console.log(`[DAT Extractor] Successfully enriched directory for ${load.company}`);
          } else {
            load.directoryData = {
              docket: "",
              dot_number: "",
              entity_type: "",
              coverage_to: "",
              credit_score: "",
              insurance_carrier: ""
            };
            if (load.company) {
              directoryCache.set(load.company, load.directoryData);
            }
          }
          await sleep(1000 + Math.random() * 1000);
          continue;
        }

        // Find a clickable text cell (avoiding checkboxes/action cells for selection stability)
        // We prioritize '.route-container' and '.cell-route' as they are confirmed to open the details panel.
        // We avoid clicking the company name link directly because it stops click event propagation.
        const clickTarget = matchedRow.querySelector('.route-container') ||
          matchedRow.querySelector('.cell-route') ||
          matchedRow.querySelector('[class*="route"]') ||
          matchedRow.querySelector('.cell-rate') ||
          matchedRow.querySelector('[class*="rate"]') ||
          matchedRow.querySelector('.cell-age') ||
          matchedRow.querySelector('[class*="age"]') ||
          matchedRow;

        clickTarget.scrollIntoView({ block: "center", behavior: "auto" });
        await sleep(400);

        // Check if details drawer is already open and belongs to the current company
        let drawerEl = findDetailsDrawer();
        const drawerText = drawerEl ? drawerEl.textContent.toLowerCase() : "";
        const companyNameLower = load.company.toLowerCase();

        // Clean company name for flexible matching (handling RXO/Coyote Logistics etc.)
        const firstWord = companyNameLower.split(/[\s\/]/)[0];
        const isCorrectDrawerOpen = drawerEl && (
          drawerText.includes(companyNameLower) ||
          (firstWord && drawerText.includes(firstWord)) ||
          isCompanySimilar(load.company, drawerText)
        );

        logToServer("DIRECTORY_ROW_FOUND", {
          company: load.company,
          isExpanded: !!drawerEl,
          isCorrectDrawerOpen: isCorrectDrawerOpen
        });

        if (!isCorrectDrawerOpen) {
          console.log("[DAT Extractor] Clicking route cell to open/switch details drawer for:", load.company);
          simulateClick(clickTarget);
          await sleep(1500); // Wait for drawer to update
          drawerEl = findDetailsDrawer();
        }

        // Fallback: If drawer still not found or not showing correct company, click the matchedRow itself
        const currentDrawerText = drawerEl ? drawerEl.textContent.toLowerCase() : "";
        if (!drawerEl || !currentDrawerText.includes(firstWord || companyNameLower)) {
          console.log("[DAT Extractor] Drawer not showing correct company. Clicking entire row element as fallback.");
          simulateClick(matchedRow);
          await sleep(1500);
          drawerEl = findDetailsDrawer();
        }

        let tabClicked = false;
        if (drawerEl) {
          logToServer("DIRECTORY_DRAWER_FOUND", { company: load.company });
          // Activate the Company / Broker tab inside the details panel
          tabClicked = await clickCompanyTab(drawerEl);
        } else {
          logToServer("DIRECTORY_DRAWER_NOT_FOUND_WARNING", { company: load.company });

          // DIAGNOSTIC LOGGING: Log all drawer/panel-like DOM nodes to see what's happening
          try {
            const candidates = [];
            document.querySelectorAll('mat-drawer, mat-sidenav, [class*="drawer"], [class*="sidenav"], [class*="panel"], [class*="detail"]').forEach(el => {
              if (el.tagName === 'DIV' && (el.className.includes('cell') || el.className.includes('row') || el.className.includes('container'))) return; // skip row items
              candidates.push({
                tag: el.tagName,
                class: el.className,
                id: el.id,
                width: el.clientWidth,
                height: el.clientHeight,
                text: el.textContent.trim().slice(0, 120).replace(/\s+/g, ' ')
              });
            });
            logToServer("DIRECTORY_DRAWER_DIAGNOSTIC", {
              company: load.company,
              candidatesCount: candidates.length,
              candidates: candidates.slice(0, 10)
            });
          } catch (diagErr) {
            logToServer("DIRECTORY_DIAGNOSTIC_ERROR", { error: diagErr.message });
          }
        }

        // Check for inline company profile content (faster & avoids opening new tabs)
        let profileEl = null;
        const startProf = Date.now();
        // Dynamic wait based on whether tab was clicked or drawer was found
        const maxProfWait = tabClicked ? 4000 : (drawerEl ? 1000 : 0);
        if (maxProfWait > 0) {
          while (Date.now() - startProf < maxProfWait) {
            if (drawerEl) {
              profileEl = drawerEl.querySelector('.company-profile__content') ||
                drawerEl.querySelector('[class*="company-profile"]');
            }
            // Global document fallback if drawer mapping is off
            if (!profileEl) {
              profileEl = document.querySelector('.company-profile__content') ||
                document.querySelector('[class*="company-profile"]');
            }

            if (profileEl && profileEl.textContent.trim().length > 100) break;
            await sleep(200);
          }
        }

        if (profileEl) {
          logToServer("DIRECTORY_INLINE_FOUND", { company: load.company });
        } else {
          // Detailed debug log on failure
          const drawerText = drawerEl ? drawerEl.textContent.trim().slice(0, 300).replace(/\s+/g, ' ') : "No drawer found";
          const bodyText = document.body.textContent.trim().slice(0, 300).replace(/\s+/g, ' ');
          logToServer("DIRECTORY_INLINE_NOT_FOUND_DEBUG", {
            company: load.company,
            drawerText,
            bodyText,
            htmlHasProfileClass: !!document.querySelector('[class*="company-profile"]')
          });
        }

        if (profileEl) {
          try {
            // Harvest the whole inline company panel, not just the six legacy fields.
            let inlineDeepSchema = null;
            if (deepMode && DEEP()) {
              const profileResult = await DEEP().extractSurface(profileEl, {
                ids: DEEP().loadIdentifiers(load),
                maxClicks: Math.min(10, deepMaxClicks),
                maxDepth: 2,
                sectionTimeoutMs: document.hidden ? 3000 : 2200,
                isCancelled: isCancelledNow
              });
              DEEP().applySurfaceToLoad(load, profileResult, "companyProfile");
              inlineDeepSchema = trimDeepForCache(profileResult.schema);
            }

            const dirDetails = extractDirectoryDetailsInline(profileEl);
            if (dirDetails && (dirDetails.dot_number || dirDetails.docket)) {
              const docketVal = dirDetails.docket || dirDetails.dir_docket || "";
              const dotNumberVal = dirDetails.dot_number || dirDetails.dir_dot_number || "";
              const entityTypeVal = dirDetails.entity_type || dirDetails.dir_gen_entity_type || "";
              const coverageToVal = dirDetails.coverage_to || dirDetails.dir_active_ins_coverage_to || "";
              const creditScoreVal = dirDetails.credit_score || dirDetails.dir_credit_score || "";
              const insCarrierVal = dirDetails.insurance_carrier || dirDetails.dir_active_ins_carrier || "";

              load.dir_docket = docketVal;
              load.dir_dot_number = dotNumberVal;
              load.dir_gen_entity_type = entityTypeVal;
              load.dir_active_ins_coverage_to = coverageToVal;
              load.dir_credit_score = creditScoreVal;
              load.dir_active_ins_carrier = insCarrierVal;

              load.docket = docketVal;
              load.dot_number = dotNumberVal;
              load.entity_type = entityTypeVal;
              load.coverage_to = coverageToVal;
              load.credit_score = creditScoreVal;
              load.insurance_carrier = insCarrierVal;

              load.directoryData = {
                docket: docketVal,
                dot_number: dotNumberVal,
                entity_type: entityTypeVal,
                coverage_to: coverageToVal,
                credit_score: creditScoreVal,
                insurance_carrier: insCarrierVal
              };

              if (inlineDeepSchema) load.directoryData.__deep = inlineDeepSchema;
              if (load.company) {
                directoryCache.set(load.company, load.directoryData);
              }

              logToServer("DIRECTORY_INLINE_SUCCESS", { company: load.company, name: dirDetails.company_name });

              // Random minor delay (300-600ms)
              await sleep(300 + Math.random() * 300);
              continue;
            }
          } catch (inlineErr) {
            console.error("[DAT Extractor] Error doing inline extraction:", inlineErr);
            logToServer("DIRECTORY_INLINE_ERROR", { company: load.company, error: inlineErr.message });
          }
        }

        // ------------------------------------------------------------
        // Fallback: check/wait for the directory button
        // ------------------------------------------------------------
        // Only click the row if the details drawer is not already open
        const drawerToCheck = findDetailsDrawer();
        if (!drawerToCheck) {
          logToServer("ROW_EXPAND_ATTEMPT", { company: load.company });
          if (matchedRow && typeof matchedRow.click === "function") {
            matchedRow.click();
          }
          await sleep(500);
        }

        // Now wait up to 4 seconds for the DIRECTORY button to appear
        let dirBtn = null;
        logToServer("DIRECTORY_BUTTON_WAIT", { company: load.company });
        const startDet = Date.now();
        while (Date.now() - startDet < 4000) {
          const currentDrawer = findDetailsDrawer();
          dirBtn = findDirectoryButton(matchedRow) || (currentDrawer ? findDirectoryButton(currentDrawer) : null);
          if (dirBtn) break;
          await sleep(250);
        }

        let dirUrl = null;
        // If no button found after scoped search, try a global search
        if (!dirBtn) {
          dirBtn = findDirectoryButton(document);
        }

        if (dirBtn) {
          // If the element is a link with an href, use it directly
          if (dirBtn.tagName === 'A' && dirBtn.getAttribute('href')) {
            dirUrl = dirBtn.getAttribute('href');
            // Normalize relative URLs if needed
            if (dirUrl && !dirUrl.startsWith('http')) {
              const base = window.location.origin;
              dirUrl = base + (dirUrl.startsWith('/') ? '' : '/') + dirUrl;
            }
          }
        }

        if (!dirUrl && !dirBtn) {
          console.log(`[DAT Extractor] View in Directory button not found for load: ${load.company}`);
          logToServer("DIRECTORY_URL_NOT_FOUND", { company: load.company });
          continue;
        }

        console.log(`[DAT Extractor] Initiating directory scrape: URL=${dirUrl || 'auto-detect via click'}`);
        logToServer("DIRECTORY_URL_FOUND", { company: load.company, url: dirUrl || "auto-detect" });

        // Send message to background script to scrape the page
        logToServer("DIRECTORY_SCRAPE_CALL", { company: load.company, url: dirUrl || "auto-detect" });
        const dirDetails = await scrapeDirectoryPage(dirUrl, dirBtn);
        logToServer("DIRECTORY_SCRAPE_RESULT", { company: load.company, success: !!dirDetails });

        if (dirDetails) {
          const docketVal = dirDetails.docket || dirDetails.dir_docket || "";
          const dotNumberVal = dirDetails.dot_number || dirDetails.dir_dot_number || "";
          const entityTypeVal = dirDetails.entity_type || dirDetails.dir_gen_entity_type || "";
          const coverageToVal = dirDetails.coverage_to || dirDetails.dir_active_ins_coverage_to || "";
          const creditScoreVal = dirDetails.credit_score || dirDetails.dir_credit_score || "";
          const insCarrierVal = dirDetails.insurance_carrier || dirDetails.dir_active_ins_carrier || "";

          load.dir_docket = docketVal;
          load.dir_dot_number = dotNumberVal;
          load.dir_gen_entity_type = entityTypeVal;
          load.dir_active_ins_coverage_to = coverageToVal;
          load.dir_credit_score = creditScoreVal;
          load.dir_active_ins_carrier = insCarrierVal;

          load.docket = docketVal;
          load.dot_number = dotNumberVal;
          load.entity_type = entityTypeVal;
          load.coverage_to = coverageToVal;
          load.credit_score = creditScoreVal;
          load.insurance_carrier = insCarrierVal;

          load.directoryData = {
            docket: docketVal,
            dot_number: dotNumberVal,
            entity_type: entityTypeVal,
            coverage_to: coverageToVal,
            credit_score: creditScoreVal,
            insurance_carrier: insCarrierVal
          };

          applyDirectoryDeep(load, dirDetails);
          if (dirDetails.__deep) load.directoryData.__deep = trimDeepForCache(dirDetails.__deep);

          if (load.company) {
            directoryCache.set(load.company, load.directoryData);
          }
          console.log(`[DAT Extractor] Successfully enriched directory for ${load.company}`);
        } else {
          console.log(`[DAT Extractor] Failed to scrape directory for ${load.company}`);
          load.directoryData = {
            docket: "",
            dot_number: "",
            entity_type: "",
            coverage_to: "",
            credit_score: "",
            insurance_carrier: ""
          };
          if (load.company) {
            directoryCache.set(load.company, load.directoryData);
          }
        }
        } finally {
          window.removeEventListener("DAT_ACTIVE_STATE_RELEASED", activeStateReleaseListener);
          if (activeStateAcquired) {
            activeStateAcquired = false;
            await releaseActiveState();
          }
          // Close details drawer at the end of each load's processing to keep the viewport clean
          const drawerEl = findDetailsDrawer();
          if (drawerEl) {
            closeDetailsDrawer(drawerEl);
            await sleep(350); // wait for drawer transition
          }
        }

        // Random human-like delay between directory crawls to bypass rate limits (1-2 seconds)
        await sleep(1000 + Math.random() * 1000);
      } catch (err) {
        console.error(`[DAT Extractor] Error processing row ${i + 1}:`, err);
        logToServer("DIRECTORY_ROW_ERROR", { index: i + 1, company: loads[i]?.company || "unknown", error: err.message || String(err) });
      }
    }
    } finally {
      document.documentElement.removeAttribute('data-dat-directory-scraping-active');

      // Authoritative roll-up: recompute every load's extraction status now that
      // both the detail and directory stages have had their chance.
      if (deepMode && DEEP()) {
        const D = DEEP();
        deepStats.complete = 0;
        deepStats.partial = 0;
        deepStats.failed = 0;
        deepStats.fields = 0;
        for (const load of loads) {
          if (load.isEmpty) continue;
          D.finalizeExtraction(load, ["detailDrawer"]);
          const st = load.extraction?.status;
          if (st === "complete") deepStats.complete++;
          else if (st === "partial") deepStats.partial++;
          else deepStats.failed++;
          deepStats.fields += load.extraction?.fieldsExtracted || 0;
        }
        deepStats.current = "";
        reportDeepProgress();
        logToServer("DEEP_EXTRACTION_SUMMARY", {
          total: deepStats.total,
          complete: deepStats.complete,
          partial: deepStats.partial,
          failed: deepStats.failed,
          fields: deepStats.fields,
          retries: deepStats.retries,
          net: D.netStats()
        });
      }
    }
  }

  function findDirectoryButton(container = document) {
    if (!container) container = document;

    // Helper to validate that a URL is a directory profile link
    const isValidDirUrl = (href) => {
      if (!href) return false;
      const h = href.toLowerCase();
      // Exclude common non‑directory actions
      if (h.startsWith('tel:') || h.startsWith('mailto:') || h.startsWith('javascript:') || h.startsWith('sms:')) return false;
      // Reject navigation/sidebar links that are unrelated
      if (h.includes('my-loads') || h.includes('search-loads') || h.includes('search-trucks') || h.includes('my-trucks') || h.includes('/list/') || h.includes('dashboard') || h.includes('private-network')) {
        return false;
      }
      if (h.includes("directory.dat.com")) {
        return true;
      }
      // Accept URLs that look like directory or office details
      const hasDirKeywords = h.includes('directory') || h.includes('office') || h.includes('details') || h.includes('broker') || h.includes('carrier');
      // Require either "offices" or "details" to avoid false positives, but allow plain directory URLs as well
      return hasDirKeywords && (h.includes('offices') || h.includes('details') || h.includes('profile'));
    };

    // 1. Direct anchors with a valid href
    const anchors = Array.from(container.querySelectorAll('a[href]'));
    for (const a of anchors) {
      if (isValidDirUrl(a.getAttribute('href'))) {
        return a;
      }
    }

    // 2. Elements whose visible text matches common phrasing
    const elements = Array.from(container.querySelectorAll('a, button, span, div, mat-icon'));
    for (const el of elements) {
      if (el.children.length === 0 || (el.children.length === 1 && el.querySelector('mat-icon'))) {
        const text = el.textContent.trim().toLowerCase();
        if (text.includes('view in directory') || text === 'directory' || text.includes('view directory') || text.includes('directory profile') || text.includes('view profile')) {

          const anchor = el.closest('a');
          if (anchor && isValidDirUrl(anchor.getAttribute('href'))) {
            return anchor;
          }

          // If element itself is an <a> without href but matches, treat it as button
          if (el.tagName === 'A') {
            return el;
          }

          // Search up to 3 ancestors for a suitable anchor
          let parent = el.parentElement;
          for (let depth = 0; depth < 3; depth++) {
            if (parent) {
              const innerAnchors = Array.from(parent.querySelectorAll('a[href]'));
              for (const a of innerAnchors) {
                if (isValidDirUrl(a.getAttribute('href'))) {
                  return a;
                }
              }
              parent = parent.parentElement;
            }
          }
        }
      }
    }
    return null;
  }

  async function requestActiveState() {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ action: "requestActiveState" }, (response) => {
        resolve(response || { success: false });
      });
    });
  }

  async function releaseActiveState() {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ action: "releaseActiveState" }, (response) => {
        resolve(response || { success: false });
      });
    });
  }

  async function scrapeDirectoryPage(url, btnElement) {
    return new Promise((resolve) => {
      const listener = (msg) => {
        if (msg.action === "directoryScrapedDone" && (!url || msg.url === url || msg.url.includes(url) || url.includes(msg.url))) {
          chrome.runtime.onMessage.removeListener(listener);
          if (msg.error) {
            console.warn("[DAT Extractor] Directory scrape failed with error:", msg.error);
            resolve(null);
          } else {
            resolve(msg.data);
          }
        }
      };
      chrome.runtime.onMessage.addListener(listener);

      // Helper to release the active search tab lock early (once the tab is triggered)
      const triggerRelease = () => {
        window.dispatchEvent(new CustomEvent("DAT_ACTIVE_STATE_RELEASED"));
      };

      if (url) {
        chrome.runtime.sendMessage({ action: "openAndScrapeDirectory", url });
        triggerRelease();
      } else if (btnElement) {
        simulateClick(btnElement);
        setTimeout(triggerRelease, 300);
      } else {
        chrome.runtime.onMessage.removeListener(listener);
        triggerRelease();
        resolve(null);
      }

      // Safety timeout of 45 seconds
      setTimeout(() => {
        chrome.runtime.onMessage.removeListener(listener);
        resolve(null);
      }, 45000);
    });
  }

  if (window.location.host.includes("directory.dat.com")) {
    console.log("[DAT Extractor] Running in DAT Directory mode...");
    logToServer("DIR_SCRAPER_START", { url: window.location.href });
    (async () => {
      const loaded = await waitPageLoaded("h2, .company-name, .summary", 30000);
      logToServer("DIR_SCRAPER_LOADED", { url: window.location.href, loaded });
      if (!loaded) {
        console.error("[DAT Extractor] Timeout waiting for directory page to load.");
        chrome.runtime.sendMessage({ action: "directoryDataScraped", success: false, error: "Load timeout", url: window.location.href });
        return;
      }
      await sleep(1000);
      try {
        logToServer("DIR_SCRAPER_EXTRACT_START", { url: window.location.href });
        const data = extractDirectoryDetails();

        // Beyond the six legacy fields, harvest the whole profile: Office
        // Information (name, address, phone, fax, affiliations), General
        // Information, DOT Authority & Insurance, Company Background, Credit Profile.
        const D = DEEP();
        if (D) {
          try {
            const root =
              document.querySelector('main, [role="main"], .details-content, [class*="details-content"], [class*="profile-content"]') ||
              document.body;
            const dirResult = await D.extractSurface(root, {
              maxClicks: 14,
              maxDepth: 2,
              sectionTimeoutMs: 2500,
              includeEmbeddedJson: true,
              isCancelled: isCancelledNow
            });
            data.__deep = dirResult.schema;
            data.__deepMeta = dirResult.meta;
            data.__deepUrl = window.location.href;

            // Backfill the legacy six from the deep schema when the label-based
            // extractor missed them (DAT renames these labels periodically).
            const g = (p) => D.valueOrNull(D.getPath(dirResult.schema, p));
            if (!data.docket) data.docket = g("company.docket") || "";
            if (!data.dot_number) data.dot_number = g("company.dotNumber") || "";
            if (!data.credit_score) data.credit_score = g("company.creditScore") || "";
            if (!data.entity_type) data.entity_type = g("company.entityType") || "";
            if (!data.coverage_to) data.coverage_to = g("company.insuranceCoverageTo") || "";
            if (!data.insurance_carrier) data.insurance_carrier = g("company.insuranceCarrier") || "";

            logToServer("DIR_SCRAPER_DEEP_OK", {
              url: window.location.href,
              fields: dirResult.meta?.fieldsExtracted || 0,
              sections: (dirResult.meta?.sectionsVisited || []).length
            });
          } catch (deepErr) {
            logToServer("DIR_SCRAPER_DEEP_ERROR", { url: window.location.href, error: deepErr.message });
          }
        }

        console.log("[DAT Extractor] Directory details scraped successfully:", data);
        logToServer("DIR_SCRAPER_EXTRACT_SUCCESS", { url: window.location.href, companyName: data?.company_name });
        chrome.runtime.sendMessage({
          action: "directoryDataScraped",
          success: true,
          data: data,
          url: window.location.href
        });
      } catch (e) {
        console.error("[DAT Extractor] Error scraping directory details:", e);
        logToServer("DIR_SCRAPER_EXTRACT_ERROR", { url: window.location.href, error: e.message });
        chrome.runtime.sendMessage({
          action: "directoryDataScraped",
          success: false,
          error: e.message,
          url: window.location.href
        });
      }
    })();
  }

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

  connectKeepAlive();
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
})();
