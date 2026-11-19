# esm_bldd.py — BLDD Supplementary Material(단일 파일: Supplementary Text S1·Supplementary Table S1-S4·Text S2 STROBE, JAGS 표기) + STROBE 단독 파일(2026-11-14, esm_sknd 이식).
#  수치는 결과 CSV에서만. 영국식 철자, 표 제목 쌍점 금지, 보충 번호 = 본문 첫 인용 순서.
import os, re, json, subprocess, pandas as pd
import content_bldd as C
from build_bldd import LABEL, GROUPS, TX, TITLE as DTITLE, foot_row
HERE = os.path.dirname(os.path.abspath(__file__)); MSD = os.path.dirname(HERE); OUT = os.path.join(MSD, "out"); B = os.path.dirname(MSD); RS = os.path.join(B, "results_std3_main")
N = C.N
st = lambda t: f"{t[0]:.2f} ({t[1]:.2f}–{t[2]:.2f})"
J = TX(cite="bracket")
def TF(title, header, rows, foot="", fs=8):
    J.page_break(); J.table_fit(title, header, rows, "", fs_max=fs, title_bold=True)
    if foot: foot_row(J, foot, 8, 12)
J.para("<b>Supplementary Material</b>"); J.para(f"Supplementary material for the manuscript entitled \"{DTITLE}\"")
J.para("Contents. Supplementary Text S1 (supplementary methods and additional results); Supplementary Table S1 (district characteristics); Supplementary Table S2 (likelihood comparison); Supplementary Table S3 (alternative specifications); Supplementary Table S4 (residual hot spots and cold spots); Supplementary Text S2 (STROBE checklist).")
_MT = pd.read_csv(os.path.join(B, "panel_META_BLDD_std3_main.csv"), encoding="utf-8-sig").set_index("variable")
_imp = lambda v: int(_MT.loc[v, "n_imputed_interp"] + _MT.loc[v, "n_imputed_sgg_mean"] + _MT.loc[v, "n_imputed_year_mean"])
gate = open(os.path.join(B, "data_gate_BLDD_std3_main_261114.txt"), encoding="utf-8").read(); nwarn = int(re.search(r"경고 (\d+)건", gate).group(1))
_vif = _MT[_MT.role.isin(["forced", "candidate"])].vif_final.dropna().sort_values(ascending=False); assert _vif.iloc[0] < 10
RULE = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(B)), "02_패널", "EXT_canonical_pool_BLDD_2025rule.csv"), encoding="utf-8-sig")
PPC = pd.read_csv(os.path.join(RS, "S42_ppc.csv")).iloc[0].to_dict()
J.page_break(); J.head("Supplementary Text S1. Supplementary methods and additional results", 2)
SM = [("Outcome.", f"Annual deaths with an underlying cause in ICD-10 Chapter III (D50–D89) by district of residence came from the 50-item district cause-of-death table of Statistics Korea for 2011–2025, summed over the urban wards of cities with general wards and joined by administrative code; the district total of all-cause deaths matched the reference district panel in all 3,435 district-years. The 15-year total was {N['cases_total']:,}. "
       f"National deaths by cause, sex and 5-year age group came from the 104-item national table (15-year total {N['national_total']:,}, a difference of {N['cases_total'] - N['national_total']} from the district table between the published tables); in that table, {N['anaemia_share']:.1f}% of deaths were anaemias (D50–D64). Districts were harmonised to the 229 units of 2024, and Sejong (created in 2012) was included in all years."),
      ("Expected deaths.", "National deaths by sex and age (0–4 to 80–84 years and 85 years or older) were divided by national populations to give annual sex- and age-specific rates, which were applied to district populations by sex and 5-year age group. For 2011–2024 these came from resident registration files, with the 2023 populations of Changwon, which repeated the 2022 values in the source file, replaced by the official 2023 values. "
       "For 2025, the sex and age composition came from resident registration at December 2025, joined to districts by a crosswalk that matched the December 2024 values exactly, and was rescaled to the reference 2025 district population; expected deaths for 2024 reproduced by this route correlated 1.00 with the main values. Expected deaths were rescaled so that each year's total equalled observed deaths."),
      ("Covariates.", "Suspected anaemia was the ratio of observed to sex- and age-standardised expected numbers of screening participants classified as suspected anaemia at the national general health screening (log-transformed); Sejong, unobserved in that source, was given the yearly mean. Suspected kidney disease was the share of screening participants so classified. "
       "Basic livelihood recipient shares that collapsed in 2021–2023 for districts of cities with general wards were set to missing and interpolated within districts. Unmet medical need came from the Community Health Survey; internal-medicine specialists (log1p-transformed), long-term care hospitals and the ill-defined cause share (R00–R99 over all deaths) came from harmonised public district panels. "
       "Values for 2025 were used where published (deaths, population, the share aged 80 years or older and most forced controls); otherwise the 2024 value was carried forward, which applied to all eight characteristics in all districts. A sensitivity analysis restricted to 2011–2024 is reported in Supplementary Table S3."),
      ("Panel checks before modelling.", f"An automated gate run on the analytic panel before the models were fitted reported {nwarn} flags: standardised columns whose yearly means were near 0 (a ratio artefact), real increases over time in the share aged 80 years or older, the sex ratio above 100 by definition, the post-2020 indicator (constant by design) and districts with no general hospital or long-term care hospital in any year (true zeros); no flag concerned keys, missing outcome counts or population denominators. "
       f"Final variance inflation factors were all below 10 (largest {_vif.iloc[0]:.1f})."),
      ("Models.", "Software: R 4.6.0 with R-INLA (one thread) and Python 3.9 for data preparation and figures. Fixed effects had normal priors with mean 0 and precision 4 (intercept precision 0.001). The Besag–York–Mollié 2 district effect used penalised-complexity priors (P(σ > 0.5) = 0.01; P(φ < 0.5) = 2/3) on a 593-edge district adjacency graph with island districts linked to the nearest mainland district; the random-walk and independent year effects used penalised-complexity priors (P(σ > 0.5) = 0.01). Covariate subsets for the multiverse were drawn with a fixed seed. Kendall's W used 2000 permutations of district ranks within years. Period maps refitted the principal model separately in 2011–2015, 2016–2019 and 2020–2025.")]
