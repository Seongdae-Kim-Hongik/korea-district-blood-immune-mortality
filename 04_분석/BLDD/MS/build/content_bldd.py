# content_bldd.py — BLDD 원고 Methods·Results 문장(수치는 numbers_bldd에서만). JAGS Clinical Investigation 규정(2026-11-19 확인):
#  구조 초록 ≤300(Background/Methods/Results/Conclusions), 본문 ≤3,500, 참고문헌 ≤50, 표+그림 ≤5, running title ≤45자, 제목 ≤125자(공백 제외), 키워드 3–5, AMA·미국식 철자,
#  비율·신뢰구간 소수 2자리, 백분율 1자리, 'older adults'(65세 이상), Key Points 상자, Acknowledgments 안에 기여·COI·Sponsor's Role·AI 고지. 컬러 그림 무료.
#  단독 저자 → 1인칭 금지. 결과 절 해석 금지. 제목 쌍점 금지.
from numbers_bldd import load, HYP, FORCED, ANE, KID, BLS, TE, UNM, LTC, IMS, ILL, FIS, P80
N = load()
def _fmt(t):   # 소수 2자리, 단 구간 끝이 1.00으로 보이거나 하한=상한이면 3자리(판정은 반올림 전 값)
    d = 3 if (f"{t[1]:.2f}" == "1.00" or f"{t[2]:.2f}" == "1.00" or f"{t[1]:.2f}" == f"{t[2]:.2f}") else 2
    return f"{t[0]:.{d}f}", f"{t[1]:.{d}f}", f"{t[2]:.{d}f}"
def tci(t): a, b, c = _fmt(t); return f"RR {a}, 95% CrI {b}–{c}"
def ci(v): r = N["main"][v]; return tci((r["IRR"], r["lo"], r["hi"]))
M = N["main"]; T1 = N["T1"]
S43 = lambda a, v: N["s43"][(a, v)]
S41 = lambda a, v: N["s41"][(a, v)]
NCO = lambda o, v: N["nco"][(o, v)]
SEN = lambda s, v: N["sens"][s][v]
KH = ("KH_typeI", "KH_typeII", "KH_typeIII", "KH_typeIV"); BEST_KH = min(KH, key=lambda a: N["s43_waic"][a]); assert BEST_KH == "KH_typeIV"
EN = {"서울시": "Seoul", "경기도": "Gyeonggi-do", "충청남도": "Chungcheongnam-do", "부산시": "Busan", "경상남도": "Gyeongsangnam-do", "경상북도": "Gyeongsangbuk-do", "울산시": "Ulsan",
      "전라북도": "Jeonbuk State", "전라남도": "Jeollanam-do"}
def sidos(d):
    l = [f"{EN[k]} ({v})" for k, v in d.items()]; return ", ".join(l[:-1]) + " and " + l[-1]
TITLE = "Is the excess of deaths from blood and immune disorders in Busan, Korea, explained by anaemia burden, deprivation or care?"
RUNNING = "Blood and immune disorder deaths in Korea"
KEYWORDS = ["anemia", "mortality", "older adults", "spatial analysis", "Republic of Korea"]
assert ":" not in TITLE and len(RUNNING) <= 45 and len(TITLE.replace(" ", "")) <= 125 and 3 <= len(KEYWORDS) <= 5
SUP = {"methods": "Supplementary Text S1", "covariates": "Supplementary Table S1", "lik": "Supplementary Table S2", "specs": "Supplementary Table S3", "hot": "Supplementary Table S4", "strobe": "Supplementary Text S2"}
sup = lambda k: SUP[k]
ALT = len(N["alt"]); RET = N["ret"]; LO = N["leaveout"]
A0 = lambda y: N["asr"][(y, "계")]
LIK = N["lik"]; NB = LIK["nbinomial"]; ZINB = LIK["zeroinflatednbinomial1"]; PO = LIK["poisson"]; POI = LIK["poisson+obs_iid"]
MV = lambda v: N["mv"][v]["cred_frac"]
NPROV = LO[("province", FIS)][0]; NYR = LO[("year", FIS)][0]

