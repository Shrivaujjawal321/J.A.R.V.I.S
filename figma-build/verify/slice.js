'use strict';
/* Split a plugin file into named top-level declarations by brace/paren balance. */
const fs = require('fs');

function stripForBalance(line) {
  // remove strings, template literals, regex-ish, and comments so braces inside them don't count
  let out = '', i = 0, n = line.length;
  while (i < n) {
    const c = line[i];
    if (c === '/' && line[i + 1] === '/') break;
    if (c === '/' && line[i + 1] === '*') {
      const e = line.indexOf('*/', i + 2);
      if (e === -1) { i = n; break; }
      i = e + 2; continue;
    }
    if (c === '"' || c === "'" || c === '`') {
      const q = c; i++;
      while (i < n) { if (line[i] === '\\') { i += 2; continue; } if (line[i] === q) { i++; break; } i++; }
      out += '""'; continue;
    }
    out += c; i++;
  }
  return out;
}

function slice(file) {
  const lines = fs.readFileSync(file, 'utf8').split('\n');
  const decls = [];
  let i = 0;
  let inBlockComment = false;
  while (i < lines.length) {
    const raw = lines[i];
    const t = raw.trim();
    if (inBlockComment) { if (t.includes('*/')) inBlockComment = false; i++; continue; }
    if (t.startsWith('/*') && !t.includes('*/')) { inBlockComment = true; i++; continue; }
    if (!t || t.startsWith('//') || (t.startsWith('/*') && t.includes('*/'))) { i++; continue; }
    // must be a top-level statement (column 0)
    if (/^\s/.test(raw)) { i++; continue; }

    const m = /^(?:async\s+)?function\s+([A-Za-z0-9_$]+)/.exec(t)
      || /^(?:const|let|var)\s+([A-Za-z0-9_$]+)/.exec(t);
    const name = m ? m[1] : (t.startsWith('(async') ? '__IIFE__' : '__STMT__');

    let depth = 0, start = i, seen = false;
    while (i < lines.length) {
      const s = stripForBalance(lines[i]);
      for (const ch of s) {
        if (ch === '{' || ch === '(' || ch === '[') { depth++; seen = true; }
        else if (ch === '}' || ch === ')' || ch === ']') depth--;
      }
      const endsClean = depth <= 0 && (seen || /;\s*$/.test(stripForBalance(lines[i]).trim()) || i === start);
      i++;
      if (endsClean) break;
    }
    decls.push({ name, start: start + 1, end: i, text: lines.slice(start, i).join('\n') });
  }
  return decls;
}

if (require.main === module) {
  const d = slice(process.argv[2]);
  console.log(d.map(x => `${String(x.start).padStart(5)}-${String(x.end).padStart(5)}  ${x.name}`).join('\n'));
}
module.exports = { slice };
