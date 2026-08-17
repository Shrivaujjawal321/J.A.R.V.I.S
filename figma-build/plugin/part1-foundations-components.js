/* =============================================================================
 * mySHIPR — Carrier Console  ·  Figma design-system + screens build script
 * -----------------------------------------------------------------------------
 * HOW TO RUN (primary path — works in the BROWSER, no desktop app needed)
 *   1. Open your Figma file in the browser.
 *   2. Run the community plugin "Scripter"
 *      (figma.com/community/plugin/757836922707087381/scripter).
 *   3. Paste this ENTIRE file into the Scripter editor and press Run (Cmd/Ctrl+Enter).
 *   4. Watch the Scripter console — it logs each build phase. Takes ~20–60s.
 *   Re-running is safe: the script deletes everything it made last time first.
 *
 * ALTERNATIVE (Figma desktop app on Windows/macOS, or figma-linux):
 *   Plugins → Development → Import plugin from manifest… → pick the manifest.json
 *   shipped next to this file, then run the plugin.
 *
 * SCRIPTER-SAFE: no plugin UI is used anywhere in this file. It does not open a
 * UI iframe, does not touch the plugin-UI namespace, does not reference the
 * bundled-HTML global, and never closes the plugin mid-run (which would abort
 * Scripter). Progress is reported with console.log; one notify() at the end.
 *
 * RUN ORDER (all inside one async IIFE at the bottom of the file):
 *   1  loadFonts()        resolve + load every family/style pair before any text
 *   2  cleanup()          delete the pages / styles / variables of a previous run
 *   3  makePages()        create 01 Foundations … 05 Prototype
 *   4  buildTokens()      variable collections Color / Radius / Spacing,
 *                         paint styles Color/*, text styles Display|Body|Mono/*
 *   5  buildFoundations() swatch + type + radius + spacing specimen page
 *   6  buildComponents()  every COMPONENT / COMPONENT_SET on "02 Components"
 *   7  buildScreens()     12 desktop frames @1440, assembled from instances
 *   8  buildResponsive()  tablet 900 + mobile 375 for Dashboard / Fleet / Detention
 *   9  wirePrototype()    12 sidebar items × 12 frames = 144 ON_CLICK → NAVIGATE
 *  10  buildProtoPage()   flow map / documentation on "05 Prototype"
 *
 * Every colour, radius, font-size and padding below is read out of
 * mySHIPR_Carrier_Console_v4.html — nothing is invented.
 * ========================================================================== */

/* ------------------------------------------------------------------ 1. TOKENS */
const C = {
  chrome:'#0f141d', chrome2:'#161d29', chrome3:'#1e2735', chromeLine:'#2a3446',
  canvas:'#eef1f4', panel:'#ffffff', panel2:'#f7f9fb', line:'#e0e5ea', line2:'#eef1f4',
  ink:'#141a24', ink2:'#586173', ink3:'#8b93a1', inkInv:'#e7ebf1', inkInv2:'#9aa5b6',
  green:'#157a4a', greenBg:'#e4f3ea', greenInk:'#0e5a37',
  amber:'#c9770a', amberBg:'#fbeede', amberInk:'#8f5405',
  red:'#c23b3b',   redBg:'#f8e4e4',   redInk:'#8f2626',
  blue:'#2c66b0',  blueBg:'#e5eefa',  blueInk:'#1e4c86',
  grey:'#6b7480',  greyBg:'#eceff3',  greyInk:'#4b5460',
  purple:'#6b4fa8',purpleBg:'#eee9f8',purpleInk:'#4d3680',
  brand:'#157a4a', sign:'#e2a90b', white:'#ffffff',
  rowHover:'#f6f9fc', rowBlocked:'#fdf6f6', subInk:'#7b8798', footInk:'#68727f',
  btnOn:'#eafff2', navSubHd:'#57647a'
};
/* the ordered token map that becomes the "Color" variable collection + paint styles */
const COLOR_TOKENS = [
  ['chrome',C.chrome],['chrome-2',C.chrome2],['chrome-3',C.chrome3],['chrome-line',C.chromeLine],
  ['canvas',C.canvas],['panel',C.panel],['panel-2',C.panel2],['line',C.line],['line-2',C.line2],
  ['ink',C.ink],['ink-2',C.ink2],['ink-3',C.ink3],['ink-inv',C.inkInv],['ink-inv-2',C.inkInv2],
  ['green',C.green],['green-bg',C.greenBg],['green-ink',C.greenInk],
  ['amber',C.amber],['amber-bg',C.amberBg],['amber-ink',C.amberInk],
  ['red',C.red],['red-bg',C.redBg],['red-ink',C.redInk],
  ['blue',C.blue],['blue-bg',C.blueBg],['blue-ink',C.blueInk],
  ['grey',C.grey],['grey-bg',C.greyBg],['grey-ink',C.greyInk],
  ['purple',C.purple],['purple-bg',C.purpleBg],['purple-ink',C.purpleInk],
  ['brand',C.brand],['sign',C.sign]
];
const RADIUS_TOKENS = [['r',10],['r-sm',7],['pill',20],['xs',5],['sm',6],['md',8],['lg',12]];
const SPACE_TOKENS  = [2,4,6,8,10,12,14,16,20,22,24,32,48,60].map(n=>['space-'+n,n]);

/* chip / status tone table — .c-green … .c-purple */
const TONE = {
  green :{bg:C.greenBg , fg:C.greenInk , solid:C.green , bd:'#bfdfcd'},
  amber :{bg:C.amberBg , fg:C.amberInk , solid:C.amber , bd:'#f0d9ab'},
  red   :{bg:C.redBg   , fg:C.redInk   , solid:C.red   , bd:'#eec4c4'},
  blue  :{bg:C.blueBg  , fg:C.blueInk  , solid:C.blue  , bd:'#c6dcf4'},
  grey  :{bg:C.greyBg  , fg:C.greyInk  , solid:C.grey  , bd:C.line},
  purple:{bg:C.purpleBg, fg:C.purpleInk, solid:C.purple, bd:C.purpleBg}
};
/* .kpi::before edge colours */
const KPI_EDGE = { default:C.brand, amber:C.sign, red:C.red, blue:C.blue, grey:C.grey };
/* .banner tones */
const BANNER = { info:'blue', warn:'amber', crit:'red', ok:'green' };

const SIDE_W = 248, DESK_W = 1440, TAB_W = 900, MOB_W = 375;
const F = {};                    /* resolved fonts               */
const COMP = {};                 /* component registry by name   */
const P = {};                    /* pages by name                */
const VARS = { Color:{}, Radius:{}, Spacing:{} };
let LIB = null;                   /* component-library board on page 02 */

/* -------------------------------------------------------------- 2. FONT LOAD */
async function tryFont(family, style){
  try { await figma.loadFontAsync({family, style}); return {family, style}; }
  catch(e){ return null; }
}
async function pickFont(cands, fallback){
  for (const [fam, st] of cands){ const f = await tryFont(fam, st); if (f) return f; }
  return fallback;
}
async function loadFonts(){
  let base = null;
  for (const fam of ['Inter','Roboto','Arial']) { if (!base) base = await tryFont(fam,'Regular'); }
  if (!base) throw new Error('No base font available (tried Inter, Roboto, Arial).');
  F.body     = base;
  F.medium   = await pickFont([['Inter','Medium'],['Roboto','Medium']], base);
  F.semi     = await pickFont([['Inter','Semi Bold'],['Inter','SemiBold'],['Roboto','Medium']], F.medium);
  F.bold     = await pickFont([['Inter','Bold'],['Roboto','Bold']], F.semi);
  F.dispMed  = await pickFont([['Barlow Semi Condensed','Medium']], F.medium);
  F.dispSemi = await pickFont([['Barlow Semi Condensed','SemiBold'],['Barlow Semi Condensed','Semi Bold']], F.semi);
  F.dispBold = await pickFont([['Barlow Semi Condensed','Bold']], F.bold);
  F.mono     = await pickFont([['IBM Plex Mono','Regular'],['Roboto Mono','Regular'],['Courier New','Regular']], base);
  F.monoMed  = await pickFont([['IBM Plex Mono','Medium'],['Roboto Mono','Medium']], F.mono);
  F.monoSemi = await pickFont([['IBM Plex Mono','SemiBold'],['IBM Plex Mono','Semi Bold'],['Roboto Mono','Bold']], F.monoMed);
  console.log('fonts →', Object.keys(F).map(k=>k+':'+F[k].family+'/'+F[k].style).join('  '));
}

/* ---------------------------------------------------------------- 3. HELPERS */
function rgb(hex){
  const h = hex.replace('#','');
  return { r:parseInt(h.slice(0,2),16)/255, g:parseInt(h.slice(2,4),16)/255, b:parseInt(h.slice(4,6),16)/255 };
}
function solid(hex, opacity){ return [{type:'SOLID', color:rgb(hex), opacity: opacity==null?1:opacity}]; }
function safe(fn){ try { return fn(); } catch(e){ return null; } }

/**
 * mkFrame — every container in this file is a real Auto Layout frame.
 * o = { dir:'V'|'H'|'N', gap, pad:n|[t,r,b,l], fill, stroke, sides:[t,r,b,l],
 *       radius, w, h, prim, ctr, align, just, wrap, crossGap, clip, name }
 */