METHODS = [
("Study design and data",
 f"This ecological study covered all {N['n_districts']} districts (urban wards, cities and counties) of the Republic of Korea, harmonised to 2024 boundaries, over 2011–2025 ({N['n_rows']:,} district-years), and is reported according to the STROBE statement [@vonelm2007strengthening] ({sup('strobe')}). "
 f"Annual deaths by underlying cause and district of residence, and national deaths by cause, sex and 5-year age group, came from the national cause-of-death statistics, which cover all registered deaths [@web:kostat2026cause]; resident populations by sex and age came from resident registration [@web:mois2026population] ({sup('methods')}). "
 "Districts were joined across sources by administrative code only. Only published aggregate statistics were used. The Institutional Review Board of Hongik University approved the study (7002340-202511-HR-012; continuing review 7002340-202611-HR-040) and waived informed consent."),
("Outcome and expected deaths",
 "The outcome was deaths with an underlying cause in the published district item 'diseases of the blood and blood-forming organs and certain disorders involving the immune mechanism' (ICD-10 D50–D89), which includes the anaemias (D50–D64), coagulation defects and purpura, other blood disorders and immune disorders such as immunodeficiency and sarcoidosis; subgroups are not published by district. "
 "Expected deaths were obtained by indirect standardisation, applying national death rates for this chapter by year, sex and 18 age groups (5-year groups to 85 years or older) to each district population [@inskip1983methods]; expected deaths were rescaled within each year so that their sum equalled observed deaths, and the observed-to-expected ratio is the standardised mortality ratio (SMR). National age-standardised rates used the 2020 resident population as the standard. Sejong, created in 2012, was represented on the 2024 boundaries in all years."),
("District characteristics",
 f"Eight characteristics representing candidate explanations for district differences were defined, each with an expected direction ({sup('covariates')}). "
 "Population anaemia and kidney disease burden were represented by the sex- and age-standardised ratio of suspected anaemia (haemoglobin below the screening threshold) and the share with suspected kidney disease at the national general health screening (both expected to raise deaths) [@kassebaum2014systematic; @weiss2019anemia]. "
 "Deprivation and access were represented by the share of basic livelihood security recipients and the share reporting unmet medical need (expected to raise deaths) and the tertiary-educated share (expected to lower them) [@chueh2020high; @moradi2018food]. "
 "Care and certification were represented by long-term care hospitals per 100,000 residents aged 65 years or older (expected to raise deaths), internal-medicine specialists per 100,000 residents and the share of deaths with an ill-defined cause (R00–R99; both expected to lower deaths) [@jo2004proportion]. "
 "Five controls were forced into every model: urban population share, physicians per 1,000 residents, sex ratio, fiscal autonomy and the population share aged 80 years or older. "
 "Values not yet published for 2025, including all eight characteristics, carried their 2024 values. Sejong, unobserved in the screening statistics, was given the yearly mean of the anaemia ratio. Three negative control exposures (hit-and-run collisions, a traffic-culture index and fires) were fitted in a separate model [@lipsitch2010negative]. All characteristics were standardised to mean 0 and standard deviation (SD) 1."),
("Statistical analysis",
 f"Five likelihoods were compared with the same random effects ({sup('lik')}). "
 f"The principal model was negative binomial, which had a lower widely applicable information criterion (WAIC) than Poisson for the forced-control model ({N['waic_nb']:,.1f} versus {N['waic_pois']:,.1f}) [@gelman2014understanding]; a Poisson model with an observation-level effect had a lower WAIC ({POI['WAIC']:,.1f}) and was refitted as an alternative specification. The model had an offset of log expected deaths, a Besag–York–Mollié 2 district effect with penalised-complexity priors [@besag1991bayesian; @riebler2016intuitive; @simpson2017penalising] and random-walk and independent year effects, fitted by integrated nested Laplace approximation in R 4.6.0 [@rue2009approximate; @web:rcore2026]. "
 "Rate ratios (RRs) per 1 SD are reported with 95% credible intervals (CrIs), rounded to two decimals; an association was called credible when its unrounded interval excluded 1. "
 "Residual hot spots and cold spots, an exploratory classification not adjusted for multiple comparisons, were districts whose posterior probability of a residual spatial RR above 1 exceeded 0.95 or fell below 0.05. "
 "Stability was described by Kendall's W over the 15 annual SMRs, Spearman correlations of SMRs between 2011–2015, 2016–2019 and 2020–2025, annual and pooled Moran's I [@moran1950notes], maps refitted in the three periods and emerging hot-spot analysis.",
 f"Robustness was assessed in {N['mv_total']} models with random covariate subsets (robust when credible in at least 75% of the models containing the characteristic) [@steegen2016increasing]; four Knorr-Held space-time interactions [@knorrheld2000bayesian]; {ALT} alternative fits of likelihood, temporal structure, lags, spatial confounding [@dupont2022spatial], extreme values, survey averaging and odd or even years (marked in {sup('specs')}); alternative district effects and priors; omission of each province and each year; and four sensitivity analyses with a 577-edge adjacency graph, without the covariate share aged 80 years or older, with crude rather than standardised expected deaths, and restricted to 2011–2024. "
 "Transport-injury deaths and patients treated for gastric cancer were fitted with the same model as comparison outcomes. "
 "Following the AGS/JAGS terminology guidance, persons aged 65 years or older are referred to as older adults; race and ethnicity were not recorded in the source statistics."),
]

