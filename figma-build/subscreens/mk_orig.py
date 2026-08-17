import json, io, os
HERE = os.path.dirname(os.path.abspath(__file__))
base  = io.open(HERE + '/_base.js', encoding='utf-8').read()
specs = json.load(io.open(HERE + '/specs12_patched.json', encoding='utf-8'))

RUNNER = r"""
await loadFonts();
await adoptComponents(true);
const pg = await getPage(PAGE.screens);
await figma.setCurrentPageAsync(pg);
let sec = null;
pg.children.forEach(function(s){ if (s.type === 'SECTION' && s.name === 'Desktop') sec = s; });
if (!sec) throw new Error('Desktop section not found');

const names = SCREENS.map(function(s){ return s.frame; });
sec.children.slice().forEach(function(n){ if (names.indexOf(n.name) >= 0) safe(function(){ n.remove(); }); });

const made = [];
for (let i = 0; i < SCREENS.length; i++){
  const r = renderScreen(SCREENS[i], 'desktop');
  placeInSection(sec, r.frame, 80 + i * (DESK_W + 120), 80);
  made.push(r.frame.name + '|' + Math.round(r.frame.height));
}
fitSection(sec, 80);
RESULT = { n: made.length, tallest: made.map(function(m){ return parseInt(m.split('|')[1],10); }).sort(function(a,b){return b-a;})[0] };
"""

js = base + "\nconst SCREENS = " + json.dumps(specs, ensure_ascii=False) + ";\n" + RUNNER
body = ("(async () => {\nvar RESULT = null, report = 'start';\ntry {\n" + js +
        "\n  report = 'ORIG n=' + RESULT.n + ' tallest=' + RESULT.tallest;\n"
        "} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 150); }\n"
        "try {\n  var p3 = null;\n  figma.root.children.forEach(function(p){ if (p.name.indexOf('03 Prototype') === 0) p3 = p; });\n"
        "  await figma.setCurrentPageAsync(p3);\n  if (p3 && p3.children.length) p3.children[0].name = report;\n} catch (e) {}\n"
        "console.log(report);\n})();\n")
io.open(HERE + '/build-orig.js','w',encoding='utf-8').write(body)
print('build-orig.js  screens=%d  chars=%d' % (len(specs), len(body)))
