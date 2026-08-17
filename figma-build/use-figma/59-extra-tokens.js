/* Colours the console uses that had no token and no representation. Adds a
   variable + a paint style for each, in the same collections as the originals. */
(async () => {
var report = 'start';
try {
  var EXTRA = [
    ['brand-deep',    '#0c5c38'], ['brand-ring',    '#2a5c44'], ['brand-prog',   '#3ba872'],
    ['chrome-tile',   '#3a4c66'], ['chrome-tile-2', '#28344a'],
    ['scroll-thumb',  '#c7cfd8'], ['scroll-thumb-inv','#2f3a4c'],
    ['row-blocked-hover','#fbeeee'], ['pick-selected','#f2fbf6'], ['drop-hover','#f4fbf7'],
    ['live-pulse',    '#3ddc84'],
    ['map-bg',        '#0f1622'], ['map-bg-2',      '#0b1017'], ['map-lane',     '#2f527a'],
    ['map-yard',      '#131c2a'], ['map-yard-dot',  '#556781'], ['map-city',     '#3c4a60'],
    ['map-city-ink',  '#6b7789'],
    ['photo-from',    '#e6ebf1'], ['photo-to',      '#d5dde6'],
    ['scrim',         '#0b1017']
  ];
  function rgbOf(hex){
    var h = hex.replace('#', '');
    return { r: parseInt(h.substring(0,2),16)/255, g: parseInt(h.substring(2,4),16)/255, b: parseInt(h.substring(4,6),16)/255 };
  }

  var ds = null;
  figma.root.children.forEach(function (p) { if (p.name === '01 Design System') ds = p; });
  await figma.setCurrentPageAsync(ds);

  var cols = await figma.variables.getLocalVariableCollectionsAsync();
  var colourCol = null;
  cols.forEach(function (c) { if (c.name === 'Color' || c.name === 'Colour') colourCol = c; });
  if (!colourCol) colourCol = cols[0];

  var existingVars = await figma.variables.getLocalVariablesAsync('COLOR');
  var haveVar = {};
  existingVars.forEach(function (v) { haveVar[v.name] = v; });

  var styles = await figma.getLocalPaintStylesAsync();
  var haveStyle = {};
  styles.forEach(function (s) { haveStyle[s.name] = s; });

  var addedVar = 0, addedStyle = 0;
  for (var i = 0; i < EXTRA.length; i++) {
    var nm = EXTRA[i][0], hex = EXTRA[i][1];
    var v = haveVar[nm];
    if (!v && colourCol) {
      try {
        v = figma.variables.createVariable(nm, colourCol, 'COLOR');
        v.setValueForMode(colourCol.modes[0].modeId, rgbOf(hex));
        addedVar++;
      } catch (e) { v = null; }
    }
    if (!haveStyle[nm]) {
      var st = figma.createPaintStyle();
      st.name = nm;
      var paint = { type: 'SOLID', color: rgbOf(hex) };
      if (v) { try { paint = figma.variables.setBoundVariableForPaint(paint, 'color', v); } catch (e) {} }
      st.paints = [paint];
      addedStyle++;
    }
  }
  var ps = (await figma.getLocalPaintStylesAsync()).length;
  var vs = (await figma.variables.getLocalVariablesAsync('COLOR')).length;
  report = 'TOKENS addedVars=' + addedVar + ' addedStyles=' + addedStyle + ' totalPaint=' + ps + ' totalColourVars=' + vs;
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 150); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
