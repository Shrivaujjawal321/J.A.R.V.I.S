/* Wire every sidebar control on all 42 desktop screens.
   Frame names carry the address: "07 RR — Coming soon" = section 7, sub 1;
   "12.10 Settings — Capacity" = section 12, sub 10. Nothing depends on labels.
   Navigating to the frame you are already inside is rejected by Figma, so those
   use Scroll To the page header instead. Safe to re-run. */
(async () => {
var report = 'start';
try {
  var KEYS = ['dashboard','fleet','drivers','loads','trips','ops','rr','yards','alerts','reports','earnings','settings'];

  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);
  var desk = null;
  sc.children.forEach(function (s) { if (s.name === 'Desktop') desk = s; });

  /* address every frame from its name prefix */
  var byAddr = {};
  desk.children.forEach(function (f) {
    if (f.type !== 'FRAME') return;
    var head = f.name.split(' ')[0];
    var bits = head.split('.');
    var secIdx = parseInt(bits[0], 10);
    var subNum = bits.length > 1 ? parseInt(bits[1], 10) : 1;
    if (!secIdx || secIdx > 12) return;
    byAddr[KEYS[secIdx - 1] + '/' + (subNum - 1)] = f;
  });

  function navAction(destId) {
    return { trigger: { type: 'ON_CLICK' }, actions: [{ type: 'NODE', destinationId: destId,
             navigation: 'NAVIGATE', transition: null, preserveScrollPosition: false, resetVideoPosition: false }] };
  }
  function scrollAction(destId) {
    return { trigger: { type: 'ON_CLICK' }, actions: [{ type: 'NODE', destinationId: destId,
             navigation: 'SCROLL_TO', transition: null, preserveScrollPosition: false, resetVideoPosition: false }] };
  }

  var nav = 0, sub = 0, scroll = 0, missing = 0, failed = 0, firstErr = '';

  for (var k = 0; k < desk.children.length; k++) {
    var f = desk.children[k];
    if (f.type !== 'FRAME') continue;
    var header = f.findOne(function (n) { return n.name === 'pagehd'; });

    var controls = f.findAll(function (n) {
      return typeof n.name === 'string' && (n.name.indexOf('nav/') === 0 || n.name.indexOf('sub/') === 0);
    });

    for (var j = 0; j < controls.length; j++) {
      var c = controls[j], dest = null, isNav = c.name.indexOf('nav/') === 0;
      if (isNav) dest = byAddr[c.name.substring(4) + '/0'];
      else dest = byAddr[c.name.substring(4)];
      if (!dest) { missing++; continue; }
      try {
        if (dest.id === f.id) {
          if (header) { await c.setReactionsAsync([scrollAction(header.id)]); scroll++; }
        } else {
          await c.setReactionsAsync([navAction(dest.id)]);
          if (isNav) nav++; else sub++;
        }
      } catch (e) {
        failed++;
        if (!firstErr) firstErr = String(e && e.message ? e.message : e).substring(0, 60);
      }
    }
  }

  /* start the flow on the dashboard */
  try {
    var dash = byAddr['dashboard/0'];
    if (dash) dash.setRelaunchData ? null : null;
    if (dash && desk.parent) { sc.flowStartingPoints = [{ nodeId: dash.id, name: 'Carrier Console' }]; }
  } catch (e) {}

  report = 'WIRED nav=' + nav + ' sub=' + sub + ' scroll=' + scroll +
           ' total=' + (nav + sub + scroll) + ' missing=' + missing + ' failed=' + failed + (firstErr ? ' err=' + firstErr : '');
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 140); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0 || p.name.indexOf('SUBFIX') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
