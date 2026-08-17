/* mySHIPR finishing pass — Scripter build */
(async () => {
try {
/* mySHIPR — Carrier Console : FINISHING PASS (run in Scripter)
 * A. hide leftover component-master placeholder text inside tables
 * B. add the .alert-eyebrow pill to the Banner master and show it on the compliance banners
 * C. build the "03 Prototype" flow-map / documentation board
 * Safe to re-run. */

const RESULT = { a: {}, b: {}, c: {} };

const hex = h => { const s = h.replace('#',''); return { r: parseInt(s.slice(0,2),16)/255, g: parseInt(s.slice(2,4),16)/255, b: parseInt(s.slice(4,6),16)/255 }; };
const paint = h => [{ type:'SOLID', color: hex(h) }];
const safe = fn => { try { return fn(); } catch (e) { return null; } };

const C = { chrome:'#0f141d', canvas:'#eef1f4', panel:'#ffffff', line:'#e0e5ea', line2:'#eef1f4',
  ink:'#141a24', ink2:'#586173', ink3:'#8b93a1', white:'#ffffff',
  green:'#157a4a', greenBg:'#e4f3ea', greenInk:'#0e5a37',
  amber:'#c9770a', amberBg:'#fbeede', amberInk:'#8f5405',
  red:'#c23b3b', redBg:'#f8e4e4', redInk:'#8f2626',
  blue:'#2c66b0', blueBg:'#e5eefa', blueInk:'#1e4c86', brand:'#157a4a', sign:'#e2a90b' };

const F = {};
async function loadFont(family, style) { try { await figma.loadFontAsync({ family, style }); return { family, style }; } catch (e) { return null; } }
async function pickFont(list, fallback) { for (const [fam, st] of list) { const f = await loadFont(fam, st); if (f) return f; } return fallback; }

F.body     = await pickFont([['Inter','Regular']], null);
F.medium   = await pickFont([['Inter','Medium']], F.body);
F.semi     = await pickFont([['Inter','Semi Bold'],['Inter','SemiBold']], F.medium);
F.bold     = await pickFont([['Inter','Bold']], F.semi);
F.dispSemi = await pickFont([['Barlow Semi Condensed','SemiBold'],['Barlow Semi Condensed','Semi Bold']], F.semi);
F.dispBold = await pickFont([['Barlow Semi Condensed','Bold']], F.bold);
F.mono     = await pickFont([['IBM Plex Mono','Regular']], F.body);
F.monoSemi = await pickFont([['IBM Plex Mono','SemiBold'],['IBM Plex Mono','Semi Bold']], F.mono);

function frame(name, o) {
  o = o || {};
  const n = figma.createFrame();
  n.name = name;
  n.layoutMode = o.dir === 'H' ? 'HORIZONTAL' : (o.dir === 'N' ? 'NONE' : 'VERTICAL');
  if (n.layoutMode !== 'NONE') {
    n.primaryAxisSizingMode = 'AUTO'; n.counterAxisSizingMode = 'AUTO';
    n.itemSpacing = o.gap || 0;
    let p = o.pad == null ? 0 : o.pad; if (typeof p === 'number') p = [p,p,p,p];
    n.paddingTop = p[0]; n.paddingRight = p[1]; n.paddingBottom = p[2]; n.paddingLeft = p[3];
    if (o.align) n.counterAxisAlignItems = o.align;
    if (o.just) n.primaryAxisAlignItems = o.just;
    if (o.wrap) { n.layoutWrap = 'WRAP'; if (o.crossGap != null) n.counterAxisSpacing = o.crossGap; }
  }
  n.fills = o.fill ? paint(o.fill) : [];
  if (o.stroke) { n.strokes = paint(o.stroke); n.strokeAlign = 'INSIDE'; } else n.strokes = [];
  if (o.radius != null) n.cornerRadius = o.radius;
  n.clipsContent = !!o.clip;
  if (o.w || o.h) n.resize(o.w || n.width, o.h || Math.max(1, n.height));
  if (o.w && n.layoutMode === 'VERTICAL') n.counterAxisSizingMode = 'FIXED';
  if (o.w && n.layoutMode === 'HORIZONTAL') n.primaryAxisSizingMode = 'FIXED';
  return n;
}
function text(s, o) {
  o = o || {};
  const t = figma.createText();
  t.fontName = o.font || F.body;
  t.characters = String(s == null ? '' : s);
  t.fontSize = o.size || 14;
  t.lineHeight = o.lh ? { value: o.lh, unit:'PIXELS' } : { value:145, unit:'PERCENT' };
  if (o.ls != null) t.letterSpacing = { value: o.ls, unit:'PIXELS' };
  t.fills = paint(o.color || C.ink);
  if (o.case) t.textCase = o.case;
  t.textAutoResize = 'WIDTH_AND_HEIGHT';
  t.name = o.name || 'text';
  return t;
}
function add(parent, child, o) {
  parent.appendChild(child); o = o || {};
  if (parent.layoutMode && parent.layoutMode !== 'NONE') {
    if (o.hFill) safe(() => { child.layoutSizingHorizontal = 'FILL'; });
    else if (o.hFix != null) safe(() => { child.layoutSizingHorizontal = 'FIXED'; child.resize(o.hFix, Math.max(1, child.height)); });
  } else { if (o.x != null) child.x = o.x; if (o.y != null) child.y = o.y; }
  return child;
}

const pageDS  = figma.root.children.filter(p => p.name === '01 Design System')[0];
const pageSC  = figma.root.children.filter(p => p.name === '02 Screens')[0];
const pagePR  = figma.root.children.filter(p => p.name === '03 Prototype')[0];
if (!pageDS || !pageSC || !pagePR) throw new Error('Expected pages 01/02/03 — run the earlier chunks first.');

/* ---------------------------------------------------------- A. placeholders */
await figma.setCurrentPageAsync(pageSC);
const screenFrames = [];
for (const sec of pageSC.children.filter(n => n.type === 'SECTION'))
  for (const fr of sec.children.filter(n => n.type === 'FRAME')) screenFrames.push(fr);

const PLACEHOLDER = ['Cell', 'sub', 'COLUMN', 'sub2'];
let hidden = 0;
for (const fr of screenFrames) {
  for (const t of fr.findAll(n => n.type === 'TEXT' && n.visible && PLACEHOLDER.indexOf(n.characters) >= 0)) {
    let p = t.parent, inTable = false;
    for (let i = 0; i < 4 && p; i++) { if (p.name === 'Table/Row' || p.name === 'Table/Header') { inTable = true; break; } p = p.parent; }
    if (!inTable) continue;
    if (safe(() => { t.visible = false; return true; })) hidden++;
  }
}
let leftover = 0;
for (const fr of screenFrames) leftover += fr.findAll(n => n.type === 'TEXT' && n.visible && PLACEHOLDER.indexOf(n.characters) >= 0).length;
RESULT.a = { hidden, leftover };

/* ------------------------------------------------- B. alert-eyebrow on Banner */
await figma.setCurrentPageAsync(pageDS);
const bannerSet = pageDS.findAll(n => n.type === 'COMPONENT_SET' && n.name === 'Banner')[0];
let eyebrowsAdded = 0;
if (bannerSet) {
  for (const variant of bannerSet.children) {
    var nm = String(variant.name); var ti = nm.indexOf('tone='); var tone = 'info';
    if (ti >= 0) { var rest = nm.substring(ti + 5); var cut = rest.indexOf(','); tone = (cut >= 0 ? rest.substring(0, cut) : rest).trim(); }
    const col = tone === 'crit' ? { bg: C.red, fg: '#ffffff' }
              : tone === 'warn' ? { bg: C.amber, fg: '#ffffff' }
              : tone === 'ok'   ? { bg: C.green, fg: '#ffffff' }
                                : { bg: C.blue, fg: '#ffffff' };
    // the text column inside the banner is the frame named "b"
    const body = variant.findOne ? variant.findOne(n => n.type === 'FRAME' && n.name === 'b') : null;
    if (!body) continue;
    if (body.children.some(c => c.name === 'alert-eyebrow')) continue;
    const pill = frame('alert-eyebrow', { dir:'H', gap:4, pad:[2,8,2,6], radius:20, fill: col.bg, align:'CENTER' });
    add(pill, text('⚠ COMPLIANCE ALERT · ACTION REQUIRED', { font: F.monoSemi, size:9.5, lh:13, ls:1.14, color: col.fg, case:'UPPER', name:'eyebrow' }));
    body.insertChild(0, pill);
    pill.visible = false;               // opt-in per instance
    eyebrowsAdded++;
  }
}
// switch it on for the compliance banners that carry it in the HTML
await figma.setCurrentPageAsync(pageSC);
let eyebrowsShown = 0;
for (const fr of screenFrames) {
  for (const inst of fr.findAll(n => n.type === 'INSTANCE' && n.name === 'Banner')) {
    const title = inst.findAll(n => n.type === 'TEXT' && n.name === 'title')[0];
    if (!title) continue;
    if (String(title.characters).toLowerCase().indexOf('compliance document outstanding') >= 0) {
      const eb = inst.findAll(n => n.name === 'alert-eyebrow')[0];
      if (eb && safe(() => { eb.visible = true; return true; })) eyebrowsShown++;
    }
  }
}
RESULT.b = { eyebrowsAddedToMaster: eyebrowsAdded, eyebrowsShownOnScreens: eyebrowsShown };

/* ----------------------------------------------------- C. 03 Prototype board */
await figma.setCurrentPageAsync(pagePR);
pagePR.children.slice().forEach(n => safe(() => n.remove()));

const board = frame('Prototype — flow & coverage', { dir:'V', gap:34, pad:56, fill: C.canvas, w:1600 });
pagePR.appendChild(board); board.x = 0; board.y = 0;

const head = frame('head', { dir:'V', gap:6 });
add(board, head, { hFill:true });
add(head, text('mySHIPR · Carrier Console — Prototype', { font: F.dispBold, size:34, lh:38, ls:.3 }), { hFill:true });
add(head, text('Every sidebar item on every screen navigates to that screen. Press ▶ Present and click through the rail.', { size:13, lh:19, color: C.ink2 }), { hFill:true });

// stat strip
const stats = frame('stats', { dir:'H', gap:16, wrap:true, crossGap:16 });
add(board, stats, { hFill:true });
[['12','Desktop screens', C.brand], ['6','Responsive frames', C.blue], ['132','Navigation links', C.green],
 ['27','Components', C.sign], ['110','Variants', C.blue], ['55','Design tokens', C.brand]]
 .forEach(([n, l, col]) => {
  const card = frame('stat', { dir:'H', gap:0, fill: C.panel, stroke: C.line, radius:10, clip:true, w:238 });
  add(card, frame('edge', { dir:'V', w:4, h:76, fill: col }));
  const b = frame('b', { dir:'V', gap:4, pad:[14,15,14,15] });
  add(card, b, { hFill:true });
  add(b, text(l.toUpperCase(), { font: F.semi, size:10.5, lh:14, ls:1.05, color: C.ink3 }), { hFill:true });
  add(b, text(n, { font: F.dispBold, size:30, lh:32, ls:.3 }));
  add(stats, card);
});

// flow map
const SCREENS = ['01 Dashboard — Overview','02 Fleet — All Vehicles','03 Drivers — All Drivers','04 Loads — Tenders',
  '05 Trips — On going','06 Driver Ops — Detention','07 RR — Coming soon','08 Yards — All yards',
  '09 Notifications','10 Reports — Operations','11 Earnings — Earnings','12 Settings — My Profile'];

const flowWrap = frame('flow', { dir:'V', gap:0, fill: C.panel, stroke: C.line, radius:10, clip:true });
add(board, flowWrap, { hFill:true });
const flowHd = frame('hd', { dir:'H', gap:10, pad:[13,16,13,16], stroke: C.line, align:'CENTER' });
add(flowWrap, flowHd, { hFill:true });
add(flowHd, text('Flow map', { font: F.dispSemi, size:15, lh:20, ls:.2 }));
add(flowHd, text('start → 01 Dashboard · every node reachable from every other node', { size:11, lh:15, color: C.ink3 }));

const grid = frame('grid', { dir:'H', gap:12, wrap:true, crossGap:12, pad:[16,16,18,16] });
add(flowWrap, grid, { hFill:true });
SCREENS.forEach((s, i) => {
  const isStart = i === 0;
  const node = frame('node', { dir:'V', gap:4, pad:[12,14,12,14], radius:8,
    fill: isStart ? C.greenBg : C.panel, stroke: isStart ? C.green : C.line, w:236 });
  add(node, text(s.substring(s.indexOf(' ') + 1), { font: F.semi, size:12.5, lh:17, color: isStart ? C.greenInk : C.ink }), { hFill:true });
  add(node, text(isStart ? 'FLOW START · 11 outgoing links' : '11 outgoing links', { font: F.mono, size:10, lh:14, color: C.ink3 }), { hFill:true });
  add(grid, node);
});

// notes
const notes = frame('notes', { dir:'V', gap:10 });
add(board, notes, { hFill:true });
[['Why 132 links and not 144',
  'Each screen has 12 sidebar items, but the item pointing at the screen you are already on cannot be wired — Figma rejects a navigation whose destination is the frame containing the trigger ("destination node may not be an ancestor"). That is also the correct behaviour: clicking the current page in the rail should do nothing. 12 screens × 11 reachable destinations = 132.'],
 ['Scope of this round',
  'The console has 42 sub-screens in total. This file covers the 12 sidebar-level screens agreed for this round; the sub-screens under Fleet, Loads and Settings are a later iteration.'],
 ['How the file is organised',
  'Page 01 holds the tokens and the component library — every screen is assembled from instances of those components, so changing a master updates all 18 frames. Page 02 holds the screens, split into Desktop (1440) and Responsive (900 / 375) sections.']]
 .forEach(([t, b]) => {
  const n = frame('note', { dir:'H', gap:0, radius:7, clip:true, stroke: C.line });
  add(notes, n, { hFill:true });
  add(n, frame('edge', { dir:'V', w:3, h:60, fill: C.blue }));
  const bb = frame('b', { dir:'V', gap:3, pad:[12,14,13,14], fill:'#f7f9fb' });
  add(n, bb, { hFill:true });
  add(bb, text(t, { font: F.semi, size:12.5, lh:17 }), { hFill:true });
  add(bb, text(b, { size:12, lh:18, color: C.ink2 }), { hFill:true });
});

safe(() => { board.resize(1600, Math.max(600, board.height)); });
RESULT.c = { boardCreated: true, nodes: board.findAll(() => true).length, screensListed: SCREENS.length };

console.log('DONE ' + JSON.stringify(RESULT));

} catch (err) { console.log('FAILED: ' + (err && err.message ? err.message : String(err))); }
})();