for h, t in SM: J.para(f"<b>{h}</b> {t}")
J.para("<b>Additional results.</b> " + f"Posterior predictive 95% intervals covered {100*PPC['coverage95']:.1f}% of district-years. The post-2020 indicator was not associated with deaths after adjustment ({st(N['covid_main'])}). "
       f"The ratio of the 90th to the 10th percentile of smoothed annual district SMRs was {N['gap'][2011]['ratio']:.2f} in 2011 and {N['gap'][2025]['ratio']:.2f} in 2025. "
       f"Kendall's W was {N['kendall']['2011-2019']:.2f} over 2011–2019 and {N['kendall']['2020-2025']:.2f} over 2020–2025. In emerging hot spot analysis, {N['ehsa'].get('Consecutive hot', 0)} district was a consecutive hot spot, {N['ehsa'].get('Intensifying hot', 0)} were intensifying hot spots, {N['ehsa'].get('Sporadic hot', 0)} were sporadic hot spots and {N['ehsa'].get('Sporadic cold', 0)} were sporadic cold spots; none was persistent. "
       f"With crude expected deaths the urban population share ({st(N['sens']['sens_crude']['urban_population_share'])}) and tertiary-educated share ({st(N['sens']['sens_crude'][C.TE])}) also became credible.")
# ── Supplementary Table S1 ──
DIR = {C.ANE: "+", C.KID: "+", C.BLS: "+", C.TE: "−", C.UNM: "+", C.LTC: "+", C.IMS: "−", C.ILL: "−"}
SRCN = {C.ANE: "National health screening", C.KID: "National health screening", C.BLS: "District panel", C.TE: "Census (district panel)", C.UNM: "Community Health Survey", C.LTC: "District panel", C.IMS: "District panel", C.ILL: "Cause-of-death statistics",
        "urban_population_share": "KOSIS local indicators", "physicians_per_1000": "KOSIS local indicators", "sex_ratio": "KOSIS local indicators", "fiscal_independence": "KOSIS local indicators", "pop80_share": "Resident registration"}
