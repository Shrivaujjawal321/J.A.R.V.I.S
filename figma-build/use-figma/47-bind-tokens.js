/* Bind the 34 paint styles and 7 text styles to actual nodes.
   Until now every fill was a raw hex and every style was decorative, so
   "select a node and see the token" was not true. Binding the component
   MASTERS makes all 27k instances inherit it. Safe to re-run. */
(async () => {
var report = 'start';
try {
  function hex(c){
    function h(v){ var x = Math.round(v * 255).toString(16); return x.length < 2 ? '0' + x : x; }
    return (h(c.r) + h(c.g) + h(c.b)).toLowerCase();
  }

  var pstyles = await figma.getLocalPaintStylesAsync();
  var tstyles = await figma.getLocalTextStylesAsync();
  var byHex = {};
  pstyles.forEach(function (s) {
    var p = s.paints && s.paints[0];
    if (p && p.type === 'SOLID') { var k = hex(p.color); if (!byHex[k]) byHex[k] = s; }
  });
  var byType = {};
  tstyles.forEach(function (s) {
    var lh = (s.lineHeight && s.lineHeight.unit === 'PIXELS') ? Math.round(s.lineHeight.value) : 0;
    byType[s.fontName.family + '|' + s.fontName.style + '|' + Math.round(s.fontSize) + '|' + lh] = s;
  });

  var ds = null, sc = null;
  figma.root.children.forEach(function (p) {
    if (p.name === '01 Design System') ds = p;
    if (p.name === '02 Screens') sc = p;
  });

  var boundFill = 0, boundText = 0, skipped = 0;

  async function bindNode(n){
    // fill
    if (n.fills && n.fills !== figma.mixed && n.fills.length === 1 && n.fills[0].type === 'SOLID'
        && (n.fills[0].opacity == null || n.fills[0].opacity === 1)
        && (!n.fillStyleId || n.fillStyleId === '')) {
      var st = byHex[hex(n.fills[0].color)];
      if (st) {
        try { if (n.setFillStyleIdAsync) { await n.setFillStyleIdAsync(st.id); } else { n.fillStyleId = st.id; } boundFill++; }
        catch (e) { skipped++; }
      }
    }
    // text
    if (n.type === 'TEXT' && n.fontName !== figma.mixed && n.fontSize !== figma.mixed
        && (!n.textStyleId || n.textStyleId === '')) {
      var lh = (n.lineHeight && n.lineHeight.unit === 'PIXELS') ? Math.round(n.lineHeight.value) : 0;
      var ts = byType[n.fontName.family + '|' + n.fontName.style + '|' + Math.round(n.fontSize) + '|' + lh];
      if (ts) {
        try { if (n.setTextStyleIdAsync) { await n.setTextStyleIdAsync(ts.id); } else { n.textStyleId = ts.id; } boundText++; }
        catch (e) { skipped++; }
      }
    }
  }

  // page 01 — masters and foundations; instances on page 02 inherit from these
  await figma.setCurrentPageAsync(ds);
  var nodes = ds.findAll(function (n) { return true; });
  for (var i = 0; i < nodes.length; i++) { await bindNode(nodes[i]); }

  report = 'BIND styles=' + pstyles.length + '/' + tstyles.length +
           ' nodes=' + nodes.length + ' fills=' + boundFill + ' text=' + boundText + ' skipped=' + skipped;
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 150); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
