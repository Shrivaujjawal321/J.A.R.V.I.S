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
const __pg = await getPage(PAGE.screens);
await figma.setCurrentPageAsync(__pg);
/* mySHIPR Carrier Console — payload-overlays.js
 * Builds the OVERLAY layer the file was missing: the OPS-03…06 assignment wizard,
 * the record drawers, the create forms, the bulk-upload validation report and the
 * five ERR-GEN states. Concatenated AFTER _base.js; runs after loadFonts() and
 * adoptComponents(true), with figma.currentPage already on "02 Screens".
 * Every string, field label and record value below is lifted from
 * mySHIPR_Carrier_Console_v4 (2).html — nothing here is invented.
 * NOTE: no regular-expression literals anywhere (Scripter's parser rejects them).
 */

/* ============================ small helpers ============================ */
/* inst() throws when a component has not been adopted yet; safe() turns that
   into null so a missing Wizard/Stepper or Pick Row cannot abort the run. */
function tryInst(name, props){ return safe(function(){ return inst(name, props); }); }

const SHEET_W = 760;          /* .drawer .sheet {width:min(760px,100%)} */
const SHEET_INNER = 720;      /* .dbody padding 20 left + right         */
const PAGE_INNER = DESK_W - 44;
/* .drawer .scrim is rgba(11,16,23,.5) over the --canvas page beneath it,
   which resolves to this flat value — Figma frames get no live backdrop. */
const SCRIM = '#7c8188';

function chipNode(tone, label, plain){
  const c = tryInst('Chip/Status', {tone: tone, style: plain ? 'plain' : 'solid-bg'});
  if (!c) return mkText(label, {size:11, lh:15, color:(TONE[tone] || TONE.grey).fg});
  setChip(c, tone, label, plain);
  return c;
}
function btnNode(label, kind){
  const b = tryInst('Button', {kind: kind === 'primary' ? 'primary' : 'secondary', size:'md', state:'default'});
  if (!b) return mkText(label, {font:F.semi, size:12.5, lh:17});
  setBtn(b, label, kind || 'secondary');
  return b;
}
function h4(parent, title, sub){
  add(parent, mkText(title, {font:F.dispSemi, size:16, lh:21}), {hFill:true});
  if (sub) add(parent, mkText(sub, {size:11.5, lh:16, color:C.ink2}), {hFill:true});
}

/* ---- .drawer .sheet ------------------------------------------------- */
function mkSheet(title, sub){
  const sh = mkFrame('sheet', {dir:'V', gap:0, fill:C.canvas, w:SHEET_W, clip:true});
  const hd = mkFrame('dhd', {dir:'H', gap:14, pad:[16,20,16,20], fill:C.chrome, align:'MIN'});
  add(sh, hd, {hFill:true});
  const hb = mkFrame('hb', {dir:'V', gap:3});
  add(hd, hb, {hFill:true});
  add(hb, mkText(title, {font:F.dispBold, size:21, lh:26, ls:0.3, color:C.white, name:'title'}), {hFill:true});
  add(hb, mkText(sub, {size:12, lh:16, color:C.inkInv2, name:'sub'}), {hFill:true});
  add(hd, mkText('×', {size:22, lh:24, color:C.inkInv2, name:'close'}));
  const body = mkFrame('dbody', {dir:'V', gap:16, pad:[18,20,40,20]});
  add(sh, body, {hFill:true});
  return {sheet: sh, body: body};
}
function mkFoot(sh, btns){
  const ft = mkFrame('dfoot', {dir:'H', gap:9, just:'MAX', align:'CENTER',
    pad:[13,20,13,20], fill:C.panel, stroke:C.line, sides:[1,0,0,0]});
  add(sh, ft, {hFill:true});
  btns.forEach(function(b){ add(ft, btnNode(b.t, b.kind)); });
  return ft;
}
/* wrap a sheet in the dimmed 1440 backdrop the console shows behind it */
function mkOverlay(name, sh){
  const h = Math.max(900, Math.ceil(sh.height));
  const f = mkFrame(name, {dir:'N', w:DESK_W, h:h, fill:SCRIM, clip:true});
  f.appendChild(sh);
  sh.x = DESK_W - SHEET_W; sh.y = 0;
  const bodyNode = sh.findOne(function(n){ return n.type === 'FRAME' && n.name === 'dbody'; });
  safe(function(){ sh.primaryAxisSizingMode = 'FIXED'; sh.resize(SHEET_W, h); });
  if (bodyNode) safe(function(){ bodyNode.layoutSizingVertical = 'FILL'; });
  return f;
}
/* a plain 1440 page frame for the states the console renders inline */
function mkPageFrame(name, title, desc){
  const f = mkFrame(name, {dir:'V', gap:16, pad:[22,22,60,22], fill:C.canvas, w:DESK_W});
  const hd = mkFrame('pagehd', {dir:'V', gap:4});
  add(f, hd, {hFill:true});
  add(hd, mkText(title, {font:F.dispBold, size:26, lh:31, ls:0.3}), {hFill:true});
  if (desc) add(hd, mkText(desc, {size:13, lh:19, color:C.ink2}), {hFix:720});
  return f;
}
function dpanel(parent, spec){ return renderPanel(parent, spec, SHEET_INNER, 'desktop'); }
function ppanel(parent, spec){ return renderPanel(parent, spec, PAGE_INNER, 'desktop'); }
function padBox(card, gap){
  const b = mkFrame('body', {dir:'V', gap: gap == null ? 13 : gap, pad:[14,16,16,16]});
  add(card, b, {hFill:true});
  return b;
}

/* ---- .field / .fgrid ------------------------------------------------- */
function fieldCell(parent, o){
  const w = mkFrame('field', {dir:'V', gap:3});
  add(parent, w, {hFill:true});
  const blank = (o.v == null || o.v === '');
  const fi = tryInst('Field', {state: o.err ? 'error' : 'default', type: o.select ? 'select' : 'input'});
  if (fi){
    add(w, fi, {hFill:true});
    setText(fi, 'label', String(o.label).toUpperCase() + (o.req ? '  *' : ''));
    const vt = setText(fi, 'value', blank ? (o.ph || '') : o.v);
    if (vt) safe(function(){ vt.fills = solid(blank ? C.ink3 : C.ink); });
    if (o.err) setText(fi, 'error', o.err);
    const car = fi.findOne(function(n){ return n.name === 'caret'; });
    if (car) car.visible = !!o.select;
  } else {
    add(w, mkText(String(o.label).toUpperCase() + (o.req ? '  *' : ''),
      {font:F.semi, size:11, lh:15, ls:0.77, color:C.ink3, case:'UPPER', name:'label'}), {hFill:true});
    const ctl = mkFrame('control', {dir:'H', gap:8, align:'CENTER', pad:[8,11,8,11], radius:7,
      fill: o.err ? '#fffafa' : C.white, stroke: o.err ? C.red : C.line});
    add(w, ctl, {hFill:true});
    add(ctl, mkText(blank ? (o.ph || '') : o.v,
      {size:12.5, lh:18, color: blank ? C.ink3 : C.ink, name:'value'}), {hFill:true});
    if (o.select) add(ctl, svgIcon(I.caretDown, 13, C.ink3, 2));
    if (o.err){
      const em2 = mkFrame('emsg', {dir:'H', gap:5, align:'CENTER'});
      add(w, em2, {hFill:true});
      add(em2, svgIcon(I.warn, 12, C.redInk, 2));
      add(em2, mkText(o.err, {size:11, lh:15, color:C.redInk, name:'error'}), {hFill:true});
    }
  }
  if (o.hlp) add(w, mkText(o.hlp, {size:11, lh:15, color:C.ink3, name:'hlp'}), {hFill:true});
  return w;
}
function fgrid(parent){
  const r = mkFrame('fgrid', {dir:'H', gap:14, align:'MIN'});
  add(parent, r, {hFill:true});
  return r;
}

