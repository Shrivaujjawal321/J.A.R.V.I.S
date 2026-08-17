/* Count nav interactions and stamp the result into a node name so it can be read from the UI. */
(async () => {
try {
  var pageSC = null, pagePR = null;
  for (var i = 0; i < figma.root.children.length; i++) {
    var p = figma.root.children[i];
    if (p.name === '02 Screens') pageSC = p;
    if (p.name.indexOf('03 Prototype') === 0) pagePR = p;
  }
  await figma.setCurrentPageAsync(pageSC);
  var desktop = null;
  pageSC.children.forEach(function (s) { if (s.name === 'Desktop') desktop = s; });

  var total = 0, nav = 0, scr = 0, none = 0;
  desktop.children.forEach(function (f) {
    if (f.type !== 'FRAME') return;
    f.findAll(function (n) { return typeof n.name === 'string' && n.name.indexOf('nav/') === 0; })
     .forEach(function (n) {
        total++;
        var rs = n.reactions || [];
        if (!rs.length || !rs[0].actions || !rs[0].actions.length) { none++; return; }
        var t = rs[0].actions[0].type;
        if (t === 'NODE') nav++; else if (t === 'SCROLL_TO') scr++; else none++;
     });
  });

  var tag = 'CHECK total=' + total + ' nav=' + nav + ' scroll=' + scr + ' unwired=' + none;
  await figma.setCurrentPageAsync(pagePR);
  var board = pagePR.children[0];
  if (board) board.name = tag;
  console.log('DONE ' + tag);
} catch (err) { console.log('FAILED: ' + (err && err.message ? err.message : String(err))); }
})();
