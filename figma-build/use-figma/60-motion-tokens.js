/* Motion tokens as real Figma variables, plus a spec board on page 01.
   Values come from the research: a 100-300ms band, nothing past 350ms,
   ease-out entering / ease-in leaving, and 0ms for anything a dispatcher
   repeats hundreds of times a day. Safe to re-run. */
(async () => {
var report = 'start';
try {
  var DUR = [
    ['none',            0,   'State a dispatcher changes hundreds of times a day: status chip, row select, HOS bar, detention tick, any keyboard action, optimistic confirmation'],
    ['instant',         90,  'Hover, focus ring, button press, tooltip'],
    ['fast',            150, 'Dropdown, popover, toggle fill, badge enter'],
    ['base',            220, 'Drawer, side panel, filter expand, wizard step'],
    ['slow',            300, 'Modal. Ceiling — nothing in this product animates past 350ms'],
    ['toast-in',        180, 'Notification enters'],
    ['toast-out',       230, 'Notification leaves (exit is faster than entry)'],
    ['skeleton-swap',   130, 'Skeleton to content crossfade, only if the load exceeded 400ms']
  ];
  var EASE = [
    ['enter',  'cubic-bezier(0, 0, 0.2, 1)',   'Anything appearing — decelerates so the eye can follow it to rest'],
    ['exit',   'cubic-bezier(0.4, 0, 1, 1)',   'Anything leaving — accelerates away'],
    ['move',   'cubic-bezier(0.4, 0, 0.2, 1)', 'Anything repositioning on screen'],
    ['spring', 'stiffness 350 · damping 32 · mass 1', 'Anything re-triggerable mid-flight (drawer, popover) — CSS keyframes visibly snap when interrupted']
  ];
  var LADDER = [
    ['under 100ms', 'no indicator at all'],
    ['100-400ms',   'small inline spinner'],
    ['400ms-3s',    'skeleton, shaped like the real content'],
    ['over 3s',     'skeleton plus progress or ETA text']
  ];

  var cols = await figma.variables.getLocalVariableCollectionsAsync();
  var mc = null;
  cols.forEach(function (c) { if (c.name === 'Motion') mc = c; });
  if (!mc) mc = figma.variables.createVariableCollection('Motion');
  var mode = mc.modes[0].modeId;
  var have = {};
  (await figma.variables.getLocalVariablesAsync('FLOAT')).forEach(function (v) { have[v.name] = v; });

  var made = 0;
  for (var i = 0; i < DUR.length; i++) {
    var nm = 'duration/' + DUR[i][0];
    if (have[nm]) { try { have[nm].setValueForMode(mode, DUR[i][1]); } catch (e) {} continue; }
    try {
      var v = figma.variables.createVariable(nm, mc, 'FLOAT');
      v.setValueForMode(mode, DUR[i][1]);
      v.description = DUR[i][2];
      made++;
    } catch (e) {}
  }

  /* the spec board — a developer should not have to read a script to find these */
  var ds = null;
  figma.root.children.forEach(function (p) { if (p.name === '01 Design System') ds = p; });
  await figma.setCurrentPageAsync(ds);
  var sec = null;
  ds.children.forEach(function (s) { if (s.type === 'SECTION' && s.name === 'Foundations') sec = s; });
  var host = sec || ds;
  host.children.slice().forEach(function (n) { if (n.name === 'Motion — spec') safe(function () { n.remove(); }); });

  var board = mkFrame('Motion — spec', {dir:'V', gap:18, pad:[26,28,30,28], fill:C.panel, stroke:C.line, radius:12, w:900});
  host.appendChild(board);
  var bb = host.absoluteBoundingBox ? 0 : 0;
  var maxB = 0;
  host.children.forEach(function (n) { if (n !== board) maxB = Math.max(maxB, n.y + n.height); });
  board.x = 0; board.y = maxB + 120;

  add(board, mkText('Motion', {font:F.dispBold, size:22, lh:27}), {hFill:true});
  add(board, mkText('A dispatcher repeats the same action hundreds of times a day. For those, the correct duration is zero — animation that delights once becomes friction at the hundredth repeat. Motion is spent only where it explains a spatial change: the wizard, drawers, and the notification centre.',
    {size:12.5, lh:18, color:C.ink2}), {hFill:true});

  function table(title, rows, w1, w2){
    add(board, mkText(title, {font:F.semi, size:13, lh:18}), {hFill:true});
    var t = mkFrame('t', {dir:'V', gap:0, stroke:C.line, radius:8, clip:true});
    add(board, t, {hFill:true});
    rows.forEach(function (r, i) {
      var row = mkFrame('r', {dir:'H', gap:12, pad:[9,12,9,12], stroke:C.line2,
                              sides:[0,0, i < rows.length - 1 ? 1 : 0, 0], align:'MIN'});
      add(t, row, {hFill:true});
      add(row, mkText(String(r[0]), {font:F.monoSemi, size:11, lh:15, color:C.ink}), {hFix:w1});
      add(row, mkText(String(r[1]), {font:F.mono, size:11, lh:15, color:C.brand}), {hFix:w2});
      if (r.length > 2) add(row, mkText(String(r[2]), {size:11.5, lh:16, color:C.ink2}), {hFill:true});
    });
  }
  table('Duration', DUR.map(function (d) { return [d[0], d[1] + 'ms', d[2]]; }), 120, 70);
  table('Easing', EASE.map(function (e) { return [e[0], e[1], e[2]]; }), 90, 230);
  table('Loading indicator ladder', LADDER, 130, 260);

  add(board, mkText('Reduced motion — prefers-reduced-motion: reduce collapses every spatial transition to a 100ms opacity crossfade. Functional feedback stays: focus rings and colour state changes carry information, not decoration. Never remove the only signal that something changed.',
    {size:11.5, lh:17, color:C.ink2}), {hFill:true});
  add(board, mkText('Never animate a number that is evidence. The detention timer and the HOS clock are a billing record and a legal compliance clock — a tweened value is a value that is briefly wrong. Animate the container’s colour when it crosses a threshold; never the digits.',
    {size:11.5, lh:17, color:C.redInk}), {hFill:true});

  report = 'MOTION vars=' + made + '/' + DUR.length + ' board=1 easings=' + EASE.length;
} catch (err) { report = 'FAIL ' + (err && err.message ? err.message : String(err)).substring(0, 150); }
try {
  var p3 = null;
  figma.root.children.forEach(function (p) { if (p.name.indexOf('03 Prototype') === 0) p3 = p; });
  await figma.setCurrentPageAsync(p3);
  if (p3 && p3.children.length) p3.children[0].name = report;
} catch (e) {}
console.log(report);
})();
