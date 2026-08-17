/* Full end-state audit of the file. Counts everything a reviewer would check. */
(async () => {
var report = 'start';
try {
  var ds = null, sc = null, pr = null;
  figma.root.children.forEach(function (p) {
    if (p.name === '01 Design System') ds = p;
    if (p.name === '02 Screens') sc = p;
    if (p.name.indexOf('03 Prototype') === 0) pr = p;
  });

  await figma.setCurrentPageAsync(ds);
  var comps = ds.findAll(function (n) { return n.type === 'COMPONENT_SET' || (n.type === 'COMPONENT' && !(n.parent && n.parent.type === 'COMPONENT_SET')); }).length;
  var vars_ = ds.findAll(function (n) { return n.type === 'COMPONENT' && n.parent && n.parent.type === 'COMPONENT_SET'; }).length;
  var ps = (await figma.getLocalPaintStylesAsync()).length;
  var ts = (await figma.getLocalTextStylesAsync()).length;

  await figma.setCurrentPageAsync(sc);
  var desk = null, resp = null, ovl = null;
  sc.children.forEach(function (s) {
    if (s.type !== 'SECTION') return;
    if (s.name === 'Desktop') desk = s;
    if (s.name === 'Responsive') resp = s;
    if (s.name === 'Overlays') ovl = s;
  });
  function frames(sec){ return sec ? sec.children.filter(function (n) { return n.type === 'FRAME'; }) : []; }
  var dF = frames(desk), rF = frames(resp), oF = frames(ovl);
  var rOpen = rF.filter(function (f) { return f.name.indexOf('Menu open') > 0; }).length;

  function links(sec){
    var n = 0;
    if (!sec) return 0;
    sec.findAll(function (x) { return x.reactions && x.reactions.length; }).forEach(function () { n++; });
    return n;
  }
  var dL = links(desk), rL = links(resp);

  // overlap between sections
  function hit(a, b){ return a && b && !(a.x >= b.x + b.width || a.x + a.width <= b.x || a.y >= b.y + b.height || a.y + a.height <= b.y); }
  var clash = (hit(desk, resp) ? 'D-R ' : '') + (hit(desk, ovl) ? 'D-O ' : '') + (hit(resp, ovl) ? 'R-O' : '');

  // frame overlap inside Desktop
  var ov = 0;
  for (var i = 0; i < dF.length; i++) for (var j = i + 1; j < dF.length; j++) {
    var a = dF[i], b = dF[j];
    if (a.x < b.x + b.width && a.x + a.width > b.x && a.y < b.y + b.height && a.y + a.height > b.y) ov++;
  }

  // bound-style coverage + leftover placeholders
  var bound = 0, unbound = 0, placeholders = 0;
  var BAD = {Cell:1, sub:1, sub2:1, COLUMN:1, Label:1, Lorem:1, TODO:1, placeholder:1};
  sc.findAll(function (n) { return n.type === 'TEXT'; }).forEach(function (t) {
    if (t.textStyleId && t.textStyleId !== '') bound++; else unbound++;
    var c = (t.characters || '').trim();
    if (BAD[c] === 1) placeholders++;
  });

  report = 'AUDIT desk=' + dF.length + ' resp=' + rF.length + '(' + rOpen + ' open) ovl=' + oF.length +
           ' | links desk=' + dL + ' resp=' + rL + ' total=' + (dL + rL) +
           ' | comps=' + comps + '/' + vars_ + ' paint=' + ps + ' text=' + ts +
           ' | textBound=' + bound + '/' + (bound + unbound) + ' placeholders=' + placeholders +
           ' | frameOverlap=' + ov + ' sectionClash=' + (clash || 'none');
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 150); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
