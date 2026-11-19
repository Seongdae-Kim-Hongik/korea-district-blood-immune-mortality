#!/usr/bin/env python3
# 55E — BLDD(혈액·조혈기관·면역 사망 D50-D89): 2011–2025 시군구 사망 수와 성×18연령 간접표준화 E (2026-11-14).
#  사망 수: 99R_next5c_mort_counts.py 규칙(원표 DT_1B34E13 정리본 → 50.load_source 일반구 합산·코드표 결합)을 2011–2025로. 검산: 계 = 기준 SQLite region_year 전체 사망 229×15칸.
#  E 2011–2024 = 02_패널/BLDD_Estd3r.csv E_std(99R_next5c_mort_E, FBD_DATA_ZIP 창원 정정 성×18연령) 그대로.
#  E 2025 = KOSIS DT_1B04005N 2025-12 성×5세(85+ 합) 구성 × 기준 SQLite region_year 2025 인구 재척도 × 전국 DT_1B34E01 2025 사인×성×연령 율, ΣE = Σcases.
#    시군구 대응 = 값 일치 대응표(02_패널/SCRT_kosis_crosswalk_2025.csv, 코드 결합). 검산: 같은 방법으로 2024-12 KOSIS로 만든 2024 E 대 E_std 상관.
#  80세 이상 비율 2025 = KOSIS 2025-12(80+ ÷ 계). 산출: 02_패널/BLDD_Estd25.csv
import os, sqlite3, unicodedata, importlib.util, numpy as np, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); PAN = os.path.join(ROOT, "02_패널")
DB = os.path.expandvars("$ST_GPT_DATASET") + "/02_체육건강_시공간_GPT버전/02_체육건강_시공간_GPT버전.sqlite"
KD = os.path.join(ROOT, "00_원천", "D_KOSIS_인구2025")
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
# ── 사망 수 2011–2025 ──
CODES = {"0": "total_chk", "3": "bldd"}
L = pd.read_parquet(os.path.join(PAN, "사망원인_시군구_연도_사인_성_long.parquet"), columns=["year", "sido", "sigungu", "sgg_code", "sgg_code_std", "level", "parent_code", "code_note", "cause_code", "sex", "deaths"])
L = L[(L.sex == "계") & L.year.between(2011, 2025) & L.cause_code.isin(list(CODES))].copy(); L["v"] = L.cause_code.map(CODES)
IDX = ["year", "sido", "sigungu", "sgg_code", "sgg_code_std", "level", "parent_code", "code_note"]
for c in IDX[1:]: L[c] = L[c].fillna("").astype(str)
W = L.pivot_table(index=IDX, columns="v", values="deaths", aggfunc="sum").reset_index().replace({"": np.nan}); W = W[W.level.notna()]
tmpf = "_tmp_bldd55_mort_wide.csv"; W.to_csv(os.path.join(PAN, tmpf), index=False, encoding="utf-8-sig")
spec = importlib.util.spec_from_file_location("m50", os.path.join(HERE, "50_build_master_panel.py")); m50 = importlib.util.module_from_spec(spec); spec.loader.exec_module(m50)
mk = pd.read_csv(os.path.join(PAN, "시군구_마스터키.csv"), dtype=str); mk = mk[mk.fbd_sido.notna()].drop_duplicates("key")
log = dict(missing_files=[], level_filter={}, unmatched=[], special=[], overlap=[], sources={})
src = dict(name="mortbldd", prefix="", files=[tmpf], sido="sido", sgg="sigungu", merge_counts=True, level="시군구", ratio=lambda c: False, label="사망원인통계")
agg, meta = m50.load_source(src, set(mk.key), log); os.remove(os.path.join(PAN, tmpf))
agg = agg.merge(mk[["key", "fbd_region"]], on="key", how="left"); agg["fbd_region"] = agg.fbd_region.map(NFC); agg["year"] = agg.year.astype(int)
R = pd.read_sql('select year, fbd_region, population, "mort__전체사망_deaths" as total from region_year where year between 2011 and 2025', con); R["fbd_region"] = R.fbd_region.map(NFC)
M = R.merge(agg[["year", "fbd_region", "total_chk", "bldd"]], on=["year", "fbd_region"], how="left", validate="one_to_one")
assert len(M) == 229 * 15 and M.total_chk.notna().all() and (M.total_chk == M.total).all(), "원표 계 ≠ 기준 SQLite 전체 사망"
M["bldd"] = M.bldd.fillna(0).astype(int)
print("[55E] 계 = 기준 SQLite 229×15칸 일치. 연도별 BLDD", M.groupby("year").bldd.sum().to_dict())
# 이전 3차 풀(2011–2024)과 같은지
X = pd.read_csv(os.path.join(PAN, "BLDD_Estd3r.csv"), encoding="utf-8-sig"); X["fbd_region"] = X.fbd_region.map(NFC)
chk = M[M.year <= 2024].merge(X[["year", "fbd_region", "cases", "E_std"]], on=["year", "fbd_region"], validate="one_to_one")
assert len(chk) == 3206 and (chk.cases == chk.bldd).all(), "2011–2024 사망 수 ≠ BLDD_Estd3r"
# 세종
base = pd.read_sql("select distinct fbd_region, sigungu_cd from disease_panel where tag='PERIO'", con); base["fbd_region"] = base.fbd_region.map(NFC); base["sigungu_cd"] = base.sigungu_cd.astype(str)
assert base.fbd_region.nunique() == 229 and base.sigungu_cd.nunique() == 229
M = M.merge(base, on="fbd_region", how="left"); assert M.sigungu_cd.notna().all()
print("[55E] 세종(29010) 연도별 사망", M[M.sigungu_cd == "29010"].set_index("year").bldd.to_dict(), "인구 2012", int(M[(M.sigungu_cd == "29010") & (M.year == 2012)].population.iat[0]))
assert (M.sigungu_cd == "29010").sum() == 15
# ── 2025 E ──
B18 = [f"{lo}-{lo+4}" for lo in range(0, 85, 5)] + ["85+"]
def band(a):
    a = a.replace(" ", "")
    if a in ("0세", "1-4세", "0-4세"): return "0-4"
    if a in ("85-89세", "90세이상", "90-94세", "95-99세", "100+"): return "85+"
    if a.endswith("세") and "-" in a:
        lo, hi = a[:-1].split("-")
        if int(hi) - int(lo) == 4 and int(lo) <= 80: return f"{lo}-{hi}"
    return None
