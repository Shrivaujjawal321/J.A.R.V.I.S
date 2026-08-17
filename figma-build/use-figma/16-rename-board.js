(async () => {
  var pr = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) pr = p; });
  await figma.setCurrentPageAsync(pr);
  if (pr.children.length) pr.children[0].name = 'Prototype - flow & coverage';
  console.log('renamed');
})();
