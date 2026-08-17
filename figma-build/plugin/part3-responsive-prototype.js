/* =============================================================================
 * mySHIPR - Carrier Console  ·  PART 3 of 3  ·  responsive frames + prototype
 * -----------------------------------------------------------------------------
 * RUN PART 1 AND PART 2 FIRST.
 *   part 1 builds the component library on "02 Components" (looked up by name)
 *   part 2 builds the 12 desktop frames on "03 Screens - Desktop" (wired here)
 * If either is missing this script stops with a clear console error.
 *
 * HOW TO RUN (browser, no desktop app needed)
 *   1. Open the same Figma file in the browser.
 *   2. Run the community plugin "Scripter".
 *   3. Paste this ENTIRE file in and press Run (Cmd/Ctrl+Enter).
 *   Re-running is safe: it wipes and rebuilds only pages 04 and 05, and it
 *   overwrites (never appends to) the reactions on the page-03 sidebar items.
 *
 * SCRIPTER-SAFE: no plugin UI, no plugin-close call, progress via console.log.
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

/* ========================================================== 7. SCREEN RENDERER
 * One data-driven renderer builds desktop, tablet and mobile from the same spec.
 * Containers (screen frame, grid rows, panel shells) are Auto Layout frames;
 * every piece of CONTENT is an instance of a component from "02 Components".
 * ========================================================================== */
function contentWidth(mode){
  return (mode === 'desktop' ? DESK_W - SIDE_W - 44 : (mode === 'tablet' ? TAB_W - 28 : MOB_W - 28));
}
function colWidths(cols, innerW){
  const out = cols.map(c => c.w || 90);
  const fixed = out.reduce((a, b) => a + b, 0);
  const gi = cols.reduce((acc, c, i) => c.grow ? i : acc, -1);
  if (gi >= 0 && innerW > fixed) out[gi] += (innerW - fixed);
  return out;
}
function setBar(bi, pct, tone, label){
  if (!bi) return;
  bi.visible = true;
  const track = bi.children[0], val = bi.children[1];
  if (val) val.characters = String(label == null ? '' : label);
  const col = tone === 'amber' ? C.sign : (TONE[tone] ? TONE[tone].solid : C.green);
  const f = track && track.children[0];
  if (f){
    safe(() => { f.fills = solid(col); });
    safe(() => { f.layoutSizingHorizontal = 'FIXED'; f.resize(Math.max(2, track.width * (pct || 0) / 100), track.height || 7); });
  }
}
/** write one Table/Row instance from a cell-descriptor array */
function fillRow(row, widths, cells){
  for (let i = 0; i < 10; i++){
    const cell = row.children[i];
    if (!cell) continue;
    if (i >= widths.length){ cell.visible = false; continue; }
    cell.visible = true;
    fixW(cell, widths[i]);
    const d = cells[i] || {};
    const box = cell.children[0], main = cell.children[1], sub = cell.children[2],
          chips = cell.children[3], sub2 = cell.children[4], bar = cell.children[5], acts = cell.children[6];
    if (box) box.visible = !!d.box;
    if (main){
      if (d.v == null || d.v === '') main.visible = false;
      else {
        main.visible = true;
        main.fontName = d.mono ? (d.b ? F.monoSemi : F.mono) : (d.b ? F.semi : F.body);
        main.characters = String(d.v);
        main.fontSize = d.mono ? 11.5 : 12.5;
        main.lineHeight = {value: d.mono ? 16 : 17, unit:'PIXELS'};
        safe(() => { main.fills = solid(d.color || (d.hi ? C.brand : C.ink)); });
        if (d.align) main.textAlignHorizontal = d.align;
      }
    }
    if (sub){
      if (d.sub){
        sub.visible = true;
        sub.fontName = d.subMono ? F.mono : F.body;
        sub.characters = String(d.sub);
        sub.fontSize = d.subMono ? 11 : 11;
        safe(() => { sub.fills = solid(d.subColor || C.ink3); });
      } else sub.visible = false;
    }
    if (chips){
      if (d.chip){
        chips.visible = true;
        setChip(chips.children[0], d.chip.tone, d.chip.t, d.chip.plain);
        if (d.chip2) setChip(chips.children[1], d.chip2.tone, d.chip2.t, d.chip2.plain);
        else if (chips.children[1]) chips.children[1].visible = false;
      } else chips.visible = false;
    }
    if (sub2){
      if (d.sub2){
        sub2.visible = true;
        sub2.characters = String(d.sub2);
        safe(() => { sub2.fills = solid(d.sub2Color || C.redInk); });
      } else sub2.visible = false;
    }
    if (bar){ if (d.bar) setBar(bar, d.bar.pct, d.bar.tone, d.bar.v); else bar.visible = false; }
    if (acts){
      if (d.btns && d.btns.length){
        acts.visible = true;
        [0,1].forEach(ix => {
          const b = acts.children[ix];
          if (!b) return;
          if (d.btns[ix]) setBtn(b, d.btns[ix].t, d.btns[ix].kind);
          else b.visible = false;
        });
      } else acts.visible = false;
    }
  }
}
function renderTable(card, t, innerW){
  const widths = colWidths(t.cols, innerW);
  const tblW = widths.reduce((a, b) => a + b, 0);
  const wrap = mkFrame('tblwrap', {dir:'V', gap:0, clip:true});
  add(card, wrap, {hFill:true});
  const hdr = inst('Table/Header');
  add(wrap, hdr);
  fixW(hdr, tblW);
  for (let i = 0; i < 10; i++){
    const c = hdr.children[i];
    if (!c) continue;
    if (i >= widths.length){ c.visible = false; continue; }
    c.visible = true; fixW(c, widths[i]);
    const lb = c.children[0];
    if (lb) lb.characters = String(t.cols[i].h || '');
  }
  t.rows.forEach(r => {
    const row = inst('Table/Row', {state: r.state || 'default'});
    add(wrap, row);
    fixW(row, tblW);
    fillRow(row, widths, r.cells);
  });
}
function renderPanel(parent, p, w, mode){
  const card = mkFrame('Panel — ' + (p.title || ''), {dir:'V', gap:0, fill:C.panel, stroke:C.line, radius:10, clip:true});
  add(parent, card, {hFill:true});
  if (w) fixW(card, w);
  const innerW = (w || contentWidth(mode)) - 2;
  if (p.title){
    const hd = inst('Panel', {header: p.action ? 'title+action' : (p.hint ? 'title+hint' : 'title-only')});
    add(card, hd, {hFill:true});
    setText(hd, 'title', p.title);
    if (p.hint) setText(hd, 'hint', p.hint);
    if (p.action) setBtn(hd.findOne(n => n.type === 'INSTANCE' && n.name === 'action'), p.action.t, p.action.kind);
  }
  (p.parts || []).forEach(part => {
    if (part.t === 'filters'){
      const fr = mkFrame('filters', {dir:'H', gap:6, wrap:true, crossGap:6, align:'CENTER',
        pad:[12,16,12,16], stroke:C.line, sides:[0,0,1,0]});
      add(card, fr, {hFill:true});
      add(fr, mkText(part.label, {font:F.semi, size:10.5, lh:14, ls:0.84, color:C.ink3, case:'UPPER'}));
      part.chips.forEach(c => {
        const ci = inst('Chip/Filter', {state: c.on ? 'on' : 'off', count: c.n == null ? 'no' : 'yes'});
        setText(ci, 'label', c.t);
        if (c.n != null) setText(ci, 'count', String(c.n));
        add(fr, ci);
      });
    }
    else if (part.t === 'table') renderTable(card, part, innerW);
    else if (part.t === 'pager'){
      const pg = inst('Pager');
      add(card, pg, {hFill:true});
      setText(pg, 'range', part.range);
    }
    else if (part.t === 'list'){
      part.items.forEach(it => {
        const li = inst('List Item', {sev: it.sev, unread: it.unread ? 'yes' : 'no'});
        add(card, li, {hFill:true});
        setText(li, 'title', it.title);
        setText(li, 'body', it.body);
        setText(li, 'code', it.code);
        setText(li, 'time', it.time);
        const act = li.findOne(n => n.type === 'INSTANCE' && n.name === 'action');
        if (it.btn) setBtn(act, it.btn, 'secondary'); else if (act) act.visible = false;
      });
    }
    else if (part.t === 'bars'){
      const box = mkFrame('bars', {dir:'V', gap:2, pad:[12,16,14,16]});
      add(card, box, {hFill:true});
      part.rows.forEach(r => {
        const br = inst('Bar Row', {tone: r.tone || 'green'});
        add(box, br, {hFill:true});
        setText(br, 'label', r.label);
        const sub = br.findOne(n => n.type === 'TEXT' && n.name === 'sub');
        if (sub){ if (r.sub){ sub.visible = true; sub.characters = r.sub; } else sub.visible = false; }
        setText(br, 'value', r.value);
        const track = br.children[1], f = track && track.children[0];
        if (f) safe(() => { f.layoutSizingHorizontal = 'FIXED'; f.resize(Math.max(2, track.width * (r.pct || 0) / 100), 9); });
      });
    }
    else if (part.t === 'kv'){
      const box = mkFrame('dl', {dir:'V', gap:2, pad:[14,16,16,16]});
      add(card, box, {hFill:true});
      part.rows.forEach(r => {
        const kv = inst('KV Row', {state: r.empty ? 'empty' : 'default'});
        add(box, kv, {hFill:true});
        setText(kv, 'key', r.k);
        setText(kv, 'value', r.v);
        const sfx = kv.findOne(n => n.type === 'TEXT' && n.name === 'suffix');
        if (sfx){ if (r.sfx){ sfx.visible = true; sfx.characters = r.sfx; } else sfx.visible = false; }
        const ch = kv.findOne(n => n.type === 'INSTANCE' && n.name === 'chip');
        if (r.chip) setChip(ch, r.chip.tone, r.chip.t, true); else if (ch) ch.visible = false;
      });
    }
    else if (part.t === 'stops'){
      const box = mkFrame('stops', {dir:'V', gap:0, pad:[4,16,8,16], fill:C.panel, stroke:C.line, radius:10});
      add(card, box, {hFill:true});
      part.rows.forEach(r => {
        const sl = inst('Stop Line', {kind: r.k === 'P' ? 'pickup' : 'drop'});
        add(box, sl, {hFill:true});
        setText(sl, 'loc', r.loc);
        setText(sl, 'zip', r.zip);
        setText(sl, 'meta', r.meta);
        const ch = sl.findOne(n => n.type === 'INSTANCE' && n.name === 'chip');
        if (r.chip) setChip(ch, 'grey', r.chip, true); else if (ch) ch.visible = false;
      });
    }
    else if (part.t === 'empty'){
      const es = inst('EmptyState', {kind: part.kind});
      add(card, es, {hFill:true});
      setText(es, 'title', part.title);
      setText(es, 'body', part.body);
      const code = es.findOne(n => n.type === 'TEXT' && n.name === 'code');
      if (code){ if (part.code){ code.visible = true; code.characters = part.code; } else code.visible = false; }
      const act = es.findOne(n => n.type === 'INSTANCE' && n.name === 'action');
      if (part.action) setBtn(act, part.action, 'secondary'); else if (act) act.visible = false;
    }
    else if (part.t === 'text'){
      const box = mkFrame('body', {dir:'V', gap:8, pad:[14,16,16,16]});
      add(card, box, {hFill:true});
      part.lines.forEach(l => add(box, mkText(l, {size:12.5, lh:18, color:C.ink2}), {hFill:true}));
      if (part.btns){
        const br = mkFrame('btns', {dir:'H', gap:8, wrap:true, crossGap:8});
        add(box, br, {hFill:true});
        part.btns.forEach(b => { const bi = inst('Button', {kind:b.kind || 'secondary', size:'md', state:'default'}); setBtn(bi, b.t, b.kind || 'secondary'); add(br, bi); });
      }
    }
    else if (part.t === 'donut'){
      const box = mkFrame('donut', {dir:'V', gap:14, pad:[18,16,18,16], align:'CENTER'});
      add(card, box, {hFill:true});
      const ring = mkFrame('ring', {dir:'N', w:210, h:210});
      add(box, ring);
      let a0 = -Math.PI / 2;
      part.segments.forEach(sg => {
        const e = figma.createEllipse();
        e.resize(210, 210);
        e.fills = solid(sg.color);
        e.arcData = {startingAngle: a0, endingAngle: a0 + Math.PI * 2 * sg.pct / 100, innerRadius: 0.62};
        e.name = sg.label;
        ring.appendChild(e); e.x = 0; e.y = 0;
        a0 += Math.PI * 2 * sg.pct / 100;
      });
      const lg = mkFrame('legend', {dir:'H', gap:14, wrap:true, crossGap:8, just:'CENTER'});
      add(box, lg, {hFill:true});
      part.segments.forEach(sg => {
        const r = mkFrame('lg', {dir:'H', gap:6, align:'CENTER'});
        add(r, mkFrame('sw', {dir:'V', w:9, h:9, radius:5, fill:sg.color}));
        add(r, mkText(sg.label, {size:11, lh:15, color:C.ink2}));
        add(lg, r);
      });
    }
  });
  return card;
}
function renderBlocks(parent, blocks, mode){
  const cw = contentWidth(mode);
  blocks.forEach(b => {
    if (b.t === 'banner'){
      const bn = inst('Banner', {tone: b.tone, action: b.btns ? 'yes' : 'no'});
      add(parent, bn, {hFill:true});
      setText(bn, 'title', b.title);
      setText(bn, 'body', b.body);
      if (b.btns){
        const acts = bn.findOne(n => n.type === 'FRAME' && n.name === 'acts');
        if (acts){
          [0,1].forEach(i => {
            const btn = acts.children[i];
            if (!btn) return;
            if (b.btns[i]) setBtn(btn, b.btns[i].t, b.btns[i].kind || 'secondary');
            else btn.visible = false;
          });
        }
      }
    }
    else if (b.t === 'pulse'){
      const strip = mkFrame('pulse', {dir:'H', gap:1, fill:C.line, stroke:C.line, radius:10, clip:true,
        wrap: mode !== 'desktop', crossGap:1});
      add(parent, strip, {hFill:true});
      const per = mode === 'desktop' ? 5 : (mode === 'tablet' ? 3 : 2);
      const cellW = (cw - (per - 1)) / per;
      b.cells.forEach(c => {
        const pc = inst('Pulse Cell');
        add(strip, pc, mode === 'desktop' ? {hFill:true} : {hFix: cellW});
        setText(pc, 'value', c.n);
        setText(pc, 'label', c.label);
        const dot = pc.findOne(n => n.name === 'dot');
        if (dot) safe(() => { dot.fills = solid(TONE[c.tone] ? TONE[c.tone].solid : C.green); });
      });
    }
    else if (b.t === 'kpi'){
      const per = mode === 'desktop' ? b.cards.length : (mode === 'tablet' ? 2 : 1);
      const row = mkFrame('kpi row', {dir:'H', gap:16, wrap: mode !== 'desktop', crossGap:16, align:'MIN'});
      add(parent, row, {hFill:true});
      const cellW = (cw - 16 * (per - 1)) / per;
      b.cards.forEach(c => {
        const k = inst('KPI Card', {tone: c.tone || 'default'});
        add(row, k, mode === 'desktop' ? {hFill:true} : {hFix: cellW});
        setText(k, 'label', c.label);
        setText(k, 'value', c.value);
        const sm = k.findOne(n => n.type === 'TEXT' && n.name === 'value-small');
        if (sm){ if (c.small){ sm.visible = true; sm.characters = c.small; } else sm.visible = false; }
        setText(k, 'sub', c.sub);
      });
    }
    else if (b.t === 'cols'){
      const stack = mode === 'desktop' ? 'H' : 'V';
      const row = mkFrame('grid', {dir:stack, gap:16, align:'MIN'});
      add(parent, row, {hFill:true});
      const total = b.ratio.reduce((a, x) => a + x, 0);
      b.cols.forEach((p, i) => {
        const w = mode === 'desktop' ? Math.round((cw - 16 * (b.cols.length - 1)) * b.ratio[i] / total) : null;
        const holder = mkFrame('col', {dir:'V', gap:16});
        add(row, holder, mode === 'desktop' ? {hFix: w} : {hFill:true});
        (Array.isArray(p) ? p : [p]).forEach(pp => renderPanel(holder, pp, mode === 'desktop' ? w : null, mode));
      });
    }
    else if (b.t === 'panel') renderPanel(parent, b, null, mode);
    else if (b.t === 'note'){
      const n = inst('Note', {tone: b.tone || 'amber'});
      add(parent, n, {hFill:true});
      setText(n, 'body', b.body);
    }
    else if (b.t === 'legend'){
      const row = mkFrame('legend-src', {dir:'H', gap:8, wrap:true, crossGap:8, pad:[16,0,0,0], stroke:C.line, sides:[1,0,0,0]});
      row.paddingTop = 16;
      add(parent, row, {hFill:true});
      b.items.forEach(t => { const c = inst('Legend Chip'); setText(c, 'label', t); add(row, c); });
    }
    else if (b.t === 'spacer'){
      add(parent, mkFrame('spacer', {dir:'V', h: b.h || 6}), {hFill:true});
    }
  });
}
/**
 * renderScreen — returns { frame, items } where items are the 12 Sidebar/Item
 * instances (part 3 wires ON_CLICK → NAVIGATE onto exactly these).
 */
