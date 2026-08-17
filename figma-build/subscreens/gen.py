# -*- coding: utf-8 -*-
"""Turn the extracted console content into Figma SCREENS specs for the 30 sub-screens."""
import json, io, re, os

SD = "/tmp/claude-1000/-home-ujjwal-Documents-J-A-R-V-I-S-/2633997f-2f24-47b1-b9bc-fed35ace9a16/scratchpad/"
D = json.load(io.open(SD + "screens.json", encoding="utf-8"))
TONE = json.load(io.open(SD + "tone_map.json", encoding="utf-8"))

INNER = 1440 - 248 - 44          # desktop content width inside the panel
SEC = ['dashboard','fleet','drivers','loads','trips','ops','rr','yards','alerts','reports','earnings','settings']
LABEL = {k: D[k + '|0']['nav'] for k in SEC}
BUILT = {k + '|0' for k in SEC}   # the 12 already in the file

def tone_of(txt):
    if txt in TONE: return TONE[txt]
    for k, v in TONE.items():
        if k.lower() == txt.lower(): return v
    t = txt.lower()
    if any(w in t for w in ('expired','missing','out of service','suspend','fault','overdue','disput','cancel','block','critical','fail')): return 'red'
    if any(w in t for w in ('pending','due','warn','await','soon','review','partial')): return 'amber'
    if any(w in t for w in ('ok','active','valid','verified','complete','signed','paid','clear','approved','serviceable','enabled','compliant')): return 'green'
    return 'grey'

def head_text(h):
    h = h.replace('⇅', '').strip()
    if not h: return ''
    if re.search(r'[0-9]', h) and h.isupper(): return h        # codes such as CO-11
    return h[:1].upper() + h[1:].lower()

def widths(heads, rows):
    n = len(heads)
    isbox = [all((r['cells'][i]['box'] if i < len(r['cells']) else False) for r in rows) and not heads[i].strip() for i in range(n)]
    w = []
    for i in range(n):
        if isbox[i]: w.append(48.0); continue
        m = len(head_text(heads[i]))
        for r in rows:
            if i < len(r['cells']):
                c = r['cells'][i]
                m = max(m, len(c['v']), len(c['sub']), max([len(x['t']) for x in c['chips']] or [0]))
        w.append(max(6.0, float(m)))
    fixed = sum(w[i] for i in range(n) if isbox[i])
    flex_i = [i for i in range(n) if not isbox[i]]
    tot = sum(w[i] for i in flex_i) or 1.0
    avail = INNER - fixed
    out = list(w)
    for i in flex_i:
        out[i] = max(72.0, min(230.0, round(avail * w[i] / tot)))
    # normalise so the row fills the panel exactly
    s = sum(out)
    if s and abs(s - INNER) > 1:
        for i in flex_i: out[i] = round(out[i] * (INNER - fixed) / (s - fixed))
    cols = [{'h': head_text(heads[i]), 'w': int(out[i])} for i in range(n)]
    if flex_i: cols[flex_i[-1]]['grow'] = True
    return cols

def cell(c, first_data):
    if c['box']: return {'box': True}
    if c['chips']:
        ch = c['chips'][0]
        o = {'chip': {'tone': tone_of(ch['t']), 't': ch['t']}}
        if ch['plain']: o['chip']['plain'] = True
        if c['sub']: o['sub2'] = c['sub']
        elif c['v']: o['sub2'] = c['v']
        return o
    o = {'v': c['v'] or '—'}
    if c['mono']: o['mono'] = True
    if first_data: o['b'] = True; o['hi'] = True
    if c['sub']:
        o['sub'] = c['sub']
        if c['mono'] or re.match(r'^[A-Z0-9\-· /:.]+$', c['sub']): o['subMono'] = True
    return o

