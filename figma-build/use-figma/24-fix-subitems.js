/* A. 12 Settings — My Profile was built before the nav was corrected: it shows 7
      sub-items, the console has 10. Clone the last item three times for
      Contract / Finance / Capacity.
   B. The original 12 frames' sub-items are unnamed, so the prototype cannot
      target them. Name every sub-item sub/<key>/<index>. */
(async () => {
var report = 'start';
try {
  var SUBS = {dashboard:1, fleet:8, drivers:3, loads:6, trips:5, ops:3, rr:1, yards:1, alerts:1, reports:1, earnings:2, settings:10};
  var KEYS = ['dashboard','fleet','drivers','loads','trips','ops','rr','yards','alerts','reports','earnings','settings'];
  var ADD = ['Contract','Finance','Capacity'];

  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);
  var desk = null;
  sc.children.forEach(function (s) { if (s.name === 'Desktop') desk = s; });

  var added = 0, named = 0, framesTouched = 0, mismatch = [];

  for (var k = 0; k < desk.children.length; k++) {
    var f = desk.children[k];
    if (f.type !== 'FRAME') continue;
    var subsFr = f.findOne(function (n) { return n.type === 'FRAME' && n.name === 'subs'; });
    if (!subsFr) continue;

    // which section is active on this frame? the selected nav item
    var key = null;
    f.findAll(function (n) { return typeof n.name === 'string' && n.name.indexOf('nav/') === 0; })
     .forEach(function (n) {
        var st = null;
        try { st = n.componentProperties && n.componentProperties.state && n.componentProperties.state.value; } catch (e) {}
        if (st === 'selected') key = n.name.substring(4);
     });
    if (!key) continue;

    var items = subsFr.children.filter(function (c) { return c.type === 'INSTANCE'; });

    // A. top up Settings to its full 10 entries
    if (key === 'settings' && items.length === 7) {
      var proto = items[items.length - 1];
      for (var a = 0; a < ADD.length; a++) {
        var cl = proto.clone();
        subsFr.appendChild(cl);
        try { cl.setProperties({ state: 'default' }); } catch (e) {}
        var lab = cl.findOne(function (n) { return n.type === 'TEXT' && n.name === 'label'; });
        if (lab) { await figma.loadFontAsync(lab.fontName); lab.characters = ADD[a]; }
        var nw = cl.findOne(function (n) { return n.type === 'TEXT' && n.name === 'new'; });
        if (nw) nw.visible = false;
        added++;
      }
      items = subsFr.children.filter(function (c) { return c.type === 'INSTANCE'; });
    }

    // B. name them in order
    for (var i = 0; i < items.length; i++) {
      var want = 'sub/' + key + '/' + i;
      if (items[i].name !== want) { items[i].name = want; named++; }
    }
    if (items.length !== SUBS[key]) mismatch.push(f.name.substring(0, 16) + ':' + items.length + '/' + SUBS[key]);
    framesTouched++;
  }
  report = 'SUBFIX frames=' + framesTouched + ' added=' + added + ' named=' + named +
           (mismatch.length ? ' MISMATCH=' + JSON.stringify(mismatch).substring(0, 80) : ' allMatch');
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 140); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0 || p.name.indexOf('ORGCHIP') === 0 || p.name.indexOf('FRAMES') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
