import json, math, statistics as st
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict
TR='/root/.claude/projects/-home-user-AgentTradeProcess/c58fd6c0-b5b4-5f81-9ee1-5a646943424a/tool-results/mcp-Robinhood-'
NY=ZoneInfo('America/New_York')
def load(fid, kind='get_equity_historicals'):
    d=json.load(open(f'{TR}{kind}-{fid}.txt'))
    out={}
    for r in d['data']['results']:
        out[r['symbol']]=[x for x in r['bars'] if not x.get('interpolated')]
    return out
def et(s): return datetime.fromisoformat(s.replace('Z','+00:00')).astimezone(NY)
F=lambda x:float(x)

# ---------- daily (2y) ----------
daily=load('1790993242837')
# ---------- 30-minute ----------
m30=defaultdict(list)
for fid in ['1790993239942','1790993241976']:
    for s,b in load(fid).items(): m30[s]+=b
# ---------- 5-minute ----------
m5=defaultdict(list)
for fid in ['1790993119913','1790993120940','1790993121858','1790993123087','1790993123957','1790993124915','1790993125969','1790993126848']:
    for s,b in load(fid).items(): m5[s]+=b
vix={x['begins_at'][:10]:F(x['close_value']) for x in json.load(open(TR+'get_index_historicals-1790993296277.txt'))['data']['results'][0]['bars'] if not x.get('interpolated')}

def by_day(bars):
    d=defaultdict(list)
    for x in bars:
        t=et(x['begins_at']); d[t.date().isoformat()].append((t.strftime('%H:%M'),F(x['open_price']),F(x['high_price']),F(x['low_price']),F(x['close_price'])))
    return {k:sorted(v) for k,v in d.items()}

def ci(k,n):
    if n==0: return 'n=0'
    p=k/n; h=1.96*math.sqrt(p*(1-p)/n)
    return f'{k}/{n} = {100*p:.1f}% (95% CI {100*(p-h):.0f}-{100*(p+h):.0f}%)'
sgn=lambda v:(v>0)-(v<0)
N=lambda x:0.5*(1+math.erf(x/math.sqrt(2)))
def bs(S,K,T,sig,call):
    if T<=0: return max(0,(S-K) if call else (K-S))
    d1=(math.log(S/K)+0.5*sig*sig*T)/(sig*math.sqrt(T)); d2=d1-sig*math.sqrt(T)
    return S*N(d1)-K*N(d2) if call else K*N(-d2)-S*N(-d1)

