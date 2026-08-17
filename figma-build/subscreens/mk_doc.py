import json, io, os
HERE = os.path.dirname(os.path.abspath(__file__))
base = io.open(HERE + '/_base.js', encoding='utf-8').read()
D = json.load(io.open("/tmp/claude-1000/-home-ujjwal-Documents-J-A-R-V-I-S-/2633997f-2f24-47b1-b9bc-fed35ace9a16/scratchpad/screens.json", encoding='utf-8'))
SEC = ['dashboard','fleet','drivers','loads','trips','ops','rr','yards','alerts','reports','earnings','settings']
SUBS = {k: len([x for x in D if x.split('|')[0] == k]) for k in SEC}

cells = []
for si, k in enumerate(SEC):
    for i in range(SUBS[k]):
        d = D['%s|%d' % (k, i)]
        name = ('%02d %s — %s' % (si + 1, d['nav'], d['sub'])) if i == 0 else ('%02d.%d %s — %s' % (si + 1, i + 1, d['nav'], d['sub']))
        cells.append({'n': name, 'i': 12 + SUBS[k], 'start': (k == 'dashboard' and i == 0)})

BOARD = r"""
await loadFonts();
await adoptComponents(false);
var pr = null;
figma.root.children.forEach(function(p){ if (p.name.indexOf('03 Prototype') === 0 || p.name.indexOf('WIRED') === 0 || p.name.indexOf('SUBFIX') === 0) pr = p; });
if (!pr) throw new Error('prototype page not found');
pr.name = '03 Prototype';
await figma.setCurrentPageAsync(pr);
pr.children.slice().forEach(function(n){ safe(function(){ n.remove(); }); });
pr.backgrounds = solid(C.canvas);

var board = mkFrame('Prototype - flow & coverage', {dir:'V', gap:22, pad:[34,36,40,36], fill:'#f5f7f9', w:1520});
pr.appendChild(board); board.x = 0; board.y = 0;

var head = mkFrame('head', {dir:'V', gap:6});
add(board, head, {hFill:true});
add(head, mkText('mySHIPR · Carrier Console — Prototype', {font:F.dispBold, size:27, lh:33, ls:0.2}), {hFill:true});
add(head, mkText('Every sidebar control on every screen is wired. Press the Present button and click through the rail.', {size:13, lh:19, color:C.ink2}), {hFill:true});

var stats = mkFrame('stats', {dir:'H', gap:14, wrap:true, crossGap:14});
add(board, stats, {hFill:true});
STAT.forEach(function(s){
  var card = mkFrame('stat', {dir:'H', gap:0, fill:C.panel, stroke:C.line, radius:10, clip:true});
  add(stats, card);
  fixW(card, 174);
  var edge = mkFrame('edge', {dir:'V', w:4, fill:s[2]});
  add(card, edge, {cV:'STRETCH'});
  var b = mkFrame('b', {dir:'V', gap:5, pad:[14,16,15,16]});
  add(card, b, {hFill:true});
  add(b, mkText(s[0], {font:F.semi, size:9.5, lh:13, ls:0.9, color:C.ink3, case:'UPPER'}), {hFill:true});
  add(b, mkText(s[1], {font:F.dispBold, size:23, lh:27}), {hFill:true});
});

var flow = mkFrame('flow', {dir:'V', gap:0, fill:C.panel, stroke:C.line, radius:10, clip:true});
add(board, flow, {hFill:true});
var fh = mkFrame('fh', {dir:'H', gap:10, pad:[12,16,12,16], align:'CENTER', stroke:C.line, sides:[0,0,1,0]});
add(flow, fh, {hFill:true});
add(fh, mkText('Flow map', {font:F.semi, size:12.5, lh:17}));
add(fh, mkText('start → 01 Dashboard · 42 screens · every screen reaches every other', {font:F.mono, size:10.5, lh:15, color:C.ink3}), {hFill:true});
var grid = mkFrame('grid', {dir:'H', gap:10, wrap:true, crossGap:10, pad:[14,16,16,16]});
add(flow, grid, {hFill:true});
CELLS.forEach(function(c){
  var cell = mkFrame('cell', {dir:'V', gap:3, pad:[9,11,10,11], fill: c.start ? C.greenBg : C.panel,
                              stroke: c.start ? C.green : C.line, radius:8, clip:true});
  add(grid, cell); fixW(cell, 226);
  add(cell, mkText(c.n, {font:F.semi, size:11, lh:15}), {hFill:true});
  add(cell, mkText((c.start ? 'FLOW START · ' : '') + c.i + ' interactions', {font:F.mono, size:9.5, lh:13, color:C.ink3}), {hFill:true});
});

NOTES.forEach(function(n){
  var box = mkFrame('note', {dir:'V', gap:4, pad:[13,16,14,16], fill:C.panel, stroke:C.line, radius:10, clip:true});
  add(board, box, {hFill:true});
  var bar = mkFrame('bar', {dir:'V', w:3, h:1, fill:C.blue});
  add(box, mkText(n[0], {font:F.semi, size:11.5, lh:16}), {hFill:true});
  add(box, mkText(n[1], {size:11, lh:16, color:C.ink2}), {hFill:true});
});
RESULT = { cells: CELLS.length, stats: STAT.length, notes: NOTES.length };
"""

