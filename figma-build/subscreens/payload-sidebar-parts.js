/* Turn the three identical parts of the rail into real components, so the rail
   stops being copy-pasted geometry on 230 frames. The nav list stays generated —
   it genuinely differs per screen, and its rows are already instances. */
var sec = null;
figma.currentPage.children.forEach(function (s) { if (s.type === 'SECTION' && s.name === 'Components') sec = s; });
var host = sec || figma.currentPage;

var WANT = ['Sidebar/Brand', 'Sidebar/OrgCard', 'Sidebar/Footer'];
var removed = 0;
figma.currentPage.findAll(function (n) {
  return (n.type === 'COMPONENT' || n.type === 'COMPONENT_SET') && WANT.indexOf(n.name) >= 0;
}).forEach(function (n) { safe(function () { n.remove(); }); removed++; });

var maxB = 0;
host.children.forEach(function (n) { maxB = Math.max(maxB, n.y + n.height); });

function place(node, name, y){
  host.appendChild(node);
  node.x = 0; node.y = y;
  var c = toComp(node);
  c.name = name;
  return c;
}
var made = [];
var b = place(buildBrandNode(), 'Sidebar/Brand', maxB + 140);
made.push(b.name);
var oc = orgCard(); safe(function(){ oc.resize(SIDE_W, Math.max(1, oc.height)); });
var o = place(oc, 'Sidebar/OrgCard', maxB + 140 + b.height + 40);
made.push(o.name);
var f = place(buildFootNode(), 'Sidebar/Footer', maxB + 140 + b.height + 40 + o.height + 40);
made.push(f.name);

RESULT = { removed: removed, created: made };
