'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { slice } = require('./slice.js');

const SRC = '/home/ujjwal/Documents/J.A.R.V.I.S./figma-build/plugin';
const OUT = '/home/ujjwal/Documents/J.A.R.V.I.S./figma-build/use-figma';
fs.mkdirSync(OUT, { recursive: true });

const p3 = slice(path.join(SRC, 'part3-responsive-prototype.js'));
const by3 = {}; p3.forEach(d => { by3[d.name] = d.text; });

const p1lines = fs.readFileSync(path.join(SRC, 'part1-foundations-components.js'), 'utf8').split('\n');
const p1 = (a, b) => p1lines.slice(a - 1, b).join('\n');

/* ---------- source pieces ---------- */
const TOKENS = ['C', 'COLOR_TOKENS', 'RADIUS_TOKENS', 'SPACE_TOKENS', 'TONE', 'KPI_EDGE', 'BANNER',
  'SIDE_W', 'F', 'COMP', 'P', 'VARS', 'LIB'];
const CORE = ['tryFont', 'pickFont', 'loadFonts', 'rgb', 'solid', 'safe', 'mkFrame', 'mkText', 'add',
  'fixW', 'fillW', 'hide', 'show', 'svgIcon', 'I'];
const COMPHELP = ['toComp', 'cross', 'makeSet', 'makeComp', 'variantOf', 'inst', 'setText', 'setChip',
  'setBtn', 'setIcon', 'collectComponents', 'REQUIRED_COMPONENTS', 'findPage'];
const SHELL = ['NAV', 'orgCard', 'buildSidebarNode', 'tbtn', 'buildTopBarNode'];
const RENDER = ['contentWidth', 'colWidths', 'setBar', 'fillRow', 'renderTable', 'renderPanel',
  'renderBlocks', 'renderScreen'];
const DATA = ['CHK', 'SCREENS'];
const PROTO = ['navReaction', 'setReact'];

const grab = (names) => names.map(n => {
  if (!by3[n]) throw new Error('missing slice: ' + n);
  return by3[n];
}).join('\n');

/* part 1 exclusives */
const P1_CLEANUP = p1(246, 253);
const P1_MKVAR = p1(255, 261);
const P1_BUILDTOKENS = p1(262, 294);
let P1_FOUNDATIONS = p1(297, 375);
let P1_COMPONENTS = p1(665, 1109);

/* ---------- patches ---------- */
function must(src, find, repl, label) {
  if (src.indexOf(find) < 0) throw new Error('PATCH FAILED (' + label + '): pattern not found');
  return src.split(find).join(repl);
}

// buildFoundations -> render into the Foundations SECTION
P1_FOUNDATIONS = must(P1_FOUNDATIONS,
  `  const page = P['01 Foundations'];\n  const board = mkFrame('Foundations', {dir:'V', gap:40, pad:56, fill:C.canvas, w:1440});\n  add(page, board); board.x = 0; board.y = 0;`,
  `  const board = mkFrame('Foundations', {dir:'V', gap:40, pad:56, fill:C.canvas, w:1440});\n  placeInSection(SEC_FOUNDATIONS, board, 80, 80);`,
  'foundations-board');

// buildComponents -> render into the Components SECTION, reusing the board across batches
P1_COMPONENTS = must(P1_COMPONENTS,
  `  const page = P['02 Components'];\n  const lib = LIB = mkFrame('Component library', {dir:'V', gap:44, pad:56, fill:C.canvas, w:1680});\n  add(page, lib); lib.x = 0; lib.y = 0;\n  add(lib, mkText('mySHIPR · Carrier Console — Components', {font:F.dispBold, size:34, lh:38, ls:0.3}));\n  add(lib, mkText('Every screen on pages 03 and 04 is assembled from instances of the sets below. Auto Layout + constraints throughout.',\n      {size:13, lh:19, color:C.ink2}));`,
  `  let lib = SEC_COMPONENTS.children.filter(n => n.name === 'Component library')[0] || null;
  if (!lib){
    lib = mkFrame('Component library', {dir:'V', gap:44, pad:56, fill:C.canvas, w:1680});
    placeInSection(SEC_COMPONENTS, lib, 80, 80);
    add(lib, mkText('mySHIPR · Carrier Console — Components', {font:F.dispBold, size:34, lh:38, ls:0.3}));
    add(lib, mkText('Every screen on page "02 Screens" is assembled from instances of the sets below. Auto Layout + constraints throughout.',
        {size:13, lh:19, color:C.ink2}));
  }
  LIB = lib;`,
  'components-board');

