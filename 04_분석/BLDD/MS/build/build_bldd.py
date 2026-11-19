# build_bldd.py — BLDD 원고 조립, JAGS Clinical Investigation(2026-11-19 규정 확인, agsjournals.onlinelibrary.wiley.com/hub/journal/15325415/forauthors.html).
#  제목면(제목 ≤125자·running title ≤45자·저자·학위·소속 각주·연구비·학회/프리프린트·교신 주소·단어 수) → Key Points 상자 → 구조 초록(≤300)+키워드 3–5 →
#  INTRODUCTION·METHODS·RESULTS·DISCUSSION·ACKNOWLEDGMENTS(기여·COI·Sponsor's Role·AI)·REFERENCES·LEGENDS, 표는 참고문헌 뒤 세로. AMA 참고문헌(6명 이하 전부, 초과 3명 et al), 위첨자 번호.
#  12 pt·이중 간격·쪽 번호·연속 줄번호. 미국식 철자(american.py). 단독 저자, 소속 홍익대 하나.
import os, re, json, subprocess
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt
from jkms_engine import JKMS
from american import amer
import content_bldd as C
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_bldd.json"), encoding="utf-8"))
DRAFT = os.path.join(MS, "draft", "01_manuscript.md")
_zf = os.path.join(OUT, "zenodo_doi.txt"); ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "[ZENODO DOI]"
TITLE = C.TITLE; ORCID = "0000-0002-1525-0091"
AFFIL = "Department of Biohealth Convergence Open Sharing System, Hongik University, Seoul, Republic of Korea"
ADDRESS = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
AI_STATEMENT = ("The author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript. "
                "They were not used to design the study, analyze data, interpret results or generate references. The author reviewed and edited the content and takes full responsibility for it.")
AI_HEAD = "Use of Artificial Intelligence Tools"
PHONE = "+82-2-320-1114"
KEYWORDS = C.KEYWORDS
FUNDING = "No funding was received for this study."
COI = "Seongdae Kim: No conflicts to disclose."
SPONSOR = "Not applicable; the study received no funding."
ETHICS = "The Institutional Review Board of Hongik University approved the study (7002340-202511-HR-012; continuing review 7002340-202611-HR-040) and waived informed consent because only published aggregate statistics were used."
AUTHORSHIP = "Seongdae Kim: study concept and design, acquisition of data, analysis and interpretation of data, and preparation of the manuscript (sole author)."
ACK_STATEMENT = "The corresponding author affirms that everyone who contributed substantially to the work is listed; no other contributors are named."
MEETING = "This work has not been presented at a meeting or posted as a preprint."
def data_statement(): return (f"All source data are publicly available aggregate statistics from Statistics Korea, the Ministry of the Interior and Safety, the National Health Insurance Service health screening statistics and the other national sources cited in the Methods. "
                             f"The analysis code that generates every number, table and figure is openly available on Zenodo (https://doi.org/{ZENODO}). The processed district-year data are available from the author on reasonable request.")

def read_draft():
    md = open(DRAFT, encoding="utf-8").read(); md = re.sub(r"<!--.*?-->", "", md, flags=re.S); S = {}; cur = None
    for line in md.split("\n"):
        m = re.match(r"^## (.+)$", line)
        if m: cur = m.group(1).strip(); S[cur] = []; continue
        if cur is not None: S[cur].append(line)
    return {k: [p.strip() for p in "\n".join(v).split("\n\n") if p.strip()] for k, v in S.items()}
