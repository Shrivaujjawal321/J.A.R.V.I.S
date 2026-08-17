/* Desktop grew from 12 frames to 42, so it now runs into the Responsive
   section. Push Responsive clear of it and report the new bounds. */
(async () => {
var report = 'start';
try {
  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);
  var desk = null, resp = null;
  sc.children.forEach(function (s) {
    if (s.type !== 'SECTION') return;
    if (s.name === 'Desktop') desk = s;
    if (s.name === 'Responsive') resp = s;
  });
  if (!desk || !resp) throw new Error('sections missing: desk=' + !!desk + ' resp=' + !!resp);

  var before = Math.round(resp.x) + ',' + Math.round(resp.y);
  resp.x = desk.x;
  resp.y = desk.y + desk.height + 320;

  var overlap = !(resp.x >= desk.x + desk.width || resp.x + resp.width <= desk.x ||
                  resp.y >= desk.y + desk.height || resp.y + resp.height <= desk.y);

  report = 'SECT desk=' + Math.round(desk.width) + 'x' + Math.round(desk.height) +
           ' resp ' + before + ' -> ' + Math.round(resp.x) + ',' + Math.round(resp.y) +
           ' overlap=' + overlap;
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 140); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
