(async () => {
var RESULT = null, report = 'start';
try {
/* mySHIPR Carrier Console — use_figma chunk: 05-screens-01-04.js
 * desktop screens 1-4
 * fileKey ktu4OlSs8rCXEqsgHzVFVg
 * Paste as the `code` argument of use_figma (skillNames: "resource:figma-use").
 * The runner auto-wraps this in an async IIFE, so top-level await + return work.
 * Run the chunks in filename order. Each one is safe to re-run.
 */
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
const TONE = {
  green :{bg:C.greenBg , fg:C.greenInk , solid:C.green , bd:'#bfdfcd'},
  amber :{bg:C.amberBg , fg:C.amberInk , solid:C.amber , bd:'#f0d9ab'},
  red   :{bg:C.redBg   , fg:C.redInk   , solid:C.red   , bd:'#eec4c4'},
  blue  :{bg:C.blueBg  , fg:C.blueInk  , solid:C.blue  , bd:'#c6dcf4'},
  grey  :{bg:C.greyBg  , fg:C.greyInk  , solid:C.grey  , bd:C.line},
  purple:{bg:C.purpleBg, fg:C.purpleInk, solid:C.purple, bd:C.purpleBg}
};
const KPI_EDGE = { default:C.brand, amber:C.sign, red:C.red, blue:C.blue, grey:C.grey };
const BANNER = { info:'blue', warn:'amber', crit:'red', ok:'green' };
const SIDE_W = 248, DESK_W = 1440, TAB_W = 900, MOB_W = 375;
const F = {};                    /* resolved fonts               */
const COMP = {};                 /* component registry by name   */
const P = {};                    /* pages by name                */
const VARS = { Color:{}, Radius:{}, Spacing:{} };
let LIB = null;                   /* component-library board on page 02 */
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
  LOGC.log('fonts →', Object.keys(F).map(k=>k+':'+F[k].family+'/'+F[k].style).join('  '));
}
function rgb(hex){
  const h = hex.replace('#','');
  return { r:parseInt(h.slice(0,2),16)/255, g:parseInt(h.slice(2,4),16)/255, b:parseInt(h.slice(4,6),16)/255 };
}
function solid(hex, opacity){ return [{type:'SOLID', color:rgb(hex), opacity: opacity==null?1:opacity}]; }
function safe(fn){ try { return fn(); } catch(e){ return null; } }
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
  if (ONLY && ONLY.indexOf(name) < 0) return COMP[name] || null;
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
  if (ONLY && ONLY.indexOf(name) < 0) return COMP[name] || null;
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
   subs:['My Profile','Notification Preferences','Roles & Users','Audit Logs','Sessions','Company Profile','Documents','Contract','Finance','Capacity'],
   groups:[['Personal Settings',2],['Company Settings',8]]}
];
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
      si.name = 'sub/' + g.key + '/' + idx;
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
const CHK = {box:true};

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

