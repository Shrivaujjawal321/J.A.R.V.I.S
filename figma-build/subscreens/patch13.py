# -*- coding: utf-8 -*-
"""Per-screen parity fixes the critics found (FINDINGS.md section D)."""
import json, io, os
SD = "/tmp/claude-1000/-home-ujjwal-Documents-J-A-R-V-I-S-/2633997f-2f24-47b1-b9bc-fed35ace9a16/scratchpad/"
HERE = os.path.dirname(os.path.abspath(__file__))
D  = json.load(io.open(SD + "screens_v2.json", encoding="utf-8"))
X2 = json.load(io.open(SD + "extra2.json", encoding="utf-8"))
S12 = json.load(io.open(HERE + "/specs12_patched.json", encoding="utf-8"))
S30 = json.load(io.open(HERE + "/specs.json", encoding="utf-8"))
log = []

def panels_of(spec):
    for b in spec['blocks']:
        if b.get('t') == 'panel': yield b
        for g in b.get('cols', []) or []:
            if isinstance(g, dict) and g.get('t') is None: yield g
            elif isinstance(g, dict): yield g
            elif isinstance(g, list):
                for gg in g: yield gg

def find_panel(spec, title):
    for p in panels_of(spec):
        if p.get('title') == title: return p
    return None

def console_list(key, title):
    for p in D[key]['panels']:
        if p['title'] == title: return p
    return None

by12 = {s['frame']: s for s in S12}
by30 = {s['frame']: s for s in S30}

# D1/D2 — Dashboard: HOS list dropped a row; payments showed a Paid item and lost its button
dash = by12['01 Dashboard — Overview']
for title in ('Hours of Service — nearing limit', 'Outstanding payments'):
    tgt = find_panel(dash, title)
    src = console_list('dashboard|0', title)
    if not tgt or not src or not src.get('list'): continue
    for part in tgt['parts']:
        if part['t'] != 'list': continue
        part['items'] = [{'sev': 'info', 'unread': False, 'title': i['title'], 'body': i['body'],
                          'code': '', 'time': '', 'btn': (i['btns'][0] if i.get('btns') else None)}
                         for i in src['list']]
        log.append('%s -> %d rows from console' % (title, len(part['items'])))
    if src.get('btns'):
        has = any(p.get('btns') for p in tgt['parts'])
        if not has:
            tgt['parts'].append({'t': 'text', 'lines': [],
                                 'btns': [{'t': b, 'kind': 'secondary'} for b in src['btns'][:2]]})
            log.append('%s -> restored %s button' % (title, src['btns'][0]))

# D3 — Notifications feed: contiguous rows plus the per-row actions
notif = by12.get('09 Notifications')
if notif:
    src = None
    for p in D['alerts|0']['panels']:
        if p.get('list'): src = p; break
    if src:
        for p in panels_of(notif):
            for part in p.get('parts', []):
                if part['t'] == 'list':
                    part['items'] = [{'sev': 'info', 'unread': False, 'title': i['title'], 'body': i['body'],
                                      'code': '', 'time': '', 'btn': (i['btns'][0] if i.get('btns') else None)}
                                     for i in src['list']]
                    log.append('Notifications -> %d contiguous rows with actions' % len(part['items']))

# D4 — POD review lost the photo-evidence block entirely
pod = by30.get('04.4 Loads — POD & Close-out')
if pod and X2.get('pod', {}).get('photos'):
    tgt = None
    for p in panels_of(pod):
        if p.get('parts'): tgt = p
    if tgt and not any(x['t'] == 'photos' for x in tgt['parts']):
        tgt['parts'].insert(0, {'t': 'photos', 'tiles': X2['pod']['photos']})
        log.append('POD -> %d photo tiles restored' % len(X2['pod']['photos']))

# D5 — Capacity: 15 selectable commodity chips became flat text and lost their state
cap = by30.get('12.10 Settings — Capacity')
cc = (X2.get('capacity') or {}).get('Commodity capability') or []
if cap and cc:
    tgt = find_panel(cap, 'Commodity capability')
    if tgt:
        tgt['parts'] = [{'t': 'filters', 'label': 'Commodity capability',
                         'chips': [{'t': c['t'], 'on': c['on']} for c in cc]}] + \
                       [x for x in tgt['parts'] if x['t'] not in ('text',)]
        log.append('Capacity -> %d chips (%d declared) with real state' % (len(cc), sum(1 for c in cc if c['on'])))

io.open(HERE + '/specs12_patched.json', 'w', encoding='utf-8').write(json.dumps(S12, ensure_ascii=False))
io.open(HERE + '/specs.json', 'w', encoding='utf-8').write(json.dumps(S30, ensure_ascii=False))
print('\n'.join('  ' + l for l in log) or '  no changes')
