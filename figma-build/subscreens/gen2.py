# -*- coding: utf-8 -*-
"""Regenerate the 30 sub-screen specs from the v2 extraction, with every
systematic defect the critics found fixed at the generator level."""
import json, io, re, os

SD = "/tmp/claude-1000/-home-ujjwal-Documents-J-A-R-V-I-S-/2633997f-2f24-47b1-b9bc-fed35ace9a16/scratchpad/"
D = json.load(io.open(SD + "screens_v2.json", encoding="utf-8"))
TONE = json.load(io.open(SD + "tone_map.json", encoding="utf-8"))

INNER = 1440 - 248 - 44
SEC = ['dashboard','fleet','drivers','loads','trips','ops','rr','yards','alerts','reports','earnings','settings']
BUILT = {k + '|0' for k in SEC}

def tone_of(txt):
    if txt in TONE: return TONE[txt]
    for k, v in TONE.items():
        if k.lower() == txt.lower(): return v
    t = txt.lower()
    if any(w in t for w in ('expired','missing','out of service','suspend','fault','overdue','disput','cancel','block','critical','fail','not ')): return 'red'
    if any(w in t for w in ('pending','due','warn','await','soon','review','partial','accru')): return 'amber'
    if any(w in t for w in ('ok','active','valid','verified','complete','signed','paid','clear','approved','serviceable','enabled','compliant','on')): return 'green'
    return 'grey'

# B2 — the console's CSS is text-transform:uppercase on every th
def head_text(h):
    return h.replace('⇅', '').strip().upper()

def widths(heads, rows):
    n = len(heads)
    isbox = [all((r['cells'][i]['box'] if i < len(r['cells']) else False) for r in rows) and not heads[i].strip() for i in range(n)]
    hasbtn = [any((r['cells'][i]['btns'] if i < len(r['cells']) else None) for r in rows) for i in range(n)]
    w = []
    for i in range(n):
        if isbox[i]: w.append(48.0); continue
        m = len(head_text(heads[i]))
        for r in rows:
            if i < len(r['cells']):
                cl = r['cells'][i]
                m = max(m, len(cl['v']), len(cl['sub']), max([len(x['t']) for x in cl['chips']] or [0]),
                        max([len(b) for b in cl['btns']] or [0]) + 4)
        if hasbtn[i]: m = max(m, 20)
        w.append(max(6.0, float(m)))
    fixed = sum(w[i] for i in range(n) if isbox[i])
    flex = [i for i in range(n) if not isbox[i]]
    tot = sum(w[i] for i in flex) or 1.0
    avail = INNER - fixed
    out = list(w)
    for i in flex: out[i] = max(72.0, min(240.0, round(avail * w[i] / tot)))
    s = sum(out)
    if s and abs(s - INNER) > 1:
        for i in flex: out[i] = round(out[i] * (INNER - fixed) / (s - fixed))
    cols = [{'h': head_text(heads[i]), 'w': int(out[i])} for i in range(n)]
    if flex: cols[flex[-1]]['grow'] = True
    return cols

def cell(c, first_data):
    if c['box']: return {'box': True}
    # B4 — row action buttons the renderer already supports and the generator never emitted
    if c['btns']:
        return {'btns': [{'t': b, 'kind': 'secondary'} for b in c['btns'][:2]]}
    if c['bar']:
        pct = c['bar']['pct'] if c['bar']['pct'] is not None else 0
        return {'bar': {'pct': pct, 'tone': 'green' if pct >= 100 else 'amber', 'v': c['bar']['v']}}
    if c['chips']:
        ch = c['chips'][0]
        o = {'chip': {'tone': tone_of(ch['t']), 't': ch['t']}}
        if ch['plain']: o['chip']['plain'] = True
        if len(c['chips']) > 1:
            c2 = c['chips'][1]
            o['chip2'] = {'tone': tone_of(c2['t']), 't': c2['t']}
            if c2['plain']: o['chip2']['plain'] = True
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

def filters_part(f):
    return {'t': 'filters', 'label': f['label'],
            'chips': [{'t': c['t'], 'on': c['on'], 'n': (int(c['n']) if c['n'] and c['n'].isdigit() else None)} for c in f['chips'][:9]]}

def panel_parts(p):
    parts = []
    for f in p.get('filters', []):          # B6 — filter rows were being dropped
        parts.append(filters_part(f))
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
        # B5 — only where the console genuinely paginates
        if p.get('pager'):
            parts.append({'t': 'pager', 'range': p.get('pagerText') or ''})
        elif p.get('rowCount', 0) > len(p['rows']):
            parts.append({'t': 'text', 'lines': ['Showing %d of %d — the console renders all rows on this screen.' % (len(p['rows']), p['rowCount'])]})
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
            {'sev': 'info', 'unread': False, 'title': i['title'], 'body': i['body'], 'code': '', 'time': '',
             'btn': (i['btns'][0] if i.get('btns') else None)} for i in p['list']]})
    elif p.get('empty'):
        e = {'t': 'empty', 'kind': 'default', 'title': p['empty']['title'], 'body': p['empty']['body']}
        if p['empty'].get('action'): e['action'] = p['empty']['action']     # RR lost its only CTA
        parts.append(e)
    elif p.get('body'):
        parts.append({'t': 'text', 'lines': p['body'][:14]})
    for n in p.get('pnotes', [])[:2]:
        parts.append({'t': 'text', 'lines': [n['body']]})
    if p.get('btns') and parts:
        btns = [{'t': b, 'kind': 'secondary'} for b in p['btns'][:3]]
        if parts[-1]['t'] == 'text' and 'btns' not in parts[-1]: parts[-1]['btns'] = btns
        else: parts.append({'t': 'text', 'lines': [], 'btns': btns})
    return parts