/* ---- .steps / .step -------------------------------------------------- */
const WSTEPS = [['Truck','OPS-03'], ['Trailer','OPS-04'], ['Driver','OPS-05'], ['Confirm','OPS-06']];
function stepper(parent, active){
  const si = tryInst('Wizard/Stepper', {step: String(active + 1)});
  if (si){
    let hits = 0;
    WSTEPS.forEach(function(s, i){
      if (setText(si, 'step-' + (i + 1), s[0])) hits++;
      if (setText(si, 'label-' + (i + 1), s[0])) hits++;
      if (setText(si, 'code-' + (i + 1), s[1])) hits++;
    });
    if (setText(si, 'label', WSTEPS[active][0])) hits++;
    if (setText(si, 'code', WSTEPS[active][1])) hits++;
    if (hits > 0){ add(parent, si, {hFill:true}); return si; }
    safe(function(){ si.remove(); });
  }
  const f = mkFrame('steps', {dir:'H', gap:0});
  add(parent, f, {hFill:true});
  WSTEPS.forEach(function(s, i){
    const done = i < active, on = i === active;
    const edge = done ? C.green : (on ? C.brand : C.line);
    const st = mkFrame('step', {dir:'V', gap:0, pad:[9,12,9,12], stroke:edge, sides:[0,0,3,0]});
    add(f, st, {hFix:180});
    add(st, mkText(s[1], {font:F.mono, size:10, lh:14, color:C.ink3, name:'sn'}), {hFill:true});
    add(st, mkText(s[0], {font:F.dispSemi, size:14, lh:19,
      color: done ? C.greenInk : (on ? C.ink : C.ink3), name:'stt'}), {hFill:true});
  });
  return f;
}

/* ---- .pick / .pick.sel / .pick.no ------------------------------------ */
function pickRow(parent, o){
  const state = o.blocked ? 'blocked' : (o.sel ? 'selected' : 'default');
  const pi = tryInst('Pick Row', {state: state});
  if (pi){
    let hits = 0;
    ['pk','code','kicker','initials'].forEach(function(n){ if (setText(pi, n, o.code)) hits++; });
    ['pt','title','label','name'].forEach(function(n){ if (setText(pi, n, o.title)) hits++; });
    ['ps','sub','meta'].forEach(function(n){ if (setText(pi, n, o.sub)) hits++; });
    if (hits > 0){
      add(parent, pi, {hFill:true});
      ['pr','reason','error'].forEach(function(n){
        const t = setText(pi, n, o.blocked ? o.reason : '');
        if (t) t.visible = !!o.blocked;
      });
      const ch = pi.findOne(function(n){ return n.type === 'INSTANCE' && n.name === 'chip'; });
      if (ch){
        if (o.blocked) ch.visible = false;
        else setChip(ch, o.chipTone || 'green', o.chip || '', false);
      }
      return pi;
    }
    safe(function(){ pi.remove(); });
  }
  const no = !!o.blocked, sel = !!o.sel;
  const f = mkFrame('Pick Row', {dir:'H', gap:12, align:'CENTER', pad:[12,14,12,14], radius:7,
    fill: no ? C.panel2 : (sel ? '#f2fbf6' : C.white), stroke: sel ? C.brand : C.line});
  add(parent, f, {hFill:true});
  const pk = mkFrame('pk', {dir:'V', w:38, h:38, radius:9, fill:C.line2, align:'CENTER', just:'CENTER'});
  add(pk, mkText(o.code, {font:F.dispBold, size:13, lh:17, color:C.ink2}));
  add(f, pk);
  const pb = mkFrame('pb', {dir:'V', gap:2});
  add(f, pb, {hFill:true});
  add(pb, mkText(o.title, {font:F.semi, size:13, lh:18, name:'pt'}), {hFill:true});
  add(pb, mkText(o.sub, {size:11.5, lh:16, color:C.ink2, name:'ps'}), {hFill:true});
  if (no){
    const pr = mkFrame('pr', {dir:'H', gap:0, pad:[2,7,2,7], radius:20, fill:C.redBg, align:'CENTER'});
    add(pr, mkText(o.reason, {font:F.mono, size:10.5, lh:15, color:C.redInk, name:'pr-text'}));
    add(f, pr);
    safe(function(){ f.opacity = 0.62; });
  } else {
    add(f, chipNode(o.chipTone || 'green', o.chip || '', false));
  }
  return f;
}

/* ---- CO-22 roster line ------------------------------------------------ */
function rosterLine(parent, o){
  const r = mkFrame('roster-line', {dir:'H', gap:10, align:'CENTER', pad:[7,0,7,0],
    stroke:C.line2, sides:[0,0,1,0]});
  add(parent, r, {hFill:true});
  const av = mkFrame('pk', {dir:'V', w:30, h:30, radius:8, fill:C.line2, align:'CENTER', just:'CENTER'});
  add(av, mkText(o.ini, {font:F.dispBold, size:11, lh:15, color:C.ink2}));
  add(r, av);
  const b = mkFrame('b', {dir:'V', gap:2});
  add(r, b, {hFill:true});
  add(b, mkText(o.name, {font:F.semi, size:12.5, lh:17}), {hFill:true});
  add(b, mkText(o.sub, {size:11, lh:15, color:C.ink3}), {hFill:true});
  add(r, chipNode(o.ok ? 'green' : 'red', o.ok ? 'May start a session' : 'Blocked', true));
  return r;
}

/* ---- .drop (bulk upload / document dropzone) -------------------------- */
function dropZone(parent, title, sub){
  const d = mkFrame('drop', {dir:'V', gap:3, pad:[22,22,22,22], radius:10, align:'CENTER',
    just:'CENTER', fill:C.panel2, stroke:C.line});
  add(parent, d, {hFill:true});
  safe(function(){ d.dashPattern = [6,4]; d.strokeWeight = 1.5; });
  add(d, svgIcon(I.up, 22, C.ink2, 1.8));
  add(d, mkText(title, {font:F.dispSemi, size:14, lh:19, align:'CENTER', name:'dt2'}), {hFill:true});
  add(d, mkText(sub, {size:11.5, lh:16, color:C.ink2, align:'CENTER', name:'ds2'}), {hFill:true});
  return d;
}

/* ============================ A. WIZARD ============================
   Load SHP-FTL-10001 — FTL - Standard Goods, Dry Van, 24 pallets / 39,600 lbs,
   Packaged Food, status Carrier Accepted. needTrailer is true (not a Dump Truck).
   Eligibility strings below are exactly what renderWizard() computes for it.  */
