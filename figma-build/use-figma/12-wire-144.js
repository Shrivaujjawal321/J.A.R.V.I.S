/* mySHIPR — wire the remaining 12 sidebar items so all 144 have an interaction.
 * Figma refuses NAVIGATE to an ancestor, so the item for the screen you are already
 * on gets SCROLL_TO the page header instead — the standard "active tab" behaviour.
 * Safe to re-run. */
(async () => {
try {
  var RESULT = { navigate: 0, scrollTo: 0, failed: 0, perFrame: [], errors: [] };

  var KEY2FRAME = {
    dashboard: '01 Dashboard — Overview',
    fleet:     '02 Fleet — All Vehicles',
    drivers:   '03 Drivers — All Drivers',
    loads:     '04 Loads — Tenders',
    trips:     '05 Trips — On going',
    ops:       '06 Driver Ops — Detention',
    rr:        '07 RR — Coming soon',
    yards:     '08 Yards — All yards',
    alerts:    '09 Notifications',
    reports:   '10 Reports — Operations',
    earnings:  '11 Earnings — Earnings',
    settings:  '12 Settings — My Profile'
  };

  var pageSC = null;
  for (var i = 0; i < figma.root.children.length; i++) {
    if (figma.root.children[i].name === '02 Screens') pageSC = figma.root.children[i];
  }
  if (!pageSC) throw new Error('page "02 Screens" not found');
  await figma.setCurrentPageAsync(pageSC);

  var desktop = null;
  for (var s = 0; s < pageSC.children.length; s++) {
    if (pageSC.children[s].type === 'SECTION' && pageSC.children[s].name === 'Desktop') desktop = pageSC.children[s];
  }
  if (!desktop) throw new Error('section "Desktop" not found');

  var frames = {};
  desktop.children.forEach(function (f) { frames[f.name] = f; });

  async function setReaction(node, reaction) {
    if (node.setReactionsAsync) { await node.setReactionsAsync([reaction]); return true; }
    node.reactions = [reaction];
    return true;
  }

  for (var k = 0; k < desktop.children.length; k++) {
    var fr = desktop.children[k];
    if (fr.type !== 'FRAME') continue;

    // the page header inside this screen — scroll target for the active item
    var header = fr.findAll(function (n) { return n.type === 'FRAME' && n.name === 'pagehd'; })[0];

    var navs = fr.findAll(function (n) {
      return typeof n.name === 'string' && n.name.indexOf('nav/') === 0;
    });

    var nav = 0, scr = 0;
    for (var j = 0; j < navs.length; j++) {
      var item = navs[j];
      var key = item.name.substring(4);
      var destName = KEY2FRAME[key];
      if (!destName) continue;
      var dest = frames[destName];
      if (!dest) continue;

      var isSelf = (dest.id === fr.id);
      try {
        if (!isSelf) {
          await setReaction(item, {
            trigger: { type: 'ON_CLICK' },
            actions: [{ type: 'NODE', destinationId: dest.id, navigation: 'NAVIGATE',
                        transition: null, preserveScrollPosition: false, resetVideoPosition: false }]
          });
          nav++;
        } else if (header) {
          await setReaction(item, {
            trigger: { type: 'ON_CLICK' },
            actions: [{ type: 'SCROLL_TO', destinationId: header.id,
                        transition: { type: 'SMART_ANIMATE', easing: { type: 'EASE_OUT' }, duration: 0.3 },
                        resetVideoPosition: false }]
          });
          scr++;
        }
      } catch (e) {
        RESULT.failed++;
        if (RESULT.errors.length < 6) RESULT.errors.push(fr.name + ' / ' + item.name + ' -> ' + String(e && e.message ? e.message : e).substring(0, 90));
      }
    }
    RESULT.navigate += nav;
    RESULT.scrollTo += scr;
    RESULT.perFrame.push(fr.name + ' : nav ' + nav + ' + scroll ' + scr);
  }

  // count everything actually wired
  var wired = 0;
  desktop.children.forEach(function (f) {
    if (f.type !== 'FRAME') return;
    f.findAll(function (n) { return typeof n.name === 'string' && n.name.indexOf('nav/') === 0; })
     .forEach(function (n) { if (n.reactions && n.reactions.length) wired++; });
  });
  RESULT.totalWired = wired;
  RESULT.target = 144;

  console.log('DONE ' + JSON.stringify(RESULT));
} catch (err) {
  console.log('FAILED: ' + (err && err.message ? err.message : String(err)));
}
})();
