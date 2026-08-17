# -*- coding: utf-8 -*-
"""Patch the 12 hand-authored screen specs against the console: verbatim legends,
real note tones, uppercase table headers, and the panels that were dropped."""
import json, io, os
SD = "/tmp/claude-1000/-home-ujjwal-Documents-J-A-R-V-I-S-/2633997f-2f24-47b1-b9bc-fed35ace9a16/scratchpad/"
HERE = os.path.dirname(os.path.abspath(__file__))
D  = json.load(io.open(SD + "screens_v2.json", encoding="utf-8"))
DX = json.load(io.open(SD + "dash_extra.json", encoding="utf-8"))
S  = json.load(io.open(HERE + "/specs12.json", encoding="utf-8"))
SEC = ['dashboard','fleet','drivers','loads','trips','ops','rr','yards','alerts','reports','earnings','settings']

def walk_parts(blocks):
    for b in blocks:
        for p in b.get('parts', []) or []: yield p
        for g in b.get('cols', []) or []:
            if isinstance(g, dict):
                for p in g.get('parts', []) or []: yield p
            elif isinstance(g, list):
                for gg in g:
                    for p in gg.get('parts', []) or []: yield p

fixed_heads = fixed_legend = fixed_tone = 0
for sp in S:
    key = '%s|0' % sp['key']
    d = D[key]

    # B2 — uppercase every table header, as the console's CSS does
    for p in walk_parts(sp['blocks']):
        if p.get('t') == 'table':
            for c in p['cols']:
                if c.get('h') and c['h'] != c['h'].upper():
                    c['h'] = c['h'].upper(); fixed_heads += 1

    # B3 — legend chips verbatim from srcline()
    if d['legend']:
        for b in sp['blocks']:
            if b.get('t') == 'legend' and b.get('items') != d['legend']:
                b['items'] = d['legend']; fixed_legend += 1

    # B1 — note tones as the console sets them
    notes = [b for b in sp['blocks'] if b.get('t') == 'note']
    for i, b in enumerate(notes):
        if i < len(d['notes']):
            want_t, want_b = d['notes'][i]['tone'], d['notes'][i]['body']
            if b.get('tone') != want_t: b['tone'] = want_t; fixed_tone += 1
            b['body'] = want_b          # also restores the verbatim wording

byframe = {s['frame']: s for s in S}

# ---- Dashboard: the five panels that were dropped -------------------------
dash = byframe['01 Dashboard — Overview']
mp = DX['map']
map_panel = {'t':'panel','title':'Live map snapshot','hint':'GPS-001 feed · refresh 5–30 s','parts':[
    {'t':'map','vb':[mp['w'],mp['h']],'nodes':mp['nodes'],'lines':mp['lines'],
     'legend':[{'t':'Yard','c':'#556781'},{'t':'Truck in transit','c':'#e2a90b'},
               {'t':'At pickup / delivery','c':'#2c66b0'},{'t':'City','c':'#3c4a60'}]}]}
chk = DX['checklist']
chk_panel = {'t':'panel','title':'Onboarding & compliance completion','hint':'ONB-004…007','parts':[
    {'t':'bars','rows':[{'label':r['title'],'sub':r['body'],'value':('Done' if r['state']=='done' else ('Blocked' if r['state']=='blocked' else 'Pending')),
                         'pct':(100 if r['state']=='done' else (40 if r['state']=='blocked' else 0)),
                         'tone':('green' if r['state']=='done' else ('red' if r['state']=='blocked' else 'grey'))} for r in chk['rows']]},
    {'t':'text','lines':['%s complete · ONB-005' % chk['pct']]}]}
alerts_panel = {'t':'panel','title':'Active Alerts','hint':'5 critical · 13 warning','parts':[
    {'t':'list','items':[{'sev':a['sev'],'unread':False,'title':a['title'],'body':a['body'],'code':'','time':'',
                          'btn':(a['btn'] or None)} for a in DX['alerts']]},
    {'t':'text','lines':[],'btns':[{'t':b,'kind':'secondary'} for b in DX['alertBtns']]}]}
tasks_panel = {'t':'panel','title':'Upcoming Tasks','hint':'5 open','parts':[
    {'t':'list','items':[{'sev':t['sev'],'unread':False,'title':t['title'],'body':t['body'],'code':'','time':'',
                          'btn':(t['btn'] or None)} for t in DX['tasks']]}]}