P1_COMPONENTS = must(P1_COMPONENTS,
  `  function sect(title, sub){\n    const s = mkFrame(title, {dir:'V', gap:14});`,
  `  function sect(title, sub){
    const ex = lib.children.filter(n => n.name === title)[0];
    if (ex){ const h = ex.children.filter(n => n.name === 'items')[0]; if (h) return h; }
    const s = mkFrame(title, {dir:'V', gap:14});`,
  'components-sect');

/* gate makeSet / makeComp on the ONLY allow-list so components ship in batches */
let COMPHELP_SRC = grab(COMPHELP);
COMPHELP_SRC = must(COMPHELP_SRC,
  `function makeSet(name, dims, build, parent){`,
  `function makeSet(name, dims, build, parent){\n  if (ONLY && ONLY.indexOf(name) < 0) return COMP[name] || null;`,
  'gate-makeSet');
COMPHELP_SRC = must(COMPHELP_SRC,
  `function makeComp(name, build, parent){`,
  `function makeComp(name, build, parent){\n  if (ONLY && ONLY.indexOf(name) < 0) return COMP[name] || null;`,
  'gate-makeComp');

/* ---------- the port shim ---------- */
const SHIM = `
/* ===================== use_figma PORT SHIM =====================
 * 3 pages already exist (Starter cap). We organise with Sections.
 *   01 Design System 0:1   -> sections Foundations | Components
 *   02 Screens       3:2   -> sections Desktop     | Responsive
 *   03 Prototype     3:3   -> section  Flow map
 * Page creation, toast notifications and stdout logging are all avoided here:
 * they either throw on this plan or are unavailable in this runtime.
 * ============================================================== */
const LOGS = [];
const LOGC = {
  log: function(){ LOGS.push(Array.prototype.slice.call(arguments).map(String).join(' ')); },
  error: function(){ LOGS.push('ERR ' + Array.prototype.slice.call(arguments).map(String).join(' ')); },
  warn: function(){ LOGS.push('WARN ' + Array.prototype.slice.call(arguments).map(String).join(' ')); }
};
const PAGE = { ds:'0:1', screens:'3:2', proto:'3:3' };
let ONLY = null;
let SEC_FOUNDATIONS = null, SEC_COMPONENTS = null;

async function getPage(id){
  const p = await figma.getNodeByIdAsync(id);
  if (!p || p.type !== 'PAGE') throw new Error('page ' + id + ' not found (expected 0:1 / 3:2 / 3:3)');
  if (p.loadAsync) await p.loadAsync();
  return p;
}
function findSection(page, name){
  return page.children.filter(function(n){ return n.type === 'SECTION' && n.name === name; })[0] || null;
}
function makeSection(page, name, x, y){
  const s = figma.createSection();
  s.name = name;
  page.appendChild(s);
  s.x = x; s.y = y;
  safe(function(){ s.resizeWithoutConstraints(1600, 1000); });
  safe(function(){ s.fills = solid('#e4e9ef'); });
  return s;
}
/* replace-not-duplicate: wipe a section we own, then recreate it in place */
function resetSection(page, name, x, y){
  const old = findSection(page, name);
  if (old) safe(function(){ old.remove(); });
  return makeSection(page, name, x, y);
}
function getOrMakeSection(page, name, x, y){
  return findSection(page, name) || makeSection(page, name, x, y);
}
/* Section child coordinates: the API is ambiguous about whether x/y on a SECTION
 * child are section-relative or page-absolute. placeInSection sets the position and
 * then self-corrects using absoluteBoundingBox, so it lands correctly either way. */
function placeInSection(sec, node, rx, ry){
  sec.appendChild(node);
  node.x = rx; node.y = ry;
  safe(function(){
    const sb = sec.absoluteBoundingBox, nb = node.absoluteBoundingBox;
    if (!sb || !nb) return;
    const dx = (sb.x + rx) - nb.x, dy = (sb.y + ry) - nb.y;
    if (Math.abs(dx) > 0.5 || Math.abs(dy) > 0.5){ node.x = rx + dx; node.y = ry + dy; }
  });
  return node;
}
/* sections do not auto-grow via the API — size them to their contents */
function fitSection(sec, pad){
  if (!sec) return null;
  pad = (pad == null) ? 80 : pad;
  const kids = sec.children;
  if (!kids.length) return sec;
  let maxX = 0, maxY = 0;
  const sb = sec.absoluteBoundingBox;
  kids.forEach(function(k){
    const nb = k.absoluteBoundingBox;
    if (sb && nb){
      maxX = Math.max(maxX, (nb.x - sb.x) + nb.width);
      maxY = Math.max(maxY, (nb.y - sb.y) + nb.height);
    } else {
      maxX = Math.max(maxX, k.x + k.width);
      maxY = Math.max(maxY, k.y + k.height);
    }
  });
  safe(function(){ sec.resizeWithoutConstraints(Math.max(400, maxX + pad), Math.max(300, maxY + pad)); });
  return sec;
}
/* components all live on page "01 Design System" now */
async function adoptComponents(strict){
  const pg = await getPage(PAGE.ds);
  const map = collectComponents(pg);
  const missing = REQUIRED_COMPONENTS.filter(function(n){ return !map[n]; });
  if (missing.length && strict !== false){
    throw new Error('Run the earlier component batches first — missing on "01 Design System": ' + missing.join(', '));
  }
  Object.keys(map).forEach(function(n){ COMP[n] = map[n]; });
  return { adopted: Object.keys(COMP).length, missing: missing };
}
function sectionReport(sec){
  if (!sec) return null;
  const all = sec.findAll(function(){ return true; });
  const cnt = function(t){ return all.filter(function(n){ return n.type === t; }).length; };
  return {
    section: sec.name,
    size: Math.round(sec.width) + 'x' + Math.round(sec.height),
    topLevel: sec.children.length,
    frames: cnt('FRAME'), text: cnt('TEXT'), instances: cnt('INSTANCE'),
    componentSets: cnt('COMPONENT_SET'),
    components: all.filter(function(n){ return n.type === 'COMPONENT' && !(n.parent && n.parent.type === 'COMPONENT_SET'); }).length,
    variants: all.filter(function(n){ return n.type === 'COMPONENT' && n.parent && n.parent.type === 'COMPONENT_SET'; }).length
  };
}
/* ================== END PORT SHIM ================== */
`;

