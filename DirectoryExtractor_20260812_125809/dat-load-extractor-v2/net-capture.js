// net-capture.js
// MAIN-world network interceptor for the DAT Load Extractor deep-extraction engine.
//
// The DAT One SPA renders every load detail from JSON it fetches over XHR/fetch.
// Whatever the drawer shows on screen, the API response already held — usually with
// more precision (raw numbers instead of "$1,343", ISO dates instead of "Aug 13").
// This file mirrors those payloads out to the isolated content-script world so the
// extractor can prefer structured data over scraped text.
//
// It is strictly read-only: responses are cloned, never modified, never blocked.
(() => {
  if (window.__DAT_NET_CAPTURE_INSTALLED__) return;
  window.__DAT_NET_CAPTURE_INSTALLED__ = true;

  const EVENT_NAME = "DAT_NET_CAPTURE";
  const MAX_BODY_BYTES = 3 * 1024 * 1024; // ignore anything bigger — not per-load data
  const RELEVANT_HOST = /(^|\.)dat\.com$/i;

  // Endpoints that never carry load data; skipping them keeps the relay quiet.
  const IGNORE_URL = /(\.js|\.css|\.png|\.jpg|\.jpeg|\.svg|\.woff2?|\.ttf|\.ico|\.map)(\?|$)|google-analytics|googletagmanager|doubleclick|segment\.io|sentry|datadoghq|fullstory|pendo|hotjar|launchdarkly|log_event/i;

  function isRelevant(url) {
    try {
      const u = new URL(String(url), window.location.href);
      if (!RELEVANT_HOST.test(u.hostname)) return false;
      if (IGNORE_URL.test(u.pathname + u.search)) return false;
      return true;
    } catch (e) {
      return false;
    }
  }

  function relay(payload) {
    try {
      window.dispatchEvent(new CustomEvent(EVENT_NAME, { detail: payload }));
    } catch (e) {
      // A structured-clone failure means the payload held something exotic; drop it.
    }
  }

  function publish(url, method, status, text) {
    if (!text || text.length > MAX_BODY_BYTES) return;
    const trimmed = text.trim();
    if (!trimmed || (trimmed[0] !== "{" && trimmed[0] !== "[")) return;
    let body;
    try {
      body = JSON.parse(trimmed);
    } catch (e) {
      return; // not JSON — the DOM remains the source for this one
    }
    relay({
      url: String(url),
      method: String(method || "GET").toUpperCase(),
      status: status || 0,
      ts: Date.now(),
      body
    });
  }

  // ── fetch ──
  try {
    const nativeFetch = window.fetch;
    if (typeof nativeFetch === "function") {
      window.fetch = function (input, init) {
        const url = (input && typeof input === "object" && "url" in input) ? input.url : input;
        const method = (init && init.method) || (input && input.method) || "GET";
        const promise = nativeFetch.apply(this, arguments);
        if (!isRelevant(url)) return promise;
        return promise.then((response) => {
          try {
            // Clone so the app still gets an unread, untouched body.
            response.clone().text().then((text) => {
              publish(url, method, response.status, text);
            }).catch(() => {});
          } catch (e) {}
          return response;
        });
      };
    }
  } catch (e) {}

  // ── XMLHttpRequest ──
  try {
    const XHR = window.XMLHttpRequest;
    const open = XHR.prototype.open;
    const send = XHR.prototype.send;

    XHR.prototype.open = function (method, url) {
      try {
        this.__datNetMethod = method;
        this.__datNetUrl = url;
      } catch (e) {}
      return open.apply(this, arguments);
    };

    XHR.prototype.send = function () {
      try {
        if (isRelevant(this.__datNetUrl)) {
          this.addEventListener("load", () => {
            try {
              const type = this.responseType;
              if (type === "" || type === "text") {
                publish(this.__datNetUrl, this.__datNetMethod, this.status, this.responseText);
              } else if (type === "json" && this.response) {
                relay({
                  url: String(this.__datNetUrl),
                  method: String(this.__datNetMethod || "GET").toUpperCase(),
                  status: this.status,
                  ts: Date.now(),
                  body: this.response
                });
              }
            } catch (e) {}
          });
        }
      } catch (e) {}
      return send.apply(this, arguments);
    };
  } catch (e) {}
})();