const WZ_STOPS = [
  {k:'P', loc:'San Jose, CA', zip:'95112',
   meta:'2026-07-25   08:00 – 12:00 UTC     24 pallets     39,600 lbs', chip:'LIVE'},
  {k:'D', loc:'Tracy, CA', zip:'95376',
   meta:'2026-07-25   15:00 – 18:00 UTC     24 pallets     39,600 lbs', chip:'DROP'}
];
function wizardShell(step){
  const s = mkSheet('Assign assets — SHP-FTL-10001',
    'Shipment Execution OPS-03 → OPS-04 → OPS-05 → OPS-06');
  stepper(s.body, step);
  dpanel(s.body, {title:'SHP-FTL-10001', hint:'Dry Van · 39,600 lbs · Packaged Food',
    parts:[{t:'stops', rows:WZ_STOPS}]});
  return s;
}
/* W1 — OPS-03 truck eligibility */
function buildW1(){
  const s = wizardShell(0);
  const hd = mkFrame('hd', {dir:'V', gap:4});
  add(s.body, hd, {hFill:true});
  h4(hd, 'Select a truck', 'Filtered on equipment type, capacity against shipment weight, annual inspection, insurance and Available asset status.');
  const list = mkFrame('picks', {dir:'V', gap:8});
  add(s.body, list, {hFill:true});
  [
   {code:'001', title:'Semi Truck (Sleeper Cab) · Freightliner Cascadia 126',
    sub:'8ZTK492 CA · reg exp 2027-02-28 · San Jose Hub',
    blocked:true, reason:'Asset status In Transit'},
   {code:'002', title:'Semi Truck (Day Cab) · Kenworth T680',
    sub:'9LMD778 CA · reg exp 2026-08-14 · San Jose Hub',
    chip:'Available', chipTone:'green'},
   {code:'003', title:'Semi Truck (Sleeper Cab) · Peterbilt 579',
    sub:'7RQP210 NV · reg exp 2027-05-30 · Sacramento Depot',
    chip:'Available', chipTone:'green'},
   {code:'004', title:'Dump Truck (Standard) · Mack Granite 64FR',
    sub:'6BHT031 CA · reg exp 2026-07-31 · Tracy Staging',
    blocked:true, reason:'Asset status Out of Service'},
   {code:'005', title:'Dump Truck (Articulated) · Volvo A40G',
    sub:'5KWD884 CA · reg exp 2027-01-15 · Tracy Staging',
    blocked:true, reason:'Asset status At Delivery/Dump'},
   {code:'006', title:'Bobtail (No Trailer) · International LT625',
    sub:'4NPC556 CA · reg exp 2027-03-20 · San Jose Hub',
    chip:'Available', chipTone:'green'},
   {code:'007', title:'Yard Truck (Terminal Tractor) · Kalmar Ottawa T2',
    sub:'YRD-0031 CA · reg exp 2026-11-02 · Sacramento Depot',
    blocked:true, reason:'Asset status Unavailable'},
   {code:'008', title:'Straight Truck (Medium Duty) · Hino 268A',
    sub:'3GTV909 CA · reg exp 2026-09-08 · San Jose Hub',
    blocked:true, reason:'Asset status Halt'}
  ].forEach(function(o){ pickRow(list, o); });
  mkFoot(s.sheet, [{t:'Cancel'}]);
  return mkOverlay('W1 Assign — Truck', s.sheet);
}
/* W2 — OPS-04 trailer eligibility (truck 002 already picked) */
function buildW2(){
  const s = wizardShell(1);
  const hd = mkFrame('hd', {dir:'V', gap:4});
  add(s.body, hd, {hFill:true});
  h4(hd, 'Select a trailer', 'Filtered on trailer type against the shipment equipment, maximum payload against shipment weight, inspection expiry and insurance. Reefer loads additionally check temperature range support and flag pre-cooling.');
  const list = mkFrame('picks', {dir:'V', gap:8});
  add(s.body, list, {hFill:true});
  [
   {code:'011', title:'Dry Van · 53′ · 45,000 lbs max payload',
    sub:'1JJV532W1PL778120 · Wabash 2021',
    blocked:true, reason:'Status In Transit'},
   {code:'012', title:'Dry Van · 48′ · 42,000 lbs max payload',
    sub:'1JJV532W7NL661044 · Great Dane 2019',
    chip:'Available', chipTone:'green'},
   {code:'013', title:'Flatbed · 48′ · 48,000 lbs max payload',
    sub:'1UYFS2483M2119887 · Utility 2020',
    chip:'Available', chipTone:'green'},
   {code:'014', title:'Step Deck · 48′ · 46,000 lbs max payload',
    sub:'1DW1A5321LB410992 · Fontaine 2018',
    chip:'Available', chipTone:'green'},
   {code:'015', title:'Reefer · 53′ · 44,000 lbs max payload',
    sub:'1UYVS2534N2445120 · Utility 2022 · set-point -2 °C',
    blocked:true, reason:'Status Out of Service'},
   {code:'016', title:'Reefer · 53′ · 44,500 lbs max payload',
    sub:'1UYVS2534P2551338 · Great Dane 2023 · set-point +2 °C',
    blocked:true, reason:'Reefer not required for this load'},
   {code:'017', title:'Double Drop · 45′ · 52,000 lbs max payload',
    sub:'1RNF48A29KR220117 · Talbert 2017',
    blocked:true, reason:'Status Unavailable'}
  ].forEach(function(o){ pickRow(list, o); });
  renderBlocks(s.body, [{t:'note', tone:'amber',
    body:'The trailer is linked to the truck as PRIMARY. CO-13 supports a secondary trailer for multi-trailer operations; add it after confirming this assignment.'}], 'desktop');
  mkFoot(s.sheet, [{t:'Cancel'}, {t:'Back'}]);
  return mkOverlay('W2 Assign — Trailer', s.sheet);
}
/* W3 — OPS-05 driver, roster of TRK-…-002 = Nair, Martinez, Alvarez, Torres */
function buildW3(){
  const s = wizardShell(2);
  renderBlocks(s.body, [{t:'banner', tone:'warn',
    title:'Driver selection is pending a business decision (OC-1)',
    body:'The Shipment Execution BRD specifies driver selection here (OPS-05). The standing truck-login model says the driver is instead derived when someone starts a session on the assigned truck. Both are shown: pick a driver now, or commit the truck alone and let the roster decide.'}], 'desktop');
  const hd = mkFrame('hd', {dir:'V', gap:4});
  add(s.body, hd, {hFill:true});
  h4(hd, 'Select a driver', 'Drivers on the roster for 002. Filtered on CDL class compatibility, CDL expiry, medical certificate expiry, insurance flag and driver status.');
  const list = mkFrame('picks', {dir:'V', gap:8});
  add(s.body, list, {hFill:true});
  [
   {code:'PN', title:'Priya Nair · Salaried',
    sub:'Class A T · CDL exp 2027-09-30 · med exp 2026-12-08 · HOS 4.0 h',
    chip:'In Transit', chipTone:'amber'},
   {code:'RM', title:'Rosa Martinez · Owner-Operator',
    sub:'Class A N · CDL exp 2029-01-22 · med exp 2027-05-11 · HOS 8.4 h',
    chip:'On Duty', chipTone:'amber'},
   {code:'DA', title:'Diego Alvarez · Contractual',
    sub:'Class A HN · CDL exp 2028-07-08 · med exp 2027-01-30 · HOS 11.0 h',
    sel:true, chip:'Available', chipTone:'green'},
   {code:'ST', title:'Sofia Torres · Salaried',
    sub:'Class A T · CDL exp 2027-11-03 · med exp 2026-06-15 · HOS 0.0 h',
    blocked:true,
    reason:'Suspended — medical_cert_expiry lapsed 2026-06-15 — FMCSA compliance failed'}
  ].forEach(function(o){ pickRow(list, o); });
  const alt = mkFrame('alt', {dir:'H', gap:8});
  add(s.body, alt, {hFill:true});
  add(alt, btnNode('Commit the truck only — driver resolves at tablet login', 'secondary'));
  mkFoot(s.sheet, [{t:'Cancel'}, {t:'Back'}]);
  return mkOverlay('W3 Assign — Driver', s.sheet);
}
/* W4 — OPS-06 confirm (truck 002 + trailer 012 PRIMARY + Diego Alvarez) */
function buildW4(){
  const s = wizardShell(3);
  const hd = mkFrame('hd', {dir:'V', gap:4});
  add(s.body, hd, {hFill:true});
  h4(hd, 'Confirm the combined load assignment');
  dpanel(s.body, {parts:[{t:'kv', rows:[
    {k:'Load',   v:'SHP-FTL-10001', sfx:'FTL - Standard Goods'},
    {k:'Truck',  v:'002', sfx:'Semi Truck (Day Cab) · Kenworth T680'},
    {k:'Trailer',v:'012', sfx:'Dry Van · PRIMARY'},
    {k:'Driver', v:'Diego Alvarez'},
    {k:'Resulting status', v:'Driver Assigned', chip:{tone:'amber', t:'Driver Assigned'}},
    {k:'Notifications fired',
     v:'CR-007 to carrier · DR-001 to driver · SH-003 to shipper · FTL-01'}
  ]}]});
  renderBlocks(s.body, [{t:'note', tone:'amber',
    body:'Compliance checks passed at assignment. The same checks are re-applied when a driver starts a session on this truck — CDL, medical certificate, drug & alcohol status, roster membership and the truck’s dispatch eligibility.'}], 'desktop');
  mkFoot(s.sheet, [{t:'Back'}, {t:'Confirm assignment', kind:'primary'}]);
  return mkOverlay('W4 Assign — Confirm', s.sheet);
}