R={}
out=[]
P=lambda *a: out.append(' '.join(str(x) for x in a))
for sym in ['SPY','QQQ']:
    P(f'\n================ {sym} ================')
    # daily table, append 10/02 from 5-min
    D={}
    for x in daily[sym]:
        D[x['begins_at'][:10]]=(F(x['open_price']),F(x['high_price']),F(x['low_price']),F(x['close_price']))
    d5=by_day(m5[sym]); d30=by_day(m30[sym])
    if '2026-10-02' not in D and '2026-10-02' in d5:
        b=d5['2026-10-02']; D['2026-10-02']=(b[0][1],max(r[2] for r in b),min(r[3] for r in b),b[-1][4])
    days=sorted(D)
    # sanity: daily close vs 5-min last close
    mism=[(d,D[d][3],d5[d][-1][4]) for d in d5 if d in D and abs(D[d][3]-d5[d][-1][4])>0.05]
    P('daily-vs-5min close mismatches >5c:',len(mism),mism[:3])
    P('daily days',len(days),days[0],days[-1],'| 30m days',len(d30),min(d30),max(d30),'| 5m days',len(d5),min(d5),max(d5))
    # gaps
    gaps={}  # day d -> gap% into next day
    for a,b in zip(days,days[1:]):
        gaps[a]=(D[b][0]/D[a][3]-1)*100
    G=list(gaps.values())
    up=sum(1 for g in G if g>0)
    P('\n-- BASE RATES (2y daily) --')
    P('gap up nights:',ci(up,len(G)))
    ab=sorted(abs(g) for g in G)
    q=lambda p:ab[int(p*(len(ab)-1))]
    P(f'|gap| %: median {q(.5):.2f}  p25 {q(.25):.2f}  p75 {q(.75):.2f}  p90 {q(.9):.2f}  max {ab[-1]:.2f}')
    # realized vol ratio for QQQ IV proxy
    rets={b:math.log(D[b][3]/D[a][3]) for a,b in zip(days,days[1:])}
    R[sym]=dict(D=D,days=days,gaps=gaps,rets=rets,d5=d5,d30=d30)

    # ---------- A1: day direction -> gap sign (2y) ----------
    k=n=0
    for a in days[:-1]:
        o,h,l,c=D[a]; s=sgn(c-o); g=sgn(gaps[a])
        if s==0 or g==0: continue
        n+=1; k+= s==g
    P('\n-- A1 day direction (open->close) predicts gap sign, 2y --'); P(ci(k,n))
    # ---------- H1: 2pm->4pm ----------
    k=n=0; kc=nc=0
    H1sig={}
    d30days=sorted(d30)
    for a,b in zip(d30days,d30days[1:]):
        bars=d30[a]
        if len(bars)!=13 or a not in gaps: continue
        two=[r for r in bars if r[0]=='14:00']
        if not two: continue
        aft=bars[-1][4]-two[0][1]; s=sgn(aft); g=sgn(gaps[a])
        H1sig[a]=s
        if s==0 or g==0: continue
        n+=1; k+= s==g
    P('\n-- H1 2:00->4:00 PM direction predicts next gap sign (30m data) --'); P(ci(k,n))
    gu=sum(1 for a in H1sig if gaps[a]>0); P('  same-window base rate gap-up:',ci(gu,len(H1sig)))
    # by direction
    for want,lab in [(1,'afternoon UP -> gap up'),(-1,'afternoon DOWN -> gap down')]:
        kk=sum(1 for a,s in H1sig.items() if s==want and sgn(gaps[a])==want); nn=sum(1 for a,s in H1sig.items() if s==want and gaps[a]!=0)
        P('  ',lab,ci(kk,nn))
    R[sym]['H1sig']=H1sig

    # ---------- H2: trend filter ----------
    # true 4h from 30m: 9:30-13:00 bars (8) and 13:30-15:30 (5)
    c4=[]  # (day, close of 2nd 4h bar) sequence of closes
    seq=[]
    for a in d30days:
        bars=d30[a]
        if len(bars)!=13: continue
        seq.append((a,1,bars[7][4])); seq.append((a,2,bars[12][4]))
    sma4={}
    for i in range(179,len(seq)):
        if seq[i][1]==2: sma4[seq[i][0]]=sum(x[2] for x in seq[i-179:i+1])/180
    P('\n-- H2 trend filter --')
    P('  true 4h-180SMA available days:',len(sma4), (min(sma4),max(sma4)) if sma4 else '')
    def trend_test(sig, trend, label):
        # trend-alone
        kk=nn=0; kf=nf=0
        for a,s in sig.items():
            if a not in trend or a not in gaps or gaps[a]==0: continue
            t=trend[a]; g=sgn(gaps[a])
            nn+=1; kk+= t==g
            if s!=0 and s==t: nf+=1; kf+= s==g
        P(f'  {label}: trend alone predicts gap {ci(kk,nn)} | signal WITH trend {ci(kf,nf)}')
    tr4={a:sgn(R[sym]['D'][a][3]-v) for a,v in sma4.items() if a in R[sym]['D']}
    trend_test(H1sig,tr4,'H1 sig + true 4h SMA180')
    # proxy: 90-day SMA daily
    tr90={}
    for i in range(89,len(days)):
        tr90[days[i]]=sgn(D[days[i]][3]-sum(D[x][3] for x in days[i-89:i+1])/90)
    daysig={a:sgn(D[a][3]-D[a][0]) for a in days}
    trend_test(daysig,tr90,'A1 day-dir + daily SMA90 proxy (2y)')
    trend_test(H1sig,tr90,'H1 sig + daily SMA90 proxy')
    R[sym]['tr90']=tr90; R[sym]['daysig']=daysig

# ---------- IV ----------
def iv(sym,a):
    v=vix.get(a)
    if v is None: return None
    s=v/100
    if sym=='QQQ':
        days=R['SPY']['days']; i=days.index(a) if a in days else None
        if i is None or i<21: return None
        w=days[i-19:i+1]
        rq=[R['QQQ']['rets'].get(x) for x in w]; rs=[R['SPY']['rets'].get(x) for x in w]
        if None in rq or None in rs: return None
        s*= st.pstdev(rq)/st.pstdev(rs)
    return s

