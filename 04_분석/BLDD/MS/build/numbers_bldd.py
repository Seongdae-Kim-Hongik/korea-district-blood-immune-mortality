# numbers_bldd.py — BLDD(D50-D89 혈액·조혈기관·면역 질환 사망, std3_main) 원고의 모든 수치를 결과 CSV에서 읽는다(2026-11-14, numbers_sknd.py 구조 이식). 손입력 금지, assert로 정합 확인.
import os, glob, numpy as np, pandas as pd
from scipy.stats import spearmanr
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(os.path.dirname(HERE)); RS = os.path.join(B, "results_std3_main"); DESC = os.path.join(B, "results_desc")
VER = "std3_main"
WIN = [("W1_2011-15", 2011, 2015), ("W2_2016-19", 2016, 2019), ("W3_2020-25", 2020, 2025)]
rd = lambda f, d=RS, **k: pd.read_csv(os.path.join(d, f), encoding="utf-8-sig", **k)
ANE, KID, BLS, TE, UNM, LTC, IMS, ILL = ("ext__anaemia_suspect_sir", "ext__kidney_suspect_share", "basic_livelihood_rate", "tertiary_educated_share", "ext__unmet_need_rate",
    "ltc_hospitals_per_100k_65", "im_specialists_per_100k", "ill_defined_death_share")
HYP = [ANE, KID, BLS, TE, UNM, LTC, IMS, ILL]
FORCED = ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"]
FIS, P80 = "fiscal_independence", "pop80_share"
SENS = ("sens_g577", "sens_no80", "sens_crude", "sens_y24")