trips = [p for p in D['dashboard|0']['panels'] if p['title'] == 'Trips on going'][0]
def tbl_from(p, widths):
    cols = [{'h': h.replace('⇅','').strip().upper(), 'w': w} for h, w in zip(p['heads'], widths)]
    cols[-1]['grow'] = True
    rows = []
    for r in p['rows']:
        cs = []
        for i, c in enumerate(r['cells']):
            if c['bar']:
                pct = c['bar']['pct'] or 0
                cs.append({'bar':{'pct':pct,'tone':('green' if pct>=100 else 'amber'),'v':c['bar']['v']}})
            elif c['btns']: cs.append({'btns':[{'t':b,'kind':'secondary'} for b in c['btns'][:2]]})
            elif c['chips']: cs.append({'chip':{'tone':'blue','t':c['chips'][0]['t']}, 'sub2': c['sub'] or ''})
            else:
                o = {'v': c['v'] or '—'}
                if c['mono']: o['mono'] = True
                if i == 0: o['b'] = True; o['hi'] = True
                if c['sub']: o['sub'] = c['sub']
                cs.append(o)
        rows.append({'cells': cs})
    return {'t':'table','cols':cols,'rows':rows}
trips_panel = {'t':'panel','title':'Trips on going','hint':'Live tracking',
               'parts':[tbl_from(trips, [128,150,240,120,150,160,200])]}
leg_i = next((i for i,b in enumerate(dash['blocks']) if b.get('t')=='legend'), len(dash['blocks']))
dash['blocks'][leg_i:leg_i] = [map_panel, chk_panel,
                               {'t':'cols','ratio':[1,1],'cols':[alerts_panel, tasks_panel]},
                               trips_panel]

# ---- Reports: analytics KPI row + the three dropped panels ----------------
rep = byframe['10 Reports — Operations']
rk = D['reports|0']['kpiCards']
rep_kpi = {'t':'kpi','cards':[{'label':c['label'],'value':c['value'],'sub':c['sub'],'tone':c['tone'] or 'default'} for c in rk]}
rp = {p['title']: p for p in D['reports|0']['panels']}
rec_panel = {'t':'panel','title':'Recurring contracts','hint':'priced per hour or per trip — not per mile',
             'parts':[tbl_from(rp['Recurring contracts'], [150,150,120,170,110,150,198])]}
def chunk_bars(body, tone, step):
    rows = []
    for i in range(0, len(body) - step + 1, step):
        lab, val = body[i], body[i+1]
        sub = body[i+2] if step == 3 and i + 2 < len(body) else ''
        rows.append({'label': lab, 'value': val, 'sub': sub, 'pct': 0, 'tone': tone})
    return rows
def money(v):
    try: return float(str(v).replace('$','').replace(',',''))
    except Exception: return 0.0
pay_rows  = chunk_bars(rp['Payment trends']['body'], 'blue', 3)
fuel_rows = chunk_bars(rp['Fuel spend by lane']['body'], 'amber', 2)
mx = max([money(r['value']) for r in pay_rows] or [1]) or 1
for r in pay_rows: r['pct'] = round(money(r['value']) / mx * 100)
mf = max([money(r['value']) for r in fuel_rows] or [1]) or 1
for r in fuel_rows: r['pct'] = round(money(r['value']) / mf * 100)
pay_panel  = {'t':'panel','title':'Payment trends','hint':'ANA-005 — billed against settled by month','parts':[{'t':'bars','rows':pay_rows}]}
fuel_panel = {'t':'panel','title':'Fuel spend by lane','hint':'ANA-003','parts':[{'t':'bars','rows':fuel_rows}]}
rep['blocks'].insert(0, rep_kpi)
leg_i = next((i for i,b in enumerate(rep['blocks']) if b.get('t')=='legend'), len(rep['blocks']))
rep['blocks'][leg_i:leg_i] = [rec_panel, {'t':'cols','ratio':[1,1],'cols':[pay_panel, fuel_panel]}]

io.open(HERE + '/specs12_patched.json','w',encoding='utf-8').write(json.dumps(S, ensure_ascii=False))
print('headers uppercased: %d | legends restored: %d | note tones fixed: %d' % (fixed_heads, fixed_legend, fixed_tone))
print('dashboard blocks: %d  reports blocks: %d' % (len(dash['blocks']), len(rep['blocks'])))
