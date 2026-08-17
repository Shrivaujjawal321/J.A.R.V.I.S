 /* ===========================================================================
 * payload-responsive-nav.js
 * Off-canvas mobile navigation for the 84 responsive frames + full wiring.
 *
 * Concatenated AFTER _base.js by the caller. Body only — no wrapper.
 * Assumes: await loadFonts(); await adoptComponents(true); and
 *          figma.currentPage === the page named "02 Screens".
 *
 * Reproduces the console's own @media(max-width:920px) rules:
 *   .side  {position:fixed;top:0;bottom:0;left:0;width:min(300px,86vw);
 *           transform:translateX(-102%);box-shadow:14px 0 40px rgba(0,0,0,.35)}
 *   .side.open {transform:none}                -> the rail pinned at x = 0
 *   .sidescrim {position:fixed;inset:0;background:rgba(11,16,23,.52)}
 *   .menu  {display:grid}                      -> the hamburger, now wired
 *
 * Scripter constraints honoured: no regular-expression literals anywhere,
 * no figma.notify / closePlugin / console.error, no figma.currentPage
 * assignment, no figma.createPage, reactions only via setReactionsAsync,
 * every reaction call wrapped in try/catch.
 *
 * RUN IT IN THREE PASSES — set PASS to 1, then 2, then 3, running the file
 * once per value. Each pass owns one third of the 84 responsive frames and is
 * independently idempotent (it deletes and rebuilds only its own third).
 * ========================================================================== */

const PASS   = 2;          /* 1 | 2 | 3 */
const PASSES = 3;

const OPEN_SUFFIX = ' — Menu open';
const TAB_SUFFIX  = ' — Tablet 900';
const MOB_SUFFIX  = ' — Mobile 375';

const SCRIM_HEX = '#0b1017';   /* rgba(11,16,23,.52) */
const SCRIM_OP  = 0.52;
const RAIL_MAX  = 300;         /* min(300px, 86vw)   */
const RAIL_VW   = 0.86;
const OPEN_GAP  = 60;          /* gap under the closed counterpart */

const KEYS = ['dashboard','fleet','drivers','loads','trips','ops','rr','yards',
              'alerts','reports','earnings','settings'];

 /* --------- tiny string helpers (no regex — Scripter's parser rejects them) */
function endsWithStr(s, suf){
  if (typeof s !== 'string' || s.length < suf.length) return false;
  return s.substring(s.length - suf.length) === suf;
}
function stripSuffix(s, suf){ return endsWithStr(s, suf) ? s.substring(0, s.length - suf.length) : s; }

 /* --------- address from the frame-name prefix, exactly as 25-wire-all.js ---
   "07 RR — Coming soon — Tablet 900"      -> rr      / sub 0 / tablet
   "12.10 Settings — Capacity — Mobile 375"-> settings/ sub 9 / mobile        */
function addrOf(name){
  const head = String(name).split(' ')[0];
  const bits = head.split('.');
  const secIdx = parseInt(bits[0], 10);
  const subNum = bits.length > 1 ? parseInt(bits[1], 10) : 1;
  if (!secIdx || secIdx > 12 || secIdx < 1) return null;
  return { key: KEYS[secIdx - 1], sub: (subNum || 1) - 1, secIdx: secIdx };
}

 /* --------- reaction descriptors (same shape the desktop wiring uses) ------ */
function navAction(destId){
  return { trigger:{ type:'ON_CLICK' }, actions:[{ type:'NODE', destinationId:destId,
           navigation:'NAVIGATE', transition:null, preserveScrollPosition:false, resetVideoPosition:false }] };
}
function scrollAction(destId){
  return { trigger:{ type:'ON_CLICK' }, actions:[{ type:'NODE', destinationId:destId,
           navigation:'SCROLL_TO', transition:null, preserveScrollPosition:false, resetVideoPosition:false }] };
}

 /* --------- the hamburger: the only `tbtn` that is a direct child of row-1 -
   (buildTopBarNode does `if (!desk) add(r1, tbtn(I.menu))`; every other tbtn
   — bell / map / wifioff / lock — lives inside the nested `actions` frame).  */
function findHamburger(frame){
  const tb = frame.findOne(function(n){ return n.name === 'TopBar'; });
  if (!tb) return null;
  const r1 = tb.findOne ? tb.findOne(function(n){ return n.name === 'row-1'; }) : null;
  const host = r1 || tb;
  const kids = host.children || [];
  for (let i = 0; i < kids.length; i++) if (kids[i].name === 'tbtn') return kids[i];
  const all = tb.findAll(function(n){ return n.name === 'tbtn'; });   /* doc order: menu first */
  return all.length ? all[0] : null;
}

 /* --------- page + sections ------------------------------------------------ */
