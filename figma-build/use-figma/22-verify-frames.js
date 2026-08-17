(async () => {
var report = 'start';
try {
  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);
  var desk = null, resp = null;
  sc.children.forEach(function (s) { if (s.name === 'Desktop') desk = s; if (s.name === 'Responsive') resp = s; });
  var orig = 0, subs = 0, overlaps = 0, tallest = 0, shortest = 99999;
  var boxes = [];
  desk.children.forEach(function (f) {
    if (f.type !== 'FRAME') return;
    if (f.name.charAt(2) === ' ') orig++; else subs++;
    tallest = Math.max(tallest, f.height); shortest = Math.min(shortest, f.height);
    boxes.push({x:f.x, y:f.y, w:f.width, h:f.height, n:f.name});
  });
  for (var i = 0; i < boxes.length; i++) for (var j = i+1; j < boxes.length; j++) {
    var a = boxes[i], b = boxes[j];
    if (a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y) overlaps++;
  }
  report = 'FRAMES desk=' + desk.children.length + ' orig=' + orig + ' sub=' + subs +
           ' resp=' + (resp ? resp.children.length : 0) + ' overlap=' + overlaps +
           ' h=' + Math.round(shortest) + '-' + Math.round(tallest);
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 140); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0 || p.name.indexOf('BUILT') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