const SCREENS = [{"key": "dashboard", "subIdx": 0, "nav": "Dashboard", "sub": "Overview", "frame": "01 Dashboard — Overview", "title": "Fleet Operations Overview", "desc": "Live snapshot of Apex Freight across the US / CA / MX network — assets, drivers, tenders, loads and compliance, all on one page.", "blocks": [{"t": "banner", "tone": "crit", "title": "1 required compliance document outstanding", "body": "CO-07 lists eight mandatory carrier documents. Profile completion is blocked at 88% until all are uploaded.", "btns": [{"t": "Go to documents", "kind": "danger"}]}, {"t": "pulse", "cells": [{"n": "3", "label": "Trucks available", "tone": "green"}, {"n": "2", "label": "Out of service / halt", "tone": "red"}, {"n": "2", "label": "Drivers available", "tone": "green"}, {"n": "4", "label": "Drivers on duty", "tone": "amber"}, {"n": "2", "label": "Non-dispatchable", "tone": "red"}]}, {"t": "kpi", "cards": [{"label": "Fleet size", "value": "8", "sub": "3 available · 5 not dispatchable", "tone": "default"}, {"label": "In transit", "value": "1", "sub": "Master Data asset status", "tone": "amber"}, {"label": "Tenders open", "value": "2", "sub": "awaiting accept / decline", "tone": "red"}, {"label": "Awaiting assignment", "value": "2", "sub": "accepted, no asset selected", "tone": "amber"}, {"label": "Trips on going", "value": "3", "sub": "1 scheduled", "tone": "blue"}, {"label": "POD outstanding", "value": "1", "sub": "awaiting close-out", "tone": "grey"}]}, {"t": "cols", "ratio": [1.6, 1], "cols": [{"title": "Fleet by asset status", "hint": "interactive · Master Data — 7 values", "parts": [{"t": "bars", "rows": [{"label": "Available", "value": "3", "pct": 100, "tone": "green"}, {"label": "Unavailable", "value": "1", "pct": 33, "tone": "blue"}, {"label": "In Transit", "value": "1", "pct": 33, "tone": "amber"}, {"label": "Halt", "value": "1", "pct": 33, "tone": "red"}, {"label": "At Pickup", "value": "0", "pct": 0, "tone": "grey"}, {"label": "At Delivery/Dump", "value": "1", "pct": 33, "tone": "blue"}, {"label": "Out of Service", "value": "1", "pct": 33, "tone": "red"}]}]}, {"title": "Drivers by dispatch eligibility", "hint": "interactive · FMCSA gate OPS-05 / DRV-002", "parts": [{"t": "donut", "segments": [{"label": "Dispatchable", "pct": 62.5, "color": "#157a4a"}, {"label": "Verification pending", "pct": 12.5, "color": "#c9770a"}, {"label": "Suspended — compliance", "pct": 12.5, "color": "#c23b3b"}, {"label": "Uninsured (CO-18)", "pct": 12.5, "color": "#6b7480"}]}]}]}, {"t": "cols", "ratio": [1, 1], "cols": [{"title": "Hours of Service — nearing limit", "hint": "ELD feed · fleet-wide", "parts": [{"t": "list", "items": [{"sev": "crit", "unread": false, "title": "Sofia Torres", "body": "OFF_DUTY · 0.0 h remaining · San Jose Hub", "code": "TEL-003 · 30 min warning", "time": "0.0 h"}, {"sev": "ok", "unread": false, "title": "Priya Nair", "body": "DRIVING · 4.0 h remaining · CA-99 near Elk Grove, CA", "code": "TRIP-58022", "time": "OK"}, {"sev": "ok", "unread": false, "title": "Marcus Reyes", "body": "DRIVING · 6.5 h remaining · I-580 near Livermore, CA", "code": "TRIP-58021", "time": "OK"}, {"sev": "warn", "unread": false, "title": "Tyler Brooks", "body": "ON_DUTY_NOT_DRIVING · 7.1 h remaining · Tracy Staging", "code": "TRIP-58024", "time": "OK"}]}]}, {"title": "Outstanding payments", "hint": "4 need action", "parts": [{"t": "list", "items": [{"sev": "warn", "unread": false, "title": "PMT-CARR-US-00142-0001 · $2,380", "body": "Load SHP-FTL-10003 · due 2026-07-30", "code": "Pending", "time": "Pending", "btn": "Approve"}, {"sev": "info", "unread": false, "title": "PMT-CARR-US-00142-0002 · $1,180", "body": "Load SHP-RCR-10005 · due 2026-07-29", "code": "Approved", "time": "Approved", "btn": "Pay now"}, {"sev": "crit", "unread": false, "title": "PMT-CARR-US-00142-0003 · $640", "body": "Load SHP-LTL-10002 · due 2026-07-25 · rate mismatch vs rate confirmation", "code": "Disputed", "time": "Disputed"}, {"sev": "grey", "unread": false, "title": "PMT-CARR-US-00142-0004 · $1,920", "body": "Load SHP-FTL-10005 · due 2026-07-20", "code": "Paid", "time": "Paid"}]}]}]}, {"t": "legend", "items": ["Master Data — asset & driver status", "Auth Services BRD V3", "Shipment Execution OPS-01…OPS-12", "Carrier Onboarding CO-01…CO-30"]}]}, {"key": "fleet", "subIdx": 0, "nav": "Fleet", "sub": "All Vehicles", "frame": "02 Fleet — All Vehicles", "title": "All Vehicles", "desc": "Every field captured at CO-10 and validated at CO-11 — licence plate, plate state, registration expiry, make and model. Rows open the full asset record.", "actions": [{"t": "Register truck", "kind": "primary"}, {"t": "Bulk upload", "kind": "secondary"}], "blocks": [{"t": "panel", "title": "Fleet", "hint": "8 vehicles", "parts": [{"t": "filters", "label": "Asset status", "chips": [{"t": "All", "n": 8, "on": true}, {"t": "Available", "n": 3}, {"t": "Unavailable", "n": 1}, {"t": "In Transit", "n": 1}, {"t": "Halt", "n": 1}, {"t": "At Pickup", "n": 0}, {"t": "At Delivery/Dump", "n": 1}, {"t": "Out of Service", "n": 1}]}, {"t": "table", "cols": [{"h": "", "w": 48}, {"h": "Truck", "w": 148}, {"h": "Type", "w": 121}, {"h": "Make / Model", "w": 130}, {"h": "Plate", "w": 84}, {"h": "Registration expiry", "w": 174}, {"h": "Asset status", "w": 169}, {"h": "CO-11", "w": 150}, {"h": "Home yard", "w": 122, "grow": true}], "rows": [{"state": "blocked", "cells": [{"box": true}, {"v": "001", "mono": true, "hi": true, "b": true, "sub": "1FUJGLDR5CLBP8834", "subMono": true}, {"v": "Semi Truck (Sleeper Cab)", "b": true}, {"v": "Freightliner Cascadia 126"}, {"v": "8ZTK492", "mono": true, "sub": "CA", "subMono": true}, {"v": "2027-02-28", "mono": true}, {"chip": {"tone": "amber", "t": "In Transit"}, "sub2": "dispatch blocked"}, {"chip": {"tone": "green", "t": "Serviceable", "plain": true}}, {"v": "San Jose Hub"}]}, {"cells": [{"box": true}, {"v": "002", "mono": true, "hi": true, "b": true, "sub": "3AKJHHDR8LSLR2210", "subMono": true}, {"v": "Semi Truck (Day Cab)", "b": true}, {"v": "Kenworth T680"}, {"v": "9LMD778", "mono": true, "sub": "CA", "subMono": true}, {"v": "2026-08-14", "mono": true, "sub": "21 days", "subColor": "#c9770a"}, {"chip": {"tone": "green", "t": "Available"}}, {"chip": {"tone": "green", "t": "Serviceable", "plain": true}}, {"v": "San Jose Hub"}]}, {"cells": [{"box": true}, {"v": "003", "mono": true, "hi": true, "b": true, "sub": "1XKYDP9X4MJ415522", "subMono": true}, {"v": "Semi Truck (Sleeper Cab)", "b": true}, {"v": "Peterbilt 579"}, {"v": "7RQP210", "mono": true, "sub": "NV", "subMono": true}, {"v": "2027-05-30", "mono": true}, {"chip": {"tone": "green", "t": "Available"}}, {"chip": {"tone": "green", "t": "Serviceable", "plain": true}}, {"v": "Sacramento Depot"}]}, {"state": "blocked", "cells": [{"box": true}, {"v": "004", "mono": true, "hi": true, "b": true, "sub": "1M2AX07C1KM021847", "subMono": true}, {"v": "Dump Truck (Standard)", "b": true, "sub": "Standard Dump Truck"}, {"v": "Mack Granite 64FR"}, {"v": "6BHT031", "mono": true, "sub": "CA", "subMono": true}, {"v": "2026-07-31", "mono": true, "sub": "7 days", "subColor": "#c23b3b"}, {"chip": {"tone": "red", "t": "Out of Service"}, "sub2": "dispatch blocked"}, {"chip": {"tone": "red", "t": "Not serviceable", "plain": true}}, {"v": "Tracy Staging"}]}, {"state": "blocked", "cells": [{"box": true}, {"v": "005", "mono": true, "hi": true, "b": true, "sub": "1M2AX13C4LM030019", "subMono": true}, {"v": "Dump Truck (Articulated)", "b": true, "sub": "Articulated Dump Truck (ADT)"}, {"v": "Volvo A40G"}, {"v": "5KWD884", "mono": true, "sub": "CA", "subMono": true}, {"v": "2027-01-15", "mono": true}, {"chip": {"tone": "blue", "t": "At Delivery/Dump"}, "sub2": "dispatch blocked"}, {"chip": {"tone": "green", "t": "Serviceable", "plain": true}}, {"v": "Tracy Staging"}]}, {"cells": [{"box": true}, {"v": "006", "mono": true, "hi": true, "b": true, "sub": "2FZHAZCV1XAH12290", "subMono": true}, {"v": "Bobtail (No Trailer)", "b": true}, {"v": "International LT625"}, {"v": "4NPC556", "mono": true, "sub": "CA", "subMono": true}, {"v": "2027-03-20", "mono": true}, {"chip": {"tone": "green", "t": "Available"}}, {"chip": {"tone": "green", "t": "Serviceable", "plain": true}}, {"v": "San Jose Hub"}]}]}, {"t": "pager", "range": "Showing 1–6 of 8"}]}, {"t": "note", "tone": "amber", "body": "Rows shaded red are not dispatchable — asset status is Out of Service or Halt, so allows_dispatch is false. The load assignment wizard filters these out automatically (OPS-03)."}, {"t": "legend", "items": ["CO-10 Truck Registration", "CO-11 DMV validation", "Master Data §1.2 truck types", "Master Data asset status", "Auth Services BRD V3 — FLEET"]}]}, {"key": "fleet", "subIdx": 1, "nav": "Fleet", "sub": "Active Vehicles", "frame": "02.2 Fleet — Active Vehicles", "title": "Active Vehicles", "desc": "Trucks currently moving or on site, by Master Data asset status.", "blocks": [{"t": "panel", "title": "Fleet", "parts": [{"t": "table", "cols": [{"h": "", "w": 48}, {"h": "Truck", "w": 135}, {"h": "Type", "w": 222}, {"h": "Make / model", "w": 198}, {"h": "Plate", "w": 79}, {"h": "Registration expiry", "w": 150}, {"h": "Asset status", "w": 127}, {"h": "CO-11", "w": 87}, {"h": "Home yard", "w": 103, "grow": true}], "rows": [{"cells": [{"box": true}, {"v": "001", "mono": true, "b": true, "hi": true, "sub": "1FUJGLDR5CLBP8834", "subMono": true}, {"v": "Semi Truck (Sleeper Cab)"}, {"v": "Freightliner Cascadia 126"}, {"v": "8ZTK492 CA", "mono": true}, {"v": "2027-02-28", "mono": true}, {"chip": {"tone": "amber", "t": "In Transit"}, "sub2": "dispatch blocked"}, {"chip": {"tone": "green", "t": "Serviceable", "plain": true}}, {"v": "San Jose Hub"}], "state": "blocked"}, {"cells": [{"box": true}, {"v": "005", "mono": true, "b": true, "hi": true, "sub": "1M2AX13C4LM030019", "subMono": true}, {"v": "Dump Truck (Articulated)", "sub": "Articulated Dump Truck (ADT)"}, {"v": "Volvo A40G"}, {"v": "5KWD884 CA", "mono": true}, {"v": "2027-01-15", "mono": true}, {"chip": {"tone": "blue", "t": "At Delivery/Dump"}, "sub2": "dispatch blocked"}, {"chip": {"tone": "green", "t": "Serviceable", "plain": true}}, {"v": "Tracy Staging"}], "state": "blocked"}]}], "hint": "8 vehicles"}, {"t": "note", "tone": "blue", "body": "Rows shaded red are not dispatchable — asset status is Out of Service or Halt, so allows_dispatch is false. The load assignment wizard filters these out automatically (OPS-03)."}, {"t": "legend", "items": ["CO-10 Truck Registration", "CO-11 DMV validation", "Master Data §1.2 truck types", "Master Data asset status", "Auth Services BRD V3 — FLEET"]}], "actions": [{"t": "Register truck", "kind": "secondary"}, {"t": "Bulk upload", "kind": "secondary"}]}, {"key": "fleet", "subIdx": 2, "nav": "Fleet", "sub": "Idle Vehicles", "frame": "02.3 Fleet — Idle Vehicles", "title": "Idle Vehicles", "desc": "Trucks with asset status Available and therefore dispatchable.", "blocks": [{"t": "panel", "title": "Fleet", "parts": [{"t": "table", "cols": [{"h": "", "w": 48}, {"h": "Truck", "w": 146}, {"h": "Type", "w": 206}, {"h": "Make / model", "w": 163}, {"h": "Plate", "w": 86}, {"h": "Registration expiry", "w": 163}, {"h": "Asset status", "w": 103}, {"h": "CO-11", "w": 95}, {"h": "Home yard", "w": 138, "grow": true}], "rows": [{"cells": [{"box": true}, {"v": "002", "mono": true, "b": true, "hi": true, "sub": "3AKJHHDR8LSLR2210", "subMono": true}, {"v": "Semi Truck (Day Cab)"}, {"v": "Kenworth T680"}, {"v": "9LMD778 CA", "mono": true}, {"v": "2026-08-14", "mono": true, "sub": "21 days", "subMono": true}, {"chip": {"tone": "green", "t": "Available"}}, {"chip": {"tone": "green", "t": "Serviceable", "plain": true}}, {"v": "San Jose Hub"}]}, {"cells": [{"box": true}, {"v": "003", "mono": true, "b": true, "hi": true, "sub": "1XKYDP9X4MJ415522", "subMono": true}, {"v": "Semi Truck (Sleeper Cab)"}, {"v": "Peterbilt 579"}, {"v": "7RQP210 NV", "mono": true}, {"v": "2027-05-30", "mono": true}, {"chip": {"tone": "green", "t": "Available"}}, {"chip": {"tone": "green", "t": "Serviceable", "plain": true}}, {"v": "Sacramento Depot"}]}, {"cells": [{"box": true}, {"v": "006", "mono": true, "b": true, "hi": true, "sub": "2FZHAZCV1XAH12290", "subMono": true}, {"v": "Bobtail (No Trailer)"}, {"v": "International LT625"}, {"v": "4NPC556 CA", "mono": true}, {"v": "2027-03-20", "mono": true}, {"chip": {"tone": "green", "t": "Available"}}, {"chip": {"tone": "green", "t": "Serviceable", "plain": true}}, {"v": "San Jose Hub"}]}]}], "hint": "8 vehicles"}, {"t": "note", "tone": "blue", "body": "Rows shaded red are not dispatchable — asset status is Out of Service or Halt, so allows_dispatch is false. The load assignment wizard filters these out automatically (OPS-03)."}, {"t": "legend", "items": ["CO-10 Truck Registration", "CO-11 DMV validation", "Master Data §1.2 truck types", "Master Data asset status", "Auth Services BRD V3 — FLEET"]}], "actions": [{"t": "Register truck", "kind": "secondary"}, {"t": "Bulk upload", "kind": "secondary"}]}, {"key": "fleet", "subIdx": 3, "nav": "Fleet", "sub": "Maintenance & DVIR", "frame": "02.4 Fleet — Maintenance & DVIR", "title": "Maintenance & DVIR", "desc": "Maintenance events and driver vehicle inspection reports. Logging an event sets the asset status and therefore gates dispatch.", "blocks": [{"t": "panel", "title": "Assets requiring attention", "parts": [{"t": "table", "cols": [{"h": "Truck", "w": 81}, {"h": "Type", "w": 257}, {"h": "Asset status", "w": 177}, {"h": "Defect / reason", "w": 166}, {"h": "Last dvir", "w": 111}, {"h": "Detail", "w": 257}, {"h": "Action", "w": 100, "grow": true}], "rows": [{"cells": [{"v": "001", "mono": true, "b": true, "hi": true}, {"v": "Semi Truck (Sleeper Cab)"}, {"chip": {"tone": "amber", "t": "In Transit"}}, {"chip": {"tone": "grey", "t": "No defect", "plain": true}}, {"v": "2026-07-23", "mono": true}, {"v": "—"}, {"v": "Log event"}]}, {"cells": [{"v": "004", "mono": true, "b": true, "hi": true}, {"v": "Dump Truck (Standard)"}, {"chip": {"tone": "red", "t": "Out of Service"}}, {"chip": {"tone": "grey", "t": "Defect reported", "plain": true}}, {"v": "2026-07-19", "mono": true}, {"v": "Hydraulic leak, rear tipper ram"}, {"v": "Log event"}]}, {"cells": [{"v": "005", "mono": true, "b": true, "hi": true}, {"v": "Dump Truck (Articulated)"}, {"chip": {"tone": "blue", "t": "At Delivery/Dump"}}, {"chip": {"tone": "grey", "t": "No defect", "plain": true}}, {"v": "2026-07-24", "mono": true}, {"v": "—"}, {"v": "Log event"}]}, {"cells": [{"v": "007", "mono": true, "b": true, "hi": true}, {"v": "Yard Truck (Terminal Tractor)"}, {"chip": {"tone": "grey", "t": "Unavailable"}}, {"chip": {"tone": "grey", "t": "No defect", "plain": true}}, {"v": "2026-07-21", "mono": true}, {"v": "—"}, {"v": "Log event"}]}, {"cells": [{"v": "008", "mono": true, "b": true, "hi": true}, {"v": "Straight Truck (Medium Duty)"}, {"chip": {"tone": "red", "t": "Halt"}}, {"chip": {"tone": "grey", "t": "No defect", "plain": true}}, {"v": "2026-07-20", "mono": true}, {"v": "—"}, {"v": "Log event"}]}]}, {"t": "text", "lines": [], "btns": [{"t": "Log event", "kind": "secondary"}, {"t": "Log event", "kind": "secondary"}, {"t": "Log event", "kind": "secondary"}]}], "hint": "5 vehicles"}, {"t": "panel", "title": "Maintenance types", "parts": [{"t": "text", "lines": ["OIL_CHANGE · DOT_ANNUAL_INSPECTION", "TIRE_ROTATION · BRAKE_SERVICE", "PM_SERVICE · REPAIR", "REEFER_PM · TABLET_BREAKDOWN"]}, {"t": "text", "lines": ["This catalogue currently has no business-document source — it originates from the database dictionary. It is retained pending promotion into Master Data."]}], "hint": "FLEET-003 catalogue"}, {"t": "panel", "title": "Inspection reminders", "parts": [{"t": "list", "items": [{"sev": "info", "unread": false, "title": "Pre-trip inspection outstanding — TRK-CARR-US-00142-006", "body": "Driver must complete DVIR before dispatch (FTL-07)", "code": "", "time": ""}, {"sev": "info", "unread": false, "title": "DVIR defect — TRK-CARR-US-00142-004", "body": "Hydraulic leak reported 2026-07-19 · asset moved Out of Service", "code": "", "time": ""}, {"sev": "info", "unread": false, "title": "DOT annual inspection due — TRK-CARR-US-00142-002", "body": "Scheduled 2026-08-30 (CR-022)", "code": "", "time": ""}]}], "hint": "DR-025 / DR-026 · TEL-011 / TEL-012"}, {"t": "legend", "items": ["Carrier View FLEET-003", "Notification Types CR-010, CR-022, TEL-011, TEL-012", "Driver BRD DR-025 / DR-026", "Fields For HOS inspection events", "Tablet Breakdown / Device Under Repair — engineering brief"]}], "actions": [{"t": "Log maintenance", "kind": "secondary"}]}, {"key": "fleet", "subIdx": 4, "nav": "Fleet", "sub": "Vehicle documents", "frame": "02.5 Fleet — Vehicle documents", "title": "Vehicle documents", "desc": "Vehicle-level documents and expiries, on the same CO-09 five-tier ladder as carrier documents — including truck registration expiry.", "blocks": [{"t": "panel", "title": "Documents by vehicle", "parts": [{"t": "table", "cols": [{"h": "Truck", "w": 168}, {"h": "Registration expiry", "w": 188}, {"h": "REGISTRATION (CO-11)", "w": 198}, {"h": "INSURANCE (CO-11)", "w": 168}, {"h": "Dot annual inspection", "w": 207}, {"h": "Cargo insurance", "w": 148}, {"h": "Action", "w": 71, "grow": true}], "rows": [{"cells": [{"v": "001", "mono": true, "b": true, "hi": true, "sub": "1FUJGLDR5CLBP8834", "subMono": true}, {"chip": {"tone": "green", "t": "OK", "plain": true}, "sub2": "2027-02-28"}, {"chip": {"tone": "green", "t": "Valid", "plain": true}}, {"chip": {"tone": "green", "t": "Valid", "plain": true}}, {"v": "2027-03-14", "mono": true}, {"v": "2026-12-31", "mono": true}, {"v": "Upload"}]}, {"cells": [{"v": "002", "mono": true, "b": true, "hi": true, "sub": "3AKJHHDR8LSLR2210", "subMono": true}, {"v": "2026-08-14", "mono": true, "sub": "tier \"1 month\"", "subMono": true}, {"chip": {"tone": "amber", "t": "Expiring", "plain": true}}, {"chip": {"tone": "green", "t": "Valid", "plain": true}}, {"v": "2026-08-30", "mono": true}, {"v": "2026-12-31", "mono": true}, {"v": "Upload"}]}, {"cells": [{"v": "003", "mono": true, "b": true, "hi": true, "sub": "1XKYDP9X4MJ415522", "subMono": true}, {"chip": {"tone": "green", "t": "OK", "plain": true}, "sub2": "2027-05-30"}, {"chip": {"tone": "green", "t": "Valid", "plain": true}}, {"chip": {"tone": "green", "t": "Valid", "plain": true}}, {"v": "2027-01-22", "mono": true}, {"v": "2027-02-14", "mono": true}, {"v": "Upload"}]}, {"cells": [{"v": "004", "mono": true, "b": true, "hi": true, "sub": "1M2AX07C1KM021847", "subMono": true}, {"v": "2026-07-31", "mono": true, "sub": "tier \"1 month\"", "subMono": true}, {"chip": {"tone": "amber", "t": "Expiring", "plain": true}}, {"chip": {"tone": "green", "t": "Valid", "plain": true}}, {"v": "2026-07-19", "mono": true, "sub": "5 days overdue", "subMono": true}, {"v": "2026-12-31", "mono": true}, {"v": "Upload"}], "state": "blocked"}, {"cells": [{"v": "005", "mono": true, "b": true, "hi": true, "sub": "1M2AX13C4LM030019", "subMono": true}, {"chip": {"tone": "green", "t": "OK", "plain": true}, "sub2": "2027-01-15"}, {"chip": {"tone": "green", "t": "Valid", "plain": true}}, {"chip": {"tone": "green", "t": "Valid", "plain": true}}, {"v": "2026-11-05", "mono": true}, {"v": "2027-02-14", "mono": true}, {"v": "Upload"}]}, {"cells": [{"v": "006", "mono": true, "b": true, "hi": true, "sub": "2FZHAZCV1XAH12290", "subMono": true}, {"chip": {"tone": "green", "t": "OK", "plain": true}, "sub2": "2027-03-20"}, {"chip": {"tone": "green", "t": "Valid", "plain": true}}, {"chip": {"tone": "green", "t": "Valid", "plain": true}}, {"v": "2027-04-18", "mono": true}, {"v": "2026-12-31", "mono": true}, {"v": "Upload"}]}, {"cells": [{"v": "007", "mono": true, "b": true, "hi": true, "sub": "1NKDX4EX3NJ447715", "subMono": true}, {"chip": {"tone": "green", "t": "OK", "plain": true}, "sub2": "2026-11-02"}, {"chip": {"tone": "green", "t": "Valid", "plain": true}}, {"chip": {"tone": "green", "t": "Valid", "plain": true}}, {"v": "2026-09-27", "mono": true}, {"chip": {"tone": "grey", "t": "Not on file", "plain": true}}, {"v": "Upload"}], "state": "blocked"}]}, {"t": "pager", "range": "Showing 1–7 of 8"}, {"t": "text", "lines": [], "btns": [{"t": "Upload", "kind": "secondary"}, {"t": "Upload", "kind": "secondary"}, {"t": "Upload", "kind": "secondary"}]}], "hint": "8 vehicles"}, {"t": "legend", "items": ["CO-10 registration expiry", "CO-11 DMV validation", "CO-09 expiry ladder", "Carrier View FLEET-004"]}]}, {"key": "fleet", "subIdx": 5, "nav": "Fleet", "sub": "Vehicle Types", "frame": "02.6 Fleet — Vehicle Types", "title": "Vehicle Types", "desc": "The full Master Data §1.2 truck catalogue — ten types. Dump trucks, bobtails, yard trucks, tankers and car haulers are all registrable.", "blocks": [{"t": "banner", "tone": "info", "title": "Dump truck, bobtail and yard truck are now registrable", "body": "Bobtail is a truck type in Master Data, so the count is read from the catalogue rather than derived from a truck having no driver."}, {"t": "panel", "title": "Trailers", "parts": [{"t": "table", "cols": [{"h": "Trailer", "w": 78}, {"h": "Type", "w": 122}, {"h": "Vin", "w": 188}, {"h": "Make / year", "w": 188}, {"h": "Length", "w": 72}, {"h": "Max payload", "w": 122}, {"h": "Status", "w": 155}, {"h": "Attached to", "w": 133}, {"h": "Photo", "w": 89, "grow": true}], "rows": [{"cells": [{"v": "011", "mono": true, "b": true, "hi": true}, {"v": "Dry Van"}, {"v": "1JJV532W1PL778120", "mono": true}, {"v": "Wabash · 2021"}, {"v": "53′"}, {"v": "45,000 lbs"}, {"chip": {"tone": "amber", "t": "In Transit"}}, {"v": "001 PRIMARY", "mono": true}, {"v": "Photo"}]}, {"cells": [{"v": "012", "mono": true, "b": true, "hi": true}, {"v": "Dry Van"}, {"v": "1JJV532W7NL661044", "mono": true}, {"v": "Great Dane · 2019"}, {"v": "48′"}, {"v": "42,000 lbs"}, {"chip": {"tone": "green", "t": "Available"}}, {"v": "—", "sub": "Not attached"}, {"v": "Photo"}]}, {"cells": [{"v": "013", "mono": true, "b": true, "hi": true}, {"v": "Flatbed"}, {"v": "1UYFS2483M2119887", "mono": true}, {"v": "Utility · 2020"}, {"v": "48′"}, {"v": "48,000 lbs"}, {"chip": {"tone": "green", "t": "Available"}}, {"v": "—", "sub": "Not attached"}, {"v": "No photo"}]}, {"cells": [{"v": "014", "mono": true, "b": true, "hi": true}, {"v": "Step Deck"}, {"v": "1DW1A5321LB410992", "mono": true}, {"v": "Fontaine · 2018"}, {"v": "48′"}, {"v": "46,000 lbs"}, {"chip": {"tone": "green", "t": "Available"}}, {"v": "—", "sub": "Not attached"}, {"v": "No photo"}]}, {"cells": [{"v": "015", "mono": true, "b": true, "hi": true}, {"v": "Reefer"}, {"v": "1UYVS2534N2445120", "mono": true}, {"v": "Utility · 2022"}, {"v": "53′"}, {"v": "44,000 lbs"}, {"chip": {"tone": "red", "t": "Out of Service"}}, {"v": "—", "sub": "Not attached"}, {"v": "Photo"}]}, {"cells": [{"v": "016", "mono": true, "b": true, "hi": true}, {"v": "Reefer"}, {"v": "1UYVS2534P2551338", "mono": true}, {"v": "Great Dane · 2023"}, {"v": "53′"}, {"v": "44,500 lbs"}, {"chip": {"tone": "green", "t": "Available"}}, {"v": "—", "sub": "Not attached"}, {"v": "Photo"}]}, {"cells": [{"v": "017", "mono": true, "b": true, "hi": true}, {"v": "Double Drop"}, {"v": "1RNF48A29KR220117", "mono": true}, {"v": "Talbert · 2017"}, {"v": "45′"}, {"v": "52,000 lbs"}, {"chip": {"tone": "grey", "t": "Unavailable"}}, {"v": "—", "sub": "Not attached"}, {"v": "No photo"}]}]}], "hint": "7 units"}, {"t": "note", "tone": "blue", "body": "Maximum payload is a legal-weight field captured at CO-12 and drives the capacity filter in the assignment wizard (OPS-04)."}, {"t": "legend", "items": ["Master Data §1.1 trailer types", "Master Data §1.2 truck types", "CO-12 Trailer onboarding", "CO-13 Assign trailer to truck"]}]}, {"key": "fleet", "subIdx": 6, "nav": "Fleet", "sub": "Devices & ELD", "frame": "02.7 Fleet — Devices & ELD", "title": "Devices & ELD", "desc": "Tablet-to-truck pairing and ELD sync health. The tablet belongs to the truck, so this pairing is the foundation of the driver-identification model.", "blocks": [{"t": "banner", "tone": "crit", "title": "TAB-4478 disconnected — HOS logging inactive on TRK-CARR-US-00142-008", "body": "Last sync 2026-07-23 06:02. HOS logs may be incomplete (TEL-002). CO-23 requires the Fleet Manager to be alerted on persistent failure — that alert now has a destination.", "btns": [{"t": "Re-pair", "kind": "danger"}]}, {"t": "panel", "title": "Devices", "parts": [{"t": "table", "cols": [{"h": "Device", "w": 116}, {"h": "Paired truck", "w": 247}, {"h": "Provider", "w": 116}, {"h": "Status", "w": 174}, {"h": "Last sync", "w": 247}, {"h": "Action", "w": 247, "grow": true}], "rows": [{"cells": [{"v": "TAB-4471", "mono": true, "b": true, "hi": true}, {"v": "001", "mono": true, "sub": "1FUJGLDR5CLBP8834", "subMono": true}, {"v": "SAMSARA"}, {"chip": {"tone": "green", "t": "Active", "plain": true}}, {"v": "2026-07-24 09:12PDT", "mono": true}, {"v": "UnassignReport faulty"}]}, {"cells": [{"v": "TAB-4472", "mono": true, "b": true, "hi": true}, {"v": "002", "mono": true, "sub": "3AKJHHDR8LSLR2210", "subMono": true}, {"v": "SAMSARA"}, {"chip": {"tone": "green", "t": "Active", "plain": true}}, {"v": "2026-07-24 09:14PDT", "mono": true}, {"v": "UnassignReport faulty"}]}, {"cells": [{"v": "TAB-4473", "mono": true, "b": true, "hi": true}, {"v": "003", "mono": true, "sub": "1XKYDP9X4MJ415522", "subMono": true}, {"v": "GEOTAB"}, {"chip": {"tone": "green", "t": "Active", "plain": true}}, {"v": "2026-07-24 09:10PDT", "mono": true}, {"v": "UnassignReport faulty"}]}, {"cells": [{"v": "TAB-4474", "mono": true, "b": true, "hi": true}, {"v": "004", "mono": true, "sub": "1M2AX07C1KM021847", "subMono": true}, {"v": "GEOTAB"}, {"chip": {"tone": "red", "t": "Sync failing", "plain": true}}, {"v": "2026-07-22 17:48PDT", "mono": true}, {"v": "UnassignReport faulty"}]}, {"cells": [{"v": "TAB-4475", "mono": true, "b": true, "hi": true}, {"v": "005", "mono": true, "sub": "1M2AX13C4LM030019", "subMono": true}, {"v": "SAMSARA"}, {"chip": {"tone": "green", "t": "Active", "plain": true}}, {"v": "2026-07-24 09:15PDT", "mono": true}, {"v": "UnassignReport faulty"}]}, {"cells": [{"v": "TAB-4478", "mono": true, "b": true, "hi": true}, {"v": "008", "mono": true, "sub": "3HAMMAAR2FL556128", "subMono": true}, {"v": "GEOTAB"}, {"chip": {"tone": "grey", "t": "Disconnected", "plain": true}}, {"v": "2026-07-23 06:02PDT", "mono": true}, {"v": "UnassignReport faulty"}], "state": "blocked"}, {"cells": [{"v": "TAB-4480", "mono": true, "b": true, "hi": true}, {"v": "—", "sub": "Not assigned"}, {"v": "SAMSARA"}, {"chip": {"tone": "green", "t": "Unassigned", "plain": true}}, {"v": "—", "sub": "Not captured"}, {"v": "Pair to truck"}]}]}, {"t": "text", "lines": [], "btns": [{"t": "Unassign", "kind": "secondary"}, {"t": "Report faulty", "kind": "secondary"}, {"t": "Unassign", "kind": "secondary"}]}], "hint": "7 registered"}, {"t": "note", "tone": "blue", "body": "Reporting a device faulty unpairs it, moves its truck to Out of Service with reason \"Tablet Breakdown / Device Under Repair\", and blocks dispatch. Pairing a replacement device to that truck clears the maintenance state automatically and restores it to Available — the workflow proposed by S. Kumar's tablet-installation brief."}, {"t": "legend", "items": ["CO-23 ELD integration", "CO-24 Tablet device assignment", "Notification Types TEL-001 / TEL-002", "Tablet Breakdown / Device Under Repair — engineering brief"]}], "actions": [{"t": "Add device", "kind": "secondary"}]}, {"key": "fleet", "subIdx": 7, "nav": "Fleet", "sub": "HOS Status", "frame": "02.8 Fleet — HOS Status", "title": "HOS Status", "desc": "Hours of service per truck, sourced from the ELD sync. Warning thresholds follow TEL-003 (30 minutes remaining) and TEL-004 (violation past the limit) against the 11-hour driving maximum — no other threshold is applied.", "blocks": [{"t": "panel", "title": "HOS by vehicle", "parts": [{"t": "table", "cols": [{"h": "Truck", "w": 95}, {"h": "Driver logged in", "w": 266}, {"h": "Duty status", "w": 266}, {"h": "Remaining", "w": 142}, {"h": "Location", "w": 266}, {"h": "Warning", "w": 111, "grow": true}], "rows": [{"cells": [{"v": "001", "mono": true, "b": true, "hi": true}, {"v": "Marcus Reyes", "mono": true, "sub": "0001", "subMono": true}, {"chip": {"tone": "amber", "t": "DRIVING"}}, {"v": "6.5 h"}, {"v": "I-580 near Livermore, CA"}, {"chip": {"tone": "green", "t": "OK", "plain": true}}]}, {"cells": [{"v": "002", "mono": true, "b": true, "hi": true}, {"v": "—", "sub": "No driver logged in"}, {"v": "—"}, {"v": "—"}, {"v": "—"}, {"chip": {"tone": "green", "t": "OK", "plain": true}}]}, {"cells": [{"v": "003", "mono": true, "b": true, "hi": true}, {"v": "Priya Nair", "mono": true, "sub": "0002", "subMono": true}, {"chip": {"tone": "amber", "t": "DRIVING"}}, {"v": "4.0 h"}, {"v": "CA-99 near Elk Grove, CA"}, {"chip": {"tone": "green", "t": "OK", "plain": true}}]}, {"cells": [{"v": "004", "mono": true, "b": true, "hi": true}, {"v": "—", "sub": "No driver logged in"}, {"v": "—"}, {"v": "—"}, {"v": "—"}, {"chip": {"tone": "green", "t": "OK", "plain": true}}]}, {"cells": [{"v": "005", "mono": true, "b": true, "hi": true}, {"v": "Tyler Brooks", "mono": true, "sub": "0007", "subMono": true}, {"chip": {"tone": "blue", "t": "ON_DUTY_NOT_DRIVING"}}, {"v": "7.1 h"}, {"v": "Tracy Staging"}, {"chip": {"tone": "green", "t": "OK", "plain": true}}]}, {"cells": [{"v": "008", "mono": true, "b": true, "hi": true}, {"v": "—", "sub": "No driver logged in"}, {"v": "—"}, {"v": "—"}, {"v": "—"}, {"chip": {"tone": "green", "t": "OK", "plain": true}}]}]}], "hint": "6 paired vehicles"}, {"t": "note", "tone": "blue", "body": "Open question (OC-3): no document defines what should happen if the driver who logs in has insufficient remaining hours — block the login, warn, alert dispatch, or nothing. The console warns and does not block, pending that decision."}, {"t": "legend", "items": ["Fields For HOS — HOS Duty Status", "Driver BRD §4.2 ELD-001…006", "Notification Types TEL-003 / TEL-004 / CR-021"]}]}, {"key": "drivers", "subIdx": 0, "nav": "Drivers", "sub": "All Drivers", "frame": "03 Drivers — All Drivers", "title": "All Drivers", "desc": "Click any driver for their full profile — status, documents, HOS, ratings, earnings, licence and insurance all in one place.", "actions": [{"t": "Add driver", "kind": "primary"}, {"t": "Bulk upload", "kind": "secondary"}], "blocks": [{"t": "panel", "title": "Driver roster", "hint": "8 drivers", "parts": [{"t": "filters", "label": "Driver status", "chips": [{"t": "All", "n": 8, "on": true}, {"t": "Offline", "n": 1}, {"t": "Available", "n": 2}, {"t": "On Duty", "n": 2}, {"t": "In Transit", "n": 2}, {"t": "Off Duty", "n": 1}]}, {"t": "table", "cols": [{"h": "Driver", "w": 140}, {"h": "Contact", "w": 210}, {"h": "CDL", "w": 130}, {"h": "Type", "w": 105}, {"h": "Status", "w": 135}, {"h": "HOS", "w": 130}, {"h": "Location", "w": 140}, {"h": "Dispatch eligibility", "w": 156, "grow": true}], "rows": [{"cells": [{"v": "Marcus Reyes", "b": true, "sub": "0001", "subMono": true}, {"v": "+1 408 555 0231", "mono": true, "sub": "m.reyes@apexfreight.example"}, {"v": "CA D2214870", "mono": true, "sub": "Class A · N T"}, {"v": "Salaried"}, {"chip": {"tone": "amber", "t": "In Transit"}}, {"bar": {"pct": 59, "tone": "green", "v": "6.5 h"}}, {"v": "I-580 near Livermore, CA"}, {"chip": {"tone": "green", "t": "Dispatchable", "plain": true}}]}, {"cells": [{"v": "Priya Nair", "b": true, "sub": "0002", "subMono": true}, {"v": "+1 408 555 0244", "mono": true, "sub": "p.nair@apexfreight.example"}, {"v": "CA D3390142", "mono": true, "sub": "Class A · T"}, {"v": "Salaried"}, {"chip": {"tone": "amber", "t": "In Transit"}}, {"bar": {"pct": 36, "tone": "green", "v": "4.0 h"}}, {"v": "CA-99 near Elk Grove, CA"}, {"chip": {"tone": "green", "t": "Dispatchable", "plain": true}}]}, {"cells": [{"v": "Rosa Martinez", "b": true, "sub": "0003", "subMono": true}, {"v": "+1 408 555 0255", "mono": true, "sub": "r.martinez@apexfreight.example"}, {"v": "CA D1102244", "mono": true, "sub": "Class A · N"}, {"v": "Owner-Operator"}, {"chip": {"tone": "amber", "t": "On Duty"}}, {"bar": {"pct": 76, "tone": "green", "v": "8.4 h"}}, {"v": "San Jose Hub"}, {"chip": {"tone": "green", "t": "Dispatchable", "plain": true}}]}, {"cells": [{"v": "Diego Alvarez", "b": true, "sub": "0004", "subMono": true}, {"v": "+1 408 555 0266", "mono": true, "sub": "d.alvarez@apexfreight.example"}, {"v": "CA D4471209", "mono": true, "sub": "Class A · H N"}, {"v": "Contractual"}, {"chip": {"tone": "green", "t": "Available"}}, {"bar": {"pct": 100, "tone": "green", "v": "11.0 h"}}, {"v": "San Jose Hub"}, {"chip": {"tone": "green", "t": "Dispatchable", "plain": true}}]}, {"state": "blocked", "cells": [{"v": "Sofia Torres", "b": true, "sub": "0005", "subMono": true}, {"v": "+1 408 555 0277", "mono": true, "sub": "s.torres@apexfreight.example"}, {"v": "CA D2298431", "mono": true, "sub": "Class A · T"}, {"v": "Salaried"}, {"chip": {"tone": "grey", "t": "Off Duty"}}, {"bar": {"pct": 0, "tone": "red", "v": "0.0 h"}}, {"v": "San Jose Hub"}, {"chip": {"tone": "red", "t": "Blocked"}, "sub2": "Suspended — medical_cert_expiry lapsed 2026-06-15 — FMCSA compliance failed"}]}, {"cells": [{"v": "James Carter", "b": true, "sub": "0006", "subMono": true}, {"v": "+1 775 555 0188", "mono": true, "sub": "j.carter@apexfreight.example"}, {"v": "NV D6543210", "mono": true, "sub": "Class A · N X"}, {"v": "Contractual"}, {"chip": {"tone": "green", "t": "Available"}}, {"bar": {"pct": 84, "tone": "green", "v": "9.2 h"}}, {"v": "Sacramento Depot"}, {"chip": {"tone": "green", "t": "Dispatchable", "plain": true}}]}, {"cells": [{"v": "Tyler Brooks", "b": true, "sub": "0007", "subMono": true}, {"v": "+1 209 555 0122", "mono": true, "sub": "t.brooks@apexfreight.example"}, {"v": "CA D5580117", "mono": true, "sub": "Class B"}, {"v": "Salaried"}, {"chip": {"tone": "amber", "t": "On Duty"}}, {"bar": {"pct": 65, "tone": "green", "v": "7.1 h"}}, {"v": "Tracy Staging"}, {"chip": {"tone": "green", "t": "Dispatchable", "plain": true}}]}, {"state": "blocked", "cells": [{"v": "Nadia Haddad", "b": true, "sub": "0008", "subMono": true}, {"v": "+1 916 555 0177", "mono": true, "sub": "n.haddad@apexfreight.example"}, {"v": "CA D6612903", "mono": true, "sub": "Class A · N P"}, {"v": "Contractual"}, {"chip": {"tone": "grey", "t": "Offline"}}, {"bar": {"pct": 100, "tone": "green", "v": "11.0 h"}}, {"v": "Sacramento Depot"}, {"chip": {"tone": "red", "t": "Blocked"}, "sub2": "Identity verification pending (CO-19)"}]}]}]}, {"t": "note", "tone": "blue", "body": "Dispatch eligibility is a derived gate, not a status — FMCSA medical certificate, CDL validity, identity verification (CO-19) and insurance (CO-18) must all pass before a driver can be assigned (OPS-05 / DRV-002)."}, {"t": "legend", "items": ["CO-17…CO-21 Driver onboarding", "Master Data — 19 driver statuses", "Fields For HOS", "Auth Services BRD V3 — DRVMGT"]}]}, {"key": "drivers", "subIdx": 1, "nav": "Drivers", "sub": "On Duty", "frame": "03.2 Drivers — On Duty", "title": "On Duty", "desc": "Drivers currently on duty, by Master Data driver status.", "blocks": [{"t": "panel", "title": "Driver roster", "parts": [{"t": "table", "cols": [{"h": "Driver", "w": 115}, {"h": "Contact", "w": 233}, {"h": "Cdl", "w": 124}, {"h": "Type", "w": 124}, {"h": "Status", "w": 89}, {"h": "Hos", "w": 73}, {"h": "Location", "w": 212}, {"h": "Dispatch eligibility", "w": 177, "grow": true}], "rows": [{"cells": [{"v": "Marcus Reyes", "mono": true, "b": true, "hi": true, "sub": "0001", "subMono": true}, {"v": "+1 408 555 0231", "mono": true, "sub": "m.reyes@apexfreight.example", "subMono": true}, {"v": "CA D2214870 CA", "mono": true, "sub": "Class A · N T", "subMono": true}, {"v": "Salaried"}, {"chip": {"tone": "amber", "t": "In Transit"}}, {"v": "6.5 h"}, {"v": "I-580 near Livermore, CA"}, {"chip": {"tone": "grey", "t": "Dispatchable", "plain": true}}]}, {"cells": [{"v": "Priya Nair", "mono": true, "b": true, "hi": true, "sub": "0002", "subMono": true}, {"v": "+1 408 555 0244", "mono": true, "sub": "p.nair@apexfreight.example", "subMono": true}, {"v": "CA D3390142 CA", "mono": true, "sub": "Class A · T", "subMono": true}, {"v": "Salaried"}, {"chip": {"tone": "amber", "t": "In Transit"}}, {"v": "4.0 h"}, {"v": "CA-99 near Elk Grove, CA"}, {"chip": {"tone": "grey", "t": "Dispatchable", "plain": true}}]}, {"cells": [{"v": "Rosa Martinez", "mono": true, "b": true, "hi": true, "sub": "0003", "subMono": true}, {"v": "+1 408 555 0255", "mono": true, "sub": "r.martinez@apexfreight.example", "subMono": true}, {"v": "CA D1102244 CA", "mono": true, "sub": "Class A · N", "subMono": true}, {"v": "Owner-Operator"}, {"chip": {"tone": "amber", "t": "On Duty"}}, {"v": "8.4 h"}, {"v": "San Jose Hub"}, {"chip": {"tone": "grey", "t": "Dispatchable", "plain": true}}]}, {"cells": [{"v": "Tyler Brooks", "mono": true, "b": true, "hi": true, "sub": "0007", "subMono": true}, {"v": "+1 209 555 0122", "mono": true, "sub": "t.brooks@apexfreight.example", "subMono": true}, {"v": "CA D5580117 CA", "mono": true, "sub": "Class B", "subMono": true}, {"v": "Salaried"}, {"chip": {"tone": "amber", "t": "On Duty"}}, {"v": "7.1 h"}, {"v": "Tracy Staging"}, {"chip": {"tone": "grey", "t": "Dispatchable", "plain": true}}]}]}], "hint": "8 drivers"}, {"t": "note", "tone": "blue", "body": "The eligibility column applies the FMCSA gate documented in DRV-002, CO-20, DOC-017 and DOC-019 and enforced at assignment by OPS-05. Blocked drivers cannot be selected in the assignment wizard and cannot start a truck session."}, {"t": "legend", "items": ["CO-17 / CO-18 driver onboarding", "CO-19 identity verification", "CO-20 drug & alcohol", "Master Data driver status (19 values)", "Shipment Execution OPS-05"]}], "actions": [{"t": "Add driver", "kind": "secondary"}, {"t": "Bulk upload", "kind": "secondary"}]}, {"key": "drivers", "subIdx": 2, "nav": "Drivers", "sub": "Off Duty", "frame": "03.3 Drivers — Off Duty", "title": "Off Duty", "desc": "Drivers off duty or offline.", "blocks": [{"t": "panel", "title": "Driver roster", "parts": [{"t": "table", "cols": [{"h": "Driver", "w": 101}, {"h": "Contact", "w": 236}, {"h": "Cdl", "w": 118}, {"h": "Type", "w": 92}, {"h": "Status", "w": 90}, {"h": "Hos", "w": 90}, {"h": "Location", "w": 135}, {"h": "Dispatch eligibility", "w": 287, "grow": true}], "rows": [{"cells": [{"v": "Sofia Torres", "mono": true, "b": true, "hi": true, "sub": "0005", "subMono": true}, {"v": "+1 408 555 0277", "mono": true, "sub": "s.torres@apexfreight.example", "subMono": true}, {"v": "CA D2298431 CA", "mono": true, "sub": "Class A · T", "subMono": true}, {"v": "Salaried"}, {"chip": {"tone": "grey", "t": "Off Duty"}}, {"v": "0.0 h"}, {"v": "San Jose Hub"}, {"chip": {"tone": "red", "t": "Blocked"}, "sub2": "Suspended — medical_cert_expiry lapsed 2026-06-15 — FMCSA compliance failed"}], "state": "blocked"}, {"cells": [{"v": "Nadia Haddad", "mono": true, "b": true, "hi": true, "sub": "0008", "subMono": true}, {"v": "+1 916 555 0177", "mono": true, "sub": "n.haddad@apexfreight.example", "subMono": true}, {"v": "CA D6612903 CA", "mono": true, "sub": "Class A · N P", "subMono": true}, {"v": "Contractual"}, {"chip": {"tone": "grey", "t": "Offline"}}, {"v": "11.0 h"}, {"v": "Sacramento Depot"}, {"chip": {"tone": "red", "t": "Blocked"}, "sub2": "Identity verification pending (CO-19)"}], "state": "blocked"}]}], "hint": "8 drivers"}, {"t": "note", "tone": "blue", "body": "The eligibility column applies the FMCSA gate documented in DRV-002, CO-20, DOC-017 and DOC-019 and enforced at assignment by OPS-05. Blocked drivers cannot be selected in the assignment wizard and cannot start a truck session."}, {"t": "legend", "items": ["CO-17 / CO-18 driver onboarding", "CO-19 identity verification", "CO-20 drug & alcohol", "Master Data driver status (19 values)", "Shipment Execution OPS-05"]}], "actions": [{"t": "Add driver", "kind": "secondary"}, {"t": "Bulk upload", "kind": "secondary"}]}, {"key": "loads", "subIdx": 0, "nav": "Loads", "sub": "Tenders", "frame": "04 Loads — Tenders", "title": "Tenders", "desc": "Loads awarded to Apex Freight and awaiting a reply. Accepting the tender links the rate confirmation and moves the load to Carrier Accepted (LED-02).", "blocks": [{"t": "banner", "tone": "info", "title": "Accepting a tender is its own step", "body": "Master Data’s lifecycle has \"Carrier Accepted\" as a distinct state, Ledger LED-02 makes it a carrier-dispatcher-triggered event, and DOC-026 / DOC-027 generate and sign the rate confirmation. A load is not yours to plan until the tender is accepted and the rate confirmation is signed."}, {"t": "panel", "title": "SHP-RF-10001 · FTL - Reefer", "hint": "Tender expires 2026-07-24 18:00 PDT", "parts": []}, {"t": "kpi", "cards": [{"label": "Awarded rate", "value": "$2,480", "sub": "as bid", "tone": "default"}, {"label": "Indicative break-even", "value": "$2,050", "sub": "from your cost per mile", "tone": "default"}, {"label": "Margin", "value": "$430", "small": "21%", "sub": "before penalties", "tone": "default"}, {"label": "TONU exposure", "value": "$200", "sub": "truck ordered not used", "tone": "amber"}]}, {"t": "cols", "ratio": [1, 1], "cols": [{"title": "Stops", "hint": "2 stops · LIVE unload", "parts": [{"t": "stops", "rows": [{"k": "P", "loc": "Sacramento, CA", "zip": "95814", "meta": "2026-07-26   08:00 – 12:00 UTC     22 pallets     38,400 lbs", "chip": "LIVE"}, {"k": "D", "loc": "San Jose, CA", "zip": "95112", "meta": "2026-07-26   18:00 – 22:00 UTC     22 pallets     38,400 lbs", "chip": "LIVE"}]}]}, {"title": "Load specification", "hint": "Master Data §17 commodity master", "parts": [{"t": "kv", "rows": [{"k": "Commodity", "v": "Fresh Produce", "sfx": "Refrigerated Goods"}, {"k": "Equipment required", "v": "53′ Reefer"}, {"k": "Temperature", "v": "+2 °C · range 0 °C to +4 °C"}, {"k": "Pre-cooling", "v": "", "chip": {"tone": "amber", "t": "Required"}}, {"k": "Pallets / weight", "v": "22 pallets · 38,400 lbs"}, {"k": "Rate confirmation", "v": "DOC-026", "chip": {"tone": "amber", "t": "Generated — signature required"}}, {"k": "AWB", "v": "", "empty": true}]}]}]}, {"t": "panel", "title": "Tender decision", "hint": "LED-02 · DOC-026 / DOC-027", "parts": [{"t": "text", "lines": ["Accepting signs the rate confirmation and moves SHP-RF-10001 to Carrier Accepted. Declining releases the load back for re-auction."], "btns": [{"t": "Accept tender & sign rate confirmation", "kind": "primary"}, {"t": "Decline", "kind": "secondary"}]}]}, {"t": "panel", "title": "SHP-LTL-10004 · LTL - Multiple Goods", "hint": "Tender expires 2026-07-25 09:00 PDT", "parts": []}, {"t": "kpi", "cards": [{"label": "Awarded rate", "value": "$3,120", "sub": "as bid", "tone": "default"}, {"label": "Indicative break-even", "value": "$2,640", "sub": "from your cost per mile", "tone": "default"}, {"label": "Margin", "value": "$480", "small": "18%", "sub": "before penalties", "tone": "default"}, {"label": "TONU exposure", "value": "$150", "sub": "truck ordered not used", "tone": "amber"}]}, {"t": "panel", "title": "Stops", "hint": "4 stops · 2 pickups, 2 deliveries", "parts": [{"t": "stops", "rows": [{"k": "P", "loc": "San Jose, CA", "zip": "95112", "meta": "2026-07-27   06:00 – 09:00 UTC     14 pallets     22,000 lbs", "chip": "LIVE"}, {"k": "P", "loc": "Tracy, CA", "zip": "95376", "meta": "2026-07-27   10:30 – 12:30 UTC     12 pallets     19,200 lbs", "chip": "LIVE"}, {"k": "D", "loc": "Sacramento, CA", "zip": "95814", "meta": "2026-07-27   16:00 – 19:00 UTC     14 pallets     22,000 lbs", "chip": "DROP"}, {"k": "D", "loc": "San Francisco, CA", "zip": "94103", "meta": "2026-07-28   07:00 – 10:00 UTC     12 pallets     19,200 lbs", "chip": "LUMPER"}]}]}, {"t": "legend", "items": ["Shipment Creation 1.2", "Ledger LED-01…LED-05", "DOC-026 / DOC-027 rate confirmation", "Master Data — 16 shipment statuses"]}]}, {"key": "loads", "subIdx": 1, "nav": "Loads", "sub": "Awaiting Assignment", "frame": "04.2 Loads — Awaiting Assignment", "title": "Awaiting Assignment", "desc": "Accepted loads with no truck, trailer or driver selected. This is where the carrier does its core job: choosing the truck and trailer that will run the load.", "blocks": [{"t": "panel", "title": "Awaiting Assignment", "parts": [{"t": "table", "cols": [{"h": "Load", "w": 152}, {"h": "Lane", "w": 199}, {"h": "Equipment", "w": 160}, {"h": "Status", "w": 122}, {"h": "Truck", "w": 91}, {"h": "Trailer", "w": 91}, {"h": "Driver", "w": 91}, {"h": "Progress", "w": 71}, {"h": "Rate", "w": 71}, {"h": "", "w": 99, "grow": true}], "rows": [{"cells": [{"v": "SHP-FTL-10001", "mono": true, "b": true, "hi": true, "sub": "FTL - Standard Goods", "subMono": true}, {"v": "San Jose Tracy", "sub": "95112", "subMono": true}, {"v": "Dry Van"}, {"chip": {"tone": "blue", "t": "Carrier Accepted"}}, {"chip": {"tone": "grey", "t": "Not selected", "plain": true}}, {"chip": {"tone": "grey", "t": "Not selected", "plain": true}}, {"chip": {"tone": "grey", "t": "Not selected", "plain": true}}, {"v": "—"}, {"v": "$1,840"}, {"v": "Assign assets"}]}, {"cells": [{"v": "SHP-RCR-10002", "mono": true, "b": true, "hi": true, "sub": "Dump Truck", "subMono": true}, {"v": "Fresno Quarry Modesto Site", "sub": "2 stops · Aggregate"}, {"v": "Dump Truck (Standard)"}, {"chip": {"tone": "blue", "t": "Carrier Accepted"}}, {"chip": {"tone": "grey", "t": "Not selected", "plain": true}}, {"v": "—", "sub": "N/A", "subMono": true}, {"chip": {"tone": "grey", "t": "Not selected", "plain": true}}, {"v": "—"}, {"v": "$217,350"}, {"v": "Assign assets"}]}]}, {"t": "text", "lines": [], "btns": [{"t": "Assign assets", "kind": "secondary"}, {"t": "Assign assets", "kind": "secondary"}]}], "hint": "2 loads"}, {"t": "note", "tone": "blue", "body": "Selecting assets runs the OPS-03 / OPS-04 / OPS-05 eligibility filters: capacity against shipment weight, equipment type match, annual inspection and insurance validity, asset status, CDL and medical validity, and driver status. Non-compliant assets are shown but cannot be chosen."}, {"t": "legend", "items": ["Shipment Execution OPS-01…OPS-12", "Master Data — Shipment Status (16 states)", "Super Set — per-stop execution data", "Notification Types CR-007 / FTL-01 / DT-001"]}]}];
const OFFSET = 0;

