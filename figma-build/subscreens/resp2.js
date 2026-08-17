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
function gradTL(a, b){
  const ca = rgb(a), cb = rgb(b);
  return [{type:'GRADIENT_LINEAR',
    gradientTransform: [[0.7071, 0.7071, -0.2071], [-0.7071, 0.7071, 0.5]],
    gradientStops: [{position:0, color:{r:ca.r, g:ca.g, b:ca.b, a:1}},
                    {position:1, color:{r:cb.r, g:cb.g, b:cb.b, a:1}}]}];
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
  if (dot){
    dot.visible = !plain;
    safe(() => { dot.fills = solid(t.fg); });
    /* shape carries severity too, so the chip still reads without colour:
       red = square, amber = diamond, everything else = circle */
    safe(() => {
      dot.rotation = 0;
      if (tone === 'red')        dot.cornerRadius = 1;
      else if (tone === 'amber'){ dot.cornerRadius = 1; dot.rotation = 45; }
      else                        dot.cornerRadius = 3;
    });
  }
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
/* The brand block, the org card and the footer are identical on every screen, so
   they are components. The nav list is not — it differs per screen — and its rows
   are already Sidebar/Item and Sidebar/SubItem instances. */
function buildBrandNode(){
  const brand = mkFrame('brand', {dir:'H', gap:10, pad:[14,16,11,16], align:'CENTER', stroke:C.chromeLine, sides:[0,0,1,0], w:SIDE_W});
  const mark = mkFrame('mark', {dir:'V', w:34, h:34, radius:8, fill:C.brand, align:'CENTER', just:'CENTER'});
  safe(() => { mark.fills = gradTL(C.brand, '#0c5c38'); });
  safe(() => { mark.effects = [{type:'INNER_SHADOW', color:{r:0.16,g:0.36,b:0.27,a:1}, offset:{x:0,y:0}, radius:0, spread:1, visible:true, blendMode:'NORMAL'}]; });
  add(mark, svgIcon(I.truck, 20, '#daffe9', 1.8)); add(brand, mark);
  add(brand, mkText('×', {font:F.dispSemi, size:15, lh:20, color:C.inkInv2}));
  const m2 = mkFrame('mark2', {dir:'V', w:34, h:34, radius:8, fill:'#22304a', align:'CENTER', just:'CENTER'});
  safe(() => { m2.fills = gradTL('#3a4c66', '#22304a'); });
  add(m2, mkText('AF', {font:F.dispBold, size:13, lh:17, color:'#cdd7e6'})); add(brand, m2);
  const bt = mkFrame('bt', {dir:'V', gap:2});
  add(brand, bt, {hFill:true});
  add(bt, mkText('mySHIPR', {font:F.dispBold, size:19, lh:19, ls:0.5, color:C.white, name:'product'}), {hFill:true});
  add(bt, mkText('Apex Freight LLC', {size:10, lh:13, ls:0.6, color:C.inkInv2, name:'carrier'}), {hFill:true});
  return brand;
}
function buildFootNode(){
  const foot = mkFrame('sidefoot', {dir:'V', pad:[11,14,11,14], stroke:C.chromeLine, sides:[1,0,0,0], w:SIDE_W});
  add(foot, mkText('Reference build. Terminology and value sets follow Master Data, Carrier Onboarding CO-01…CO-30, Auth Services BRD V3 and Shipment Execution OPS-01…OPS-12. Records are illustrative.',
    {size:10, lh:15, color:C.footInk, name:'note'}), {hFill:true});
  return foot;
}
function buildSidebarNode(activeKey, activeSub){
  const side = mkFrame('Sidebar', {dir:'V', gap:0, fill:C.chrome, stroke:C.chromeLine, sides:[0,1,0,0], w:SIDE_W, clip:true});
  const brandI = safe(() => inst('Sidebar/Brand'));
  add(side, brandI || buildBrandNode(), {hFill:true});
  const orgI = safe(() => inst('Sidebar/OrgCard'));
  add(side, orgI || orgCard(), {hFill:true});
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
  const footI = safe(() => inst('Sidebar/Footer'));
  add(side, footI || buildFootNode(), {hFill:true});
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
function renderTableAsCards(card, t, innerW){
  const cols = t.cols;
  const box = mkFrame('cards', {dir:'V', gap:8, pad:[10,12,12,12]});
  add(card, box, {hFill:true});
  /* the first non-checkbox column is the record's identity */
  let idIx = 0;
  for (let i = 0; i < cols.length; i++){
    const c0 = t.rows.length ? t.rows[0].cells[i] : null;
    if (!(c0 && c0.box)) { idIx = i; break; }
  }
  t.rows.forEach(r => {
    const cd = mkFrame('row card', {dir:'V', gap:7, pad:[11,12,12,12], radius:10,
      fill: r.state === 'blocked' ? C.rowBlocked : C.panel, stroke:C.line, clip:true});
    add(box, cd, {hFill:true});

    const idc = r.cells[idIx] || {};
    const head = mkFrame('hd', {dir:'H', gap:8, align:'CENTER'});
    add(cd, head, {hFill:true});
    const idt = mkFrame('idt', {dir:'V', gap:1});
    add(head, idt, {hFill:true});
    add(idt, mkText(String(idc.v || '—'), {font:F.semi, size:13.5, lh:18, color:C.ink}), {hFill:true});
    if (idc.sub) add(idt, mkText(String(idc.sub), {font:F.mono, size:10.5, lh:14, color:C.ink3}), {hFill:true});
    /* the first chip in the row rides up next to the identity — it is the status */
    for (let i = 0; i < r.cells.length; i++){
      if (r.cells[i] && r.cells[i].chip){
        const ch = inst('Chip/Status', {tone:r.cells[i].chip.tone, style:r.cells[i].chip.plain ? 'plain' : 'solid-bg'});
        if (ch){ setChip(ch, r.cells[i].chip.tone, r.cells[i].chip.t, r.cells[i].chip.plain); add(head, ch); }
        break;
      }
    }

    /* remaining fields as label / value pairs, capped so the card stays scannable */
    let shown = 0, hidden = 0;
    for (let i = 0; i < cols.length; i++){
      const c = r.cells[i] || {};
      if (i === idIx || c.box) continue;
      const label = (cols[i].h || '').trim();
      let val = '';
      if (c.chip) val = c.chip.t;
      else if (c.bar) val = String(c.bar.v || '');
      else if (c.btns) continue;
      else val = String(c.v == null ? '' : c.v);
      if (!label || !val || val === '—') continue;
      if (shown >= 5) { hidden++; continue; }
      const rw = mkFrame('f', {dir:'H', gap:10, align:'MIN'});
      add(cd, rw, {hFill:true});
      add(rw, mkText(label, {font:F.semi, size:9.5, lh:14, ls:0.7, color:C.ink3, case:'UPPER'}), {hFix:104});
      add(rw, mkText(val + (c.sub ? ' · ' + c.sub : ''), {size:12, lh:16, color:C.ink}), {hFill:true});
      shown++;
    }

    const acts = mkFrame('acts', {dir:'H', gap:8, wrap:true, crossGap:8, pad:[3,0,0,0]});
    add(cd, acts, {hFill:true});
    let placed = 0;
    r.cells.forEach(c => {
      if (!c || !c.btns) return;
      c.btns.forEach(b => {
        if (placed >= 2) return;
        const bi = inst('Button', {kind:b.kind || 'secondary', size:'sm', state:'default'});
        if (bi){ setBtn(bi, b.t, b.kind || 'secondary'); add(acts, bi); placed++; }
      });
    });
    if (hidden > 0){
      const more = inst('Button', {kind:'secondary', size:'sm', state:'default'});
      if (more){ setBtn(more, 'View details (' + hidden + ' more)', 'secondary'); add(acts, more); placed++; }
    }
    if (!placed) acts.visible = false;
  });
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
    else if (part.t === 'table'){ if (mode === 'mobile') renderTableAsCards(card, part, innerW); else renderTable(card, part, innerW, mode); }
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
    else if (part.t === 'photos'){
      const g = mkFrame('photoblk', {dir:'H', gap:10, wrap:true, crossGap:10, pad:[12,16,14,16]});
      add(card, g, {hFill:true});
      const per = mode === 'desktop' ? 4 : (mode === 'tablet' ? 3 : 2);
      const tw = Math.floor((innerW - 32 - 10 * (per - 1)) / per);
      part.tiles.forEach(cap => {
        const ph = safe(() => inst('Photo Tile'));
        if (ph){ add(g, ph); fixW(ph, tw); setText(ph, 'caption', cap); }
        else {
          const f = mkFrame('photo', {dir:'V', h:Math.round(tw * 0.75), radius:8, fill:'#e6ebf1', just:'MAX', clip:true});
          add(g, f); fixW(f, tw);
          const cp = mkFrame('pl2', {dir:'H', pad:[6,8,6,8], fill:'#0f141d'});
          add(f, cp, {hFill:true});
          add(cp, mkText(cap, {size:10, lh:13, color:C.white}), {hFill:true});
        }
      });
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
      /* rows of N with FILL children, not a wrap of fixed pixels — this is what
         makes the frame genuinely reflow when its width changes */
      const per = mode === 'desktop' ? 5 : (mode === 'tablet' ? 3 : 2);
      const strip = mkFrame('pulse', {dir:'V', gap:1, fill:C.line, stroke:C.line, radius:10, clip:true});
      add(parent, strip, {hFill:true});
      for (let i = 0; i < b.cells.length; i += per){
        const line = mkFrame('pulse row', {dir:'H', gap:1});
        add(strip, line, {hFill:true});
        const slice = b.cells.slice(i, i + per);
        slice.forEach(c => {
          const pc = inst('Pulse Cell');
          add(line, pc, {hFill:true});
          setText(pc, 'value', c.n);
          setText(pc, 'label', c.label);
          const dot = pc.findOne(n => n.name === 'dot');
          if (dot) safe(() => { dot.fills = solid(TONE[c.tone] ? TONE[c.tone].solid : C.green); });
        });
        for (let k = slice.length; k < per; k++){
          add(line, mkFrame('spacer', {dir:'V', fill:C.panel}), {hFill:true});
        }
      }
    }
    else if (b.t === 'kpi'){
      const per = mode === 'desktop' ? Math.min(b.cards.length, 6) : (mode === 'tablet' ? 2 : 1);
      const stack = mkFrame('kpi', {dir:'V', gap:16});
      add(parent, stack, {hFill:true});
      for (let i = 0; i < b.cards.length; i += per){
        const row = mkFrame('kpi row', {dir:'H', gap:16, align:'MIN'});
        add(stack, row, {hFill:true});
        const slice = b.cards.slice(i, i + per);
        slice.forEach(c => {
          const k = inst('KPI Card', {tone: c.tone || 'default'});
          add(row, k, {hFill:true});
          setText(k, 'label', c.label);
          setText(k, 'value', c.value);
          const sm = k.findOne(n => n.type === 'TEXT' && n.name === 'value-small');
          if (sm){ if (c.small){ sm.visible = true; sm.characters = c.small; } else sm.visible = false; }
          setText(k, 'sub', c.sub);
        });
        for (let k2 = slice.length; k2 < per; k2++){
          add(row, mkFrame('spacer', {dir:'V'}), {hFill:true});
        }
      }
    }
    else if (b.t === 'cols'){
      const stack = mode === 'desktop' ? 'H' : 'V';
      const row = mkFrame('grid', {dir:stack, gap:16, align:'MIN'});
      add(parent, row, {hFill:true});
      const total = b.ratio.reduce((a, x) => a + x, 0);
      b.cols.forEach((p, i) => {
        /* equal ratios can FILL and therefore reflow; an uneven split (1.6:1)
           cannot be expressed by Figma's layoutGrow, so it stays measured */
        const even = b.ratio.every(x => x === b.ratio[0]);
        const w = mode === 'desktop' ? Math.round((cw - 16 * (b.cols.length - 1)) * b.ratio[i] / total) : null;
        const holder = mkFrame('col', {dir:'V', gap:16});
        add(row, holder, (mode === 'desktop' && !even) ? {hFix: w} : {hFill:true});
        const pw = (mode === 'desktop' && !even) ? w : null;
        (Array.isArray(p) ? p : [p]).forEach(pp => renderPanel(holder, pp, pw, mode));
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

const SCREENS = [{"key": "loads", "subIdx": 2, "nav": "Loads", "sub": "In Execution", "frame": "04.3 Loads — In Execution", "title": "In Execution", "desc": "Loads with assets committed and moving. Per-stop status, live position and recurring cycle counts.", "blocks": [{"t": "panel", "title": "In Execution", "parts": [{"t": "table", "cols": [{"h": "LOAD", "w": 151}, {"h": "LANE", "w": 197}, {"h": "EQUIPMENT", "w": 182}, {"h": "STATUS", "w": 120}, {"h": "TRUCK", "w": 68}, {"h": "TRAILER", "w": 68}, {"h": "DRIVER", "w": 90}, {"h": "PROGRESS", "w": 136}, {"h": "RATE", "w": 68}, {"h": "", "w": 68, "grow": true}], "rows": [{"cells": [{"v": "SHP-FTL-10005", "mono": true, "b": true, "hi": true, "sub": "FTL - Standard Goods", "subMono": true}, {"v": "San Jose Tracy", "sub": "95112", "subMono": true}, {"v": "Dry Van"}, {"chip": {"tone": "amber", "t": "In Transit"}}, {"v": "001", "mono": true}, {"v": "011", "mono": true}, {"v": "Marcus Reyes"}, {"bar": {"pct": 62, "tone": "amber", "v": "62%"}}, {"v": "$1,960"}, {"v": "—"}]}, {"cells": [{"v": "SHP-LTL-10002", "mono": true, "b": true, "hi": true, "sub": "LTL - Multiple Goods", "subMono": true}, {"v": "Sacramento San Jose", "sub": "95814", "subMono": true}, {"v": "Dry Van"}, {"chip": {"tone": "amber", "t": "In Transit"}}, {"v": "003", "mono": true}, {"v": "016", "mono": true}, {"v": "Priya Nair"}, {"bar": {"pct": 48, "tone": "amber", "v": "48%"}}, {"v": "$2,740"}, {"v": "—"}]}, {"cells": [{"v": "SHP-RCR-10005", "mono": true, "b": true, "hi": true, "sub": "Dump Truck", "subMono": true}, {"v": "Fresno Quarry Modesto Site", "sub": "2 stops · Gravel"}, {"v": "Dump Truck (Articulated)"}, {"chip": {"tone": "blue", "t": "At Delivery/Dump"}}, {"v": "005", "mono": true}, {"v": "—", "sub": "N/A", "subMono": true}, {"v": "Tyler Brooks"}, {"v": "—", "sub": "Trip 3 of 20 today"}, {"v": "$132,300"}, {"v": "—"}]}]}], "hint": "3 loads"}, {"t": "legend", "items": ["Shipment Execution OPS-01…OPS-12", "Master Data — Shipment Status (16 states)", "Super Set — per-stop execution data", "Notification Types CR-007 / FTL-01 / DT-001"]}]}, {"key": "loads", "subIdx": 3, "nav": "Loads", "sub": "POD & Close-out", "frame": "04.4 Loads — POD & Close-out", "title": "POD & Close-out", "desc": "Proof of delivery captured by the driver, reviewed here before the load is closed. POD gates close-out and opens the payment sequence (LED-05).", "blocks": [{"t": "panel", "title": "SHP-FTL-10003 · POD review", "parts": [{"t": "photos", "tiles": ["Driver selfie · POD-006", "Truck photo 1 of 2", "Truck photo 2 of 2", "Signature — K. Alvarado"]}, {"t": "kv", "rows": [{"k": "GPS at submission", "v": "37.7397, -121.4252 POD-007 auto-captured"}, {"k": "Signature", "v": "K. Alvarado"}, {"k": "Damage notes", "v": "None reported"}, {"k": "Photos", "v": "1 selfie + 2 truck photos Count valid", "chip": {"tone": "green", "t": "Count valid"}}, {"k": "Receipts", "v": "1 uploaded · AI-classified POD-008 / DT-26"}, {"k": "Delivered", "v": "2026-07-23 16:42PDT"}, {"k": "Driver", "v": "Rosa Martinez"}, {"k": "Truck / trailer", "v": "002 · 012"}]}, {"t": "text", "lines": [], "btns": [{"t": "Confirm POD & close out", "kind": "secondary"}, {"t": "Request resubmission", "kind": "secondary"}]}], "hint": "Captured 2026-07-23 16:42 PDT"}, {"t": "legend", "items": ["Driver BRD POD-001…008, DT-25, DT-26", "Auth Services BRD V3 — POD category", "Master Data POD event sequences", "Ledger LED-05", "Carrier View SHP-006"]}]}, {"key": "loads", "subIdx": 4, "nav": "Loads", "sub": "Completed", "frame": "04.5 Loads — Completed", "title": "Completed", "desc": "Delivered loads with POD captured and close-out complete.", "blocks": [{"t": "panel", "title": "Completed", "parts": [{"t": "table", "cols": [{"h": "LOAD", "w": 213}, {"h": "LANE", "w": 202}, {"h": "EQUIPMENT", "w": 95}, {"h": "STATUS", "w": 128}, {"h": "TRUCK", "w": 71}, {"h": "TRAILER", "w": 75}, {"h": "DRIVER", "w": 138}, {"h": "PROGRESS", "w": 85}, {"h": "RATE", "w": 71}, {"h": "", "w": 71, "grow": true}], "rows": [{"cells": [{"v": "SHP-FTL-10003", "mono": true, "b": true, "hi": true, "sub": "FTL - Standard Goods", "subMono": true}, {"v": "San Jose Tracy", "sub": "95112", "subMono": true}, {"v": "Dry Van"}, {"chip": {"tone": "green", "t": "POD Captured"}}, {"v": "002", "mono": true}, {"v": "012", "mono": true}, {"v": "Rosa Martinez"}, {"v": "—"}, {"v": "$1,780"}, {"v": "—"}]}, {"cells": [{"v": "SHP-LTL-10003", "mono": true, "b": true, "hi": true, "sub": "Multileg", "subMono": true}, {"v": "San Jose Sacramento", "sub": "95112", "subMono": true}, {"v": "Dry Van"}, {"chip": {"tone": "green", "t": "Completed"}}, {"v": "002", "mono": true}, {"v": "012", "mono": true}, {"v": "Rosa Martinez"}, {"v": "—"}, {"v": "$5,100"}, {"v": "—"}]}]}], "hint": "2 loads"}, {"t": "legend", "items": ["Shipment Execution OPS-01…OPS-12", "Master Data — Shipment Status (16 states)", "Super Set — per-stop execution data", "Notification Types CR-007 / FTL-01 / DT-001"]}]}, {"key": "loads", "subIdx": 5, "nav": "Loads", "sub": "History", "frame": "04.6 Loads — History", "title": "History", "desc": "Archived loads.", "blocks": [{"t": "panel", "title": "History", "parts": [{"t": "table", "cols": [{"h": "LOAD", "w": 155}, {"h": "LANE", "w": 227}, {"h": "EQUIPMENT", "w": 108}, {"h": "STATUS", "w": 108}, {"h": "TRUCK", "w": 72}, {"h": "TRAILER", "w": 84}, {"h": "DRIVER", "w": 155}, {"h": "PROGRESS", "w": 96}, {"h": "RATE", "w": 72}, {"h": "", "w": 72, "grow": true}], "rows": [{"cells": [{"v": "SHP-LTL-10003", "mono": true, "b": true, "hi": true, "sub": "Multileg", "subMono": true}, {"v": "San Jose Sacramento", "sub": "95112", "subMono": true}, {"v": "Dry Van"}, {"chip": {"tone": "green", "t": "Completed"}}, {"v": "002", "mono": true}, {"v": "012", "mono": true}, {"v": "Rosa Martinez"}, {"v": "—"}, {"v": "$5,100"}, {"v": "—"}]}]}], "hint": "1 loads"}, {"t": "legend", "items": ["Shipment Execution OPS-01…OPS-12", "Master Data — Shipment Status (16 states)", "Super Set — per-stop execution data", "Notification Types CR-007 / FTL-01 / DT-001"]}]}, {"key": "trips", "subIdx": 0, "nav": "Trips", "sub": "On going", "frame": "05 Trips — On going", "title": "Trips — On going", "desc": "A trip is one truck movement against a load. Every trip links to its load, and both follow the single Master Data lifecycle. Live position for every on-going trip is also on the Dashboard Overview.", "blocks": [{"t": "banner", "tone": "info", "title": "Open question (OC-4)", "body": "Shipments, Trips and Loads are modelled as three entities across three documents. This build treats the trip as a view over the load and adopts Master Data’s sixteen-state lifecycle, which also closes Carrier View OPEN-05."}, {"t": "panel", "title": "On going", "hint": "3 trips", "parts": [{"t": "table", "cols": [{"h": "TRIP", "w": 130}, {"h": "LOAD", "w": 150}, {"h": "LANE", "w": 320}, {"h": "TRUCK", "w": 90}, {"h": "DRIVER", "w": 150}, {"h": "ETA", "w": 190}, {"h": "PROGRESS", "w": 116, "grow": true}], "rows": [{"state": "clickable-hover", "cells": [{"v": "TRIP-58021", "mono": true, "hi": true, "b": true}, {"v": "SHP-FTL-10005", "mono": true}, {"v": "San Jose  →  Tracy", "b": true, "sub": "95112  →  95376", "subMono": true}, {"v": "001", "mono": true}, {"v": "Marcus Reyes"}, {"v": "2026-07-24 18:20", "mono": true, "sub": "PDT", "subMono": true}, {"bar": {"pct": 62, "tone": "amber", "v": "62%"}}]}, {"cells": [{"v": "TRIP-58022", "mono": true, "hi": true, "b": true}, {"v": "SHP-LTL-10002", "mono": true}, {"v": "Sacramento  →  San Jose", "b": true, "sub": "95814  →  95112", "subMono": true}, {"v": "003", "mono": true}, {"v": "Priya Nair"}, {"v": "2026-07-24 15:40", "mono": true, "sub": "PDT", "subMono": true}, {"bar": {"pct": 48, "tone": "amber", "v": "48%"}}]}, {"cells": [{"v": "TRIP-58024", "mono": true, "hi": true, "b": true}, {"v": "SHP-RCR-10005", "mono": true}, {"v": "Fresno  →  Modesto", "b": true, "sub": "93721  →  95350", "subMono": true}, {"v": "005", "mono": true}, {"v": "Tyler Brooks"}, {"v": "2026-07-24 11:05", "mono": true, "sub": "PDT", "subMono": true}, {"bar": {"pct": 74, "tone": "amber", "v": "74%"}}]}]}]}, {"t": "legend", "items": ["Master Data — Shipment Status", "Carrier View TRIP-01…03", "FTL Master Reference status machine"]}]}, {"key": "trips", "subIdx": 1, "nav": "Trips", "sub": "Scheduled", "frame": "05.2 Trips — Scheduled", "title": "Trips — Scheduled", "desc": "A trip is one truck movement against a load. Every trip links to its load, and both follow the single Master Data lifecycle.", "blocks": [{"t": "panel", "title": "Scheduled", "parts": [{"t": "table", "cols": [{"h": "TRIP", "w": 123}, {"h": "LOAD", "w": 160}, {"h": "LANE", "w": 173}, {"h": "TRUCK", "w": 148}, {"h": "DRIVER", "w": 210}, {"h": "ETA", "w": 235}, {"h": "PROGRESS", "w": 99, "grow": true}], "rows": [{"cells": [{"v": "TRIP-58026", "mono": true, "b": true, "hi": true}, {"v": "SHP-FTL-10001", "mono": true}, {"v": "San Jose Tracy", "sub": "95112", "subMono": true}, {"v": "—", "sub": "Not assigned"}, {"v": "—", "sub": "Resolves at login"}, {"v": "2026-07-25 18:00PDT", "mono": true}, {"bar": {"pct": 0, "tone": "amber", "v": "0%"}}]}]}], "hint": "1 trips"}, {"t": "note", "tone": "blue", "body": "Open question (OC-4): Shipments, Trips and Loads are modelled as three entities across three documents. This build treats the trip as a view over the load and adopts Master Data's sixteen-state lifecycle, which also closes Carrier View OPEN-05."}, {"t": "legend", "items": ["Master Data — Shipment Status", "Carrier View TRIP-01…03", "FTL Master Reference status machine"]}]}, {"key": "trips", "subIdx": 2, "nav": "Trips", "sub": "Upcoming", "frame": "05.3 Trips — Upcoming", "title": "Trips — Upcoming", "desc": "A trip is one truck movement against a load. Every trip links to its load, and both follow the single Master Data lifecycle.", "blocks": [{"t": "panel", "title": "Upcoming", "parts": [{"t": "table", "cols": [{"h": "TRIP", "w": 123}, {"h": "LOAD", "w": 160}, {"h": "LANE", "w": 173}, {"h": "TRUCK", "w": 148}, {"h": "DRIVER", "w": 210}, {"h": "ETA", "w": 235}, {"h": "PROGRESS", "w": 99, "grow": true}], "rows": [{"cells": [{"v": "TRIP-58027", "mono": true, "b": true, "hi": true}, {"v": "SHP-RCR-10002", "mono": true}, {"v": "Fresno Modesto", "sub": "93721", "subMono": true}, {"v": "—", "sub": "Not assigned"}, {"v": "—", "sub": "Resolves at login"}, {"v": "2026-07-28 17:00PDT", "mono": true}, {"bar": {"pct": 0, "tone": "amber", "v": "0%"}}]}]}], "hint": "1 trips"}, {"t": "note", "tone": "blue", "body": "Open question (OC-4): Shipments, Trips and Loads are modelled as three entities across three documents. This build treats the trip as a view over the load and adopts Master Data's sixteen-state lifecycle, which also closes Carrier View OPEN-05."}, {"t": "legend", "items": ["Master Data — Shipment Status", "Carrier View TRIP-01…03", "FTL Master Reference status machine"]}]}, {"key": "trips", "subIdx": 3, "nav": "Trips", "sub": "Completed", "frame": "05.4 Trips — Completed", "title": "Trips — Completed", "desc": "A trip is one truck movement against a load. Every trip links to its load, and both follow the single Master Data lifecycle.", "blocks": [{"t": "panel", "title": "Completed", "parts": [{"t": "table", "cols": [{"h": "TRIP", "w": 132}, {"h": "LOAD", "w": 172}, {"h": "LANE", "w": 243}, {"h": "TRUCK", "w": 79}, {"h": "DRIVER", "w": 172}, {"h": "ETA", "w": 243}, {"h": "PROGRESS", "w": 105, "grow": true}], "rows": [{"cells": [{"v": "TRIP-58015", "mono": true, "b": true, "hi": true}, {"v": "SHP-FTL-10003", "mono": true}, {"v": "San Jose Tracy", "sub": "95112", "subMono": true}, {"v": "002", "mono": true}, {"v": "Rosa Martinez"}, {"v": "2026-07-23 16:42PDT", "mono": true}, {"bar": {"pct": 100, "tone": "green", "v": "100%"}}]}, {"cells": [{"v": "TRIP-58009", "mono": true, "b": true, "hi": true}, {"v": "SHP-LTL-10003", "mono": true}, {"v": "San Jose Sacramento", "sub": "95112", "subMono": true}, {"v": "002", "mono": true}, {"v": "Rosa Martinez"}, {"v": "2026-07-20 12:10PDT", "mono": true}, {"bar": {"pct": 100, "tone": "green", "v": "100%"}}]}]}], "hint": "2 trips"}, {"t": "note", "tone": "blue", "body": "Open question (OC-4): Shipments, Trips and Loads are modelled as three entities across three documents. This build treats the trip as a view over the load and adopts Master Data's sixteen-state lifecycle, which also closes Carrier View OPEN-05."}, {"t": "legend", "items": ["Master Data — Shipment Status", "Carrier View TRIP-01…03", "FTL Master Reference status machine"]}]}, {"key": "trips", "subIdx": 4, "nav": "Trips", "sub": "Cancelled", "frame": "05.5 Trips — Cancelled", "title": "Trips — Cancelled", "desc": "A trip is one truck movement against a load. Every trip links to its load, and both follow the single Master Data lifecycle.", "blocks": [{"t": "panel", "title": "Cancelled", "parts": [{"t": "table", "cols": [{"h": "TRIP", "w": 136}, {"h": "LOAD", "w": 178}, {"h": "LANE", "w": 248}, {"h": "TRUCK", "w": 163}, {"h": "DRIVER", "w": 231}, {"h": "ETA", "w": 82}, {"h": "PROGRESS", "w": 110, "grow": true}], "rows": [{"cells": [{"v": "TRIP-58011", "mono": true, "b": true, "hi": true}, {"v": "SHP-FTL-10004", "mono": true}, {"v": "Salinas San Francisco", "sub": "93901", "subMono": true}, {"v": "—", "sub": "Not assigned"}, {"v": "—", "sub": "Resolves at login"}, {"v": "—"}, {"bar": {"pct": 0, "tone": "amber", "v": "0%"}}]}]}], "hint": "1 trips"}, {"t": "note", "tone": "blue", "body": "Open question (OC-4): Shipments, Trips and Loads are modelled as three entities across three documents. This build treats the trip as a view over the load and adopts Master Data's sixteen-state lifecycle, which also closes Carrier View OPEN-05."}, {"t": "legend", "items": ["Master Data — Shipment Status", "Carrier View TRIP-01…03", "FTL Master Reference status machine"]}]}, {"key": "ops", "subIdx": 0, "nav": "Driver Ops", "sub": "Detention", "frame": "06 Driver Ops — Detention", "title": "Detention", "desc": "Detention starts at geofence arrival (GPS-004) and runs against the free time agreed for that stop. Minutes past free time are billable and must be raised before the load closes out.", "actions": [{"t": "Export", "kind": "secondary"}], "blocks": [{"t": "banner", "tone": "warn", "title": "2 stops accruing detention right now", "body": "DET-003 notifies dispatch as free time expires. Detention is not recoverable once the load is closed out (LED-05), so raise it before POD confirmation."}, {"t": "kpi", "cards": [{"label": "Accruing now", "value": "2", "sub": "stops past free time", "tone": "amber"}, {"label": "Billable minutes", "value": "195", "sub": "across all open stops", "tone": "red"}, {"label": "Recoverable value", "value": "$254", "sub": "before close-out", "tone": "blue"}, {"label": "Within free time", "value": "1", "sub": "no charge", "tone": "grey"}]}, {"t": "panel", "title": "Detention events", "hint": "4", "parts": [{"t": "table", "cols": [{"h": "EVENT", "w": 95}, {"h": "STOP", "w": 110}, {"h": "DRIVER / TRUCK", "w": 125}, {"h": "ARRIVED", "w": 110}, {"h": "FREE TIME", "w": 85}, {"h": "ELAPSED", "w": 85}, {"h": "BILLABLE", "w": 85}, {"h": "AMOUNT", "w": 95}, {"h": "STATUS", "w": 150}, {"h": "ACTION", "w": 206, "grow": true}], "rows": [{"state": "blocked", "cells": [{"v": "DET-0041", "mono": true, "hi": true, "b": true, "sub": "SHP-FTL-10005", "subMono": true}, {"v": "Tracy, CA — Delivery"}, {"v": "Marcus Reyes", "b": true, "sub": "001", "subMono": true}, {"v": "2026-07-24 16:04", "mono": true, "sub": "PDT", "subMono": true}, {"v": "120 min"}, {"v": "3h 6m", "b": true}, {"v": "66 min", "b": true, "color": "#c23b3b"}, {"v": "$83", "b": true, "sub": "at $75/h"}, {"chip": {"tone": "amber", "t": "Accruing"}}, {"btns": [{"t": "Acknowledge", "kind": "secondary"}, {"t": "Raise as billable", "kind": "primary"}]}]}, {"state": "blocked", "cells": [{"v": "DET-0040", "mono": true, "hi": true, "b": true, "sub": "SHP-RCR-10005", "subMono": true}, {"v": "Fresno Quarry, CA — Pickup"}, {"v": "Tyler Brooks", "b": true, "sub": "005", "subMono": true}, {"v": "2026-07-24 06:12", "mono": true, "sub": "PDT", "subMono": true}, {"v": "60 min"}, {"v": "1h 37m", "b": true}, {"v": "37 min", "b": true, "color": "#c23b3b"}, {"v": "$56", "b": true, "sub": "at $90/h"}, {"chip": {"tone": "amber", "t": "Accruing"}, "chip2": {"tone": "green", "t": "Ack", "plain": true}}, {"btns": [{"t": "Raise as billable", "kind": "primary"}]}]}, {"cells": [{"v": "DET-0038", "mono": true, "hi": true, "b": true, "sub": "SHP-FTL-10003", "subMono": true}, {"v": "Tracy, CA — Delivery"}, {"v": "Rosa Martinez", "b": true, "sub": "002", "subMono": true}, {"v": "2026-07-23 15:10", "mono": true, "sub": "PDT", "subMono": true}, {"v": "120 min"}, {"v": "3h 32m", "b": true}, {"v": "92 min", "b": true, "color": "#c23b3b"}, {"v": "$115", "b": true, "sub": "at $75/h"}, {"chip": {"tone": "blue", "t": "Billable"}, "chip2": {"tone": "green", "t": "Ack", "plain": true}}, {}]}, {"cells": [{"v": "DET-0035", "mono": true, "hi": true, "b": true, "sub": "SHP-LTL-10003", "subMono": true}, {"v": "Stockton, CA — Delivery"}, {"v": "Rosa Martinez", "b": true, "sub": "002", "subMono": true}, {"v": "2026-07-19 13:22", "mono": true, "sub": "PDT", "subMono": true}, {"v": "120 min"}, {"v": "1h 44m", "b": true}, {"chip": {"tone": "green", "t": "None", "plain": true}}, {"v": "—"}, {"chip": {"tone": "green", "t": "Closed — within free time", "plain": true}, "chip2": {"tone": "green", "t": "Ack", "plain": true}}, {}]}]}]}, {"t": "note", "tone": "blue", "body": "Open question (OC-11): the Auth Services BRD V3 matrix gives Driver Operations to the Carrier Super Admin alone, yet every channel on these screens is addressed to dispatch — DET-005, SOS-003, MEC-002 and DSP-001…006 all name the dispatcher as the recipient. Either DRVOPS needs a Dispatcher column or the Driver BRD needs rewording. Sign in as Dispatcher to see the effect."}, {"t": "legend", "items": ["Driver BRD §4.14 DET-001…005", "Driver BRD DT-15", "GPS-003 / GPS-004 geofence arrival", "Ledger LED-05", "Notification Types DET-003"]}]}, {"key": "ops", "subIdx": 1, "nav": "Driver Ops", "sub": "Exceptions & Safety", "frame": "06.2 Driver Ops — Exceptions & Safety", "title": "Exceptions & Safety", "desc": "Route deviation, excessive idle, distance mismatch, speeding, breakdown and reefer deviation. CO-25 generates a red flag; this is where it lands.", "blocks": [{"t": "banner", "tone": "crit", "title": "3 open exceptions — 2 critical", "body": "A critical exception holds the asset out of dispatch until it is cleared. Acknowledging records who saw it; clearing records that it was resolved."}, {"t": "panel", "title": "Exception log", "parts": [{"t": "filters", "label": "TYPE", "chips": [{"t": "All", "on": true, "n": 6}, {"t": "Vehicle breakdown", "on": false, "n": 1}, {"t": "Reefer deviation", "on": false, "n": 1}, {"t": "Route deviation", "on": false, "n": 1}, {"t": "Excessive idle", "on": false, "n": 1}, {"t": "Speed limit exceeded", "on": false, "n": 1}, {"t": "Distance mismatch", "on": false, "n": 1}]}, {"t": "table", "cols": [{"h": "EVENT", "w": 93}, {"h": "TYPE", "w": 127}, {"h": "DRIVER", "w": 93}, {"h": "ASSET", "w": 93}, {"h": "TRIP", "w": 93}, {"h": "DETAIL", "w": 310}, {"h": "DETECTED", "w": 120}, {"h": "STATUS", "w": 93}, {"h": "ACTION", "w": 127, "grow": true}], "rows": [{"cells": [{"v": "EXC-0117", "mono": true, "b": true, "hi": true, "sub": "MEC-001", "subMono": true}, {"v": "Vehicle breakdown"}, {"v": "Rosa Martinez"}, {"v": "004", "mono": true}, {"v": "—", "sub": "—"}, {"v": "Driver reported hydraulic leak on the rear tipper ram. Asset moved to Out of Service; roadside assistance requested (MEC-003)."}, {"v": "2026-07-19 11:40PDT", "mono": true}, {"chip": {"tone": "grey", "t": "Open", "plain": true}}, {"btns": [{"t": "Acknowledge", "kind": "secondary"}, {"t": "Clear", "kind": "secondary"}]}], "state": "blocked"}, {"cells": [{"v": "EXC-0116", "mono": true, "b": true, "hi": true, "sub": "TRL-002", "subMono": true}, {"v": "Reefer deviation"}, {"v": "—", "sub": "System"}, {"v": "015", "mono": true}, {"v": "—", "sub": "—"}, {"v": "Set-point -2 °C, last reading +6 °C, unit offline at Tracy Staging. Sensor disconnect raised a maintenance alert (ALT-003)."}, {"v": "2026-07-24 04:15PDT", "mono": true}, {"chip": {"tone": "grey", "t": "Open", "plain": true}}, {"btns": [{"t": "Acknowledge", "kind": "secondary"}, {"t": "Clear", "kind": "secondary"}]}], "state": "blocked"}, {"cells": [{"v": "EXC-0115", "mono": true, "b": true, "hi": true, "sub": "CO-25", "subMono": true}, {"v": "Route deviation"}, {"v": "Priya Nair"}, {"v": "003", "mono": true}, {"v": "TRIP-58022", "mono": true}, {"v": "Vehicle 8.4 miles off the planned route near Elk Grove for 22 minutes. Red flag generated per CO-25 (ALT-002)."}, {"v": "2026-07-24 09:02PDT", "mono": true}, {"chip": {"tone": "grey", "t": "Acknowledged", "plain": true}}, {"btns": [{"t": "Clear", "kind": "secondary"}]}]}, {"cells": [{"v": "EXC-0114", "mono": true, "b": true, "hi": true, "sub": "CO-25", "subMono": true}, {"v": "Excessive idle"}, {"v": "Marcus Reyes"}, {"v": "001", "mono": true}, {"v": "TRIP-58021", "mono": true}, {"v": "Engine idle 41 minutes at a non-stop location. Threshold is 30 minutes (CO-25 exception monitoring)."}, {"v": "2026-07-24 10:18PDT", "mono": true}, {"chip": {"tone": "grey", "t": "Open", "plain": true}}, {"btns": [{"t": "Acknowledge", "kind": "secondary"}, {"t": "Clear", "kind": "secondary"}]}]}, {"cells": [{"v": "EXC-0113", "mono": true, "b": true, "hi": true, "sub": "DR-007", "subMono": true}, {"v": "Speed limit exceeded"}, {"v": "Marcus Reyes"}, {"v": "001", "mono": true}, {"v": "TRIP-58021", "mono": true}, {"v": "71 mph recorded in a 65 mph zone on I-580 for 3.1 miles (GPS-007 speed monitoring)."}, {"v": "2026-07-24 09:51PDT", "mono": true}, {"chip": {"tone": "green", "t": "Cleared", "plain": true}}, {"v": "—"}]}, {"cells": [{"v": "EXC-0111", "mono": true, "b": true, "hi": true, "sub": "CO-25", "subMono": true}, {"v": "Distance mismatch"}, {"v": "Rosa Martinez"}, {"v": "002", "mono": true}, {"v": "TRIP-58009", "mono": true}, {"v": "Odometer distance 214 mi against a planned 187 mi — 14% over. Reconcile before settlement."}, {"v": "2026-07-20 12:40PDT", "mono": true}, {"chip": {"tone": "green", "t": "Cleared", "plain": true}}, {"v": "—"}]}]}, {"t": "text", "lines": [], "btns": [{"t": "Acknowledge", "kind": "secondary"}, {"t": "Clear", "kind": "secondary"}, {"t": "Acknowledge", "kind": "secondary"}]}], "hint": "6 events"}, {"t": "note", "tone": "amber", "body": "Every row here is a channel the Driver BRD specifies: CO-25 exception monitoring, GPS-005 distance, GPS-007 / DR-007 speed, MEC-001…005 breakdown, TRL-002 / ALT-003 reefer. Clearing an exception is audited."}, {"t": "legend", "items": ["Carrier Onboarding CO-25", "Driver BRD §4.11 TRL-002, §4.13 MEC-001…005", "GPS-005 / GPS-007", "Notification Types ALT-002 / ALT-003 / DR-007"]}]}, {"key": "ops", "subIdx": 2, "nav": "Driver Ops", "sub": "Messages", "frame": "06.3 Driver Ops — Messages", "title": "Messages", "desc": "Two-way dispatch messaging with every driver on a live trip. Text, voice notes, documents and location, with read receipts — DSP-001…006, under two seconds delivery.", "blocks": [{"t": "panel", "title": "Conversation — Marcus Reyes", "parts": [{"t": "text", "lines": ["MR", "Loaded and rolling out of San Jose. Seal 88231 applied.", "Marcus Reyes · 09:41 PDT · read", "Y", "Copy. Consignee contact for Tracy is +1-1234567890, ask for the dock supervisor.", "You · 09:44 PDT · read", "MR", "Live location", "37.7016, -121.7680 · I-580 near Livermore, CA", "Marcus Reyes · 10:58 PDT · read", "MR", "Voice note · 0:14", "“Traffic on 580 eastbound, adding about 25 minutes to ETA.”", "Marcus Reyes · 11:02 PDT · read"], "btns": [{"t": "Play", "kind": "secondary"}, {"t": "Open", "kind": "secondary"}, {"t": "Send", "kind": "secondary"}]}], "hint": "+1 408 555 0231 · 001"}, {"t": "panel", "title": "Threads", "parts": [{"t": "list", "items": [{"sev": "info", "unread": false, "title": "Marcus Reyes", "body": "Voice note", "code": "", "time": "", "btn": null}, {"sev": "info", "unread": false, "title": "Tyler Brooks", "body": "Shared a document", "code": "", "time": "", "btn": null}]}], "hint": "2 drivers"}, {"t": "panel", "title": "Delivery", "parts": [{"t": "kv", "rows": [{"k": "Target delivery", "v": "< 2 seconds (DSP-006)"}, {"k": "Read receipts", "v": "", "chip": {"tone": "green", "t": "On"}}, {"k": "Retention", "v": "Message history is retained against the trip record"}]}], "hint": "DSP-006"}, {"t": "note", "tone": "blue", "body": "Open question (OC-11): the Auth Services BRD V3 matrix gives Driver Operations to the Carrier Super Admin alone, yet every channel on these screens is addressed to dispatch — DET-005, SOS-003, MEC-002 and DSP-001…006 all name the dispatcher as the recipient. Either DRVOPS needs a Dispatcher column or the Driver BRD needs rewording. Sign in as Dispatcher to see the effect."}, {"t": "legend", "items": ["Driver BRD §4.8 DSP-001…006", "Driver BRD DT-08", "Auth Services BRD V3 — DRVOPS"]}]}, {"key": "rr", "subIdx": 0, "nav": "RR", "sub": "Coming soon", "frame": "07 RR — Coming soon", "title": "RR — Rate & Auction Bidding", "desc": "Real-time load auctions, bidding and bid history for this carrier.", "blocks": [{"t": "panel", "parts": [{"t": "empty", "kind": "empty", "title": "Coming soon", "body": "Auction and bidding mechanics (lot visibility, live bidding, won / lost outcomes and bid history) are being redesigned as part of the TMS build and are not available in this console yet. The carrier-side inputs that decide auction eligibility — lanes, commodities, cost per mile and declared capacity — are managed under Settings → Capacity & Service Profile.", "action": "Go to Capacity & Service Profile"}]}, {"t": "legend", "items": ["6A Carrier Eligibility & Auction Targeting", "Carrier View RR-01…RR-06"]}]}, {"key": "yards", "subIdx": 0, "nav": "Yards", "sub": "All yards", "frame": "08 Yards — All yards", "title": "All Yards", "desc": "Yard address and geo-coordinates are captured at CO-14 — a yard without an address cannot be used for dispatch, and the coordinates drive geofencing, arrival detection and detention timing.", "actions": [{"t": "Add yard", "kind": "primary"}], "blocks": [{"t": "panel", "title": "Yards", "hint": "3", "parts": [{"t": "table", "cols": [{"h": "YARD", "w": 130}, {"h": "TYPE (CO-14)", "w": 100}, {"h": "SUBTYPE", "w": 130}, {"h": "ADDRESS", "w": 190}, {"h": "COORDINATES", "w": 150}, {"h": "TRUCK SLOTS", "w": 105}, {"h": "TRAILER SLOTS", "w": 110}, {"h": "GEOFENCE", "w": 95}, {"h": "STATUS", "w": 136, "grow": true}], "rows": [{"cells": [{"v": "001", "mono": true, "hi": true, "b": true, "sub": "San Jose Hub"}, {"v": "Owned"}, {"chip": {"tone": "grey", "t": "STAGING", "plain": true}}, {"v": "1180 Coleman Ave", "sub": "San Jose, CA 95110, USA"}, {"v": "37.3654,", "mono": true, "sub": "-121.9245", "subMono": true}, {"v": "33 / 40"}, {"v": "47 / 60"}, {"v": "300 m", "mono": true}, {"chip": {"tone": "green", "t": "active"}}]}, {"cells": [{"v": "002", "mono": true, "hi": true, "b": true, "sub": "Sacramento Depot"}, {"v": "Leased"}, {"chip": {"tone": "grey", "t": "DROP_AND_HOOK", "plain": true}}, {"v": "4400 Power Inn Rd", "sub": "Sacramento, CA 95826, USA"}, {"v": "38.5310,", "mono": true, "sub": "-121.4020", "subMono": true}, {"v": "12 / 25"}, {"v": "19 / 35"}, {"v": "250 m", "mono": true}, {"chip": {"tone": "green", "t": "active"}}]}, {"cells": [{"v": "003", "mono": true, "hi": true, "b": true, "sub": "Tracy Staging"}, {"v": "Shared"}, {"chip": {"tone": "grey", "t": "FUEL_STOP", "plain": true}}, {"v": "2400 Grant Line Rd", "sub": "Tracy, CA 95377, USA"}, {"v": "37.7255,", "mono": true, "sub": "-121.4380", "subMono": true}, {"v": "6 / 15"}, {"v": "8 / 20"}, {"v": "180 m", "mono": true}, {"chip": {"tone": "amber", "t": "maintenance"}}]}]}]}, {"t": "note", "tone": "amber", "body": "Yard type and status now use the CO-14 vocabulary — Owned / Leased / Shared and active / inactive / maintenance — rather than the database values PRIVATE / LEASED / SHARED / CROSS_DOCK and ACTIVE / INACTIVE / UNDER_MAINTENANCE / CLOSED, which could not store what onboarding captured."}, {"t": "legend", "items": ["CO-14 Yard onboarding", "Driver BRD GPS-003/004, DET-001/002"]}]}];
const OFFSET = 14;

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

  report = 'RESP2 n=' + RESULT.n + ' badTablet=' + RESULT.badT + ' badMobile=' + RESULT.badM + ' secKids=' + RESULT.secKids;
} catch (err) { report = 'FAIL2 ' + (err && err.message ? err.message : String(err)).substring(0, 140); }
try {
  var p3 = null;
  figma.root.children.forEach(function(p){ if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