function renderScreen(spec, mode){
  const W = mode === 'desktop' ? DESK_W : (mode === 'tablet' ? TAB_W : MOB_W);
  const pad = mode === 'desktop' ? 22 : 14;
  const frame = mkFrame(spec.frame + (mode === 'desktop' ? '' : ' — ' + (mode === 'tablet' ? 'Tablet 900' : 'Mobile 375')),
    {dir:'H', gap:0, fill:C.canvas, w:W, clip:true});
  let items = null, sideNode = null;
  if (mode === 'desktop'){
    const sb = buildSidebarNode(spec.key, spec.subIdx || 0);
    add(frame, sb.node, {cV:'STRETCH'});
    items = sb.items; sideNode = sb.node;
  }
  const main = mkFrame('Main', {dir:'V', gap:0});
  add(frame, main, {hFill:true});
  if (mode === 'desktop'){
    const tb = inst('TopBar');
    add(main, tb, {hFill:true});
    setText(tb, 'crumb-title', spec.nav);
    setText(tb, 'crumb-sub', spec.sub);
  } else {
    add(main, buildTopBarNode(mode, spec.nav, spec.sub), {hFill:true});
  }
  const content = mkFrame('Content', {dir:'V', gap:16, pad:[pad, pad, mode === 'desktop' ? 60 : 70, pad]});
  add(main, content, {hFill:true});
  /* page header — .pagehd */
  const ph = mkFrame('pagehd', {dir: mode === 'desktop' ? 'H' : 'V', gap:16, align: mode === 'desktop' ? 'MAX' : 'MIN', just:'SPACE_BETWEEN'});
  add(content, ph, {hFill:true});
  const phl = mkFrame('l', {dir:'V', gap:4});
  add(ph, phl, mode === 'desktop' ? {} : {hFill:true});
  add(phl, mkText(spec.title, {font:F.dispBold, size: mode === 'desktop' ? 26 : 22, lh: mode === 'desktop' ? 31 : 27, ls:0.3}), {hFill:true});
  if (spec.desc) add(phl, mkText(spec.desc, {size:13, lh:19, color:C.ink2}), mode === 'desktop' ? {hFix: Math.min(720, contentWidth(mode) - 260)} : {hFill:true});
  if (spec.actions){
    const acts = mkFrame('acts', {dir:'H', gap:8, wrap:true, crossGap:8});
    add(ph, acts);
    spec.actions.forEach(a => { const b = inst('Button', {kind:a.kind || 'secondary', size:'md', state:'default'}); setBtn(b, a.t, a.kind || 'secondary'); add(acts, b); });
  }
  renderBlocks(content, spec.blocks || [], mode);
  /* Auto Layout cannot FILL a counter axis while the parent hugs it, so pin the
     frame height once the content has measured, then let the rail fill it and
     the nav column push the side footer to the bottom — as in the CSS. */
  const h = Math.max(frame.height, 900);
  safe(() => { frame.counterAxisSizingMode = 'FIXED'; frame.resize(W, h); });
  if (sideNode){
    safe(() => { sideNode.layoutSizingVertical = 'FILL'; });
    const nav = sideNode.findOne(n => n.type === 'FRAME' && n.name === 'nav');
    if (nav) safe(() => { nav.layoutSizingVertical = 'FILL'; });
  }
  return {frame, items};
}