await loadFonts();
await adoptComponents(true);
const pg = await getPage(PAGE.screens);
await figma.setCurrentPageAsync(pg);

let sec = null;
pg.children.forEach(function(s){ if (s.type === 'SECTION' && s.name === 'Responsive') sec = s; });
if (!sec) throw new Error('Responsive section not found');

/* idempotent — drop anything this batch is about to (re)create */
const kill = {};
SCREENS.forEach(function(s){
  kill[s.frame + ' — Tablet 900'] = 1;
  kill[s.frame + ' — Mobile 375'] = 1;
  kill['lbl:' + s.frame] = 1;
});
sec.children.slice().forEach(function(n){ if (kill[n.name]) safe(function(){ n.remove(); }); });

/* one long row, exactly as the first three screens were laid out — heights vary
   hugely at 375 wide, so a single row removes any chance of overlap */
const SLOT = TAB_W + 60 + MOB_W + 160;
const made = [];
for (let i = 0; i < SCREENS.length; i++){
  const spec = SCREENS[i];
  const x = 80 + (OFFSET + i) * SLOT;
  const cut = spec.frame.indexOf(' ');
  const lbl = mkText(cut > 0 ? spec.frame.substring(cut + 1) : spec.frame,
                     {font:F.dispBold, size:22, lh:26, color:C.ink, name:'lbl:' + spec.frame});
  lbl.name = 'lbl:' + spec.frame;
  placeInSection(sec, lbl, x, 30);
  const t = renderScreen(spec, 'tablet');
  placeInSection(sec, t.frame, x, 80);
  const m = renderScreen(spec, 'mobile');
  placeInSection(sec, m.frame, x + TAB_W + 60, 80);
  made.push(Math.round(t.frame.width) + 'x' + Math.round(t.frame.height) + '/' +
            Math.round(m.frame.width) + 'x' + Math.round(m.frame.height));
}
fitSection(sec, 80);
const badT = made.filter(function(r){ return r.indexOf('900x') !== 0; }).length;
const badM = made.filter(function(r){ return r.split('/')[1].indexOf('375x') !== 0; }).length;
RESULT = { n: made.length, badT: badT, badM: badM, secKids: sec.children.length };

  report = 'RESP1 n=' + RESULT.n + ' badTablet=' + RESULT.badT + ' badMobile=' + RESULT.badM + ' secKids=' + RESULT.secKids;
} catch (err) { report = 'FAIL1 ' + (err && err.message ? err.message : String(err)).substring(0, 140); }
try {
  var p3 = null;
  figma.root.children.forEach(function(p){ if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
