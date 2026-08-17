/* Refresh the page-03 documentation now that all 144 sidebar items are wired,
   and restore the board name. Result stamped into the board name. */
(async () => {
var report = 'start';
try {
  var pr = null;
  figma.root.children.forEach(function (p) {
    var n = p.name;
    if (n.indexOf('03 Prototype') === 0 || n.indexOf('RES ') === 0 || n.indexOf('CHECK') === 0 || n.indexOf('FAIL ') === 0) pr = p;
  });
  if (!pr) throw new Error('prototype page not found');
  await figma.setCurrentPageAsync(pr);
  pr.name = '03 Prototype';
  var board = pr.children[0];

  var NOTE = 'Every sidebar item on every screen is interactive: 144 of 144. ' +
             '132 are page-to-page navigations (12 screens x 11 other destinations). ' +
             'The remaining 12 are the item for the screen you are already on - Figma rejects a ' +
             'navigation whose destination contains the trigger, so those use Scroll To instead ' +
             'and return the screen to its header, which is the standard active-tab behaviour.';

  var texts = board.findAll(function (n) { return n.type === 'TEXT'; });
  var fonts = {};
  texts.forEach(function (t) {
    if (t.fontName && t.fontName !== figma.mixed) fonts[t.fontName.family + '||' + t.fontName.style] = t.fontName;
  });
  var keys = Object.keys(fonts);
  for (var i = 0; i < keys.length; i++) { await figma.loadFontAsync(fonts[keys[i]]); }

  var changed = 0, samples = [];
  for (var j = 0; j < texts.length; j++) {
    var t = texts[j];
    if (t.fontName === figma.mixed) continue;
    var c = t.characters, nc = c;
    if (c === '132') nc = '144';
    else if (c.indexOf('11 outgoing links') >= 0) nc = c.split('11 outgoing links').join('12 interactions');
    else if (c.indexOf('NAVIGATION LINKS') >= 0) nc = c.split('NAVIGATION LINKS').join('SIDEBAR INTERACTIONS');
    else if (c.length > 60 && c.indexOf('132') >= 0) nc = NOTE;
    if (nc !== c) { t.characters = nc; changed++; if (samples.length < 3) samples.push(c.substring(0, 26)); }
  }

  board.name = 'Prototype - flow & coverage';
  report = 'DOC changed=' + changed + '/' + texts.length + ' ex=' + JSON.stringify(samples);
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 130); }
try {
  var p2 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p2 = p; });
  if (p2 && p2.children.length) p2.children[0].name = report;
} catch (e) {}
console.log(report);
})();
