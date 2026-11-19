#!/usr/bin/env python3
# 99c — 혈액·조혈기관·면역 사망(BLDD, D50-D89) 공변량 풀, 2011–2025 (2026-11-14; 99c_extra_canonical_pool_scrt.py 구조 복제).
#  모든 모형 변수를 이 풀에서 명시적으로 공급(2025 값을 80 빌더가 조용히 채우지 않게). 시군구는 코드·대응표로만 결합.
#  ① 기준 02 SQLite region_year(229×2011–2025): 강제통제 4(도시지역 인구 비율·의사 수·성비·재정자주도), 종합병원, 음성대조 3, 검진 신장질환 의심 비율(민감도)
#  ② ALLD 풀(수급률 양쪽 규칙 33칸 정정판): 수급률·고등교육·내과 전문의(민감도)
#  ③ ANEM: 검진 빈혈 의심 성×연령 표준화비(SIR_std = 빈혈 의심 수 / E_std, 02_패널/ANEM_Estd3.csv, 2011–2024; 세종 전 연도 미관측 → 그해 전국 평균, 기록)
#  ④ 02_패널/BLDD_Estd25.csv: 사망 수·인구·E, 80세 이상 비율(2011–24 INFECT_Estd2 시리즈 공통, 2025 KOSIS DT_1B04005N 2025-12)
#  2025 규칙: region_year 2025 원값이 있으면 그대로, 없으면 2024 값 이월(LOCF)하고 칸 수를 기록(02_패널/EXT_canonical_pool_BLDD_2025rule.csv). 2011–2024 민감도는 체인에서 따로(y24).
import os, sqlite3, unicodedata, numpy as np, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); PAN = os.path.join(ROOT, "02_패널")
DB = os.path.expandvars("$ST_GPT_DATASET") + "/02_체육건강_시공간_GPT버전/02_체육건강_시공간_GPT버전.sqlite"
E = pd.read_csv(os.path.join(PAN, "BLDD_Estd25.csv"), encoding="utf-8-sig", dtype={"sigungu_cd": str}); E["fbd_region"] = E.fbd_region.map(NFC)
assert len(E) == 229 * 15 and E.groupby("year").sigungu_cd.nunique().eq(229).all() and (E.sigungu_cd == "29010").sum() == 15
out = E[["year", "fbd_region", "sigungu_cd", "offset", "cases", "pop80_share_kosis2025"]].rename(columns={"offset": "population", "cases": "bldd_deaths"})
RULE = []
def locf(col, src):
    m25 = (out.year == 2025) & out[col].isna(); v24 = out[out.year == 2024].set_index("fbd_region")[col]
    out.loc[m25, col] = out.loc[m25, "fbd_region"].map(v24).values
    RULE.append(dict(variable=col, source=src, n2025_observed=int(229 - m25.sum()), n2025_locf=int(m25.sum())))
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
RY = {"urban_pop": "eloc__DT_1YL20421E__1인당도시지역면적현황__도시지역인구", "physicians_per_1000": "eloc__DT_1YL20981__인구천명당의료기관종사의사수＜br＞(A÷B×1000)",
      "sex_ratio": "eloc__DT_1YL20701__남녀성비＜br＞(A÷B×100)", "fiscal_independence": "eloc__DT_1YL20891__재정자주도(세입과목개편전)",
      "genhosp_n": "chk__요양기관_종합병원",
      "kidney_suspect_share": "chk__질환의심_신장질환_수검자대비비율", "dm_suspect_share": "chk__질환의심_고혈압당뇨_당뇨병_수검자대비비율", "older_single_share": "eloc__DT_1YL12701__독거노인가구비율＜br＞(A÷B×100)",
      "hit_and_run_rate": "eloc__DT_1YL13901__뺑소니교통사고율＜br＞(A÷B×100)", "traffic_culture_index": "eloc__DT_1YL20331__지수__계",
      "fires_per_10000": "eloc__DT_1YL21081__주민만명당화재발생건수＜br＞(A÷B×10000)", "ry_population": "population"}
q = ", ".join(f'"{c}" as "{k}"' for k, c in RY.items())
R = pd.read_sql(f"select year, fbd_region, {q} from region_year where year between 2011 and 2025", con); R["fbd_region"] = R.fbd_region.map(NFC)
out = out.merge(R, on=["year", "fbd_region"], how="left", validate="one_to_one")
d = (out.population - out.ry_population).abs(); print("[99c-bldd] 인구 대 region_year 최대 차", float(d.max()), out.loc[d > 0, ["year", "fbd_region", "population", "ry_population"]].values.tolist()[:5])
for c in ["urban_pop", "genhosp_n"]:   # 수 → 2025 결측이면 2024 값 이월 후 비율화
    if out[out.year == 2025][c].notna().sum() < 229: locf(c, "region_year 2025 결측 → 2024 이월")
    else: RULE.append(dict(variable=c, source="region_year 2025 원값", n2025_observed=229, n2025_locf=0))
out["urban_population_share"] = 100 * out.urban_pop / out.population
out["genhosp_per100k"] = 1e5 * out.genhosp_n / out.population
for c in ["physicians_per_1000", "sex_ratio", "fiscal_independence", "kidney_suspect_share", "dm_suspect_share", "older_single_share", "hit_and_run_rate", "traffic_culture_index", "fires_per_10000"]:
    if out[out.year == 2025][c].notna().sum() < 229: locf(c, "region_year 2025 결측 칸 → 2024 이월")
    else: RULE.append(dict(variable=c, source="region_year 2025 원값", n2025_observed=229, n2025_locf=0))