/* ============================ B. RECORD DRAWERS ============================ */
/* D1 — openTruck('TRK-CARR-US-00142-002') */
function buildD1(){
  const s = mkSheet('002 · Semi Truck (Day Cab)', 'Full CO-10 / CO-11 record');
  dpanel(s.body, {parts:[{t:'kv', rows:[
    {k:'Truck code', v:'TRK-CARR-US-00142-002'},
    {k:'VIN', v:'3AKJHHDR8LSLR2210'},
    {k:'Vehicle type', v:'Semi Truck (Day Cab)'},
    {k:'Make / model', v:'Kenworth T680'},
    {k:'Licence plate', v:'9LMD778', sfx:'issuing state CA'},
    {k:'Registration expiry', v:'2026-08-14', chip:{tone:'amber', t:'21 days'}},
    {k:'Registration status', v:'Expiring', sfx:'CO-11 DMV validation'},
    {k:'Insurance status', v:'Valid', chip:{tone:'green', t:'Valid'}},
    {k:'Serviceable (CO-11)', v:'Yes', chip:{tone:'green', t:'Yes'}},
    {k:'Asset status', v:'Available', sfx:'dispatch allowed'},
    {k:'Home yard', v:'San Jose Hub'},
    {k:'Paired device', v:'TAB-4472', sfx:'SAMSARA · Active'},
    {k:'Odometer', v:'288,150 mi', sfx:'source: telematics — not captured at CO-10 (OC-8)'},
    {k:'Fuel type', v:'DIESEL', sfx:'not captured at CO-10 (OC-8)'},
    {k:'Last DVIR', v:'2026-07-24', chip:{tone:'green', t:'No defect'}}
  ]}]});
  const card = dpanel(s.body, {title:'Truck roster', hint:'CO-22 · minimum 4 drivers'});
  const rbox = mkFrame('roster', {dir:'V', gap:0, pad:[12,16,12,16]});
  add(card, rbox, {hFill:true});
  [
   {ini:'PN', name:'Priya Nair',    sub:'Class A · Salaried',       ok:true},
   {ini:'RM', name:'Rosa Martinez', sub:'Class A · Owner-Operator', ok:true},
   {ini:'DA', name:'Diego Alvarez', sub:'Class A · Contractual',    ok:true},
   {ini:'ST', name:'Sofia Torres',  sub:'Class A · Salaried',       ok:false}
  ].forEach(function(o){ rosterLine(rbox, o); });
  dpanel(s.body, {title:'Attached trailers', hint:'CO-13 · primary + secondary',
    parts:[{t:'kv', rows:[
      {k:'PRIMARY',   v:'None attached', empty:true},
      {k:'SECONDARY', v:'None attached', empty:true}
    ]}]});
  renderBlocks(s.body, [{t:'note', tone:'amber',
    body:'A secondary trailer is only valid where the tractor and jurisdiction permit a multi-trailer combination. The assignment wizard commits the primary; the secondary is attached here.'}], 'desktop');
  mkFoot(s.sheet, [{t:'Edit truck'}, {t:'Log maintenance'}]);
  return mkOverlay('D1 Drawer — Truck', s.sheet);
}
/* D2 — openTrailer('TRL-CARR-US-00142-015') */
function buildD2(){
  const s = mkSheet('015 · Reefer', 'Full CO-12 record');
  dpanel(s.body, {parts:[{t:'kv', rows:[
    {k:'Trailer code', v:'TRL-CARR-US-00142-015'},
    {k:'Trailer VIN', v:'1UYVS2534N2445120'},
    {k:'Trailer type', v:'Reefer'},
    {k:'Make / model year', v:'Utility · 2022'},
    {k:'Length', v:'53 feet'},
    {k:'Maximum payload', v:'44,000 lbs',
     sfx:'legal weight limit — drives the OPS-04 capacity filter'},
    {k:'Trailer photo', v:'On file', chip:{tone:'green', t:'On file'}},
    {k:'Status', v:'Out of Service', chip:{tone:'red', t:'Out of Service'}},
    {k:'Attached to truck', v:'Not attached', empty:true},
    {k:'Annual inspection expiry', v:'2026-09-19'},
    {k:'Insured', v:'Yes', chip:{tone:'green', t:'Yes'}},
    {k:'Reefer set-point', v:'-2 °C'},
    {k:'Reefer alarm', v:'Unit offline — REEFER_PM due', chip:{tone:'red', t:'Alarm'}},
    {k:'Home yard', v:'Tracy Staging'}
  ]}]});
  mkFoot(s.sheet, [{t:'Edit trailer'}]);
  return mkOverlay('D2 Drawer — Trailer', s.sheet);
}
/* D3 — openDriver('DRV-CARR-US-00142-0005') — Sofia Torres, incl. CO-21 Ratings */
function buildD3(){
  const s = mkSheet('Sofia Torres',
    'Full profile — status, documents, licence, ratings, earnings & insurance in one place');
  renderBlocks(s.body, [{t:'banner', tone:'crit', title:'Not dispatchable',
    body:'Suspended — medical_cert_expiry lapsed 2026-06-15 — FMCSA compliance failed'}], 'desktop');
  dpanel(s.body, {title:'Status', hint:'live · ELD feed', parts:[{t:'kv', rows:[
    {k:'Driver status', v:'Off Duty', chip:{tone:'grey', t:'Off Duty'}},
    {k:'Duty status (HOS)', v:'OFF_DUTY', chip:{tone:'grey', t:'OFF_DUTY'}},
    {k:'Remaining driving hours', v:'0.0 h', chip:{tone:'red', t:'30 min warning'}},
    {k:'Current truck', v:'Not in a truck', empty:true},
    {k:'Location', v:'San Jose Hub'},
    {k:'Dispatch eligibility', v:'Blocked', chip:{tone:'red', t:'Blocked'},
     sfx:'Suspended — medical_cert_expiry lapsed 2026-06-15'}
  ]}]});
  dpanel(s.body, {title:'Identity & contact', hint:'CO-17', parts:[{t:'kv', rows:[
    {k:'Driver code', v:'DRV-CARR-US-00142-0005'},
    {k:'Date of birth', v:'1988-11-03'},
    {k:'Phone', v:'+1 408 555 0277'},
    {k:'Email', v:'s.torres@apexfreight.example'},
    {k:'Address', v:'314 Delmas Ave, San Jose, CA 95126'},
    {k:'Nationality', v:'US', sfx:'CO-18'}
  ]}]});
  dpanel(s.body, {title:'Documents', hint:'CO-09 ladder · CO-19 / CO-20', parts:[{t:'kv', rows:[
    {k:'CDL expiry', v:'2027-11-03'},
    {k:'Medical certificate expiry', v:'2026-06-15', chip:{tone:'red', t:'expired'}},
    {k:'Identity verification (CO-19)', v:'Verified',
     sfx:'CDL OCR + facial recognition match'},
    {k:'Drug & alcohol status (CO-20)', v:'Compliant', sfx:'Federal Clearinghouse'},
    {k:'Driver photo', v:'On file', chip:{tone:'green', t:'On file'}}
  ]}]});
  dpanel(s.body, {title:'Licence', hint:'CO-17 · DRV-07', parts:[{t:'kv', rows:[
    {k:'CDL number', v:'CA D2298431'},
    {k:'Issuing state', v:'CA', sfx:'state prefix validated per DRV-07'},
    {k:'CDL class', v:'Class A'},
    {k:'Endorsements', v:'T'},
    {k:'Years of experience', v:'9'},
    {k:'Examiner name', v:'R. Villanueva'},
    {k:'Hire date', v:'2020-02-17'}
  ]}]});
  dpanel(s.body, {title:'Ratings', hint:'CO-21', parts:[
    {t:'bars', rows:[
      {label:'On-time delivery', value:'4.4', pct:88, tone:'amber'},
      {label:'Behaviour',        value:'4.5', pct:90, tone:'green'},
      {label:'Communication',    value:'4.2', pct:84, tone:'amber'}
    ]},
    {t:'kv', rows:[
      {k:'No-shows', v:'0', chip:{tone:'green', t:'0'}},
      {k:'Bid cancellations', v:'0', chip:{tone:'green', t:'0'}},
      {k:'Overall', v:'4.4'},
      {k:'Trips / completed', v:'187 / 184'},
      {k:'Idle time', v:'3.4 h'}
    ]}
  ]});
  dpanel(s.body, {title:'Earnings', hint:'CO-18 settlement', parts:[{t:'kv', rows:[
    {k:'Driver type', v:'Salaried'},
    {k:'Payment model', v:'Salary · $6,000 / month'},
    {k:'Associated AWB', v:'No air segment', empty:true},
    {k:'Shipments', v:'None', empty:true}
  ]}]});
  dpanel(s.body, {title:'Insurance', hint:'CO-18 · Appendix F', parts:[{t:'kv', rows:[
    {k:'Is the driver insured?', v:'Yes', chip:{tone:'green', t:'Yes'},
     sfx:'CO-18 — answers OPEN-02'},
    {k:'Policy detail', v:'Policy record not modelled — OC-5', empty:true},
    {k:'Assignment eligibility', v:'Eligible', chip:{tone:'green', t:'Eligible'}}
  ]}]});
  dpanel(s.body, {title:'Truck roster', hint:'CO-22', parts:[{t:'kv', rows:[
    {k:'Rostered on', v:'002 · 004 · 006 · 008'},
    {k:'Favourite destination', v:'Sacramento', sfx:'6A priority input · DT-29'}
  ]}]});
  mkFoot(s.sheet, [{t:'Edit driver'}, {t:'Message driver'}]);
  return mkOverlay('D3 Drawer — Driver', s.sheet);
}
/* D4 — openLoad('SHP-FTL-10001') */
function buildD4(){
  const s = mkSheet('SHP-FTL-10001', 'FTL - Standard Goods · Dry Van');
  dpanel(s.body, {title:'Stops', hint:'2 stops · Super Set execution data',
    parts:[{t:'stops', rows:WZ_STOPS}]});
  dpanel(s.body, {title:'Load detail', parts:[{t:'kv', rows:[
    {k:'Shipment ID', v:'SHP-FTL-10001', sfx:'prefix per Super Set'},
    {k:'Status', v:'Carrier Accepted', chip:{tone:'blue', t:'Carrier Accepted'}},
    {k:'Commodity', v:'Packaged Food', sfx:'Food & Beverage'},
    {k:'Equipment', v:'Dry Van'},
    {k:'Pallets / weight', v:'24 pallets · 39,600 lbs'},
    {k:'Rate / break-even', v:'$1,840 · $1,520'},
    {k:'AWB', v:'Not applicable — no air segment', empty:true},
    {k:'Truck / trailer / driver', v:'— · — · —'},
    {k:'Tender accepted', v:'2026-07-23 14:20'},
    {k:'Rate confirmation', v:'Signed 2026-07-23', sfx:'DOC-027'}
  ]}]});
  mkFoot(s.sheet, [{t:'Assign assets', kind:'primary'}]);
  return mkOverlay('D4 Drawer — Load', s.sheet);
}
/* D5 — openPaymentDetails() */
function buildD5(){
  const s = mkSheet('Update payment details',
    'ACH payout account and payout schedule — changes apply from the next payout cycle');
  const c1 = dpanel(s.body, {title:'ACH payout account', hint:'Stripe Connect'});
  const b1 = padBox(c1);
  fieldCell(b1, {label:'Bank name', v:'First Republic Bank'});
  const g1 = fgrid(b1);
  fieldCell(g1, {label:'Routing number', v:'121000358'});
  fieldCell(g1, {label:'Account number', v:'••••••4417'});
  const nt = tryInst('Note', {tone:'blue'});
  if (nt){
    add(b1, nt, {hFill:true});
    setText(nt, 'body', 'Changing your bank account restarts Stripe micro-deposit verification (1–2 business days) before payouts resume.');
  }
  const c2 = dpanel(s.body, {title:'Payout schedule', hint:'carrier-configurable'});
  const b2 = padBox(c2);
  const g2 = fgrid(b2);
  fieldCell(g2, {label:'Weekly payout day', v:'Friday', select:true,
    hlp:'Currently paid out every Friday'});
  fieldCell(g2, {label:'Payout week anchor', v:'Week 1 (this cycle)', select:true,
    hlp:'Aligns your payout to a specific week if you are moved between cycles'});
  mkFoot(s.sheet, [{t:'Cancel'}, {t:'Save changes', kind:'primary'}]);
  return mkOverlay('D5 Drawer — Payment details', s.sheet);
}