def pandoc_cites(t): return re.sub(r"\s*\[(@[^\]]+)\]", lambda m: "{{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
def all_keys():
    src = open(os.path.join(HERE, "content_bldd.py"), encoding="utf-8").read() + open(DRAFT, encoding="utf-8").read()
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S); src = re.sub(r"(?m)^\s*#.*$", "", src)
    return sorted(k for k in {k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")} if re.fullmatch(r"(web:)?[a-z][a-z0-9]*", k))
KEYS = all_keys()

MON = {m: i for i, m in enumerate(["January","February","March","April","May","June","July","August","September","October","November","December"], 1)}
def acc(d):   # '14 November 2026' -> 'November 14, 2026'
    dd, mm, yy = d.split(); return f"{mm} {int(dd)}, {yy}"
def ref(k):   # JAGS(AMA 변형): 6명 이하 전부, 초과 3명 + et al. 약어 저널명, Year;Vol:first–last. doi
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. {r['title']} (online). Available at: {r['url']}. Accessed {acc(r['accessed'])}."
    au = r["authors"]; a = ", ".join(au) if len(au) <= 6 else ", ".join(au[:3]) + " et al"
    t = r["title"].rstrip("."); t = t + ("" if t.endswith(("?", "!")) else ".")
    s = f"{a}. {t} {r['journal']} {r['year']}"
    if r.get("vol"): s += f";{r['vol']}"
    if r.get("pages"): s += f":{r['pages'].replace('-', '–')}"
    s += "."
    if r.get("doi"): s += f" doi:{r['doi']}"
    elif r.get("pmid"): s += f" PMID: {r['pmid']}."
    return s

class TX(JKMS):
    raw = False
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw:
            text = amer(text); text = re.sub(r"(^|[\s(])-(?=\d)", "\\1\u2212", text)
        return super()._emit(p, text, sz, bold, italic)

TAB1_COV = [("ext__anaemia_suspect_sir", "Suspected anaemia at screening, log standardised ratio"), ("ext__kidney_suspect_share", "Suspected kidney disease at screening, %"), ("basic_livelihood_rate", "Basic livelihood recipients, %"),
            ("tertiary_educated_share", "Tertiary-educated adults, %"), ("ext__unmet_need_rate", "Unmet medical need, %"), ("ltc_hospitals_per_100k_65", "Long-term care hospitals per 100,000 aged ≥ 65 years"),
            ("im_specialists_per_100k", "Internal-medicine specialists, log(1 + per 100,000)"), ("ill_defined_death_share", "Ill-defined causes of death, %"), ("fiscal_independence", "Fiscal autonomy, %"), ("pop80_share", "Population aged ≥ 80 years, %")]
WC = ["W1_2011-15", "W2_2016-19", "W3_2020-25", "ALL"]; WH = ["2011–2015", "2016–2019", "2020–2025", "2011–2025"]
def table1():
    T = N["T1"]; A = N["asr"]
    def mean_asr(a, b): return sum(A[(y, "계")] for y in range(a, b + 1)) / (b - a + 1)
    rows = [["__H__", "Deaths"], ["  District-years, no."] + [f"{T[c]['n']:,}" for c in WC], ["  Deaths (D50–D89), no."] + [f"{T[c]['cases']:,}" for c in WC],
            ["  District-years with no death, no."] + [f"{T[c]['zeros']:,}" for c in WC],
            ["  Age-standardised rate per 100,000*"] + [f"{mean_asr(a, b):.2f}" for a, b in ((2011, 2015), (2016, 2019), (2020, 2025), (2011, 2025))],
            ["  District SMR, median (P10–P90)†"] + [f"{T[c]['med']:.2f} ({T[c]['p10']:.2f}–{T[c]['p90']:.2f})" for c in WC], ["__H__", "District characteristics, mean (SD)"]]
    for v, lab in TAB1_COV:
        mx = max(abs(T[c]['cov'][v][0]) for c in WC); dp = 0 if mx >= 100 else (2 if mx < 1 else 1)
        rows.append([f"  {lab}"] + [f"{T[c]['cov'][v][0]:.{dp}f} ({T[c]['cov'][v][1]:.{dp}f})" for c in WC])
    foot = ("P10–P90, 10th–90th percentile; SD, standard deviation; SMR, standardised mortality ratio. *Mean of annual national rates, 2020 resident population as standard. †Observed over sex- and age-standardised expected deaths summed over the period. "
            "Characteristics are district-year means; the other forced controls are in Supplementary Table S1. Values not yet published for 2025 carried their 2024 values.")
    return (f"Table 1 Blood and immune disorder deaths and district characteristics, {N['n_districts']} districts, Republic of Korea, 2011–2025", ["Characteristic"] + WH, rows, foot)

GROUPS = [("Anaemia and kidney disease burden", [C.ANE, C.KID]), ("Deprivation and access", [C.BLS, C.TE, C.UNM]), ("Care and certification", [C.LTC, C.IMS, C.ILL]),
          ("Forced controls", ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"])]
LABEL = {C.ANE: "Suspected anaemia, standardised ratio (+)", C.KID: "Suspected kidney disease (+)", C.BLS: "Basic livelihood recipients (+)", C.TE: "Tertiary-educated adults (−)", C.UNM: "Unmet medical need (+)",
         C.LTC: "Long-term care hospitals (+)", C.IMS: "Internal-medicine specialists (−)", C.ILL: "Ill-defined causes of death (−)",
         "urban_population_share": "Urban population share", "physicians_per_1000": "Physicians per 1,000", "sex_ratio": "Sex ratio", "fiscal_independence": "Fiscal autonomy", "pop80_share": "Population aged ≥ 80 years"}
def f3(t): a, b, c = C._fmt(t); return f"{a} ({b}–{c})"
def table2():
    rows = []; assert sum(len(v) for g, v in GROUPS[:-1]) == N["n_hyp"] and set(LABEL) == set(N["main"])
    for g, vs in GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            m = N["main"][v]; mv = N["mv"].get(v); k = N["s43"][(C.BEST_KH, v)]; y24 = N["sens"]["sens_y24"][v]; sc = N["sens"]["sens_crude"][v]; tr = N["nco"][("TRANS", v)]
            rows.append([f"  {LABEL[v]}", f3((m["IRR"], m["lo"], m["hi"])), f"{100*mv['cred_frac']:.1f}" if mv else "Forced", f3(k), f3(y24), f3(sc), f3(tr)])
    foot = (f"CrI, credible interval; RR, rate ratio per 1 standard deviation; expected direction in parentheses. Principal model: negative binomial with a Besag–York–Mollié 2 district effect and random-walk and independent year effects, all characteristics and five forced controls (n = {N['n_rows']:,} district-years). "
            "Credibility was judged on unrounded interval limits; limits that round to 1.00 are shown to three decimals. *Share of the 200 covariate-subset models containing the characteristic in which the CrI excluded 1. †Knorr-Held type IV space-time interaction added, the best-fitting interaction model. "
            "‡Crude expected deaths (population × national rate) instead of sex- and age-standardised expected deaths. §Transport-injury deaths as a comparison outcome with the same model.")
    return (f"Table 2 District characteristics and blood and immune disorder deaths, {N['n_districts']} districts, Republic of Korea, 2011–2025",
            ["Characteristic", "Principal RR (95% CrI)", "Subsets credible, %*", "Type IV RR (95% CrI)†", "2011–2024 only", "Crude expected deaths‡", "Transport-injury deaths§"], rows, foot)

FIGCAP = {
 1: "Deaths from blood and immune disorders (International Classification of Diseases, 10th Revision, D50–D89), Republic of Korea, 2011–2025. (A) Deaths by year and sex. (B) Age-standardised rates per 100,000 (2020 resident population as standard) by sex. (C) Age distribution of deaths by sex.",
 2: "District geography of blood and immune disorder deaths, 229 districts, 2011–2025. (A) Standardised mortality ratio (observed over sex- and age-standardised expected deaths), 15 years pooled. (B) Residual spatial rate ratio from the principal model. (C) Residual hot spots and cold spots (posterior probability of a rate ratio above 1 greater than 0.95 or less than 0.05). Thick lines are province boundaries.",
 3: "Residual spatial rate ratios refitted separately in (A) 2011–2015, (B) 2016–2019 and (C) 2020–2025, 229 districts. Hot spots (posterior probability of a rate ratio above 1 greater than 0.95) are outlined.",
}
SUPPINFO = ["Supplementary Text S1. Supplementary methods and additional results.", "Supplementary Table S1. Source, unit, expected direction and filled cells of each district characteristic.",
            "Supplementary Table S2. Likelihood comparison.", "Supplementary Table S3. Rate ratios across alternative specifications.", "Supplementary Table S4. Residual hot spots and cold spots.", "Supplementary Text S2. STROBE checklist."]
def foot_row(J, text, sz=9, ls=13):
    from docx.enum.text import WD_LINE_SPACING
    t = J.doc.tables[-1]; r = t.add_row(); m = r.cells[0].merge(r.cells[-1]); m.text = ""; p = m.paragraphs[0]
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(ls); p.paragraph_format.space_before = Pt(4)
    c = J.counting; J.counting = False; J._emit(p, text, sz); J.counting = c
def put_table(J, t, fs=9):
    c = J.counting; J.counting = False; J.table_fit(t[0], t[1], t[2], "", fs_max=fs, title_bold=True); foot_row(J, t[3], 8); J.counting = c
def box(p):   # Key Points 상자: 문단 테두리(표가 아님)
    pPr = p._p.get_or_add_pPr(); b = OxmlElement("w:pBdr")
    for side in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{side}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "8"); e.set(qn("w:space"), "6"); e.set(qn("w:color"), "000000"); b.append(e)
    pPr.append(b)
HEADS = ["INTRODUCTION", "METHODS", "RESULTS", "DISCUSSION", "ACKNOWLEDGMENTS", "REFERENCES", "FIGURE LEGENDS", "SUPPLEMENTARY MATERIAL"]

def build(bw=0, aw=0, kw=0):
    D = read_draft(); J = TX(cite="sup")
    J.para(f"<b>{TITLE}</b>")
    J.para(f"<b>Running title:</b> {C.RUNNING}", before=6)
    J.para("Seongdae Kim, PhD<sup>a</sup>", before=6); J.para(f"<sup>a</sup>{AFFIL}"); J.para(f"ORCID: https://orcid.org/{ORCID}")
    J.para(f"<b>Corresponding author:</b> Seongdae Kim, PhD, {ADDRESS}. Telephone: {PHONE}. Email: kimsd@hongik.ac.kr", before=6)
    J.para(f"<b>Funding sources:</b> {FUNDING}", before=6); J.para(f"<b>Meetings and preprints:</b> {MEETING}")
    J.para(f"<b>Word counts:</b> abstract {aw}; main text {bw}; Key Points box {kw}. <b>Tables:</b> 2. <b>Figures:</b> 3.", before=6)
    J.page_break()
    kp = re.split(r"(?<=\.)\s+(?=[A-Z])", D["Key Points"][0]); assert 2 <= len(kp) <= 3
    ps = [J.para("<b>Key Points</b>")] + [J.para(f"• {x}") for x in kp] + [J.para("<b>Why does this paper matter?</b>")] + [J.para(D["Why does this paper matter"][0])]
    for q in ps:
        if q is not None: box(q)
    J.page_break(); J.head("ABSTRACT", 1)
    for p in D["Abstract"]:
        lab, txt = p.split(": ", 1); J.para(f"<b>{lab}:</b> {txt}")
    J.para(f"<b>Key words:</b> {'; '.join(KEYWORDS)}", before=6)
    J.page_break(); J.counting = True
    J.head("INTRODUCTION", 1)
    for p in D["Introduction"]: J.para(pandoc_cites(p), indent=True)
    J.head("METHODS", 1)
    for x in C.METHODS:
        J.head(x[0], 2)
        for p in x[1:]: J.para(pandoc_cites(p), indent=True)
    J.head("RESULTS", 1)
    for x in C.RESULTS:
        J.head(x[0], 2)
        for p in x[1:]: J.para(pandoc_cites(p), indent=True)
    J.head("DISCUSSION", 1)
    for p in D["Discussion"]:
        if p.startswith("### "): J.head(p[4:].strip(), 2); continue
        J.para(pandoc_cites(p), indent=True)
    J.counting = False
    J.head("ACKNOWLEDGMENTS", 1); J.para(ACK_STATEMENT)
    J.para(f"<b>Author Contributions:</b> {AUTHORSHIP}"); J.para(f"<b>Conflict of Interest:</b> {COI}"); J.para(f"<b>Sponsor's Role:</b> {SPONSOR}")
    J.para(f"<b>Funding:</b> {FUNDING}"); J.para(f"<b>{AI_HEAD}:</b> {AI_STATEMENT}")
    J.para(f"<b>Data Availability Statement:</b> {data_statement()}"); J.para(f"<b>Ethics Approval:</b> {ETHICS}")
    assert sorted(J.cites) == KEYS, (set(J.cites) ^ set(KEYS))
    J.page_break(); J.head("REFERENCES", 1); J.raw = True; rl = []
    for i, k in enumerate(J.cites, 1): s = f"{i}. " + ref(k); rl.append(s); J.para(s)
    J.raw = False
    J.page_break(); J.head("FIGURE LEGENDS", 1)
    for k in sorted(FIGCAP): J.para(f"<b>Figure {k}.</b> {FIGCAP[k]}", after=6)
    J.head("SUPPLEMENTARY MATERIAL", 1)
    for x in SUPPINFO: J.para(x)
    J.page_break(); put_table(J, table1())
    J.page_break(); put_table(J, table2(), fs=8)
    return J, rl, D

def docx_bw(path):   # 본문 단어 수: INTRODUCTION ~ DISCUSSION 끝(ACKNOWLEDGMENTS 직전)
    from docx import Document
    t = "\n".join(x.text for x in Document(path).paragraphs)
    i = t.find("\nINTRODUCTION\n"); j = t.find("\nACKNOWLEDGMENTS\n"); assert 0 < i < j; return len(t[i:j].split()) - 1
def fix_orphans(path, heads, max_iter=8):
    from docx import Document
    fixed = set()
    for _ in range(max_iter):
        pdf = path.replace(".docx", ".pdf")
        subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_bldd_ms2", "--convert-to", "pdf", "--outdir", os.path.dirname(path), path], check=True, capture_output=True)
        pages = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout.split("\f"); orphan = None
        for pg in pages:
            ls = [re.sub(r"^\d+\s+", "", l.strip()) for l in pg.split("\n") if l.strip()]; ls = [l for l in ls if not re.fullmatch(r"\d+", l)]
            if ls and ls[-1] in heads:
                k = len(ls) - 1
                while k > 0 and ls[k - 1] in heads: k -= 1
                orphan = ls[k]; break
        if orphan is None: return
        if orphan in fixed: print("orphan persists, stop:", orphan); return
        fixed.add(orphan); d = Document(path)
        for p in d.paragraphs:
            if p.text.strip() == orphan:
                np_ = OxmlElement("w:p"); r = OxmlElement("w:r"); br = OxmlElement("w:br"); br.set(qn("w:type"), "page"); r.append(br); np_.append(r); p._p.addprevious(np_); break
        d.save(path); print("orphan fixed:", orphan)

if __name__ == "__main__":
    p = os.path.join(OUT, "Manuscript_BLDD.docx"); D = read_draft()
    aw = sum(len(x.split()) for x in D["Abstract"]) - len(D["Abstract"])   # 소제목 단어 제외
    kw = sum(len(x.split()) for x in D["Key Points"] + D["Why does this paper matter"])
    J, rl, D = build(); J.doc_title = "Manuscript"; J.save(p); bw = docx_bw(p)
    J, rl, D = build(bw, aw, kw); J.doc_title = "Manuscript"; J.save(p); assert docx_bw(p) == bw
    heads = set(HEADS) | {"ABSTRACT"} | {x[0] for x in C.METHODS + C.RESULTS} | {p[4:].strip() for p in D["Discussion"] if p.startswith("### ")}
    fix_orphans(p, heads)
    open(os.path.join(OUT, "wordcount.txt"), "w").write(f"body_words={bw}\nabstract_words={aw}\nkeypoints_words={kw}\nrefs={len(KEYS)}\ntables=2\nfigures=3\nrunning_title_chars={len(C.RUNNING)}\ntitle_chars_nospace={len(TITLE.replace(' ', ''))}\n")
    open(os.path.join(OUT, "reference_list.txt"), "w").write("\n".join(rl) + "\n")
    print(f"body {bw} | abstract {aw} | key points {kw} | refs {len(KEYS)}")
    assert bw <= 3500 and aw <= 300 and kw <= 300 and len(KEYS) <= 50 and len(C.RUNNING) <= 45 and 3 <= len(KEYWORDS) <= 5
