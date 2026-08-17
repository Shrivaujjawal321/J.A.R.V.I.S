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