/* ============================================================ 8. SCREEN DATA
 * Records are the real ones out of the HTML (TRUCKS, DRIVERS, SHIPMENTS, TRIPS,
 * YARDS, DETENTION, NOTIFS, BIDS) — no lorem, no invented IDs.
 * ========================================================================== */
const CHK = {box:true};
const SCREENS = [
/* ---------------------------------------------------------------- 1 DASHBOARD */
{key:'dashboard', subIdx:0, nav:'Dashboard', sub:'Overview', frame:'01 Dashboard — Overview',
 title:'Fleet Operations Overview',
 desc:'Live snapshot of Apex Freight across the US / CA / MX network — assets, drivers, tenders, loads and compliance, all on one page.',
 blocks:[
  {t:'banner', tone:'crit', title:'1 required compliance document outstanding',
   body:'CO-07 lists eight mandatory carrier documents. Profile completion is blocked at 88% until all are uploaded.',
   btns:[{t:'Go to documents', kind:'danger'}]},
  {t:'pulse', cells:[
   {n:'3', label:'Trucks available', tone:'green'},
   {n:'2', label:'Out of service / halt', tone:'red'},
   {n:'2', label:'Drivers available', tone:'green'},
   {n:'4', label:'Drivers on duty', tone:'amber'},
   {n:'2', label:'Non-dispatchable', tone:'red'}]},
  {t:'kpi', cards:[
   {label:'Fleet size', value:'8', sub:'3 available · 5 not dispatchable', tone:'default'},
   {label:'In transit', value:'1', sub:'Master Data asset status', tone:'amber'},
   {label:'Tenders open', value:'2', sub:'awaiting accept / decline', tone:'red'},
   {label:'Awaiting assignment', value:'2', sub:'accepted, no asset selected', tone:'amber'},
   {label:'Trips on going', value:'3', sub:'1 scheduled', tone:'blue'},
   {label:'POD outstanding', value:'1', sub:'awaiting close-out', tone:'grey'}]},
  {t:'cols', ratio:[1.6,1], cols:[
   {title:'Fleet by asset status', hint:'interactive · Master Data — 7 values', parts:[{t:'bars', rows:[
     {label:'Available', value:'3', pct:100, tone:'green'},
     {label:'Unavailable', value:'1', pct:33, tone:'blue'},
     {label:'In Transit', value:'1', pct:33, tone:'amber'},
     {label:'Halt', value:'1', pct:33, tone:'red'},
     {label:'At Pickup', value:'0', pct:0, tone:'grey'},
     {label:'At Delivery/Dump', value:'1', pct:33, tone:'blue'},
     {label:'Out of Service', value:'1', pct:33, tone:'red'}]}]},
   {title:'Drivers by dispatch eligibility', hint:'interactive · FMCSA gate OPS-05 / DRV-002', parts:[{t:'donut', segments:[
     {label:'Dispatchable', pct:62.5, color:C.green},
     {label:'Verification pending', pct:12.5, color:C.amber},
     {label:'Suspended — compliance', pct:12.5, color:C.red},
     {label:'Uninsured (CO-18)', pct:12.5, color:C.grey}]}]}]},
  {t:'cols', ratio:[1,1], cols:[
   {title:'Hours of Service — nearing limit', hint:'ELD feed · fleet-wide', parts:[{t:'list', items:[
     {sev:'crit', unread:false, title:'Sofia Torres', body:'OFF_DUTY · 0.0 h remaining · San Jose Hub', code:'TEL-003 · 30 min warning', time:'0.0 h'},
     {sev:'ok', unread:false, title:'Priya Nair', body:'DRIVING · 4.0 h remaining · CA-99 near Elk Grove, CA', code:'TRIP-58022', time:'OK'},
     {sev:'ok', unread:false, title:'Marcus Reyes', body:'DRIVING · 6.5 h remaining · I-580 near Livermore, CA', code:'TRIP-58021', time:'OK'},
     {sev:'warn', unread:false, title:'Tyler Brooks', body:'ON_DUTY_NOT_DRIVING · 7.1 h remaining · Tracy Staging', code:'TRIP-58024', time:'OK'}]}]},
   {title:'Outstanding payments', hint:'4 need action', parts:[{t:'list', items:[
     {sev:'warn', unread:false, title:'PMT-CARR-US-00142-0001 · $2,380', body:'Load SHP-FTL-10003 · due 2026-07-30', code:'Pending', time:'Pending', btn:'Approve'},
     {sev:'info', unread:false, title:'PMT-CARR-US-00142-0002 · $1,180', body:'Load SHP-RCR-10005 · due 2026-07-29', code:'Approved', time:'Approved', btn:'Pay now'},
     {sev:'crit', unread:false, title:'PMT-CARR-US-00142-0003 · $640', body:'Load SHP-LTL-10002 · due 2026-07-25 · rate mismatch vs rate confirmation', code:'Disputed', time:'Disputed'},
     {sev:'grey', unread:false, title:'PMT-CARR-US-00142-0004 · $1,920', body:'Load SHP-FTL-10005 · due 2026-07-20', code:'Paid', time:'Paid'}]}]}]},
  {t:'legend', items:['Master Data — asset & driver status','Auth Services BRD V3','Shipment Execution OPS-01…OPS-12','Carrier Onboarding CO-01…CO-30']}
 ]},
/* ------------------------------------------------------------------- 2 FLEET */
{key:'fleet', subIdx:0, nav:'Fleet', sub:'All Vehicles', frame:'02 Fleet — All Vehicles',
 title:'All Vehicles',
 desc:'Every field captured at CO-10 and validated at CO-11 — licence plate, plate state, registration expiry, make and model. Rows open the full asset record.',
 actions:[{t:'Register truck', kind:'primary'},{t:'Bulk upload', kind:'secondary'}],
 blocks:[
  {t:'panel', title:'Fleet', hint:'8 vehicles', parts:[
   {t:'filters', label:'Asset status', chips:[
    {t:'All', n:8, on:true},{t:'Available', n:3},{t:'Unavailable', n:1},{t:'In Transit', n:1},
    {t:'Halt', n:1},{t:'At Pickup', n:0},{t:'At Delivery/Dump', n:1},{t:'Out of Service', n:1}]},
   {t:'table',
    cols:[{h:'', w:48},{h:'Truck', w:148},{h:'Type', w:121},{h:'Make / Model', w:130},{h:'Plate', w:84},
          {h:'Registration expiry', w:174},{h:'Asset status', w:169},{h:'CO-11', w:150},{h:'Home yard', w:122, grow:true}],
    rows:[
     {state:'blocked', cells:[CHK,
      {v:'001', mono:true, hi:true, b:true, sub:'1FUJGLDR5CLBP8834', subMono:true},
      {v:'Semi Truck (Sleeper Cab)', b:true},{v:'Freightliner Cascadia 126'},
      {v:'8ZTK492', mono:true, sub:'CA', subMono:true},
      {v:'2027-02-28', mono:true},
      {chip:{tone:'amber', t:'In Transit'}, sub2:'dispatch blocked'},
      {chip:{tone:'green', t:'Serviceable', plain:true}},{v:'San Jose Hub'}]},
     {cells:[CHK,
      {v:'002', mono:true, hi:true, b:true, sub:'3AKJHHDR8LSLR2210', subMono:true},
      {v:'Semi Truck (Day Cab)', b:true},{v:'Kenworth T680'},
      {v:'9LMD778', mono:true, sub:'CA', subMono:true},
      {v:'2026-08-14', mono:true, sub:'21 days', subColor:C.amber},
      {chip:{tone:'green', t:'Available'}},
      {chip:{tone:'green', t:'Serviceable', plain:true}},{v:'San Jose Hub'}]},
     {cells:[CHK,
      {v:'003', mono:true, hi:true, b:true, sub:'1XKYDP9X4MJ415522', subMono:true},
      {v:'Semi Truck (Sleeper Cab)', b:true},{v:'Peterbilt 579'},
      {v:'7RQP210', mono:true, sub:'NV', subMono:true},
      {v:'2027-05-30', mono:true},
      {chip:{tone:'green', t:'Available'}},
      {chip:{tone:'green', t:'Serviceable', plain:true}},{v:'Sacramento Depot'}]},
     {state:'blocked', cells:[CHK,
      {v:'004', mono:true, hi:true, b:true, sub:'1M2AX07C1KM021847', subMono:true},
      {v:'Dump Truck (Standard)', b:true, sub:'Standard Dump Truck'},{v:'Mack Granite 64FR'},
      {v:'6BHT031', mono:true, sub:'CA', subMono:true},
      {v:'2026-07-31', mono:true, sub:'7 days', subColor:C.red},
      {chip:{tone:'red', t:'Out of Service'}, sub2:'dispatch blocked'},
      {chip:{tone:'red', t:'Not serviceable', plain:true}},{v:'Tracy Staging'}]},
     {state:'blocked', cells:[CHK,
      {v:'005', mono:true, hi:true, b:true, sub:'1M2AX13C4LM030019', subMono:true},
      {v:'Dump Truck (Articulated)', b:true, sub:'Articulated Dump Truck (ADT)'},{v:'Volvo A40G'},
      {v:'5KWD884', mono:true, sub:'CA', subMono:true},
      {v:'2027-01-15', mono:true},
      {chip:{tone:'blue', t:'At Delivery/Dump'}, sub2:'dispatch blocked'},
      {chip:{tone:'green', t:'Serviceable', plain:true}},{v:'Tracy Staging'}]},
     {cells:[CHK,
      {v:'006', mono:true, hi:true, b:true, sub:'2FZHAZCV1XAH12290', subMono:true},
      {v:'Bobtail (No Trailer)', b:true},{v:'International LT625'},
      {v:'4NPC556', mono:true, sub:'CA', subMono:true},
      {v:'2027-03-20', mono:true},
      {chip:{tone:'green', t:'Available'}},
      {chip:{tone:'green', t:'Serviceable', plain:true}},{v:'San Jose Hub'}]}]},
   {t:'pager', range:'Showing 1–6 of 8'}]},
  {t:'note', tone:'amber', body:'Rows shaded red are not dispatchable — asset status is Out of Service or Halt, so allows_dispatch is false. The load assignment wizard filters these out automatically (OPS-03).'},
  {t:'legend', items:['CO-10 Truck Registration','CO-11 DMV validation','Master Data §1.2 truck types','Master Data asset status','Auth Services BRD V3 — FLEET']}
 ]},
/* ----------------------------------------------------------------- 3 DRIVERS */
{key:'drivers', subIdx:0, nav:'Drivers', sub:'All Drivers', frame:'03 Drivers — All Drivers',
 title:'All Drivers',
 desc:'Click any driver for their full profile — status, documents, HOS, ratings, earnings, licence and insurance all in one place.',
 actions:[{t:'Add driver', kind:'primary'},{t:'Bulk upload', kind:'secondary'}],
 blocks:[
  {t:'panel', title:'Driver roster', hint:'8 drivers', parts:[
   {t:'filters', label:'Driver status', chips:[
    {t:'All', n:8, on:true},{t:'Offline', n:1},{t:'Available', n:2},{t:'On Duty', n:2},{t:'In Transit', n:2},{t:'Off Duty', n:1}]},
   {t:'table',
    cols:[{h:'Driver', w:140},{h:'Contact', w:210},{h:'CDL', w:130},{h:'Type', w:105},
          {h:'Status', w:135},{h:'HOS', w:130},{h:'Location', w:140},{h:'Dispatch eligibility', w:156, grow:true}],
    rows:[
     {cells:[{v:'Marcus Reyes', b:true, sub:'0001', subMono:true},
      {v:'+1 408 555 0231', mono:true, sub:'m.reyes@apexfreight.example'},
      {v:'CA D2214870', mono:true, sub:'Class A · N T'},{v:'Salaried'},
      {chip:{tone:'amber', t:'In Transit'}},{bar:{pct:59, tone:'green', v:'6.5 h'}},
      {v:'I-580 near Livermore, CA'},{chip:{tone:'green', t:'Dispatchable', plain:true}}]},
     {cells:[{v:'Priya Nair', b:true, sub:'0002', subMono:true},
      {v:'+1 408 555 0244', mono:true, sub:'p.nair@apexfreight.example'},
      {v:'CA D3390142', mono:true, sub:'Class A · T'},{v:'Salaried'},
      {chip:{tone:'amber', t:'In Transit'}},{bar:{pct:36, tone:'green', v:'4.0 h'}},
      {v:'CA-99 near Elk Grove, CA'},{chip:{tone:'green', t:'Dispatchable', plain:true}}]},
     {cells:[{v:'Rosa Martinez', b:true, sub:'0003', subMono:true},
      {v:'+1 408 555 0255', mono:true, sub:'r.martinez@apexfreight.example'},
      {v:'CA D1102244', mono:true, sub:'Class A · N'},{v:'Owner-Operator'},
      {chip:{tone:'amber', t:'On Duty'}},{bar:{pct:76, tone:'green', v:'8.4 h'}},
      {v:'San Jose Hub'},{chip:{tone:'green', t:'Dispatchable', plain:true}}]},
     {cells:[{v:'Diego Alvarez', b:true, sub:'0004', subMono:true},
      {v:'+1 408 555 0266', mono:true, sub:'d.alvarez@apexfreight.example'},
      {v:'CA D4471209', mono:true, sub:'Class A · H N'},{v:'Contractual'},
      {chip:{tone:'green', t:'Available'}},{bar:{pct:100, tone:'green', v:'11.0 h'}},
      {v:'San Jose Hub'},{chip:{tone:'green', t:'Dispatchable', plain:true}}]},
     {state:'blocked', cells:[{v:'Sofia Torres', b:true, sub:'0005', subMono:true},
      {v:'+1 408 555 0277', mono:true, sub:'s.torres@apexfreight.example'},
      {v:'CA D2298431', mono:true, sub:'Class A · T'},{v:'Salaried'},
      {chip:{tone:'grey', t:'Off Duty'}},{bar:{pct:0, tone:'red', v:'0.0 h'}},
      {v:'San Jose Hub'},
      {chip:{tone:'red', t:'Blocked'}, sub2:'Suspended — medical_cert_expiry lapsed 2026-06-15 — FMCSA compliance failed'}]},
     {cells:[{v:'James Carter', b:true, sub:'0006', subMono:true},
      {v:'+1 775 555 0188', mono:true, sub:'j.carter@apexfreight.example'},
      {v:'NV D6543210', mono:true, sub:'Class A · N X'},{v:'Contractual'},
      {chip:{tone:'green', t:'Available'}},{bar:{pct:84, tone:'green', v:'9.2 h'}},
      {v:'Sacramento Depot'},{chip:{tone:'green', t:'Dispatchable', plain:true}}]},
     {cells:[{v:'Tyler Brooks', b:true, sub:'0007', subMono:true},
      {v:'+1 209 555 0122', mono:true, sub:'t.brooks@apexfreight.example'},
      {v:'CA D5580117', mono:true, sub:'Class B'},{v:'Salaried'},
      {chip:{tone:'amber', t:'On Duty'}},{bar:{pct:65, tone:'green', v:'7.1 h'}},
      {v:'Tracy Staging'},{chip:{tone:'green', t:'Dispatchable', plain:true}}]},
     {state:'blocked', cells:[{v:'Nadia Haddad', b:true, sub:'0008', subMono:true},
      {v:'+1 916 555 0177', mono:true, sub:'n.haddad@apexfreight.example'},
      {v:'CA D6612903', mono:true, sub:'Class A · N P'},{v:'Contractual'},
      {chip:{tone:'grey', t:'Offline'}},{bar:{pct:100, tone:'green', v:'11.0 h'}},
      {v:'Sacramento Depot'},
      {chip:{tone:'red', t:'Blocked'}, sub2:'Identity verification pending (CO-19)'}]}]}]},
  {t:'note', tone:'blue', body:'Dispatch eligibility is a derived gate, not a status — FMCSA medical certificate, CDL validity, identity verification (CO-19) and insurance (CO-18) must all pass before a driver can be assigned (OPS-05 / DRV-002).'},
  {t:'legend', items:['CO-17…CO-21 Driver onboarding','Master Data — 19 driver statuses','Fields For HOS','Auth Services BRD V3 — DRVMGT']}
 ]},
/* ------------------------------------------------------------------- 4 LOADS */
{key:'loads', subIdx:0, nav:'Loads', sub:'Tenders', frame:'04 Loads — Tenders',
 title:'Tenders',
 desc:'Loads awarded to Apex Freight and awaiting a reply. Accepting the tender links the rate confirmation and moves the load to Carrier Accepted (LED-02).',
 blocks:[
  {t:'banner', tone:'info', title:'Accepting a tender is its own step',
   body:'Master Data’s lifecycle has "Carrier Accepted" as a distinct state, Ledger LED-02 makes it a carrier-dispatcher-triggered event, and DOC-026 / DOC-027 generate and sign the rate confirmation. A load is not yours to plan until the tender is accepted and the rate confirmation is signed.'},
  {t:'panel', title:'SHP-RF-10001 · FTL - Reefer', hint:'Tender expires 2026-07-24 18:00 PDT', parts:[]},
  {t:'kpi', cards:[
   {label:'Awarded rate', value:'$2,480', sub:'as bid', tone:'default'},
   {label:'Indicative break-even', value:'$2,050', sub:'from your cost per mile', tone:'default'},
   {label:'Margin', value:'$430', small:'21%', sub:'before penalties', tone:'default'},
   {label:'TONU exposure', value:'$200', sub:'truck ordered not used', tone:'amber'}]},
  {t:'cols', ratio:[1,1], cols:[
   {title:'Stops', hint:'2 stops · LIVE unload', parts:[{t:'stops', rows:[
     {k:'P', loc:'Sacramento, CA', zip:'95814', meta:'2026-07-26   08:00 – 12:00 UTC     22 pallets     38,400 lbs', chip:'LIVE'},
     {k:'D', loc:'San Jose, CA', zip:'95112', meta:'2026-07-26   18:00 – 22:00 UTC     22 pallets     38,400 lbs', chip:'LIVE'}]}]},
   {title:'Load specification', hint:'Master Data §17 commodity master', parts:[{t:'kv', rows:[
     {k:'Commodity', v:'Fresh Produce', sfx:'Refrigerated Goods'},
     {k:'Equipment required', v:'53′ Reefer'},
     {k:'Temperature', v:'+2 °C · range 0 °C to +4 °C'},
     {k:'Pre-cooling', v:'', chip:{tone:'amber', t:'Required'}},
     {k:'Pallets / weight', v:'22 pallets · 38,400 lbs'},
     {k:'Rate confirmation', v:'DOC-026', chip:{tone:'amber', t:'Generated — signature required'}},
     {k:'AWB', v:'', empty:true}]}]}]},
  {t:'panel', title:'Tender decision', hint:'LED-02 · DOC-026 / DOC-027', parts:[
   {t:'text', lines:['Accepting signs the rate confirmation and moves SHP-RF-10001 to Carrier Accepted. Declining releases the load back for re-auction.'],
    btns:[{t:'Accept tender & sign rate confirmation', kind:'primary'},{t:'Decline', kind:'secondary'}]}]},
  {t:'panel', title:'SHP-LTL-10004 · LTL - Multiple Goods', hint:'Tender expires 2026-07-25 09:00 PDT', parts:[]},
  {t:'kpi', cards:[
   {label:'Awarded rate', value:'$3,120', sub:'as bid', tone:'default'},
   {label:'Indicative break-even', value:'$2,640', sub:'from your cost per mile', tone:'default'},
   {label:'Margin', value:'$480', small:'18%', sub:'before penalties', tone:'default'},
   {label:'TONU exposure', value:'$150', sub:'truck ordered not used', tone:'amber'}]},
  {t:'panel', title:'Stops', hint:'4 stops · 2 pickups, 2 deliveries', parts:[{t:'stops', rows:[
    {k:'P', loc:'San Jose, CA', zip:'95112', meta:'2026-07-27   06:00 – 09:00 UTC     14 pallets     22,000 lbs', chip:'LIVE'},
    {k:'P', loc:'Tracy, CA', zip:'95376', meta:'2026-07-27   10:30 – 12:30 UTC     12 pallets     19,200 lbs', chip:'LIVE'},
    {k:'D', loc:'Sacramento, CA', zip:'95814', meta:'2026-07-27   16:00 – 19:00 UTC     14 pallets     22,000 lbs', chip:'DROP'},
    {k:'D', loc:'San Francisco, CA', zip:'94103', meta:'2026-07-28   07:00 – 10:00 UTC     12 pallets     19,200 lbs', chip:'LUMPER'}]}]},
  {t:'legend', items:['Shipment Creation 1.2','Ledger LED-01…LED-05','DOC-026 / DOC-027 rate confirmation','Master Data — 16 shipment statuses']}
 ]},
/* ------------------------------------------------------------------- 5 TRIPS */
{key:'trips', subIdx:0, nav:'Trips', sub:'On going', frame:'05 Trips — On going',
 title:'Trips — On going',
 desc:'A trip is one truck movement against a load. Every trip links to its load, and both follow the single Master Data lifecycle. Live position for every on-going trip is also on the Dashboard Overview.',
 blocks:[
  {t:'banner', tone:'info', title:'Open question (OC-4)',
   body:'Shipments, Trips and Loads are modelled as three entities across three documents. This build treats the trip as a view over the load and adopts Master Data’s sixteen-state lifecycle, which also closes Carrier View OPEN-05.'},
  {t:'panel', title:'On going', hint:'3 trips', parts:[
   {t:'table',
    cols:[{h:'Trip', w:130},{h:'Load', w:150},{h:'Lane', w:320},{h:'Truck', w:90},
          {h:'Driver', w:150},{h:'ETA', w:190},{h:'Progress', w:116, grow:true}],
    rows:[
     {state:'clickable-hover', cells:[{v:'TRIP-58021', mono:true, hi:true, b:true},{v:'SHP-FTL-10005', mono:true},
      {v:'San Jose  →  Tracy', b:true, sub:'95112  →  95376', subMono:true},{v:'001', mono:true},
      {v:'Marcus Reyes'},{v:'2026-07-24 18:20', mono:true, sub:'PDT', subMono:true},{bar:{pct:62, tone:'amber', v:'62%'}}]},
     {cells:[{v:'TRIP-58022', mono:true, hi:true, b:true},{v:'SHP-LTL-10002', mono:true},
      {v:'Sacramento  →  San Jose', b:true, sub:'95814  →  95112', subMono:true},{v:'003', mono:true},
      {v:'Priya Nair'},{v:'2026-07-24 15:40', mono:true, sub:'PDT', subMono:true},{bar:{pct:48, tone:'amber', v:'48%'}}]},
     {cells:[{v:'TRIP-58024', mono:true, hi:true, b:true},{v:'SHP-RCR-10005', mono:true},
      {v:'Fresno  →  Modesto', b:true, sub:'93721  →  95350', subMono:true},{v:'005', mono:true},
      {v:'Tyler Brooks'},{v:'2026-07-24 11:05', mono:true, sub:'PDT', subMono:true},{bar:{pct:74, tone:'amber', v:'74%'}}]}]}]},
  {t:'legend', items:['Master Data — Shipment Status','Carrier View TRIP-01…03','FTL Master Reference status machine']}
 ]},
/* ------------------------------------------------------------- 6 DRIVER OPS */
{key:'ops', subIdx:0, nav:'Driver Ops', sub:'Detention', frame:'06 Driver Ops — Detention',
 title:'Detention',
 desc:'Detention starts at geofence arrival (GPS-004) and runs against the free time agreed for that stop. Minutes past free time are billable and must be raised before the load closes out.',
 actions:[{t:'Export', kind:'secondary'}],
 blocks:[
  {t:'banner', tone:'warn', title:'2 stops accruing detention right now',
   body:'DET-003 notifies dispatch as free time expires. Detention is not recoverable once the load is closed out (LED-05), so raise it before POD confirmation.'},
  {t:'kpi', cards:[
   {label:'Accruing now', value:'2', sub:'stops past free time', tone:'amber'},
   {label:'Billable minutes', value:'195', sub:'across all open stops', tone:'red'},
   {label:'Recoverable value', value:'$254', sub:'before close-out', tone:'blue'},
   {label:'Within free time', value:'1', sub:'no charge', tone:'grey'}]},
  {t:'panel', title:'Detention events', hint:'4', parts:[
   {t:'table',
    cols:[{h:'Event', w:95},{h:'Stop', w:110},{h:'Driver / truck', w:125},{h:'Arrived', w:110},
          {h:'Free time', w:85},{h:'Elapsed', w:85},{h:'Billable', w:85},{h:'Amount', w:95},
          {h:'Status', w:150},{h:'Action', w:206, grow:true}],
    rows:[
     {state:'blocked', cells:[
      {v:'DET-0041', mono:true, hi:true, b:true, sub:'SHP-FTL-10005', subMono:true},
      {v:'Tracy, CA — Delivery'},{v:'Marcus Reyes', b:true, sub:'001', subMono:true},
      {v:'2026-07-24 16:04', mono:true, sub:'PDT', subMono:true},
      {v:'120 min'},{v:'3h 6m', b:true},{v:'66 min', b:true, color:C.red},
      {v:'$83', b:true, sub:'at $75/h'},
      {chip:{tone:'amber', t:'Accruing'}},
      {btns:[{t:'Acknowledge', kind:'secondary'},{t:'Raise as billable', kind:'primary'}]}]},
     {state:'blocked', cells:[
      {v:'DET-0040', mono:true, hi:true, b:true, sub:'SHP-RCR-10005', subMono:true},
      {v:'Fresno Quarry, CA — Pickup'},{v:'Tyler Brooks', b:true, sub:'005', subMono:true},
      {v:'2026-07-24 06:12', mono:true, sub:'PDT', subMono:true},
      {v:'60 min'},{v:'1h 37m', b:true},{v:'37 min', b:true, color:C.red},
      {v:'$56', b:true, sub:'at $90/h'},
      {chip:{tone:'amber', t:'Accruing'}, chip2:{tone:'green', t:'Ack', plain:true}},
      {btns:[{t:'Raise as billable', kind:'primary'}]}]},
     {cells:[
      {v:'DET-0038', mono:true, hi:true, b:true, sub:'SHP-FTL-10003', subMono:true},
      {v:'Tracy, CA — Delivery'},{v:'Rosa Martinez', b:true, sub:'002', subMono:true},
      {v:'2026-07-23 15:10', mono:true, sub:'PDT', subMono:true},
      {v:'120 min'},{v:'3h 32m', b:true},{v:'92 min', b:true, color:C.red},
      {v:'$115', b:true, sub:'at $75/h'},
      {chip:{tone:'blue', t:'Billable'}, chip2:{tone:'green', t:'Ack', plain:true}},{}]},
     {cells:[
      {v:'DET-0035', mono:true, hi:true, b:true, sub:'SHP-LTL-10003', subMono:true},
      {v:'Stockton, CA — Delivery'},{v:'Rosa Martinez', b:true, sub:'002', subMono:true},
      {v:'2026-07-19 13:22', mono:true, sub:'PDT', subMono:true},
      {v:'120 min'},{v:'1h 44m', b:true},{chip:{tone:'green', t:'None', plain:true}},
      {v:'—'},
      {chip:{tone:'green', t:'Closed — within free time', plain:true}, chip2:{tone:'green', t:'Ack', plain:true}},{}]}]}]},
  {t:'note', tone:'blue', body:'Open question (OC-11): the Auth Services BRD V3 matrix gives Driver Operations to the Carrier Super Admin alone, yet every channel on these screens is addressed to dispatch — DET-005, SOS-003, MEC-002 and DSP-001…006 all name the dispatcher as the recipient. Either DRVOPS needs a Dispatcher column or the Driver BRD needs rewording.'},
  {t:'legend', items:['Driver BRD §4.14 DET-001…005','GPS-004 geofence arrival','Ledger LED-05 close-out']}
 ]},
/* ---------------------------------------------------------------------- 7 RR */
{key:'rr', subIdx:0, nav:'RR', sub:'Coming soon', frame:'07 RR — Coming soon',
 title:'RR — Rate & Auction Bidding',
 desc:'Real-time load auctions, bidding and bid history for this carrier.',
 blocks:[
  {t:'panel', parts:[{t:'empty', kind:'empty', title:'Coming soon',
   body:'Auction and bidding mechanics (lot visibility, live bidding, won / lost outcomes and bid history) are being redesigned as part of the TMS build and are not available in this console yet. The carrier-side inputs that decide auction eligibility — lanes, commodities, cost per mile and declared capacity — are managed under Settings → Capacity & Service Profile.',
   action:'Go to Capacity & Service Profile'}]},
  {t:'legend', items:['6A Carrier Eligibility & Auction Targeting','Carrier View RR-01…RR-06']}
 ]},
/* ------------------------------------------------------------------- 8 YARDS */
{key:'yards', subIdx:0, nav:'Yards', sub:'All yards', frame:'08 Yards — All yards',
 title:'All Yards',
 desc:'Yard address and geo-coordinates are captured at CO-14 — a yard without an address cannot be used for dispatch, and the coordinates drive geofencing, arrival detection and detention timing.',
 actions:[{t:'Add yard', kind:'primary'}],
 blocks:[
  {t:'panel', title:'Yards', hint:'3', parts:[
   {t:'table',
    cols:[{h:'Yard', w:130},{h:'Type (CO-14)', w:100},{h:'Subtype', w:130},{h:'Address', w:190},
          {h:'Coordinates', w:150},{h:'Truck slots', w:105},{h:'Trailer slots', w:110},
          {h:'Geofence', w:95},{h:'Status', w:136, grow:true}],
    rows:[
     {cells:[{v:'001', mono:true, hi:true, b:true, sub:'San Jose Hub'},{v:'Owned'},
      {chip:{tone:'grey', t:'STAGING', plain:true}},
      {v:'1180 Coleman Ave', sub:'San Jose, CA 95110, USA'},
      {v:'37.3654,', mono:true, sub:'-121.9245', subMono:true},
      {v:'33 / 40'},{v:'47 / 60'},{v:'300 m', mono:true},{chip:{tone:'green', t:'active'}}]},
     {cells:[{v:'002', mono:true, hi:true, b:true, sub:'Sacramento Depot'},{v:'Leased'},
      {chip:{tone:'grey', t:'DROP_AND_HOOK', plain:true}},
      {v:'4400 Power Inn Rd', sub:'Sacramento, CA 95826, USA'},
      {v:'38.5310,', mono:true, sub:'-121.4020', subMono:true},
      {v:'12 / 25'},{v:'19 / 35'},{v:'250 m', mono:true},{chip:{tone:'green', t:'active'}}]},
     {cells:[{v:'003', mono:true, hi:true, b:true, sub:'Tracy Staging'},{v:'Shared'},
      {chip:{tone:'grey', t:'FUEL_STOP', plain:true}},
      {v:'2400 Grant Line Rd', sub:'Tracy, CA 95377, USA'},
      {v:'37.7255,', mono:true, sub:'-121.4380', subMono:true},
      {v:'6 / 15'},{v:'8 / 20'},{v:'180 m', mono:true},{chip:{tone:'amber', t:'maintenance'}}]}]}]},
  {t:'note', tone:'amber', body:'Yard type and status now use the CO-14 vocabulary — Owned / Leased / Shared and active / inactive / maintenance — rather than the database values PRIVATE / LEASED / SHARED / CROSS_DOCK and ACTIVE / INACTIVE / UNDER_MAINTENANCE / CLOSED, which could not store what onboarding captured.'},
  {t:'legend', items:['CO-14 Yard onboarding','Driver BRD GPS-003/004, DET-001/002']}
 ]},
/* ----------------------------------------------------------- 9 NOTIFICATIONS */
{key:'alerts', subIdx:0, nav:'Notifications', sub:'Notifications', frame:'09 Notifications',
 title:'Notifications',
 desc:'Every alert in one place. Open any item to acknowledge it, call the driver, or join their chat thread — no need to leave this page.',
 actions:[{t:'Mark all read', kind:'secondary'}],
 blocks:[
  {t:'banner', tone:'crit', title:'SOS alert from Driver Tyler Brooks',
   body:'Emergency (911) status received with GPS 37.6390, -120.9969 on TRIP-58024. Emergency response coordinator notified. Acknowledge to confirm dispatch has seen this.',
   btns:[{t:'Acknowledge', kind:'danger'},{t:'Call driver', kind:'secondary'}]},
  {t:'panel', title:'All notifications', hint:'8 unread of 22', parts:[
   {t:'filters', label:'Category', chips:[
    {t:'All', n:22, on:true},{t:'SOS', n:1},{t:'Telematics', n:3},{t:'Documents', n:3},{t:'Assets', n:2},
    {t:'Yard', n:2},{t:'Loads', n:2},{t:'Safety', n:2},{t:'Penalties', n:1},{t:'Onboarding', n:1},
    {t:'Detention', n:2},{t:'Exceptions', n:3}]},
   {t:'list', items:[
    {sev:'crit', unread:true, title:'SOS alert from Driver Tyler Brooks',
     body:'Emergency (911) status received with GPS 37.6390, -120.9969 on TRIP-58024. Emergency response coordinator notified.', code:'CR-025 · SOS', time:'4m ago', btn:'Call driver'},
    {sev:'crit', unread:true, title:'ELD disconnected — TRK-CARR-US-00142-008',
     body:'HOS logs may be incomplete. Device TAB-4478 last synced 2026-07-23 06:02 PDT. Verify on the driver app and re-pair the device.', code:'TEL-002 · Telematics', time:'26m ago'},
    {sev:'warn', unread:true, title:'Insurance certificate expires in 19 days',
     body:'COI expires 2026-08-12. Escalation tier "3 weeks" reached per CO-09. Marketplace access is suspended automatically on expiry (DOC-011).', code:'DOC-009 · Documents', time:'1h ago'},
    {sev:'crit', unread:false, title:'Asset TRK-CARR-US-00142-004 is Out of Service',
     body:'DVIR defect reported 2026-07-19: hydraulic leak, rear tipper ram. Dispatch is blocked while the asset is Out of Service.', code:'AST-007 · Assets', time:'2h ago'},
    {sev:'warn', unread:false, title:'Asset TRK-CARR-US-00142-008 is on Halt',
     body:'Halt reported at San Jose Hub. Reason: insurance lapsed — asset withheld from dispatch pending renewal.', code:'AST-004 · Assets', time:'2h ago'},
    {sev:'warn', unread:false, title:'CDL expiring — James Carter',
     body:'CDL NV D6543210 expires 2026-09-12. Renewal at the state DMV required. Driver becomes non-dispatchable on expiry (DOC-017).', code:'DOC-016 · Documents', time:'3h ago', btn:'Call driver'},
    {sev:'warn', unread:false, title:'Medical certificate expiring — Tyler Brooks',
     body:'Medical Examiner Certificate expires 2026-07-30 — six days. Driving privileges suspend on expiry (DOC-019).', code:'DOC-018 · Documents', time:'3h ago', btn:'Call driver'},
    {sev:'warn', unread:true, title:'HOS warning — Priya Nair, 30 minutes remaining',
     body:'30 minutes remain on the driving window for TRIP-58022. Plan a safe stop. Violation is logged automatically past the limit (TEL-004).', code:'TEL-003 · Telematics', time:'42m ago'},
    {sev:'ok', unread:false, title:'Truck TRK-CARR-US-00142-001 assigned to SHP-FTL-10005',
     body:'Assignment confirmed by M. Whitfield (Dispatcher). Trailer TRL-CARR-US-00142-011 linked as PRIMARY.', code:'CR-007 · Loads', time:'8h ago'},
    {sev:'ok', unread:true, title:'Bid accepted — SHP-RF-10001',
     body:'Your bid has been accepted for Shipment SHP-RF-10001 at $2,480. Accept the tender and sign the rate confirmation to proceed.', code:'CR-005 · Loads', time:'9h ago'}]}]},
  {t:'legend', items:['Notification Types — CR / DR / AST / TEL / DOC / YD / SAF / ONB / PEN / CS','CO-09 five-tier expiry ladder']}
 ]},
/* ----------------------------------------------------------------- 10 REPORTS */
{key:'reports', subIdx:0, nav:'Reports', sub:'Operations', frame:'10 Reports — Operations',
 title:'Operations reports',
 desc:'Fleet, driver and compliance reporting. All five carrier roles hold a view right; export is restricted.',
 actions:[{t:'Export CSV', kind:'secondary'}],
 blocks:[
  {t:'kpi', cards:[
   {label:'Fleet utilisation', value:'63%', sub:'5 of 8 engaged', tone:'default'},
   {label:'Dispatchable assets', value:'3', sub:'of 8 registered', tone:'amber'},
   {label:'Compliant drivers', value:'6', sub:'of 8 on roster', tone:'blue'}]},
  {t:'kpi', cards:[
   {label:'On-time delivery', value:'94%', sub:'last 30 days', tone:'default'},
   {label:'Documents expiring ≤30 d', value:'4', sub:'carrier + driver', tone:'red'},
   {label:'Loads completed (30 d)', value:'1', sub:'across all freight types', tone:'grey'}]},
  {t:'panel', title:'Freight mix by type', hint:'Master Data — Types of Shipment', parts:[{t:'bars', rows:[
   {label:'FTL - Standard Goods', sub:'SHP-FTL', value:'3', pct:100, tone:'green'},
   {label:'FTL - Reefer', sub:'SHP-RF', value:'1', pct:33, tone:'green'},
   {label:'LTL - Multiple Goods', sub:'SHP-LTL', value:'2', pct:66, tone:'green'},
   {label:'Dump Truck', sub:'SHP-RCR', value:'2', pct:66, tone:'green'},
   {label:'Multileg', sub:'SHP-LTL', value:'1', pct:33, tone:'green'}]}]},
  {t:'panel', title:'Route profitability & revenue per mile', action:{t:'Export', kind:'secondary'}, parts:[
   {t:'table',
    cols:[{h:'Lane', w:180},{h:'Loads', w:80},{h:'Loaded miles', w:120},{h:'Deadhead', w:110},
          {h:'Revenue', w:110},{h:'RPM', w:100},{h:'Fuel', w:100},{h:'Margin vs break-even', w:346, grow:true}],
    rows:[
     {cells:[{v:'San Jose  →  Tracy', b:true},{v:'3'},{v:'186 mi'},{v:'33 mi', sub:'15% of total'},
      {v:'$5,580', b:true},{v:'$25.48', b:true},{v:'$619'},
      {v:'$960', b:true, color:C.greenInk, sub:'21% over break-even', subColor:C.ink2}]},
     {cells:[{v:'Sacramento  →  San Jose', b:true},{v:'2'},{v:'236 mi'},{v:'21 mi', sub:'8% of total'},
      {v:'$5,220', b:true},{v:'$20.31', b:true},{v:'$798'},
      {v:'$890', b:true, color:C.greenInk, sub:'21% over break-even', subColor:C.ink2}]},
     {cells:[{v:'San Jose  →  Sacramento', b:true},{v:'1'},{v:'154 mi'},{v:'18 mi', sub:'10% of total'},
      {v:'$5,100', b:true},{v:'$29.65', b:true},{v:'$512'},
      {v:'$800', b:true, color:C.greenInk, sub:'19% over break-even', subColor:C.ink2}]},
     {cells:[{v:'Fresno  →  Modesto', b:true},{v:'2'},{v:'192 mi'},{v:'44 mi', sub:'23% of total'},
      {v:'$349,650', b:true},{v:'$1,821', b:true},{v:'$1,940'},
      {v:'$58,650', b:true, color:C.greenInk, sub:'20% over break-even', subColor:C.ink2}]},
     {state:'blocked', cells:[{v:'Salinas  →  San Francisco', b:true},{v:'0'},{v:'—'},{v:'—'},
      {v:'$0'},{v:'—'},{v:'—'},
      {v:'Lost at auction', color:C.redInk, b:true, sub:'AUC-76998 · ours $1,620 vs $1,485', subColor:C.ink2}]}]}]},
  {t:'legend', items:['Auth Services BRD V3 — REP','Ledger — settlement','Master Data — Types of Shipment']}
 ]},
/* ---------------------------------------------------------------- 11 EARNINGS */
{key:'earnings', subIdx:0, nav:'Earnings', sub:'Earnings', frame:'11 Earnings — Earnings',
 title:'Earnings',
 desc:'Revenue, margin and outstanding payments in one place. Approve a pending payment to queue it for payout, pay it immediately once approved, or open a dispute chat directly with mySHIPR admin.',
 actions:[{t:'Update payment details', kind:'secondary'}],
 blocks:[
  {t:'kpi', cards:[
   {label:'Gross revenue', value:'$368,670', sub:'all loads in view', tone:'default'},
   {label:'Net margin', value:'22%', sub:'after fuel, maintenance & settlement', tone:'blue'},
   {label:'Recurring programmes', value:'$349,650', sub:'dump truck contracts', tone:'grey'},
   {label:'Outstanding balance', value:'$5,060', sub:'4 payments awaiting action', tone:'red'}]},
  {t:'panel', title:'Outstanding payments', hint:'5', parts:[
   {t:'table',
    cols:[{h:'Payment', w:240},{h:'Load', w:180},{h:'Amount', w:120},{h:'Due', w:140},
          {h:'Status', w:220},{h:'Actions', w:246, grow:true}],
    rows:[
     {cells:[{v:'PMT-CARR-US-00142-0001', mono:true, hi:true},{v:'SHP-FTL-10003', mono:true},
      {v:'$2,380', b:true},{v:'2026-07-30', mono:true},{chip:{tone:'amber', t:'Pending', plain:true}},
      {btns:[{t:'Approve', kind:'secondary'},{t:'Dispute', kind:'secondary'}]}]},
     {cells:[{v:'PMT-CARR-US-00142-0002', mono:true, hi:true},{v:'SHP-RCR-10005', mono:true},
      {v:'$1,180', b:true},{v:'2026-07-29', mono:true},{chip:{tone:'blue', t:'Approved', plain:true}},
      {btns:[{t:'Pay now', kind:'primary'},{t:'Dispute', kind:'secondary'}]}]},
     {state:'blocked', cells:[{v:'PMT-CARR-US-00142-0003', mono:true, hi:true},{v:'SHP-LTL-10002', mono:true},
      {v:'$640', b:true},{v:'2026-07-25', mono:true},
      {chip:{tone:'red', t:'Disputed', plain:true}, sub2:'Rate mismatch vs rate confirmation'},
      {btns:[{t:'Dispute', kind:'secondary'}]}]},
     {cells:[{v:'PMT-CARR-US-00142-0004', mono:true, hi:true},{v:'SHP-FTL-10005', mono:true},
      {v:'$1,920', b:true},{v:'2026-07-20', mono:true},{chip:{tone:'green', t:'Paid', plain:true}},{}]},
     {cells:[{v:'PMT-CARR-US-00142-0005', mono:true, hi:true},{v:'SHP-RCR-10002', mono:true},
      {v:'$860', b:true},{v:'2026-08-02', mono:true},{chip:{tone:'amber', t:'Pending', plain:true}},
      {btns:[{t:'Approve', kind:'secondary'},{t:'Dispute', kind:'secondary'}]}]}]}]},
  {t:'panel', title:'Revenue by load', hint:'9 loads', parts:[
   {t:'table',
    cols:[{h:'Load', w:150},{h:'Type', w:180},{h:'Lane', w:300},{h:'Status', w:190},
          {h:'Rate', w:110},{h:'Break-even', w:110},{h:'Margin', w:106, grow:true}],
    rows:[
     {cells:[{v:'SHP-RF-10001', mono:true, hi:true},{v:'FTL - Reefer'},
      {v:'Sacramento  →  San Jose', sub:'95814  →  95112', subMono:true},{chip:{tone:'purple', t:'Tendered'}},
      {v:'$2,480', b:true},{v:'$2,050'},{v:'$430', b:true, color:C.greenInk}]},
     {cells:[{v:'SHP-LTL-10004', mono:true, hi:true},{v:'LTL - Multiple Goods'},
      {v:'San Jose  →  San Francisco', sub:'95112  →  94103', subMono:true},{chip:{tone:'purple', t:'Tendered'}},
      {v:'$3,120', b:true},{v:'$2,640'},{v:'$480', b:true, color:C.greenInk}]},
     {cells:[{v:'SHP-FTL-10001', mono:true, hi:true},{v:'FTL - Standard Goods'},
      {v:'San Jose  →  Tracy', sub:'95112  →  95376', subMono:true},{chip:{tone:'blue', t:'Carrier Accepted'}},
      {v:'$1,840', b:true},{v:'$1,520'},{v:'$320', b:true, color:C.greenInk}]},
     {cells:[{v:'SHP-RCR-10002', mono:true, hi:true},{v:'Dump Truck'},
      {v:'Fresno Quarry  →  Modesto Site'},{chip:{tone:'blue', t:'Carrier Accepted'}},
      {v:'$217,350', b:true},{v:'$181,000'},{v:'$36,350', b:true, color:C.greenInk}]},
     {cells:[{v:'SHP-FTL-10005', mono:true, hi:true},{v:'FTL - Standard Goods'},
      {v:'San Jose  →  Tracy', sub:'95112  →  95376', subMono:true},{chip:{tone:'amber', t:'In Transit'}},
      {v:'$1,960', b:true},{v:'$1,610'},{v:'$350', b:true, color:C.greenInk}]},
     {cells:[{v:'SHP-LTL-10002', mono:true, hi:true},{v:'LTL - Multiple Goods'},
      {v:'Sacramento  →  San Jose', sub:'95814  →  95112', subMono:true},{chip:{tone:'amber', t:'In Transit'}},
      {v:'$2,740', b:true},{v:'$2,280'},{v:'$460', b:true, color:C.greenInk}]},
     {cells:[{v:'SHP-RCR-10005', mono:true, hi:true},{v:'Dump Truck'},
      {v:'Fresno Quarry  →  Modesto Site'},{chip:{tone:'blue', t:'At Delivery/Dump'}},
      {v:'$132,300', b:true},{v:'$110,000'},{v:'$22,300', b:true, color:C.greenInk}]}]}]},
  {t:'legend', items:['Ledger — LED-01…LED-05','CO-29 financial setup','Auth Services BRD V3 — BILL / PAY']}
 ]},
/* ---------------------------------------------------------------- 12 SETTINGS */
{key:'settings', subIdx:0, nav:'Settings', sub:'My Profile', frame:'12 Settings — My Profile',
 title:'My Profile',
 desc:'Your personal account details, distinct from the organisation-wide settings under Company Settings.',
 actions:[{t:'Edit profile', kind:'secondary'}],
 blocks:[
  {t:'cols', ratio:[1.6,1], cols:[
   [{title:'Account', hint:'Signed in as', parts:[{t:'kv', rows:[
     {k:'Name', v:'D. Rao'},
     {k:'Email', v:'d.rao@apexfreight.example'},
     {k:'Role', v:'Carrier Super Admin', sfx:'CSA'},
     {k:'Multi-factor authentication', v:'', chip:{tone:'green', t:'Enabled'}},
     {k:'Last sign-in', v:'2026-07-24 08:02 PDT'}]}]},
    {title:'Password & security', hint:'personal', parts:[{t:'text',
     lines:['Organisation-wide sessions and lockout policy are under Settings → Sessions.'],
     btns:[{t:'Change password', kind:'secondary'},{t:'Re-enrol MFA device', kind:'secondary'}]}]}],
   [{title:'Display', hint:'Master Data §18', parts:[
     {t:'text', lines:['Timestamps are stored in UTC and rendered in this zone on every screen. §18 gives the Carrier Super Admin, Fleet Manager, Dispatcher and Compliance Manager a user-configured zone; the Driver alone follows device/GPS time.']},
     {t:'kv', rows:[
      {k:'Company default', v:'America/Los_Angeles', sfx:'PDT — from the registered address'},
      {k:'Sample timestamp', v:'2026-07-24 09:12 PDT'},
      {k:'Density', v:'Comfortable'}]}]}]]},
  {t:'legend', items:['Auth Services BRD V3 — self-managed account fields','Master Data §18 time zones']}
 ]}
];