UNIT = {C.ANE: "ratio (log)", C.KID: "% of participants", C.BLS: "%", C.TE: "% of adults", C.UNM: "%", C.LTC: "per 100,000 aged ≥ 65", C.IMS: "per 100,000 (log1p)", C.ILL: "% of deaths",
        "urban_population_share": "%", "physicians_per_1000": "per 1,000", "sex_ratio": "ratio", "fiscal_independence": "%", "pop80_share": "%"}
rows = []
for g, vs in GROUPS:
    rows.append(["__H__", g])
    for v in vs:
        m = _MT.loc[v]; rows.append([f"  {LABEL[v].split(' (')[0]}", UNIT[v], SRCN[v], ("Forced" if m.role == "forced" else DIR[v]), f"{_imp(v)}"])
TF("Supplementary Table S1 Source, unit, expected direction and filled cells for each district characteristic, 229 districts, Republic of Korea, 2011–2025", ["Characteristic", "Unit", "Source", "Direction", "Filled cells"], rows,
   "KOSIS, Korean Statistical Information Service; ratio for sex ratio, men per 100 women; forced, in every model. Filled cells are those filled by the model-building step (interpolation within districts, district means or yearly means) of 3,435 district-years; cells filled earlier (2025 values carried forward from 2024, Sejong anaemia ratio set to the yearly mean, corrected livelihood shares) are described in Supplementary Text S1. "
   "Negative control exposures (separate model): hit-and-run collisions, a traffic-culture index and fires per 10,000 residents.")
# ── Supplementary Table S2 우도 ──
LN = [("poisson", "Poisson"), ("nbinomial", "Negative binomial"), ("zeroinflatedpoisson1", "Zero-inflated Poisson"), ("zeroinflatednbinomial1", "Zero-inflated negative binomial"), ("poisson+obs_iid", "Poisson with observation-level effect")]
rows = [[lab, f"{L['WAIC']:.1f}", f"{L['DIC']:.1f}", f"{L['neg_logscore']:.1f}", "–" if pd.isna(L["zero_prob"]) else f"{L['zero_prob']:.4f}", "–" if pd.isna(L["size"]) else f"{L['size']:.1f}", "–" if pd.isna(L["expected_zeros"]) else f"{L['expected_zeros']:.0f}"] for k, lab in LN for L in [N["lik"][k]]]
TF("Supplementary Table S2 Likelihood comparison for blood and immune disorder deaths with forced controls and the same random effects, 3,435 district-years, Republic of Korea, 2011–2025", ["Likelihood", "WAIC", "DIC", "−Σ log CPO", "Zero probability", "Size", "Expected zeros"], rows,
   f"WAIC, widely applicable information criterion; DIC, deviance information criterion; CPO, conditional predictive ordinate; size, negative binomial size parameter; –, not applicable. Observed district-years with no death: {N['zeros']}. "
   "Expected zeros are the sum of posterior-mean probabilities of a zero count. The principal model used the negative binomial likelihood, chosen before covariates were added by comparison with Poisson; the Poisson model with an observation-level effect gave the same conclusions (Supplementary Table S3).", fs=8)
# ── Supplementary Table S3 사양 ──
NAMES = [("principal", "Principal model"), ("KH_typeI", "Knorr-Held type I"), ("KH_typeII", "Knorr-Held type II"), ("KH_typeIII", "Knorr-Held type III"), ("KH_typeIV", "Knorr-Held type IV"),
         ("icar_besag", "ICAR district effect"), ("iid_only", "IID district effect"), ("no_spatial", "No district effect"), ("knn3", "3 nearest neighbours"), ("knn4", "4 nearest neighbours"), ("knn5", "5 nearest neighbours"),
         ("pc_phi_flat", "Flat prior on mixing"), ("pc_relaxA", "Relaxed priors A"), ("pc_relaxB", "Relaxed priors B"),
         ("B3_smooth_forced", "Smoothed forced controls*"), ("C1_poisson_lognormal", "Poisson, observation effect*"), ("C2_rw2_year", "RW2 year effect*"), ("C3_ar1_year", "AR1 year effect*"), ("C4_sido_year_iid", "Province-by-year effect*"), ("D1_spatial_plus", "Spatial+-type*"),
         ("E0_nolag_from2012", "No lag, from 2012*"), ("E1_lag1", "Lag 1 year*"), ("E0_nolag_from2013", "No lag, from 2013*"), ("E2_lag2", "Lag 2 years*"), ("F3_extreme_R7", "Extreme values refilled*"), ("G1_kchs_ma3", "Survey 3-year averages*"), ("H4_odd_years", "Odd years only*"), ("H4_even_years", "Even years only*"),
         ("sens_y24", "2011–2024 only"), ("sens_crude", "Crude expected deaths"), ("sens_no80", "Share aged 80+ omitted"), ("sens_g577", "Queen graph, 577 edges"),
         ("H1_nco_TRANS", "Transport-injury deaths (comparison)"), ("H1_nco_GCA", "Gastric cancer patients (comparison)")]
