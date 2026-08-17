import json, io, os
HERE = os.path.dirname(os.path.abspath(__file__))
base = io.open(HERE + '/_base.js', encoding='utf-8').read()
s12  = json.load(io.open(HERE + '/specs12_patched.json', encoding='utf-8'))
s30  = json.load(io.open(HERE + '/specs.json',   encoding='utf-8'))

SEC = ['dashboard','fleet','drivers','loads','trips','ops','rr','yards','alerts','reports','earnings','settings']
allspecs = s12 + s30
allspecs.sort(key=lambda s: (SEC.index(s['key']), s.get('subIdx', 0)))
for s in allspecs:
    if 'actions' in s:
        s['actions'] = [a for a in s['actions'] if not str(a.get('t','')).lower().startswith('read only')]
        if not s['actions']: del s['actions']

RUNNER = r"""
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
"""

BATCH = 14
for bi in range(0, len(allspecs), BATCH):
    chunk = allspecs[bi:bi + BATCH]
    n = bi // BATCH + 1
    js = (base + "\nconst SCREENS = " + json.dumps(chunk, ensure_ascii=False) + ";\n"
          + "const OFFSET = %d;\n" % bi + RUNNER)
    body = ("(async () => {\nvar RESULT = null, report = 'start';\ntry {\n" + js +
            "\n  report = 'RESP%d n=' + RESULT.n + ' badTablet=' + RESULT.badT + ' badMobile=' + RESULT.badM + ' secKids=' + RESULT.secKids;\n" % n +
            "} catch (err) { report = 'FAIL%d ' + (err && err.message ? err.message : String(err)).substring(0, 140); }\n" % n +
            "try {\n  var p3 = null;\n  figma.root.children.forEach(function(p){ if (p.name.indexOf('03 Prototype') === 0) p3 = p; });\n"
            "  await figma.setCurrentPageAsync(p3);\n  if (p3 && p3.children.length) p3.children[0].name = report;\n} catch (e) {}\nconsole.log(report);\n})();\n")
    p = HERE + '/resp%d.js' % n
    io.open(p, 'w', encoding='utf-8').write(body)
    print('resp%d.js  screens=%d  chars=%d' % (n, len(chunk), len(body)))
print('total screens:', len(allspecs))
