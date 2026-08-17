(async () => {
var report = 'start';
try {
  var ds = null, sc = null, pr = null;
  figma.root.children.forEach(function (p) {
    if (p.name === '01 Design System') ds = p;
    if (p.name === '02 Screens') sc = p;
    if (p.name.indexOf('03 Prototype') === 0) pr = p;
  });

  await figma.setCurrentPageAsync(sc);
  var desk = null, resp = null;
  sc.children.forEach(function (s) {
    if (s.type !== 'SECTION') return;
    if (s.name === 'Desktop') desk = s;
    if (s.name === 'Responsive') resp = s;
  });
  var deskFrames = desk.children.filter(function (n) { return n.type === 'FRAME'; }).length;
  var respFrames = resp.children.filter(function (n) { return n.type === 'FRAME'; }).length;
  var inst = sc.findAll(function (n) { return n.type === 'INSTANCE'; }).length;

  var links = 0;
  desk.findAll(function (n) {
    return typeof n.name === 'string' && (n.name.indexOf('nav/') === 0 || n.name.indexOf('sub/') === 0);
  }).forEach(function (n) { if (n.reactions && n.reactions.length) links++; });

  await figma.setCurrentPageAsync(ds);
  var comps = ds.findAll(function (n) { return n.type === 'COMPONENT_SET' || (n.type === 'COMPONENT' && !(n.parent && n.parent.type === 'COMPONENT_SET')); }).length;
  var vars = ds.findAll(function (n) { return n.type === 'COMPONENT' && n.parent && n.parent.type === 'COMPONENT_SET'; }).length;

  await figma.setCurrentPageAsync(pr);
  pr.name = '03 Prototype';

  report = 'FINAL desk=' + deskFrames + ' resp=' + respFrames + ' inst=' + inst +
           ' links=' + links + ' comps=' + comps + ' variants=' + vars + ' p3kids=' + pr.children.length;
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 140); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