CW = pd.read_csv(os.path.join(PAN, "SCRT_kosis_crosswalk_2025.csv"), dtype=str, encoding="utf-8-sig"); assert CW.sigungu_cd.nunique() == 229 and set(CW.sigungu_cd) == set(base.sigungu_cd)
def kpop(ym):
    K = pd.read_csv(os.path.join(KD, f"DT_1B04005N_{ym}.csv"), dtype=str, encoding="utf-8-sig"); K = K[(K.C1.str.len() == 5) & (K.C2 != "0")].copy()
    K["band"] = K.C2_NM.map(band); assert K.band.notna().all(), K[K.band.isna()].C2_NM.unique()
    K["sex"] = K.ITM_ID.map({"T3": "남자", "T4": "여자"}); K["v"] = pd.to_numeric(K.DT)
    K = K.merge(CW, left_on=["C1", "C1_NM"], right_on=["kosis_C1", "kosis_C1_NM"]); assert K.sigungu_cd.nunique() == 229
    return K.pivot_table(index=["sigungu_cd", "sex"], columns="band", values="v", aggfunc="sum")[B18]
def nat(df, y):
    d = df[(df.year == y) & df.sex.isin(["남자", "여자"]) & (df.item == "사망자수") & df.cause.str.contains("D50-D89")].copy(); d["band"] = d.age.map(band)
    tot = d[d.age == "계"].groupby("sex").value.sum(); unk = d[d.age == "연령미상"].groupby("sex").value.sum().reindex(tot.index).fillna(0)
    nb = d[d.band.notna()].groupby(["sex", "band"]).value.sum().unstack()[B18]; assert ((nb.sum(axis=1) + unk - tot).abs() <= 1).all(); return nb
