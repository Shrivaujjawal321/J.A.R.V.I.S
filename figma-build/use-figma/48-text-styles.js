/* The console uses 23 distinct font sizes; the file shipped 7 text styles, so
   most type — including the 32px KPI numeral — had no style to bind to.
   Scan what is actually used, create a style for every real combination,
   then bind every text node to it. Safe to re-run. */
(async () => {
var report = 'start';
try {
  var ds = null, sc = null;
  figma.root.children.forEach(function (p) {
    if (p.name === '01 Design System') ds = p;
    if (p.name === '02 Screens') sc = p;
  });

  function keyOf(n){
    var lh = (n.lineHeight && n.lineHeight.unit === 'PIXELS') ? Math.round(n.lineHeight.value * 10) / 10 : 0;
    var ls = (n.letterSpacing && n.letterSpacing.unit === 'PIXELS') ? Math.round(n.letterSpacing.value * 100) / 100 : 0;
    return n.fontName.family + '|' + n.fontName.style + '|' + (Math.round(n.fontSize * 10) / 10) + '|' + lh + '|' + ls;
  }
  function groupOf(fam){
    if (fam.indexOf('Barlow') === 0) return 'Display';
    if (fam.indexOf('IBM Plex Mono') === 0 || fam.indexOf('Mono') > 0) return 'Mono';
    return 'Body';
  }

  // 1. what type is actually in use
  await figma.setCurrentPageAsync(ds);
  var counts = {};
  function scan(page){
    page.findAll(function (n) { return n.type === 'TEXT'; }).forEach(function (n) {
      if (n.fontName === figma.mixed || n.fontSize === figma.mixed) return;
      var k = keyOf(n); counts[k] = (counts[k] || 0) + 1;
    });
  }
  scan(ds);
  await figma.setCurrentPageAsync(sc);
  scan(sc);

  // 2. create a style for every combination used at least 8 times
  var existing = await figma.getLocalTextStylesAsync();
  var have = {};
  existing.forEach(function (s) {
    var lh = (s.lineHeight && s.lineHeight.unit === 'PIXELS') ? Math.round(s.lineHeight.value * 10) / 10 : 0;
    var ls = (s.letterSpacing && s.letterSpacing.unit === 'PIXELS') ? Math.round(s.letterSpacing.value * 100) / 100 : 0;
    have[s.fontName.family + '|' + s.fontName.style + '|' + (Math.round(s.fontSize * 10) / 10) + '|' + lh + '|' + ls] = s;
  });

  var keys = Object.keys(counts).filter(function (k) { return counts[k] >= 8; });
  keys.sort(function (a, b) { return counts[b] - counts[a]; });
  var created = 0;
  for (var i = 0; i < keys.length; i++) {
    if (have[keys[i]]) continue;
    var bits = keys[i].split('|');
    var fam = bits[0], sty = bits[1], size = parseFloat(bits[2]), lh = parseFloat(bits[3]), ls = parseFloat(bits[4]);
    await figma.loadFontAsync({ family: fam, style: sty });
    var st = figma.createTextStyle();
    var strong = (sty.indexOf('Semi') >= 0 || sty.indexOf('Bold') >= 0 || sty.indexOf('Medium') >= 0);
    st.name = groupOf(fam) + '/' + size + (strong ? ' ' + sty : '');
    st.fontName = { family: fam, style: sty };
    st.fontSize = size;
    if (lh) st.lineHeight = { value: lh, unit: 'PIXELS' };
    if (ls) st.letterSpacing = { value: ls, unit: 'PIXELS' };
    have[keys[i]] = st; created++;
  }

  // 3. bind every text node that now has a matching style
  var bound = 0, unmatched = 0;
  async function bindPage(page){
    await figma.setCurrentPageAsync(page);
    var ts = page.findAll(function (n) { return n.type === 'TEXT'; });
    for (var j = 0; j < ts.length; j++) {
      var n = ts[j];
      if (n.fontName === figma.mixed || n.fontSize === figma.mixed) continue;
      if (n.textStyleId && n.textStyleId !== '') continue;
      var st2 = have[keyOf(n)];
      if (!st2) { unmatched++; continue; }
      try { if (n.setTextStyleIdAsync) { await n.setTextStyleIdAsync(st2.id); } else { n.textStyleId = st2.id; } bound++; }
      catch (e) { unmatched++; }
    }
  }
  await bindPage(ds);
  await bindPage(sc);

  report = 'TEXTSTYLE combos=' + Object.keys(counts).length + ' created=' + created +
           ' total=' + (existing.length + created) + ' bound=' + bound + ' unmatched=' + unmatched;
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 150); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
