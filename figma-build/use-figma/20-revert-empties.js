(async () => {
var report = 'start';
try {
  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);
  var shown = 0, ctx = [];
  sc.findAll(function (n) { return n.type === 'TEXT' && n.visible === false; }).forEach(function (t) {
    if ((t.characters || '').trim()) return;
    var par = t.parent;
    if (par && String(par.name).indexOf('h0') === 0) {
      t.visible = true; shown++;
      if (ctx.length < 3) ctx.push(String(par.name) + ' layout=' + String(par.layoutMode) + ' w=' + Math.round(t.width));
    }
  });
  report = 'REVERT shown=' + shown + ' ' + JSON.stringify(ctx);
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 130); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