/* ========================================== 9. RESPONSIVE + PROTOTYPE (PART 3) */
const RESPONSIVE_KEYS = ['dashboard','fleet','ops'];

function navReaction(destId){
  return { trigger:{type:'ON_CLICK'},
           actions:[{type:'NODE', destinationId:destId, navigation:'NAVIGATE',
                     transition:null, preserveScrollPosition:false, resetVideoPosition:false}] };
}
async function setReact(node, r){
  try {
    if (node.setReactionsAsync) { await node.setReactionsAsync([r]); return true; }
    node.reactions = [r]; return true;
  } catch (e){
    try {
      node.reactions = [{ trigger:{type:'ON_CLICK'},
        action:{type:'NODE', destinationId:r.actions[0].destinationId, navigation:'NAVIGATE',
                transition:null, preserveScrollPosition:false} }];
      return true;
    } catch (e2){ return false; }
  }
}

async function buildResponsive(){
  const page = await resetPage('04 Screens — Responsive');
  await figma.setCurrentPageAsync(page);
  page.backgrounds = solid(C.line);
  let x = 0;
  for (const key of RESPONSIVE_KEYS){
    const spec = SCREENS.filter(s => s.key === key)[0];
    if (!spec){ console.error('no screen spec for ' + key); continue; }
    const lbl = mkText(spec.frame.replace(/^\d+\s/, ''), {font:F.dispBold, size:22, lh:26, color:C.ink});
    page.appendChild(lbl); lbl.x = x; lbl.y = -60;
    const t = renderScreen(spec, 'tablet');
    page.appendChild(t.frame); t.frame.x = x; t.frame.y = 0;
    const m = renderScreen(spec, 'mobile');
    page.appendChild(m.frame); m.frame.x = x + TAB_W + 60; m.frame.y = 0;
    console.log('  responsive: ' + spec.frame + '  tablet ' + Math.round(t.frame.height) + 'px / mobile ' + Math.round(m.frame.height) + 'px');
    x += TAB_W + 60 + MOB_W + 160;
  }
  safe(() => { figma.viewport.scrollAndZoomIntoView(page.children); });
}

