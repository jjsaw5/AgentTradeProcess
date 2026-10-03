import json
exec(open('../2026-10-03-overnight-1dte/analyze.py').read().split('R={}')[0])
plan=[]
for sym in ['SPY','QQQ']:
    d5=by_day(m5[sym]); days=sorted(d for d in d5 if d>='2026-08-18')
    for i,d in enumerate(days):
        b=d5[d]; o=b[0][1]; p945=b[2][4]
        nxt=days[i+1] if i+1<len(days) else '2026-10-05'
        plan.append(dict(sym=sym,day=d,open=o,p945=p945,side='call' if p945>o else 'put',K=round(p945),exp1=nxt))
json.dump(plan,open('plan.json','w'),indent=0)
for p in plan: print(p['sym'],p['day'],p['side'],p['K'],p['exp1'])
print(len(plan))