SS = {**N["s43"], **N["s41"]}; WA = {**N["s43_waic"], **N["s41_waic"]}
for v in ("sens_g577", "sens_no80", "sens_crude", "sens_y24"): SS.update({(v, c): t for c, t in N["sens"][v].items()}); WA[v] = float(pd.read_csv(os.path.join(B, f"results_{v}", "S3_main_fit.csv")).WAIC.iloc[0])
WA["principal"] = N["waic_main"]; SS.update({("principal", c): (r["IRR"], r["lo"], r["hi"], r["cred"]) for c, r in N["main"].items()})
def cell(a, v): t = SS.get((a, v)); return "–" if t is None else st(t)
HV = [C.FIS, C.ANE, C.BLS, C.LTC]; HN = {C.FIS: "Fiscal autonomy", C.ANE: "Suspected anaemia", C.BLS: "Livelihood recipients", C.LTC: "Long-term care hospitals"}
rows = [[lab, f"{WA[a]:.0f}" if a in WA and not a.startswith("H1_") and a != "sens_y24" else "–"] + [cell(a, v) for v in HV] for a, lab in NAMES]
TF("Supplementary Table S3 Rate ratios per 1 standard deviation across alternative specifications and comparison outcomes, 229 districts, Republic of Korea, 2011–2025", ["Specification", "WAIC"] + [HN[v] for v in HV], rows,
   "Values are rate ratios (95% credible intervals) per 1 standard deviation; –, not estimated. *The 14 alternative fits counted in the main text. For the Spatial+-type model, rate ratios are per 1 standard deviation of the residualised covariate. Comparison outcomes were fitted with the same covariates and model. WAIC: widely applicable information criterion (not comparable across outcomes or numbers of years); ICAR: intrinsic conditional autoregressive; IID: independent and identically distributed; RW2: second-order random walk; AR1: first-order autoregressive. "
   f"Omitting each province: fiscal autonomy credible in {N['leaveout'][('province', C.FIS)][1]} of {N['leaveout'][('province', C.FIS)][0]}; omitting each year: {N['leaveout'][('year', C.FIS)][1]} of {N['leaveout'][('year', C.FIS)][0]}. No hypothesised characteristic was credible in more than one alternative specification other than the crude-expected, independent-district-effect and no-district-effect models.", fs=7)
# ── Supplementary Table S4 핫·콜드 ──
EN = {"서울시": "Seoul", "부산시": "Busan", "대구시": "Daegu", "인천시": "Incheon", "광주시": "Gwangju", "대전시": "Daejeon", "울산시": "Ulsan", "세종시": "Sejong", "경기도": "Gyeonggi-do", "강원도": "Gangwon-do", "충청북도": "Chungcheongbuk-do",
      "충청남도": "Chungcheongnam-do", "전라북도": "Jeollabuk-do", "전라남도": "Jeollanam-do", "경상북도": "Gyeongsangbuk-do", "경상남도": "Gyeongsangnam-do", "제주도": "Jeju"}
ROM = json.load(open(os.path.join(HERE, "district_romanization_all.json"), encoding="utf-8"))   # 공식 영문 시군구명 229곳(SCRT 사본)
S6 = N["s6"].copy(); S6["sido"] = S6.fbd_region.str.extract(r"^(\S+?(?:도|시))")[0]; S6["sgg"] = [r[len(s):] for r, s in zip(S6.fbd_region, S6.sido)]
rom = lambda region: ROM[region]
rows = []
for cls, lab in (("hotspot", "Hot spots"), ("coldspot", "Cold spots")):
    q = S6[S6["class"] == cls].sort_values(["sido", "RR"], ascending=[True, cls != "hotspot"]); rows.append(["__H__", f"{lab} ({len(q)})"])
    for r in q.itertuples(): rows.append([f"  {EN[r.sido]}", rom(r.fbd_region), f"{r.RR:.2f} ({r.lo:.2f}–{r.hi:.2f})", f"{r.P_gt1:.3f}", f"{r.SIR_obs:.2f}"])