/* ============================ C. CREATE FORMS ============================ */
/* F1 — openTruckForm(), VIN in its CO-10 duplicate-rejected error state */
function buildF1(){
  const s = mkSheet('Register truck',
    'Carrier Onboarding CO-10 — validated at CO-11 against the DMV');
  const form = mkFrame('form', {dir:'V', gap:13});
  add(s.body, form, {hFill:true});
  fieldCell(form, {label:'VIN', req:true, v:'1FUJGLDR5CLBP8834',
    hlp:'17 characters. Must be unique across your fleet (CO-10).',
    err:'This VIN is already registered to 001. Duplicate VIN rejected (CO-10).'});
  const g1 = fgrid(form);
  fieldCell(g1, {label:'Vehicle type', req:true, select:true, v:'Straight Truck (Light Duty)',
    hlp:'Master Data §1.2 — ten types'});
  fieldCell(g1, {label:'Home yard', req:true, select:true, v:'San Jose Hub'});
  const g2 = fgrid(form);
  fieldCell(g2, {label:'Vehicle make', req:true, ph:'Freightliner'});
  fieldCell(g2, {label:'Vehicle model', req:true, ph:'Cascadia 126'});
  const g3 = fgrid(form);
  fieldCell(g3, {label:'Licence plate number', req:true, ph:'8ZTK492'});
  fieldCell(g3, {label:'Plate issuing state', req:true, ph:'CA', hlp:'Two-letter state code'});
  fieldCell(g3, {label:'Registration expiry', req:true, ph:'yyyy-mm-dd',
    hlp:'Monitored on the CO-09 ladder'});
  renderBlocks(s.body, [{t:'note', tone:'amber',
    body:'On save the truck is created with registration status Pending until CO-11 DMV validation returns, and it cannot be selected for a load until it is Serviceable.'}], 'desktop');
  mkFoot(s.sheet, [{t:'Cancel'}, {t:'Register truck', kind:'primary'}]);
  return mkOverlay('F1 Form — Register truck', s.sheet);
}
/* F2 — openYardForm(), yard code in its CO-14 uniqueness error state */
function buildF2(){
  const s = mkSheet('Add yard',
    'Carrier Onboarding CO-14 — usable for dispatch, staging and relay');
  const form = mkFrame('form', {dir:'V', gap:13});
  add(s.body, form, {hFill:true});
  const g1 = fgrid(form);
  fieldCell(g1, {label:'Yard name', req:true, ph:'San Jose Hub'});
  fieldCell(g1, {label:'Yard code', req:true, v:'001',
    hlp:'Unique per carrier (carrier_id + yard_code)',
    err:'A yard with this code already exists — unique constraint on carrier + yard code (CO-14).'});
  const g2 = fgrid(form);
  fieldCell(g2, {label:'Yard type', req:true, select:true, v:'Owned', hlp:'CO-14 vocabulary'});
  fieldCell(g2, {label:'Status', req:true, select:true, v:'active'});
  fieldCell(form, {label:'Address line 1', req:true, ph:'1180 Coleman Ave'});
  const g3 = fgrid(form);
  fieldCell(g3, {label:'City', req:true, ph:'San Jose'});
  fieldCell(g3, {label:'State', req:true, ph:'CA'});
  fieldCell(g3, {label:'ZIP code', req:true, ph:'95110'});
  const g4 = fgrid(form);
  fieldCell(g4, {label:'Latitude', req:true, ph:'37.3654',
    hlp:'Drives geofencing, arrival detection and detention timing'});
  fieldCell(g4, {label:'Longitude', req:true, ph:'-121.9245'});
  const g5 = fgrid(form);
  fieldCell(g5, {label:'Truck capacity', req:true, ph:'40'});
  fieldCell(g5, {label:'Trailer capacity', req:true, ph:'60'});
  fieldCell(g5, {label:'Geofence radius (m)', req:true, v:'250'});
  mkFoot(s.sheet, [{t:'Cancel'}, {t:'Add yard', kind:'primary'}]);
  return mkOverlay('F2 Form — Add yard', s.sheet);
}
/* F3 — openDriverForm(), CDL number in its CO-17 duplicate error state */
function buildF3(){
  const s = mkSheet('Add driver',
    'Carrier Onboarding CO-17 — creates the auth user record and starts identity verification');
  const form = mkFrame('form', {dir:'V', gap:13});
  add(s.body, form, {hFill:true});
  const g1 = fgrid(form);
  fieldCell(g1, {label:'First name', req:true, ph:'Marcus'});
  fieldCell(g1, {label:'Last name', req:true, ph:'Reyes'});
  const g2 = fgrid(form);
  fieldCell(g2, {label:'Date of birth', req:true, ph:'yyyy-mm-dd'});
  fieldCell(g2, {label:'Hire date', req:true, ph:'yyyy-mm-dd'});
  const g3 = fgrid(form);
  fieldCell(g3, {label:'Phone number', req:true, ph:'+1 408 555 0231',
    hlp:'Must be unique (CO-17)'});
  fieldCell(g3, {label:'Email address', req:true, ph:'m.reyes@apexfreight.example',
    hlp:'Must be unique (CO-17)'});
  const g4 = fgrid(form);
  fieldCell(g4, {label:'CDL number', req:true, v:'D2214870', hlp:'Duplicate CDL rejected',
    err:'This CDL number is already on your roster — duplicate CDL rejected (CO-17).'});
  fieldCell(g4, {label:'CDL issuing state', req:true, v:'CA',
    hlp:'Two-letter code — drives the DRV-07 state-prefix check'});
  fieldCell(g4, {label:'CDL expiry', req:true, ph:'yyyy-mm-dd'});
  const g5 = fgrid(form);
  fieldCell(g5, {label:'CDL class', req:true, select:true, v:'A'});
  fieldCell(g5, {label:'Driver type', req:true, select:true, v:'Salaried', hlp:'CO-18'});
  fieldCell(g5, {label:'Endorsements',
    ph:'H N T X P S',
    hlp:'H N T X P S — comma separated. H additionally requires a TSA assessment (DRV-07).'});
  fieldCell(form, {label:'Medical certificate expiry', req:true, ph:'yyyy-mm-dd',
    hlp:'Monitored on the CO-09 ladder (DOC-018/019)'});
  renderBlocks(s.body, [{t:'note', tone:'amber',
    body:'The driver is created with status Pending. CO-19 identity verification and the CO-20 Drug & Alcohol Clearinghouse check must both pass before the driver becomes dispatchable.'}], 'desktop');
  mkFoot(s.sheet, [{t:'Cancel'}, {t:'Add driver', kind:'primary'}]);
  return mkOverlay('F3 Form — Add driver', s.sheet);
}
/* F4 — openInvite(), email in its CO-28 409-Conflict error state */
function buildF4(){
  const s = mkSheet('Invite user',
    'Creates an unverified account and sends a verification code by email (CO-28).');
  const form = mkFrame('form', {dir:'V', gap:13});
  add(s.body, form, {hFill:true});
  const g1 = fgrid(form);
  fieldCell(g1, {label:'First name', req:true, ph:'D.'});
  fieldCell(g1, {label:'Last name', req:true, ph:'Rao'});
  fieldCell(form, {label:'Email address', req:true, v:'d.rao@apexfreight.example',
    hlp:'Must be unique within the organisation — duplicates return 409 Conflict',
    err:'This email is already registered in your organisation. 409 Conflict (CO-28).'});
  const g2 = fgrid(form);
  fieldCell(g2, {label:'Phone number', req:true, ph:'+1 408 555 0142'});
  fieldCell(g2, {label:'Role', req:true, select:true, v:'Carrier Super Admin',
    hlp:'Determines every screen and action available to this user'});
  renderBlocks(s.body, [{t:'note', tone:'amber',
    body:'CO-28 rejects a duplicate email within the organisation with 409 Conflict. Try d.rao@apexfreight.example to see the rule fire.'}], 'desktop');
  mkFoot(s.sheet, [{t:'Cancel'}, {t:'Send invite', kind:'primary'}]);
  return mkOverlay('F4 Form — Invite user', s.sheet);
}
/* F5 — openCreateRole(), the fixed Auth Services BRD V3 permission catalogue */
const RBAC_CATS = [
  ['ORG','Organization & Setup'], ['USERS','Roles & User Management'],
  ['SHIP','Shipment Management'], ['LOAD','Load Board & Auctions'],
  ['TRACK','Shipment Tracking'], ['POD','Delivery & POD'],
  ['FLEET','Fleet & Truck Management'], ['DRVMGT','Driver Management'],
  ['DRVOPS','Driver Operations'], ['COMP','Compliance & Documents'],
  ['PAY','Payments (ACH)'], ['BILL','Billing & Invoicing'],
  ['AWB','AWB'], ['REP','Reports & Dashboards']
];
function buildF5(){
  const s = mkSheet('Create role',
    'Carrier admin composes a new role from the fixed permission catalogue below — permissions themselves cannot be invented, only combined. The role becomes assignable to any user once created.');
  const form = mkFrame('form', {dir:'V', gap:13});
  add(s.body, form, {hFill:true});
  fieldCell(form, {label:'Role name', req:true, ph:'Custom Role 1',
    hlp:'Shown wherever roles are listed and assigned'});
  const wrap = mkFrame('field', {dir:'V', gap:3});
  add(form, wrap, {hFill:true});
  add(wrap, mkText('PERMISSION CATEGORIES  *', {font:F.semi, size:11, lh:15, ls:0.77,
    color:C.ink3, case:'UPPER', name:'label'}), {hFill:true});
  add(wrap, mkText('Select every functional category this role should have view/update access to',
    {size:11, lh:15, color:C.ink3, name:'hlp'}), {hFill:true});
  const box = mkFrame('catbox', {dir:'V', gap:0, radius:7, stroke:C.line, fill:C.white, clip:true});
  add(wrap, box, {hFill:true});
  RBAC_CATS.forEach(function(c, i){
    const row = mkFrame('cat', {dir:'H', gap:10, align:'CENTER', pad:[9,12,9,12],
      stroke:C.line2, sides:[0,0, i === RBAC_CATS.length - 1 ? 0 : 1, 0]});
    add(box, row, {hFill:true});
    const cb = mkFrame('checkbox', {dir:'V', w:14, h:14, radius:4,
      fill: i < 3 ? C.brand : C.white, stroke: i < 3 ? C.brand : C.line, align:'CENTER', just:'CENTER'});
    if (i < 3) add(cb, svgIcon(I.check, 10, C.white, 2.6));
    add(row, cb);
    const lb = mkFrame('lb', {dir:'H', gap:6, align:'CENTER', wrap:true, crossGap:2});
    add(row, lb, {hFill:true});
    add(lb, mkText(c[1], {font:F.semi, size:12.5, lh:17}));
    add(lb, mkText(c[0], {font:F.mono, size:10.5, lh:15, color:C.ink3}));
  });
  mkFoot(s.sheet, [{t:'Cancel'}, {t:'Create role', kind:'primary'}]);
  return mkOverlay('F5 Form — Create role', s.sheet);
}