RESULTS = [
("Deaths by year, sex and age",
 f"There were {N['cases_total']:,} deaths over 2011–2025, rising from {N['n_y'][2011]} in 2011 to {N['n_y'][2025]} in 2025 (Table 1). "
 f"In the national age table, {N['pct65']:.1f}% occurred at 65 years or older and {N['pct80']:.1f}% at 80 years or older, {N['pct_women']:.1f}% were in women and {N['anaemia_share']:.1f}% were anaemias (Figure 1). "
 f"The age-standardised rate was {A0(2011):.2f} per 100,000 in 2011 and {A0(2025):.2f} in 2025. "
 f"Of the district-years, {N['zeros']} ({100*N['zeros']/N['n_rows']:.1f}%) had no death; the negative binomial model expected {NB['expected_zeros']:.0f}, and the zero-inflated negative binomial model estimated a structural-zero probability of {ZINB['zero_prob']:.3f} without a lower WAIC ({ZINB['WAIC']:,.1f} versus {NB['WAIC']:,.1f}; {sup('lik')})."),
("Geography and its stability",
 f"The 15-year district SMR had a median of {T1['ALL']['med']:.2f} (10th–90th percentile {T1['ALL']['p10']:.2f}–{T1['ALL']['p90']:.2f}), and Moran's I of the pooled log SMR was {N['moran_pooled']:.2f}. "
 f"The spatially structured component accounted for {100*N['vp_spatial']:.1f}% of the variance of the linear predictor (mixing parameter φ {N['phi'][0]:.2f}, 95% CrI {N['phi'][1]:.2f}–{N['phi'][2]:.2f}). "
 f"There were {N['n_hot']} residual hot spots, in {sidos(N['hot_by_sido'])}, and {N['n_cold']} cold spots, in {sidos(N['cold_by_sido'])} (Figure 2; {sup('hot')}); all {N['n_busan']} districts of Busan were hot spots, with residual RRs up to {N['rr_max']:.2f}. "
 f"Busan and the south-east had the highest spatial RRs in each of the three periods (Figure 3). In single years, Moran's I ranged from {N['moran_year'][0]:.2f} to {N['moran_year'][1]:.2f}, Kendall's W was {N['kendall']['2011-2025']:.2f}, and Spearman correlations of SMRs between periods were {N['rho_win'][0]:.2f}–{N['rho_win'][1]:.2f}; "
 f"emerging hot-spot analysis classified {N['ehsa']['Sporadic hot'] + N['ehsa']['Intensifying hot'] + N['ehsa']['Consecutive hot']} districts, all in Busan and its neighbour Yangsan, as sporadic, intensifying or consecutive hot spots and none as persistent."),
("District characteristics",
 f"Across districts, the 15-year SMR was correlated with the suspected-anaemia ratio (ρ {N['rho_raw']['ane']:.2f}) and the livelihood-recipient share (ρ {N['rho_raw']['bls']:.2f}). "
 f"In the principal model, none of the eight characteristics had a credible association (Table 2): suspected anaemia {ci(ANE)}, suspected kidney disease {ci(KID)}, livelihood recipients {ci(BLS)}, tertiary education {ci(TE)} and long-term care hospitals {ci(LTC)}. "
 f"Adding them did not lower the WAIC ({N['waic_forced']:,.1f} for forced controls alone and {N['waic_main']:,.1f} with all characteristics), and none was robust in the covariate-subset models (largest share credible {100*max(MV(v) for v in HYP):.1f}%, tertiary education). Residual Moran's I was {N['moran_resid']:.2f}. "
 f"Long-term care hospitals were credible in the 2016–2019 and 2020–2025 refits and in their interaction with the post-2020 period, but in no covariate-subset model, in {RET[LTC][0]} of the {RET[LTC][1]} alternative fits (even years only) and in the models with an independent or no district effect. Of the negative control exposures, the fires exposure had a lower limit at 1 ({tci(N['negctl']['fires_per_10000'][:3])}).",
 f"Of the forced controls, fiscal autonomy was inversely associated with deaths ({ci(FIS)}; 1 SD = {T1['ALL']['cov'][FIS][1]:.1f} percentage points), in all {RET[FIS][1]} alternative fits, all four Knorr-Held models (type IV, with the lowest WAIC, similar to type III: {tci(S43(BEST_KH, FIS))}), {LO[('province', FIS)][1]} of {NPROV} province omissions, {LO[('year', FIS)][1]} of {NYR} year omissions and the sensitivity analyses with the other adjacency graph, without the share aged 80 years or older and restricted to 2011–2024. "
 f"For transport-injury deaths its association was in the opposite direction ({tci(NCO('TRANS', FIS))}). "
 f"With crude expected deaths, five further coefficients became credible: livelihood recipients ({tci(SEN('sens_crude', BLS))}), tertiary education ({tci(SEN('sens_crude', TE))}), internal-medicine specialists, in the direction opposite to that expected ({tci(SEN('sens_crude', IMS))}), urban population share ({tci(SEN('sens_crude', 'urban_population_share'))}) and the share aged 80 years or older ({tci(SEN('sens_crude', P80))})."),
]

