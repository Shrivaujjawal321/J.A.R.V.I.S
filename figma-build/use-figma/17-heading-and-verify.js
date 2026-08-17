(async () => {
var report = 'start';
try {
  var pr = null, sc = null;
  figma.root.children.forEach(function (p) {
    if (p.name.indexOf('03 Prototype') === 0) pr = p;
    if (p.name === '02 Screens') sc = p;
  });

  // --- A/B checks on the screens page (from the earlier finishing pass) ---
  await figma.setCurrentPageAsync(sc);
  var PH = { Cell: 1, sub: 1, COLUMN: 1, sub2: 1 };
  var phTotal = 0, phHidden = 0;
  sc.findAll(function (n) { return PH[n.name] === 1; }).forEach(function (n) {
    var p = n.parent;
    if (p && typeof p.name === 'string' && p.name.indexOf('Table/') === 0) {
      phTotal++; if (n.visible === false) phHidden++;
    }
  });
  var eyebrowTotal = 0, eyebrowShown = 0;
  sc.findAll(function (n) { return n.name === 'alert-eyebrow'; }).forEach(function (n) {
    eyebrowTotal++; if (n.visible !== false) eyebrowShown++;
  });

  // --- fix the stale note heading on page 03 ---
  await figma.setCurrentPageAsync(pr);
  var board = pr.children[0];
  var texts = board.findAll(function (n) { return n.type === 'TEXT'; });
  var fonts = {};
  texts.forEach(function (t) { if (t.fontName && t.fontName !== figma.mixed) fonts[t.fontName.family + '||' + t.fontName.style] = t.fontName; });
  var keys = Object.keys(fonts);
  for (var i = 0; i < keys.length; i++) { await figma.loadFontAsync(fonts[keys[i]]); }
  var fixed = 0;
  texts.forEach(function (t) {
    if (t.fontName === figma.mixed) return;
    if (t.characters.indexOf('132') >= 0 && t.characters.length <= 60) {
      t.characters = 'All 144 sidebar items are interactive'; fixed++;
    }
  });

  report = 'OK heading=' + fixed + ' | placeholders hidden ' + phHidden + '/' + phTotal +
           ' | alert-eyebrow ' + eyebrowShown + ' shown of ' + eyebrowTotal;
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 130); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
