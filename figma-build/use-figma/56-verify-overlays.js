(async () => {
var report = 'start';
try {
  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);
  var ov = null, desk = null, resp = null;
  sc.children.forEach(function (s) {
    if (s.type !== 'SECTION') return;
    if (s.name === 'Overlays') ov = s;
    if (s.name === 'Desktop') desk = s;
    if (s.name === 'Responsive') resp = s;
  });
  if (!ov) throw new Error('no Overlays section');
  var frames = ov.children.filter(function (n) { return n.type === 'FRAME'; });
  var names = frames.map(function (f) { return f.name.substring(0, 12); });
  function hit(a, b){ return !(a.x >= b.x + b.width || a.x + a.width <= b.x || a.y >= b.y + b.height || a.y + a.height <= b.y); }
  var clash = (desk && hit(ov, desk)) || (resp && hit(ov, resp));
  report = 'OVL frames=' + frames.length + ' inst=' + ov.findAll(function(n){return n.type==='INSTANCE';}).length +
           ' clash=' + clash + ' ' + JSON.stringify(names).substring(0, 110);
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 140); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
