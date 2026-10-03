import json, statistics as st, math
exec(open('../2026-10-03-overnight-1dte/analyze.py').read().split('R={}')[0])
TRO='/root/.claude/projects/-home-user-AgentTradeProcess/c58fd6c0-b5b4-5f81-9ee1-5a646943424a/tool-results/mcp-Robinhood-get_option_historicals-'
opt={}
for f in ['1790995553168','1790995566698','1790995566727','1790995566714']:
    for r in json.load(open(TRO+f+'.txt'))['data']['results']:
        opt[r['instrument_id']]={b['begins_at']:(None if b.get('interpolated') else float(b['close_price'])) for b in r['bars']}
ids={}
for l in open('ids.txt'):
    s,d,e,i=l.split(); ids[(s,d,e)]=i
plan={(p['sym'],p['day']):p for p in json.load(open('plan.json'))}
DAYS=['2026-09-23','2026-09-24','2026-09-25','2026-09-28','2026-09-29','2026-09-30','2026-10-01','2026-10-02']
DTYPE={'2026-09-23':'UNCLEAR','2026-09-24':'RUNNING','2026-09-25':'STUCK','2026-09-28':'UNCLEAR','2026-09-29':'RUNNING','2026-09-30':'STUCK','2026-10-01':'UNCLEAR','2026-10-02':'UNCLEAR'}
CK=[('entry','13:40'),('10:15','14:10'),('10:45','14:40'),('12:00','15:55'),('3:30','19:25')]
rows=[]
for sym in ['SPY','QQQ']:
    d5=by_day(m5[sym])
    for d in DAYS:
        p=plan[(sym,d)]; sg=1 if p['side']=='call' else -1
        b=d5[d]; after=[x for x in b if '09:45'<=x[0]<='15:25']
        p330=[x for x in b if x[0]=='15:25'][0][4]
        hi=max(x[2] for x in after); lo=min(x[3] for x in after)
        ran=abs(p330-p['p945'])>=0.5*(hi-lo)
        right=(p330-p['p945'])*sg>0
        r=dict(sym=sym,day=d,side=p['side'],K=p['K'],p945=p['p945'],p330=p330,ran=ran,right=right,dtype=DTYPE[d])
        for lab,exp in [('0',d),('1',p['exp1'])]:
            ser=opt[ids[(sym,d,exp)]]
            v={c:ser.get(f'{d}T{t}:00Z') for c,t in CK}
            r['px'+lab]=v
        rows.append(r)
def ret(r,lab,c):
    e=r['px'+lab]['entry']; x=r['px'+lab][c]
    if e is None or x is None or e==0: return None
    return (x/e-1)*100
out=[]
P=lambda *a: out.append(' '.join(str(x) for x in a))
P('Per trade (entry 9:45 last trade; % of premium at 10:15 / 10:45 / 12:00 / 3:30):')
for r in rows:
    s=lambda lab:' '.join(f'{ret(r,lab,c):+5.0f}' if ret(r,lab,c) is not None else '  NA ' for c,_ in CK[1:])
    P(f"{r['sym']} {r['day']} {r['dtype']:7} {r['side']:4} K{r['K']} {'RAN  ' if r['ran'] else 'STUCK'} {'right' if r['right'] else 'wrong'} | 0DTE ${r['px0']['entry']:.2f}: {s('0')} | 1DTE ${r['px1']['entry']:.2f}: {s('1')}")
P('\nP1 cost ratio 1DTE/0DTE at 9:45:', ', '.join(f"{r['px1']['entry']/r['px0']['entry']:.2f}" for r in rows), '| median', f"{st.median(r['px1']['entry']/r['px0']['entry'] for r in rows):.2f}")
def summ(sel,label):
    P(f'\n{label} (n={len(sel)})')
    for c,_ in CK[1:]:
        a=[ret(r,'0',c) for r in sel]; b=[ret(r,'1',c) for r in sel]
        a=[x for x in a if x is not None]; b=[x for x in b if x is not None]
        if not a: continue
        sd=lambda L: st.pstdev(L) if len(L)>1 else float('nan')
        P(f'  {c:5}: 0DTE mean {st.mean(a):+6.1f}% median {st.median(a):+6.1f}% sd {sd(a):5.1f} | 1DTE mean {st.mean(b):+6.1f}% median {st.median(b):+6.1f}% sd {sd(b):5.1f} | 1DTE better on {sum(1 for x,y in zip(a,b) if y>x)}/{len(a)}')
summ(rows,'ALL')
summ([r for r in rows if not r['right'] or not r['ran']],'P2: WRONG direction or STUCK day')
summ([r for r in rows if r['right'] and r['ran']],'P3: RIGHT direction on a RAN day')
summ([r for r in rows if not r['ran']],'(b) STUCK after 9:45')
summ([r for r in rows if r['ran']],'(b) RAN after 9:45')
summ([r for r in rows if not r['right']],'(c) wrong at 3:30')
summ([r for r in rows if r['right']],'(c) right at 3:30')
for t in ['STUCK','RUNNING','UNCLEAR']:
    summ([r for r in rows if r['dtype']==t],f'(d) brief called {t}')
# dollars per contract
P('\nDollars per 1 contract at 3:30 (0DTE vs 1DTE):')
for r in rows:
    a=(r['px0']['3:30']-r['px0']['entry'])*100; b=(r['px1']['3:30']-r['px1']['entry'])*100
    P(f"  {r['sym']} {r['day']} 0DTE {a:+7.0f} (cost {r['px0']['entry']*100:.0f}) | 1DTE {b:+7.0f} (cost {r['px1']['entry']*100:.0f})")
na=sum(1 for r in rows for lab in '01' for c,_ in CK if r['px'+lab][c] is None)
P('\nNA_no_data checkpoints:',na)
json.dump(rows,open('vehicle_rows.json','w'),indent=1)
print('\n'.join(out))
