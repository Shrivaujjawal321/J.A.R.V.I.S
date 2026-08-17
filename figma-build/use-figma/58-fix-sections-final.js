/* Responsive grew to 168 frames and now runs into Overlays. Re-stack the three
   sections vertically, then re-count placeholders counting VISIBLE text only
   (hidden component-default text like "sub"/"Cell" is not a defect). */
(async () => {
var report = 'start';
try {
  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);
  var desk = null, resp = null, ovl = null;
  sc.children.forEach(function (s) {
    if (s.type !== 'SECTION') return;
    if (s.name === 'Desktop') desk = s;
    if (s.name === 'Responsive') resp = s;
    if (s.name === 'Overlays') ovl = s;
  });

  function fit(sec){
    if (!sec || !sec.children.length) return;
    var sb = sec.absoluteBoundingBox, mr = 0, mb = 0;
    sec.children.forEach(function (k) {
      var nb = k.absoluteBoundingBox;
      if (sb && nb){ mr = Math.max(mr, (nb.x - sb.x) + nb.width); mb = Math.max(mb, (nb.y - sb.y) + nb.height); }
    });
    try { sec.resizeWithoutConstraints(mr + 80, mb + 80); } catch (e) { try { sec.resize(mr + 80, mb + 80); } catch (e2) {} }
  }
  fit(desk); fit(resp); fit(ovl);
  resp.x = desk.x; resp.y = desk.y + desk.height + 400;
  ovl.x  = desk.x; ovl.y  = resp.y + resp.height + 400;

  function hit(a, b){ return a && b && !(a.x >= b.x + b.width || a.x + a.width <= b.x || a.y >= b.y + b.height || a.y + a.height <= b.y); }
  var clash = (hit(desk, resp) ? 'D-R ' : '') + (hit(desk, ovl) ? 'D-O ' : '') + (hit(resp, ovl) ? 'R-O' : '');

  var BAD = {Cell:1, sub:1, sub2:1, COLUMN:1, Label:1, Lorem:1, TODO:1, placeholder:1};
  var vis = 0, ph = 0, empty = 0;
  sc.findAll(function (n) { return n.type === 'TEXT'; }).forEach(function (t) {
    var p = t, ok = true;
    while (p && p.type !== 'PAGE') { if (p.visible === false) { ok = false; break; } p = p.parent; }
    if (!ok) return;
    vis++;
    var c = (t.characters || '').trim();
    if (!c) { empty++; return; }
    if (BAD[c] === 1) ph++;
  });

  report = 'SECTFIX clash=' + (clash || 'none') +
           ' | desk=' + Math.round(desk.height) + ' resp=' + Math.round(resp.height) + ' ovl=' + Math.round(ovl.height) +
           ' | visibleText=' + vis + ' placeholders=' + ph + ' empty=' + empty;
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 150); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
