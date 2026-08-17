'use strict';
const fs = require('fs');
const vm = require('vm');
const path = require('path');
const sim = require('./figma-sim.js');

const DIR = '/home/ujjwal/Documents/J.A.R.V.I.S./figma-build/use-figma';
const files = fs.readdirSync(DIR).filter(f => /^\d\d-.*\.js$/.test(f)).sort();

function ctx() {
  return vm.createContext({
    figma: sim.figma,
    Promise, Symbol, Math, JSON, Object, Array, String, Number, Boolean, Error, RegExp, Date, Set, Map,
    setTimeout, parseInt, parseFloat, isNaN, console: { log() { }, error() { }, warn() { } },
  });
}

(async () => {
  let hardFail = false;
  for (const f of files) {
    const src = fs.readFileSync(path.join(DIR, f), 'utf8');
    // reproduce use_figma's auto async-IIFE wrap
    const wrapped = `(async () => {\n${src}\n})()`;
    process.stdout.write(`\n########## ${f} ##########\n`);
    try {
      const r = await vm.runInContext(wrapped, ctx(), { filename: f });
      const out = JSON.parse(JSON.stringify(r, (k, v) => (k === 'log' ? undefined : v)));
      console.log(JSON.stringify(out, null, 1));
      if (r && r.log && r.log.length) console.log('log: ' + r.log.join(' | '));
      if (r && r.ok === false) { console.log('*** ok:false ***'); hardFail = true; }
    } catch (e) {
      hardFail = true;
      console.log('!!! THROWN: ' + (e && e.stack ? e.stack.split('\n').slice(0, 8).join('\n') : e));
    }
  }
  console.log('\n########## FINAL DOCUMENT ##########');
  console.log(JSON.stringify(sim.stats(), null, 1));
  const w = [...new Set(sim.WARN)];
  console.log('\nWARNINGS (' + w.length + ' unique):\n' + w.slice(0, 30).join('\n'));
  console.log('\nRESULT: ' + (hardFail ? 'FAILURES PRESENT' : 'all chunks ok'));
})();