# TODO: the Components and Variants counts below are the pre-component-pass figures
# (27 masters / 110 variants). A parallel pass is adding ~12 new components and
# rebuilding 7 existing ones. Refresh both cards from the live library once that
# pass lands, and re-run this generator.
STAT = [["Desktop screens","42",        "#157a4a"],
        ["Responsive frames","168",   "#2c66b0"],
        ["Overlay frames","20",       "#c9770a"],
        ["Sidebar interactions","2436","#6b4fa8"],
        ["Components","40",           "#e2a90b"],
        ["Variants","229",            "#2c66b0"],
        ["Paint styles","55",         "#157a4a"],
        ["Text styles","71",          "#6b4fa8"],
        ["Design tokens","76",        "#157a4a"],
        ["Motion tokens","8",         "#c9770a"],
        ["Bound nodes","16k+",        "#2c66b0"]]

NOTES = [
 ["Interaction — 2,436 wired controls, and motion that is spent, not sprinkled",
  "On desktop, every screen carries the 12 top-level nav items plus its section's sub-items and each one is wired: 756 links, of which 702 navigate and 54 are the control for the screen you are already on. On tablet and mobile the rail is off-canvas, so each of the 84 responsive frames has a Menu-open twin: the hamburger opens it, the scrim closes it, and its rail navigates within the same width — a further 1,680 links. The 54 Scroll-To links are the control for the screen you are already on — Figma rejects a navigation whose destination contains the trigger, so those use Scroll To and return the screen to its header, which is the standard active-item behaviour."],
 ["Coverage",
  "All 42 sub-screens of the console are built at 1440 — the 12 sidebar-level screens plus every sub-screen under Fleet (8), Drivers (3), Loads (6), Trips (5), Driver Ops (3), Earnings (2) and Settings (10). Content is taken from the console build, not re-typed: tables, chips, key/value blocks and empty states all carry their real records. Dashboard now carries all 9 panels the console has and Reports all 5. Each of the 42 also has a tablet (900) and a mobile (375) frame, each labelled, so the Responsive section holds 84 more — and below 480px a table is not a table at all: each row becomes a card carrying the record's identity, its status chip, its key fields and its actions, with the rest behind View details. A scrolling grid on a phone hides columns from a dispatcher checking a load one-handed, and they never learn they missed one."],
 ["The token layer — why a change in one place lands everywhere",
  "The 55 paint styles and 71 text styles on page 01 are not just a swatch chart: 7,168 fills and 9,015 text nodes across the component masters and the screen frames are actually bound to them. Select any of those nodes and the right-hand panel shows the style name where a raw hex used to be. Because the screens are assembled from instances of the masters, the chain runs style to master to instance: edit a paint style's value, or restyle a master, and every instance carrying it updates with it — no screen-by-screen repainting. The 34 colour values themselves are read 1:1 from the console's CSS :root, so the palette is the product's palette, not an approximation."],
 ["How the file is organised",
  "Page 01 holds the design tokens (55 colour, 7 radius, 14 spacing variables), the 55 paint styles and 71 text styles, and the component library — every screen is assembled from instances of those components, so changing a master updates all 42 frames. Page 02 holds the screens, split into Desktop (42 frames at 1440) and Responsive (84 frames — each screen at 900 and 375). Frame names carry the address: 12.10 Settings — Capacity is section 12, sub-screen 10."]]

js = (base + "\nconst CELLS = " + json.dumps(cells, ensure_ascii=False) + ";\n"
      + "const STAT = " + json.dumps(STAT, ensure_ascii=False) + ";\n"
      + "const NOTES = " + json.dumps(NOTES, ensure_ascii=False) + ";\n" + BOARD)
body = ("(async () => {\nvar RESULT = null, report = 'start';\ntry {\n" + js +
        "\n  report = 'DOC cells=' + RESULT.cells + ' stats=' + RESULT.stats + ' notes=' + RESULT.notes;\n"
        "} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 150); }\n"
        "try {\n  var p3 = null;\n  figma.root.children.forEach(function(p){ if (p.name.indexOf('03 Prototype') === 0) p3 = p; });\n"
        "  if (p3 && p3.children.length) p3.children[0].name = report;\n} catch (e) {}\nconsole.log(report);\n})();\n")
io.open(HERE + '/build-doc.js', 'w', encoding='utf-8').write(body)
print('build-doc.js  cells=%d  chars=%d' % (len(cells), len(body)))
