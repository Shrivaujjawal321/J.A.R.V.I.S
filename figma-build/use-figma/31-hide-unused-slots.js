/* List Item's code/time and KV Row's value are optional slots — the renderer
   hides them when unused, but the generated sub-screens left a few set to "".
   Hide exactly those. Table header labels that are blank stay visible: they sit
   in a vertical auto-layout and hiding them collapses the header height. */
(async () => {
var report = 'start';
try {
  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);
  var SLOT = { code: 1, time: 1, value: 1 };
  var PARENT = { body: 1, meta: 1, dd: 1 };
  var hidden = 0, left = 0;
  sc.findAll(function (n) { return n.type === 'TEXT'; }).forEach(function (t) {
    if ((t.characters || '').trim()) return;
    if (t.visible === false) return;
    var pn = t.parent ? String(t.parent.name) : '';
    if (SLOT[t.name] === 1 && PARENT[pn] === 1) { t.visible = false; hidden++; }
    else left++;
  });
  report = 'SLOTS hidden=' + hidden + ' leftVisible=' + left;
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 140); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
