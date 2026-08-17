(async () => {
var report = 'start';
try {
  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);
  var ovl = null;
  sc.children.forEach(function (s) { if (s.type === 'SECTION' && s.name === 'Overlays') ovl = s; });
  var out = [];
  ['W1', 'W2', 'W3'].forEach(function (pfx) {
    var f = null;
    ovl.children.forEach(function (x) { if (x.type === 'FRAME' && x.name.indexOf(pfx) === 0) f = x; });
    if (!f) { out.push(pfx + ':missing'); return; }
    var labels = [];
    f.findAll(function (n) { return n.type === 'INSTANCE'; }).forEach(function (n) {
      var t = n.findOne(function (x) { return x.type === 'TEXT'; });
      if (t && t.characters && t.characters.length < 30) labels.push(t.characters);
    });
    out.push(pfx + ':[' + labels.slice(-6).join(' | ') + ']');
  });
  report = 'WIZBTN ' + out.join('  ');
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 140); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report.substring(0, 170);
} catch (e) {}
console.log(report);
})();
