/* Bind fills on the raw frames the renderer builds directly on the screens
   (sidebar, panels, content, map). Nodes inside instances are skipped —
   they inherit from the masters bound in step 47. Safe to re-run. */
(async () => {
var report = 'start';
try {
  function hex(c){
    function h(v){ var x = Math.round(v * 255).toString(16); return x.length < 2 ? '0' + x : x; }
    return (h(c.r) + h(c.g) + h(c.b)).toLowerCase();
  }
  var pstyles = await figma.getLocalPaintStylesAsync();
  var byHex = {};
  pstyles.forEach(function (s) {
    var p = s.paints && s.paints[0];
    if (p && p.type === 'SOLID') { var k = hex(p.color); if (!byHex[k]) byHex[k] = s; }
  });

  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);

  var bound = 0, seen = 0, noMatch = 0;
  var stack = sc.children.slice();
  while (stack.length) {
    var n = stack.pop();
    seen++;
    if (n.type === 'INSTANCE') continue;          // inherits from its master
    if (n.fills && n.fills !== figma.mixed && n.fills.length === 1 && n.fills[0].type === 'SOLID'
        && (n.fills[0].opacity == null || n.fills[0].opacity === 1)
        && (!n.fillStyleId || n.fillStyleId === '')) {
      var st = byHex[hex(n.fills[0].color)];
      if (st) {
        try { if (n.setFillStyleIdAsync) { await n.setFillStyleIdAsync(st.id); } else { n.fillStyleId = st.id; } bound++; }
        catch (e) { noMatch++; }
      } else noMatch++;
    }
    if (n.children) { for (var i = 0; i < n.children.length; i++) stack.push(n.children[i]); }
  }
  report = 'BINDSCR walked=' + seen + ' fillsBound=' + bound + ' noMatch=' + noMatch;
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 150); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
