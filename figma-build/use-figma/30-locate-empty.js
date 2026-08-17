(async () => {
var report = 'start';
try {
  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);
  var counts = {}, frames = {};
  sc.findAll(function (n) { return n.type === 'TEXT'; }).forEach(function (t) {
    var vis = true, p = t, frame = '?';
    while (p && p.type !== 'PAGE') {
      if (p.visible === false) { vis = false; break; }
      if (p.parent && p.parent.type === 'SECTION') frame = p.name;
      p = p.parent;
    }
    if (!vis) return;
    if ((t.characters || '').trim()) return;
    var key = String(t.parent && t.parent.name) + '>' + t.name;
    counts[key] = (counts[key] || 0) + 1;
    frames[frame.substring(0, 18)] = (frames[frame.substring(0, 18)] || 0) + 1;
  });
  report = 'EMPTYLOC ' + JSON.stringify(counts).substring(0, 130) + ' | frames ' + JSON.stringify(frames).substring(0, 90);
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 140); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
