import json, io, os
HERE = os.path.dirname(os.path.abspath(__file__))
base  = io.open(HERE + '/_base.js', encoding='utf-8').read()
specs = json.load(io.open(HERE + '/specs.json', encoding='utf-8'))

# drop pseudo-actions that are really read-only badges, not buttons
for s in specs:
    if 'actions' in s:
        s['actions'] = [a for a in s['actions'] if not a['t'].lower().startswith('read only')]
        if not s['actions']: del s['actions']

RUNNER = r"""
await loadFonts();
await adoptComponents(true);
const pg = await getPage(PAGE.screens);
await figma.setCurrentPageAsync(pg);

let sec = null;
pg.children.forEach(function(s){ if (s.type === 'SECTION' && s.name === 'Desktop') sec = s; });
if (!sec) throw new Error('Desktop section not found');

/* idempotent — remove anything we are about to rebuild */
const names = SCREENS.map(function(s){ return s.frame; });
sec.children.slice().forEach(function(n){ if (names.indexOf(n.name) >= 0) safe(function(){ n.remove(); }); });

/* the original 12 are named "NN Label"; ours are "NN.M Label" — sit below them */
const PERROW = 6, GAPX = 120, GAPY = 220, X0 = 80;
let baseY = 80;
sec.children.forEach(function(n){ if (n.name.charAt(2) === ' ') baseY = Math.max(baseY, n.y + n.height); });
let rowY = baseY + GAPY;

const made = [];
let rowMax = 0;
for (let i = 0; i < SCREENS.length; i++){
  const col = i % PERROW;
  if (col === 0 && i > 0){ rowY += rowMax + GAPY; rowMax = 0; }
  const r = renderScreen(SCREENS[i], 'desktop');
  placeInSection(sec, r.frame, X0 + col * (DESK_W + GAPX), rowY);
  rowMax = Math.max(rowMax, r.frame.height);
  made.push(r.frame.name + '|' + Math.round(r.frame.height) + '|' + r.frame.findAll(function(n){ return n.type === 'INSTANCE'; }).length);
}
fitSection(sec, 80);
RESULT = { ok: made.length === SCREENS.length, added: made.length, made: made };
"""

js = base + "\nconst SCREENS = " + json.dumps(specs, ensure_ascii=False) + ";\n"
body = (
"(async () => {\n"
"var RESULT = null, report = 'start';\n"
"try {\n" + js + RUNNER +
"  report = 'BUILT n=' + RESULT.added + ' inst=' + RESULT.made.reduce(function(a,s){ return a + parseInt(s.split('|')[2],10); }, 0);\n"
"} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 150); }\n"
"try {\n"
"  var p3 = null;\n"
"  figma.root.children.forEach(function(p){ if (p.name.indexOf('03 Prototype') === 0) p3 = p; });\n"
"  await figma.setCurrentPageAsync(p3);\n"
"  if (p3 && p3.children.length) p3.children[0].name = report;\n"
"} catch (e) {}\n"
"console.log(report);\n"
"})();\n")
p = HERE + '/build-subscreens.js'
io.open(p, 'w', encoding='utf-8').write(body)
print('build-subscreens.js  screens=%d  chars=%d' % (len(specs), len(body)))
