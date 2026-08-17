/* Give the wizard, the drawers and the mobile menu real Smart-Animate transitions
   at the documented durations, so the motion system can be demonstrated rather
   than only read. Durations come from the Motion spec board. Safe to re-run. */
(async () => {
var report = 'start';
try {
  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);
  var ovl = null, resp = null;
  sc.children.forEach(function (s) {
    if (s.type !== 'SECTION') return;
    if (s.name === 'Overlays') ovl = s;
    if (s.name === 'Responsive') resp = s;
  });

  function byName(sec, prefix){
    var hit = null;
    if (!sec) return null;
    sec.children.forEach(function (f) { if (f.type === 'FRAME' && f.name.indexOf(prefix) === 0) hit = f; });
    return hit;
  }
  function smart(destId, ms, easing){
    return { trigger: { type: 'ON_CLICK' },
             actions: [{ type: 'NODE', destinationId: destId, navigation: 'NAVIGATE',
                         transition: { type: 'SMART_ANIMATE',
                                       easing: { type: easing || 'EASE_OUT' },
                                       duration: ms / 1000 },
                         preserveScrollPosition: false, resetVideoPosition: false }] };
  }
  function firstButton(frame, labelPart){
    var hit = null;
    frame.findAll(function (n) { return n.type === 'INSTANCE'; }).forEach(function (n) {
      if (hit) return;
      var t = n.findOne(function (x) { return x.type === 'TEXT'; });
      if (t && String(t.characters).toLowerCase().indexOf(labelPart) >= 0) hit = n;
    });
    return hit;
  }

  var wired = 0, missed = 0;

  /* The wizard advances by PICKING an asset, not by a Next button — same as the
     console, where choosing a truck moves the step on. So every pick row in a step
     navigates to the next step, and Back returns. 220ms, ease-out. */
  var W = ['W1 Assign', 'W2 Assign', 'W3 Assign', 'W4 Assign'].map(function (p) { return byName(ovl, p); });
  function pickRows(frame){
    var rows = [];
    frame.findAll(function (n) { return n.type === 'INSTANCE'; }).forEach(function (n) {
      var nm = String(n.name);
      if (nm.indexOf('Pick Row') >= 0) { rows.push(n); return; }
      var t = n.findOne(function (x) { return x.type === 'TEXT'; });
      if (!t) return;
      var c = String(t.characters).trim();
      if (!c || c.length > 6) return;
      if (c === 'Cancel' || c === 'Back') return;
      rows.push(n);
    });
    return rows;
  }
  for (var i = 0; i < W.length - 1; i++) {
    if (!W[i] || !W[i + 1]) { missed++; continue; }
    var rows = pickRows(W[i]);
    if (!rows.length) { missed++; continue; }
    for (var r = 0; r < rows.length; r++) {
      try { await rows[r].setReactionsAsync([smart(W[i + 1].id, 220, 'EASE_OUT')]); wired++; }
      catch (e) { missed++; }
    }
    /* Back goes to the previous step, and exits are quicker than entries */
    if (i > 0) {
      var back = firstButton(W[i], 'back');
      if (back) { try { await back.setReactionsAsync([smart(W[i - 1].id, 180, 'EASE_IN')]); wired++; } catch (e) { missed++; } }
    }
  }
  var back4 = W[3] ? firstButton(W[3], 'back') : null;
  if (back4 && W[2]) { try { await back4.setReactionsAsync([smart(W[2].id, 180, 'EASE_IN')]); wired++; } catch (e) { missed++; } }

  /* mobile and tablet menu: closed -> open at motion.base, scrim closes faster (exit is quicker) */
  var pairs = 0;
  if (resp) {
    var closed = {}, open = {};
    resp.children.forEach(function (f) {
      if (f.type !== 'FRAME') return;
      if (f.name.indexOf(' — Menu open') > 0) open[f.name.replace(' — Menu open', '')] = f;
      else closed[f.name] = f;
    });
    var keys = Object.keys(open);
    for (var k = 0; k < keys.length; k++) {
      var c = closed[keys[k]], o = open[keys[k]];
      if (!c || !o) continue;
      var burger = null;
      c.findAll(function (n) { return n.type === 'FRAME' && n.name === 'tbtn'; }).forEach(function (n) { if (!burger) burger = n; });
      var scrim = o.findOne(function (n) { return n.name === 'scrim' || n.name === 'sidescrim'; });
      try {
        if (burger) { await burger.setReactionsAsync([smart(o.id, 220, 'EASE_OUT')]); wired++; }
        if (scrim)  { await scrim.setReactionsAsync([smart(c.id, 180, 'EASE_IN')]);  wired++; }
        pairs++;
      } catch (e) { missed++; }
    }
  }

  report = 'PROTO wired=' + wired + ' menuPairs=' + pairs + ' missed=' + missed;
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 150); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
