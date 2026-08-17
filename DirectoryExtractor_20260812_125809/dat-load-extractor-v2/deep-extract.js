// deep-extract.js — Deep Load Extraction Engine (v3)
//
// The row scraper in content.js reads the search-results table. This file reads
// everything *behind* a row: the details drawer, its tabs, its accordions, the route
// panel, the company profile, and the DAT Directory office page — then normalizes all
// of it into one record per load.
//
// Design rules that this file follows throughout:
//   • Never invent a value. A field that was not found stays null.
//   • Never overwrite a real value with an empty one during merges.
//   • Never click anything that books, bids, calls, emails, saves or navigates away.
//   • Anything found but not recognised is kept under additionalData, so a DAT
//     redesign that adds a field degrades to "unmapped" rather than "lost".
//
// Runs in the isolated content-script world and exposes window.__DAT_DEEP__.
(() => {
  if (window.__DAT_DEEP__) return;

  // ══════════════════════════════════════════════════════════════════
  //  Timing helpers (worker-backed so background tabs are not throttled)
  // ══════════════════════════════════════════════════════════════════
  let sleepWorker = null;
  let nextSleepId = 0;
  const sleepResolves = new Map();

  function initSleepWorker() {
    if (sleepWorker) return;
    try {
      const blob = new Blob([
        `self.onmessage=function(e){var d=e.data;setTimeout(function(){self.postMessage({id:d.id})},d.ms)}`
      ], { type: "application/javascript" });
      sleepWorker = new Worker(URL.createObjectURL(blob));
      sleepWorker.onmessage = (e) => {
        const r = sleepResolves.get(e.data.id);
        if (r) { sleepResolves.delete(e.data.id); r(); }
      };
    } catch (err) {
      sleepWorker = null;
    }
  }

  function sleep(ms) {
    initSleepWorker();
    if (!sleepWorker) return new Promise((r) => setTimeout(r, ms));
    return new Promise((resolve) => {
      const id = nextSleepId++;
      sleepResolves.set(id, resolve);
      sleepWorker.postMessage({ id, ms });
    });
  }

  /**
   * Resolve once the subtree has stopped mutating for `quietMs`, or on timeout.
   * This is the readiness primitive used after every click — never a fixed delay.
   */
  function waitForStable(root, opts = {}) {
    const quietMs = opts.quietMs ?? 260;
    const timeoutMs = opts.timeoutMs ?? 3500;
    // A panel that renders on a delayed timer produces no mutations at first.
    // Without a floor the quiet timer would fire before the content appears.
    const minMs = opts.minMs ?? 0;
    const startedAt = Date.now();
    const target = (root && root.nodeType === 1) ? root : document.body;
    return new Promise((resolve) => {
      let quietTimer = null;
      let done = false;
      let observer = null;
      let mutations = 0;

      const finish = (reason) => {
        if (done) return;
        done = true;
        if (quietTimer) clearTimeout(quietTimer);
        if (observer) { try { observer.disconnect(); } catch (e) {} }
        // `mutated` tells the caller whether a click did anything at all, which
        // distinguishes an inert control from an exhausted surface.
        resolve({ reason, mutated: mutations > 0, mutations });
      };

      const arm = () => {
        if (quietTimer) clearTimeout(quietTimer);
        const elapsed = Date.now() - startedAt;
        const wait = Math.max(quietMs, minMs - elapsed);
        quietTimer = setTimeout(() => {
          if (Date.now() - startedAt < minMs) { arm(); return; }
          finish("quiet");
        }, wait);
      };

      try {
        observer = new MutationObserver((records) => {
          mutations += records.length;
          arm();
        });
        observer.observe(target, { childList: true, subtree: true, characterData: true, attributes: true });
      } catch (e) {
        return finish("no-observer");
      }
      arm();
      setTimeout(() => finish("timeout"), timeoutMs);
    });
  }

  /** Wait until `check()` returns truthy, polling on the worker clock. */
  async function waitFor(check, timeoutMs = 3000, intervalMs = 120) {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      try {
        const v = check();
        if (v) return v;
      } catch (e) {}
      await sleep(intervalMs);
    }
    return null;
  }

  // ══════════════════════════════════════════════════════════════════
  //  Text / value utilities
  // ══════════════════════════════════════════════════════════════════
  // Placeholder glyphs only. "None" and "No" are NOT placeholders in this
  // domain — they are real DOT authority statuses and must survive.
  const DASHES = new Set(["–", "-", "—", "--", "n/a", "null", "undefined", ""]);

  // Material-icon ligatures leak into textContent. Only compound ligatures are
  // listed here: single English words like "phone", "email", "check" or "info"
  // are legitimate DAT labels and values, and stripping them corrupted real
  // fields ("Office phone" became "Office").
  const ICON_WORDS = /\b(open_in_new|arrow_forward|arrow_back|arrow_drop_down|chevron_right|chevron_left|expand_more|expand_less|keyboard_arrow_down|keyboard_arrow_up|keyboard_arrow_right|keyboard_arrow_left|info_outline|help_outline|content_copy|star_border|more_vert|more_horiz|local_shipping|open_in_full|check_circle|radio_button_unchecked)\b/gi;

  const ICON_SELECTOR = "mat-icon, .mat-icon, .material-icons, .material-icons-outlined, .material-symbols-outlined, i.fa, i.fas, i.far";

  /**
   * Text of an element with icon-font ligatures removed at the source.
   * Icon elements render as glyphs but contribute their ligature name to
   * textContent, so they are subtracted rather than word-filtered.
   */
  function txt(el) {
    if (!el) return "";
    let s = String(el.textContent || "");

    // <br> carries the line structure of addresses, and textContent drops it,
    // welding "…Airport Road" to "Mississauga, ON" into one unparseable string.
    if (el.querySelector) {
      let hasBr = false;
      try { hasBr = !!el.querySelector("br"); } catch (e) {}
      if (hasBr) {
        s = String(el.innerHTML || "")
          .replace(/<br\s*\/?>/gi, "\n")
          .replace(/<[^>]+>/g, " ")
          .replace(/&nbsp;/gi, " ")
          .replace(/&amp;/gi, "&")
          .replace(/&lt;/gi, "<")
          .replace(/&gt;/gi, ">")
          .replace(/&quot;/gi, '"')
          .replace(/&#0?39;/gi, "'");
      }
    }

    if (s && el.querySelectorAll) {
      let icons;
      try { icons = el.querySelectorAll(ICON_SELECTOR); } catch (e) { icons = []; }
      for (const ic of icons) {
        const t = ic.textContent;
        if (t && t.trim()) s = s.split(t).join(" ");
      }
    }
    return s.replace(/\s+/g, " ").trim();
  }

  function clean(value) {
    if (value == null) return "";
    let s = String(value).replace(/ /g, " ");
    s = s.replace(ICON_WORDS, " ");
    s = s.replace(/\s+/g, " ").trim();
    s = s.replace(/^[:•\-–—]\s*/, "").trim();
    return s;
  }

  /** Normalize to null when the page is showing a placeholder rather than a value. */
  function valueOrNull(v) {
    const s = clean(v);
    if (!s) return null;
    if (DASHES.has(s.toLowerCase())) return null;
    return s;
  }

  function isBlankish(v) {
    return valueOrNull(v) === null;
  }

  function normLabel(s) {
    return clean(s)
      .toLowerCase()
      .replace(/[:*]+\s*$/, "")
      .replace(/[()]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function camelKey(s) {
    const parts = clean(s)
      .replace(/[:*]+$/, "")
      .replace(/[^A-Za-z0-9]+/g, " ")
      .trim()
      .split(/\s+/)
      .filter(Boolean);
    if (!parts.length) return null;
    return parts[0].toLowerCase() + parts.slice(1).map((p) => p[0].toUpperCase() + p.slice(1).toLowerCase()).join("");
  }

  function isVisible(el) {
    if (!el || el.nodeType !== 1) return false;
    try {
      const style = window.getComputedStyle(el);
      if (style.display === "none" || style.visibility === "hidden") return false;
      if (style.opacity === "0") return false;
      // In a background tab layout boxes collapse to 0×0; trust the style instead.
      if (document.hidden) return true;
      const rect = el.getBoundingClientRect();
      return rect.width > 0 || rect.height > 0;
    } catch (e) {
      return false;
    }
  }

  const MONEY_RE = /\$\s?-?[\d,]+(?:\.\d+)?/g;
  const PHONE_RE = /(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?:\s*(?:x|ext\.?)\s*\d{1,6})?/gi;
  const EMAIL_RE = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g;
  const CITY_STATE_RE = /^([A-Za-z][A-Za-z .'\-]{1,40}),\s*([A-Z]{2})$/;
  const ZIP_RE = /\b(\d{5}(?:-\d{4})?|[A-Z]\d[A-Z]\s?\d[A-Z]\d)\b/;

  function firstMatch(text, re) {
    if (!text) return null;
    const m = String(text).match(re);
    return m ? m[0].trim() : null;
  }

  function allMatches(text, re) {
    if (!text) return [];
    const m = String(text).match(re);
    return m ? m.map((x) => x.trim()) : [];
  }

  function toNumber(v) {
    const s = clean(v);
    if (!s) return null;
    const m = s.replace(/,/g, "").match(/-?\d+(?:\.\d+)?/);
    return m ? Number(m[0]) : null;
  }

  /**
   * Split a free-form US/CA address block into parts.
   * "820-5915 Airport Road, Mississauga, ON L4V1T1 CA"
   */
  function parseAddress(raw) {
    const s = valueOrNull(raw);
    if (!s) return null;
    const out = { raw: s, line1: null, line2: null, city: null, state: null, zip: null, country: null };

    // Preserve the original break structure when the DOM gave us one.
    const parts = s.split(/\s*(?:\n|,(?=\s*[A-Za-z]))\s*/).map((p) => p.trim()).filter(Boolean);
    const region = parts.length ? parts[parts.length - 1] : s;

    const zip = firstMatch(region, ZIP_RE);
    if (zip) out.zip = zip;

    const countryM = region.match(/\b(USA|US|CA|CAN|CANADA|MX|MEX|MEXICO)\b\s*$/i);
    if (countryM) out.country = countryM[1].toUpperCase();

    const stateM = region.match(/\b([A-Z]{2})\b(?=\s*(?:\d|[A-Z]\d|$))/);
    if (stateM && stateM[1] !== out.country) out.state = stateM[1];

    // Whatever remains of the last segment after removing state/zip/country is
    // the city; if nothing remains, the city is the segment before it.
    const regionLeftover = region
      .replace(ZIP_RE, "")
      .replace(/\b(USA|US|CA|CAN|CANADA|MX|MEX|MEXICO)\b\s*$/i, "")
      .replace(/\b[A-Z]{2}\b\s*$/, "")
      .trim()
      .replace(/[,\s]+$/, "");

    const STREET_SUFFIX = /\b(ave|avenue|st|street|rd|road|blvd|boulevard|dr|drive|ln|lane|way|pkwy|parkway|hwy|highway|ct|court|pl|place|ste|suite|unit|floor|fl)\b\.?$/i;

    if (parts.length >= 3) {
      out.line1 = parts[0];
      out.city = regionLeftover || parts[parts.length - 2];
      const midStart = 1;
      const midEnd = regionLeftover ? parts.length - 1 : parts.length - 2;
      const mid = parts.slice(midStart, midEnd);
      out.line2 = mid.length ? mid.join(", ") : null;
    } else if (parts.length === 2) {
      if (regionLeftover) {
        out.line1 = parts[0];
        out.city = regionLeftover;
      } else {
        // "305 MADISON AVE. MORRISTOWN, NJ 07962" — street and city share a segment.
        const words = parts[0].split(/\s+/);
        const last = words[words.length - 1];
        if (words.length >= 3 && last && !STREET_SUFFIX.test(last) && /^[A-Za-z][A-Za-z.'\-]{2,}$/.test(last)) {
          out.city = last.replace(/\.$/, "");
          out.line1 = words.slice(0, -1).join(" ").replace(/[,\s]+$/, "");
        } else {
          out.line1 = parts[0];
        }
      }
    } else {
      out.line1 = s;
    }
    return out;
  }

  // ══════════════════════════════════════════════════════════════════
  //  Interaction safety
  // ══════════════════════════════════════════════════════════════════
  //
  // Section 14 of the brief: explore everything that reveals data, touch nothing
  // that acts on Boss's behalf. The deny list wins over the allow list, always.

  const UNSAFE_TEXT = /\b(book|bid|offer|quote|call|connect|contact\s+now|send|email\s+(broker|company|now)|message|save|favorite|favourite|delete|remove|clear|report|flag|hide|block|unblock|mark\s+as|add\s+to|share|print|export|download|logout|sign\s*out|subscribe|upgrade|buy|purchase|pay|checkout|apply|submit|confirm|accept|decline|reject|assign|dispatch|post\s+(a\s+)?(truck|load)|new\s+search|search|refresh|reload|rateview|open\s+in|view\s+in\s+directory|next|previous|prev\b|page\s*\d|sort|filter|settings|preferences|feedback|help|support|log\s*in|sign\s*in)\b/i;

  const SAFE_TEXT = /\b(view\s+route|route|show\s+(more|all|details)|more\s+(info|details)|see\s+(more|all|details)|details?|expand|company|broker|carrier|contact|office|truck|equipment|rate|rates|market|spot|contract|location|history|additional|general|summary|information|profile|credit|insurance|authority|background|stops?|schedule|notes?|comments?|requirements?|specs?)\b/i;

  const UNSAFE_ATTR = /\b(book|bid|offer|call|email|save|delete|remove|report|flag|block|share|print|export|download|submit|apply|logout|signout|search|rateview|external)\b/i;

  function elementSignature(el) {
    const bits = [
      el.tagName,
      el.getAttribute("data-test") || "",
      el.getAttribute("aria-label") || "",
      el.getAttribute("title") || "",
      typeof el.className === "string" ? el.className : "",
      el.id || "",
      txt(el).slice(0, 60)
    ];
    return bits.join("|");
  }

  /**
   * Decide whether an element may be clicked during traversal.
   * Returns { safe: boolean, reason: string }.
   */
  function classifyInteractive(el) {
    if (!el || el.nodeType !== 1) return { safe: false, reason: "not-element" };
    if (el.disabled) return { safe: false, reason: "disabled" };

    const tag = el.tagName;
    const text = txt(el);
    if (text.length > 60) return { safe: false, reason: "text-too-long" };

    const attrBag = [
      el.getAttribute("data-test") || "",
      el.getAttribute("aria-label") || "",
      el.getAttribute("title") || "",
      el.getAttribute("name") || "",
      typeof el.className === "string" ? el.className : ""
    ].join(" ");

    // Anything that leaves the page or opens a tab is handled by the dedicated
    // directory pipeline, not by generic traversal.
    if (tag === "A") {
      const href = el.getAttribute("href") || "";
      if (/^(mailto:|tel:|sms:)/i.test(href)) return { safe: false, reason: "contact-link" };
      if (el.target === "_blank") return { safe: false, reason: "new-tab" };
      if (href && href !== "#" && !href.startsWith("javascript:")) return { safe: false, reason: "navigates" };
    }
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || tag === "FORM") {
      return { safe: false, reason: "form-control" };
    }

    if (UNSAFE_TEXT.test(text)) return { safe: false, reason: "unsafe-text" };
    if (UNSAFE_ATTR.test(attrBag)) return { safe: false, reason: "unsafe-attr" };

    // Structural expanders are safe by construction, whatever their label says.
    const expanded = el.getAttribute("aria-expanded");
    if (expanded === "false") return { safe: true, reason: "aria-expanded" };
    if (expanded === "true") return { safe: false, reason: "already-expanded" };
    if (el.getAttribute("role") === "tab") {
      if (el.getAttribute("aria-selected") === "true") return { safe: false, reason: "tab-active" };
      return { safe: true, reason: "tab" };
    }
    if (el.matches?.("mat-expansion-panel-header, .mat-expansion-panel-header, .mat-tab-label, .mat-mdc-tab, [role='tab'], summary")) {
      return { safe: true, reason: "panel-header" };
    }

    if (SAFE_TEXT.test(text)) return { safe: true, reason: "safe-text" };

    // A bare chevron/expand icon with no text still reveals content.
    const iconish = /\b(expand_more|expand_less|keyboard_arrow_down|keyboard_arrow_up|chevron|caret|toggle|accordion|collaps|expand)\b/i;
    if (iconish.test(attrBag) || iconish.test(text)) return { safe: true, reason: "expander-icon" };

    return { safe: false, reason: "unclassified" };
  }

  /**
   * Lower is clicked first. Structural expanders reveal data reliably; a plain
   * <span> that merely matched a safe word usually does nothing.
   */
  function revealPriority(el, verdict) {
    const reason = verdict && verdict.reason;
    if (reason === "aria-expanded") return 0;
    if (reason === "tab" || reason === "panel-header") return 1;
    if (reason === "expander-icon") return 2;
    if (el.tagName === "BUTTON" || el.getAttribute("role") === "button") return 3;
    if (el.tagName === "A") return 4;
    return 5;
  }

  function simulateClick(el) {
    if (!el) return false;
    try {
      const rect = el.getBoundingClientRect();
      const clientX = rect.left + rect.width / 2 || 10;
      const clientY = rect.top + rect.height / 2 || 10;
      const base = {
        bubbles: true, cancelable: true, composed: true, view: window, detail: 1,
        clientX, clientY,
        screenX: window.screenX + clientX, screenY: window.screenY + clientY,
        button: 0, buttons: 1, pointerId: 1, isPrimary: true
      };
      el.dispatchEvent(new PointerEvent("pointerdown", base));
      el.dispatchEvent(new MouseEvent("mousedown", base));
      try { el.focus?.(); } catch (e) {}
      const up = { ...base, buttons: 0 };
      el.dispatchEvent(new PointerEvent("pointerup", up));
      el.dispatchEvent(new MouseEvent("mouseup", up));
      if (typeof el.click === "function") el.click();
      else el.dispatchEvent(new MouseEvent("click", up));
      return true;
    } catch (e) {
      try { el.click(); return true; } catch (err) { return false; }
    }
  }

  // ══════════════════════════════════════════════════════════════════
  //  Section detection
  // ══════════════════════════════════════════════════════════════════
  const HEADING_SELECTOR = "h1,h2,h3,h4,h5,h6,legend,caption,[class*='title'],[class*='heading'],[class*='header'],[class*='section-name'],[role='heading']";

  function looksLikeHeading(el) {
    const t = txt(el);
    if (!t || t.length < 2 || t.length > 48) return false;
    if (el.querySelector("input,textarea,select,table")) return false;
    if (/[.!?]$/.test(t)) return false;
    return true;
  }

  /** Walk up from a heading to the block that actually contains its fields. */
  function headingContainer(heading, root) {
    let node = heading.parentElement;
    let hops = 0;
    while (node && node !== root && node !== document.body && hops < 6) {
      const cls = typeof node.className === "string" ? node.className.toLowerCase() : "";
      const isCard =
        node.tagName === "SECTION" || node.tagName === "ARTICLE" || node.tagName === "FIELDSET" ||
        /card|panel|section|container|block|group|widget|module|tile|box/.test(cls);
      // A container qualifies only once it holds more than the heading itself.
      if (isCard && txt(node).length > txt(heading).length + 4) return node;
      node = node.parentElement;
      hops++;
    }
    return heading.parentElement || root;
  }

  /**
   * Partition a root into named sections. Falls back to a single "root" section
   * so harvesting still works on layouts with no headings at all.
   */
  function detectSections(root) {
    const sections = [];
    const seen = new Set();
    let headings = [];
    try {
      headings = Array.from(root.querySelectorAll(HEADING_SELECTOR));
    } catch (e) {
      headings = [];
    }

    for (const h of headings) {
      if (!looksLikeHeading(h)) continue;
      if (!isVisible(h)) continue;
      const container = headingContainer(h, root);
      if (!container || seen.has(container)) continue;
      seen.add(container);
      sections.push({ name: clean(txt(h)), el: container, headingEl: h });
    }

    sections.push({ name: "", el: root, headingEl: null, isRoot: true });
    return sections;
  }

  /** Nearest enclosing section name for an element — used to disambiguate labels. */
  function sectionNameFor(el, sections) {
    let best = "";
    let bestDepth = -1;
    for (const s of sections) {
      if (s.isRoot || !s.el || !s.name) continue;
      if (s.el === el || s.el.contains(el)) {
        let depth = 0;
        let n = el;
        while (n && n !== s.el) { n = n.parentElement; depth++; }
        // Smallest containing section wins.
        if (bestDepth === -1 || depth < bestDepth) { bestDepth = depth; best = s.name; }
      }
    }
    return best;
  }

  // ══════════════════════════════════════════════════════════════════
  //  Generic label / value harvesting
  // ══════════════════════════════════════════════════════════════════

  function isLeafish(el) {
    if (!el || el.nodeType !== 1) return false;
    const kids = Array.from(el.children);
    if (kids.length === 0) return true;
    // Only icon wrappers count as leaves. A <div><span>Load</span><span>Full</span></div>
    // is a *row*, not a label — treating it as one produced "LoadFull" garbage.
    return kids.every((k) =>
      /^(MAT-ICON|I|SVG|IMG)$/i.test(k.tagName) ||
      (/^(SPAN|SMALL|B|STRONG|EM)$/i.test(k.tagName) && txt(k).length === 0)
    );
  }

  function looksLikeLabel(text) {
    const t = clean(text);
    if (!t || t.length > 46) return false;
    if (/:$/.test(t)) return true;
    if (MONEY_RE.test(t)) return false;
    // Long digit runs mean this is a value ("MC#839498", "3768033"), not a label.
    if (/\d{3,}/.test(t)) return false;
    const words = t.split(/\s+/);
    if (words.length > 5) return false;
    // "Rate / mile", "MC Number", "SPOT RATE", "Days to pay"
    return /^[A-Za-z][A-Za-z0-9 /&.'()\-#]*$/.test(t);
  }

  /**
   * A value element holds one value. An element with two or more text-bearing
   * children is a container of further fields and must not be swallowed whole.
   */
  function isValueLike(el) {
    if (!el || el.nodeType !== 1) return false;
    if (/^(TABLE|THEAD|TBODY|TFOOT|TR|UL|OL|DL|FORM|NAV|SECTION|ARTICLE|ASIDE|MAIN|HEADER|FOOTER)$/.test(el.tagName)) {
      return false;
    }
    const kids = Array.from(el.children).filter((k) => txt(k));
    if (kids.length >= 2) return false;
    // A single wrapper child can still hide a whole card underneath it.
    let descendants = 0;
    try { descendants = el.querySelectorAll("*").length; } catch (e) {}
    return descendants <= 6;
  }

  /** Paired value for a label whose class follows the *--label / * convention. */
  function valueFromGridClass(labelEl, scope) {
    const classes = Array.from(labelEl.classList || []);
    const GENERIC = new Set([
      "fields-grid__cell", "fields-grid", "grid__cell", "cell", "label", "value",
      "field-label", "field-value", "field", "data-label", "data-item", "title"
    ]);
    for (const c of classes) {
      if (!/(--label|-label|__label)$/.test(c)) continue;
      const valClass = c.replace(/(--label|-label|__label)$/, "");
      if (!valClass || GENERIC.has(valClass.toLowerCase())) continue;
      try {
        const valEl = scope.querySelector(`.${CSS.escape(valClass)}:not(.${CSS.escape(c)})`);
        if (valEl) return txt(valEl);
      } catch (e) {}
    }
    return null;
  }

  /**
   * Given a label element, find its value using progressively looser strategies.
   * Every strategy rejects a candidate that is itself a label.
   */
  function valueForLabel(labelEl, scope) {
    const labelText = clean(txt(labelEl));

    // 0. "Label: value" inside one node.
    const inlineM = labelText.match(/^(.{1,46}?):\s*(.+)$/);
    if (inlineM && inlineM[2] && !looksLikeLabel(inlineM[2])) {
      return inlineM[2];
    }

    // 1. Class-convention pairing (DAT directory grids).
    const gridVal = valueFromGridClass(labelEl, scope);
    if (gridVal && clean(gridVal) !== labelText) return gridVal;

    // 2. Next element sibling.
    let sib = labelEl.nextElementSibling;
    while (sib) {
      const t = txt(sib);
      if (t) {
        if (!isValueLike(sib)) break; // a card body, not a value
        if (looksLikeLabel(t) && !valueOrNull(t)) break;
        return t;
      }
      sib = sib.nextElementSibling;
    }

    // 3. Trailing text node inside the same parent (label span + bare text).
    const parent = labelEl.parentElement;
    if (parent) {
      let after = labelEl.nextSibling;
      while (after) {
        if (after.nodeType === Node.TEXT_NODE) {
          const t = clean(after.textContent);
          if (t) return t;
        }
        after = after.nextSibling;
      }

      // 4. Two-column row: <div><span>Load</span><span>Full</span></div>
      const kids = Array.from(parent.children);
      if (kids.length === 2 && kids[0] === labelEl && isValueLike(kids[1])) {
        const t = txt(kids[1]);
        if (t) return t;
      }

      // 5. Label wrapped in its own cell — take the next cell of the grandparent.
      if (kids.length === 1 && kids[0] === labelEl) {
        const grand = parent.parentElement;
        if (grand) {
          const idx = Array.from(grand.children).indexOf(parent);
          if (idx > -1 && idx + 1 < grand.children.length) {
            const next = grand.children[idx + 1];
            const t = txt(next);
            if (t && !looksLikeLabel(t) && isValueLike(next)) return t;
          }
        }
      }

      // 6. Stacked label-over-value (DAT directory cards).
      const parentText = clean(parent.textContent || "");
      if (parentText.toLowerCase().startsWith(labelText.toLowerCase())) {
        const rest = parentText.slice(labelText.length).replace(/^[:\s]+/, "");
        if (rest && rest !== labelText) return rest;
      }
    }

    return null;
  }

  /**
   * Harvest every label/value pair reachable inside `root`.
   * Returns [{ label, value, section, source }] with duplicates collapsed.
   */
  function harvestPairs(root, sections) {
    const pairs = [];
    const seen = new Set();

    const push = (label, value, el, source) => {
      const l = clean(label).replace(/[:*]+$/, "").trim();
      const v = valueOrNull(value);
      if (!l || l.length > 46) return;
      const section = el ? sectionNameFor(el, sections) : "";
      const key = `${section.toLowerCase()}::${l.toLowerCase()}::${v === null ? "" : v}`;
      if (seen.has(key)) return;
      seen.add(key);
      pairs.push({ label: l, value: v, section, source });
    };

    // ── Definition lists ──
    try {
      root.querySelectorAll("dl").forEach((dl) => {
        let currentDt = null;
        Array.from(dl.children).forEach((child) => {
          if (child.tagName === "DT") currentDt = txt(child);
          else if (child.tagName === "DD" && currentDt) push(currentDt, txt(child), child, "dl");
        });
      });
    } catch (e) {}

    // ── Tables ──
    // Two-column tables are label/value. Wider tables (DOT Authority Status:
    // Authority × Status × Application pending) are matrices — pairing header
    // cells with each other would invent fields, so each body cell is keyed by
    // "<row label> <column header>" instead.
    try {
      root.querySelectorAll("table").forEach((table) => {
        const rows = Array.from(table.querySelectorAll("tr"));
        if (!rows.length) return;
        const cellsOf = (tr) => Array.from(tr.children).filter((c) => /^(TD|TH)$/.test(c.tagName));

        const headerRow = rows.find((tr) => cellsOf(tr).every((c) => c.tagName === "TH") && cellsOf(tr).length > 1);
        const headers = headerRow ? cellsOf(headerRow).map((c) => txt(c)) : null;

        for (const tr of rows) {
          if (tr === headerRow) continue;
          const cells = cellsOf(tr);
          if (cells.length === 2 && !headers) {
            push(txt(cells[0]), txt(cells[1]), cells[1], "table");
          } else if (headers && cells.length >= 2) {
            const rowLabel = txt(cells[0]);
            for (let i = 1; i < cells.length && i < headers.length; i++) {
              if (!headers[i]) continue;
              push(`${rowLabel} ${headers[i]}`, txt(cells[i]), cells[i], "table-matrix");
            }
          } else if (cells.length === 2) {
            push(txt(cells[0]), txt(cells[1]), cells[1], "table");
          }
        }
      });
    } catch (e) {}

    // Section headings name a block, they are not field labels — pairing them
    // swallowed whole cards ("Company" → "VIEW IN DIRECTORY"). A heading that
    // ends with ':' really is a label styled as one, so it stays eligible.
    const headingEls = new Set();
    try {
      root.querySelectorAll(HEADING_SELECTOR).forEach((h) => {
        if (looksLikeHeading(h) && !/:$/.test(clean(txt(h)))) headingEls.add(h);
      });
    } catch (e) {}

    // ── Generic label elements ──
    let candidates = [];
    try {
      candidates = Array.from(root.querySelectorAll("span,div,label,p,td,th,dt,h4,h5,h6,li,strong,b,small"));
    } catch (e) {}

    for (const el of candidates) {
      if (headingEls.has(el)) continue;
      if (!isLeafish(el)) continue;
      // Header cells describe columns, not the cell beside them. Body cells of a
      // headed table were already paired by the matrix rule above.
      if (el.tagName === "TH") continue;
      if (el.tagName === "TD") {
        let headed = false;
        try { headed = !!el.closest("table")?.querySelector("th"); } catch (e) {}
        if (headed) continue;
      }
      const t = clean(txt(el));
      if (!t || !looksLikeLabel(t)) continue;
      if (!isVisible(el)) continue;
      const value = valueForLabel(el, root);
      if (value == null) continue;
      const v = clean(value);
      if (!v || v.toLowerCase() === t.toLowerCase()) continue;
      if (v.length > 400) continue;
      push(t.replace(/:$/, ""), v, el, "dom");
    }

    // ── Attribute-carried data ──
    try {
      root.querySelectorAll("[data-test],[aria-label],[title]").forEach((el) => {
        if (!isLeafish(el)) return;
        const v = txt(el);
        if (!v) return;
        const aria = el.getAttribute("aria-label");
        const title = el.getAttribute("title");
        if (aria && looksLikeLabel(aria) && clean(aria) !== clean(v)) push(aria, v, el, "aria");
        else if (title && looksLikeLabel(title) && clean(title) !== clean(v)) push(title, v, el, "title");
      });
    } catch (e) {}

    // ── data-* attributes carrying values directly ──
    try {
      root.querySelectorAll("*").forEach((el) => {
        const ds = el.dataset;
        if (!ds) return;
        for (const k of Object.keys(ds)) {
          if (/^(test|testid|cy|qa)$/i.test(k)) continue;
          const v = ds[k];
          if (v && String(v).length < 200 && /[A-Za-z0-9]/.test(v)) push(k, v, el, "data-attr");
        }
      });
    } catch (e) {}

    return pairs;
  }

  /** Links, emails and phone numbers reachable inside `root`. */
  function harvestContacts(root) {
    const out = { emails: [], phones: [], links: [], websites: [] };
    try {
      root.querySelectorAll("a[href]").forEach((a) => {
        const href = a.getAttribute("href") || "";
        const label = clean(txt(a));
        if (/^mailto:/i.test(href)) {
          const e = href.replace(/^mailto:/i, "").split("?")[0].trim();
          if (e && !out.emails.includes(e)) out.emails.push(e);
        } else if (/^tel:/i.test(href)) {
          const p = href.replace(/^tel:/i, "").trim();
          if (p && !out.phones.includes(p)) out.phones.push(p);
        } else if (/^https?:/i.test(href)) {
          const rec = { href, text: label };
          if (!out.links.some((l) => l.href === href)) out.links.push(rec);
          if (!/dat\.com/i.test(href) && !out.websites.includes(href)) out.websites.push(href);
        }
      });
    } catch (e) {}

    const text = clean(root.innerText || root.textContent || "");
    for (const e of allMatches(text, EMAIL_RE)) {
      if (!out.emails.includes(e)) out.emails.push(e);
    }
    for (const p of allMatches(text, PHONE_RE)) {
      const digits = p.replace(/\D/g, "");
      // Reject MC/DOT numbers and money that happen to match the loose phone shape.
      if (digits.length < 10) continue;
      if (!out.phones.some((x) => x.replace(/\D/g, "") === digits)) out.phones.push(p);
    }
    return out;
  }

  // ══════════════════════════════════════════════════════════════════
  //  Section-specific parsers
  // ══════════════════════════════════════════════════════════════════

  /**
   * The market-rate card is positional, not label/value:
   *   SPOT RATE   Montreal Mkt - Rochester X-Mkt
   *   $1,343  ($3.87/mi)          347 mi | 7d average
   *   Range:  $1,072 - $1,572 ($3.09 - $4.53/mi)
   */
  /**
   * Visual lines inside an element, newlines preserved.
   * clean() collapses newlines, which destroys the positional structure the
   * rate and trip cards depend on — so those parsers use this instead.
   * innerText collapses to nothing in a background tab, hence the leaf fallback.
   */
  function elementLines(el) {
    if (!el) return [];
    const fromText = String(el.innerText || "")
      .split(/\n+/)
      .map((l) => l.replace(ICON_WORDS, " ").replace(/[ \t]+/g, " ").trim())
      .filter(Boolean);
    if (fromText.length > 1) return fromText;

    const acc = [];
    try {
      Array.from(el.querySelectorAll("*")).forEach((node) => {
        if (!isLeafish(node)) return;
        const t = clean(txt(node));
        if (t && acc[acc.length - 1] !== t) acc.push(t);
      });
    } catch (e) {}
    return acc.length ? acc : (fromText.length ? fromText : [clean(txt(el))].filter(Boolean));
  }

  /**
   * Find the blocks introduced by a heading matching `re`.
   * Only real headings qualify — a stray <td>Broker</td> must not be mistaken
   * for a "Company" card, which is exactly what happened on directory pages.
   */
  function findHeadedBlocks(root, re) {
    const blocks = [];
    let headings = [];
    try { headings = Array.from(root.querySelectorAll(HEADING_SELECTOR)); } catch (e) { return blocks; }
    for (const el of headings) {
      if (!looksLikeHeading(el)) continue;
      const t = clean(txt(el));
      if (!re.test(t)) continue;
      const container = headingContainer(el, root);
      if (!container || blocks.some((b) => b.el === container)) continue;
      blocks.push({ kind: t.toLowerCase(), el: container, headingEl: el });
    }
    return blocks;
  }

  function parseRateBlocks(root) {
    const out = {};
    const blocks = findHeadedBlocks(root, /^(spot rate|contract rate|market rates?|rate)$/i);

    for (const block of blocks) {
      const lines = elementLines(block.el);
      if (!lines.length) continue;
      const isTitle = (l) => /^(spot rate|contract rate|market rates?|rate)\b/i.test(l);

      if (/^spot rate$/.test(block.kind)) {
        const rangeLine = lines.find((l) => /^range\b/i.test(l));
        if (rangeLine) {
          const m = rangeLine.match(/(\$[\d,]+(?:\.\d+)?)\s*[-–]\s*(\$[\d,]+(?:\.\d+)?)\s*(?:\(\s*(\$[\d.]+)\s*[-–]\s*(\$[\d.]+)\s*\/\s*mi\s*\))?/i);
          if (m) {
            out.rateRangeLow = m[1];
            out.rateRangeHigh = m[2];
            out.rateRange = `${m[1]} - ${m[2]}`;
            if (m[3]) out.rateRangePerMileLow = m[3];
            if (m[4]) out.rateRangePerMileHigh = m[4];
          }
        }

        // The headline rate is the first money line that is not the range.
        const headline = lines.find((l) => l !== rangeLine && !isTitle(l) && MONEY_RE.test(l));
        if (headline) {
          const money = allMatches(headline, MONEY_RE);
          if (money.length) out.spotRate = money[0];
          const perMi = headline.match(/\(\s*(\$[\d.]+)\s*\/\s*mi\s*\)/i);
          if (perMi) out.spotRatePerMile = perMi[1];
        }

        const basisLine = lines.find((l) => /\d[\d,]*\s*mi\s*\|/i.test(l));
        if (basisLine) {
          const m = basisLine.match(/(\d[\d,]*)\s*mi\s*\|\s*(.+)$/i);
          if (m) {
            out.spotRateBasisMiles = m[1];
            out.spotRateBasis = clean(m[2]);
          }
        }

        // The market name is its own line: no money, not the title.
        const mktLine = lines.find((l) =>
          !isTitle(l) && !MONEY_RE.test(l) && l !== basisLine && /\b(mkt|market)\b/i.test(l)
        );
        if (mktLine) out.rateMarket = clean(mktLine);
      }

      if (/^contract rate$/.test(block.kind)) {
        const body = lines.filter((l) => !isTitle(l)).join(" ");
        if (/not available|no data|unavailable/i.test(body)) {
          out.contractRate = null;
          out.contractRateNote = clean(body);
        } else {
          const money = allMatches(body, MONEY_RE);
          if (money.length) out.contractRate = money[0];
          const perMi = body.match(/\(\s*(\$[\d.]+)\s*\/\s*mi\s*\)/i);
          if (perMi) out.contractRatePerMile = perMi[1];
        }
      }
    }
    return out;
  }

  /**
   * The company card is a stack of bare values with no labels at all:
   *   TMX Inc/TMX Logitran Llc
   *   Jack.Boyer@tmxinc.net
   *   MC#839498
   *   Erlanger, KY
   *   Factoring Eligible / ★★★★☆ (10)
   * Classify them by shape rather than by an adjacent label.
   */
  function parseCompanyBlock(root) {
    const out = {};
    const blocks = findHeadedBlocks(root, /^(company|broker|carrier|company details?)$/i);
    if (!blocks.length) return out;
    const container = blocks[0].el;
    // A whole page matched by accident would poison every field; a company card
    // is small by nature.
    if (clean(txt(container)).length > 1500) return out;

    for (const line of elementLines(container)) {
      if (/^(company|broker|carrier)$/i.test(line)) continue;
      if (/view in directory|mark as|book now|expand|see all/i.test(line)) continue;

      const mc = line.match(/\bMC\s*#?\s*(\d{3,})/i);
      if (mc && !out.mcNumber) { out.mcNumber = mc[1]; continue; }

      const dot = line.match(/\b(?:US)?DOT\s*#?\s*:?\s*(\d{3,})/i);
      if (dot && !out.dotNumber) { out.dotNumber = dot[1]; continue; }

      if (EMAIL_RE.test(line)) { EMAIL_RE.lastIndex = 0; continue; } // handled by contact harvest
      EMAIL_RE.lastIndex = 0;

      if (/factoring/i.test(line)) {
        if (!out.factoring) out.factoring = /eligible|enabled|yes/i.test(line) ? "Yes" : clean(line);
        continue;
      }

      const reviews = line.match(/\((\d+)\)\s*$/);
      if (reviews && /[★☆*]/.test(line)) {
        out.rating = clean(line);
        out.reviews = reviews[1];
        continue;
      }

      if (CITY_STATE_RE.test(line) && !out.location) { out.location = line; continue; }

      // First substantial non-classified line is the company name.
      if (!out.name && /[A-Za-z]{2,}/.test(line) && line.length >= 3 && line.length <= 90 && !MONEY_RE.test(line)) {
        out.name = line;
      }
    }
    return out;
  }

  /**
   * The trip column lists stops in visual order, each optionally carrying a
   * deadhead distance in parentheses and a date beneath it.
   */
  function parseTripStops(root) {
    const stops = [];
    // Only parse stops when a genuine Trip/Route/Stops card exists. Scanning the
    // whole surface invented a "stop" out of a company's city on directory pages.
    const blocks = findHeadedBlocks(root, /^(trip|route|stops?|itinerary)$/i);
    if (!blocks.length) return stops;
    const scope = blocks[0].el;

    const rawLines = elementLines(scope);

    for (let i = 0; i < rawLines.length; i++) {
      const line = rawLines[i];
      const m = line.match(/^([A-Za-z][A-Za-z .'\-]{1,40},\s*[A-Z]{2})\s*(?:\((\d+)\))?/);
      if (!m) continue;
      const stop = {
        location: m[1].trim(),
        city: null,
        state: null,
        deadheadMiles: m[2] ? Number(m[2]) : null,
        date: null,
        time: null
      };
      const cs = stop.location.match(CITY_STATE_RE);
      if (cs) { stop.city = cs[1].trim(); stop.state = cs[2]; }

      // Look ahead a couple of lines for the date/time that belongs to this stop.
      for (let j = i + 1; j < Math.min(i + 3, rawLines.length); j++) {
        const nxt = rawLines[j];
        if (/^[A-Za-z][A-Za-z .'\-]{1,40},\s*[A-Z]{2}/.test(nxt)) break;
        const dateM = nxt.match(/\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:,\s*\d{4})?|\d{1,2}\/\d{1,2}(?:\/\d{2,4})?)\b/i);
        if (dateM && !stop.date) stop.date = dateM[1];
        const timeM = nxt.match(/\b(\d{1,2}:\d{2}\s*(?:am|pm)?(?:\s*[-–]\s*\d{1,2}:\d{2}\s*(?:am|pm)?)?)\b/i);
        if (timeM && !stop.time) stop.time = timeM[1];
      }
      if (!stops.some((s) => s.location === stop.location && s.deadheadMiles === stop.deadheadMiles)) {
        stops.push(stop);
      }
    }
    return stops;
  }

  // ══════════════════════════════════════════════════════════════════
  //  Embedded structured data
  // ══════════════════════════════════════════════════════════════════
  function harvestEmbeddedJson(root) {
    const found = [];
    try {
      document.querySelectorAll('script[type="application/ld+json"],script[type="application/json"]').forEach((s) => {
        const raw = (s.textContent || "").trim();
        if (!raw || raw.length > 500000) return;
        try { found.push(JSON.parse(raw)); } catch (e) {}
      });
    } catch (e) {}
    for (const key of ["__INITIAL_STATE__", "__NUXT__", "__NEXT_DATA__", "__APP_STATE__", "datState"]) {
      try {
        const v = window[key];
        if (v && typeof v === "object") found.push(v);
      } catch (e) {}
    }
    return found;
  }

  // ══════════════════════════════════════════════════════════════════
  //  Network payload store
  // ══════════════════════════════════════════════════════════════════
  const MAX_PAYLOADS = 220;
  const netPayloads = [];
  const netIndex = new Map(); // id value -> object that carries it

  const ID_KEY_RE = /^(id|_id|uuid|guid|matchid|postingid|loadid|assetid|referenceid|shipmentid|offerid)$/i;

  function indexObject(obj, depth = 0, nodeBudget = { n: 0 }) {
    if (!obj || typeof obj !== "object" || depth > 8) return;
    if (nodeBudget.n++ > 8000) return;
    if (Array.isArray(obj)) {
      for (const item of obj) indexObject(item, depth + 1, nodeBudget);
      return;
    }
    for (const [k, v] of Object.entries(obj)) {
      if (ID_KEY_RE.test(k) && (typeof v === "string" || typeof v === "number")) {
        const key = String(v);
        if (key.length >= 4 && key.length <= 64 && !netIndex.has(key)) netIndex.set(key, obj);
      }
      if (v && typeof v === "object") indexObject(v, depth + 1, nodeBudget);
    }
  }

  function recordNetPayload(payload) {
    if (!payload || !payload.body) return;
    netPayloads.push(payload);
    if (netPayloads.length > MAX_PAYLOADS) netPayloads.shift();
    try { indexObject(payload.body); } catch (e) {}
    if (netIndex.size > 6000) netIndex.clear();
  }

  /** Best structured record for a load, keyed by any identifier we hold. */
  function findNetRecord(ids) {
    for (const id of ids) {
      if (!id) continue;
      const hit = netIndex.get(String(id));
      if (hit) return hit;
    }
    return null;
  }

  /** Flatten a network record into label/value pairs the normalizer understands. */
  function pairsFromNetRecord(obj, prefix = "", depth = 0, out = []) {
    if (!obj || typeof obj !== "object" || depth > 4) return out;
    if (out.length > 300) return out;
    for (const [k, v] of Object.entries(obj)) {
      if (v == null) continue;
      const label = prefix ? `${prefix}.${k}` : k;
      if (typeof v === "object") {
        if (Array.isArray(v)) {
          if (v.length && typeof v[0] !== "object") {
            out.push({ label, value: v.join(", "), section: "api", source: "network" });
          } else {
            v.slice(0, 6).forEach((item, i) => pairsFromNetRecord(item, `${label}[${i}]`, depth + 1, out));
          }
        } else {
          pairsFromNetRecord(v, label, depth + 1, out);
        }
      } else {
        out.push({ label, value: String(v), section: "api", source: "network" });
      }
    }
    return out;
  }

  window.addEventListener("DAT_NET_CAPTURE", (e) => {
    try { recordNetPayload(e.detail); } catch (err) {}
  });

  // ══════════════════════════════════════════════════════════════════
  //  Normalization — label ➜ schema path
  // ══════════════════════════════════════════════════════════════════
  //
  // Section-scoped rules are consulted before the global map, because the same
  // word means different things in different cards: "Total" under Rate is the
  // line-haul total, "Trip" under Rate is mileage, "Trip" as a heading is the stop list.

  const SECTION_RULES = [
    {
      match: /rate|market|spot|contract|pricing/i,
      map: {
        "total": "rate.rateTotal",
        "rate total": "rate.rateTotal",
        "trip": "rate.totalTrip",
        "rate / mile": "rate.ratePerMile",
        "rate/mile": "rate.ratePerMile",
        "rate per mile": "rate.ratePerMile",
        "per mile": "rate.ratePerMile",
        "range": "rate.rateRange",
        "spot rate": "rate.spotRate",
        "contract rate": "rate.contractRate",
        "total cost": "rate.totalCost",
        "total trip": "rate.totalTrip",
        "cost": "rate.totalCost",
        "amount": "rate.rateTotal"
      }
    },
    {
      match: /office/i,
      map: {
        "company name": "office.name",
        "name": "office.name",
        "address": "office.addressRaw",
        "phone": "office.phone",
        "office phone": "office.phone",
        "fax": "office.fax",
        "office fax": "office.fax",
        "email": "office.email",
        "contact": "office.contact",
        "hours": "office.hours",
        "office hours": "office.hours",
        "company type": "office.companyType",
        "parent account": "office.parentAccount",
        "membership / affiliations": "office.affiliations"
      }
    },
    {
      // On a directory profile the address/phone/fax under this card belong to
      // the insurance carrier, not to the broker's office.
      match: /insurance|dot authority/i,
      map: {
        "address": "company.insuranceAddress",
        "phone": "company.insurancePhone",
        "fax": "company.insuranceFax",
        "contact": "company.insuranceContact",
        "insurance carrier": "company.insuranceCarrier",
        "policy / surety": "company.insurancePolicy",
        "coverage to": "company.insuranceCoverageTo",
        "coverage from": "company.insuranceCoverageFrom",
        "effective date": "company.insuranceEffectiveDate",
        "cancellation date": "company.insuranceCancellationDate"
      }
    },
    {
      match: /contact/i,
      map: {
        "name": "contact.name",
        "contact": "contact.name",
        "phone": "contact.phone",
        "mobile": "contact.mobile",
        "email": "contact.email",
        "fax": "contact.fax",
        "title": "contact.title",
        "role": "contact.role"
      }
    },
    {
      match: /equipment|truck/i,
      map: {
        "load": "details.loadType",
        "truck": "truck.truckType",
        "length": "truck.length",
        "weight": "truck.weight",
        "commodity": "details.commodity",
        "reference id": "details.referenceId"
      }
    },
    {
      match: /credit/i,
      map: {
        "name on record": "company.nameOnRecord",
        "credit score": "company.creditScore",
        "days to pay": "company.daysToPay"
      }
    }
  ];

  const GLOBAL_MAP = {
    // ── Load / details ──
    "load": "details.loadType",
    "load type": "details.loadType",
    "load id": "details.loadId",
    "load number": "details.loadNumber",
    "load status": "details.loadStatus",
    "status": "details.loadStatus",
    "age": "details.loadAge",
    "posted": "details.loadAge",
    "commodity": "details.commodity",
    "commodities": "details.commodity",
    "reference id": "details.referenceId",
    "reference": "details.referenceId",
    "ref id": "details.referenceId",
    "notes": "details.notes",
    "comments": "details.notes",

    // ── Equipment / truck ──
    "truck": "truck.truckType",
    "truck type": "truck.truckType",
    "equipment": "truck.equipmentType",
    "equipment type": "truck.equipmentType",
    "trailer": "truck.trailerType",
    "trailer type": "truck.trailerType",
    "length": "truck.length",
    "weight": "truck.weight",
    "capacity": "truck.capacity",
    "dimensions": "truck.dimensions",
    "special requirements": "truck.specialRequirements",
    "requirements": "truck.specialRequirements",

    // ── Rate ──
    "rate": "rate.rate",
    "rate total": "rate.rateTotal",
    "total rate": "rate.rateTotal",
    "rate / mile": "rate.ratePerMile",
    "rate/mile": "rate.ratePerMile",
    "rate per mile": "rate.ratePerMile",
    "spot rate": "rate.spotRate",
    "contract rate": "rate.contractRate",
    "range": "rate.rateRange",
    "minimum rate": "rate.minimumRate",
    "maximum rate": "rate.maximumRate",
    "total trip": "rate.totalTrip",
    "total cost": "rate.totalCost",
    "fuel": "rate.fuelCost",
    "fuel cost": "rate.fuelCost",
    "fuel surcharge": "rate.fuelSurcharge",
    "line haul": "rate.lineHaul",
    "linehaul": "rate.lineHaul",
    "accessorials": "rate.accessorials",
    "detention": "rate.detention",
    "tolls": "rate.tolls",
    "toll": "rate.tolls",
    "other charges": "rate.otherCharges",

    // ── Route ──
    "origin": "route.origin",
    "destination": "route.destination",
    "pickup": "route.pickupLocation",
    "pickup location": "route.pickupLocation",
    "delivery": "route.deliveryLocation",
    "delivery location": "route.deliveryLocation",
    "pickup date": "details.pickupDate",
    "ship date": "details.pickupDate",
    "available": "details.pickupDate",
    "delivery date": "details.deliveryDate",
    "pickup time": "details.pickupTime",
    "delivery time": "details.deliveryTime",
    "hours": "details.pickupTime",
    "miles": "route.totalMiles",
    "trip miles": "route.totalMiles",
    "total miles": "route.totalMiles",
    "distance": "route.totalMiles",
    "route distance": "route.routeDistance",
    "stops": "route.stopsText",
    "deadhead": "route.deadheadOrigin",
    "deadhead origin": "route.deadheadOrigin",
    "deadhead destination": "route.deadheadDestination",
    "dh-o": "route.deadheadOrigin",
    "dh-d": "route.deadheadDestination",

    // ── Company ──
    "company": "company.name",
    "company name": "company.name",
    "name on record": "company.nameOnRecord",
    "dba name": "company.dbaName",
    "authority name": "company.authorityName",
    "mc": "company.mcNumber",
    "mc number": "company.mcNumber",
    "mc#": "company.mcNumber",
    "docket": "company.docket",
    "mc/mx/ff number": "company.docket",
    "dot": "company.dotNumber",
    "dot number": "company.dotNumber",
    "usdot number": "company.dotNumber",
    "credit score": "company.creditScore",
    "days to pay": "company.daysToPay",
    "factoring": "company.factoring",
    "company type": "company.companyType",
    "entity type": "company.entityType",
    "operating status": "company.operatingStatus",
    "operation type": "company.operationType",
    "parent account": "company.parentAccount",
    "parent company": "company.parentCompany",
    "membership / affiliations": "company.affiliations",
    "affiliations": "company.affiliations",
    "insurance carrier": "company.insuranceCarrier",
    "coverage to": "company.insuranceCoverageTo",
    "coverage from": "company.insuranceCoverageFrom",
    "policy / surety": "company.insurancePolicy",
    "effective date": "company.insuranceEffectiveDate",
    "cancellation date": "company.insuranceCancellationDate",
    "out of interstate services": "company.outOfInterstateServices",
    "special commodities": "company.specialCommodities",
    "rating": "company.rating",
    "reviews": "company.reviews",
    "years in business": "company.yearsInBusiness",

    // ── Contact ──
    "contact": "contact.name",
    "contact name": "contact.name",
    "contact person": "contact.name",
    "first name": "contact.firstName",
    "last name": "contact.lastName",
    "title": "contact.title",
    "contact title": "contact.title",
    "role": "contact.role",
    "phone": "contact.phone",
    "telephone": "contact.phone",
    "business phone": "company.businessPhone",
    "mailing phone": "company.mailingPhone",
    "office phone": "office.phone",
    "mobile": "contact.mobile",
    "cell": "contact.mobile",
    "fax": "contact.fax",
    "business fax": "company.businessFax",
    "office fax": "office.fax",
    "mailing fax": "company.mailingFax",
    "email": "contact.email",
    "website": "contact.website",

    // ── Office / addresses ──
    "address": "office.addressRaw",
    "business address": "office.businessAddress",
    "mailing address": "office.mailingAddress",
    "office name": "office.name",
    "office hours": "office.hours",
    "location": "company.location"
  };

  // Network payloads use camelCase keys; map the important ones explicitly.
  const NET_MAP = {
    "ratetotal": "rate.rateTotal",
    "rate.total": "rate.rateTotal",
    "rate.amount": "rate.rateTotal",
    "rateperMile": "rate.ratePerMile",
    "ratepermile": "rate.ratePerMile",
    "permile": "rate.ratePerMile",
    "totalrate": "rate.rateTotal",
    "ratetotalamount": "rate.rateTotal",
    "spotrate": "rate.spotRate",
    "tripmiles": "route.totalMiles",
    "tripmileage": "route.totalMiles",
    "mileage": "route.totalMiles",
    "loadid": "details.loadId",
    "postingid": "details.loadId",
    "matchid": "details.loadId",
    "referenceid": "details.referenceId",
    "commodity": "details.commodity",
    "equipmenttype": "truck.equipmentType",
    "fullpartial": "details.loadType",
    "shipmentweight": "truck.weight",
    "shipmentlength": "truck.length",
    "creditscore": "company.creditScore",
    "dotnumber": "company.dotNumber",
    "docketnumber": "company.docket",
    "mcnumber": "company.mcNumber",
    "companyname": "company.name",
    "contactemail": "contact.email",
    "contactphone": "contact.phone"
  };

  function resolveField(label, section) {
    const l = normLabel(label);
    if (!l) return null;

    for (const rule of SECTION_RULES) {
      if (section && rule.match.test(section)) {
        if (rule.map[l]) return rule.map[l];
      }
    }
    if (GLOBAL_MAP[l]) return GLOBAL_MAP[l];

    // Network keys arrive dotted / camelCase.
    const flat = l.replace(/[^a-z0-9.]/g, "");
    if (NET_MAP[flat]) return NET_MAP[flat];
    const leaf = flat.split(".").pop();
    if (NET_MAP[leaf]) return NET_MAP[leaf];
    if (GLOBAL_MAP[leaf]) return GLOBAL_MAP[leaf];

    return null;
  }

  function setPath(obj, path, value, provenance, key) {
    const v = valueOrNull(value);
    if (v === null) return false;
    const parts = path.split(".");
    let node = obj;
    for (let i = 0; i < parts.length - 1; i++) {
      if (!node[parts[i]] || typeof node[parts[i]] !== "object") node[parts[i]] = {};
      node = node[parts[i]];
    }
    const leaf = parts[parts.length - 1];
    // First writer wins for equal-quality sources; longer/structured values upgrade.
    const existing = node[leaf];
    if (existing == null || existing === "" || (typeof existing === "string" && existing.length < v.length && provenance === "network")) {
      node[leaf] = v;
      if (key) provenanceRecord(provenance, path, key);
      return true;
    }
    return false;
  }

  let currentProvenance = null;
  function provenanceRecord(source, path) {
    if (!currentProvenance) return;
    if (!currentProvenance[path]) currentProvenance[path] = source;
  }

  function emptySchema() {
    return {
      details: {
        loadId: null, loadNumber: null, loadStatus: null, loadAge: null, loadType: null,
        commodity: null, referenceId: null, notes: null,
        pickupDate: null, deliveryDate: null, pickupTime: null, deliveryTime: null
      },
      route: {
        origin: null, destination: null, pickupLocation: null, deliveryLocation: null,
        stops: [], totalMiles: null, routeDistance: null, routeText: null, stopsText: null,
        deadheadOrigin: null, deadheadDestination: null
      },
      truck: {
        truckType: null, equipmentType: null, trailerType: null,
        length: null, weight: null, capacity: null, dimensions: null, specialRequirements: null
      },
      rate: {
        rate: null, rateTotal: null, ratePerMile: null, totalTrip: null, totalCost: null,
        spotRate: null, spotRatePerMile: null, spotRateBasis: null, spotRateBasisMiles: null,
        rateMarket: null, rateRange: null, rateRangeLow: null, rateRangeHigh: null,
        rateRangePerMileLow: null, rateRangePerMileHigh: null,
        contractRate: null, contractRatePerMile: null, contractRateNote: null,
        minimumRate: null, maximumRate: null,
        fuelCost: null, fuelSurcharge: null, lineHaul: null,
        accessorials: null, detention: null, tolls: null, otherCharges: null
      },
      company: {
        name: null, nameOnRecord: null, dbaName: null, authorityName: null,
        mcNumber: null, docket: null, dotNumber: null, creditScore: null, daysToPay: null,
        factoring: null, companyType: null, entityType: null,
        operatingStatus: null, operationType: null,
        parentAccount: null, parentCompany: null, affiliations: null,
        insuranceCarrier: null, insuranceCoverageTo: null, insuranceCoverageFrom: null,
        insurancePolicy: null, insuranceEffectiveDate: null, insuranceCancellationDate: null,
        insuranceAddress: null, insurancePhone: null, insuranceFax: null, insuranceContact: null,
        businessPhone: null, businessFax: null, mailingPhone: null, mailingFax: null,
        location: null, rating: null, reviews: null, yearsInBusiness: null,
        outOfInterstateServices: null, specialCommodities: null
      },
      contact: {
        name: null, firstName: null, lastName: null, title: null, role: null,
        phone: null, mobile: null, fax: null, email: null, website: null,
        emails: [], phones: []
      },
      office: {
        name: null, addressRaw: null, businessAddress: null, mailingAddress: null,
        address: { line1: null, line2: null, city: null, state: null, zip: null, country: null },
        phone: null, fax: null, email: null, contact: null, hours: null,
        companyType: null, parentAccount: null, affiliations: null
      },
      additionalData: {}
    };
  }

  /**
   * Fold harvested pairs + parsed blocks into the normalized schema.
   * Everything unmapped lands in additionalData rather than being dropped.
   */
  function normalize(input) {
    const { pairs = [], contacts = null, rateBlocks = null, stops = null, companyBlock = null, netPairs = [] } = input;
    const schema = emptySchema();
    const provenance = {};
    currentProvenance = provenance;

    const applyPairs = (list, source) => {
      for (const p of list) {
        if (!p || p.value == null) continue;
        const path = resolveField(p.label, p.section);
        if (path) {
          setPath(schema, path, p.value, source);
        } else {
          const key = camelKey(p.section ? `${p.section} ${p.label}` : p.label);
          if (key && !(key in schema.additionalData)) {
            const v = valueOrNull(p.value);
            if (v !== null) schema.additionalData[key] = v;
          }
        }
      }
    };

    // DOM first (it is what Boss actually sees), network second as an upgrade.
    applyPairs(pairs, "dom");
    applyPairs(netPairs, "network");

    // The rate card is read positionally, which beats any label-adjacency guess
    // (a "SPOT RATE" heading sits next to the market name, not the amount).
    if (rateBlocks) {
      for (const [k, v] of Object.entries(rateBlocks)) {
        if (v == null) continue;
        const parsed = valueOrNull(v);
        if (parsed === null) continue;
        schema.rate[k] = parsed;
        provenanceRecord("dom-rate", `rate.${k}`);
      }
      if (rateBlocks.contractRateNote && rateBlocks.contractRate == null) {
        schema.rate.contractRate = null;
      }
    }

    // The company card carries bare values with no labels; fill only the gaps,
    // because a labelled grid elsewhere in the drawer is more trustworthy.
    if (companyBlock) {
      for (const [k, v] of Object.entries(companyBlock)) {
        const parsed = valueOrNull(v);
        if (parsed === null) continue;
        if (schema.company[k] == null) {
          schema.company[k] = parsed;
          provenanceRecord("dom-company", `company.${k}`);
        }
      }
    }

    if (stops && stops.length) {
      schema.route.stops = stops;
      if (!schema.route.origin && stops[0]) schema.route.origin = stops[0].location;
      if (!schema.route.destination && stops.length > 1) schema.route.destination = stops[stops.length - 1].location;
      if (schema.route.deadheadOrigin == null && stops[0] && stops[0].deadheadMiles != null) {
        schema.route.deadheadOrigin = String(stops[0].deadheadMiles);
      }
      if (schema.route.deadheadDestination == null && stops.length > 1) {
        const last = stops[stops.length - 1];
        if (last.deadheadMiles != null) schema.route.deadheadDestination = String(last.deadheadMiles);
      }
      if (!schema.details.pickupDate && stops[0] && stops[0].date) schema.details.pickupDate = stops[0].date;
      if (!schema.details.deliveryDate && stops.length > 1) {
        const last = stops[stops.length - 1];
        if (last.date) schema.details.deliveryDate = last.date;
      }
      schema.route.routeText = stops.map((s) => s.location).join(" → ");
    }

    if (contacts) {
      schema.contact.emails = contacts.emails.slice(0, 10);
      schema.contact.phones = contacts.phones.slice(0, 10);
      if (!schema.contact.email && contacts.emails.length) schema.contact.email = contacts.emails[0];
      if (!schema.contact.phone && contacts.phones.length) schema.contact.phone = contacts.phones[0];
      if (!schema.contact.website && contacts.websites.length) schema.contact.website = contacts.websites[0];
    }

    // Cross-fill the identifiers that appear in more than one shape.
    if (!schema.company.name) {
      schema.company.name = schema.office.name || schema.company.nameOnRecord || schema.company.dbaName || null;
    }
    if (!schema.company.mcNumber && schema.company.docket) {
      const m = String(schema.company.docket).match(/(\d{4,})/);
      if (m) schema.company.mcNumber = m[1];
    }
    if (!schema.company.docket && schema.company.mcNumber) {
      schema.company.docket = `MC${String(schema.company.mcNumber).replace(/\D/g, "")}`;
    }
    if (!schema.rate.totalTrip && schema.route.totalMiles) schema.rate.totalTrip = schema.route.totalMiles;
    if (!schema.route.totalMiles && schema.rate.totalTrip) schema.route.totalMiles = schema.rate.totalTrip;

    const addrSource = schema.office.addressRaw || schema.office.businessAddress;
    if (addrSource) {
      const parsed = parseAddress(addrSource);
      if (parsed) {
        schema.office.address = {
          line1: parsed.line1, line2: parsed.line2, city: parsed.city,
          state: parsed.state, zip: parsed.zip, country: parsed.country
        };
      }
    }

    // Drop additionalData entries that merely restate a value already mapped
    // into the schema — keeps the "unknown fields" bucket genuinely unknown.
    const mappedValues = new Set();
    const collectValues = (obj, depth = 0) => {
      if (!obj || typeof obj !== "object" || depth > 3) return;
      for (const [k, v] of Object.entries(obj)) {
        if (k === "additionalData" || k.startsWith("_")) continue;
        if (v == null) continue;
        if (typeof v === "object") collectValues(v, depth + 1);
        else mappedValues.add(String(v).toLowerCase());
      }
    };
    collectValues(schema);
    for (const [k, v] of Object.entries(schema.additionalData)) {
      if (mappedValues.has(String(v).toLowerCase())) delete schema.additionalData[k];
    }

    currentProvenance = null;
    schema._provenance = provenance;
    return schema;
  }

  // ══════════════════════════════════════════════════════════════════
  //  Recursive traversal of a detail surface
  // ══════════════════════════════════════════════════════════════════

  /**
   * Explore `root` fully: harvest what is visible, then click each safe
   * revealer and harvest again, recursing into whatever appeared.
   */
  async function exploreSurface(root, ctx) {
    const state = ctx.state;
    const collected = { pairs: [], sectionsVisited: [], sectionsFailed: [], linksVisited: [], warnings: [] };

    const harvestNow = (label) => {
      try {
        const sections = detectSections(root);
        const pairs = harvestPairs(root, sections);
        let added = 0;
        for (const p of pairs) {
          const key = `${p.section.toLowerCase()}::${p.label.toLowerCase()}::${p.value ?? ""}`;
          if (state.pairKeys.has(key)) continue;
          state.pairKeys.add(key);
          collected.pairs.push(p);
          added++;
        }
        for (const s of sections) {
          if (s.name && !collected.sectionsVisited.includes(s.name)) collected.sectionsVisited.push(s.name);
        }
        if (label && added > 0 && !collected.sectionsVisited.includes(label)) {
          collected.sectionsVisited.push(label);
        }
        return added;
      } catch (e) {
        collected.warnings.push(`harvest failed: ${e.message}`);
        return 0;
      }
    };

    harvestNow(null);

    // ── Recursive expansion ──
    const maxDepth = ctx.maxDepth ?? 3;
    const maxClicks = ctx.maxClicks ?? 26;

    async function expand(depth) {
      if (depth > maxDepth) return;
      if (state.clicks >= maxClicks) return;
      if (ctx.isCancelled && ctx.isCancelled()) return;

      // Only elements that behave like controls. Clicking every <span> whose
      // text merely contained a safe word cost ~25 inert clicks per load and
      // revealed nothing; Angular's real controls are either semantic or
      // carry cursor:pointer.
      let candidates = [];
      try {
        const structural = Array.from(root.querySelectorAll(
          "button,[role='tab'],[role='button'],[aria-expanded],[tabindex]," +
          "mat-expansion-panel-header,.mat-expansion-panel-header,.mat-tab-label,.mat-mdc-tab,summary," +
          "[class*='expand'],[class*='toggle'],[class*='accordion'],[class*='chevron'],[class*='collaps'],a"
        ));
        const pointerish = Array.from(root.querySelectorAll("div,span,mat-icon,li,p"))
          .filter((el) => {
            const t = txt(el);
            if (!t || t.length > 40) return false;
            if (!SAFE_TEXT.test(t)) return false;
            try { return window.getComputedStyle(el).cursor === "pointer"; } catch (e) { return false; }
          });
        candidates = structural.concat(pointerish);
      } catch (e) {
        return;
      }

      const round = [];
      for (const el of candidates) {
        if (round.length >= 12) break;
        const sig = elementSignature(el);
        if (state.visitedElements.has(sig)) continue;
        if (!isVisible(el) && !document.hidden) continue;
        const verdict = classifyInteractive(el);
        if (!verdict.safe) {
          if (verdict.reason !== "unclassified" && verdict.reason !== "text-too-long") {
            state.visitedElements.add(sig);
          }
          continue;
        }
        // Prefer the outermost clickable wrapper so Angular gets the event it expects.
        const wrapper = el.closest("button,[role='tab'],[role='button'],mat-expansion-panel-header,.mat-expansion-panel-header,.mat-tab-label,.mat-mdc-tab,summary") || el;
        const wsig = elementSignature(wrapper);
        if (state.visitedElements.has(wsig)) continue;
        state.visitedElements.add(sig);
        state.visitedElements.add(wsig);
        round.push({ el: wrapper, label: clean(txt(wrapper)) || verdict.reason, priority: revealPriority(wrapper, verdict) });
      }

      // Real expanders first: they are the ones that actually reveal data, and
      // clicking them early makes the barren-streak signal meaningful.
      round.sort((a, b) => a.priority - b.priority);

      for (const item of round) {
        if (state.clicks >= maxClicks) break;
        if (ctx.isCancelled && ctx.isCancelled()) break;
        // Once several reveals in a row yield nothing new, the surface is
        // exhausted — keep clicking and every load pays the wait for no data.
        if (state.barrenStreak >= (ctx.barrenLimit ?? 4)) {
          collected.warnings.push(`traversal stopped early: ${state.barrenStreak} reveals in a row added no fields`);
          return;
        }
        if (!document.contains(item.el)) continue;
        try {
          state.clicks++;
          simulateClick(item.el);
          const settle = await waitForStable(root, {
            quietMs: 220,
            timeoutMs: ctx.sectionTimeoutMs ?? 2500,
            minMs: ctx.revealMinMs ?? 380
          });
          const added = harvestNow(item.label);
          if (added > 0) state.barrenStreak = 0;
          // A click that changed nothing was an inert control, not evidence that
          // the surface is exhausted — it must not count toward the streak.
          else if (settle && settle.mutated) state.barrenStreak++;
          collected.linksVisited.push({ label: item.label, newFields: added, inert: !(settle && settle.mutated) });
        } catch (e) {
          state.barrenStreak++;
          collected.sectionsFailed.push(item.label);
          collected.warnings.push(`click "${item.label}" failed: ${e.message}`);
        }
      }

      if (round.length) await expand(depth + 1);
    }

    if (ctx.traverse !== false) {
      await expand(1);
      // Final sweep: the last panel opened has had no harvest after it yet, and
      // slow renders may have landed after their own wait returned.
      await waitForStable(root, { quietMs: 200, timeoutMs: 1200, minMs: 350 });
      harvestNow(null);
    }

    // ── Positional parsers, run after everything is revealed ──
    let rateBlocks = null;
    let stops = null;
    let contacts = null;
    let companyBlock = null;
    try { rateBlocks = parseRateBlocks(root); } catch (e) { collected.warnings.push(`rate parse: ${e.message}`); }
    try { stops = parseTripStops(root); } catch (e) { collected.warnings.push(`stops parse: ${e.message}`); }
    try { contacts = harvestContacts(root); } catch (e) { collected.warnings.push(`contacts parse: ${e.message}`); }
    try { companyBlock = parseCompanyBlock(root); } catch (e) { collected.warnings.push(`company parse: ${e.message}`); }

    let text = "";
    try {
      text = clean(root.innerText || root.textContent || "").slice(0, 20000);
    } catch (e) {}

    return { ...collected, rateBlocks, stops, contacts, companyBlock, text };
  }

  /**
   * Public entry: deep-extract one open detail surface (drawer, modal, page).
   * Never throws — failures come back as warnings on the result.
   */
  async function extractSurface(root, options = {}) {
    const ctx = {
      maxDepth: options.maxDepth ?? 3,
      maxClicks: options.maxClicks ?? 26,
      sectionTimeoutMs: options.sectionTimeoutMs ?? 2500,
      traverse: options.traverse !== false,
      barrenLimit: options.barrenLimit ?? 4,
      revealMinMs: options.revealMinMs ?? 380,
      isCancelled: options.isCancelled,
      state: {
        visitedElements: new Set(),
        pairKeys: new Set(),
        clicks: 0,
        barrenStreak: 0
      }
    };

    const started = Date.now();
    let surface;
    try {
      surface = await exploreSurface(root, ctx);
    } catch (e) {
      return {
        schema: emptySchema(),
        raw: { pairs: [], text: "" },
        meta: {
          status: "failed",
          sectionsVisited: [], sectionsFailed: [], linksVisited: [],
          fieldsExtracted: 0, clicks: 0, durationMs: Date.now() - started,
          warnings: [], errors: [{ stage: "surfaceExploration", message: e.message }]
        }
      };
    }

    const ids = options.ids || [];
    let netPairs = [];
    let netRecord = null;
    if (ids.length) {
      netRecord = findNetRecord(ids);
      if (netRecord) netPairs = pairsFromNetRecord(netRecord);
    }

    const schema = normalize({
      pairs: surface.pairs,
      contacts: surface.contacts,
      rateBlocks: surface.rateBlocks,
      stops: surface.stops,
      companyBlock: surface.companyBlock,
      netPairs
    });

    const embedded = options.includeEmbeddedJson ? harvestEmbeddedJson(root) : [];

    return {
      schema,
      raw: {
        pairs: surface.pairs,
        text: surface.text,
        netRecord: netRecord || null,
        embedded
      },
      meta: {
        status: "complete",
        sectionsVisited: surface.sectionsVisited,
        sectionsFailed: surface.sectionsFailed,
        linksVisited: surface.linksVisited,
        fieldsExtracted: countFields(schema),
        clicks: ctx.state.clicks,
        usedNetwork: !!netRecord,
        durationMs: Date.now() - started,
        warnings: surface.warnings,
        errors: []
      }
    };
  }

  function countFields(schema) {
    let n = 0;
    const walk = (obj, depth = 0) => {
      if (!obj || typeof obj !== "object" || depth > 4) return;
      for (const [k, v] of Object.entries(obj)) {
        if (k.startsWith("_")) continue;
        if (v == null) continue;
        if (Array.isArray(v)) { if (v.length) n++; }
        else if (typeof v === "object") walk(v, depth + 1);
        else if (String(v).trim() !== "") n++;
      }
    };
    walk(schema);
    return n;
  }

  // ══════════════════════════════════════════════════════════════════
  //  Merging into the load record
  // ══════════════════════════════════════════════════════════════════

  function deepMergeInto(target, source) {
    let written = 0;
    for (const [k, v] of Object.entries(source || {})) {
      if (k.startsWith("_")) continue;
      if (v == null) continue;
      if (Array.isArray(v)) {
        if (!v.length) continue;
        if (!Array.isArray(target[k]) || target[k].length < v.length) { target[k] = v; written++; }
        continue;
      }
      if (typeof v === "object") {
        if (!target[k] || typeof target[k] !== "object" || Array.isArray(target[k])) target[k] = {};
        written += deepMergeInto(target[k], v);
        continue;
      }
      const str = valueOrNull(v);
      if (str === null) continue;
      // Rule 15: a real value is never replaced by an empty one.
      if (target[k] == null || String(target[k]).trim() === "" || isBlankish(target[k])) {
        target[k] = str;
        written++;
      }
    }
    return written;
  }

  /** Stable identifiers for a load, most authoritative first. */
  function loadIdentifiers(load, deep) {
    const ids = [];
    const add = (v) => {
      const s = valueOrNull(v);
      if (s && !ids.includes(s)) ids.push(s);
    };
    add(load.postingId);
    if (deep) {
      add(deep.details?.loadId);
      add(deep.details?.loadNumber);
      add(deep.details?.referenceId);
    }
    add(load._captureKey);
    return ids;
  }

  /**
   * Attach a surface result to a load record.
   * Existing top-level fields keep working; nested detail lives under load.deep.
   */
  function applySurfaceToLoad(load, result, stage) {
    if (!load) return load;
    if (!load.deep) load.deep = emptySchema();
    if (!load.extraction) {
      load.extraction = {
        status: "pending",
        sectionsVisited: [],
        sectionsFailed: [],
        linksVisited: [],
        fieldsExtracted: 0,
        stages: [],
        retries: 0,
        warnings: [],
        errors: []
      };
    }

    if (!result) {
      load.extraction.errors.push({ stage: stage || "unknown", message: "no result" });
      load.extraction.status = load.extraction.fieldsExtracted > 0 ? "partial" : "failed";
      return load;
    }

    const written = deepMergeInto(load.deep, result.schema);

    // additionalData merges by key rather than being replaced wholesale.
    if (result.schema.additionalData) {
      load.deep.additionalData = load.deep.additionalData || {};
      for (const [k, v] of Object.entries(result.schema.additionalData)) {
        if (!(k in load.deep.additionalData)) load.deep.additionalData[k] = v;
      }
    }

    const m = result.meta || {};
    for (const s of m.sectionsVisited || []) {
      if (!load.extraction.sectionsVisited.includes(s)) load.extraction.sectionsVisited.push(s);
    }
    for (const s of m.sectionsFailed || []) {
      if (!load.extraction.sectionsFailed.includes(s)) load.extraction.sectionsFailed.push(s);
    }
    for (const l of m.linksVisited || []) load.extraction.linksVisited.push(l);
    for (const w of m.warnings || []) load.extraction.warnings.push(w);
    for (const e of m.errors || []) load.extraction.errors.push(e);

    load.extraction.stages.push({
      stage: stage || "detail",
      fields: written,
      clicks: m.clicks || 0,
      usedNetwork: !!m.usedNetwork,
      durationMs: m.durationMs || 0
    });
    load.extraction.fieldsExtracted = countFields(load.deep);

    // Keep the flat legacy fields populated so old exports do not regress.
    backfillLegacyFields(load);
    return load;
  }

  const LEGACY_BACKFILL = [
    // Across 60k real captures the row-level rate cell was empty on ~45% of
    // loads and rate/mile on ~54%; the detail Rate card carries both.
    ["rate", "rate.rateTotal"],
    ["ratePerMile", "rate.ratePerMile"],
    ["tripMiles", "route.totalMiles"],
    ["commodity", "details.commodity"],
    ["truckType", "truck.truckType"],
    ["length", "truck.length"],
    ["weight", "truck.weight"],
    ["loadType", "details.loadType"],
    ["referenceId", "details.referenceId"],
    ["pickupDate", "details.pickupDate"],
    ["pickupTime", "details.pickupTime"],
    ["deliveryTime", "details.deliveryTime"],
    ["phone", "contact.phone"],
    ["email", "contact.email"],
    ["companyLocation", "company.location"],
    ["equipmentType", "truck.equipmentType"]
  ];

  function getPath(obj, path) {
    let node = obj;
    for (const part of path.split(".")) {
      if (!node || typeof node !== "object") return null;
      node = node[part];
    }
    return node ?? null;
  }

  /** Fill blank legacy columns from deep data — never overwrite a real value. */
  function backfillLegacyFields(load) {
    if (!load.deep) return;
    for (const [flat, path] of LEGACY_BACKFILL) {
      const v = valueOrNull(getPath(load.deep, path));
      if (v !== null && isBlankish(load[flat])) load[flat] = v;
    }
    // Company/DOT identifiers feed the existing directory columns when empty.
    const dot = valueOrNull(getPath(load.deep, "company.dotNumber"));
    if (dot && isBlankish(load.dir_dot_number)) { load.dir_dot_number = dot; load.dot_number = dot; }
    const docket = valueOrNull(getPath(load.deep, "company.docket"));
    if (docket && isBlankish(load.dir_docket)) { load.dir_docket = docket; load.docket = docket; }
    const credit = valueOrNull(getPath(load.deep, "company.creditScore"));
    if (credit && isBlankish(load.dir_credit_score)) { load.dir_credit_score = credit; load.credit_score = credit; }
  }

  /** Roll the per-stage record up into one status. */
  function finalizeExtraction(load, expectedStages = []) {
    if (!load.extraction) {
      load.extraction = {
        status: "failed", sectionsVisited: [], sectionsFailed: [], linksVisited: [],
        fieldsExtracted: 0, stages: [], retries: 0, warnings: [],
        errors: [{ stage: "detailExtraction", message: "extraction never ran" }]
      };
      return load;
    }
    const ex = load.extraction;
    const ranStages = new Set(ex.stages.map((s) => s.stage));
    const missing = expectedStages.filter((s) => !ranStages.has(s));

    if (ex.fieldsExtracted === 0) ex.status = "failed";
    else if (ex.errors.length || ex.sectionsFailed.length || missing.length) ex.status = "partial";
    else ex.status = "complete";

    if (missing.length) ex.missingStages = missing;
    return load;
  }

  // ══════════════════════════════════════════════════════════════════
  //  Flattening for CSV / XLSX
  // ══════════════════════════════════════════════════════════════════
  //
  // Ordered so a spreadsheet reads left-to-right the way the drawer reads
  // top-to-bottom. Header text stays stable across versions.
  const DEEP_COLUMNS = [
    ["Load ID", "details.loadId"],
    ["Load Number", "details.loadNumber"],
    ["Load Status", "details.loadStatus"],
    ["Detail Load Type", "details.loadType"],
    ["Commodity", "details.commodity"],
    ["Detail Reference ID", "details.referenceId"],
    ["Detail Pickup Date", "details.pickupDate"],
    ["Detail Delivery Date", "details.deliveryDate"],
    ["Detail Pickup Time", "details.pickupTime"],
    ["Detail Delivery Time", "details.deliveryTime"],
    ["Notes", "details.notes"],

    ["Route Origin", "route.origin"],
    ["Route Destination", "route.destination"],
    ["Route Text", "route.routeText"],
    ["Route Stops", "route.stopsFlat"],
    ["Route Stop Count", "route.stopCount"],
    ["Route Total Miles", "route.totalMiles"],
    ["Route Distance", "route.routeDistance"],
    ["Route DH Origin", "route.deadheadOrigin"],
    ["Route DH Destination", "route.deadheadDestination"],

    ["Truck", "truck.truckType"],
    ["Detail Equipment", "truck.equipmentType"],
    ["Trailer", "truck.trailerType"],
    ["Detail Length", "truck.length"],
    ["Detail Weight", "truck.weight"],
    ["Capacity", "truck.capacity"],
    ["Dimensions", "truck.dimensions"],
    ["Special Requirements", "truck.specialRequirements"],

    ["Rate Total", "rate.rateTotal"],
    ["Total Trip", "rate.totalTrip"],
    ["Detail Rate/Mile", "rate.ratePerMile"],
    ["Total Cost", "rate.totalCost"],
    ["Spot Rate", "rate.spotRate"],
    ["Spot Rate/Mile", "rate.spotRatePerMile"],
    ["Spot Rate Basis", "rate.spotRateBasis"],
    ["Rate Market", "rate.rateMarket"],
    ["Rate Range", "rate.rateRange"],
    ["Rate Range Low", "rate.rateRangeLow"],
    ["Rate Range High", "rate.rateRangeHigh"],
    ["Rate Range/Mile Low", "rate.rateRangePerMileLow"],
    ["Rate Range/Mile High", "rate.rateRangePerMileHigh"],
    ["Contract Rate", "rate.contractRate"],
    ["Contract Rate Note", "rate.contractRateNote"],
    ["Line Haul", "rate.lineHaul"],
    ["Fuel Cost", "rate.fuelCost"],
    ["Accessorials", "rate.accessorials"],
    ["Detention", "rate.detention"],
    ["Tolls", "rate.tolls"],
    ["Other Charges", "rate.otherCharges"],

    ["Detail Company", "company.name"],
    ["Company Name On Record", "company.nameOnRecord"],
    ["DBA Name", "company.dbaName"],
    ["Authority Name", "company.authorityName"],
    ["MC Number", "company.mcNumber"],
    ["Detail Docket", "company.docket"],
    ["Detail DOT Number", "company.dotNumber"],
    ["Detail Credit Score", "company.creditScore"],
    ["Days To Pay", "company.daysToPay"],
    ["Company Type", "company.companyType"],
    ["Entity Type", "company.entityType"],
    ["Operating Status", "company.operatingStatus"],
    ["Operation Type", "company.operationType"],
    ["Parent Account", "company.parentAccount"],
    ["Affiliations", "company.affiliations"],
    ["Insurance Carrier", "company.insuranceCarrier"],
    ["Insurance Coverage To", "company.insuranceCoverageTo"],
    ["Insurance Coverage From", "company.insuranceCoverageFrom"],
    ["Insurance Policy", "company.insurancePolicy"],
    ["Insurance Effective Date", "company.insuranceEffectiveDate"],
    ["Insurance Cancellation Date", "company.insuranceCancellationDate"],
    ["Insurance Address", "company.insuranceAddress"],
    ["Insurance Phone", "company.insurancePhone"],
    ["Insurance Fax", "company.insuranceFax"],
    ["Business Phone", "company.businessPhone"],
    ["Business Fax", "company.businessFax"],
    ["Company Location", "company.location"],
    ["Company Rating", "company.rating"],

    ["Contact Name", "contact.name"],
    ["Contact Title", "contact.title"],
    ["Contact Phone", "contact.phone"],
    ["Contact Mobile", "contact.mobile"],
    ["Contact Fax", "contact.fax"],
    ["Contact Email", "contact.email"],
    ["Contact Website", "contact.website"],
    ["All Emails", "contact.emailsFlat"],
    ["All Phones", "contact.phonesFlat"],

    ["Office Name", "office.name"],
    ["Office Address", "office.addressRaw"],
    ["Office Address Line1", "office.address.line1"],
    ["Office Address Line2", "office.address.line2"],
    ["Office City", "office.address.city"],
    ["Office State", "office.address.state"],
    ["Office ZIP", "office.address.zip"],
    ["Office Country", "office.address.country"],
    ["Office Phone", "office.phone"],
    ["Office Fax", "office.fax"],
    ["Office Email", "office.email"],
    ["Office Hours", "office.hours"],
    ["Business Address", "office.businessAddress"],
    ["Mailing Address", "office.mailingAddress"],

    ["Extraction Status", "_ex.status"],
    ["Extraction Fields", "_ex.fieldsExtracted"],
    ["Sections Visited", "_ex.sectionsVisitedFlat"],
    ["Sections Failed", "_ex.sectionsFailedFlat"],
    ["Extraction Retries", "_ex.retries"],
    ["Extraction Warnings", "_ex.warningsFlat"],
    ["Additional Data", "_ex.additionalDataFlat"]
  ];

  /** Resolve one flattened column value for a load. */
  function deepValue(load, path) {
    const deep = load.deep;
    const ex = load.extraction;

    if (path.startsWith("_ex.")) {
      if (!ex) return "";
      const k = path.slice(4);
      if (k === "sectionsVisitedFlat") return (ex.sectionsVisited || []).join(" | ");
      if (k === "sectionsFailedFlat") return (ex.sectionsFailed || []).join(" | ");
      if (k === "warningsFlat") return (ex.warnings || []).slice(0, 5).join(" | ");
      if (k === "additionalDataFlat") {
        const ad = deep && deep.additionalData ? deep.additionalData : {};
        return Object.entries(ad).map(([a, b]) => `${a}=${b}`).join(" | ");
      }
      const v = ex[k];
      if (v == null) return "";
      return Array.isArray(v) ? v.join(" | ") : String(v);
    }

    if (!deep) return "";

    if (path === "route.stopsFlat") {
      const stops = deep.route?.stops || [];
      return stops.map((s) => {
        const dh = s.deadheadMiles != null ? ` (${s.deadheadMiles})` : "";
        const d = s.date ? ` ${s.date}` : "";
        return `${s.location}${dh}${d}`.trim();
      }).join(" → ");
    }
    if (path === "route.stopCount") {
      const stops = deep.route?.stops || [];
      return stops.length ? String(stops.length) : "";
    }
    if (path === "contact.emailsFlat") return (deep.contact?.emails || []).join("; ");
    if (path === "contact.phonesFlat") return (deep.contact?.phones || []).join("; ");

    const v = getPath(deep, path);
    if (v == null) return "";
    if (Array.isArray(v)) return v.join("; ");
    if (typeof v === "object") return JSON.stringify(v);
    return String(v);
  }

  /** The nested export shape from section 22 of the brief. */
  function toExportRecord(load) {
    return {
      load: {
        id: load.postingId || load._captureKey || null,
        summary: {
          listIndex: load.listIndex ?? null,
          timestamp: load.timestamp ?? null,
          age: load.age ?? null,
          rate: load.rate ?? null,
          ratePerMile: load.ratePerMile ?? null,
          tripMiles: load.tripMiles ?? null,
          origin: load.origin ?? null,
          destination: load.destination ?? null,
          deadheadOrigin: load.deadheadOrigin ?? null,
          deadheadDestination: load.deadheadDest ?? null,
          equipmentType: load.equipmentType ?? null,
          weight: load.weight ?? null,
          length: load.length ?? null,
          loadType: load.loadType ?? null,
          company: load.company ?? null,
          factoring: load.factoring ?? null,
          rowStatus: load.rowStatus ?? null,
          captureKey: load._captureKey ?? null,
          apOrigin: load._apOrigin ?? null,
          apDest: load._apDest ?? null,
          apEq: load._apEq ?? null,
          apLt: load._apLt ?? null,
          docket: load.dir_docket ?? null,
          dotNumber: load.dir_dot_number ?? null,
          creditScore: load.dir_credit_score ?? null
        },
        details: load.deep?.details ?? null,
        route: load.deep?.route ?? null,
        truck: load.deep?.truck ?? null,
        company: load.deep?.company ?? null,
        contact: load.deep?.contact ?? null,
        office: load.deep?.office ?? null,
        rate: load.deep?.rate ?? null,
        additionalData: load.deep?.additionalData ?? {}
      },
      extraction: load.extraction ?? null
    };
  }

  // ══════════════════════════════════════════════════════════════════
  //  Public surface
  // ══════════════════════════════════════════════════════════════════
  window.__DAT_DEEP__ = {
    version: "3.0.0",

    // extraction
    extractSurface,
    normalize,
    emptySchema,

    // merge / lifecycle
    applySurfaceToLoad,
    finalizeExtraction,
    backfillLegacyFields,
    loadIdentifiers,
    countFields,

    // export
    DEEP_COLUMNS,
    deepValue,
    toExportRecord,

    // primitives reused by content.js
    sleep,
    waitForStable,
    waitFor,
    simulateClick,
    classifyInteractive,
    isVisible,
    clean,
    valueOrNull,
    isBlankish,
    parseAddress,
    getPath,

    // network layer
    recordNetPayload,
    findNetRecord,
    netStats: () => ({ payloads: netPayloads.length, indexed: netIndex.size })
  };
})();