function mkFrame(name, o){
  o = o || {};
  const f = figma.createFrame();
  f.name = name;
  f.layoutMode = o.dir === 'H' ? 'HORIZONTAL' : (o.dir === 'N' ? 'NONE' : 'VERTICAL');
  if (f.layoutMode !== 'NONE'){
    f.primaryAxisSizingMode  = o.prim || 'AUTO';
    f.counterAxisSizingMode  = o.ctr  || 'AUTO';
    f.itemSpacing = o.gap || 0;
    let p = o.pad == null ? 0 : o.pad;
    if (typeof p === 'number') p = [p,p,p,p];
    f.paddingTop=p[0]; f.paddingRight=p[1]; f.paddingBottom=p[2]; f.paddingLeft=p[3];
    if (o.align) f.counterAxisAlignItems = o.align;
    if (o.just)  f.primaryAxisAlignItems = o.just;
    if (o.wrap){ f.layoutWrap = 'WRAP'; if (o.crossGap != null) f.counterAxisSpacing = o.crossGap; }
  }
  f.fills = o.fill ? solid(o.fill) : [];
  if (o.stroke){
    f.strokes = solid(o.stroke);
    f.strokeAlign = 'INSIDE';
    const s = o.sides || [1,1,1,1];
    f.strokeTopWeight=s[0]; f.strokeRightWeight=s[1]; f.strokeBottomWeight=s[2]; f.strokeLeftWeight=s[3];
  } else f.strokes = [];
  if (o.radius != null) f.cornerRadius = o.radius;
  f.clipsContent = !!o.clip;
  if (o.w || o.h) f.resize(o.w || f.width, o.h || Math.max(1, f.height));
  if (o.w && f.layoutMode === 'VERTICAL') f.counterAxisSizingMode = 'FIXED';
  if (o.w && f.layoutMode === 'HORIZONTAL') f.primaryAxisSizingMode = 'FIXED';
  if (o.h && f.layoutMode === 'VERTICAL') f.primaryAxisSizingMode = 'FIXED';
  if (o.h && f.layoutMode === 'HORIZONTAL') f.counterAxisSizingMode = 'FIXED';
  return f;
}
/** mkText — o = {font, size, lh, ls, color, case, align, name, op} */
function mkText(chars, o){
  o = o || {};
  const t = figma.createText();
  t.fontName = o.font || F.body;
  t.characters = String(chars == null ? '' : chars);
  t.fontSize = o.size || 14;
  t.lineHeight = o.lh ? {value:o.lh, unit:'PIXELS'} : {value:145, unit:'PERCENT'};
  if (o.ls != null) t.letterSpacing = {value:o.ls, unit:'PIXELS'};
  t.fills = solid(o.color || C.ink, o.op);
  if (o.case)  t.textCase = o.case;
  if (o.align) t.textAlignHorizontal = o.align;
  t.textAutoResize = 'WIDTH_AND_HEIGHT';
  t.name = o.name || 'text';
  return t;
}
/** add(parent, child, opts) — append then apply auto-layout sizing + constraints */
function add(parent, child, o){
  parent.appendChild(child);
  o = o || {};
  const inAL = parent.layoutMode && parent.layoutMode !== 'NONE';
  if (inAL){
    if (o.hFill) safe(()=>{ child.layoutSizingHorizontal = 'FILL'; });
    else if (o.hFix != null) safe(()=>{ child.layoutSizingHorizontal='FIXED'; child.resize(o.hFix, Math.max(1,child.height)); });
    if (o.vFill) safe(()=>{ child.layoutSizingVertical = 'FILL'; });
    else if (o.vFix != null) safe(()=>{ child.layoutSizingVertical='FIXED'; child.resize(Math.max(1,child.width), o.vFix); });
    if (o.self) safe(()=>{ child.layoutAlign = o.self; });
  } else {
    if (o.x != null) child.x = o.x;
    if (o.y != null) child.y = o.y;
  }
  /* constraints so the frame survives a reviewer dragging its edge */
  safe(()=>{ child.constraints = { horizontal: o.cH || (o.hFill ? 'STRETCH' : 'MIN'), vertical: o.cV || 'MIN' }; });
  return child;
}
function fixW(n, w){ safe(()=>{ n.layoutSizingHorizontal='FIXED'; }); safe(()=>n.resize(w, Math.max(1,n.height))); return n; }
function fillW(n){ safe(()=>{ n.layoutSizingHorizontal='FILL'; }); return n; }
function hide(n){ if (n) n.visible = false; return n; }
function show(n){ if (n) n.visible = true; return n; }

/** svgIcon — real vector icons lifted from the HTML's icon sprite */
function svgIcon(path, size, color, sw){
  const s = '<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+
            '" viewBox="0 0 24 24" fill="none" stroke="'+color+'" stroke-width="'+(sw||1.8)+
            '" stroke-linecap="round" stroke-linejoin="round">'+path+'</svg>';
  const n = figma.createNodeFromSvg(s);
  n.name = 'icon';
  if (n.width > 0 && Math.abs(n.width - size) > 0.5) safe(()=>n.rescale(size / n.width));
  return n;
}
const I = {
  chart:'<path d="M3 3v18h18"/><path d="M7 15l4-5 3 3 5-7"/>',
  truck:'<path d="M1 3h13v11H1z"/><path d="M14 7h4l3 3v4h-7z"/><circle cx="5.5" cy="17.5" r="1.6"/><circle cx="17.5" cy="17.5" r="1.6"/>',
  user:'<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/>',
  box:'<path d="M12 2 3 7v10l9 5 9-5V7z"/><path d="M3 7l9 5 9-5M12 22V12"/>',
  route:'<circle cx="6" cy="19" r="2"/><circle cx="18" cy="5" r="2"/><path d="M8 19h6a4 4 0 0 0 0-8H8a4 4 0 0 1 0-8h4"/>',
  msg:'<path d="M21 15a2 2 0 0 1-2 2H8l-5 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2Z"/>',
  gavel:'<path d="M14 4l6 6M4 14l6 6M11 7l6 6M7 11l-4 4 2 2 4-4M17 3l4 4"/>',
  yard:'<path d="M3 21V8l9-5 9 5v13"/><path d="M3 21h18M9 21v-6h6v6"/>',
  bell:'<path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/>',
  coin:'<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>',
  gear:'<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9M4.6 9a1.7 1.7 0 0 0-.3-1.9M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M19.1 4.9L17 7M7 17l-2.1 2.1"/>',
  caret:'<path d="M9 6l6 6-6 6"/>',
  caretDown:'<path d="M6 9l6 6 6-6"/>',
  search:'<circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/>',
  map:'<path d="M9 3 3 5v16l6-2 6 2 6-2V3l-6 2-6-2Z"/><path d="M9 3v16M15 5v16"/>',
  wifioff:'<path d="M5 12.55a11 11 0 0 1 14 0M8.5 16.1a6 6 0 0 1 7 0M12 20h.01"/><path d="M3 3l18 18"/>',
  lock:'<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
  sun:'<path d="M12 2v4M12 18v4M4.9 4.9l2.8 2.8M16.3 16.3l2.8 2.8M2 12h4M18 12h4M4.9 19.1l2.8-2.8M16.3 7.7l2.8-2.8"/>',
  menu:'<path d="M3 6h18M3 12h18M3 18h18"/>',
  warn:'<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/>',
  info:'<circle cx="12" cy="12" r="9"/><path d="M12 16v-4M12 8h.01"/>',
  check:'<path d="M20 6 9 17l-5-5"/>',
  clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  up:'<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M17 8l-5-5-5 5M12 3v12"/>',
  plus:'<path d="M12 5v14M5 12h14"/>',
  empty:'<rect x="3" y="6" width="18" height="14" rx="2"/><path d="M3 11h18M8 6V3M16 6V3"/>',
  arrow:'<path d="M5 12h14M13 6l6 6-6 6"/>',
  doc:'<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/>',
  db:'<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/>',
  users:'<circle cx="9" cy="8" r="3.4"/><path d="M2 20c0-3.6 3.2-5.6 7-5.6s7 2 7 5.6"/><path d="M17 7.5a3 3 0 0 1 0 5.6M18.5 20c0-2.3-.9-4-2.3-5"/>'
};

/* ------------------------------------------------ 4. CLEAN UP A PREVIOUS RUN */

