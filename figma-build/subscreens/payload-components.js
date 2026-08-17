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