/* ============================ D. BULK UPLOAD ============================ */
/* F6 — openBulkUpload('trucks') dropzone + template + rules, then bulkPick()'s
        per-row validation report. */
const BULK_COLS = ['vin','vehicle_type','make','model','plate_number','plate_state',
  'registration_expiry','home_yard'];
const BULK_RULES = [
  'VIN must be 17 characters and unique across the fleet',
  'plate_state must be a two-letter code',
  'registration_expiry must be a future date',
  'vehicle_type must match the Master Data §1.2 catalogue'
];
function buildF6(){
  const s = mkSheet('Bulk upload trucks — validation report',
    '8 rows read · 6 accepted · 2 rejected');
  dropZone(s.body, 'Choose a CSV or XLSX file',
    'Any other format is rejected with 415 — File format not supported. Please upload PDF, JPG, or PNG.');
  const cc = dpanel(s.body, {title:'Template columns', hint:'8 columns'});
  const cbox = mkFrame('cols', {dir:'H', gap:7, wrap:true, crossGap:7, pad:[14,16,14,16]});
  add(cc, cbox, {hFill:true});
  BULK_COLS.forEach(function(c){
    const ch = mkFrame('fchip', {dir:'H', gap:0, pad:[4,9,4,9], radius:20, fill:C.panel2, stroke:C.line});
    add(ch, mkText(c, {font:F.mono, size:10.5, lh:15, color:C.ink2}));
    add(cbox, ch);
  });
  const rc = dpanel(s.body, {title:'Validation applied to every row',
    hint:'rejected rows are returned, accepted rows are created'});
  const rbox = mkFrame('rules', {dir:'V', gap:0, pad:[12,16,12,16]});
  add(rc, rbox, {hFill:true});
  BULK_RULES.forEach(function(r, i){
    const row = mkFrame('rule', {dir:'H', gap:9, align:'CENTER', pad:[6,0,6,0],
      stroke:C.line2, sides:[0,0, i === BULK_RULES.length - 1 ? 0 : 1, 0]});
    add(rbox, row, {hFill:true});
    add(row, svgIcon(I.check, 14, C.green, 2.4));
    add(row, mkText(r, {size:12.5, lh:17, color:C.ink}), {hFill:true});
  });
  renderBlocks(s.body, [{t:'banner', tone:'warn',
    title:'2 rows rejected — nothing was created for them',
    body:'Accepted rows are created immediately. Rejected rows are returned with the failing rule so the file can be corrected and re-uploaded.'}], 'desktop');
  dpanel(s.body, {title:'Rejected rows', hint:'2', parts:[{t:'table',
    cols:[{h:'Row', w:70}, {h:'Value', w:220}, {h:'Rule that failed', w:428, grow:true}],
    rows:[
      {state:'blocked', cells:[
        {v:'4', mono:true},
        {v:'1FUJGLDR5CLBP8834', mono:true},
        {v:'Duplicate VIN — already registered to TRK-001 (CO-10)'}
      ]},
      {state:'blocked', cells:[
        {v:'7', mono:true},
        {v:'CALIF', mono:true},
        {v:'plate_state must be a two-letter code (CO-10)'}
      ]}
    ]}]});
  renderBlocks(s.body, [{t:'note', tone:'amber',
    body:'Re-upload only the corrected rows — accepted rows are not duplicated on a second run.'}], 'desktop');
  mkFoot(s.sheet, [{t:'Close'}, {t:'Download template'},
    {t:'Accept 6 valid rows', kind:'primary'}]);
  return mkOverlay('F6 Form — Bulk upload', s.sheet);
}

