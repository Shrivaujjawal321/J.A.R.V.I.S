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
  add(wb, wn); wn.visible = mode === 'desktop';
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
function renderTable(card, t, innerW, mode){
  let widths = colWidths(t.cols, innerW);
  let tblW = widths.reduce((a, b) => a + b, 0);
  /* The console is `.tblwrap{overflow-x:auto}` with `min-width:600px` below 640.
     Desktop always fits. Tablet compresses to fit (table.t{width:100%}).
     Mobile keeps a 600px readable minimum and scrolls horizontally. */
  if (mode && mode !== 'desktop' && tblW > innerW){
    const floor = 56, target = (mode === 'mobile') ? Math.max(600, innerW) : innerW;
    if (tblW > target){
      const k = target / tblW;
      widths = widths.map(w => Math.max(floor, Math.round(w * k)));
      const drift = target - widths.reduce((a, b) => a + b, 0);
      if (drift !== 0){
        let gi = 0;
        widths.forEach((w, i) => { if (w > widths[gi]) gi = i; });
        widths[gi] = Math.max(floor, widths[gi] + drift);
      }
      tblW = widths.reduce((a, b) => a + b, 0);
    }
  }
  const wrap = mkFrame('tblwrap', {dir:'V', gap:0, clip:true});
  add(card, wrap, {hFill:true});
  /* scrollable, exactly as the console is, when the table is wider than the frame */
  if (tblW > innerW) safe(() => { wrap.overflowDirection = 'HORIZONTAL'; });
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
    else if (part.t === 'table') renderTable(card, part, innerW, mode);
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
        if (mode !== 'desktop'){
          const kn = kv.findOne(n => n.type === 'TEXT' && n.name === 'key');
          const holder = kn && kn.parent;
          if (holder && holder !== kv) safe(() => { holder.layoutSizingHorizontal = 'FIXED'; holder.resize(mode === 'mobile' ? 104 : 150, Math.max(1, holder.height)); });
        }
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
    else if (part.t === 'map'){
      /* the console's GPS panel, redrawn from its own projected SVG geometry */
      const VB = part.vb || [560, 380];
      const box = mkFrame('mapwrap', {dir:'N', fill:'#0f1622', radius:10, clip:true});
      add(card, box, {hFill:true});
      const W = innerW - 32, H = Math.round(W * VB[1] / VB[0]);
      safe(() => { box.layoutSizingHorizontal = 'FILL'; box.resize(W, H); });
      const sx = W / VB[0], sy = H / VB[1];
      (part.lines || []).forEach(l => {
        if (l.x1 == null) return;
        const v = figma.createVector();
        box.appendChild(v);
        safe(() => { v.vectorPaths = [{windingRule:'NONE',
          data: 'M ' + (+l.x1 * sx) + ' ' + (+l.y1 * sy) + ' L ' + (+l.x2 * sx) + ' ' + (+l.y2 * sy)}]; });
        safe(() => { v.strokes = solid(l.stroke || '#2f527a'); v.strokeWeight = 1.5; });
        v.name = 'lane';
      });
      (part.nodes || []).forEach(n => {
        if (n.label){
          const t = mkText(n.label, {size:9, lh:12, color:n.fill || '#6b7789', name:'m-label'});
          box.appendChild(t); t.x = n.x * sx; t.y = n.y * sy - 6;
        } else {
          const e = figma.createEllipse();
          const r = Math.max(3, (n.r || 4)) * 2;
          box.appendChild(e); e.resize(r * sx, r * sy);
          e.x = n.x * sx - (r * sx) / 2; e.y = n.y * sy - (r * sy) / 2;
          safe(() => { e.fills = solid(n.fill || '#556781'); });
          if (n.stroke) safe(() => { e.strokes = solid(n.stroke); e.strokeWeight = 1.5; });
          e.name = 'm-node';
        }
      });
      if (part.legend && part.legend.length){
        const lg = mkFrame('maplgd', {dir:'H', gap:14, wrap:true, crossGap:6, pad:[10,16,12,16]});
        add(card, lg, {hFill:true});
        part.legend.forEach(x => {
          const r = mkFrame('lg', {dir:'H', gap:6, align:'CENTER'});
          add(r, mkFrame('sw', {dir:'V', w:8, h:8, radius:4, fill:x.c || C.grey}));
          add(r, mkText(x.t, {size:10.5, lh:14, color:C.ink2}));
          add(lg, r);
        });
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
  const pad = mode === 'desktop' ? 22 : (mode === 'mobile' ? 10 : 14);
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
  const content = mkFrame('Content', {dir:'V', gap:16, pad:[mode === 'mobile' ? 12 : pad, pad, mode === 'desktop' ? 60 : 70, pad]});
  add(main, content, {hFill:true});
  /* page header — .pagehd */
  const ph = mkFrame('pagehd', {dir: mode === 'desktop' ? 'H' : 'V', gap:16, align: mode === 'desktop' ? 'MAX' : 'MIN', just:'SPACE_BETWEEN'});
  add(content, ph, {hFill:true});
  const phl = mkFrame('l', {dir:'V', gap:4});
  add(ph, phl, mode === 'desktop' ? {} : {hFill:true});
  add(phl, mkText(spec.title, {font:F.dispBold, size: mode === 'desktop' ? 26 : 22, lh: mode === 'desktop' ? 31 : 27, ls:0.3}), {hFill:true});
  if (spec.desc) add(phl, mkText(spec.desc, {size:13, lh:19, color:C.ink2}), mode === 'desktop' ? {hFix: Math.min(720, contentWidth(mode) - 260)} : {hFill:true});
  if (spec.actions || spec.lock){
    const acts = mkFrame('acts', {dir:'H', gap:8, wrap:true, crossGap:8, align:'CENTER'});
    add(ph, acts);
    (spec.actions || []).forEach(a => { const b = inst('Button', {kind:a.kind || 'secondary', size:'md', state:'default'}); setBtn(b, a.t, a.kind || 'secondary'); add(acts, b); });
    /* .lock is a read-only badge in the console, not an action — never a Button */
    if (spec.lock){
      const lk = mkFrame('lock', {dir:'H', gap:6, pad:[6,10,6,10], radius:6, fill:C.line2, align:'CENTER', name:'lock'});
      add(lk, svgIcon(I.lock, 13, C.ink3, 1.8));
      add(lk, mkText(spec.lock, {font:F.mono, size:10, lh:14, color:C.ink3}));
      add(acts, lk);
    }
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

await loadFonts();
await adoptComponents(true);
const __pg = await getPage(PAGE.ds);
await figma.setCurrentPageAsync(__pg);
 /* payload-components.js — design-system gap fill (batch: missing + rebuilt components)
 * Runs concatenated AFTER _base.js, inside the caller's async wrapper.
 * Pre-conditions: loadFonts() done, adoptComponents(true) done,
 *                 the current page is already "01 Design System".
 * No regex literals anywhere (Scripter parser limitation).
 * Every padding / radius / colour / size below is read out of
 * mySHIPR_Carrier_Console_v4.html — nothing invented.
 */

 /* ---------------------------------------------------------------- 0. SETUP */
const BOARD_NAME = 'Component library — additions';

const NEW_NAMES = ['Checkbox','Bulk Bar','Skeleton','Wizard/Stepper','Pick Row',
  'Message Bubble','Matrix Cell','Photo Tile','Dropzone','Avatar','Tag','Pill/Lock',
  'Pager Button'];
const REBUILT_NAMES = ['Icon','Toast','Table/Header','Pager','Field','Pulse Cell'];
const ALL_NAMES = NEW_NAMES.concat(REBUILT_NAMES);

let sec = null;
figma.currentPage.children.forEach(function(s){
  if (s.type === 'SECTION' && s.name === 'Components') sec = s;
});
if (!sec) throw new Error('SECTION "Components" not found on the current page.');

 /* --- idempotency: drop last run's board, then every same-named top-level comp --- */
let removed = 0;
sec.children.slice().forEach(function(n){
  if (n.name === BOARD_NAME) { safe(function(){ n.remove(); }); removed++; }
});
figma.currentPage.findAll(function(n){
  return n.type === 'COMPONENT_SET' || n.type === 'COMPONENT';
}).forEach(function(n){
  if (n.type === 'COMPONENT' && n.parent && n.parent.type === 'COMPONENT_SET') return;
  if (ALL_NAMES.indexOf(n.name) < 0) return;
  safe(function(){ n.remove(); });
  removed++;
});

 /* --- board placed under whatever the section already holds --- */
let baseY = 0;
const secBox = sec.absoluteBoundingBox;
sec.children.forEach(function(k){
  const nb = k.absoluteBoundingBox;
  const bottom = (secBox && nb) ? ((nb.y - secBox.y) + nb.height) : (k.y + k.height);
  if (bottom > baseY) baseY = bottom;
});
const board = mkFrame(BOARD_NAME, {dir:'V', gap:44, pad:56, fill:C.canvas, w:1680});
placeInSection(sec, board, 0, baseY + 120);
add(board, mkText('mySHIPR · Carrier Console — Components (additions + rebuilds)',
  {font:F.dispBold, size:34, lh:38, ls:0.3}), {hFill:true});
add(board, mkText('Selection, bulk, loading, wizard, messaging, evidence and RBAC primitives that the first component batch did not cover — plus six sets rebuilt against the console CSS.',
  {size:13, lh:19, color:C.ink2}), {hFill:true});

function sect(title, sub){
  const s = mkFrame(title, {dir:'V', gap:14});
  add(board, s, {hFill:true});
  add(s, mkText(title, {font:F.dispBold, size:20, lh:24}), {hFill:true});
  if (sub) add(s, mkText(sub, {size:12, lh:17, color:C.ink2}), {hFill:true});
  const holder = mkFrame('items', {dir:'H', gap:36, wrap:true, crossGap:36, align:'MIN'});
  add(s, holder, {hFill:true});
  return holder;
}

 /* gradient paints — the console uses linear-gradient() in .photo and .skel */
function gradFill(stops, tf){
  const gs = stops.map(function(s){
    const c = rgb(s[1]);
    return { position: s[0], color: {r:c.r, g:c.g, b:c.b, a:1} };
  });
  return [{ type:'GRADIENT_LINEAR', gradientTransform: tf || [[1,0,0],[0,1,0]], gradientStops: gs }];
}

 /* glyphs present in the console sprite but absent from the shared I map */
const XI = {
  x:'<path d="M18 6 6 18M6 6l12 12"/>',
  pin:'<path d="M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11Z"/><circle cx="12" cy="10" r="2.6"/>',
  cam:'<path d="M3 8h3l2-3h8l2 3h3v12H3z"/><circle cx="12" cy="13" r="3.6"/>',
  shield:'<path d="M12 3l8 3v6c0 5-3.4 8.3-8 9-4.6-.7-8-4-8-9V6Z"/><path d="M9 12l2 2 4-4"/>',
  bldg:'<path d="M4 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16"/><path d="M14 9h4a2 2 0 0 1 2 2v10M3 21h18M8 7h2M8 11h2M8 15h2"/>'
};

 /* =========================================================== 1. REBUILT SETS */
const hRe = sect('Rebuilt — Icon, Toast, Table/Header, Pager, Field, Pulse Cell',
  'Same names, same slot names, corrected against the console CSS. Icon now covers the whole sprite and settings finally points at the gear.');

 /* ---------- Icon: every sprite key + the 12 nav aliases ---------- */
const SPRITE = [];
Object.keys(I).forEach(function(k){ SPRITE.push([k, I[k]]); });
Object.keys(XI).forEach(function(k){ SPRITE.push([k, XI[k]]); });
const NAV_ALIAS = [['dashboard',I.chart],['fleet',I.truck],['drivers',I.user],['loads',I.box],
  ['trips',I.route],['ops',I.msg],['rr',I.gavel],['yards',I.yard],['alerts',I.bell],
  ['reports',I.chart],['earnings',I.coin],['settings',I.gear]];
const ICONS = NAV_ALIAS.concat(SPRITE);
const ICON_MAP = {};
ICONS.forEach(function(p){ if (!ICON_MAP[p[0]]) ICON_MAP[p[0]] = p[1]; });
const ICON_NAMES = [];
ICONS.forEach(function(p){ if (ICON_NAMES.indexOf(p[0]) < 0) ICON_NAMES.push(p[0]); });

makeSet('Icon', [['name', ICON_NAMES]], function(cmb){
  const f = mkFrame('Icon', {dir:'N', w:17, h:17});
  const g = svgIcon(ICON_MAP[cmb.name] || I.chart, 17, C.white, 1.7);
  f.appendChild(g); g.x = 0; g.y = 0;
  return toComp(f);
}, hRe);

 /* ---------- Toast — .toast / .toast.err ---------- */
makeSet('Toast', [['tone',['success','error']]], function(cmb){
  const err = cmb.tone === 'error';
  const f = mkFrame('Toast', {dir:'H', gap:9, align:'CENTER', pad:[11,18,11,18], radius:9,
    fill: err ? C.redInk : C.chrome3});
  const g = svgIcon(err ? I.warn : I.check, 16, err ? '#ffdada' : '#7fe6ac', 2);
  g.name = 'icon'; add(f, g);
  add(f, mkText(err ? 'Upload rejected — ERR-GEN-004 · HTTP 415'
                    : 'Detention raised as billable — DET-0041',
    {size:13, lh:18, color:C.white, name:'label'}));
  safe(function(){ f.effects = [{type:'DROP_SHADOW', color:{r:0,g:0,b:0,a:0.28},
    offset:{x:0,y:10}, radius:30, spread:0, visible:true, blendMode:'NORMAL'}]; });
  return toComp(f);
}, hRe);

 /* ---------- Table/Header — th.sortable + .sarr ---------- */
const COLW2 = [150,150,150,120,120,120,120,120,120,120];
makeSet('Table/Header', [['sort',['none','asc','desc']]], function(cmb){
  const arrow = cmb.sort === 'asc' ? '▲' : (cmb.sort === 'desc' ? '▼' : '⇅');
  const f = mkFrame('Table/Header', {dir:'H', gap:0, fill:C.panel2, stroke:C.line, sides:[0,0,1,0], w:1132});
  for (let i = 0; i < 10; i++){
    const cell = mkFrame('h' + i, {dir:'H', gap:4, pad:[10,14,10,14], align:'CENTER'});
    add(f, cell, {hFix: COLW2[i]});
    add(cell, mkText('COLUMN', {font:F.semi, size:10.5, lh:14, ls:0.74, color:C.ink3,
      case:'UPPER', name:'label'}), {hFill:true});
    const sa = mkText(arrow, {size:10, lh:14, color: cmb.sort === 'none' ? C.ink3 : C.ink, name:'sarr'});
    sa.opacity = cmb.sort === 'none' ? 0.45 : 0.85;
    add(cell, sa);
  }
  return toComp(f);
}, hRe);

 /* ---------- Pager Button (.pgb / .pgb.on / .pgb:disabled) ---------- */
makeSet('Pager Button', [['state',['default','current','disabled']]], function(cmb){
  const on = cmb.state === 'current';
  const f = mkFrame('Pager Button', {dir:'H', w:28, h:26, align:'CENTER', just:'CENTER', radius:5,
    fill: on ? C.brand : C.white, stroke: on ? C.brand : C.line});
  add(f, mkText('1', {font: on ? F.monoSemi : F.mono, size:11, lh:14,
    color: on ? C.white : C.ink2, name:'label'}));
  if (cmb.state === 'disabled') f.opacity = 0.4;
  return toComp(f);
}, hRe);

 /* ---------- Pager — now assembled from Pager Button ---------- */
makeComp('Pager', function(){
  const f = mkFrame('Pager', {dir:'H', gap:10, align:'CENTER', just:'SPACE_BETWEEN',
    pad:[10,16,10,16], fill:C.panel, stroke:C.line, sides:[1,0,0,0], w:1132});
  add(f, mkText('Showing 1–6 of 8', {size:12, lh:16, color:C.ink2, name:'range'}));
  const pgs = mkFrame('pgs', {dir:'H', gap:4, align:'CENTER'});
  add(f, pgs);
  [['‹','disabled','prev'],['1','current','p1'],['2','default','p2'],['›','default','next']]
  .forEach(function(b){
    const bi = inst('Pager Button', {state: b[1]});
    bi.name = b[2];
    const lbl = bi.findOne(function(n){ return n.type === 'TEXT' && n.name === 'label'; });
    if (lbl) lbl.characters = b[0];
    add(pgs, bi);
  });
  return toComp(f);
}, hRe);

 /* ---------- Field — required / help / disabled / textarea ---------- */
makeSet('Field',
  [['state',['default','focus','error','disabled']],
   ['type',['input','select','textarea']],
   ['required',['true','false']],
   ['help',['true','false']]], function(cmb){
  const err = cmb.state === 'error', foc = cmb.state === 'focus', dis = cmb.state === 'disabled';
  const ta  = cmb.type === 'textarea';
  const f = mkFrame('Field', {dir:'V', gap:4, w:300});
  /* label row — .field label + .field label .req */
  const lr = mkFrame('label-row', {dir:'H', gap:2, align:'CENTER'});
  add(f, lr, {hFill:true});
  add(lr, mkText('LICENCE PLATE', {font:F.semi, size:11, lh:15, ls:0.77, color:C.ink3,
    case:'UPPER', name:'label'}));
  const req = mkText('*', {font:F.semi, size:11, lh:15, color:C.red, name:'req'});
  add(lr, req); req.visible = cmb.required === 'true';
  /* control — .field input / select / textarea */
  const ctl = mkFrame('control', {dir:'H', gap:8, align: ta ? 'MIN' : 'CENTER',
    pad:[8,11,8,11], radius:7,
    fill: err ? '#fffafa' : (dis ? C.panel2 : C.white),
    stroke: err ? C.red : (foc ? C.brand : C.line)});
  add(f, ctl, {hFill:true});
  if (ta) safe(function(){ ctl.layoutSizingVertical = 'FIXED'; ctl.resize(300, 72); });
  add(ctl, mkText(ta ? 'Notes for the driver — visible on the tablet at pickup.' : '8ZTK492',
    {size:12.5, lh:18, color: (cmb.state === 'default' || dis) ? C.ink3 : C.ink, name:'value'}), {hFill:true});
  const car = svgIcon(I.caretDown, 13, C.ink3, 2); car.name = 'caret';
  add(ctl, car); car.visible = cmb.type === 'select';
  if (foc) safe(function(){ ctl.effects = [{type:'DROP_SHADOW',
    color:{r:0.08,g:0.48,b:0.29,a:0.18}, offset:{x:0,y:0}, radius:0, spread:3,
    visible:true, blendMode:'NORMAL'}]; });
  /* help — .field .hlp */
  const hlp = mkText('Plate as printed on the registration — CO-10.',
    {size:11, lh:15, color:C.ink3, name:'help'});
  add(f, hlp, {hFill:true}); hlp.visible = cmb.help === 'true';
  /* error — .field .emsg */
  const msg = mkFrame('emsg', {dir:'H', gap:5, align:'CENTER'});
  add(f, msg);
  add(msg, svgIcon(I.warn, 12, C.redInk, 2));
  add(msg, mkText('Required fields are missing — ERR-GEN-005',
    {size:11, lh:15, color:C.redInk, name:'error'}));
  msg.visible = err;
  if (dis) f.opacity = 0.55;
  return toComp(f);
}, hRe);

 /* ---------- Pulse Cell — .pcell, dot tone is a property now ---------- */
makeSet('Pulse Cell', [['tone',['green','amber','red','blue','grey']]], function(cmb){
  const f = mkFrame('Pulse Cell', {dir:'H', gap:10, align:'CENTER', pad:[12,15,12,15], fill:C.panel, w:222});
  const dot = mkFrame('dot', {dir:'V', w:9, h:9, radius:5, fill: TONE[cmb.tone].solid});
  add(f, dot);
  const b = mkFrame('b', {dir:'V', gap:2});
  add(f, b, {hFill:true});
  add(b, mkText('3', {font:F.dispBold, size:20, lh:20, name:'value'}));
  add(b, mkText('TRUCKS AVAILABLE', {size:10, lh:13, ls:0.7, color:C.ink2, case:'UPPER', name:'label'}), {hFill:true});
  return toComp(f);
}, hRe);

 /* ================================================ 2. SELECTION & BULK ACTIONS */
const hSel = sect('Selection & bulk actions',
  '.ck .box is 20×20 on a 6px radius with a 1.5px rule · .bulkbar is the dark chrome-3 strip that appears the moment a row is ticked.');

makeSet('Checkbox', [['state',['off','on','indeterminate','disabled']]], function(cmb){
  const on = cmb.state === 'on', ind = cmb.state === 'indeterminate', dis = cmb.state === 'disabled';
  const filled = on || ind;
  const f = mkFrame('Checkbox', {dir:'V', w:20, h:20, radius:6,
    fill: filled ? C.green : (dis ? C.panel2 : C.white),
    stroke: filled ? C.green : C.line, sides:[1.5,1.5,1.5,1.5],
    align:'CENTER', just:'CENTER'});
  const tick = svgIcon(I.check, 13, C.white, 2.4); tick.name = 'tick';
  add(f, tick); tick.visible = on;
  const dash = mkFrame('dash', {dir:'V', w:10, h:2, radius:1, fill:C.white});
  add(f, dash); dash.visible = ind;
  if (dis) f.opacity = 0.45;
  return toComp(f);
}, hSel);

makeComp('Bulk Bar', function(){
  const f = mkFrame('Bulk Bar', {dir:'H', gap:12, align:'CENTER', pad:[9,16,9,16],
    fill:C.chrome3, w:1132});
  add(f, mkText('3', {font:F.dispBold, size:15, lh:20, color:C.white, name:'count'}));
  add(f, mkText('loads selected', {size:12.5, lh:17, color:C.white, name:'noun'}));
  add(f, mkFrame('spacer', {dir:'H', h:1}), {hFill:true});
  const acts = mkFrame('acts', {dir:'H', gap:8, align:'CENTER'});
  add(f, acts);
  const a1 = inst('Button', {kind:'secondary', size:'sm', state:'default'});
  a1.name = 'btn';  setBtn(a1, 'Assign driver', 'secondary'); add(acts, a1);
  const a2 = inst('Button', {kind:'secondary', size:'sm', state:'default'});
  a2.name = 'btn2'; setBtn(a2, 'Export selected', 'secondary'); add(acts, a2);
  const a3 = inst('Button', {kind:'secondary', size:'sm', state:'default'});
  a3.name = 'clear'; setBtn(a3, 'Clear', 'secondary'); add(acts, a3);
  return toComp(f);
}, hSel);

 /* ======================================================= 3. LOADING & WIZARD */
const hLoad = sect('Loading & wizard',
  '.skel is the 12px shimmer bar (drawn at its mid-sweep) · .steps / .step carry a 3px bottom rule that recolours per state.');

makeSet('Skeleton', [['kind',['line','block']]], function(cmb){
  const line = cmb.kind === 'line';
  const f = mkFrame('Skeleton', {dir:'V', radius:5, w: line ? 240 : 240, h: line ? 12 : 92});
  safe(function(){ f.fills = gradFill([[0.25,'#eef1f4'],[0.37,'#f7f9fb'],[0.63,'#eef1f4']]); });
  return toComp(f);
}, hLoad);

makeSet('Wizard/Stepper', [['state',['upcoming','on','done']]], function(cmb){
  const done = cmb.state === 'done', on = cmb.state === 'on';
  const edge = done ? C.green : (on ? C.brand : C.line);
  const f = mkFrame('Wizard/Stepper', {dir:'V', gap:1, pad:[9,12,9,12], w:180,
    stroke:edge, sides:[0,0,3,0]});
  add(f, mkText('STEP 1 OF 4', {font:F.mono, size:10, lh:14, color:C.ink3, name:'index'}), {hFill:true});
  add(f, mkText('Choose truck', {font:F.dispSemi, size:14, lh:19,
    color: done ? C.greenInk : (on ? C.ink : C.ink3), name:'label'}), {hFill:true});
  return toComp(f);
}, hLoad);

makeSet('Pick Row', [['state',['default','selected','blocked']]], function(cmb){
  const selr = cmb.state === 'selected', no = cmb.state === 'blocked';
  const f = mkFrame('Pick Row', {dir:'H', gap:12, align:'CENTER', pad:[12,14,12,14], radius:7,
    fill: selr ? '#f2fbf6' : (no ? C.panel2 : C.white),
    stroke: selr ? C.brand : C.line, w:420});
  const pk = mkFrame('pk', {dir:'V', w:38, h:38, radius:9, fill:C.line2, align:'CENTER', just:'CENTER'});
  add(pk, mkText('T4', {font:F.dispBold, size:13, lh:17, color:C.ink2, name:'initials'}));
  add(f, pk);
  const pb = mkFrame('pb', {dir:'V', gap:2});
  add(f, pb, {hFill:true});
  add(pb, mkText('TRK-CARR-US-00142-004', {font:F.semi, size:13, lh:18, name:'title'}), {hFill:true});
  add(pb, mkText('Mack Granite 64FR · Tracy Staging · 8ZTK492',
    {size:11.5, lh:16, color:C.ink2, name:'sub'}), {hFill:true});
  const pr = mkFrame('pr', {dir:'H', pad:[2,7,2,7], radius:20, fill:C.redBg, align:'CENTER'});
  add(pr, mkText('DVIR defect open', {font:F.mono, size:10.5, lh:15, color:C.redInk, name:'reason'}));
  add(f, pr); pr.visible = no;
  if (no) f.opacity = 0.62;
  return toComp(f);
}, hLoad);

 /* ================================================ 4. MESSAGING & POD EVIDENCE */
const hMsg2 = sect('Messaging & POD evidence',
  'msgBubble() — 32px initials avatar, tinted bubble (green-bg when it is us, panel-2 when it is the driver), then who · time · receipt. .photo is the 4:3 POD tile with a 78%-black caption strip.');

makeSet('Message Bubble', [['author',['me','driver']], ['kind',['text','voice','doc','location']]],
function(cmb){
  const mine = cmb.author === 'me';
  const f = mkFrame('Message Bubble', {dir:'H', gap:10, align:'MIN', w:420});
  const av = mkFrame('avatar', {dir:'V', w:32, h:32, radius:9, fill:C.line2, align:'CENTER', just:'CENTER'});
  add(av, mkText(mine ? 'YO' : 'TB', {font:F.dispBold, size:11, lh:15, color:C.ink2, name:'initials'}));
  const col = mkFrame('col', {dir:'V', gap:3});
  const bub = mkFrame('bubble', {dir:'V', gap:0, pad:[9,12,9,12], radius:10,
    fill: mine ? C.greenBg : C.panel2, stroke:C.line});
  if (cmb.kind === 'text'){
    add(bub, mkText('Running about 20 minutes behind at the Tracy gate — trailer is loaded.',
      {size:12.5, lh:18, name:'text'}), {hFill:true});
  } else {
    const row = mkFrame('row', {dir:'H', gap:9, align:'CENTER'});
    add(bub, row, {hFill:true});
    const glyph = cmb.kind === 'voice' ? I.msg : (cmb.kind === 'doc' ? I.doc : XI.pin);
    const g = svgIcon(glyph, 16, C.ink2, 1.8); g.name = 'icon'; add(row, g);
    const tb = mkFrame('tb', {dir:'V', gap:2});
    add(row, tb, {hFill:true});
    const title = cmb.kind === 'voice' ? 'Voice note · 0:08'
                : (cmb.kind === 'doc' ? 'dispatch-instructions.pdf' : 'Live location');
    add(tb, mkText(title, {font:F.semi, size:12, lh:16, name:'title'}), {hFill:true});
    const subTxt = cmb.kind === 'voice' ? '“Recorded from the console — playback available on the driver tablet.”'
                 : (cmb.kind === 'doc' ? '96 KB · DSP-004 document sharing' : '37.6390, -120.9969');
    add(tb, mkText(subTxt, {font: cmb.kind === 'location' ? F.mono : F.body,
      size:11, lh:15, color:C.ink3, name:'sub'}), {hFill:true});
    if (cmb.kind !== 'location'){
      const act = inst('Button', {kind:'secondary', size:'sm', state:'default'});
      act.name = 'action';
      setBtn(act, cmb.kind === 'voice' ? 'Play' : 'Open', 'secondary');
      add(row, act);
    }
  }
  add(col, bub, {hFill:true});
  add(col, mkText((mine ? 'You' : 'Tyler Brooks') + ' · 10:24 · ' + (mine ? 'read' : 'delivered'),
    {size:11, lh:15, color:C.ink3, name:'meta'}), {hFill:true});
  if (mine){ add(f, col, {hFill:true}); add(f, av); }
  else { add(f, av); add(f, col, {hFill:true}); }
  return toComp(f);
}, hMsg2);

makeComp('Photo Tile', function(){
  const f = mkFrame('Photo Tile', {dir:'V', gap:0, w:160, h:120, radius:7, stroke:C.line, clip:true});
  safe(function(){ f.fills = gradFill([[0,'#e6ebf1'],[1,'#d5dde6']], [[0.7,0.7,0],[-0.7,0.7,0.5]]); });
  const thumb = mkFrame('thumb', {dir:'V', align:'CENTER', just:'CENTER'});
  add(f, thumb, {hFill:true, vFill:true});
  add(thumb, svgIcon(XI.cam, 26, '#9aa5b6', 1.8));
  const cap = mkFrame('pl2', {dir:'H', pad:[4,6,4,6], just:'CENTER', align:'CENTER'});
  safe(function(){ cap.fills = solid('#0f141d', 0.78); });
  add(f, cap, {hFill:true});
  add(cap, mkText('Driver selfie · POD-006', {font:F.mono, size:9.5, lh:13,
    color:C.white, align:'CENTER', name:'caption'}), {hFill:true});
  return toComp(f);
}, hMsg2);

makeComp('Dropzone', function(){
  const f = mkFrame('Dropzone', {dir:'V', gap:3, pad:22, radius:10, fill:C.panel2,
    stroke:C.line, sides:[1.5,1.5,1.5,1.5], align:'CENTER', w:420});
  safe(function(){ f.dashPattern = [5,4]; });
  const hd = mkFrame('hd', {dir:'H', gap:7, align:'CENTER'});
  add(f, hd);
  add(hd, svgIcon(I.up, 22, C.ink2, 1.8));
  add(hd, mkText('Choose a CSV or XLSX file', {font:F.dispSemi, size:14, lh:19, name:'title'}));
  add(f, mkText('Any other format is rejected with HTTP 415 — unsupported file type.',
    {size:11.5, lh:16, color:C.ink2, align:'CENTER', name:'sub'}), {hFill:true});
  return toComp(f);
}, hMsg2);

 /* ============================================================ 5. PRIMITIVES */
const hPrim = sect('Primitives — matrix cell, avatar, tag, lock',
  '.matrix td.y / td.v / td.n is the RBAC grid cell · .who .av is 32px round, .pick .pk is 38px on a 9px radius · .tag2 is the 9.5px mono chip · .lock is the read-only badge.');

makeSet('Matrix Cell', [['value',['create','view','none']]], function(cmb){
  const f = mkFrame('Matrix Cell', {dir:'H', gap:0, pad:[11,14,11,14], align:'CENTER',
    just:'CENTER', fill:C.panel, stroke:C.line2, sides:[0,0,1,0], w:170});
  if (cmb.value === 'none'){
    add(f, mkText('—', {size:11.5, lh:16, color:C.line, align:'CENTER', name:'label'}));
  } else {
    const tone = cmb.value === 'create' ? 'green' : 'blue';
    const ch = inst('Chip/Status', {tone: tone, style:'plain'});
    ch.name = 'chip';
    setChip(ch, tone, cmb.value === 'create' ? 'CREATE / VIEW / UPDATE' : 'ONLY VIEW', true);
    const tx = ch.children && ch.children[1];
    if (tx) safe(function(){ tx.fontSize = 9.5; });
    add(f, ch);
  }
  return toComp(f);
}, hPrim);

makeSet('Avatar', [['size',['sm','md']]], function(cmb){
  const sm = cmb.size === 'sm';
  const f = mkFrame('Avatar', {dir:'V', w: sm ? 32 : 38, h: sm ? 32 : 38,
    radius: sm ? 16 : 9, fill: sm ? '#22304a' : C.line2, align:'CENTER', just:'CENTER'});
  add(f, mkText(sm ? 'DR' : 'T4', {font: sm ? F.dispSemi : F.dispBold, size:13, lh:17,
    color: sm ? '#cdd7e6' : C.ink2, name:'initials'}));
  return toComp(f);
}, hPrim);

makeSet('Tag', [['tone',['neutral','green','red','amber']]], function(cmb){
  const bg = cmb.tone === 'green' ? C.greenBg : (cmb.tone === 'red' ? C.redBg
           : (cmb.tone === 'amber' ? C.amberBg : C.line2));
  const fg = cmb.tone === 'green' ? C.greenInk : (cmb.tone === 'red' ? C.redInk
           : (cmb.tone === 'amber' ? C.amberInk : C.ink2));
  const f = mkFrame('Tag', {dir:'H', pad:[2,6,2,6], radius:4, fill:bg, align:'CENTER'});
  add(f, mkText('Fleet management', {font:F.mono, size:9.5, lh:13, ls:0.57, color:fg,
    case:'UPPER', name:'label'}));
  return toComp(f);
}, hPrim);

makeComp('Pill/Lock', function(){
  const f = mkFrame('Pill/Lock', {dir:'H', gap:5, pad:[3,7,3,7], radius:5, fill:C.line2, align:'CENTER'});
  add(f, svgIcon(I.lock, 11, C.ink3, 1.8));
  add(f, mkText('users.invite required', {font:F.mono, size:10, lh:14, color:C.ink3, name:'label'}));
  return toComp(f);
}, hPrim);

 /* ============================================================ 6. WRAP-UP */
fitSection(sec);

 /* Note already carries tone = amber | red | blue — verified, left untouched */
let noteOk = false, noteTones = '';
const noteSet = COMP['Note'];
if (noteSet && noteSet.type === 'COMPONENT_SET'){
  noteTones = noteSet.children.map(function(c){ return c.name; }).join(' | ');
  noteOk = noteTones.indexOf('tone=amber') >= 0 && noteTones.indexOf('tone=red') >= 0
        && noteTones.indexOf('tone=blue') >= 0;
}

let variants = 0;
NEW_NAMES.concat(REBUILT_NAMES).forEach(function(n){
  const c = COMP[n];
  if (c && c.type === 'COMPONENT_SET') variants += c.children.length;
  else if (c) variants += 1;
});

RESULT = {
  created: NEW_NAMES.length,
  rebuilt: REBUILT_NAMES.length,
  removedBeforeBuild: removed,
  variants: variants,
  iconVariants: ICON_NAMES.length,
  names: NEW_NAMES.concat(REBUILT_NAMES),
  createdNames: NEW_NAMES,
  rebuiltNames: REBUILT_NAMES,
  noteAlreadyToned: noteOk,
  noteVariants: noteTones,
  board: BOARD_NAME,
  section: sectionReport(sec)
};

  report = 'COMP ' + JSON.stringify(RESULT).substring(0, 150);
} catch (err) { report = 'FAIL-COMP ' + (err && err.message ? err.message : String(err)).substring(0, 140); }
try {
  var p3 = null;
  figma.root.children.forEach(function(p){ if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