def panel_parts(p):
    parts = []
    if p.get('heads'):
        cols = widths(p['heads'], p['rows'])
        fd = next((i for i in range(len(cols)) if not (p['rows'] and p['rows'][0]['cells'][i]['box'])), 0)
        rows = []
        for r in p['rows']:
            cs = [cell(r['cells'][i], i == fd) if i < len(r['cells']) else {'v': ''} for i in range(len(cols))]
            row = {'cells': cs}
            if r.get('state') == 'blocked': row['state'] = 'blocked'
            rows.append(row)
        parts.append({'t': 'table', 'cols': cols, 'rows': rows})
        if p.get('rowCount', 0) > len(p['rows']):
            parts.append({'t': 'pager', 'range': 'Showing 1–%d of %d' % (len(p['rows']), p['rowCount'])})
    elif p.get('kv'):
        rows = []
        for r in p['kv']:
            o = {'k': r['k'], 'v': r['v'] or 'Not captured'}
            if r['chips']:
                o['chip'] = {'tone': tone_of(r['chips'][0]['t']), 't': r['chips'][0]['t']}
                if o['v'] in ('', r['chips'][0]['t']): o['v'] = ''
            if r.get('empty'): o['empty'] = True
            rows.append(o)
        parts.append({'t': 'kv', 'rows': rows})
    elif p.get('list'):
        parts.append({'t': 'list', 'items': [
            {'sev': 'info', 'unread': False, 'title': i['title'], 'body': i['body'], 'code': '', 'time': ''} for i in p['list']]})
    elif p.get('empty'):
        parts.append({'t': 'empty', 'kind': 'default', 'title': p['empty']['title'], 'body': p['empty']['body']})
    elif p.get('body'):
        lines, i = [], 0
        b = p['body']
        while i < len(b):
            if i + 1 < len(b) and len(b[i]) < 34 and len(b[i + 1]) > 0 and len(b) % 2 == 0:
                lines.append('%s · %s' % (b[i], b[i + 1])); i += 2
            else:
                lines.append(b[i]); i += 1
        parts.append({'t': 'text', 'lines': lines[:14]})
    if p.get('pnotes'):
        parts.append({'t': 'text', 'lines': p['pnotes'][:2]})
    if p.get('btns') and parts:
        last = parts[-1]
        if last['t'] == 'text':
            last['btns'] = [{'t': b, 'kind': 'secondary'} for b in p['btns'][:3]]
        else:
            parts.append({'t': 'text', 'lines': [], 'btns': [{'t': b, 'kind': 'secondary'} for b in p['btns'][:3]]})
    return parts

def build(k):
    sec, sidx = k.split('|'); sidx = int(sidx)
    d = D[k]
    blocks = []
    if d['banner']:
        b = {'t': 'banner', 'tone': d['banner']['tone'], 'title': d['banner']['title'], 'body': d['banner']['body']}
        if d['banner']['btns']: b['btns'] = [{'t': x, 'kind': 'danger' if b['tone'] == 'crit' else 'secondary'} for x in d['banner']['btns'][:2]]
        blocks.append(b)
    for p in d['panels']:
        parts = panel_parts(p)
        if not parts and not p['title']: continue
        blk = {'t': 'panel', 'title': p['title'] or 'Details', 'parts': parts}
        if p['hint']: blk['hint'] = p['hint']
        blocks.append(blk)
    for n in d['notes'][:3]:
        blocks.append({'t': 'note', 'tone': 'blue', 'body': n})
    if d['legend']:
        blocks.append({'t': 'legend', 'items': d['legend'][:6]})
    spec = {'key': sec, 'subIdx': sidx, 'nav': d['nav'], 'sub': d['sub'],
            'frame': '%02d.%d %s — %s' % (SEC.index(sec) + 1, sidx + 1, d['nav'], d['sub']),
            'title': d['title'] or d['sub'], 'desc': d['desc'], 'blocks': blocks}
    acts = [a for a in d['acts'] if a and len(a) < 40]
    if acts: spec['actions'] = [{'t': a, 'kind': 'secondary'} for a in acts[:3]]
    return spec

TODO = [k for k in D if k not in BUILT]
TODO.sort(key=lambda k: (SEC.index(k.split('|')[0]), int(k.split('|')[1])))
specs = [build(k) for k in TODO]
io.open(os.path.join(os.path.dirname(__file__), 'specs.json'), 'w', encoding='utf-8').write(json.dumps(specs, ensure_ascii=False))
print('screens generated: %d' % len(specs))
for s in specs:
    tb = sum(1 for b in s['blocks'] if b['t'] == 'panel' and any(p['t'] == 'table' for p in b['parts']))
    print('  %-34s blocks=%-3d tables=%d' % (s['frame'], len(s['blocks']), tb))
