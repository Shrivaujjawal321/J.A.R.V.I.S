(async () => {
var report = 'start';
try {
  var sc = null;
  figma.root.children.forEach(function (p) { if (p.name === '02 Screens') sc = p; });
  await figma.setCurrentPageAsync(sc);
  var desk = null;
  sc.children.forEach(function (s) { if (s.name === 'Desktop') desk = s; });

  var okFrames = 0, badFrames = 0, sample = '', badSample = '';
  desk.children.forEach(function (f) {
    if (f.type !== 'FRAME') return;
    var ost = f.findOne(function (n) { return n.name === 'ost'; });
    if (!ost) { badFrames++; if (!badSample) badSample = f.name + ':no-ost'; return; }
    var texts = [];
    ost.children.forEach(function (c) {
      var t = c.findOne ? c.findOne(function (n) { return n.type === 'TEXT'; }) : null;
      texts.push(t ? (t.characters || '(blank)') : '(no-text-node)');
    });
    var good = texts.length === 4 && texts.every(function (t) { return t && t !== '(blank)' && t !== '(no-text-node)'; });
    if (good) { okFrames++; if (!sample) sample = f.name.substring(0,14) + '=' + texts.join(','); }
    else { badFrames++; if (!badSample) badSample = f.name.substring(0,16) + '=' + texts.join(','); }
  });
  report = 'ORGCHIP ok=' + okFrames + ' bad=' + badFrames + ' | good:' + sample.substring(0,60) + ' | bad:' + badSample.substring(0,60);
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 140); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0 || p.name.indexOf('FRAMES') === 0 || p.name.indexOf('BUILT') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