async function wirePrototype(){
  const page = findPage('03 Screens — Desktop') || findPage('03 Screens - Desktop');
  if (!page) throw new Error('Page "03 Screens — Desktop" not found. Run part2-screens.js first.');
  if (page.loadAsync) await page.loadAsync();
  const byName = {};
  page.children.forEach(f => { byName[f.name] = f; });
  const dest = {};
  SCREENS.forEach(s => { if (byName[s.frame]) dest[s.key] = byName[s.frame]; });
  const missing = SCREENS.filter(s => !byName[s.frame]).map(s => s.frame);
  if (missing.length) console.error('missing desktop frames (re-run part 2): ' + missing.join(', '));
  let wired = 0, failed = 0;
  for (const s of SCREENS){
    const frame = byName[s.frame];
    if (!frame) continue;
    const items = frame.findAll(n => typeof n.name === 'string' && n.name.indexOf('nav/') === 0);
    for (const it of items){
      const target = dest[it.name.slice(4)];
      if (!target) continue;
      const ok = await setReact(it, navReaction(target.id));
      if (ok) wired++; else failed++;
    }
  }
  const first = byName[SCREENS[0].frame];
  if (first) safe(() => { page.flowStartingPoints = [{nodeId:first.id, name:'Carrier Console — Dashboard'}]; });
  console.log('  prototype: ' + wired + ' ON_CLICK to NAVIGATE reactions set' + (failed ? ' (' + failed + ' failed)' : ''));
  return {wired, failed};
}

