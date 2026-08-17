(async () => {
var report = 'start';
try {
  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);

  var found = [], hid = 0;
  sc.findAll(function (n) { return n.type === 'TEXT'; }).forEach(function (t) {
    var vis = true, p = t, screenName = '?';
    while (p && p.type !== 'PAGE') {
      if (p.visible === false) { vis = false; break; }
      if (p.parent && p.parent.type === 'SECTION') screenName = p.name;
      p = p.parent;
    }
    if (!vis) return;
    if ((t.characters || '').trim()) return;
    if (found.length < 5) found.push(screenName.substring(0, 22) + '>' + String(t.parent && t.parent.name).substring(0, 14));
    t.visible = false; hid++;
  });

  report = 'EMPTY hid=' + hid + ' at=' + JSON.stringify(found);
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 130); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