# ---------- H3 + P&L simulation ----------
for sym in ['SPY','QQQ']:
    D=R[sym]['D']; days=R[sym]['days']; gaps=R[sym]['gaps']; d5=R[sym]['d5']
    P(f'\n================ {sym} H3 cost & P&L (ESTIMATE, Black-Scholes, IV=VIX{"*QQQ/SPY realized ratio" if sym=="QQQ" else ""}) ================')
    spread=0.02 if sym=='SPY' else 0.03
    for conv in ['calendar','trading(overnight=0.25 session)']:
        for sigsrc,label in [('day','signal=day direction (2y)'),('h1','signal=2-4PM direction (Jan30+)'),('call','always CALL (2y)')]:
            rets930=[]; rets945=[]; costs=[]; wins=0
            for a,b in zip(days,days[1:]):
                sig = R[sym]['daysig'][a] if sigsrc=='day' else (R[sym]['H1sig'].get(a) if sigsrc=='h1' else 1)
                if not sig: continue
                s=iv(sym,a)
                if s is None: continue
                S0=D[a][3]; K=round(S0); call=sig>0
                cal_days=(datetime.fromisoformat(b)-datetime.fromisoformat(a)).days
                if conv=='calendar':
                    T0=(24*cal_days)/8760; T930=6.5/8760; T945=6.25/8760
                else:
                    u=1/(252*1.25)  # one 'unit' of variance-time, year = 252*(1+0.25)
                    T0=(1+0.25*cal_days)*u; T930=1*u; T945=(1-0.25/6.5)*u
                c0=bs(S0,K,T0,s,call)+spread/2
                costs.append(c0/S0*100)
                S1=D[b][0]; v930=bs(S1,K,T930,s,call)-spread/2
                r930=(v930/c0-1)*100; rets930.append(r930)
                if b in d5:
                    S945=d5[b][2][4]  # close of 9:40 bar = 9:45 price
                    v945=bs(S945,K,T945,s,call)-spread/2; rets945.append((v945/c0-1)*100)
            if not rets930: continue
            w=sum(1 for r in rets930 if r>0)
            P(f'[{conv}] {label}: n={len(rets930)} cost median {st.median(costs):.2f}% of price | sell 9:30: win {100*w/len(rets930):.0f}%, median {st.median(rets930):+.0f}%, MEAN {st.mean(rets930):+.1f}% of premium'
              + (f' | sell 9:45 (n={len(rets945)}): win {100*sum(1 for r in rets945 if r>0)/len(rets945):.0f}%, mean {st.mean(rets945):+.1f}%' if rets945 else ''))

# ---------- H4 / H5 (5-minute) ----------
for sym in ['SPY','QQQ']:
    D=R[sym]['D']; gaps=R[sym]['gaps']; d5=R[sym]['d5']; H1sig=R[sym]['H1sig']
    P(f'\n================ {sym} H4/H5 first 15 minutes (5m data) ================')
    ext=n4=0; mfe=[]; giveback=0
    rev=n5=0; revday=0
    for a,sig in H1sig.items():
        b=None
        days=R[sym]['days']
        if a not in days: continue
        i=days.index(a)
        if i+1>=len(days): continue
        b=days[i+1]
        if b not in d5 or not sig or gaps[a]==0: continue
        bars=d5[b]; o=bars[0][1]; p945=bars[2][4]; close=bars[-1][4]
        hi=max(r[2] for r in bars[:3]); lo=min(r[3] for r in bars[:3])
        if sgn(gaps[a])==sig:   # gap in our favour
            n4+=1
            if (p945-o)*sig>0: ext+=1
            mfe.append(((hi-o) if sig>0 else (o-lo))/o*100)
        else:                   # gap against us -> reverse = trade in gap direction (-sig)
            n5+=1
            if (p945-o)*(-sig)>0: rev+=1
            if (close-p945)*(-sig)>0: revday+=1
    P('H4 favourable gap: 9:45 better than 9:30 open:',ci(ext,n4))
    if mfe: P(f'   best price inside first 15 min vs open: median {st.median(mfe):.2f}% (you will not catch the exact best)')
    P('H5 adverse gap: first 15 min continues AGAINST original idea (reversal pays by 9:45):',ci(rev,n5))
    P('   reversal entered 9:45, held to close, pays:',ci(revday,n5))
print('\n'.join(out))
