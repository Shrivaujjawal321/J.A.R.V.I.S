(async () => {
var report = 'start';
try {
  var sc = null, pr = null;
  figma.root.children.forEach(function (p) {
    if (p.name === '02 Screens') sc = p;
    if (p.name.indexOf('03 Prototype') === 0) pr = p;
  });
  await figma.setCurrentPageAsync(sc);

  var BAD = {}; ['Cell','sub','sub2','COLUMN','Label','text','Text','TEXT','placeholder','Placeholder','Lorem','TODO','xxx','...'].forEach(function (w) { BAD[w] = 1; });
  var counts = {}, empties = 0, visTexts = 0;
  sc.findAll(function (n) { return n.type === 'TEXT'; }).forEach(function (t) {
    var vis = true, p = t;
    while (p && p.type !== 'PAGE') { if (p.visible === false) { vis = false; break; } p = p.parent; }
    if (!vis) return;
    visTexts++;
    var c = (t.characters || '').trim();
    if (!c) { empties++; return; }
    if (BAD[c] === 1) counts[c] = (counts[c] || 0) + 1;
  });

  report = 'SCAN visibleText=' + visTexts + ' empty=' + empties + ' placeholders=' + JSON.stringify(counts);
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 130); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0 || p.name.indexOf('OK heading') === 0 || p.name.indexOf('SCAN ') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