const pg = figma.currentPage;
let SEC_DESK = null, SEC_RESP = null;
pg.children.forEach(function(s){
  if (s.type !== 'SECTION') return;
  if (s.name === 'Desktop')    SEC_DESK = s;
  if (s.name === 'Responsive') SEC_RESP = s;
});
if (!SEC_RESP) throw new Error('Responsive section not found on ' + pg.name);

 /* --------- catalogue every CLOSED responsive frame ------------------------ */
const closed = [];      /* {frame, key, sub, w, rank}                          */
const byAddr = {};      /* "key/sub/t" | "key/sub/m" -> closed frame           */
const closedNames = {};
SEC_RESP.children.forEach(function(f){
  if (f.type !== 'FRAME') return;
  if (endsWithStr(f.name, OPEN_SUFFIX)) return;
  let w = null;
  if (endsWithStr(f.name, TAB_SUFFIX)) w = 't';
  else if (endsWithStr(f.name, MOB_SUFFIX)) w = 'm';
  if (!w) return;
  const a = addrOf(f.name);
  if (!a) return;
  byAddr[a.key + '/' + a.sub + '/' + w] = f;
  closedNames[f.name] = 1;
  closed.push({ frame:f, key:a.key, sub:a.sub, w:w,
                rank: a.secIdx * 10000 + a.sub * 10 + (w === 't' ? 0 : 1) });
});
closed.sort(function(a, b){ return a.rank - b.rank; });

 /* --------- this pass's third --------------------------------------------- */
const N     = closed.length;
const lo    = Math.floor(N * (PASS - 1) / PASSES);
const hi    = Math.floor(N * PASS / PASSES);
const slice = closed.slice(lo, hi);

 /* --------- idempotency: drop this pass's own "— Menu open" frames ---------
   (and, on PASS 1 only, any orphaned open frame whose closed twin is gone)   */
const mine = {};
slice.forEach(function(c){ mine[c.frame.name + OPEN_SUFFIX] = 1; });
let removed = 0;
SEC_RESP.children.slice().forEach(function(n){
  if (n.type !== 'FRAME' || !endsWithStr(n.name, OPEN_SUFFIX)) return;
  const base = stripSuffix(n.name, OPEN_SUFFIX);
  const orphan = (PASS === 1) && !closedNames[base];
  if (mine[n.name] || orphan){ if (safe(function(){ n.remove(); return 1; })) removed++; }
});

 /* --------- build + wire ---------------------------------------------------- */
let openFrames = 0, links = 0, failed = 0, missing = 0, scroll = 0,
    hamburgers = 0, scrims = 0, renamed = 0;
let firstErr = '';

function note(e){
  failed++;
  if (!firstErr) firstErr = String(e && e.message ? e.message : e).substring(0, 80);
}