NL = pd.read_csv(os.path.join(ROOT, "00_원천", "D_사망_인구_암", "DT_1B34E01_national_long.csv"), encoding="utf-8-sig")
N25 = pd.read_csv(os.path.join(PAN, "BLDD_national_2025_long.csv"), encoding="utf-8-sig")
def Ey(y, ym, natdf):
    P = kpop(ym); pop = M[M.year == y].set_index("sigungu_cd").population
    adj = pop / P.groupby(level=0).sum().sum(axis=1); P = P.mul(P.index.get_level_values(0).map(adj).values, axis=0)
    nb = nat(natdf, y); rate = nb / P.groupby(level="sex").sum()
    e = (P * rate.loc[P.index.get_level_values("sex")].values).sum(axis=1).groupby(level=0).sum()
    cs = M[M.year == y].set_index("sigungu_cd").bldd; e = e * cs.sum() / e.sum(); return e, adj
e24, a24 = Ey(2024, "202412", NL); e25, a25 = Ey(2025, "202512", N25)
v = chk[chk.year == 2024].merge(base, on="fbd_region"); v["e_k"] = v.sigungu_cd.map(e24)
print("[55E] 검산 2024 E(KOSIS 2024-12 경로) 대 E_std: 상관", round(float(np.corrcoef(v.e_k, v.E_std)[0, 1]), 5), "비 범위", np.round((v.e_k / v.E_std).describe()[["min", "50%", "max"]].values, 4).tolist())
print("[55E] 2025 인구 재척도 비(region_year/KOSIS) 범위", np.round(a25.describe()[["min", "50%", "max"]].values, 4).tolist())
M["E_std"] = M.set_index(["year", "fbd_region"]).index.map(X.set_index(["year", "fbd_region"]).E_std)
m = M.year == 2025; M.loc[m, "E_std"] = M.loc[m, "sigungu_cd"].map(e25).values
assert M.E_std.notna().all() and (M.E_std > 0).all()
# 80+ 비율
K = pd.read_csv(os.path.join(KD, "DT_1B04005N_202512.csv"), dtype=str, encoding="utf-8-sig"); K = K[K.C1.str.len() == 5].copy(); K["v"] = pd.to_numeric(K.DT)
K = K.merge(CW, left_on=["C1", "C1_NM"], right_on=["kosis_C1", "kosis_C1_NM"]); tot = K[K.C2 == "0"].groupby("sigungu_cd").v.sum()
lo = K[K.C2 != "0"].copy(); lo["a"] = lo.C2_NM.str.extract(r"^(\d+)")[0].astype(float); p80 = 100 * lo[lo.a >= 80].groupby("sigungu_cd").v.sum() / tot
M["pop80_share_kosis2025"] = np.where(m, M.sigungu_cd.map(p80), np.nan)
M = M.rename(columns={"bldd": "cases", "population": "offset"})
M["E_crude"] = M.offset * M.year.map(M.groupby("year").cases.sum() / M.groupby("year").offset.sum())   # 민감도 sc(조 E)
M[["year", "fbd_region", "sigungu_cd", "offset", "cases", "E_std", "E_crude", "total_chk", "pop80_share_kosis2025"]].sort_values(["year", "fbd_region"]).to_csv(os.path.join(PAN, "BLDD_Estd25.csv"), index=False, encoding="utf-8-sig")
print("[55E] 저장 02_패널/BLDD_Estd25.csv", len(M), "0칸", int((M.cases == 0).sum()), "합", int(M.cases.sum()))