def load():
    N = {}
    P = pd.read_csv(os.path.join(B, f"panel_BLDD_{VER}.csv")); N["n_rows"], N["n_districts"] = len(P), P.fbd_region.nunique(); assert (N["n_rows"], N["n_districts"]) == (3435, 229)
    N["cases_total"] = int(P.cases.sum()); assert N["cases_total"] == 11759
    N["zeros"] = int((P.cases == 0).sum()); assert N["zeros"] == 460
    yc = P.groupby("year").cases.sum().astype(int); N["n_y"] = yc.to_dict(); assert N["n_y"][2011] == 572 and N["n_y"][2025] == 940
    N["per_year"] = (int(yc.min()), int(yc.max()))
    N["sejong_n"] = int(P[P.fbd_region.str.contains("세종")].cases.sum())
    # 전국 기술(DT_1B34E01, 55D)
    D = rd("S55D_national.csv", DESC); N["asr"] = {(r.year, r.sex): r.asr_2020 for r in D.itertuples()}; N["crude"] = {(r.year, r.sex): r.crude for r in D.itertuples()}
    N["deaths_sex"] = D[D.sex != "계"].groupby("sex").deaths.sum().to_dict(); N["national_total"] = int(D[D.sex == "계"].deaths.sum())
    assert sum(N["deaths_sex"].values()) == N["national_total"] and abs(N["national_total"] - N["cases_total"]) <= 3, (N["national_total"], N["cases_total"])
    A = rd("S55D_agesex.csv", DESC); A = A[A.sex == "계"]; A["lo"] = A.band.map(lambda b: int(str(b).split("-")[0].replace("+", ""))); tot = A.사망자수.sum()
    N["pct65"] = 100 * A[A.lo >= 65].사망자수.sum() / tot; N["pct80"] = 100 * A[A.lo >= 80].사망자수.sum() / tot; N["pct85"] = 100 * A[A.lo >= 85].사망자수.sum() / tot
    N["pct_women"] = 100 * N["deaths_sex"]["여자"] / N["national_total"]
    SUB = rd("S55D_subcause.csv", DESC).set_index("year"); N["anaemia_share"] = 100 * SUB.anaemia.sum() / SUB.total.sum(); N["sub"] = SUB.to_dict("index")
    P["window"] = pd.cut(P.year, [2010, 2015, 2019, 2025], labels=[w[0] for w in WIN]).astype(str)
    T1 = {}
    for wn, a, b in WIN + [("ALL", 2011, 2025)]:
        q = P[P.year.between(a, b)]; smr = q.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.E.sum(), include_groups=False)
        T1[wn] = dict(n=len(q), cases=int(q.cases.sum()), zeros=int((q.cases == 0).sum()), p10=smr.quantile(.1), med=smr.median(), p90=smr.quantile(.9),
                      cov={v: (q[f"{v}_raw"].mean(), q[f"{v}_raw"].std()) for v in HYP + FORCED})
    N["T1"] = T1
    L = rd("S55K_likelihood.csv").set_index("likelihood"); N["lik"] = L.to_dict("index")
    lk = rd("S1_likelihood.csv"); lk = lk[lk.set == "REF_forced_only"].set_index("family").WAIC; N["waic_pois"], N["waic_nb"] = lk["poisson"], lk["nbinomial"]; assert N["waic_nb"] < N["waic_pois"]
    hb = open(os.path.join(B, f"HM_best_BLDD_{VER}.txt")).read(); N["waic_forced"] = float(hb.split("ref_forced_only_WAIC=")[1].split()[0]); N["waic_main"] = float(hb.split("S1_narrative_full(")[1].split(",")[0])
    s6m = rd("S6_moran_year.csv"); N["moran_year"] = (s6m.moran_I.min(), s6m.moran_I.max()); N["moran_year_sig"] = int((s6m.p_perm < 0.05).sum())
    r8 = rd("S8_residual_moran.csv").set_index("quantity"); N["moran_pooled"] = r8.loc["observed_logSIR_pooled", "moran_I"]; N["moran_resid"] = r8.loc["pearson_residual_area_mean", "moran_I"]
    h = rd("S3_main_hyper.csv"); ph = h[h.hyperpar.str.startswith("Phi")].iloc[0]; N["phi"] = (ph["mean"], ph["X0.025quant"], ph["X0.975quant"])
    s6 = rd("S6_spatial_RR.csv"); N["s6"] = s6; N["rr_min"], N["rr_max"] = s6.RR.min(), s6.RR.max()
    N["n_hot"], N["n_cold"] = int((s6["class"] == "hotspot").sum()), int((s6["class"] == "coldspot").sum()); assert (N["n_hot"], N["n_cold"]) == (26, 18)
    sido = s6.fbd_region.str.extract(r"^(\S+?(?:도|시))")[0]
    N["hot_by_sido"] = s6[s6["class"] == "hotspot"].groupby(sido).size().sort_values(ascending=False).to_dict()
    N["cold_by_sido"] = s6[s6["class"] == "coldspot"].groupby(sido).size().sort_values(ascending=False).to_dict()
    N["n_busan"] = int(sido.eq("부산시").sum())
    N["top_rr"] = s6.sort_values("RR", ascending=False).head(3)[["fbd_region", "RR"]].values.tolist()
    pe = rd("S12_persistence.csv").set_index("set"); N["kendall"] = pe.kendall_W.to_dict()
    N["ehsa"] = rd("S11_ehsa_summary.csv").set_index("category").n.to_dict()
    vp = rd("S42_variance_partition.csv").set_index("component"); N["vp_spatial"] = vp.loc["spatial_structured", "share_of_linear_predictor_var"]
    d = P.groupby("fbd_region").agg(c=("cases", "sum"), e=("E", "sum"), ane=(f"{ANE}_raw", "mean"), bls=(f"{BLS}_raw", "mean"), fis=(f"{FIS}_raw", "mean")).reset_index(); d["sir"] = d.c / d.e
    N["rho_raw"] = {k: float(spearmanr(d.sir, d[k])[0]) for k in ("ane", "bls", "fis")}
    w = P.groupby(["fbd_region", "window"]).agg(c=("cases", "sum"), e=("E", "sum")).reset_index(); w["sir"] = w.c / w.e
    pw = w.pivot(index="fbd_region", columns="window", values="sir").corr(method="spearman"); N["rho_win"] = (pw.values[np.triu_indices(3, 1)].min(), pw.values[np.triu_indices(3, 1)].max())
    sp = d.assign(sido=d.fbd_region.str.extract(r"^(\S+?(?:도|시))")[0]).groupby("sido")[["c", "e"]].sum(); N["sido_sir"] = (sp.c / sp.e).to_dict()
    m3 = rd("S3_main_IRR.csv").set_index("cov"); N["main"] = m3[["IRR", "lo", "hi", "cred", "role"]].to_dict("index")
    N["n_hyp"] = int((m3.role == "hypothesis").sum()); assert N["n_hyp"] == 8 and set(m3.index[m3.role == "hypothesis"]) == set(HYP)
    N["cred_hyp"] = sorted(v for v in HYP if N["main"][v]["cred"]); assert N["cred_hyp"] == []
    assert N["main"][FIS]["cred"] and N["main"][FIS]["IRR"] < 1
    s7 = rd("S7_multiverse_summary.csv").set_index("cov"); N["mv"] = s7[["n_specs", "cred_frac", "sign_agree", "robust"]].to_dict("index"); assert not s7.robust.any()
    N["mv_total"] = int(s7.n_specs_total.iloc[0])
    nc = rd("S3_negcontrol.csv").set_index("cov"); N["negctl"] = {v: (r.IRR, r.lo, r.hi, bool(r.cred)) for v, r in nc.iterrows()}
    wi = rd("S4_window_IRR.csv"); N["win"] = {(r.cov, r.window): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in wi.itertuples()}
    N["win_ncred"] = [sum(1 for v in HYP if N["win"].get((v, w), (0, 0, 0, False))[3]) for w, _, _ in WIN]
    ia = rd("S4_interaction.csv"); N["n_inter"], N["n_inter_cred"] = len(ia), int(ia.cred.astype(bool).sum())
    cv = rd("S5_covid.csv"); N["covid_main"] = tuple(cv[cv.term == "post_main"][["IRR", "lo", "hi", "cred"]].iloc[0])
    N["covid"] = {(r.term, r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in cv.itertuples()}
    S43 = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(RS, "S43_part_*.csv"))]); N["s43"] = {(r.analysis, r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in S43.itertuples()}
    N["s43_waic"] = S43.groupby("analysis").WAIC.first().to_dict()
    T9 = rd("S9_typeI_IRR.csv"); N["s43"].update({("KH_typeI", r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in T9.itertuples()}); N["s43_waic"]["KH_typeI"] = float(T9.WAIC.iloc[0])
    S41 = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(RS, "S41_part_*.csv"))]); N["s41"] = {(r.analysis, r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in S41.itertuples()}
    N["s41_waic"] = S41.groupby("analysis").WAIC.first().to_dict()
    ALT = sorted({a for a in S41.analysis.unique() if not a.startswith(("F1_", "F2_", "G2_", "H1_", "bw_"))}); N["alt"] = ALT
    m3s = {v: np.sign(np.log(N["main"][v]["IRR"])) for v in N["main"]}; altd = S41[S41.analysis.isin(ALT)]   # 89g는 강건 변수 0개라 retention 빈 표 → 모든 변수에 대해 직접 계산(같은 정의: 대체 사양 중 CrI가 1 제외·같은 부호)
    N["ret"] = {v: (int((g.cred.astype(bool) & (np.sign(np.log(g.IRR)) == m3s[v])).sum()), int(g.analysis.nunique())) for v, g in altd.groupby("cov") if v in m3s}
    N["bw"] = {r.cov: (r.IRR, r.lo, r.hi, bool(r.cred)) for r in S41[S41.analysis == "bw_twoway"].itertuples()}
    N["nco"] = {(r.analysis.replace("H1_nco_", ""), r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in S41[S41.analysis.str.startswith("H1_nco_")].itertuples()}
    N["leaveout"] = {}
    for pre, lab in (("F1_drop_sido", "province"), ("F2_drop_year", "year")):
        a_ = S41[S41.analysis.str.startswith(pre)]
        for v, g in a_.groupby("cov"):
            if v in m3s: N["leaveout"][(lab, v)] = (int(g.analysis.nunique()), int((g.cred.astype(bool) & (np.sign(np.log(g.IRR)) == m3s[v])).sum()))
    N["sens"] = {}
    for v in SENS:
        m = pd.read_csv(os.path.join(B, f"results_{v}", "S3_main_IRR.csv")).set_index("cov"); N["sens"][v] = {c: (m.loc[c, "IRR"], m.loc[c, "lo"], m.loc[c, "hi"], bool(m.loc[c, "cred"])) for c in m.index}
    eb = rd("S12c_yearly_EB_SIR.csv"); g = eb.groupby("year").ebSIR; gap = pd.DataFrame({"p10": g.quantile(.1), "p90": g.quantile(.9)}); gap["ratio"] = gap.p90 / gap.p10; N["gap"] = gap.to_dict("index")
    return N

if __name__ == "__main__":
    N = load()
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in N.items() if not isinstance(v, (dict, list, pd.DataFrame, tuple))})
    for k in ("phi", "moran_year", "covid_main", "rho_win", "per_year", "top_rr"): print(k, N[k])
    print("hot", N["hot_by_sido"]); print("cold", N["cold_by_sido"]); print("ret", N["ret"], len(N["alt"])); print("rho", N["rho_raw"])
    print("kendall", N["kendall"]); print("asr", {k: v for k, v in N["asr"].items() if k[1] == "계" and k[0] in (2011, 2025)}); print("inter", N["n_inter"], N["n_inter_cred"], "win", N["win_ncred"])
    print("mv", {k: round(v["cred_frac"], 2) for k, v in N["mv"].items()}); print("ehsa", N["ehsa"]); print("sens", {s: [c for c, t in d.items() if t[3]] for s, d in N["sens"].items()})
    print("KH", {a: [c for (aa, c), t in N["s43"].items() if aa == a and t[3]] for a in sorted(N["s43_waic"])}, {a: round(w, 1) for a, w in N["s43_waic"].items()})
    print("nco", {k: v for k, v in N["nco"].items() if v[3]}); print("bw", {k: v for k, v in N["bw"].items() if v[3]})