for (let i = 0; i < slice.length; i++){
  const rec  = slice[i];
  const shut = rec.frame;

  /* --- 1. clone the closed frame ----------------------------------------- */
  const open = shut.clone();
  open.name = shut.name + OPEN_SUFFIX;
  const FW = open.width, FH = open.height;

  /* the clone must not shadow the rail's addressable controls */
  const stale = open.findAll(function(n){
    return typeof n.name === 'string' &&
           (n.name.indexOf('nav/') === 0 || n.name.indexOf('sub/') === 0);
  });
  stale.forEach(function(n){ n.name = 'closed-' + n.name; renamed++; });

  /* --- 2. place it directly beneath its closed counterpart, 60px gap ------ */
  const sb = SEC_RESP.absoluteBoundingBox, cb = shut.absoluteBoundingBox;
  if (sb && cb) placeInSection(SEC_RESP, open, cb.x - sb.x, (cb.y - sb.y) + cb.height + OPEN_GAP);
  else { SEC_RESP.appendChild(open); open.x = shut.x; open.y = shut.y + shut.height + OPEN_GAP; }

  /* --- 3. scrim — .sidescrim{position:fixed;inset:0;background:rgba(11,16,23,.52)} */
  const scrim = figma.createRectangle();
  scrim.name = 'sidescrim';
  safe(function(){ scrim.resize(FW, FH); });
  safe(function(){ scrim.fills = solid(SCRIM_HEX, SCRIM_OP); });
  scrim.strokes = [];
  open.appendChild(scrim);
  safe(function(){ scrim.layoutPositioning = 'ABSOLUTE'; });
  scrim.x = 0; scrim.y = 0;
  safe(function(){ scrim.constraints = { horizontal:'STRETCH', vertical:'STRETCH' }; });

  /* --- 4. the off-canvas rail — .side.open{transform:none} ---------------- */
  const railW = Math.min(RAIL_MAX, Math.round(FW * RAIL_VW));
  const built = buildSidebarNode(rec.key, rec.sub);
  const rail  = built.node;
  rail.name = 'Sidebar (off-canvas)';
  open.appendChild(rail);
  safe(function(){ rail.layoutPositioning = 'ABSOLUTE'; });
  safe(function(){ rail.primaryAxisSizingMode = 'FIXED'; rail.counterAxisSizingMode = 'FIXED'; });
  safe(function(){ rail.resize(railW, FH); });
  rail.x = 0; rail.y = 0;
  safe(function(){ rail.constraints = { horizontal:'MIN', vertical:'STRETCH' }; });
  safe(function(){
    rail.effects = [{ type:'DROP_SHADOW', color:{ r:0, g:0, b:0, a:0.35 },
                      offset:{ x:14, y:0 }, radius:40, spread:0, visible:true, blendMode:'NORMAL' }];
  });
  /* let the nav column absorb the slack so the side footer pins to the bottom */
  const navCol = rail.findOne(function(n){ return n.type === 'FRAME' && n.name === 'nav'; });
  if (navCol) safe(function(){ navCol.layoutSizingVertical = 'FILL'; });
  openFrames++;

  /* --- 5. hamburger on the CLOSED frame -> the open frame ----------------- */
  const burger = findHamburger(shut);
  if (!burger) missing++;
  else {
    try { await burger.setReactionsAsync([navAction(open.id)]); links++; hamburgers++; }
    catch (e){ note(e); }
  }

  /* --- 6. scrim on the OPEN frame -> back to the closed frame ------------- */
  try { await scrim.setReactionsAsync([navAction(shut.id)]); links++; scrims++; }
  catch (e){ note(e); }

  /* --- 7. every rail control -> the closed frame AT THE SAME WIDTH -------- */
  const header   = open.findOne(function(n){ return n.name === 'pagehd'; });
  const controls = rail.findAll(function(n){
    return typeof n.name === 'string' &&
           (n.name.indexOf('nav/') === 0 || n.name.indexOf('sub/') === 0);
  });
  for (let j = 0; j < controls.length; j++){
    const c = controls[j];
    const isNav = c.name.indexOf('nav/') === 0;
    const dest  = isNav ? byAddr[c.name.substring(4) + '/0/' + rec.w]
                        : byAddr[c.name.substring(4) + '/' + rec.w];
    if (!dest){ missing++; continue; }
    try {
      /* Figma rejects a NAVIGATE whose destination contains the trigger, so a
         control pointing at its own frame scrolls to that frame's pagehd. */
      if (dest.id === open.id){
        if (header){ await c.setReactionsAsync([scrollAction(header.id)]); links++; scroll++; }
        else missing++;
      } else {
        await c.setReactionsAsync([navAction(dest.id)]);
        links++;
      }
    } catch (e){ note(e); }
  }
}

 /* --------- sections do not auto-grow: refit, then keep clear of Desktop --- */
safe(function(){ fitSection(SEC_RESP, 80); });
let moved = false;
safe(function(){
  if (!SEC_DESK) return;
  const d = SEC_DESK.absoluteBoundingBox, r = SEC_RESP.absoluteBoundingBox;
  if (!d || !r) return;
  const clear = !(r.x >= d.x + d.width || r.x + r.width <= d.x ||
                  r.y >= d.y + d.height || r.y + r.height <= d.y);
  if (clear){ SEC_RESP.x = SEC_DESK.x; SEC_RESP.y = SEC_DESK.y + SEC_DESK.height + 320; moved = true; }
});

RESULT = {
  pass: PASS + '/' + PASSES,
  scope: lo + '..' + (hi - 1) + ' of ' + N,
  openFrames: openFrames,
  links: links,
  failed: failed,
  removed: removed,
  missing: missing,
  hamburgers: hamburgers,
  scrims: scrims,
  scrollTo: scroll,
  renamedStale: renamed,
  sectionMoved: moved,
  sectionSize: Math.round(SEC_RESP.width) + 'x' + Math.round(SEC_RESP.height),
  err: firstErr
};
