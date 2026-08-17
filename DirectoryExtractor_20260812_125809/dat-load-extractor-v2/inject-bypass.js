// inject-bypass.js
// Runs in the MAIN world at document_start to bypass background tab layout/timing throttling
(() => {
  const logToServer = (eventType, details = {}) => {
    fetch("http://127.0.0.1:5000/log_event", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ event_type: eventType, details })
    }).catch(() => {});
  };

  try {
    logToServer("BYPASS_SCRIPT_START", { url: window.location.href });

    // Intercept window.open calls to directory URLs to open in background
    try {
      const originalWindowOpen = window.open;
      window.open = function(url, target, features) {
        if (url && (String(url).includes("directory.dat.com") || String(url).includes("/offices/") || String(url).includes("/directory/") || String(url).includes("/profile/"))) {
          if (document.documentElement.getAttribute('data-dat-directory-scraping-active') === 'true') {
            window.dispatchEvent(new CustomEvent("DAT_OPEN_BACKGROUND_TAB", { detail: { url: String(url) } }));
            return null;
          }
        }
        return originalWindowOpen.apply(this, arguments);
      };
    } catch (e) {
      logToServer("BYPASS_WINDOW_OPEN_OVERRIDE_FAILED", { error: e.message });
    }

    // Override Document prototype properties
    Object.defineProperty(Document.prototype, 'hidden', { get: () => false, configurable: true });
    Object.defineProperty(Document.prototype, 'visibilityState', { get: () => 'visible', configurable: true });
    Object.defineProperty(Document.prototype, 'webkitHidden', { get: () => false, configurable: true });
    
    // Override document instance directly
    Object.defineProperty(document, 'hidden', { get: () => false, configurable: true });
    Object.defineProperty(document, 'visibilityState', { get: () => 'visible', configurable: true });
    Object.defineProperty(document, 'webkitHidden', { get: () => false, configurable: true });
    
    // Override hasFocus
    Document.prototype.hasFocus = function() { return true; };
    document.hasFocus = function() { return true; };

    // Prevent visibilitychange event from dispatching or modify event properties
    const originalDispatchEvent = EventTarget.prototype.dispatchEvent;
    EventTarget.prototype.dispatchEvent = function(event) {
      if (event && event.type === 'visibilitychange') {
        Object.defineProperty(event, 'target', { value: document, configurable: true });
        Object.defineProperty(event, 'currentTarget', { value: document, configurable: true });
      }
      return originalDispatchEvent.call(this, event);
    };

    // Keep track of original addEventListener to bypass custom visibility triggers
    const orgAddEventListener = EventTarget.prototype.addEventListener;
    EventTarget.prototype.addEventListener = function(type, listener, options) {
      if (type === 'visibilitychange') {
        const wrappedListener = function(event) {
          try {
            listener.call(this, event);
          } catch(e) {}
        };
        return orgAddEventListener.call(this, type, wrappedListener, options);
      }
      return orgAddEventListener.call(this, type, listener, options);
    };

    // Override requestAnimationFrame to run continuously in background tabs
    let workerSupported = false;
    try {
      const workerCode = `
        self.onmessage = function(e) {
          if (e.data === 'tick') {
            setInterval(() => {
              self.postMessage('tick');
            }, 200); // 5fps (enough for background tabs, avoids pegging CPU)
          }
        };
      `;
      const blob = new Blob([workerCode], { type: 'application/javascript' });
      const worker = new Worker(URL.createObjectURL(blob));
      
      const callbacks = [];
      let nextId = 1;
      
      worker.onmessage = function() {
        const now = performance.now();
        const currentCallbacks = [...callbacks];
        callbacks.length = 0; // Clear
        for (const cb of currentCallbacks) {
          try { cb.fn(now); } catch(e) {}
        }
      };
      
      worker.postMessage('tick');
      
      window.requestAnimationFrame = function(callback) {
        const id = nextId++;
        callbacks.push({ id, fn: callback });
        return id;
      };
      
      window.cancelAnimationFrame = function(id) {
        const idx = callbacks.findIndex(c => c.id === id);
        if (idx !== -1) {
          callbacks.splice(idx, 1);
        }
      };
      
      workerSupported = true;
      logToServer("BYPASS_WORKER_INIT_SUCCESS");
    } catch (e) {
      logToServer("BYPASS_WORKER_INIT_FAILED", { error: e.message });
    }
    
    if (!workerSupported) {
      window.requestAnimationFrame = function(callback) {
        return setTimeout(() => {
          try { callback(performance.now()); } catch(e) {}
        }, 16);
      };
      window.cancelAnimationFrame = function(id) {
        clearTimeout(id);
      };
      logToServer("BYPASS_TIMEOUT_FALLBACK_INIT");
    }
  } catch (e) {
    logToServer("BYPASS_CRITICAL_ERROR", { error: e.message });
  }
})();