# the 5x3 channel matrix the console renders as checkboxes
NOTIF_MATRIX = [
    ['Critical alerts (SOS, breakdown, compliance)', 1, 1, 1],
    ['Load tenders & assignment',                    1, 0, 1],
    ['Document & compliance reminders',              1, 0, 0],
    ['Messages from drivers',                        0, 0, 1],
    ['Weekly / monthly financial reports',           1, 0, 0]]

def notif_prefs_panel():
    cols = [{'h': 'NOTIFICATION TYPE', 'w': 560, 'grow': True},
            {'h': 'EMAIL', 'w': 196}, {'h': 'SMS', 'w': 196}, {'h': 'PUSH', 'w': 196}]
    rows = []
    for r in NOTIF_MATRIX:
        cs = [{'v': r[0], 'b': True}]
        for on in r[1:]:
            cs.append({'chip': {'tone': 'green' if on else 'grey', 't': 'On' if on else 'Off', 'plain': True}})
        rows.append({'cells': cs})
    return {'t': 'panel', 'title': 'Delivery channels', 'hint': 'per notification type',
            'parts': [{'t': 'table', 'cols': cols, 'rows': rows}]}

def build(k):
    sec, sidx = k.split('|'); sidx = int(sidx)
    d = D[k]
    blocks = []
    if d['banner']:
        b = {'t': 'banner', 'tone': d['banner']['tone'], 'title': d['banner']['title'], 'body': d['banner']['body']}
        if d['banner']['btns']:
            b['btns'] = [{'t': x, 'kind': 'danger' if b['tone'] == 'crit' else 'secondary'} for x in d['banner']['btns'][:2]]
        blocks.append(b)
    if len(d.get('kpiCards', [])) >= 2:
        blocks.append({'t': 'kpi', 'cards': [{'label': c['label'], 'value': c['value'], 'sub': c['sub'],
                                              'tone': c['tone'] or 'default'} for c in d['kpiCards'][:10]]})
    for f in d.get('filters', []):
        if not any(f in p.get('filters', []) for p in d['panels']):
            blocks.append({'t': 'panel', 'title': '', 'parts': [filters_part(f)]})
    if k == 'settings|1':
        blocks.append(notif_prefs_panel())
    else:
        for p in d['panels']:
            parts = panel_parts(p)
            if not parts and not p['title']: continue
            blk = {'t': 'panel', 'title': p['title'] or 'Details', 'parts': parts}
            if p['hint']: blk['hint'] = p['hint']
            if p.get('hdBtns'): blk['action'] = {'t': p['hdBtns'][0], 'kind': 'secondary'}
            blocks.append(blk)
    for n in d['notes'][:3]:
        blocks.append({'t': 'note', 'tone': n['tone'], 'body': n['body']})   # B1 — real tone
    if d['legend']:
        blocks.append({'t': 'legend', 'items': d['legend'][:6]})             # B3 — verbatim
    spec = {'key': sec, 'subIdx': sidx, 'nav': d['nav'], 'sub': d['sub'],
            'frame': '%02d.%d %s — %s' % (SEC.index(sec) + 1, sidx + 1, d['nav'], d['sub']),
            'title': d['title'] or d['sub'], 'desc': d['desc'], 'blocks': blocks}
    acts = [a for a in d['acts'] if a and len(a) < 40]
    if acts: spec['actions'] = [{'t': a, 'kind': 'secondary'} for a in acts[:3]]
    if d.get('lock'): spec['lock'] = d['lock']    # a badge, never a button
    return spec

TODO = [k for k in D if k not in BUILT]
TODO.sort(key=lambda k: (SEC.index(k.split('|')[0]), int(k.split('|')[1])))
specs = [build(k) for k in TODO]
io.open(os.path.join(os.path.dirname(__file__), 'specs.json'), 'w', encoding='utf-8').write(json.dumps(specs, ensure_ascii=False))

nt = {}; nf = np_ = nb = nbar = 0
for s in specs:
    for b in s['blocks']:
        if b['t'] == 'note': nt[b['tone']] = nt.get(b['tone'], 0) + 1
        for p in b.get('parts', []):
            if p['t'] == 'filters': nf += 1
            if p['t'] == 'pager': np_ += 1
            if p['t'] == 'table':
                for r in p['rows']:
                    for c in r['cells']:
                        if c.get('btns'): nb += 1
                        if c.get('bar'): nbar += 1
print('screens: %d | note tones: %s | filter rows: %d | pagers: %d | cell buttons: %d | cell bars: %d'
      % (len(specs), nt, nf, np_, nb, nbar))
