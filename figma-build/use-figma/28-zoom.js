(async () => {
  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);
  var desk = null;
  sc.children.forEach(function (s) { if (s.name === 'Desktop') desk = s; });
  var target = null;
  desk.children.forEach(function (f) { if (f.name.indexOf('02.4 ') === 0) target = f; });
  if (target) { figma.currentPage.selection = [target]; figma.viewport.scrollAndZoomIntoView([target]); }
  console.log('zoomed ' + (target ? target.name : 'none'));
})();