async function cleanupStyles(){
  const ps = await figma.getLocalPaintStylesAsync();
  ps.forEach(s => { if (s.name.indexOf('Color/') === 0) safe(()=>s.remove()); });
  const ts = await figma.getLocalTextStylesAsync();
  ts.forEach(s => { if (/^(Display|Body|Mono)\//.test(s.name)) safe(()=>s.remove()); });
  const cols = await figma.variables.getLocalVariableCollectionsAsync();
  cols.forEach(c => { if (['Color','Radius','Spacing'].indexOf(c.name) >= 0) safe(()=>c.remove()); });
}
/* ------------------------------------------- 5. VARIABLES + STYLES (tokens) */
function mkVar(collection, name, type, value){
  let v = null;
  try { v = figma.variables.createVariable(name, collection, type); }
  catch(e){ try { v = figma.variables.createVariable(name, collection.id, type); } catch(e2){ return null; } }
  safe(()=>v.setValueForMode(collection.modes[0].modeId, value));
  return v;
}
async function buildTokens(){
  const cCol = figma.variables.createVariableCollection('Color');
  COLOR_TOKENS.forEach(([n,hex]) => { VARS.Color[n] = mkVar(cCol, n, 'COLOR', rgb(hex)); });
  const rCol = figma.variables.createVariableCollection('Radius');
  RADIUS_TOKENS.forEach(([n,v]) => { VARS.Radius[n] = mkVar(rCol, n, 'FLOAT', v); });
  const sCol = figma.variables.createVariableCollection('Spacing');
  SPACE_TOKENS.forEach(([n,v]) => { VARS.Spacing[n] = mkVar(sCol, n, 'FLOAT', v); });

  COLOR_TOKENS.forEach(([n,hex]) => {
    const st = figma.createPaintStyle();
    st.name = 'Color/' + n;
    let paint = { type:'SOLID', color: rgb(hex) };
    if (VARS.Color[n]) paint = safe(()=>figma.variables.setBoundVariableForPaint(paint,'color',VARS.Color[n])) || paint;
    st.paints = [paint];
  });

  const TS = [
    ['Display/H1',    F.dispBold, 26,  30, 0.3],
    ['Display/Panel', F.dispSemi, 15,  20, 0.2],
    ['Body/Base',     F.body,     14,  20, 0],
    ['Body/Small',    F.body,     12.5,18, 0],
    ['Body/Sub',      F.body,     11,  16, 0],
    ['Mono/Code',     F.mono,     11.5,16, 0],
    ['Mono/Label',    F.monoMed,  10.5,14, 0.2]
  ];
  TS.forEach(([n,f,sz,lh,ls]) => {
    const s = figma.createTextStyle();
    s.name = n; s.fontName = f; s.fontSize = sz;
    s.lineHeight = {value:lh, unit:'PIXELS'};
    s.letterSpacing = {value:ls, unit:'PIXELS'};
  });
  console.log('tokens → 34 colours, 7 radii, 14 spacings, 34 paint styles, 7 text styles');
}

/* --------------------------------------------------- 6. FOUNDATIONS SPECIMEN */
function buildFoundations(){
  const page = P['01 Foundations'];
  const board = mkFrame('Foundations', {dir:'V', gap:40, pad:56, fill:C.canvas, w:1440});
  add(page, board); board.x = 0; board.y = 0;

  const head = mkFrame('head', {dir:'V', gap:6});
  add(board, head, {hFill:true});
  add(head, mkText('mySHIPR · Carrier Console — Foundations', {font:F.dispBold, size:34, lh:38, ls:0.3}));
  add(head, mkText('Every value below is read out of mySHIPR_Carrier_Console_v4.html :root. Collections: Color · Radius · Spacing.',
      {size:13, lh:19, color:C.ink2}));

  /* colour swatches */
  const swWrap = mkFrame('Color', {dir:'V', gap:12});
  add(board, swWrap, {hFill:true});
  add(swWrap, mkText('COLOR', {font:F.semi, size:11, lh:14, ls:1.2, color:C.ink3, case:'UPPER'}));
  const grid = mkFrame('swatches', {dir:'H', gap:12, wrap:true, crossGap:12});
  add(swWrap, grid, {hFill:true});
  COLOR_TOKENS.forEach(([n,hex]) => {
    const cell = mkFrame('sw/'+n, {dir:'V', gap:0, fill:C.panel, stroke:C.line, radius:10, clip:true, w:150});
    const chipBox = mkFrame('chip', {dir:'V', h:56, fill:hex});
    add(cell, chipBox, {hFill:true});
    const meta = mkFrame('meta', {dir:'V', gap:2, pad:[9,10,10,10]});
    add(cell, meta, {hFill:true});
    add(meta, mkText(n, {font:F.semi, size:11.5, lh:15}));
    add(meta, mkText(hex.toUpperCase(), {font:F.mono, size:10.5, lh:14, color:C.ink3}));
    add(grid, cell);
  });

  /* type specimen */
  const tyWrap = mkFrame('Type', {dir:'V', gap:12});
  add(board, tyWrap, {hFill:true});
  add(tyWrap, mkText('TYPE', {font:F.semi, size:11, lh:14, ls:1.2, color:C.ink3, case:'UPPER'}));
  const tyCard = mkFrame('type card', {dir:'V', gap:0, fill:C.panel, stroke:C.line, radius:10, clip:true});
  add(tyWrap, tyCard, {hFill:true});
  const SPEC = [
    ['Display/H1',   'Fleet Operations Overview', F.dispBold, 26,  30],
    ['Display/Panel','Detention events',          F.dispSemi, 15,  20],
    ['Body/Base',    'Live snapshot of Apex Freight across the US / CA / MX network.', F.body, 14, 20],
    ['Body/Small',   'Every field captured at CO-10 and validated at CO-11.', F.body, 12.5, 18],
    ['Body/Sub',     'interactive · Master Data — 7 values', F.body, 11, 16],
    ['Mono/Code',    'TRK-CARR-US-00142-001 · 1FUJGLDR5CLBP8834', F.mono, 11.5, 16],
    ['Mono/Label',   'ASSET STATUS · REGISTRATION EXPIRY', F.monoMed, 10.5, 14]
  ];
  SPEC.forEach(([n, sample, fnt, sz, lh], i) => {
    const row = mkFrame('row', {dir:'H', gap:24, pad:[14,18,14,18], align:'CENTER',
      stroke: i < SPEC.length-1 ? C.line2 : null, sides:[0,0,1,0]});
    add(tyCard, row, {hFill:true});
    const l = add(row, mkFrame('l', {dir:'V', gap:2}), {hFix:170});
    add(l, mkText(n, {font:F.semi, size:12, lh:16}));
    add(l, mkText(sz+' / '+lh+' · '+fnt.family+' '+fnt.style, {font:F.mono, size:10, lh:13, color:C.ink3}));
    add(row, mkText(sample, {font:fnt, size:sz, lh:lh}), {hFill:true});
  });

  /* radius + spacing */
  const rs = mkFrame('Radius & Spacing', {dir:'H', gap:24});
  add(board, rs, {hFill:true});
  const rCard = mkFrame('radius', {dir:'V', gap:12, pad:18, fill:C.panel, stroke:C.line, radius:10});
  add(rs, rCard, {hFill:true});
  add(rCard, mkText('RADIUS', {font:F.semi, size:11, lh:14, ls:1.2, color:C.ink3}));
  const rRow = mkFrame('r', {dir:'H', gap:14, align:'CENTER', wrap:true, crossGap:14});
  add(rCard, rRow, {hFill:true});
  RADIUS_TOKENS.forEach(([n,v]) => {
    const b = mkFrame('r/'+n, {dir:'V', gap:6, align:'CENTER'});
    const sq = mkFrame('sq', {dir:'V', w:52, h:52, fill:C.panel2, stroke:C.line, radius:v});
    add(b, sq); add(b, mkText(n+' · '+v, {font:F.mono, size:10, lh:13, color:C.ink3}));
    add(rRow, b);
  });
  const sCard = mkFrame('spacing', {dir:'V', gap:12, pad:18, fill:C.panel, stroke:C.line, radius:10});
  add(rs, sCard, {hFill:true});
  add(sCard, mkText('SPACING', {font:F.semi, size:11, lh:14, ls:1.2, color:C.ink3}));
  SPACE_TOKENS.forEach(([n,v]) => {
    const row = mkFrame('s', {dir:'H', gap:10, align:'CENTER'});
    add(sCard, row, {hFill:true});
    add(row, mkText(n, {font:F.mono, size:10, lh:13, color:C.ink3}), {hFix:70});
    const bar = mkFrame('bar', {dir:'V', w:Math.max(2,v*3), h:10, fill:C.brand, radius:2});
    add(row, bar);
  });
  console.log('01 Foundations built');
}

/* ------------------------------------------- 4. COMPONENT REGISTRY HELPERS */
function toComp(frame){ return figma.createComponentFromNode(frame); }
function cross(dims){
  let out = [{}];
  dims.forEach(([k, vals]) => {
    const next = [];
    out.forEach(o => vals.forEach(v => { const c = Object.assign({}, o); c[k] = v; next.push(c); }));
    out = next;
  });
  return out;
}
function makeSet(name, dims, build, parent){
  const order = dims.map(d => d[0]);
  const comps = cross(dims).map(cmb => {
    const c = build(cmb);
    c.name = order.map(k => k + '=' + cmb[k]).join(', ');
    return c;
  });
  const set = figma.combineAsVariants(comps, parent);
  set.name = name;
  set.fills = solid(C.white); set.strokes = solid(C.line); set.cornerRadius = 8;
  COMP[name] = set;
  return set;
}
function makeComp(name, build, parent){
  const c = build();
  c.name = name;
  parent.appendChild(c);
  COMP[name] = c;
  return c;
}
function variantOf(set, props){
  if (!set || set.type !== 'COMPONENT_SET') return set;
  const keys = Object.keys(props || {});
  for (const ch of set.children){
    const map = {};
    ch.name.split(',').forEach(p => { const s = p.trim().split('='); map[s[0]] = s[1]; });
    if (keys.every(k => map[k] === String(props[k]))) return ch;
  }
  return set.defaultVariant || set.children[0];
}
function inst(name, props){
  const c = COMP[name];
  if (!c) throw new Error('missing component: ' + name + ' — run part 1 first.');
  return variantOf(c, props).createInstance();
}
function setText(node, name, value, font, color){
  if (!node || !node.findOne) return null;
  const t = node.findOne(n => n.type === 'TEXT' && n.name === name);
  if (!t) return null;
  if (font) t.fontName = font;
  t.characters = String(value == null ? '' : value);
  if (color) safe(() => { t.fills = solid(color); });
  return t;
}
/* nested Chip/Status override — setProperties first, then force the visuals so the
   result is right even if the nested-instance property override is refused. */
function setChip(ci, tone, label, plain){
  if (!ci) return;
  ci.visible = true;
  safe(() => ci.setProperties({ tone: tone, style: plain ? 'plain' : 'solid-bg' }));
  const t = TONE[tone] || TONE.grey;
  safe(() => { ci.fills = solid(t.bg); });
  const dot = ci.children && ci.children[0];
  if (dot){ dot.visible = !plain; safe(() => { dot.fills = solid(t.fg); }); }
  const tx = ci.children && ci.children[1];
  if (tx){ tx.characters = String(label); safe(() => { tx.fills = solid(t.fg); }); }
}
function setBtn(bi, label, kind){
  if (!bi) return;
  bi.visible = true;
  const lbl = bi.findOne ? bi.findOne(n => n.type === 'TEXT') : null;
  if (lbl) lbl.characters = String(label);
  if (kind === 'primary'){ safe(()=>{ bi.fills = solid(C.brand); bi.strokes = []; }); if (lbl) safe(()=>{ lbl.fills = solid(C.btnOn); }); }
  else if (kind === 'danger'){ safe(()=>{ bi.fills = solid(C.red); bi.strokes = []; }); if (lbl) safe(()=>{ lbl.fills = solid(C.btnOn); }); }
  else { safe(()=>{ bi.fills = solid(C.white); bi.strokes = solid(C.line); }); if (lbl) safe(()=>{ lbl.fills = solid(C.ink); }); }
}
function setIcon(iconInst, name){
  if (!iconInst) return;
  const ok = safe(() => { iconInst.setProperties({ name: name }); return true; });
  if (!ok) safe(() => iconInst.swapComponent(variantOf(COMP['Icon'], {name: name})));
}
/** find every top-level COMPONENT / COMPONENT_SET on a page, keyed by name */
function collectComponents(page){
  const all = page.findAll(n => n.type === 'COMPONENT_SET' || n.type === 'COMPONENT');
  const map = {};
  all.forEach(n => {
    if (n.type === 'COMPONENT' && n.parent && n.parent.type === 'COMPONENT_SET') return;
    if (!map[n.name]) map[n.name] = n;
  });
  return map;
}
const REQUIRED_COMPONENTS = ['Icon','Sidebar/Item','Sidebar/SubItem','Sidebar/Root','TopBar','Button',
  'Chip/Status','Chip/Filter','Legend Chip','KPI Card','Pulse Cell','HOS Bar','Bar Row','Panel',
  'Table/Header','Table/Row','Pager','Banner','Note','EmptyState','Toast','Field','Drawer',
  'List Item','Stop Line','KV Row','Lane'];
function findPage(name){
  const hit = figma.root.children.filter(p => p.name === name);
  return hit.length ? hit[0] : null;
}
/** parts 2 and 3 call this — Scripter does not share scope between runs */
async function adoptComponents(){
  const page = findPage('02 Components');
  if (!page) throw new Error('Page "02 Components" not found. Run part1-foundations-components.js first.');
  if (page.loadAsync) await page.loadAsync();
  const map = collectComponents(page);
  const missing = REQUIRED_COMPONENTS.filter(n => !map[n]);
  if (missing.length){
    console.error('MISSING COMPONENTS:', missing.join(', '));
    throw new Error('Run part1-foundations-components.js first — ' + missing.length + ' component(s) missing.');
  }
  REQUIRED_COMPONENTS.forEach(n => { COMP[n] = map[n]; });
  console.log('adopted ' + REQUIRED_COMPONENTS.length + ' components from "02 Components"');
}
/** replace-not-duplicate: wipe a page we own, creating it if needed */
async function resetPage(name){
  let pg = findPage(name);
  if (!pg){ pg = figma.createPage(); pg.name = name; }
  if (pg.loadAsync) await pg.loadAsync();
  pg.children.slice().forEach(n => safe(() => n.remove()));
  P[name] = pg;
  return pg;
}

/* ------------------------------------------------- 5. NAVIGATION MODEL (NAV) */
const NAV = [
  {key:'dashboard', label:'Dashboard',    icon:'dashboard', subs:['Overview']},
  {key:'fleet',     label:'Fleet',        icon:'fleet',     subs:['All Vehicles','Active Vehicles','Idle Vehicles','Maintenance & DVIR','Vehicle documents','Vehicle Types','Devices & ELD','HOS Status']},
  {key:'drivers',   label:'Drivers',      icon:'drivers',   subs:['All Drivers','On Duty','Off Duty']},
  {key:'loads',     label:'Loads',        icon:'loads',     isNew:true, subs:['Tenders','Awaiting Assignment','In Execution','POD & Close-out','Completed','History']},
  {key:'trips',     label:'Trips',        icon:'trips',     subs:['On going','Scheduled','Upcoming','Completed','Cancelled']},
  {key:'ops',       label:'Driver Ops',   icon:'ops',       isNew:true, subs:['Detention','Exceptions & Safety','Messages']},
  {key:'rr',        label:'RR',           icon:'rr',        subs:['Coming soon']},
  {key:'yards',     label:'Yards',        icon:'yards',     subs:['All yards']},
  {key:'alerts',    label:'Notifications',icon:'alerts',    badge:'8', isNew:true, subs:['Notifications']},
  {key:'reports',   label:'Reports',      icon:'reports',   isNew:true, subs:['Operations']},
  {key:'earnings',  label:'Earnings',     icon:'earnings',  subs:['Earnings','Salary Payout']},
  {key:'settings',  label:'Settings',     icon:'settings',  isNew:true,
   subs:['My Profile','Notification Preferences','Roles & Users','Audit Logs','Sessions','Company Profile','Documents'],
   groups:[['Personal Settings',2],['Company Settings',5]]}
];

/* ------------------------------------------------ 6. SIDEBAR + TOP BAR NODES */
function orgCard(){
  const wrap = mkFrame('orgcard-wrap', {dir:'V', pad:12});
  const card = mkFrame('orgcard', {dir:'V', gap:0, pad:[11,12,11,12], radius:10, fill:C.chrome2, stroke:C.chromeLine});
  add(wrap, card, {hFill:true});
  add(card, mkText('Apex Freight LLC', {font:F.dispSemi, size:15, lh:19, ls:0.2, color:C.white}), {hFill:true});
  const cc = mkText('CARR-US-00142', {font:F.mono, size:11, lh:15, color:C.sign});
  add(card, cc, {hFill:true}); card.itemSpacing = 3;
  const om = mkFrame('om', {dir:'H', gap:10, wrap:true, crossGap:4});
  om.paddingTop = 4; add(card, om, {hFill:true});
  ['USDOT 3421887','MC 874120','US · CA · MX'].forEach(t =>
    add(om, mkText(t, {font:F.mono, size:10, lh:14, color:C.inkInv2})));
  const ost = mkFrame('ost', {dir:'H', gap:5, wrap:true, crossGap:5, pad:[9,0,0,0], stroke:C.chromeLine, sides:[1,0,0,0]});
  ost.paddingTop = 9; add(card, ost, {hFill:true});
  [['Active','green'],['Authority Active','green'],['Contract signed','green'],['COI 19d','amber']].forEach(([t, tone]) => {
    const c = inst('Chip/Status', {tone: tone, style:'plain'});
    setChip(c, tone, t, true); add(ost, c);
  });
  return wrap;
}
/**
 * buildSidebarNode — the real 248px chrome rail. Returns { node, items }.
 * items maps nav key → the Sidebar/Item instance, which is what the prototype wires.
 */
function buildSidebarNode(activeKey, activeSub){
  const side = mkFrame('Sidebar', {dir:'V', gap:0, fill:C.chrome, stroke:C.chromeLine, sides:[0,1,0,0], w:SIDE_W, clip:true});
  /* brand */
  const brand = mkFrame('brand', {dir:'H', gap:10, pad:[14,16,11,16], align:'CENTER', stroke:C.chromeLine, sides:[0,0,1,0]});
  add(side, brand, {hFill:true});
  const mark = mkFrame('mark', {dir:'V', w:34, h:34, radius:8, fill:C.brand, align:'CENTER', just:'CENTER'});
  add(mark, svgIcon(I.truck, 20, '#daffe9', 1.8)); add(brand, mark);
  add(brand, mkText('×', {font:F.dispSemi, size:15, lh:20, color:C.inkInv2}));
  const m2 = mkFrame('mark2', {dir:'V', w:34, h:34, radius:8, fill:'#22304a', align:'CENTER', just:'CENTER'});
  add(m2, mkText('AF', {font:F.dispBold, size:13, lh:17, color:'#cdd7e6'})); add(brand, m2);
  const bt = mkFrame('bt', {dir:'V', gap:2});
  add(brand, bt, {hFill:true});
  add(bt, mkText('mySHIPR', {font:F.dispBold, size:19, lh:19, ls:0.5, color:C.white}), {hFill:true});
  add(bt, mkText('Apex Freight LLC', {size:10, lh:13, ls:0.6, color:C.inkInv2}), {hFill:true});
  /* org card */
  add(side, orgCard(), {hFill:true});
  /* nav */
  const nav = mkFrame('nav', {dir:'V', gap:1, pad:[2,8,16,8]});
  add(side, nav, {hFill:true});
  const items = {};
  NAV.forEach(g => {
    const active = g.key === activeKey;
    const it = inst('Sidebar/Item', {state: active ? 'selected' : 'default', badge: g.badge ? 'count' : 'none'});
    it.name = 'nav/' + g.key;
    setText(it, 'label', g.label);
    setIcon(it.findOne(n => n.type === 'INSTANCE' && n.name === 'icon'), g.icon);
    if (g.badge) setText(it, 'count', g.badge);
    add(nav, it, {hFill:true});
    items[g.key] = it;
    if (!active) return;
    const subs = mkFrame('subs', {dir:'V', gap:0, pad:[2,0,6,38]});
    add(nav, subs, {hFill:true});
    const render = (label, idx) => {
      const si = inst('Sidebar/SubItem', {state: idx === activeSub ? 'active' : 'default'});
      setText(si, 'label', label);
      const nw = si.findOne(n => n.type === 'TEXT' && n.name === 'new');
      if (nw) nw.visible = !!(g.isNew && idx === 0);
      add(subs, si, {hFill:true});
    };
    if (g.groups){
      let i = 0;
      g.groups.forEach(([gl, n]) => {
        add(subs, mkText(gl, {font:F.bold, size:9.5, lh:13, ls:1.14, color:C.navSubHd, case:'UPPER', name:'subgrphd'}), {hFill:true});
        for (let j = 0; j < n; j++, i++) render(g.subs[i], i);
      });
    } else g.subs.forEach(render);
  });
  /* foot */
  const foot = mkFrame('sidefoot', {dir:'V', pad:[11,14,11,14], stroke:C.chromeLine, sides:[1,0,0,0]});
  add(side, foot, {hFill:true});
  add(foot, mkText('Reference build. Terminology and value sets follow Master Data, Carrier Onboarding CO-01…CO-30, Auth Services BRD V3 and Shipment Execution OPS-01…OPS-12. Records are illustrative.',
    {size:10, lh:15, color:C.footInk}), {hFill:true});
  return {node: side, items: items};
}
/** tbtn — the 36×36 chrome icon button in the top bar */
function tbtn(icon, badge){
  const b = mkFrame('tbtn', {dir:'V', w:36, h:36, radius:8, fill:C.chrome2, stroke:C.chromeLine, align:'CENTER', just:'CENTER', clip:false});
  add(b, svgIcon(icon, 17, C.inkInv, 1.8));
  if (badge){
    const d = mkFrame('dot', {dir:'H', pad:[0,3,0,3], h:15, radius:20, fill:C.red, align:'CENTER', just:'CENTER'});
    add(d, mkText(badge, {font:F.monoSemi, size:9, lh:12, color:C.white}));
    b.layoutMode = 'NONE';
    b.appendChild(d); d.x = 24; d.y = 3;
    b.children[0].x = 9.5; b.children[0].y = 9.5;
  }
  return b;
}
/**
 * buildTopBarNode — mode 'desktop' is one 12×22 row; 'tablet'/'mobile' reflow the
 * search onto its own row and swap the crumb for a hamburger, per the 920px rules.
 */
function buildTopBarNode(mode, title, sub){
  const desk = mode === 'desktop';
  const bar = mkFrame('TopBar', {dir:'V', gap:0, fill:C.chrome, w: desk ? DESK_W - SIDE_W : (mode === 'tablet' ? TAB_W : MOB_W)});
  const pad = desk ? 22 : 14;
  const r1 = mkFrame('row-1', {dir:'H', gap: desk ? 14 : 10, align:'CENTER', pad:[desk ? 12 : 10, pad, desk ? 12 : 0, pad], wrap: !desk, crossGap:10});
  add(bar, r1, {hFill:true});
  if (!desk) add(r1, tbtn(I.menu));
  const crumb = mkFrame('crumb', {dir:'V', gap:1});
  add(r1, crumb);
  add(crumb, mkText(title || 'Dashboard', {font:F.dispSemi, size: desk ? 17 : 15, lh: desk ? 21 : 19, ls:0.3, color:C.white, name:'crumb-title'}));
  add(crumb, mkText(sub || 'Overview', {size:11, lh:14, color:C.inkInv2, name:'crumb-sub'}));
  const spacer = mkFrame('spacer', {dir:'H', h:1});
  add(r1, spacer, {hFill:true});
  const search = mkFrame('search', {dir:'H', gap:9, align:'CENTER', pad:[9,12,9,11], radius:8, fill:C.chrome2, stroke:C.chromeLine});
  add(search, svgIcon(I.search, 16, C.subInk, 2));
  add(search, mkText('Search shipments, drivers, trucks, trailers, yards, commodity…',
    {size:12.5, lh:17, color:C.footInk, name:'placeholder'}), {hFill:true});
  if (desk) add(r1, search, {hFix:460});
  const icons = mkFrame('actions', {dir:'H', gap: desk ? 14 : 10, align:'CENTER'});
  add(r1, icons);
  add(icons, tbtn(I.bell, '8'));
  add(icons, tbtn(I.map));
  add(icons, tbtn(I.wifioff));
  add(icons, tbtn(I.lock));
  const sim = mkFrame('simmode', {dir:'H', gap:6, align:'CENTER', h:36, pad:[0,12,0,12], radius:8, fill:C.chrome2, stroke:C.chromeLine});
  add(sim, svgIcon(I.sun, 15, C.inkInv2, 1.8));
  add(sim, mkText('Preview: new carrier', {font:F.semi, size:11.5, lh:15, color:C.inkInv2}));
  const who = mkFrame('who', {dir:'H', gap:9, align:'CENTER'});
  const av = mkFrame('av', {dir:'V', w:32, h:32, radius:16, fill:'#22304a', align:'CENTER', just:'CENTER'});
  add(av, mkText('DR', {font:F.dispSemi, size:13, lh:17, color:'#cdd7e6'})); add(who, av);
  const wb = mkFrame('wb', {dir:'V', gap:2});
  add(who, wb);
  const wn = mkText('D. Rao', {font:F.semi, size:12.5, lh:16, color:C.inkInv});
  add(wb, wn); wn.visible = mode !== 'mobile';
  const sel = mkFrame('rolesel', {dir:'H', gap:5, align:'CENTER', pad:[2,4,2,4], radius:5, fill:C.chrome2, stroke:C.chromeLine});
  add(sel, mkText('Carrier Super Admin', {font:F.mono, size:10, lh:13, color:C.sign}));
  add(sel, svgIcon(I.caretDown, 10, C.sign, 2));
  add(wb, sel);
  if (desk){ add(r1, sim); add(r1, who); }
  else if (mode === 'tablet'){
    add(r1, sim); add(r1, who);
    const r2 = mkFrame('row-2', {dir:'H', pad:[10,pad,10,pad]});
    add(bar, r2, {hFill:true}); add(r2, search, {hFill:true});
  } else {
    const r2 = mkFrame('row-2', {dir:'H', gap:10, align:'CENTER', pad:[10,pad,0,pad]});
    add(bar, r2, {hFill:true}); add(r2, sim); add(r2, who);
    const r3 = mkFrame('row-3', {dir:'H', pad:[10,pad,10,pad]});
    add(bar, r3, {hFill:true}); add(r3, search, {hFill:true});
  }
  return bar;
}
function buildComponents(){
  const page = P['02 Components'];
  const lib = LIB = mkFrame('Component library', {dir:'V', gap:44, pad:56, fill:C.canvas, w:1680});
  add(page, lib); lib.x = 0; lib.y = 0;
  add(lib, mkText('mySHIPR · Carrier Console — Components', {font:F.dispBold, size:34, lh:38, ls:0.3}));
  add(lib, mkText('Every screen on pages 03 and 04 is assembled from instances of the sets below. Auto Layout + constraints throughout.',
      {size:13, lh:19, color:C.ink2}));

  function sect(title, sub){
    const s = mkFrame(title, {dir:'V', gap:14});
    add(lib, s, {hFill:true});
    add(s, mkText(title, {font:F.dispBold, size:20, lh:24}));
    if (sub) add(s, mkText(sub, {size:12, lh:17, color:C.ink2}));
    const holder = mkFrame('items', {dir:'H', gap:36, wrap:true, crossGap:36, align:'MIN'});
    add(s, holder, {hFill:true});
    return holder;
  }

  /* ---------- Icon ---------- */
  const NAVICON = [['dashboard',I.chart],['fleet',I.truck],['drivers',I.user],['loads',I.box],
                   ['trips',I.route],['ops',I.msg],['rr',I.gavel],['yards',I.yard],
                   ['alerts',I.bell],['reports',I.chart],['earnings',I.coin],['settings',I.users]];
  const hIcon = sect('Icon', 'Nav glyphs lifted verbatim from the HTML icon sprite. Tone is driven by instance opacity in Sidebar/Item.');
  makeSet('Icon', [['name', NAVICON.map(x => x[0])]], cmb => {
    const f = mkFrame('Icon', {dir:'N', w:17, h:17});
    const path = (NAVICON.filter(x => x[0] === cmb.name)[0] || NAVICON[0])[1];
    const g = svgIcon(path, 17, C.white, 1.7);
    f.appendChild(g); g.x = 0; g.y = 0;
    return toComp(f);
  }, hIcon);

  /* ---------- Sidebar/Item ---------- */
  const hSide = sect('Sidebar', '.navhead 9/10 padding · 7px radius · Inter 13/500 · badge pills are mono 9.5.');
  makeSet('Sidebar/Item', [['state',['default','hover','selected']], ['badge',['none','count','new']]], cmb => {
    const bg = cmb.state === 'selected' ? C.chrome3 : (cmb.state === 'hover' ? C.chrome2 : null);
    const fg = cmb.state === 'selected' ? C.white   : (cmb.state === 'hover' ? C.inkInv : C.inkInv2);
    const f = mkFrame('Sidebar/Item', {dir:'H', gap:10, pad:[9,10,9,10], radius:7, fill:bg, align:'CENTER', w:232});
    const ic = inst('Icon', {name:'dashboard'});
    ic.name = 'icon';
    ic.opacity = cmb.state === 'selected' ? 1 : (cmb.state === 'hover' ? 0.85 : 0.62);
    add(f, ic);
    add(f, mkText('Dashboard', {font:F.medium, size:13, lh:19, color:fg, name:'label'}), {hFill:true});
    const bc = mkFrame('badge-count', {dir:'H', pad:[1,6,1,6], radius:20, fill:C.red, align:'CENTER'});
    add(bc, mkText('8', {font:F.monoSemi, size:9.5, lh:13, color:C.white, name:'count'}));
    add(f, bc); bc.visible = cmb.badge === 'count';
    const bn = mkFrame('badge-new', {dir:'H', pad:[1,6,1,6], radius:20, fill:C.sign, align:'CENTER'});
    add(bn, mkText('NEW', {font:F.monoSemi, size:9.5, lh:13, color:'#241a00', ls:0.5, name:'new'}));
    add(f, bn); bn.visible = cmb.badge === 'new';
    const car = svgIcon(cmb.state === 'selected' ? I.caretDown : I.caret, 14, fg, 2);
    car.name = 'caret'; car.opacity = 0.6;
    add(f, car);
    return toComp(f);
  }, hSide);

  makeSet('Sidebar/SubItem', [['state',['default','active']]], cmb => {
    const on = cmb.state === 'active';
    const f = mkFrame('Sidebar/SubItem', {dir:'H', gap:0, radius:5, fill: on ? C.chrome2 : null, clip:true, w:194, align:'CENTER'});
    const edge = mkFrame('edge', {dir:'V', w:2, h:26, fill:C.brand});
    add(f, edge, {vFill:true}); edge.visible = on;
    const body = mkFrame('body', {dir:'H', gap:6, pad:[5,8,5,8], align:'CENTER'});
    add(f, body, {hFill:true});
    add(body, mkText('All Vehicles', {font: on ? F.semi : F.body, size:12.5, lh:17, color: on ? C.white : C.subInk, name:'label'}), {hFill:true});
    const nw = mkText('NEW', {font:F.mono, size:8, lh:11, color:C.sign, ls:0.6, name:'new'});
    add(body, nw); nw.visible = false;
    return toComp(f);
  }, hSide);

  /* ---------- Button ---------- */
  const hBtn = sect('Button', '.btn — display font 13.5/600, 8×15 padding, 7px radius. .btn.sm — 12px, 5×10, 6px.');
  makeSet('Button', [['kind',['primary','secondary','danger']], ['size',['md','sm']], ['state',['default','hover','disabled']]], cmb => {
    const sm = cmb.size === 'sm';
    let fill = C.brand, fg = C.btnOn, stroke = null;
    if (cmb.kind === 'secondary'){ fill = C.white; fg = C.ink; stroke = C.line; }
    if (cmb.kind === 'danger') fill = C.red;
    if (cmb.state === 'hover'){
      if (cmb.kind === 'primary') fill = '#12693f';
      if (cmb.kind === 'danger')  fill = '#a83232';
      if (cmb.kind === 'secondary'){ fill = C.panel2; stroke = C.ink3; }
    }
    const f = mkFrame('Button', {dir:'H', gap:7, align:'CENTER', radius: sm ? 6 : 7,
      pad: sm ? [5,10,5,10] : [8,15,8,15], fill: fill, stroke: stroke});
    const g = svgIcon(I.plus, sm ? 13 : 15, fg, 2);
    g.name = 'icon'; add(f, g); g.visible = false;
    add(f, mkText(sm ? 'Action' : 'Register truck',
      {font:F.dispSemi, size: sm ? 12 : 13.5, lh: sm ? 16 : 18, ls:0.3, color:fg, name:'label'}));
    if (cmb.state === 'disabled') f.opacity = 0.45;
    return toComp(f);
  }, hBtn);

  /* ---------- Chips ---------- */
  const hChip = sect('Chips', '.chip — mono 10.5/500, 2×8 padding, 20px radius, 6px status dot. .fchip — filter pill with count.');
  makeSet('Chip/Status', [['tone',Object.keys(TONE)], ['style',['solid-bg','plain']]], cmb => {
    const t = TONE[cmb.tone];
    const f = mkFrame('Chip/Status', {dir:'H', gap:5, align:'CENTER', pad:[2,8,2,8], radius:20, fill:t.bg});
    const dot = mkFrame('dot', {dir:'V', w:6, h:6, radius:3, fill:t.fg});
    dot.opacity = 0.85; add(f, dot); dot.visible = cmb.style === 'solid-bg';
    add(f, mkText('Available', {font:F.monoMed, size:10.5, lh:15, ls:0.2, color:t.fg, name:'label'}));
    return toComp(f);
  }, hChip);

  makeSet('Chip/Filter', [['state',['off','on']], ['count',['yes','no']]], cmb => {
    const on = cmb.state === 'on';
    const f = mkFrame('Chip/Filter', {dir:'H', gap:5, align:'CENTER', pad:[3,9,3,9], radius:20,
      fill: on ? C.brand : C.white, stroke: on ? C.brand : C.line});
    add(f, mkText('Available', {font: on ? F.monoSemi : F.mono, size:10.5, lh:15, color: on ? C.white : C.ink2, name:'label'}));
    const cnt = mkText('3', {font:F.mono, size:10.5, lh:15, color: on ? '#cfe9dc' : C.ink3, name:'count'});
    add(f, cnt); cnt.visible = cmb.count === 'yes';
    return toComp(f);
  }, hChip);

  makeComp('Legend Chip', () => {
    const f = mkFrame('Legend Chip', {dir:'H', pad:[3,9,3,9], radius:20, fill:C.white, stroke:C.line, align:'CENTER'});
    add(f, mkText('CO-10 Truck Registration', {font:F.mono, size:10, lh:14, color:C.ink3, name:'label'}));
    return toComp(f);
  }, hChip);

  /* ---------- KPI / pulse / bars ---------- */
  const hKpi = sect('KPI, pulse & bars', '.kpi 14×15 with a 4px coloured left edge · display 32/700 value · .pcell strip · chart bar rows.');
  makeSet('KPI Card', [['tone',['default','amber','red','blue','grey']]], cmb => {
    const f = mkFrame('KPI Card', {dir:'H', gap:0, fill:C.panel, stroke:C.line, radius:10, clip:true, w:178});
    const edge = mkFrame('edge', {dir:'V', w:4, h:96, fill:KPI_EDGE[cmb.tone]});
    add(f, edge, {vFill:true});
    const body = mkFrame('body', {dir:'V', gap:0, pad:[14,15,14,15]});
    add(f, body, {hFill:true});
    add(body, mkText('FLEET SIZE', {font:F.semi, size:10.5, lh:14, ls:1.05, color:C.ink3, case:'UPPER', name:'label'}), {hFill:true});
    const vr = mkFrame('value-row', {dir:'H', gap:6, align:'BASELINE'});
    vr.paddingTop = 6; add(body, vr, {hFill:true});
    add(vr, mkText('8', {font:F.dispBold, size:32, lh:34, ls:0.3, name:'value'}));
    const small = mkText('%', {font:F.dispBold, size:15, lh:20, color:C.ink2, name:'value-small'});
    add(vr, small); small.visible = false;
    const sub = mkText('3 available · 5 not dispatchable', {size:11.5, lh:16, color:C.ink2, name:'sub'});
    sub.name = 'sub'; add(body, sub, {hFill:true});
    body.itemSpacing = 4;
    return toComp(f);
  }, hKpi);

  makeComp('Pulse Cell', () => {
    const f = mkFrame('Pulse Cell', {dir:'H', gap:10, align:'CENTER', pad:[12,15,12,15], fill:C.panel, w:222});
    const dot = mkFrame('dot', {dir:'V', w:9, h:9, radius:5, fill:C.green});
    add(f, dot);
    const b = mkFrame('b', {dir:'V', gap:2});
    add(f, b, {hFill:true});
    add(b, mkText('3', {font:F.dispBold, size:20, lh:20, name:'value'}));
    add(b, mkText('TRUCKS AVAILABLE', {size:10, lh:13, ls:0.7, color:C.ink2, case:'UPPER', name:'label'}), {hFill:true});
    return toComp(f);
  }, hKpi);

  makeSet('HOS Bar', [['band',['green','amber','red']]], cmb => {
    const col = cmb.band === 'green' ? C.green : (cmb.band === 'amber' ? C.sign : C.red);
    const f = mkFrame('HOS Bar', {dir:'H', gap:8, align:'CENTER'});
    const track = mkFrame('track', {dir:'H', w:80, h:7, radius:20, fill:C.line2, clip:true});
    add(f, track, {hFill:true});
    const fillN = mkFrame('fill', {dir:'V', w:52, h:7, radius:20, fill:col});
    add(track, fillN, {vFill:true});
    add(f, mkText('6.5 h', {font:F.monoSemi, size:11, lh:15, name:'value'}));
    return toComp(f);
  }, hKpi);

  makeSet('Bar Row', [['tone',['green','amber','red','blue','grey']]], cmb => {
    const col = TONE[cmb.tone].solid;
    const f = mkFrame('Bar Row', {dir:'H', gap:14, align:'CENTER', pad:[7,0,7,0], w:900});
    const l = mkFrame('l', {dir:'V', gap:1});
    add(f, l, {hFix:230});
    add(l, mkText('FTL - Standard Goods', {font:F.semi, size:12.5, lh:17, name:'label'}), {hFill:true});
    const sub = mkText('SHP-FTL', {font:F.mono, size:10.5, lh:14, color:C.ink3, name:'sub'});
    add(l, sub, {hFill:true});
    const track = mkFrame('track', {dir:'H', h:9, radius:20, fill:C.line2, clip:true});
    add(f, track, {hFill:true});
    const fillN = mkFrame('fill', {dir:'V', w:280, h:9, radius:20, fill:col});
    add(track, fillN, {vFill:true});
    add(f, mkText('3', {font:F.dispBold, size:16, lh:20, align:'RIGHT', name:'value'}), {hFix:44});
    return toComp(f);
  }, hKpi);

  /* ---------- Panel + table ---------- */
  const hPanel = sect('Panel & table', '.panelhd 13×16 with a 1px bottom rule · th 10.5 uppercase on #f7f9fb · td 11×14 on a #eef1f4 rule.');
  makeSet('Panel', [['header',['title-only','title+hint','title+action']]], cmb => {
    const f = mkFrame('Panel', {dir:'H', gap:10, align:'CENTER', just:'SPACE_BETWEEN',
      pad:[13,16,13,16], fill:C.panel, stroke:C.line, sides:[0,0,1,0], w:640});
    add(f, mkText('Fleet', {font:F.dispSemi, size:15, lh:20, ls:0.2, name:'title'}));
    const right = mkFrame('right', {dir:'H', gap:8, align:'CENTER'});
    add(f, right);
    const hint = mkText('8 vehicles', {size:11, lh:15, color:C.ink3, name:'hint'});
    add(right, hint); hint.visible = cmb.header === 'title+hint';
    const act = inst('Button', {kind:'secondary', size:'sm', state:'default'});
    act.name = 'action'; add(right, act); act.visible = cmb.header === 'title+action';
    return toComp(f);
  }, hPanel);

  const COLW = [150,150,150,120,120,120,120,120,120,120];
  makeComp('Table/Header', () => {
    const f = mkFrame('Table/Header', {dir:'H', gap:0, fill:C.panel2, stroke:C.line, sides:[0,0,1,0], w:1132});
    for (let i = 0; i < 10; i++){
      const cell = mkFrame('h' + i, {dir:'V', gap:0, pad:[10,14,10,14]});
      add(f, cell, {hFix: COLW[i]});
      add(cell, mkText('COLUMN', {font:F.semi, size:10.5, lh:14, ls:0.74, color:C.ink3, case:'UPPER', name:'label'}), {hFill:true});
    }
    return toComp(f);
  }, hPanel);

  makeSet('Table/Row', [['state',['default','clickable-hover','blocked']]], cmb => {
    const bg = cmb.state === 'blocked' ? C.rowBlocked : (cmb.state === 'clickable-hover' ? C.rowHover : C.panel);
    const f = mkFrame('Table/Row', {dir:'H', gap:0, fill:bg, stroke:C.line2, sides:[0,0,1,0], w:1132});
    for (let i = 0; i < 10; i++){
      const cell = mkFrame('c' + i, {dir:'V', gap:3, pad:[11,14,11,14], align:'MIN'});
      add(f, cell, {hFix: COLW[i]});
      /* 0 box */
      const box = mkFrame('box', {dir:'V', w:15, h:15, radius:3, fill:C.white, stroke:C.ink3});
      add(cell, box); box.visible = false;
      /* 1 main */
      add(cell, mkText('Cell', {size:12.5, lh:17, name:'main'}), {hFill:true});
      /* 2 sub */
      const sub = mkText('sub', {size:11, lh:15, color:C.ink3, name:'sub'});
      add(cell, sub, {hFill:true}); sub.visible = false;
      /* 3 chips */
      const chips = mkFrame('chips', {dir:'H', gap:6, wrap:true, crossGap:4});
      add(cell, chips, {hFill:true});
      const c1 = inst('Chip/Status', {tone:'green', style:'solid-bg'}); c1.name = 'chip';  add(chips, c1);
      const c2 = inst('Chip/Status', {tone:'grey',  style:'plain'});    c2.name = 'chip2'; add(chips, c2); c2.visible = false;
      chips.visible = false;
      /* 4 sub2 — the line that sits UNDER a status chip, e.g. "dispatch blocked" */
      const sub2 = mkText('dispatch blocked', {size:11, lh:15, color:C.redInk, name:'sub2'});
      add(cell, sub2, {hFill:true}); sub2.visible = false;
      /* 5 bar */
      const bar = inst('HOS Bar', {band:'green'}); bar.name = 'bar';
      add(cell, bar, {hFill:true}); bar.visible = false;
      /* 6 acts */
      const acts = mkFrame('acts', {dir:'V', gap:6});
      add(cell, acts);
      const b1 = inst('Button', {kind:'secondary', size:'sm', state:'default'}); b1.name = 'btn';  add(acts, b1);
      const b2 = inst('Button', {kind:'primary',   size:'sm', state:'default'}); b2.name = 'btn2'; add(acts, b2); b2.visible = false;
      acts.visible = false;
    }
    return toComp(f);
  }, hPanel);

  makeComp('Pager', () => {
    const f = mkFrame('Pager', {dir:'H', gap:10, align:'CENTER', just:'SPACE_BETWEEN',
      pad:[10,16,10,16], fill:C.panel, stroke:C.line, sides:[1,0,0,0], w:1132});
    add(f, mkText('Showing 1–6 of 8', {size:12, lh:16, color:C.ink2, name:'range'}));
    const pgs = mkFrame('pgs', {dir:'H', gap:4, align:'CENTER'});
    add(f, pgs);
    [['‹',false],['1',true],['2',false],['›',false]].forEach(([t, on]) => {
      const b = mkFrame('pgb', {dir:'H', w:28, h:26, align:'CENTER', just:'CENTER', radius:5,
        fill: on ? C.brand : C.white, stroke: on ? C.brand : C.line});
      add(b, mkText(t, {font: on ? F.monoSemi : F.mono, size:11, lh:14, color: on ? C.white : C.ink2}));
      add(pgs, b);
    });
    return toComp(f);
  }, hPanel);

  /* ---------- Banner / Note / Empty / Toast ---------- */
  const hMsg = sect('Messaging', '.banner 13×16 with a tonal 1px border · .note with a 3px left rule · .state 46×24 empty / 403 / error.');
  makeSet('Banner', [['tone',['info','warn','crit','ok']], ['action',['yes','no']]], cmb => {
    const t = TONE[BANNER[cmb.tone]];
    const f = mkFrame('Banner', {dir:'H', gap:12, pad:[13,16,13,16], radius:10, fill:t.bg, stroke:t.bd, align:'MIN', w:1132});
    const g = svgIcon(cmb.tone === 'info' ? I.info : (cmb.tone === 'ok' ? I.check : I.warn), 18, t.fg, 1.8);
    g.name = 'icon'; add(f, g);
    const b = mkFrame('b', {dir:'V', gap:2});
    add(f, b, {hFill:true});
    add(b, mkText('1 required compliance document outstanding', {font:F.dispBold, size:15, lh:20, ls:0.2, color:t.fg, name:'title'}), {hFill:true});
    add(b, mkText('CO-07 lists eight mandatory carrier documents.', {size:12, lh:17, color:t.fg, name:'body'}), {hFill:true});
    const acts = mkFrame('acts', {dir:'H', gap:8});
    add(f, acts); acts.visible = cmb.action === 'yes';
    const a1 = inst('Button', {kind:'primary', size:'md', state:'default'}); a1.name = 'btn';  add(acts, a1);
    const a2 = inst('Button', {kind:'secondary', size:'md', state:'default'}); a2.name = 'btn2'; add(acts, a2); a2.visible = false;
    return toComp(f);
  }, hMsg);

  makeSet('Note', [['tone',['amber','red','blue']]], cmb => {
    const col = cmb.tone === 'amber' ? C.sign : (cmb.tone === 'red' ? C.red : C.blue);
    const f = mkFrame('Note', {dir:'H', gap:0, radius:7, clip:true, stroke:C.line, w:1132});
    const edge = mkFrame('edge', {dir:'V', w:3, h:44, fill:col});
    add(f, edge, {vFill:true});
    const b = mkFrame('b', {dir:'H', gap:9, pad:[11,13,11,13], fill:C.panel2, align:'MIN'});
    add(f, b, {hFill:true});
    const g = svgIcon(I.info, 16, col, 1.8); g.name = 'icon'; add(b, g);
    add(b, mkText('Rows shaded red are not dispatchable.', {size:12, lh:17, color:C.ink2, name:'body'}), {hFill:true});
    return toComp(f);
  }, hMsg);

  makeSet('EmptyState', [['kind',['empty','denied','error']]], cmb => {
    const tone = cmb.kind === 'empty' ? 'grey' : 'red';
    const t = TONE[tone];
    const f = mkFrame('EmptyState', {dir:'V', gap:0, pad:[46,24,46,24], align:'CENTER', just:'CENTER', fill:C.panel, w:640});
    const ic = mkFrame('si', {dir:'V', w:44, h:44, radius:12, fill:t.bg, align:'CENTER', just:'CENTER'});
    add(ic, svgIcon(cmb.kind === 'empty' ? I.empty : (cmb.kind === 'denied' ? I.lock : I.warn), 22, t.solid, 1.8));
    add(f, ic); ic.paddingBottom = 0;
    const sp = mkFrame('sp', {dir:'V', h:12}); add(f, sp);
    add(f, mkText(cmb.kind === 'empty' ? 'Nothing here yet'
       : (cmb.kind === 'denied' ? 'You do not have permission to access this resource'
       : 'Unable to connect to server. Please try again later.'),
       {font:F.dispSemi, size:17, lh:22, align:'CENTER', name:'title'}), {hFill:true});
    add(f, mkText('No records match the current filters.', {size:12.5, lh:18, color:C.ink2, align:'CENTER', name:'body'}), {hFix:400});
    const code = mkText(cmb.kind === 'denied' ? 'ERR-GEN-002 · HTTP 403' : 'ERR-GEN-003 · HTTP 503',
      {font:F.mono, size:10.5, lh:14, color:C.ink3, align:'CENTER', name:'code'});
    add(f, code); code.visible = cmb.kind !== 'empty';
    const act = inst('Button', {kind:'secondary', size:'md', state:'default'});
    act.name = 'action'; add(f, act); act.visible = false;
    f.itemSpacing = 8;
    return toComp(f);
  }, hMsg);

  makeComp('Toast', () => {
    const f = mkFrame('Toast', {dir:'H', gap:9, align:'CENTER', pad:[11,18,11,18], radius:9, fill:C.chrome3});
    add(f, svgIcon(I.check, 16, '#7fe6ac', 2));
    add(f, mkText('Detention raised as billable — DET-0041', {size:13, lh:18, color:C.white, name:'label'}));
    safe(()=>{ f.effects = [{type:'DROP_SHADOW', color:{r:0,g:0,b:0,a:0.28}, offset:{x:0,y:10}, radius:30, spread:0, visible:true, blendMode:'NORMAL'}]; });
    return toComp(f);
  }, hMsg);

  /* ---------- Form ---------- */
  const hForm = sect('Form', '.field label 11 uppercase · control 8×11 on a 7px radius · focus adds the brand ring, error the red ring + message.');
  makeSet('Field', [['state',['default','focus','error']], ['type',['input','select']]], cmb => {
    const err = cmb.state === 'error', foc = cmb.state === 'focus';
    const f = mkFrame('Field', {dir:'V', gap:4, w:300});
    add(f, mkText('LICENCE PLATE', {font:F.semi, size:11, lh:15, ls:0.77, color:C.ink3, case:'UPPER', name:'label'}), {hFill:true});
    const ctl = mkFrame('control', {dir:'H', gap:8, align:'CENTER', pad:[8,11,8,11], radius:7,
      fill: err ? '#fffafa' : C.white, stroke: err ? C.red : (foc ? C.brand : C.line)});
    add(f, ctl, {hFill:true});
    add(ctl, mkText('8ZTK492', {size:12.5, lh:18, color: cmb.state === 'default' ? C.ink3 : C.ink, name:'value'}), {hFill:true});
    const car = svgIcon(I.caretDown, 13, C.ink3, 2); car.name = 'caret';
    add(ctl, car); car.visible = cmb.type === 'select';
    if (foc) safe(()=>{ ctl.effects = [{type:'DROP_SHADOW', color:{r:0.08,g:0.48,b:0.29,a:0.18}, offset:{x:0,y:0}, radius:0, spread:3, visible:true, blendMode:'NORMAL'}]; });
    const msg = mkFrame('emsg', {dir:'H', gap:5, align:'CENTER'});
    add(f, msg);
    add(msg, svgIcon(I.warn, 12, C.redInk, 2));
    add(msg, mkText('Required fields are missing — ERR-GEN-005', {size:11, lh:15, color:C.redInk, name:'error'}));
    msg.visible = err;
    return toComp(f);
  }, hForm);

  /* ---------- Lists ---------- */
  const hList = sect('Lists & rows', '.mitem notification row · .stopline pickup / drop · .dl key-value row · .lane origin → destination.');
  makeSet('List Item', [['sev',['crit','warn','info','ok','grey']], ['unread',['yes','no']]], cmb => {
    const tone = cmb.sev === 'crit' ? 'red' : cmb.sev === 'warn' ? 'amber' : cmb.sev === 'info' ? 'blue' : cmb.sev === 'ok' ? 'green' : 'grey';
    const t = TONE[tone], un = cmb.unread === 'yes';
    const f = mkFrame('List Item', {dir:'H', gap:0, fill: un ? '#fbfdff' : C.panel, stroke:C.line2, sides:[0,0,1,0], w:1132});
    const edge = mkFrame('edge', {dir:'V', w:3, h:60, fill:C.blue});
    add(f, edge, {vFill:true}); edge.visible = un;
    const b = mkFrame('b', {dir:'H', gap:11, pad:[12,16,12,16], align:'MIN'});
    add(f, b, {hFill:true});
    const ic = mkFrame('mi-ico', {dir:'V', w:30, h:30, radius:8, fill:t.bg, align:'CENTER', just:'CENTER'});
    add(ic, svgIcon(cmb.sev === 'ok' ? I.check : cmb.sev === 'info' ? I.info : I.warn, 16, t.solid, 1.8));
    add(b, ic);
    const body = mkFrame('body', {dir:'V', gap:2});
    add(b, body, {hFill:true});
    add(body, mkText('SOS alert from Driver Tyler Brooks', {font:F.semi, size:12.5, lh:17, name:'title'}), {hFill:true});
    add(body, mkText('Emergency (911) status received with GPS 37.6390, -120.9969 on TRIP-58024.',
      {size:11.5, lh:16, color:C.ink2, name:'body'}), {hFill:true});
    add(body, mkText('CR-025 · SOS', {font:F.mono, size:10.5, lh:14, color:C.ink3, name:'code'}), {hFill:true});
    const meta = mkFrame('meta', {dir:'V', gap:5, align:'MAX'});
    add(b, meta);
    add(meta, mkText('4m ago', {font:F.mono, size:10.5, lh:14, color:C.ink3, name:'time'}));
    const act = inst('Button', {kind:'secondary', size:'sm', state:'default'});
    act.name = 'action'; add(meta, act); act.visible = false;
    return toComp(f);
  }, hList);

  makeSet('Stop Line', [['kind',['pickup','drop']]], cmb => {
    const pick = cmb.kind === 'pickup';
    const t = pick ? TONE.blue : TONE.green;
    const f = mkFrame('Stop Line', {dir:'H', gap:12, pad:[12,0,12,0], align:'MIN', stroke:C.line2, sides:[0,0,1,0], w:560});
    const sq = mkFrame('sq', {dir:'V', w:26, h:26, radius:13, fill:t.bg, align:'CENTER', just:'CENTER'});
    add(sq, mkText(pick ? 'P' : 'D', {font:F.monoSemi, size:11, lh:15, color:t.fg}));
    add(f, sq);
    const b = mkFrame('b', {dir:'V', gap:3});
    add(f, b, {hFill:true});
    const top = mkFrame('top', {dir:'H', gap:7, align:'BASELINE'});
    add(b, top, {hFill:true});
    add(top, mkText('Sacramento, CA', {font:F.semi, size:12.5, lh:17, name:'loc'}));
    add(top, mkText('95814', {font:F.mono, size:10.5, lh:15, color:C.ink3, name:'zip'}));
    add(b, mkText('2026-07-26   08:00 – 12:00 UTC     22 pallets     38,400 lbs',
      {size:11.5, lh:16, color:C.ink2, name:'meta'}), {hFill:true});
    const chip = inst('Chip/Status', {tone:'grey', style:'plain'});
    chip.name = 'chip'; add(top, chip);
    return toComp(f);
  }, hList);

  makeSet('KV Row', [['state',['default','empty']]], cmb => {
    const f = mkFrame('KV Row', {dir:'H', gap:14, align:'MIN', w:520});
    const dt = mkFrame('dt', {dir:'V', pad:[6,0,6,0], stroke:C.line2, sides:[0,0,1,0]});
    add(f, dt, {hFix:190});
    add(dt, mkText('Commodity', {size:12.5, lh:17, color:C.ink3, name:'key'}), {hFill:true});
    const dd = mkFrame('dd', {dir:'H', gap:6, pad:[6,0,6,0], stroke:C.line2, sides:[0,0,1,0], align:'CENTER', wrap:true, crossGap:4});
    add(f, dd, {hFill:true});
    add(dd, mkText(cmb.state === 'empty' ? 'Not captured' : 'Fresh Produce',
      {font: cmb.state === 'empty' ? F.body : F.medium, size:12.5, lh:17,
       color: cmb.state === 'empty' ? C.ink3 : C.ink, name:'value'}));
    const sfx = mkText('Refrigerated Goods', {size:11.5, lh:16, color:C.ink3, name:'suffix'});
    add(dd, sfx); sfx.visible = false;
    const chip = inst('Chip/Status', {tone:'amber', style:'plain'});
    chip.name = 'chip'; add(dd, chip); chip.visible = false;
    return toComp(f);
  }, hList);

  makeComp('Lane', () => {
    const f = mkFrame('Lane', {dir:'H', gap:7, align:'CENTER'});
    add(f, mkText('San Jose', {font:F.medium, size:12.5, lh:17, name:'from'}));
    add(f, mkText('95112', {font:F.mono, size:10, lh:14, color:C.ink3, name:'from-zip'}));
    add(f, svgIcon(I.arrow, 14, C.ink3, 1.6));
    add(f, mkText('Tracy', {font:F.medium, size:12.5, lh:17, name:'to'}));
    add(f, mkText('95376', {font:F.mono, size:10, lh:14, color:C.ink3, name:'to-zip'}));
    return toComp(f);
  }, hList);
  /* ---------- Shell: TopBar, Sidebar/Root, Drawer ---------- */
  const hShell = sect('Shell', 'TopBar is the 12x22 chrome bar; Sidebar/Root is the assembled 248px rail; Drawer is the 760px right sheet.');
  makeComp('TopBar', () => toComp(buildTopBarNode('desktop', 'Dashboard', 'Overview')), hShell);
  makeComp('Sidebar/Root', () => toComp(buildSidebarNode('dashboard', 0).node), hShell);
  makeComp('Drawer', () => {
    const f = mkFrame('Drawer', {dir:'V', gap:0, fill:C.canvas, w:760, clip:true});
    const hd = mkFrame('dhd', {dir:'H', gap:14, pad:[16,20,16,20], fill:C.chrome, align:'MIN'});
    add(f, hd, {hFill:true});
    const hb = mkFrame('hb', {dir:'V', gap:3});
    add(hd, hb, {hFill:true});
    add(hb, mkText('TRK-CARR-US-00142-004', {font:F.dispBold, size:21, lh:26, ls:0.3, color:C.white, name:'title'}), {hFill:true});
    add(hb, mkText('Mack Granite 64FR - Out of Service - DVIR defect', {size:12, lh:16, color:C.inkInv2, name:'sub'}), {hFill:true});
    add(hd, mkText('X', {size:18, lh:22, color:C.inkInv2}));
    const body = mkFrame('dbody', {dir:'V', gap:16, pad:[18,20,40,20]});
    add(f, body, {hFill:true});
    const card = mkFrame('panel', {dir:'V', gap:0, fill:C.panel, stroke:C.line, radius:10, clip:true});
    add(body, card, {hFill:true});
    const ph = inst('Panel', {header:'title+hint'});
    add(card, ph, {hFill:true});
    setText(ph, 'title', 'Asset record'); setText(ph, 'hint', 'CO-10 / CO-11');
    const kvbox = mkFrame('dl', {dir:'V', gap:2, pad:[14,16,16,16]});
    add(card, kvbox, {hFill:true});
    [['VIN','1M2AX07C1KM021847'],['Plate','6BHT031 - CA'],['Registration expiry','2026-07-31 - 7 days'],['Home yard','Tracy Staging']].forEach(kv2 => {
      const kv = inst('KV Row', {state:'default'});
      add(kvbox, kv, {hFill:true});
      setText(kv, 'key', kv2[0]); setText(kv, 'value', kv2[1]);
      const ch = kv.findOne(n => n.type === 'INSTANCE' && n.name === 'chip'); if (ch) ch.visible = false;
      const sfx = kv.findOne(n => n.type === 'TEXT' && n.name === 'suffix'); if (sfx) sfx.visible = false;
    });
    const nt = inst('Note', {tone:'red'});
    add(body, nt, {hFill:true});
    setText(nt, 'body', 'Dispatch is blocked until the DVIR defect is cleared (MEC-001 / MEC-003).');
    const ft = mkFrame('dfoot', {dir:'H', gap:9, just:'MAX', pad:[13,20,13,20], fill:C.panel, stroke:C.line, sides:[1,0,0,0]});
    add(f, ft, {hFill:true});
    const b1 = inst('Button', {kind:'secondary', size:'md', state:'default'}); setBtn(b1, 'Close', 'secondary'); add(ft, b1);
    const b2 = inst('Button', {kind:'primary', size:'md', state:'default'}); setBtn(b2, 'Schedule maintenance', 'primary'); add(ft, b2);
    return toComp(f);
  }, hShell);
  console.log('02 Components - ' + Object.keys(COMP).length + ' components / sets built');
}

/* =============================================================== 9. RUN PART 1 */
(async () => {
  try {
    console.log('mySHIPR Carrier Console - build part 1 of 3 (foundations + components)');
    await loadFonts();
    await cleanupStyles();
    await resetPage('01 Foundations');
    await resetPage('02 Components');
    await figma.setCurrentPageAsync(P['01 Foundations']);
    await buildTokens();
    buildFoundations();
    await figma.setCurrentPageAsync(P['02 Components']);
    buildComponents();
    console.log('PART 1 DONE. Next: paste and run part2-screens.js');
    if (typeof figma.notify === 'function') figma.notify('mySHIPR part 1 done - foundations + components');
  } catch (e) {
    console.error('PART 1 FAILED:', (e && e.message) ? e.message : e);
    throw e;
  }
})();
