/* Tidy the Responsive section after the rebuild:
   drop orphan labels left over from the original 3-screen build, verify the
   full set, hide the optional empty slots, and move the section clear of
   Desktop (which is now 42 frames tall). */
(async () => {
var report = 'start';
try {
  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);
  var desk = null, resp = null;
  sc.children.forEach(function (s) {
    if (s.type !== 'SECTION') return;
    if (s.name === 'Desktop') desk = s;
    if (s.name === 'Responsive') resp = s;
  });

  /* 1. orphan labels: TEXT nodes not named lbl:* */
  var orphans = 0;
  resp.children.slice().forEach(function (n) {
    if (n.type === 'TEXT' && String(n.name).indexOf('lbl:') !== 0) { n.remove(); orphans++; }
  });

  /* 2. count */
  var tab = 0, mob = 0, lbl = 0, other = 0;
  resp.children.forEach(function (n) {
    var nm = String(n.name);
    if (n.type === 'TEXT') { lbl++; return; }
    if (nm.indexOf('Tablet 900') > 0) tab++;
    else if (nm.indexOf('Mobile 375') > 0) mob++;
    else other++;
  });

  /* 3. hide the optional empty slots on the new frames */
  var SLOT = { code:1, time:1, value:1 }, PARENT = { body:1, meta:1, dd:1 };
  var hidden = 0;
  resp.findAll(function (n) { return n.type === 'TEXT'; }).forEach(function (t) {
    if ((t.characters || '').trim() || t.visible === false) return;
    var pn = t.parent ? String(t.parent.name) : '';
    if (SLOT[t.name] === 1 && PARENT[pn] === 1) { t.visible = false; hidden++; }
  });

  /* 4. keep the two sections apart */
  // sections do not auto-grow via the API — size Responsive to its contents
  var maxR = 0, maxB = 0;
  var rb = resp.absoluteBoundingBox;
  resp.children.forEach(function (k) {
    var nb = k.absoluteBoundingBox;
    if (rb && nb) { maxR = Math.max(maxR, (nb.x - rb.x) + nb.width); maxB = Math.max(maxB, (nb.y - rb.y) + nb.height); }
  });
  try { resp.resizeWithoutConstraints(maxR + 80, maxB + 80); } catch (e) { try { resp.resize(maxR + 80, maxB + 80); } catch (e2) {} }

  resp.x = desk.x;
  resp.y = desk.y + desk.height + 320;
  var overlap = !(resp.x >= desk.x + desk.width || resp.x + resp.width <= desk.x ||
                  resp.y >= desk.y + desk.height || resp.y + resp.height <= desk.y);

  report = 'RESPFIN tablet=' + tab + ' mobile=' + mob + ' labels=' + lbl + ' other=' + other +
           ' orphansRemoved=' + orphans + ' slotsHidden=' + hidden + ' overlap=' + overlap;
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 140); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
