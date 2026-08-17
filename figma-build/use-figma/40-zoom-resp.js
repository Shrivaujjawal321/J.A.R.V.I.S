(async () => {
  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);
  var resp = null;
  sc.children.forEach(function (s) { if (s.type === 'SECTION' && s.name === 'Responsive') resp = s; });
  var picks = [];
  resp.children.forEach(function (f) {
    if (f.name.indexOf('12.6 Settings — Company Profile') === 0) picks.push(f);
  });
  if (picks.length) { figma.currentPage.selection = picks; figma.viewport.scrollAndZoomIntoView(picks); }
  console.log('zoom ' + picks.length);
})();
