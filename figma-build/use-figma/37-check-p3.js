(async () => {
  var pr = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) pr = p; });
  await figma.setCurrentPageAsync(pr);
  var names = pr.children.map(function (n) { return n.type + ':' + String(n.name).substring(0, 34); });
  console.log('P3 kids=' + pr.children.length + ' ' + JSON.stringify(names).substring(0, 200));
})();
