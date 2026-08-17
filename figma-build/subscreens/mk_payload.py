import io, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
name, page, tag = sys.argv[1], sys.argv[2], sys.argv[3]   # payload file, 'ds'|'screens', report tag
base = io.open(HERE + '/_base.js', encoding='utf-8').read()
pay  = io.open(HERE + '/' + name, encoding='utf-8').read()
PAGEKEY = {'ds': 'PAGE.ds', 'screens': 'PAGE.screens'}[page]
body = (
"(async () => {\nvar RESULT = null, report = 'start';\ntry {\n" + base +
"\nawait loadFonts();\nawait adoptComponents(true);\n"
"const __pg = await getPage(" + PAGEKEY + ");\nawait figma.setCurrentPageAsync(__pg);\n" +
pay +
"\n  report = '" + tag + " ' + JSON.stringify(RESULT).substring(0, 150);\n"
"} catch (err) { report = 'FAIL-" + tag + " ' + (err && err.message ? err.message : String(err)).substring(0, 140); }\n"
"try {\n  var p3 = null;\n  figma.root.children.forEach(function(p){ if (p.name.indexOf('03 Prototype') === 0) p3 = p; });\n"
"  await figma.setCurrentPageAsync(p3);\n  if (p3 && p3.children.length) p3.children[0].name = report;\n} catch (e) {}\n"
"console.log(report);\n})();\n")
out = HERE + '/../use-figma/' + sys.argv[4]
io.open(out, 'w', encoding='utf-8').write(body)
print('%s -> %s  (%d chars)' % (name, sys.argv[4], len(body)))