TF("Supplementary Table S4 Residual hot spots and cold spots of blood and immune disorder deaths, 229 districts, Republic of Korea, 2011–2025", ["Province", "District", "Residual spatial RR (95% CrI)", "P(RR > 1)", "Observed SMR"], rows,
   "RR, rate ratio from the district effect of the principal model; CrI, credible interval; SMR, standardised mortality ratio over 15 years. Hot spots: posterior probability of RR > 1 above 0.95; cold spots: below 0.05. Because this one-sided criterion differs from exclusion of 1 by the two-sided 95% CrI, some intervals include 1. Exploratory; not adjusted for multiple comparisons.", fs=7)
assert not any(isinstance(r[1], str) and re.search(r"[가-힣]", r[1]) for r in rows if r[0] != "__H__"), "untranslated district name"
# ── STROBE ──
MH = [x[0] for x in C.METHODS]; RH = [x[0] for x in C.RESULTS]
CK = [("Title and abstract", "1", "Title page; Abstract"), ("Background/rationale", "2", "Introduction"), ("Objectives", "3", "Introduction, final paragraph"),
      ("Study design", "4", f"Methods, {MH[0]}"), ("Setting", "5", f"Methods, {MH[0]}"), ("Participants", "6", f"Methods, {MH[0]} (all registered deaths; ecological)"),
      ("Variables", "7", f"Methods, {MH[1]}; {MH[2]}; Supplementary Table S1"), ("Data sources/measurement", "8", "Methods; Supplementary Text S1"),
      ("Bias", "9", f"Methods, {MH[3]}; Supplementary Table S3"), ("Study size", "10", f"Methods, {MH[0]} (all 229 districts)"), ("Quantitative variables", "11", f"Methods, {MH[2]}"),
      ("Statistical methods", "12", f"Methods, {MH[3]}; Supplementary Text S1; Supplementary Table S2"), ("Participants (flow)", "13", "Not applicable (aggregate district data; no exclusions)"),
      ("Descriptive data", "14", f"Results, {RH[0]}; Table 1"), ("Outcome data", "15", f"Results, {RH[0]}; Table 1; Figure 1"),
      ("Main results", "16", f"Results, {RH[1]}; {RH[2]}; Table 2; Figures 2–3"), ("Other analyses", "17", f"Results, {RH[2]}; Tables S2–S4"),
      ("Key results", "18", "Discussion, first paragraph"), ("Limitations", "19", "Discussion, Limitations"), ("Interpretation", "20", "Discussion"), ("Generalisability", "21", "Discussion, Conclusions"),
      ("Other information (funding, code)", "22", "Funding; Data availability statement")]
J.page_break()
J.table_fit("Supplementary Text S2 STROBE checklist for this ecological study", ["Item", "No.", "Where reported"], [[a, b, c] for a, b, c in CK], "", fs_max=8, title_bold=True)
foot_row(J, "STROBE: Strengthening the Reporting of Observational Studies in Epidemiology.", 8, 12)
ps = os.path.join(OUT, "Supplementary_Material_BLDD.docx"); J.doc_title = "Supplementary Material"; J.save(ps)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_bldd_esm", "--convert-to", "pdf", "--outdir", OUT, ps], check=True, capture_output=True)
print("saved", os.path.basename(ps))
K = TX(cite="bracket"); K.para("<b>STROBE checklist</b>"); K.para(f"Manuscript \"{DTITLE}\"")
K.table_fit("STROBE checklist for this ecological study", ["Item", "No.", "Where reported"], [[a, b, c] for a, b, c in CK], "", fs_max=9, title_bold=True)
foot_row(K, "Section names refer to the main manuscript and the Supplementary Material.", 8, 12)
pk = os.path.join(OUT, "STROBE_Checklist_BLDD.docx"); K.doc_title = "STROBE checklist"; K.save(pk)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_bldd_esm", "--convert-to", "pdf", "--outdir", OUT, pk], check=True, capture_output=True)
print("saved", os.path.basename(pk))
