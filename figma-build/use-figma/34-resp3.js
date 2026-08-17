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

const SCREENS = [{"key": "alerts", "subIdx": 0, "nav": "Notifications", "sub": "Notifications", "frame": "09 Notifications", "title": "Notifications", "desc": "Every alert in one place. Open any item to acknowledge it, call the driver, or join their chat thread — no need to leave this page.", "actions": [{"t": "Mark all read", "kind": "secondary"}], "blocks": [{"t": "banner", "tone": "crit", "title": "SOS alert from Driver Tyler Brooks", "body": "Emergency (911) status received with GPS 37.6390, -120.9969 on TRIP-58024. Emergency response coordinator notified. Acknowledge to confirm dispatch has seen this.", "btns": [{"t": "Acknowledge", "kind": "danger"}, {"t": "Call driver", "kind": "secondary"}]}, {"t": "panel", "title": "All notifications", "hint": "8 unread of 22", "parts": [{"t": "filters", "label": "Category", "chips": [{"t": "All", "n": 22, "on": true}, {"t": "SOS", "n": 1}, {"t": "Telematics", "n": 3}, {"t": "Documents", "n": 3}, {"t": "Assets", "n": 2}, {"t": "Yard", "n": 2}, {"t": "Loads", "n": 2}, {"t": "Safety", "n": 2}, {"t": "Penalties", "n": 1}, {"t": "Onboarding", "n": 1}, {"t": "Detention", "n": 2}, {"t": "Exceptions", "n": 3}]}, {"t": "list", "items": [{"sev": "crit", "unread": true, "title": "SOS alert from Driver Tyler Brooks", "body": "Emergency (911) status received with GPS 37.6390, -120.9969 on TRIP-58024. Emergency response coordinator notified.", "code": "CR-025 · SOS", "time": "4m ago", "btn": "Call driver"}, {"sev": "crit", "unread": true, "title": "ELD disconnected — TRK-CARR-US-00142-008", "body": "HOS logs may be incomplete. Device TAB-4478 last synced 2026-07-23 06:02 PDT. Verify on the driver app and re-pair the device.", "code": "TEL-002 · Telematics", "time": "26m ago"}, {"sev": "warn", "unread": true, "title": "Insurance certificate expires in 19 days", "body": "COI expires 2026-08-12. Escalation tier \"3 weeks\" reached per CO-09. Marketplace access is suspended automatically on expiry (DOC-011).", "code": "DOC-009 · Documents", "time": "1h ago"}, {"sev": "crit", "unread": false, "title": "Asset TRK-CARR-US-00142-004 is Out of Service", "body": "DVIR defect reported 2026-07-19: hydraulic leak, rear tipper ram. Dispatch is blocked while the asset is Out of Service.", "code": "AST-007 · Assets", "time": "2h ago"}, {"sev": "warn", "unread": false, "title": "Asset TRK-CARR-US-00142-008 is on Halt", "body": "Halt reported at San Jose Hub. Reason: insurance lapsed — asset withheld from dispatch pending renewal.", "code": "AST-004 · Assets", "time": "2h ago"}, {"sev": "warn", "unread": false, "title": "CDL expiring — James Carter", "body": "CDL NV D6543210 expires 2026-09-12. Renewal at the state DMV required. Driver becomes non-dispatchable on expiry (DOC-017).", "code": "DOC-016 · Documents", "time": "3h ago", "btn": "Call driver"}, {"sev": "warn", "unread": false, "title": "Medical certificate expiring — Tyler Brooks", "body": "Medical Examiner Certificate expires 2026-07-30 — six days. Driving privileges suspend on expiry (DOC-019).", "code": "DOC-018 · Documents", "time": "3h ago", "btn": "Call driver"}, {"sev": "warn", "unread": true, "title": "HOS warning — Priya Nair, 30 minutes remaining", "body": "30 minutes remain on the driving window for TRIP-58022. Plan a safe stop. Violation is logged automatically past the limit (TEL-004).", "code": "TEL-003 · Telematics", "time": "42m ago"}, {"sev": "ok", "unread": false, "title": "Truck TRK-CARR-US-00142-001 assigned to SHP-FTL-10005", "body": "Assignment confirmed by M. Whitfield (Dispatcher). Trailer TRL-CARR-US-00142-011 linked as PRIMARY.", "code": "CR-007 · Loads", "time": "8h ago"}, {"sev": "ok", "unread": true, "title": "Bid accepted — SHP-RF-10001", "body": "Your bid has been accepted for Shipment SHP-RF-10001 at $2,480. Accept the tender and sign the rate confirmation to proceed.", "code": "CR-005 · Loads", "time": "9h ago"}]}]}, {"t": "legend", "items": ["Notification Types — CR / DR / AST / TEL / DOC / YD / SAF / ONB / PEN / CS", "CO-09 five-tier expiry ladder"]}]}, {"key": "reports", "subIdx": 0, "nav": "Reports", "sub": "Operations", "frame": "10 Reports — Operations", "title": "Operations reports", "desc": "Fleet, driver and compliance reporting. All five carrier roles hold a view right; export is restricted.", "actions": [{"t": "Export CSV", "kind": "secondary"}], "blocks": [{"t": "kpi", "cards": [{"label": "Fleet utilisation", "value": "63%", "sub": "5 of 8 engaged", "tone": "default"}, {"label": "Dispatchable assets", "value": "3", "sub": "of 8 registered", "tone": "amber"}, {"label": "Compliant drivers", "value": "6", "sub": "of 8 on roster", "tone": "blue"}]}, {"t": "kpi", "cards": [{"label": "On-time delivery", "value": "94%", "sub": "last 30 days", "tone": "default"}, {"label": "Documents expiring ≤30 d", "value": "4", "sub": "carrier + driver", "tone": "red"}, {"label": "Loads completed (30 d)", "value": "1", "sub": "across all freight types", "tone": "grey"}]}, {"t": "panel", "title": "Freight mix by type", "hint": "Master Data — Types of Shipment", "parts": [{"t": "bars", "rows": [{"label": "FTL - Standard Goods", "sub": "SHP-FTL", "value": "3", "pct": 100, "tone": "green"}, {"label": "FTL - Reefer", "sub": "SHP-RF", "value": "1", "pct": 33, "tone": "green"}, {"label": "LTL - Multiple Goods", "sub": "SHP-LTL", "value": "2", "pct": 66, "tone": "green"}, {"label": "Dump Truck", "sub": "SHP-RCR", "value": "2", "pct": 66, "tone": "green"}, {"label": "Multileg", "sub": "SHP-LTL", "value": "1", "pct": 33, "tone": "green"}]}]}, {"t": "panel", "title": "Route profitability & revenue per mile", "action": {"t": "Export", "kind": "secondary"}, "parts": [{"t": "table", "cols": [{"h": "Lane", "w": 180}, {"h": "Loads", "w": 80}, {"h": "Loaded miles", "w": 120}, {"h": "Deadhead", "w": 110}, {"h": "Revenue", "w": 110}, {"h": "RPM", "w": 100}, {"h": "Fuel", "w": 100}, {"h": "Margin vs break-even", "w": 346, "grow": true}], "rows": [{"cells": [{"v": "San Jose  →  Tracy", "b": true}, {"v": "3"}, {"v": "186 mi"}, {"v": "33 mi", "sub": "15% of total"}, {"v": "$5,580", "b": true}, {"v": "$25.48", "b": true}, {"v": "$619"}, {"v": "$960", "b": true, "color": "#0e5a37", "sub": "21% over break-even", "subColor": "#586173"}]}, {"cells": [{"v": "Sacramento  →  San Jose", "b": true}, {"v": "2"}, {"v": "236 mi"}, {"v": "21 mi", "sub": "8% of total"}, {"v": "$5,220", "b": true}, {"v": "$20.31", "b": true}, {"v": "$798"}, {"v": "$890", "b": true, "color": "#0e5a37", "sub": "21% over break-even", "subColor": "#586173"}]}, {"cells": [{"v": "San Jose  →  Sacramento", "b": true}, {"v": "1"}, {"v": "154 mi"}, {"v": "18 mi", "sub": "10% of total"}, {"v": "$5,100", "b": true}, {"v": "$29.65", "b": true}, {"v": "$512"}, {"v": "$800", "b": true, "color": "#0e5a37", "sub": "19% over break-even", "subColor": "#586173"}]}, {"cells": [{"v": "Fresno  →  Modesto", "b": true}, {"v": "2"}, {"v": "192 mi"}, {"v": "44 mi", "sub": "23% of total"}, {"v": "$349,650", "b": true}, {"v": "$1,821", "b": true}, {"v": "$1,940"}, {"v": "$58,650", "b": true, "color": "#0e5a37", "sub": "20% over break-even", "subColor": "#586173"}]}, {"state": "blocked", "cells": [{"v": "Salinas  →  San Francisco", "b": true}, {"v": "0"}, {"v": "—"}, {"v": "—"}, {"v": "$0"}, {"v": "—"}, {"v": "—"}, {"v": "Lost at auction", "color": "#8f2626", "b": true, "sub": "AUC-76998 · ours $1,620 vs $1,485", "subColor": "#586173"}]}]}]}, {"t": "legend", "items": ["Auth Services BRD V3 — REP", "Ledger — settlement", "Master Data — Types of Shipment"]}]}, {"key": "earnings", "subIdx": 0, "nav": "Earnings", "sub": "Earnings", "frame": "11 Earnings — Earnings", "title": "Earnings", "desc": "Revenue, margin and outstanding payments in one place. Approve a pending payment to queue it for payout, pay it immediately once approved, or open a dispute chat directly with mySHIPR admin.", "actions": [{"t": "Update payment details", "kind": "secondary"}], "blocks": [{"t": "kpi", "cards": [{"label": "Gross revenue", "value": "$368,670", "sub": "all loads in view", "tone": "default"}, {"label": "Net margin", "value": "22%", "sub": "after fuel, maintenance & settlement", "tone": "blue"}, {"label": "Recurring programmes", "value": "$349,650", "sub": "dump truck contracts", "tone": "grey"}, {"label": "Outstanding balance", "value": "$5,060", "sub": "4 payments awaiting action", "tone": "red"}]}, {"t": "panel", "title": "Outstanding payments", "hint": "5", "parts": [{"t": "table", "cols": [{"h": "Payment", "w": 240}, {"h": "Load", "w": 180}, {"h": "Amount", "w": 120}, {"h": "Due", "w": 140}, {"h": "Status", "w": 220}, {"h": "Actions", "w": 246, "grow": true}], "rows": [{"cells": [{"v": "PMT-CARR-US-00142-0001", "mono": true, "hi": true}, {"v": "SHP-FTL-10003", "mono": true}, {"v": "$2,380", "b": true}, {"v": "2026-07-30", "mono": true}, {"chip": {"tone": "amber", "t": "Pending", "plain": true}}, {"btns": [{"t": "Approve", "kind": "secondary"}, {"t": "Dispute", "kind": "secondary"}]}]}, {"cells": [{"v": "PMT-CARR-US-00142-0002", "mono": true, "hi": true}, {"v": "SHP-RCR-10005", "mono": true}, {"v": "$1,180", "b": true}, {"v": "2026-07-29", "mono": true}, {"chip": {"tone": "blue", "t": "Approved", "plain": true}}, {"btns": [{"t": "Pay now", "kind": "primary"}, {"t": "Dispute", "kind": "secondary"}]}]}, {"state": "blocked", "cells": [{"v": "PMT-CARR-US-00142-0003", "mono": true, "hi": true}, {"v": "SHP-LTL-10002", "mono": true}, {"v": "$640", "b": true}, {"v": "2026-07-25", "mono": true}, {"chip": {"tone": "red", "t": "Disputed", "plain": true}, "sub2": "Rate mismatch vs rate confirmation"}, {"btns": [{"t": "Dispute", "kind": "secondary"}]}]}, {"cells": [{"v": "PMT-CARR-US-00142-0004", "mono": true, "hi": true}, {"v": "SHP-FTL-10005", "mono": true}, {"v": "$1,920", "b": true}, {"v": "2026-07-20", "mono": true}, {"chip": {"tone": "green", "t": "Paid", "plain": true}}, {}]}, {"cells": [{"v": "PMT-CARR-US-00142-0005", "mono": true, "hi": true}, {"v": "SHP-RCR-10002", "mono": true}, {"v": "$860", "b": true}, {"v": "2026-08-02", "mono": true}, {"chip": {"tone": "amber", "t": "Pending", "plain": true}}, {"btns": [{"t": "Approve", "kind": "secondary"}, {"t": "Dispute", "kind": "secondary"}]}]}]}]}, {"t": "panel", "title": "Revenue by load", "hint": "9 loads", "parts": [{"t": "table", "cols": [{"h": "Load", "w": 150}, {"h": "Type", "w": 180}, {"h": "Lane", "w": 300}, {"h": "Status", "w": 190}, {"h": "Rate", "w": 110}, {"h": "Break-even", "w": 110}, {"h": "Margin", "w": 106, "grow": true}], "rows": [{"cells": [{"v": "SHP-RF-10001", "mono": true, "hi": true}, {"v": "FTL - Reefer"}, {"v": "Sacramento  →  San Jose", "sub": "95814  →  95112", "subMono": true}, {"chip": {"tone": "purple", "t": "Tendered"}}, {"v": "$2,480", "b": true}, {"v": "$2,050"}, {"v": "$430", "b": true, "color": "#0e5a37"}]}, {"cells": [{"v": "SHP-LTL-10004", "mono": true, "hi": true}, {"v": "LTL - Multiple Goods"}, {"v": "San Jose  →  San Francisco", "sub": "95112  →  94103", "subMono": true}, {"chip": {"tone": "purple", "t": "Tendered"}}, {"v": "$3,120", "b": true}, {"v": "$2,640"}, {"v": "$480", "b": true, "color": "#0e5a37"}]}, {"cells": [{"v": "SHP-FTL-10001", "mono": true, "hi": true}, {"v": "FTL - Standard Goods"}, {"v": "San Jose  →  Tracy", "sub": "95112  →  95376", "subMono": true}, {"chip": {"tone": "blue", "t": "Carrier Accepted"}}, {"v": "$1,840", "b": true}, {"v": "$1,520"}, {"v": "$320", "b": true, "color": "#0e5a37"}]}, {"cells": [{"v": "SHP-RCR-10002", "mono": true, "hi": true}, {"v": "Dump Truck"}, {"v": "Fresno Quarry  →  Modesto Site"}, {"chip": {"tone": "blue", "t": "Carrier Accepted"}}, {"v": "$217,350", "b": true}, {"v": "$181,000"}, {"v": "$36,350", "b": true, "color": "#0e5a37"}]}, {"cells": [{"v": "SHP-FTL-10005", "mono": true, "hi": true}, {"v": "FTL - Standard Goods"}, {"v": "San Jose  →  Tracy", "sub": "95112  →  95376", "subMono": true}, {"chip": {"tone": "amber", "t": "In Transit"}}, {"v": "$1,960", "b": true}, {"v": "$1,610"}, {"v": "$350", "b": true, "color": "#0e5a37"}]}, {"cells": [{"v": "SHP-LTL-10002", "mono": true, "hi": true}, {"v": "LTL - Multiple Goods"}, {"v": "Sacramento  →  San Jose", "sub": "95814  →  95112", "subMono": true}, {"chip": {"tone": "amber", "t": "In Transit"}}, {"v": "$2,740", "b": true}, {"v": "$2,280"}, {"v": "$460", "b": true, "color": "#0e5a37"}]}, {"cells": [{"v": "SHP-RCR-10005", "mono": true, "hi": true}, {"v": "Dump Truck"}, {"v": "Fresno Quarry  →  Modesto Site"}, {"chip": {"tone": "blue", "t": "At Delivery/Dump"}}, {"v": "$132,300", "b": true}, {"v": "$110,000"}, {"v": "$22,300", "b": true, "color": "#0e5a37"}]}]}]}, {"t": "legend", "items": ["Ledger — LED-01…LED-05", "CO-29 financial setup", "Auth Services BRD V3 — BILL / PAY"]}]}, {"key": "earnings", "subIdx": 1, "nav": "Earnings", "sub": "Salary Payout", "frame": "11.2 Earnings — Salary Payout", "title": "Driver Settlement", "desc": "One settlement view covering all three CO-18 driver types and all four payment models. AWB and shipment ID are now separate columns.", "blocks": [{"t": "banner", "tone": "info", "title": "One settlement view for every driver type", "body": "CO-18 defines three driver types — Salaried, Contractual and Owner-Operator — and four payment models: Per Mile, Per Load, percentage and Salary. All of them settle here. Payment timing and commission are governed by the platform and are not shown on this screen."}, {"t": "panel", "title": "Settlement by driver", "parts": [{"t": "table", "cols": [{"h": "Driver", "w": 154}, {"h": "DRIVER TYPE (CO-18)", "w": 226}, {"h": "Payment model", "w": 154}, {"h": "Rate", "w": 167}, {"h": "Associated awb", "w": 202}, {"h": "Shipments", "w": 243, "grow": true}], "rows": [{"cells": [{"v": "Marcus Reyes", "b": true, "hi": true}, {"v": "Salaried"}, {"v": "Salary", "mono": true}, {"v": "$6,400 / month"}, {"v": "—", "sub": "No air segment"}, {"v": "SHP-FTL-10005", "mono": true}]}, {"cells": [{"v": "Priya Nair", "b": true, "hi": true}, {"v": "Salaried"}, {"v": "Salary", "mono": true}, {"v": "$6,100 / month"}, {"chip": {"tone": "green", "t": "Check digit valid", "plain": true}, "sub2": "180-12345675"}, {"v": "SHP-LTL-10002", "mono": true}]}, {"cells": [{"v": "Rosa Martinez", "b": true, "hi": true}, {"v": "Owner-Operator"}, {"v": "Per Mile", "mono": true}, {"v": "$0.72 / mile"}, {"chip": {"tone": "green", "t": "Check digit valid", "plain": true}, "sub2": "180-23456786"}, {"v": "SHP-FTL-10003SHP-LTL-10003", "mono": true}]}, {"cells": [{"v": "Diego Alvarez", "b": true, "hi": true}, {"v": "Contractual"}, {"v": "Per Load", "mono": true}, {"v": "$310 / load"}, {"v": "—", "sub": "No air segment"}, {"v": "—", "sub": "None"}]}, {"cells": [{"v": "Sofia Torres", "b": true, "hi": true}, {"v": "Salaried"}, {"v": "Salary", "mono": true}, {"v": "$6,000 / month"}, {"v": "—", "sub": "No air segment"}, {"v": "—", "sub": "None"}]}, {"cells": [{"v": "James Carter", "b": true, "hi": true}, {"v": "Contractual"}, {"v": "Per Mile", "mono": true}, {"v": "$0.68 / mile"}, {"v": "—", "sub": "No air segment"}, {"v": "—", "sub": "None"}]}, {"cells": [{"v": "Tyler Brooks", "b": true, "hi": true}, {"v": "Salaried"}, {"v": "Salary", "mono": true}, {"v": "$5,400 / month"}, {"v": "—", "sub": "No air segment"}, {"v": "SHP-RCR-10005", "mono": true}]}]}, {"t": "pager", "range": "Showing 1–7 of 8"}], "hint": "8 drivers"}, {"t": "note", "tone": "blue", "body": "AWB and shipment ID are separate identifiers. AWB follows the format {AIRLINE_PREFIX_3}-{SERIAL_8} with a modulo-7 check digit and is only present where the shipment has an air segment."}, {"t": "legend", "items": ["CO-18 driver payment configuration", "Driver BRD DT-28 / ERN-004", "FTL Master Reference §C5", "Auth Services BRD V3 — AWB"]}]}, {"key": "settings", "subIdx": 0, "nav": "Settings", "sub": "My Profile", "frame": "12 Settings — My Profile", "title": "My Profile", "desc": "Your personal account details, distinct from the organisation-wide settings under Company Settings.", "actions": [{"t": "Edit profile", "kind": "secondary"}], "blocks": [{"t": "cols", "ratio": [1.6, 1], "cols": [[{"title": "Account", "hint": "Signed in as", "parts": [{"t": "kv", "rows": [{"k": "Name", "v": "D. Rao"}, {"k": "Email", "v": "d.rao@apexfreight.example"}, {"k": "Role", "v": "Carrier Super Admin", "sfx": "CSA"}, {"k": "Multi-factor authentication", "v": "", "chip": {"tone": "green", "t": "Enabled"}}, {"k": "Last sign-in", "v": "2026-07-24 08:02 PDT"}]}]}, {"title": "Password & security", "hint": "personal", "parts": [{"t": "text", "lines": ["Organisation-wide sessions and lockout policy are under Settings → Sessions."], "btns": [{"t": "Change password", "kind": "secondary"}, {"t": "Re-enrol MFA device", "kind": "secondary"}]}]}], [{"title": "Display", "hint": "Master Data §18", "parts": [{"t": "text", "lines": ["Timestamps are stored in UTC and rendered in this zone on every screen. §18 gives the Carrier Super Admin, Fleet Manager, Dispatcher and Compliance Manager a user-configured zone; the Driver alone follows device/GPS time."]}, {"t": "kv", "rows": [{"k": "Company default", "v": "America/Los_Angeles", "sfx": "PDT — from the registered address"}, {"k": "Sample timestamp", "v": "2026-07-24 09:12 PDT"}, {"k": "Density", "v": "Comfortable"}]}]}]]}, {"t": "legend", "items": ["Auth Services BRD V3 — self-managed account fields", "Master Data §18 time zones"]}]}, {"key": "settings", "subIdx": 1, "nav": "Settings", "sub": "Notification Preferences", "frame": "12.2 Settings — Notification Preferences", "title": "Notification Preferences", "desc": "How you personally are notified. This does not change what appears in the Notifications section — only how you are alerted.", "blocks": [{"t": "panel", "title": "Delivery channels", "parts": [{"t": "text", "lines": ["Critical alerts (SOS, breakdown, compliance)", "Load tenders & assignment", "Document & compliance reminders", "Messages from drivers", "Weekly / monthly financial reports"]}], "hint": "per notification type"}, {"t": "legend", "items": ["Personal preference — does not affect Notifications section content or audit trail"]}]}, {"key": "settings", "subIdx": 2, "nav": "Settings", "sub": "Roles & Users", "frame": "12.3 Settings — Roles & Users", "title": "Roles & Users", "desc": "Every person in the carrier organisation, their role, session state and admin controls — plus the permission matrix those roles are built from. The carrier admin assigns roles from a fixed permission catalogue, and may compose new roles from that same catalogue.", "blocks": [{"t": "banner", "tone": "warn", "title": "Auth Services BRD V3 contains two matrices that disagree", "body": "The Role Permission Matrix grants drivers.add, drivers.onboard and drivers.update to the Carrier Super Admin alone; the \"Dummy Functional Matrix\" grants Driver Management Create/View/Update to the Dispatcher; CO-17/18/22 name the Fleet Manager. This console implements the Role Permission Matrix and flags the conflict."}, {"t": "panel", "title": "Organisation users", "parts": [{"t": "table", "cols": [{"h": "User", "w": 264}, {"h": "Role", "w": 210}, {"h": "Status", "w": 110}, {"h": "Security", "w": 88}, {"h": "Last sign-in", "w": 210}, {"h": "Actions", "w": 264, "grow": true}], "rows": [{"cells": [{"v": "D. Rao", "b": true, "hi": true, "sub": "d.rao@apexfreight.example"}, {"v": "Carrier Super Admin"}, {"chip": {"tone": "green", "t": "Active", "plain": true}}, {"v": "MFA on"}, {"v": "2026-07-24 08:02PDT", "mono": true}, {"v": "Change roleFreezeRevoke sessions"}]}, {"cells": [{"v": "K. Osei", "b": true, "hi": true, "sub": "k.osei@apexfreight.example"}, {"v": "Fleet Manager"}, {"chip": {"tone": "green", "t": "Active", "plain": true}}, {"v": "MFA on"}, {"v": "2026-07-24 07:40PDT", "mono": true}, {"v": "Change roleFreezeRevoke sessions"}]}, {"cells": [{"v": "M. Whitfield", "b": true, "hi": true, "sub": "m.whitfield@apexfreight.example"}, {"v": "Dispatcher"}, {"chip": {"tone": "green", "t": "Active", "plain": true}}, {"v": "MFA on"}, {"v": "2026-07-24 06:12PDT", "mono": true}, {"v": "Change roleFreezeRevoke sessions"}]}, {"cells": [{"v": "A. Beckett", "b": true, "hi": true, "sub": "a.beckett@apexfreight.example"}, {"v": "Compliance Manager"}, {"chip": {"tone": "green", "t": "Active", "plain": true}}, {"v": "MFA on"}, {"v": "2026-07-23 16:55PDT", "mono": true}, {"v": "Change roleFreezeRevoke sessions"}]}, {"cells": [{"v": "S. Iyer", "b": true, "hi": true, "sub": "s.iyer@apexfreight.example"}, {"v": "System Admin"}, {"chip": {"tone": "green", "t": "Active", "plain": true}}, {"v": "MFA on"}, {"v": "2026-07-22 11:30PDT", "mono": true}, {"v": "Change roleFreezeRevoke sessions"}]}, {"cells": [{"v": "L. Marino", "b": true, "hi": true, "sub": "l.marino@apexfreight.example"}, {"v": "Dispatcher"}, {"chip": {"tone": "green", "t": "Unverified", "plain": true}}, {"v": "MFA off"}, {"v": "—", "sub": "Never signed in"}, {"v": "Change roleFreezeRevoke sessions"}]}, {"cells": [{"v": "R. Okafor", "b": true, "hi": true, "sub": "r.okafor@apexfreight.example"}, {"v": "Fleet Manager"}, {"chip": {"tone": "red", "t": "Suspended", "plain": true}}, {"v": "MFA on"}, {"v": "2026-06-30 09:14PDT", "mono": true}, {"v": "Change roleFreezeReactivate"}]}]}, {"t": "text", "lines": [], "btns": [{"t": "Change role", "kind": "secondary"}, {"t": "Freeze", "kind": "secondary"}, {"t": "Revoke sessions", "kind": "secondary"}]}], "hint": "7 accounts"}, {"t": "panel", "title": "Functional matrix — fixed permission set", "parts": [{"t": "table", "cols": [{"h": "Functional category", "w": 212}, {"h": "Carrier super admin", "w": 194}, {"h": "Fleet manager", "w": 194}, {"h": "Dispatcher", "w": 194}, {"h": "Compliance manager", "w": 159}, {"h": "System admin", "w": 194, "grow": true}], "rows": [{"cells": [{"v": "Organization & Setup", "mono": true, "b": true, "hi": true, "sub": "ORG", "subMono": true}, {"chip": {"tone": "grey", "t": "CREATE / VIEW / UPDATE", "plain": true}}, {"chip": {"tone": "grey", "t": "ONLY VIEW", "plain": true}}, {"chip": {"tone": "grey", "t": "ONLY VIEW", "plain": true}}, {"chip": {"tone": "grey", "t": "ONLY VIEW", "plain": true}}, {"chip": {"tone": "grey", "t": "ONLY VIEW", "plain": true}}]}, {"cells": [{"v": "Roles & User Management", "mono": true, "b": true, "hi": true, "sub": "USERS", "subMono": true}, {"chip": {"tone": "grey", "t": "CREATE / VIEW / UPDATE", "plain": true}}, {"v": "—"}, {"v": "—"}, {"v": "—"}, {"chip": {"tone": "grey", "t": "CREATE / VIEW / UPDATE", "plain": true}}]}, {"cells": [{"v": "Shipment Management", "mono": true, "b": true, "hi": true, "sub": "SHIP", "subMono": true}, {"chip": {"tone": "grey", "t": "ONLY VIEW", "plain": true}}, {"v": "—"}, {"chip": {"tone": "grey", "t": "ONLY VIEW", "plain": true}}, {"v": "—"}, {"v": "—"}]}, {"cells": [{"v": "Load Board & Auctions", "mono": true, "b": true, "hi": true, "sub": "LOAD", "subMono": true}, {"chip": {"tone": "grey", "t": "CREATE / VIEW / UPDATE", "plain": true}}, {"v": "—"}, {"chip": {"tone": "grey", "t": "CREATE / VIEW / UPDATE", "plain": true}}, {"v": "—"}, {"v": "—"}]}, {"cells": [{"v": "Shipment Tracking", "mono": true, "b": true, "hi": true, "sub": "TRACK", "subMono": true}, {"chip": {"tone": "grey", "t": "ONLY VIEW", "plain": true}}, {"chip": {"tone": "grey", "t": "ONLY VIEW", "plain": true}}, {"chip": {"tone": "grey", "t": "ONLY VIEW", "plain": true}}, {"v": "—"}, {"chip": {"tone": "grey", "t": "ONLY VIEW", "plain": true}}]}, {"cells": [{"v": "Delivery & POD", "mono": true, "b": true, "hi": true, "sub": "POD", "subMono": true}, {"chip": {"tone": "grey", "t": "CREATE / VIEW / UPDATE", "plain": true}}, {"v": "—"}, {"chip": {"tone": "grey", "t": "ONLY VIEW", "plain": true}}, {"v": "—"}, {"v": "—"}]}, {"cells": [{"v": "Fleet & Truck Management", "mono": true, "b": true, "hi": true, "sub": "FLEET", "subMono": true}, {"chip": {"tone": "grey", "t": "CREATE / VIEW / UPDATE", "plain": true}}, {"chip": {"tone": "grey", "t": "CREATE / VIEW / UPDATE", "plain": true}}, {"v": "—"}, {"chip": {"tone": "grey", "t": "ONLY VIEW", "plain": true}}, {"v": "—"}]}]}, {"t": "pager", "range": "Showing 1–7 of 14"}], "hint": "14 categories · 75 permission codes"}, {"t": "panel", "title": "Permission codes in force", "parts": [{"t": "table", "cols": [{"h": "Permission code", "w": 345}, {"h": "Name", "w": 345}, {"h": "Category", "w": 216}, {"h": "Your role", "w": 242, "grow": true}], "rows": [{"cells": [{"v": "org.profile.view", "mono": true, "b": true, "hi": true}, {"v": "View Organization Profile"}, {"v": "ORG", "mono": true}, {"chip": {"tone": "grey", "t": "Granted", "plain": true}}]}, {"cells": [{"v": "org.profile.update", "mono": true, "b": true, "hi": true}, {"v": "Update Organization Profile"}, {"v": "ORG", "mono": true}, {"chip": {"tone": "grey", "t": "Granted", "plain": true}}]}, {"cells": [{"v": "org.contacts.manage", "mono": true, "b": true, "hi": true}, {"v": "Manage Company Contacts"}, {"v": "ORG", "mono": true}, {"chip": {"tone": "grey", "t": "Granted", "plain": true}}]}, {"cells": [{"v": "org.addresses.manage", "mono": true, "b": true, "hi": true}, {"v": "Manage Company Addresses"}, {"v": "ORG", "mono": true}, {"chip": {"tone": "grey", "t": "Granted", "plain": true}}]}, {"cells": [{"v": "users.invite", "mono": true, "b": true, "hi": true}, {"v": "Invite / Create User"}, {"v": "USERS", "mono": true}, {"chip": {"tone": "grey", "t": "Granted", "plain": true}}]}, {"cells": [{"v": "users.view", "mono": true, "b": true, "hi": true}, {"v": "View Users"}, {"v": "USERS", "mono": true}, {"chip": {"tone": "grey", "t": "Granted", "plain": true}}]}, {"cells": [{"v": "users.status.manage", "mono": true, "b": true, "hi": true}, {"v": "Manage User Status"}, {"v": "USERS", "mono": true}, {"chip": {"tone": "grey", "t": "Granted", "plain": true}}]}]}, {"t": "pager", "range": "Showing 1–7 of 43"}], "hint": "selected from the 75-code catalogue"}, {"t": "note", "tone": "blue", "body": "Freeze shuts a user down immediately — every active session ends and sign-in is blocked until an admin unfreezes the account. Invites enforce a unique email within the organisation and return 409 Conflict on duplicates (CO-28). Role assignment, freeze/unfreeze and revocation all emit an audit event (see Audit Logs)."}, {"t": "legend", "items": ["CO-28 Invite user", "Auth Services BRD V3 — Permission Categories, Permission Catalogue, Role Permission Matrix", "Notification Types AU-014…AU-023"]}], "actions": [{"t": "Create role", "kind": "secondary"}, {"t": "Invite user", "kind": "secondary"}]}, {"key": "settings", "subIdx": 3, "nav": "Settings", "sub": "Audit Logs", "frame": "12.4 Settings — Audit Logs", "title": "Audit Logs", "desc": "Every role assignment, freeze/unfreeze, session revocation and role-creation event in this organisation, each carrying an Audit ID.", "blocks": [{"t": "panel", "title": "Audit events", "parts": [{"t": "table", "cols": [{"h": "Audit id", "w": 148}, {"h": "Timestamp", "w": 296}, {"h": "Actor", "w": 111}, {"h": "Action", "w": 296}, {"h": "Detail", "w": 296, "grow": true}], "rows": [{"cells": [{"v": "AU-023", "mono": true, "b": true, "hi": true}, {"v": "2026-07-24 08:05PDT", "mono": true}, {"v": "D. Rao"}, {"v": "User viewed"}, {"v": "S. Iyer profile viewed"}]}, {"cells": [{"v": "AU-021", "mono": true, "b": true, "hi": true}, {"v": "2026-07-23 16:55PDT", "mono": true}, {"v": "D. Rao"}, {"v": "Role assigned"}, {"v": "A. Beckett → Compliance Manager"}]}, {"cells": [{"v": "AU-022", "mono": true, "b": true, "hi": true}, {"v": "2026-06-30 09:20PDT", "mono": true}, {"v": "D. Rao"}, {"v": "Sessions revoked"}, {"v": "R. Okafor — 1 session revoked"}]}, {"cells": [{"v": "AU-014", "mono": true, "b": true, "hi": true}, {"v": "2026-06-30 09:14PDT", "mono": true}, {"v": "System"}, {"v": "User suspended"}, {"v": "R. Okafor — compliance hold"}]}, {"cells": [{"v": "AU-018", "mono": true, "b": true, "hi": true}, {"v": "2026-05-11 10:02PDT", "mono": true}, {"v": "D. Rao"}, {"v": "User invited"}, {"v": "L. Marino invited as Dispatcher"}]}]}], "hint": "5 events"}, {"t": "note", "tone": "blue", "body": "Audit IDs follow the AU-0xx series (AU-014 status changes, AU-018 invites, AU-021 role assignment, AU-022 session revocation, AU-023 profile views). Every entry is immutable once written."}, {"t": "legend", "items": ["Auth Services BRD V3 — USERS category", "Notification Types AU-014…AU-023"]}], "actions": [{"t": "Export", "kind": "secondary"}]}, {"key": "settings", "subIdx": 4, "nav": "Settings", "sub": "Sessions", "frame": "12.5 Settings — Sessions", "title": "Sessions", "desc": "Active sign-ins across every user in the organisation, and the security policy that governs them.", "blocks": [{"t": "panel", "title": "Active sessions", "parts": [{"t": "table", "cols": [{"h": "User", "w": 287}, {"h": "Device", "w": 287}, {"h": "Started", "w": 287}, {"h": "Action", "w": 287, "grow": true}], "rows": [{"cells": [{"v": "D. Rao this session", "b": true, "hi": true}, {"v": "Chrome · macOS 15"}, {"v": "2026-07-24 08:02PDT", "mono": true}, {"v": "—", "sub": "Current session"}]}, {"cells": [{"v": "D. Rao", "b": true, "hi": true}, {"v": "mySHIPR — iOS app"}, {"v": "2026-07-22 14:10PDT", "mono": true}, {"v": "Revoke"}]}, {"cells": [{"v": "K. Osei", "b": true, "hi": true}, {"v": "Chrome · Windows 11"}, {"v": "2026-07-24 07:40PDT", "mono": true}, {"v": "Revoke"}]}, {"cells": [{"v": "M. Whitfield", "b": true, "hi": true}, {"v": "Edge · Windows 11"}, {"v": "2026-07-24 06:12PDT", "mono": true}, {"v": "Revoke"}]}, {"cells": [{"v": "A. Beckett", "b": true, "hi": true}, {"v": "Safari · macOS 14"}, {"v": "2026-07-23 16:55PDT", "mono": true}, {"v": "Revoke"}]}]}, {"t": "text", "lines": [], "btns": [{"t": "Revoke", "kind": "secondary"}, {"t": "Revoke", "kind": "secondary"}, {"t": "Revoke", "kind": "secondary"}]}], "hint": "5"}, {"t": "panel", "title": "Security policy", "parts": [{"t": "kv", "rows": [{"k": "Multi-factor authentication", "v": "Enabled required before a session is issued", "chip": {"tone": "green", "t": "Enabled"}}, {"k": "Account lockout", "v": "After 3 consecutive failed attempts · reset via Forgot Password with email and phone verification codes"}, {"k": "Session freeze", "v": "Freezing a user (Roles & Users) ends every session listed here for that user instantly"}, {"k": "Multi-organisation login", "v": "Available a carrier may also operate as a shipper on the same identity", "chip": {"tone": "green", "t": "Available"}}]}], "hint": "Auth Services BRD V3"}, {"t": "legend", "items": ["Auth Services BRD V3 §3.1, Driver Login", "Notification Types AU-022"]}], "actions": [{"t": "Revoke all other sessions", "kind": "secondary"}]}, {"key": "settings", "subIdx": 5, "nav": "Settings", "sub": "Company Profile", "frame": "12.6 Settings — Company Profile", "title": "Company Profile", "desc": "Core legal and regulatory identity captured at CO-02, CO-05 and CO-06. This record is locked — it defines the carrier's identity on the platform and cannot be edited from the console. Contact mySHIPR support for corrections.", "blocks": [{"t": "banner", "tone": "crit", "title": "1 required compliance document outstanding", "body": "CO-07 lists eight mandatory carrier documents. Profile completion is blocked at 88% until all are uploaded.", "btns": [{"t": "Go to documents", "kind": "danger"}]}, {"t": "panel", "title": "Legal identity", "parts": [{"t": "kv", "rows": [{"k": "Company name", "v": "Apex Freight LLC"}, {"k": "DBA (Doing Business As)", "v": "Apex Logistics"}, {"k": "Entity type", "v": "Limited Liability Company (LLC)"}, {"k": "EIN / Tax ID", "v": "87-2214508"}, {"k": "Corporation number", "v": "CA-LLC-2011-884210"}, {"k": "Year established", "v": "2011"}, {"k": "Fleet size declared", "v": "8 vehicles · 8 registered"}, {"k": "Country", "v": "United States"}, {"k": "Operating scope", "v": "US · CA · MX"}, {"k": "Company website", "v": "www.apexfreight.example"}]}], "hint": "CO-05 · locked"}, {"t": "panel", "title": "Regulatory identity & authority", "parts": [{"t": "kv", "rows": [{"k": "USDOT number", "v": "3421887 Verified", "chip": {"tone": "green", "t": "Verified"}}, {"k": "MC number", "v": "874120 Verified", "chip": {"tone": "green", "t": "Verified"}}, {"k": "SCAC code", "v": "APXF"}, {"k": "Operating authority", "v": "Active DOC-004 — may haul interstate freight", "chip": {"tone": "green", "t": "Active"}}, {"k": "Insurance status", "v": "", "chip": {"tone": "green", "t": "Active"}}, {"k": "Compliance status", "v": "APPROVED ONB-010 KYC approved"}, {"k": "Account status", "v": "Active CO-05 Pending → CO-06 Active", "chip": {"tone": "green", "t": "Active"}}]}, {"t": "text", "lines": ["An inactive operating authority blocks interstate haulage and halts onboarding (CO-06, DOC-005). This status is visible on every screen through the sidebar badge."]}], "hint": "CO-06 · DOC-001…006"}, {"t": "panel", "title": "Contacts", "parts": [{"t": "list", "items": [{"sev": "info", "unread": false, "title": "Primary — Super Admin", "body": "D. Rao · +1 408 555 0142 · d.rao@apexfreight.example", "code": "", "time": ""}, {"sev": "info", "unread": false, "title": "Compliance", "body": "A. Beckett · +1 408 555 0198 · compliance@apexfreight.example", "code": "", "time": ""}, {"sev": "info", "unread": false, "title": "After hours dispatch", "body": "+1 408 555 0111", "code": "", "time": ""}]}, {"t": "text", "lines": [], "btns": [{"t": "Request contact change", "kind": "secondary"}]}], "hint": "org.contacts.manage"}, {"t": "panel", "title": "Addresses", "parts": [{"t": "list", "items": [{"sev": "info", "unread": false, "title": "Registered office", "body": "1180 Coleman Ave, San Jose, CA 95110, USA", "code": "", "time": ""}, {"sev": "info", "unread": false, "title": "Operations", "body": "2400 Grant Line Rd, Tracy, CA 95377, USA", "code": "", "time": ""}]}], "hint": "org.addresses.manage"}, {"t": "panel", "title": "Primary phone & email", "parts": [{"t": "kv", "rows": [{"k": "Company phone (US · CA · MX)", "v": "+1 408 555 0142"}, {"k": "Company email", "v": "ops@apexfreight.example"}]}], "hint": "CO-05"}, {"t": "legend", "items": ["CO-02 Super Admin signup", "CO-05 Company profile", "CO-06 FMCSA verification", "Auth Services BRD V3 — ORG category", "Notification Types DOC-001…006"]}]}, {"key": "settings", "subIdx": 6, "nav": "Settings", "sub": "Documents", "frame": "12.7 Settings — Documents", "title": "Compliance & Documents", "desc": "The eight carrier documents CO-07 requires, with OCR status, version history and the CO-09 five-tier expiry ladder. Owned by the Compliance Manager.", "blocks": [{"t": "banner", "tone": "crit", "title": "1 required compliance document outstanding", "body": "CO-07 lists eight mandatory carrier documents. Profile completion is blocked at 88% until all are uploaded.", "btns": [{"t": "Go to documents", "kind": "danger"}]}, {"t": "panel", "title": "Carrier documents", "parts": [{"t": "table", "cols": [{"h": "Document type", "w": 281}, {"h": "Status", "w": 123}, {"h": "Expiry", "w": 281}, {"h": "Uploaded", "w": 154}, {"h": "Version", "w": 108}, {"h": "Ocr", "w": 93}, {"h": "Action", "w": 108, "grow": true}], "rows": [{"cells": [{"v": "Insurance Certificate (COI)", "mono": true, "b": true, "hi": true, "sub": "apex-coi-2026.pdf", "subMono": true}, {"chip": {"tone": "amber", "t": "Expiring"}}, {"v": "2026-08-12", "mono": true, "sub": "19 days · tier \"1 month\"", "subMono": true}, {"v": "2026-01-14", "mono": true}, {"v": "v3"}, {"v": "OCR OK"}, {"v": "Replace"}]}, {"cells": [{"v": "MC Permit", "mono": true, "b": true, "hi": true, "sub": "mc-874120.pdf", "subMono": true}, {"chip": {"tone": "green", "t": "Verified"}}, {"v": "2028-11-02", "mono": true}, {"v": "2025-11-02", "mono": true}, {"v": "v1"}, {"v": "OCR OK"}, {"v": "Replace"}]}, {"cells": [{"v": "Cargo Insurance Certificate", "mono": true, "b": true, "hi": true, "sub": "cargo-ins-2026.pdf", "subMono": true}, {"chip": {"tone": "green", "t": "Verified"}}, {"v": "2026-12-31", "mono": true}, {"v": "2026-01-14", "mono": true}, {"v": "v2"}, {"v": "OCR OK"}, {"v": "Replace"}]}, {"cells": [{"v": "MCS-150", "mono": true, "b": true, "hi": true, "sub": "mcs150-2026.pdf", "subMono": true}, {"chip": {"tone": "green", "t": "Verified"}}, {"v": "2028-02-03", "mono": true}, {"v": "2026-02-03", "mono": true}, {"v": "v1"}, {"v": "OCR OK"}, {"v": "Replace"}]}, {"cells": [{"v": "FMCSA Safety Rating", "mono": true, "b": true, "hi": true, "sub": "safety-rating.pdf", "subMono": true}, {"chip": {"tone": "green", "t": "Verified"}}, {"v": "2027-09-19", "mono": true}, {"v": "2025-09-19", "mono": true}, {"v": "v1"}, {"v": "OCR OK"}, {"v": "Replace"}]}, {"cells": [{"v": "Drug & Alcohol Program Policy", "mono": true, "b": true, "hi": true, "sub": "da-policy-v4.pdf", "subMono": true}, {"chip": {"tone": "green", "t": "Verified"}}, {"v": "2027-03-08", "mono": true}, {"v": "2026-03-08", "mono": true}, {"v": "v4"}, {"v": "OCR OK"}, {"v": "Replace"}]}, {"cells": [{"v": "Auto Liability", "mono": true, "b": true, "hi": true, "sub": "auto-liability.pdf", "subMono": true}, {"chip": {"tone": "amber", "t": "Expiring"}}, {"v": "2026-08-12", "mono": true, "sub": "19 days · tier \"1 month\"", "subMono": true}, {"v": "2026-01-14", "mono": true}, {"v": "v2"}, {"v": "OCR OK"}, {"v": "Replace"}]}]}, {"t": "pager", "range": "Showing 1–7 of 8"}, {"t": "text", "lines": [], "btns": [{"t": "Replace", "kind": "secondary"}, {"t": "Replace", "kind": "secondary"}, {"t": "Replace", "kind": "secondary"}]}], "hint": "CO-07 · 8 required types"}, {"t": "panel", "title": "Expiry escalation ladder", "parts": [{"t": "text", "lines": ["1", "1 month", "notify at 30 days before expiry", "2", "3 weeks", "notify at 21 days before expiry", "3", "2 weeks", "notify at 14 days before expiry", "4", "7 days", "notify at 7 days before expiry", "5", "daily after expiry"]}, {"t": "text", "lines": ["Applies to carrier documents, driver CDL and medical certificates, vehicle documents and truck registration expiry. Notification Types DOC-009/010/016/018 and CR-009 are aligned to this ladder."]}], "hint": "CO-09 — adopted as the single schedule"}, {"t": "panel", "title": "Driver-level compliance", "parts": [{"t": "table", "cols": [{"h": "Driver", "w": 209}, {"h": "IDENTITY (CO-19)", "w": 252}, {"h": "DRUG & ALCOHOL (CO-20)", "w": 252}, {"h": "Medical cert", "w": 194}, {"h": "INSURED (CO-18)", "w": 242, "grow": true}], "rows": [{"cells": [{"v": "Marcus Reyes", "mono": true, "b": true, "hi": true, "sub": "0001", "subMono": true}, {"chip": {"tone": "green", "t": "Verified"}}, {"chip": {"tone": "green", "t": "Compliant"}}, {"v": "2027-02-19", "mono": true}, {"chip": {"tone": "grey", "t": "Yes", "plain": true}}]}, {"cells": [{"v": "Priya Nair", "mono": true, "b": true, "hi": true, "sub": "0002", "subMono": true}, {"chip": {"tone": "green", "t": "Verified"}}, {"chip": {"tone": "green", "t": "Compliant"}}, {"v": "2026-12-08", "mono": true}, {"chip": {"tone": "grey", "t": "Yes", "plain": true}}]}, {"cells": [{"v": "Rosa Martinez", "mono": true, "b": true, "hi": true, "sub": "0003", "subMono": true}, {"chip": {"tone": "green", "t": "Verified"}}, {"chip": {"tone": "green", "t": "Compliant"}}, {"v": "2027-05-11", "mono": true}, {"chip": {"tone": "grey", "t": "Yes", "plain": true}}]}, {"cells": [{"v": "Diego Alvarez", "mono": true, "b": true, "hi": true, "sub": "0004", "subMono": true}, {"chip": {"tone": "green", "t": "Verified"}}, {"chip": {"tone": "green", "t": "Compliant"}}, {"v": "2027-01-30", "mono": true}, {"chip": {"tone": "grey", "t": "Yes", "plain": true}}]}, {"cells": [{"v": "Sofia Torres", "mono": true, "b": true, "hi": true, "sub": "0005", "subMono": true}, {"chip": {"tone": "green", "t": "Verified"}}, {"chip": {"tone": "green", "t": "Compliant"}}, {"v": "2026-06-15", "mono": true, "sub": "expired", "subMono": true}, {"chip": {"tone": "grey", "t": "Yes", "plain": true}}]}, {"cells": [{"v": "James Carter", "mono": true, "b": true, "hi": true, "sub": "0006", "subMono": true}, {"chip": {"tone": "green", "t": "Verified"}}, {"chip": {"tone": "green", "t": "Compliant"}}, {"v": "2027-03-22", "mono": true}, {"chip": {"tone": "grey", "t": "No", "plain": true}}], "state": "blocked"}, {"cells": [{"v": "Tyler Brooks", "mono": true, "b": true, "hi": true, "sub": "0007", "subMono": true}, {"chip": {"tone": "green", "t": "Verified"}}, {"chip": {"tone": "green", "t": "Compliant"}}, {"v": "2026-07-30", "mono": true, "sub": "6 days", "subMono": true}, {"chip": {"tone": "grey", "t": "Yes", "plain": true}}]}]}, {"t": "pager", "range": "Showing 1–7 of 8"}], "hint": "CO-19 identity · CO-20 drug & alcohol"}, {"t": "legend", "items": ["CO-04 OCR & virus scan", "CO-07 document upload", "CO-09 expiry monitoring", "CO-19 / CO-20", "Auth Services BRD V3 — COMP", "Notification Types DOC-001…030"]}], "actions": [{"t": "Upload document", "kind": "secondary"}]}, {"key": "settings", "subIdx": 7, "nav": "Settings", "sub": "Contract", "frame": "12.8 Settings — Contract", "title": "Contract", "desc": "Two contract flows are specified in the onboarding workflow. The console shows the one currently in force and flags the target state.", "blocks": [{"t": "banner", "tone": "info", "title": "Interim flow in force — CO-30 mock contract", "body": "CO-30 is an OTP-verified mock contract record. CO-08 (DocuSign e-signature) is the target-state flow and will replace it when the Document Service is integrated. Both are marked Critical priority in the same workbook."}, {"t": "panel", "title": "Current contract", "parts": [{"t": "kv", "rows": [{"k": "Contract reference", "v": "CTR-APX-00142"}, {"k": "Status", "v": "", "chip": {"tone": "green", "t": "Verified & saved"}}, {"k": "Verification method", "v": "Verification code (OTP) confirmed 2026-01-09"}, {"k": "Bound to", "v": "Carrier Company ID CARR-US-00142"}, {"k": "Contract type", "v": "Master carrier agreement (mock record)"}, {"k": "Archived", "v": "No"}]}, {"t": "text", "lines": [], "btns": [{"t": "Update", "kind": "secondary"}, {"t": "Archive", "kind": "secondary"}]}], "hint": "CO-30"}, {"t": "panel", "title": "Target-state flow", "parts": [{"t": "text", "lines": ["Preview contract · Digital signature via DocuSign", "Signature validation · Store signed contract"]}, {"t": "text", "lines": ["Until the Document Service is integrated, contract signature has no legal artefact — the record is a verification receipt, not an executed agreement. Access to trading is gated on this status regardless (CO-08 acceptance criterion)."]}], "hint": "CO-08 — not yet active"}, {"t": "legend", "items": ["CO-08 Digital Contract Signing", "CO-30 Contract Management", "Notification Types DOC-026 / DOC-027"]}]}, {"key": "settings", "subIdx": 8, "nav": "Settings", "sub": "Finance", "frame": "12.9 Settings — Finance", "title": "Financial Setup", "desc": "Stripe Connect onboarding and the ACH payout account required before the carrier can be paid (CO-29). Payment mechanics, commission and settlement timing are governed elsewhere and are not shown here.", "blocks": [{"t": "panel", "title": "Onboarding status", "parts": [{"t": "kv", "rows": [{"k": "Stripe Connect onboarding", "v": "", "chip": {"tone": "green", "t": "Completed"}}, {"k": "KYC / business verification", "v": "Passed ONB-010", "chip": {"tone": "grey", "t": "Passed"}}, {"k": "ACH payout account", "v": "Linked · account ending ••4417"}, {"k": "ACH status", "v": "", "chip": {"tone": "green", "t": "Active"}}, {"k": "Completed at", "v": "2026-01-11 10:24PDT"}, {"k": "W-9 on file", "v": "Received DOC-013", "chip": {"tone": "grey", "t": "Received"}}]}, {"t": "text", "lines": [], "btns": [{"t": "Re-run onboarding", "kind": "secondary"}]}], "hint": "CO-29"}, {"t": "panel", "title": "Payment details", "parts": [{"t": "text", "lines": ["Bank account, routing number and your weekly payout day/week are managed in one place."], "btns": [{"t": "Update payment details", "kind": "secondary"}]}], "hint": "ACH · payout schedule"}, {"t": "legend", "items": ["CO-29 Financial Setup", "Notification Types DOC-012/013"]}]}, {"key": "settings", "subIdx": 9, "nav": "Settings", "sub": "Capacity", "frame": "12.10 Settings — Capacity", "title": "Capacity & Service Profile", "desc": "The four carrier-declared inputs auction eligibility depends on. Unlike the core Company Profile, these are operational values the carrier keeps current — without them the carrier is filtered out before an auction is ever created, and 6A's freeze rule makes that exclusion permanent for that auction.", "blocks": [{"t": "banner", "tone": "info", "title": "These fields decide which loads you are shown", "body": "6A evaluates route match, truck and trailer compatibility, weight and pallet capacity, remaining space, FMCSA compliance and insurance as hard filters, then dead miles, ETA feasibility, break-even cost, commodity compatibility and reefer capability as dynamic filters."}, {"t": "panel", "title": "Operating lanes", "parts": [{"t": "text", "lines": ["95112 · 95376", "95112 · 95814", "95814 · 95112", "95376 · 95202", "94103 · 93901"], "btns": [{"t": "Remove", "kind": "secondary"}, {"t": "Remove", "kind": "secondary"}, {"t": "Remove", "kind": "secondary"}]}], "hint": "6A §3.1 — Route Matching"}, {"t": "panel", "title": "Declared capacity", "parts": [{"t": "kv", "rows": [{"k": "Remaining pallet slots", "v": "14 pallets"}, {"k": "Available trailer dimensions", "v": "48 × 8.2 × 9 ft (L × B × H)"}, {"k": "Cost per mile (break-even)", "v": "$2.35 / mile"}, {"k": "Equipment capability", "v": "Semi Truck (Sleeper Cab), Semi Truck (Day Cab), Dump Truck (Standard), Dump Truck (Articulated) +3 more"}, {"k": "Team-driver capability", "v": "Available 6A §6.3 Long Distance Rule", "chip": {"tone": "green", "t": "Available"}}]}, {"t": "text", "lines": ["Pallet-to-weight validation is blocked pending a decision on weight per pallet: Master Data states 30–40 lbs, the Shipment Execution BRD states 2,000 lbs and cites Master Data as its source."]}], "hint": "6A §5.3 — carrier must provide"}, {"t": "panel", "title": "Commodity capability", "parts": [{"t": "text", "lines": ["Construction Materials", "Metals", "Lumber & Building Supplies", "Agriculture", "Food & Beverage", "Retail Goods", "Automotive", "Industrial Equipment", "Chemicals", "Petroleum", "Refrigerated Goods", "Waste Management", "Oversized Cargo", "General Freight"]}, {"t": "text", "lines": ["Hazardous Materials requires a driver with the H endorsement and a valid TSA security threat assessment (DRV-07), and blocks status advance to In Transit until confirmed (FTL Manual BR-09)."]}], "hint": "Master Data §17 — 15 categories"}, {"t": "note", "tone": "blue", "body": "Hazardous Materials requires a driver with the H endorsement and a valid TSA security threat assessment (DRV-07), and blocks status advance to In Transit until confirmed (FTL Manual BR-09)."}, {"t": "legend", "items": ["6A Carrier Eligibility & Auction Targeting §3.1–§5.3", "Carrier View RR-03", "Master Data §17 Commodity Master", "Notification Types CR-012"]}], "actions": [{"t": "Update profile", "kind": "secondary"}]}];
const OFFSET = 28;

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

  report = 'RESP3 n=' + RESULT.n + ' badTablet=' + RESULT.badT + ' badMobile=' + RESULT.badM + ' secKids=' + RESULT.secKids;
} catch (err) { report = 'FAIL3 ' + (err && err.message ? err.message : String(err)).substring(0, 140); }
try {
  var p3 = null;
  figma.root.children.forEach(function(p){ if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