/* ---------- prelude assembly ---------- */
function clean(src) {
  return src
    .replace(/console\.log\(/g, 'LOGC.log(')
    .replace(/console\.error\(/g, 'LOGC.error(')
    .replace(/console\.warn\(/g, 'LOGC.warn(')
    .replace(/^.*figma\.notify\(.*$/gm, '')
    .replace(/[ \t]+$/gm, '');
}

const PRE_LITE = clean([grab(TOKENS), grab(CORE)].join('\n'));
const PRE_COMP = clean([grab(TOKENS), grab(CORE), COMPHELP_SRC, grab(SHELL)].join('\n'));
const PRE_FULL = clean([grab(TOKENS), grab(CORE), COMPHELP_SRC, grab(SHELL), grab(RENDER), grab(DATA)].join('\n'));

/* ---------- SCREEN metadata (so the prototype chunks don't need the 486-line data block) ---------- */
function screenMeta() {
  const sim = require('./figma-sim.js');
  const ctx = vm.createContext({
    figma: sim.figma, console: { log() { }, error() { }, warn() { } },
    Promise, Symbol, Math, JSON, Object, Array, String, Number, Boolean, Error, RegExp, Date, Set, Map,
    setTimeout, parseInt, parseFloat, isNaN,
  });
  const code = [grab(TOKENS), grab(CORE), grab(DATA),
    'SCREENS.map(function(s){ return {key:s.key, frame:s.frame, nav:s.nav, sub:s.sub}; })'].join('\n');
  return vm.runInContext(code, ctx);
}
const META = screenMeta();
const META_SRC = 'const SCREEN_META = ' + JSON.stringify(META, null, 1) + ';';

/* ---------- chunk bodies ---------- */
const CH = [];
const add_ = (file, prelude, body, note) => CH.push({ file, prelude, body, note });

add_('01-foundations.js', PRE_LITE, `
${P1_CLEANUP}
${P1_MKVAR}
${clean(P1_BUILDTOKENS)}
${clean(P1_FOUNDATIONS)}

/* ---- run ---- */
await loadFonts();
await cleanupStyles();
const pg = await getPage(PAGE.ds);
await figma.setCurrentPageAsync(pg);
SEC_FOUNDATIONS = resetSection(pg, 'Foundations', 0, 0);
await buildTokens();
buildFoundations();
fitSection(SEC_FOUNDATIONS, 80);
return {
  ok: true,
  page: pg.name + ' (' + pg.id + ')',
  fonts: Object.keys(F).map(function(k){ return k + '=' + F[k].family + '/' + F[k].style; }),
  variableCollections: (await figma.variables.getLocalVariableCollectionsAsync()).map(function(c){ return c.name + ':' + c.variableIds.length; }),
  paintStyles: (await figma.getLocalPaintStylesAsync()).length,
  textStyles: (await figma.getLocalTextStylesAsync()).map(function(s){ return s.name; }),
  foundations: sectionReport(SEC_FOUNDATIONS),
  log: LOGS
};`, 'variables + paint styles + 7 text styles + specimen board');

const BATCHES = [
  ['02-components-a.js', ['Icon', 'Sidebar/Item', 'Sidebar/SubItem', 'Button', 'Chip/Status', 'Chip/Filter', 'Legend Chip'], true],
  ['03-components-b.js', ['KPI Card', 'Pulse Cell', 'HOS Bar', 'Bar Row', 'Panel', 'Table/Header', 'Table/Row', 'Pager'], false],
  ['04-components-c.js', ['Banner', 'Note', 'EmptyState', 'Toast', 'Field', 'List Item', 'Stop Line', 'KV Row', 'Lane', 'TopBar', 'Sidebar/Root', 'Drawer'], false],
];
BATCHES.forEach(([file, only, first]) => {
  add_(file, PRE_COMP, `
${clean(P1_COMPONENTS)}

/* ---- run ---- */
await loadFonts();
const pg = await getPage(PAGE.ds);
await figma.setCurrentPageAsync(pg);
SEC_COMPONENTS = ${first ? `resetSection(pg, 'Components', 1760, 0)` : `getOrMakeSection(pg, 'Components', 1760, 0)`};
const adopted = await adoptComponents(false);
ONLY = ${JSON.stringify(only)};
buildComponents();
fitSection(SEC_COMPONENTS, 80);
const built = ONLY.filter(function(n){ return !!COMP[n]; });
return {
  ok: built.length === ONLY.length,
  batch: ${JSON.stringify(file)},
  requested: ONLY,
  built: built,
  failed: ONLY.filter(function(n){ return !COMP[n]; }),
  previouslyPresent: adopted.adopted,
  components: sectionReport(SEC_COMPONENTS),
  log: LOGS
};`, 'component batch: ' + only.join(', '));
});

const GROUPS = [[0, 4, '05-screens-01-04.js', true], [4, 8, '06-screens-05-08.js', false], [8, 12, '07-screens-09-12.js', false]];
GROUPS.forEach(([a, b, file, first]) => {
  add_(file, PRE_FULL, `
/* ---- run ---- */
await loadFonts();
await adoptComponents(true);
const pg = await getPage(PAGE.screens);
await figma.setCurrentPageAsync(pg);
const sec = ${first ? `resetSection(pg, 'Desktop', 0, 0)` : `getOrMakeSection(pg, 'Desktop', 0, 0)`};
const made = [];
for (let i = ${a}; i < ${b}; i++){
  const spec = SCREENS[i];
  const r = renderScreen(spec, 'desktop');
  placeInSection(sec, r.frame, 80 + i * (DESK_W + 120), 80);
  made.push({ n: i + 1, name: r.frame.name, w: Math.round(r.frame.width), h: Math.round(r.frame.height),
              navItems: Object.keys(r.items || {}).length,
              instances: r.frame.findAll(function(n){ return n.type === 'INSTANCE'; }).length });
}
fitSection(sec, 80);
return {
  ok: made.length === ${b - a},
  page: pg.name,
  screens: made,
  desktopSection: sectionReport(sec),
  log: LOGS
};`, 'desktop screens ' + (a + 1) + '-' + b);
});

add_('08-responsive.js', PRE_FULL, `
${grab(['RESPONSIVE_KEYS'])}

/* ---- run ---- */
await loadFonts();
await adoptComponents(true);
const pg = await getPage(PAGE.screens);
await figma.setCurrentPageAsync(pg);
const sec = resetSection(pg, 'Responsive', 0, 2400);
const made = [];
let x = 80;
for (const key of RESPONSIVE_KEYS){
  const spec = SCREENS.filter(function(s){ return s.key === key; })[0];
  if (!spec){ LOGC.error('no screen spec for ' + key); continue; }
  const lbl = mkText(spec.frame.replace(/^\\d+\\s/, ''), {font:F.dispBold, size:22, lh:26, color:C.ink});
  placeInSection(sec, lbl, x, 30);
  const t = renderScreen(spec, 'tablet');
  placeInSection(sec, t.frame, x, 80);
  const m = renderScreen(spec, 'mobile');
  placeInSection(sec, m.frame, x + TAB_W + 60, 80);
  made.push({ screen: spec.frame,
              tablet: Math.round(t.frame.width) + 'x' + Math.round(t.frame.height),
              mobile: Math.round(m.frame.width) + 'x' + Math.round(m.frame.height) });
  x += TAB_W + 60 + MOB_W + 160;
}
fitSection(sec, 80);
return {
  ok: made.length === 3 && made.every(function(r){ return r.tablet.indexOf('900x') === 0 && r.mobile.indexOf('375x') === 0; }),
  responsive: made,
  responsiveSection: sectionReport(sec),
  log: LOGS
};`, 'tablet 900 + mobile 375 for Dashboard / Fleet / Detention');

add_('09-prototype-wire.js', PRE_LITE, `
${META_SRC}
${clean(grab(PROTO))}

/* ---- run ---- */
const pg = await getPage(PAGE.screens);
const sec = findSection(pg, 'Desktop');
if (!sec) throw new Error('Section "Desktop" not found on page "02 Screens" — run the screen chunks first.');
const byName = {};
sec.children.forEach(function(f){ byName[f.name] = f; });
const dest = {};
SCREEN_META.forEach(function(s){ if (byName[s.frame]) dest[s.key] = byName[s.frame]; });
const missingFrames = SCREEN_META.filter(function(s){ return !byName[s.frame]; }).map(function(s){ return s.frame; });

let wired = 0, failed = 0;
const perFrame = [];
for (const s of SCREEN_META){
  const frame = byName[s.frame];
  if (!frame) continue;
  const items = frame.findAll(function(n){ return typeof n.name === 'string' && n.name.indexOf('nav/') === 0; });
  let n = 0;
  for (const it of items){
    const target = dest[it.name.slice(4)];
    if (!target) continue;
    const ok = await setReact(it, navReaction(target.id));
    if (ok){ wired++; n++; } else failed++;
  }
  perFrame.push(s.frame + ' -> ' + n);
}
const first = byName[SCREEN_META[0].frame];
if (first) safe(function(){ pg.flowStartingPoints = [{ nodeId: first.id, name: 'Carrier Console — Dashboard' }]; });
return {
  ok: wired === 144 && failed === 0 && missingFrames.length === 0,
  wired: wired, failed: failed, expected: 144,
  missingFrames: missingFrames,
  perFrame: perFrame,
  flowStart: first ? first.name : null,
  log: LOGS
};`, '12 sidebar items x 12 frames = 144 ON_CLICK -> NAVIGATE');

add_('10-prototype-doc.js', PRE_COMP, `
${META_SRC}

/* ---- run ---- */
await loadFonts();
await adoptComponents(true);
const pgS = await getPage(PAGE.screens);
const deskSec = findSection(pgS, 'Desktop');
const navNodes = deskSec ? deskSec.findAll(function(n){
  return typeof n.name === 'string' && n.name.indexOf('nav/') === 0;
}) : [];
const reactionCount = navNodes.filter(function(n){ return n.reactions && n.reactions.length; }).length;
const pg = await getPage(PAGE.proto);
await figma.setCurrentPageAsync(pg);
const sec = resetSection(pg, 'Flow map', 0, 0);

const board = mkFrame('Prototype — navigation map', {dir:'V', gap:28, pad:56, fill:C.canvas, w:1200});
placeInSection(sec, board, 80, 80);
add(board, mkText('Prototype — navigation map', {font:F.dispBold, size:34, lh:38, ls:0.3}), {hFill:true});
add(board, mkText('Wiring lives on page "02 Screens", section "Desktop". Every one of the 12 sidebar items on every one of the 12 desktop frames is an ON_CLICK to NAVIGATE to the matching frame, transition Instant, so the rail behaves like the real console from any starting screen. Flow starting point: 01 Dashboard — Overview.',
  {size:14, lh:21, color:C.ink2}), {hFill:true});

const stat = mkFrame('stats', {dir:'H', gap:16, wrap:true, crossGap:16});
add(board, stat, {hFill:true});
[['Frames wired','12','desktop screens','default'],
 ['Reactions', String(reactionCount), 'ON_CLICK to NAVIGATE','blue'],
 ['Per frame','12','one per sidebar item','grey'],
 ['Transition','Instant','no animation','grey']].forEach(function(k){
  const c = inst('KPI Card', {tone:k[3]});
  add(stat, c, {hFix:270});
  setText(c, 'label', k[0]); setText(c, 'value', k[1]); setText(c, 'sub', k[2]);
  const sm = c.findOne(function(n){ return n.type === 'TEXT' && n.name === 'value-small'; }); if (sm) sm.visible = false;
});

const card = mkFrame('map', {dir:'V', gap:0, fill:C.panel, stroke:C.line, radius:10, clip:true});
add(board, card, {hFill:true});
const hd = inst('Panel', {header:'title+hint'});
add(card, hd, {hFill:true});
setText(hd, 'title', 'Sidebar item to destination frame');
setText(hd, 'hint', '12 x 12 = 144 links');
const box = mkFrame('rows', {dir:'V', gap:0});
add(card, box, {hFill:true});
SCREEN_META.forEach(function(s, i){
  const r = mkFrame('r', {dir:'H', gap:14, align:'CENTER', pad:[10,16,10,16],
    stroke: i < SCREEN_META.length - 1 ? C.line2 : null, sides:[0,0,1,0]});
  add(box, r, {hFill:true});
  add(r, mkText('nav/' + s.key, {font:F.mono, size:11.5, lh:16, color:C.brand}), {hFix:170});
  add(r, svgIcon(I.arrow, 14, C.ink3, 1.6));
  add(r, mkText(s.frame, {font:F.medium, size:12.5, lh:17}), {hFill:true});
  add(r, mkText(s.nav + ' / ' + s.sub, {size:11.5, lh:16, color:C.ink3}));
});
const n = inst('Note', {tone:'blue'});
add(board, n, {hFill:true});
setText(n, 'body', 'Agreed scope: only the sidebar is wired. In-screen controls (filter chips, table rows, pagers, drawer triggers) are documented as component states on page "01 Design System" but are deliberately not prototyped.');
fitSection(sec, 80);
return {
  ok: true,
  page: pg.name + ' (' + pg.id + ')',
  reactionsFoundOnDesktop: reactionCount,
  flowMap: sectionReport(sec),
  log: LOGS
};`, 'readable flow map / wiring documentation on page 03');

/* ---------- emit ---------- */
const HEAD = (note, file) => `/* mySHIPR Carrier Console — use_figma chunk: ${file}
 * ${note}
 * fileKey ktu4OlSs8rCXEqsgHzVFVg
 * Paste as the \`code\` argument of use_figma (skillNames: "resource:figma-use").
 * The runner auto-wraps this in an async IIFE, so top-level await + return work.
 * Run the chunks in filename order. Each one is safe to re-run.
 */
`;

const manifest = [];
CH.forEach(c => {
  const src = HEAD(c.note, c.file) + c.prelude + '\n' + SHIM + '\n' + c.body + '\n';
  fs.writeFileSync(path.join(OUT, c.file), src);
  manifest.push({ file: c.file, bytes: src.length, lines: src.split('\n').length, note: c.note });
});
console.log(manifest.map(m => `${m.file.padEnd(26)} ${String(m.lines).padStart(5)} lines  ${(m.bytes / 1024).toFixed(1).padStart(6)} KB  ${m.note}`).join('\n'));
console.log('\nSCREEN_META frames:\n' + META.map(m => ' ' + m.key.padEnd(10) + m.frame).join('\n'));
