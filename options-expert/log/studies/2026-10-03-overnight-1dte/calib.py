exec(open('analyze.py').read().split('R={}')[0])
d5=by_day(m5['SPY']); d30=by_day(m30['SPY'])
# night: (entry day, next day, K, call close 3:55 bar, put close, call 9:30, put 9:30, call 9:45, put 9:45)
N_=[('2026-09-23','2026-09-24',768,1.77,1.84,0.36,3.62,0.31,3.65),
    ('2026-09-24','2026-09-25',767,2.41,1.88,3.02,0.67,2.96,0.47),
    ('2026-09-29','2026-09-30',764,2.52,1.98,3.42,0.67,3.27,0.64),
    ('2026-09-30','2026-10-01',762,3.63,2.11,3.55,0.80,2.65,1.23),
    ('2026-10-01','2026-10-02',764,2.74,2.40,6.25,0.29,7.74,0.15)]
u=1/(252*1.25)
print('night       S_close K  straddle%  | model straddle: calendar  trading | 2-4PM sig | ACTUAL return on signal side: sell 9:30 / 9:45 | other side 9:30/9:45')
for a,b,K,c0,p0,c930,p930,c945,p945 in N_:
    S=d5[a][-1][4]; s=vix[a]/100
    m_cal=bs(S,K,24/8760,s,1)+bs(S,K,24/8760,s,0); m_tr=bs(S,K,1.25*u,s,1)+bs(S,K,1.25*u,s,0)
    bars=d30[a]; two=[r for r in bars if r[0]=='14:00'][0]; sig=sgn(bars[-1][4]-two[1])
    sc,sp=( (c0,c930,c945),(p0,p930,p945) ) if sig>0 else ((p0,p930,p945),(c0,c930,c945))
    r=lambda t:f'{(t[1]/t[0]-1)*100:+.0f}% / {(t[2]/t[0]-1)*100:+.0f}%'
    print(a, f'{S:.2f} {K} {(c0+p0)/S*100:.2f}%  | {m_cal/S*100:.2f}% {m_tr/S*100:.2f}% | {"CALL" if sig>0 else "PUT"} | {r(sc)} | {r(sp)}  gap {(d5[b][0][1]/S-1)*100:+.2f}%')
# time-value decay check: actual straddle next morning minus intrinsic vs model
print('\nTime value left at 9:45 (straddle - intrinsic), actual vs model:')
for a,b,K,c0,p0,c930,p930,c945,p945 in N_:
    S=d5[a][-1][4]; s=vix[a]/100; S945=d5[b][2][4]
    tv_act=c945+p945-abs(S945-K)
    tv0=c0+p0-abs(S-K)
    m_cal=bs(S945,K,6.25/8760,s,1)+bs(S945,K,6.25/8760,s,0)-abs(S945-K)
    m_tr=bs(S945,K,(1-0.25/6.5)*u,s,1)+bs(S945,K,(1-0.25/6.5)*u,s,0)-abs(S945-K)
    print(a,f'close TV {tv0:.2f} -> 9:45 TV actual {tv_act:.2f} | model cal {m_cal:.2f} trading {m_tr:.2f} | S945-K {S945-K:+.2f}')
