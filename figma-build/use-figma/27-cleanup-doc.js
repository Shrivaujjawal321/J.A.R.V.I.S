(async () => {
var report = 'start';
try {
  var pr = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) pr = p; });
  await figma.setCurrentPageAsync(pr);
  var removed = 0, board = null;
  pr.children.slice().forEach(function (n) {
    if (n.name === 'Prototype - flow & coverage' || n.name.indexOf('DOC ') === 0) { board = n; return; }
    n.remove(); removed++;
  });
  if (board) board.name = 'Prototype - flow & coverage';
  report = 'CLEAN removed=' + removed + ' children=' + pr.children.length;
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 130); }
console.log(report);
})();
