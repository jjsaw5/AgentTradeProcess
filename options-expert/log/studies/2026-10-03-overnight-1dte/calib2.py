exec(open('analyze.py').read().split("# ---------- H3 + P&L simulation")[0].replace("print('\\n'.join(out))",""))
exec(open('calib.py').read().split("u=1/(252*1.25)")[0].split("d5=by_day")[1].join(["d5=by_day",""]) if False else "")
d5s=R['SPY']['d5']; d30s=R['SPY']['d30']
N_=[('2026-09-23','2026-09-24',768,1.77,1.84,0.36,3.62,0.31,3.65),
    ('2026-09-24','2026-09-25',767,2.41,1.88,3.02,0.67,2.96,0.47),
    ('2026-09-29','2026-09-30',764,2.52,1.98,3.42,0.67,3.27,0.64),
    ('2026-09-30','2026-10-01',762,3.63,2.11,3.55,0.80,2.65,1.23),
    ('2026-10-01','2026-10-02',764,2.74,2.40,6.25,0.29,7.74,0.15)]
# fit: entry IV mult, exit IV mult (calendar time) minimizing squared error on all 4 prices per night
best=None
for ki in [x/100 for x in range(60,131,2)]:
  for ko in [x/100 for x in range(80,221,5)]:
    err=0
    for a,b,K,c0,p0,c930,p930,c945,p945 in N_:
      S=d5s[a][-1][4]; s=vix[a]/100; S945=d5s[b][2][4]
      err+=(bs(S,K,24/8760,s*ki,1)-c0)**2+(bs(S,K,24/8760,s*ki,0)-p0)**2+(bs(S945,K,6.25/8760,s*ko,1)-c945)**2+(bs(S945,K,6.25/8760,s*ko,0)-p945)**2
    if best is None or err<best[0]: best=(err,ki,ko)
print('fit (calendar time): entry IV = VIX x %.2f, 9:45 IV = VIX x %.2f, rms err $%.2f'%(best[1],best[2],math.sqrt(best[0]/20)))
ki,ko=best[1],best[2]
for a,b,K,c0,p0,c930,p930,c945,p945 in N_:
    S=d5s[a][-1][4]; s=vix[a]/100; S945=d5s[b][2][4]
    print(a,'call act %.2f->%.2f model %.2f->%.2f | put act %.2f->%.2f model %.2f->%.2f'%(c0,c945,bs(S,K,24/8760,s*ki,1),bs(S945,K,6.25/8760,s*ko,1),p0,p945,bs(S,K,24/8760,s*ki,0),bs(S945,K,6.25/8760,s*ko,0)))
# rerun 2y sim with fitted model, exit 9:45 only possible on 5m days; 9:30 use ko too
for sym in ['SPY','QQQ']:
  D=R[sym]['D']; days=R[sym]['days']; d5=R[sym]['d5']
  spread=0.02 if sym=='SPY' else 0.03
  for sigsrc,label in [('day','day direction (2y)'),('h1','2-4PM direction (Jan30+)'),('call','always CALL (2y)'),('put','always PUT (2y)')]:
    r930=[];r945=[];g=[]
    for a,b in zip(days,days[1:]):
      sig={'day':R[sym]['daysig'].get(a),'h1':R[sym]['H1sig'].get(a),'call':1,'put':-1}[sigsrc]
      if not sig: continue
      s=iv(sym,a)
      if s is None: continue
      S0=D[a][3];K=round(S0);call=sig>0
      cd=(datetime.fromisoformat(b)-datetime.fromisoformat(a)).days
      c0=bs(S0,K,24*cd/8760,s*ki,call)+spread/2
      v=bs(D[b][0],K,6.5/8760,s*ko,call)-spread/2; r930.append((v/c0-1)*100)
      if b in d5:
        v=bs(d5[b][2][4],K,6.25/8760,s*ko,call)-spread/2; r945.append((v/c0-1)*100)
    w=lambda L:100*sum(1 for x in L if x>0)/len(L)
    print(f'{sym} FITTED {label}: n={len(r930)} sell 9:30 win {w(r930):.0f}% median {st.median(r930):+.0f}% MEAN {st.mean(r930):+.1f}% | sell 9:45 n={len(r945)} win {w(r945):.0f}% mean {st.mean(r945):+.1f}%')
print()
for sym in ['SPY','QQQ']:
  D=R[sym]['D']; days=R[sym]['days']; gaps=R[sym]['gaps']
  right=[];wrong=[]; big=[]
  for a,b in zip(days,days[1:]):
    s=iv(sym,a)
    if s is None or gaps[a]==0: continue
    sig=sgn(gaps[a])  # perfect-foresight side, and wrong side
    S0=D[a][3];K=round(S0);cd=(datetime.fromisoformat(b)-datetime.fromisoformat(a)).days
    for side,L in [(sig,right),(-sig,wrong)]:
      c0=bs(S0,K,24*cd/8760,s*ki,side>0)+0.01
      v=bs(D[b][0],K,6.5/8760,s*ko,side>0)-0.01; L.append((v/c0-1)*100)
  mr,mw=st.mean(right),st.mean(wrong)
  print(f'{sym}: right side mean {mr:+.0f}% (median {st.median(right):+.0f}%), wrong side mean {mw:+.0f}%  -> breakeven hit rate {100*-mw/(mr-mw):.0f}%; right-side still loses on {100*sum(1 for x in right if x<=0)/len(right):.0f}% of nights')