H = [v for v in M if M[v]["role"] == "hypothesis"]
assert not any(M[v]["cred"] for v in H) and M[FIS]["cred"] and M[FIS]["IRR"] < 1
assert N["waic_main"] > N["waic_forced"] and not any(N["mv"][v]["robust"] for v in HYP)
assert RET[FIS][0] == RET[FIS][1] and all(S43(a, FIS)[3] for a in KH) and all(SEN(s, FIS)[3] for s in ("sens_g577", "sens_no80", "sens_y24"))
assert NCO("TRANS", FIS)[3] and NCO("TRANS", FIS)[0] > 1
assert all(SEN("sens_crude", v)[3] for v in (BLS, TE, IMS, 'urban_population_share', P80)) and SEN('sens_crude', IMS)[0] > 1 and sum(t[3] for t in N['sens']['sens_crude'].values()) == 6 and S43('iid_only', LTC)[3] and S43('no_spatial', LTC)[3] and S41('H4_even_years', LTC)[3]
assert N["win"][(LTC, "W2_2016-19")][3] and N["win"][(LTC, "W3_2020-25")][3] and N["covid"][("var_x_post", LTC)][3] and MV(LTC) == 0
assert N['hot_by_sido']['부산시'] == N['n_busan'] and list(N["hot_by_sido"])[0] == "부산시" and list(N["cold_by_sido"])[:2] == ["서울시", "경기도"]
assert N["ehsa"]["Persistent hot"] == 0 and N["negctl"]["fires_per_10000"][3] and not N["negctl"]["hit_and_run_rate"][3] and not N["negctl"]["traffic_culture_index"][3]
assert A0(2025) < A0(2011) and N["n_y"][2025] > N["n_y"][2011]

if __name__ == "__main__":
    import re
    for x in METHODS + RESULTS: print("##", x[0], "\n", "\n\n".join(x[1:]), "\n")
    print("words M", sum(len(re.sub(r"\[@[^\]]+\]", "", t).split()) for x in METHODS for t in x[1:]), "R", sum(len(re.sub(r"\[@[^\]]+\]", "", t).split()) for x in RESULTS for t in x[1:]))