/* ============================ E. ERR-GEN STATES ============================ */
/* S1 — ERR-GEN-003 / HTTP 503, rendered inline where the page data would be */
function buildS1(){
  const f = mkPageFrame('S1 State — Error 503', 'Dashboard',
    'ERR-GEN-003 — the console must say so when the API is unreachable, not render stale data.');
  ppanel(f, {title:'Overview', hint:'live', parts:[{t:'empty', kind:'error',
    title:'Unable to connect to server. Please try again later.',
    body:'The console could not reach the mySHIPR API. Nothing on this page is live — no cached figures are shown, because a stale dispatch board is worse than an empty one.',
    code:'ERR-GEN-003 · HTTP 503', action:'Retry'}]});
  return f;
}
/* S2 — ERR-GEN-002 / HTTP 403, deniedState('FLEET') for the Dispatcher role */
function buildS2(){
  const f = mkPageFrame('S2 State — Denied 403', 'All Vehicles',
    'Auth Services BRD V3 — the Role Permission Matrix decides what each role may even see.');
  ppanel(f, {title:'Fleet', hint:'8 vehicles', parts:[{t:'empty', kind:'denied',
    title:'You do not have permission to access this resource',
    body:'The Dispatcher role holds no rights over Fleet & Truck Management. Switch role in the top bar to see how the console changes.',
    code:'ERR-GEN-002 · HTTP 403 · category FLEET'}]});
  return f;
}
/* S3 — ERR-GEN-001 / HTTP 401, simSessionExpired() opens it as a drawer */
function buildS3(){
  const s = mkSheet('Session expired',
    'Auth Services BRD V3 — re-authentication required');
  dpanel(s.body, {parts:[{t:'empty', kind:'error',
    title:'Invalid email or password. Please try again.',
    body:'Your session was revoked or has expired. Sign in again to continue. Repeated failures lock the account per the organisation lockout policy under Settings → Sessions.',
    code:'ERR-GEN-001 · HTTP 401'}]});
  mkFoot(s.sheet, [{t:'Close'}, {t:'Sign in again', kind:'primary'}]);
  return mkOverlay('S3 State — Session expired 401', s.sheet);
}
/* S4 — ERR-GEN-004 / HTTP 415, the rejected upload */
function buildS4(){
  const s = mkSheet('Upload rejected',
    'CO-07 and Master Data §5 — PDF, JPG and PNG only');
  dropZone(s.body, 'Choose a CSV or XLSX file',
    'Any other format is rejected with 415 — File format not supported. Please upload PDF, JPG, or PNG.');
  dpanel(s.body, {parts:[{t:'empty', kind:'error',
    title:'File format not supported. Please upload PDF, JPG, or PNG.',
    body:'fleet_export.numbers was not accepted. CO-07 and Master Data §5 allow PDF, JPG and PNG only.',
    code:'ERR-GEN-004 · HTTP 415', action:'Choose another file'}]});
  mkFoot(s.sheet, [{t:'Close'}, {t:'Upload file', kind:'primary'}]);
  return mkOverlay('S4 State — Upload rejected 415', s.sheet);
}
/* S5 — loadingState(4): four .skel bars at 100 / 93 / 86 / 79 % */
function buildS5(){
  const f = mkPageFrame('S5 State — Loading', 'All Vehicles',
    'loadingState() — skeleton rows hold the layout while the request is in flight.');
  const card = ppanel(f, {title:'Fleet', hint:'loading…'});
  const box = mkFrame('skeletons', {dir:'V', gap:11, pad:[16,16,16,16]});
  add(card, box, {hFill:true});
  const inner = PAGE_INNER - 34;
  [100, 93, 86, 79].forEach(function(p){
    const bar = mkFrame('skel', {dir:'V', h:12, radius:5, fill:C.line2});
    add(box, bar, {hFix: Math.round(inner * p / 100)});
  });
  return f;
}

