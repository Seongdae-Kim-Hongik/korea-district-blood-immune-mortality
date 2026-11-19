#!/usr/bin/env python3
# 55D — BLDD 전국 기술(2026-11-14, 47D_sknd 복제 + 2025): 성×5세 사망자수·사망률(DT_1B34E01 2011–24 long + 2025 55N) → 직접표준화율(2020 전국 인구 표준, 18구간 85+), 연령·성 구성, 세부 사인(D50-D64 빈혈 대 D65-D89).
#  산출: 04_분석/BLDD/results_desc/S55D_national.csv, S55D_agesex.csv
import os, pandas as pd, numpy as np
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); O=f"{R}/04_분석/BLDD/results_desc"; os.makedirs(O,exist_ok=True)
N=pd.read_csv(f"{R}/00_원천/D_사망_인구_암/DT_1B34E01_national_long.csv",encoding="utf-8-sig")
import json
d25=json.load(open(f"{R}/00_원천/D_사망_인구_암/DT_1B34E01_national/2025.json",encoding="utf-8"))
N25=pd.DataFrame([dict(year=int(r["PRD_DE"]),cause_code=r["C1"],cause=r["C1_NM"],sex=r["C2_NM"],age_code=r["C3"],age=r["C3_NM"],item=r["ITM_NM"],value=pd.to_numeric(r["DT"],errors="coerce")) for r in d25])
N=pd.concat([N,N25],ignore_index=True)
B=['0세','1 - 4세']+[f"{a} - {a+4}세" for a in range(5,85,5)]+['85 - 89세','90세이상']
s=N[N.cause.str.contains('D50-D89')&N.age.isin(B)&N.year.between(2011,2025)]
d=s.pivot_table(index=['year','sex','age'],columns='item',values='value',aggfunc='sum').reset_index()
P=N[N.age.isin(B)&N.year.between(2011,2025)].pivot_table(index=['year','sex','age','cause'],columns='item',values='value',aggfunc='sum').reset_index()
P=P[(P['사망률']>0)&(P['사망자수']>=20)]; P['pop']=P['사망자수']/P['사망률']*1e5; pp=P.groupby(['year','sex','age'])['pop'].median()
d['pop']=d.set_index(['year','sex','age']).index.map(pp)
def band(a): return '0-4' if a in ('0세','1 - 4세') else ('85+' if a in ('85 - 89세','90세이상') else a.replace(' - ','-').replace('세',''))
d['band']=d.age.map(band); g=d.groupby(['year','sex','band'])[['사망자수','pop']].sum().reset_index()
std=g[(g.year==2020)&(g.sex=='계')].set_index('band')['pop']; w=std/std.sum()
rows=[]
for (y,sx),h in g.groupby(['year','sex']):
    h=h.set_index('band'); r=(h['사망자수']/h['pop']*1e5); rows.append(dict(year=y,sex=sx,deaths=int(h['사망자수'].sum()),crude=round(h['사망자수'].sum()/h['pop'].sum()*1e5,3),asr_2020=round(float((r*w).sum()),3),share85=round(h.loc['85+','사망자수']/h['사망자수'].sum(),3)))
T=pd.DataFrame(rows); T.to_csv(f"{O}/S55D_national.csv",index=False); print(T[T.sex=='계'].to_string(index=False)); print(T[T.sex!='계'].pivot(index='year',columns='sex',values='asr_2020'))
g.to_csv(f"{O}/S55D_agesex.csv",index=False)
a=g[g.sex!='계'].groupby(['sex','band'])['사망자수'].sum().unstack(0); tot=a.values.sum(); print("성 비중", (a.sum()/tot).round(3).to_dict()); print("65+ 비중", round(a.loc[[f"{x}-{x+4}" for x in range(65,85,5)]+['85+']].values.sum()/tot,3), "80+", round(a.loc[['80-84','85+']].values.sum()/tot,3))
sub=N[(N.sex=='계')&(N.age=='계')&(N.item=='사망자수')&N.cause.str.contains('D50-D89|D65-D89|빈혈')]
print(sub.pivot_table(index='year',columns='cause',values='value').to_string())
# 세부 사인(빈혈 D50-D64 대 나머지 D65-D89) 연도별 → S55D_subcause.csv
pv=sub.pivot_table(index='year',columns='cause',values='value'); cA=[c for c in pv.columns if 'D50-D64' in c][0]; cR=[c for c in pv.columns if 'D65-D89' in c][0]; cT=[c for c in pv.columns if 'D50-D89' in c][0]
pd.DataFrame({'year':pv.index.astype(int),'anaemia':pv[cA].values,'rest':pv[cR].values,'total':pv[cT].values}).to_csv(f"{O}/S55D_subcause.csv",index=False)
