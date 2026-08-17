/* Measure what the sidebar rail is actually made of before deciding how to fix it. */
(async () => {
var report = 'start';
try {
  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);
  var desk = null;
  sc.children.forEach(function (s) { if (s.type === 'SECTION' && s.name === 'Desktop') desk = s; });
  var frame = null;
  desk.children.forEach(function (f) { if (f.type === 'FRAME' && f.name.indexOf('02 Fleet — All') === 0) frame = f; });
  var rail = frame.findOne(function (n) { return n.type === 'FRAME' && n.name === 'Sidebar'; });

  var inst = 0, raw = 0, txt = 0, vec = 0;
  var rawNames = {}, instNames = {};
  var stack = rail.children.slice();
  while (stack.length) {
    var n = stack.pop();
    if (n.type === 'INSTANCE') {
      inst++;
      var mn = n.mainComponent ? (n.mainComponent.parent && n.mainComponent.parent.type === 'COMPONENT_SET'
                ? n.mainComponent.parent.name : n.mainComponent.name) : n.name;
      instNames[mn] = (instNames[mn] || 0) + 1;
      continue;                       /* do not descend into instances */
    }
    if (n.type === 'TEXT') txt++;
    else if (n.type === 'VECTOR' || n.type === 'ELLIPSE' || n.type === 'RECTANGLE') vec++;
    else { raw++; rawNames[n.name] = (rawNames[n.name] || 0) + 1; }
    if (n.children) for (var i = 0; i < n.children.length; i++) stack.push(n.children[i]);
  }
  report = 'RAIL inst=' + inst + ' rawFrames=' + raw + ' text=' + txt + ' vec=' + vec +
           ' | instances=' + JSON.stringify(instNames).substring(0, 120) +
           ' | raw=' + JSON.stringify(rawNames).substring(0, 90);
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 140); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report.substring(0, 200);
} catch (e) {}
console.log(report);
})();
