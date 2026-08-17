(async () => {
  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);
  var resp = null;
  sc.children.forEach(function (s) { if (s.type === 'SECTION' && s.name === 'Responsive') resp = s; });
  var t = null;
  resp.children.forEach(function (f) {
    if (f.type !== 'FRAME') return;
    if (f.name.indexOf('02 Fleet') === 0 && f.name.indexOf('Mobile 375') > 0 && f.name.indexOf('Menu open') < 0) t = f;
  });
  if (t) { figma.currentPage.selection = [t]; figma.viewport.scrollAndZoomIntoView([t]); }
  console.log('zoom ' + (t ? t.name : 'none'));
})();