/* ============================ RUN ============================ */
const OV_PAGE = figma.currentPage;
/* keep the new section clear of Desktop + Responsive, which sit above it */
let ovBottom = 0;
OV_PAGE.children.forEach(function(n){
  if (n.type !== 'SECTION') return;
  if (n.name !== 'Desktop' && n.name !== 'Responsive') return;
  const bb = n.absoluteBoundingBox;
  const bot = bb ? (n.y + bb.height) : (n.y + n.height);
  if (bot > ovBottom) ovBottom = bot;
});
if (!ovBottom) ovBottom = 12000;
const OV_Y = Math.ceil(ovBottom) + 400;
const OV_SEC = getOrMakeSection(OV_PAGE, 'Overlays', 0, OV_Y);

const OV_NAMES = [
  'W1 Assign — Truck', 'W2 Assign — Trailer', 'W3 Assign — Driver', 'W4 Assign — Confirm',
  'D1 Drawer — Truck', 'D2 Drawer — Trailer', 'D3 Drawer — Driver', 'D4 Drawer — Load',
  'D5 Drawer — Payment details',
  'F1 Form — Register truck', 'F2 Form — Add yard', 'F3 Form — Add driver',
  'F4 Form — Invite user', 'F5 Form — Create role', 'F6 Form — Bulk upload',
  'S1 State — Error 503', 'S2 State — Denied 403', 'S3 State — Session expired 401',
  'S4 State — Upload rejected 415', 'S5 State — Loading'
];
/* idempotent: drop any frame we are about to rebuild */
OV_SEC.children.slice().forEach(function(n){
  if (OV_NAMES.indexOf(n.name) > -1) safe(function(){ n.remove(); });
});

const OV_BUILDERS = [buildW1, buildW2, buildW3, buildW4,
  buildD1, buildD2, buildD3, buildD4, buildD5,
  buildF1, buildF2, buildF3, buildF4, buildF5, buildF6,
  buildS1, buildS2, buildS3, buildS4, buildS5];

const OV_GAP = 120;
const OV_MADE = [];
let ovX = 0, ovRowTop = 0, ovRowMax = 0;
for (let ovi = 0; ovi < OV_BUILDERS.length; ovi++){
  if (ovi % 6 === 0 && ovi > 0){
    ovRowTop += ovRowMax + OV_GAP;
    ovRowMax = 0; ovX = 0;
  }
  const node = OV_BUILDERS[ovi]();
  placeInSection(OV_SEC, node, ovX, ovRowTop);
  ovX += DESK_W + OV_GAP;
  if (node.height > ovRowMax) ovRowMax = node.height;
  OV_MADE.push(node.name);
}
/* sections do not auto-grow — size to contents */
fitSection(OV_SEC, 120);

RESULT = {
  section: 'Overlays',
  sectionY: OV_Y,
  size: Math.round(OV_SEC.width) + 'x' + Math.round(OV_SEC.height),
  frames: OV_MADE.length,
  names: OV_MADE
};

  report = 'OVERLAY ' + JSON.stringify(RESULT).substring(0, 150);
} catch (err) { report = 'FAIL-OVERLAY ' + (err && err.message ? err.message : String(err)).substring(0, 140); }
try {
  var p3 = null;
  figma.root.children.forEach(function(p){ if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