A = pd.read_csv(os.path.join(PAN, "EXT_canonical_pool_ALLD_261112.csv"), encoding="utf-8-sig"); A["fbd_region"] = A.fbd_region.map(NFC)
X = pd.read_csv(os.path.join(PAN, "EXT_canonical_pool_ANEM_261111.csv"), encoding="utf-8-sig"); X["fbd_region"] = X.fbd_region.map(NFC)
out = out.merge(A[["year", "fbd_region", "basic_livelihood_rate", "tertiary_educated_share", "ltc_hospitals_per100k_65", "ill_defined_share"]], on=["year", "fbd_region"], how="left")
out = out.merge(X[["year", "fbd_region", "im_specialists_per100k", "unmet_need_rate"]], on=["year", "fbd_region"], how="left")
r = out.fbd_region.map(out[out.year.isin([2020, 2024])].groupby("fbd_region").basic_livelihood_rate.mean())
assert not (out.year.isin([2021, 2022, 2023]) & ((out.basic_livelihood_rate < 0.2 * r) | (out.basic_livelihood_rate > 5 * r))).any(), "수급률 정정 위반"
for c in ["basic_livelihood_rate", "tertiary_educated_share", "ltc_hospitals_per100k_65", "ill_defined_share"]: locf(c, "ALLD 풀 2024까지 → 2025 이월")
locf("im_specialists_per100k", "ANEM 풀 2024까지 → 2025 이월"); locf("unmet_need_rate", "ANEM 풀 2024까지 → 2025 이월")
AN = pd.read_csv(os.path.join(PAN, "ANEM_Estd3.csv"), encoding="utf-8-sig"); AN["fbd_region"] = AN.fbd_region.map(NFC)
out = out.merge(AN[["year", "fbd_region", "SIR_std"]].rename(columns={"SIR_std": "anaemia_suspect_sir"}), on=["year", "fbd_region"], how="left")
sj = out.sigungu_cd == "29010"; print("[99c-bldd] 빈혈 의심 SIR 결측(세종 포함)", int(out.anaemia_suspect_sir.isna().sum()), "세종", int(out[sj].anaemia_suspect_sir.isna().sum()))
locf("anaemia_suspect_sir", "ANEM SIR_std 2024까지 → 2025 이월")
P8 = pd.read_csv(os.path.join(PAN, "INFECT_Estd2.csv"), encoding="utf-8-sig"); P8["fbd_region"] = P8.fbd_region.map(NFC)
out = out.merge(P8[["year", "fbd_region", "pop80_share_raw"]].rename(columns={"pop80_share_raw": "pop80_share"}), on=["year", "fbd_region"], how="left")
m = out.year == 2025; out.loc[m, "pop80_share"] = out.loc[m, "pop80_share_kosis2025"]
RULE.append(dict(variable="pop80_share", source="2011–24 INFECT_Estd2(시리즈 공통), 2025 KOSIS DT_1B04005N 2025-12 원값", n2025_observed=229, n2025_locf=0))
keep = ["year", "fbd_region", "sigungu_cd", "population", "bldd_deaths", "pop80_share", "urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence",
        "basic_livelihood_rate", "tertiary_educated_share", "anaemia_suspect_sir", "genhosp_per100k",
        "kidney_suspect_share", "im_specialists_per100k", "ltc_hospitals_per100k_65", "ill_defined_share", "dm_suspect_share", "older_single_share", "unmet_need_rate", "hit_and_run_rate", "traffic_culture_index", "fires_per_10000"]
out = out[keep].sort_values(["fbd_region", "year"]).reset_index(drop=True)
miss = out.isna().sum(); print("[99c-bldd] 결측(보간 전)", miss[miss > 0].to_dict())
for c in keep[5:]:
    n = int(out[c].isna().sum())
    if n:
        out[c] = out.groupby("fbd_region")[c].transform(lambda s: s.interpolate(limit_direction="both")); n2 = int(out[c].isna().sum())
        if n2: out[c] = out[c].fillna(out.groupby("year")[c].transform("mean"))
        RULE.append(dict(variable=c, source=f"결측 {n}칸: 시군구 안 선형 보간(양끝 이월) {n - n2}칸, 전 연도 결측 시군구 {n2}칸 = 그해 전국 평균", n2025_observed=None, n2025_locf=None))
assert out.notna().all().all() and len(out) == 3435 and out.groupby("year").fbd_region.nunique().eq(229).all() and (out.sigungu_cd == "29010").sum() == 15
pd.DataFrame(RULE).to_csv(os.path.join(PAN, "EXT_canonical_pool_BLDD_2025rule.csv"), index=False, encoding="utf-8-sig")
out.to_csv(os.path.join(PAN, "EXT_canonical_pool_BLDD_261114.csv"), index=False, encoding="utf-8-sig")
print("[99c-bldd] 저장", out.shape); print(pd.DataFrame(RULE).to_string(index=False))
print(out[keep[5:]].describe().T[["mean", "min", "max"]].round(3).to_string())