async function buildProtoPage(res){
  const page = await resetPage('05 Prototype');
  await figma.setCurrentPageAsync(page);
  page.backgrounds = solid(C.canvas);
  const board = mkFrame('Prototype map', {dir:'V', gap:28, pad:56, fill:C.canvas, w:1200});
  page.appendChild(board); board.x = 0; board.y = 0;
  add(board, mkText('Prototype - navigation map', {font:F.dispBold, size:34, lh:38, ls:0.3}), {hFill:true});
  add(board, mkText('Wiring lives on page "03 Screens — Desktop". Every one of the 12 sidebar items on every one of the 12 frames is an ON_CLICK to NAVIGATE to the matching frame, transition Instant, so the rail behaves like the real console from any starting screen. Flow starting point: 01 Dashboard - Overview.',
    {size:14, lh:21, color:C.ink2}), {hFill:true});
  const stat = mkFrame('stats', {dir:'H', gap:16, wrap:true, crossGap:16});
  add(board, stat, {hFill:true});
  [['Frames wired','12','desktop screens','default'],
   ['Reactions','' + (res ? res.wired : 0), 'ON_CLICK to NAVIGATE','blue'],
   ['Per frame','12','one per sidebar item','grey'],
   ['Transition','Instant','no animation','grey']].forEach(k => {
    const c = inst('KPI Card', {tone:k[3]});
    add(stat, c, {hFix:270});
    setText(c, 'label', k[0]); setText(c, 'value', k[1]); setText(c, 'sub', k[2]);
    const sm = c.findOne(n => n.type === 'TEXT' && n.name === 'value-small'); if (sm) sm.visible = false;
  });
  const card = mkFrame('map', {dir:'V', gap:0, fill:C.panel, stroke:C.line, radius:10, clip:true});
  add(board, card, {hFill:true});
  const hd = inst('Panel', {header:'title+hint'});
  add(card, hd, {hFill:true});
  setText(hd, 'title', 'Sidebar item to destination frame');
  setText(hd, 'hint', '12 x 12 = 144 links');
  const box = mkFrame('rows', {dir:'V', gap:0});
  add(card, box, {hFill:true});
  SCREENS.forEach((s, i) => {
    const r = mkFrame('r', {dir:'H', gap:14, align:'CENTER', pad:[10,16,10,16],
      stroke: i < SCREENS.length - 1 ? C.line2 : null, sides:[0,0,1,0]});
    add(box, r, {hFill:true});
    add(r, mkText('nav/' + s.key, {font:F.mono, size:11.5, lh:16, color:C.brand}), {hFix:170});
    add(r, svgIcon(I.arrow, 14, C.ink3, 1.6));
    add(r, mkText(s.frame, {font:F.medium, size:12.5, lh:17}), {hFill:true});
    add(r, mkText(s.nav + ' / ' + s.sub, {size:11.5, lh:16, color:C.ink3}));
  });
  const n = inst('Note', {tone:'blue'});
  add(board, n, {hFill:true});
  setText(n, 'body', 'Agreed scope: only the sidebar is wired. In-screen controls (filter chips, table rows, pagers, drawer triggers) are documented as states on page 02 but are deliberately not prototyped.');
}

/* ============================================================== 10. RUN PART 3 */
(async () => {
  try {
    console.log('mySHIPR Carrier Console - build part 3 of 3 (responsive + prototype)');
    await loadFonts();
    await adoptComponents();
    await buildResponsive();
    const res = await wirePrototype();
    await buildProtoPage(res);
    console.log('PART 3 DONE - responsive frames + ' + res.wired + ' prototype links.');
    if (typeof figma.notify === 'function') figma.notify('mySHIPR part 3 done - responsive + prototype');
  } catch (e) {
    console.error('PART 3 FAILED:', (e && e.message) ? e.message : e);
    throw e;
  }
})();
