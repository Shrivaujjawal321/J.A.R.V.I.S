/* Give the 12 currently-unwired sidebar items an interaction.
   Figma refuses NAVIGATE to an ancestor, so the item for the screen you are already on
   gets SCROLL_TO the top of that same screen — standard "active tab" behaviour.
   Result is stamped into the page-03 board name because plugin console is unreadable
   once setCurrentPageAsync detaches the UI iframe. Safe to re-run. */
(async () => {
var report = 'start';
try {
  var pageSC = null, pagePR = null;
  figma.root.children.forEach(function (p) {
    if (p.name === '02 Screens') pageSC = p;
    if (p.name.indexOf('03 Prototype') === 0 || p.name.indexOf('CHECK') === 0) pagePR = p;
  });
  await figma.setCurrentPageAsync(pageSC);
  var desktop = null;
  pageSC.children.forEach(function (s) { if (s.name === 'Desktop') desktop = s; });
  if (!desktop) throw new Error('no Desktop section');

  var fixed = 0, skipped = 0, firstErr = '', targets = {};

  for (var k = 0; k < desktop.children.length; k++) {
    var fr = desktop.children[k];
    if (fr.type !== 'FRAME') continue;

    var navs = fr.findAll(function (n) { return typeof n.name === 'string' && n.name.indexOf('nav/') === 0; });
    var unwired = navs.filter(function (n) { return !n.reactions || !n.reactions.length; });
    if (!unwired.length) continue;

    // scroll target: a named header inside this screen, else the screen's first child
    var want = ['header', 'head', 'pagehd', 'topbar', 'main'];
    var dest = null;
    for (var w = 0; w < want.length && !dest; w++) {
      dest = fr.findOne(function (n) { return n.name === want[w] && n.id !== fr.id; });
    }
    if (!dest && fr.children.length) dest = fr.children[0];
    if (!dest) { skipped += unwired.length; continue; }
    targets[dest.name] = (targets[dest.name] || 0) + 1;

    for (var j = 0; j < unwired.length; j++) {
      try {
        await unwired[j].setReactionsAsync([{
          trigger: { type: 'ON_CLICK' },
          actions: [{ type: 'NODE', destinationId: dest.id, navigation: 'SCROLL_TO',
                      transition: null, preserveScrollPosition: false, resetVideoPosition: false }]
        }]);
        fixed++;
      } catch (e) {
        skipped++;
        if (!firstErr) firstErr = String(e && e.message ? e.message : e).substring(0, 150);
      }
    }
  }

  // recount
  var total = 0, nav = 0, scr = 0, none = 0;
  desktop.children.forEach(function (f) {
    if (f.type !== 'FRAME') return;
    f.findAll(function (n) { return typeof n.name === 'string' && n.name.indexOf('nav/') === 0; })
     .forEach(function (n) {
        total++;
        var rs = n.reactions || [];
        if (!rs.length || !rs[0].actions || !rs[0].actions.length) { none++; return; }
        var t = rs[0].actions[0].type;
        if (t === 'NODE') { if (rs[0].actions[0].navigation === 'SCROLL_TO') scr++; else nav++; } else none++;
     });
  });
  report = 'RES total=' + total + ' nav=' + nav + ' scroll=' + scr + ' unwired=' + none +
           ' | fixed=' + fixed + ' skipped=' + skipped +
           ' | tgt=' + JSON.stringify(targets) + (firstErr ? ' | err=' + firstErr : '');
} catch (err) {
  report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 120);
}
try {
  var pr = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0 || p.name.indexOf('CHECK') === 0 || p.name.indexOf('RES ') === 0 || p.name.indexOf('FAIL ') === 0) pr = p; });
  await figma.setCurrentPageAsync(pr);
  if (pr.children.length) pr.children[0].name = report;
} catch (e2) {}
console.log(report);
})();
