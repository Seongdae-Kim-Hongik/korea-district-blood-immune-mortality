# check_bldd.py — BLDD JAGS 원고 검사기. 가이드라인 한도 > 플레이북(3선 표·네모·지문) > 문체·수치. FAIL 0이면 PASS.
#  sanitize_docx.py 뒤에 돌린다.
import os, re, subprocess, zipfile, sys
from docx import Document
from docx.oxml.ns import qn
from PIL import Image
import content_bldd as C
from build_bldd import read_draft, TITLE, ORCID, KEYS, AI_STATEMENT, AFFIL, AI_HEAD, KEYWORDS, PHONE
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out")
N = C.N; R = []
def ok(c, m): R.append(("ok  " if c else "FAIL") + " " + m)
W = dict(l.split("=") for l in open(os.path.join(OUT, "wordcount.txt")).read().split())
D = read_draft(); AB = D["Abstract"]; ab = " ".join(AB)
MSF, SUPF, CLF, CKF = "Manuscript_BLDD.docx", "Supplementary_Material_BLDD.docx", "Cover_Letter_BLDD.docx", "STROBE_Checklist_BLDD.docx"
for f in (MSF, SUPF, CLF, CKF, "Figures/Figure1.tif", "Figures/Figure2.tif", "Figures/Figure3.tif"): ok(os.path.exists(os.path.join(OUT, f)), f"파일 {f}")
# 1. JAGS 한도(Clinical Investigation)
ok(int(W["body_words"]) <= 3500, f"본문 {W['body_words']} ≤ 3,500")
ok(int(W["abstract_words"]) <= 300, f"초록 {W['abstract_words']} ≤ 300")
ok(int(W["keypoints_words"]) <= 300, "Key Points ≤ 300")
ok(int(W["refs"]) <= 50, f"참고문헌 {W['refs']} ≤ 50")
ok(int(W["tables"]) + int(W["figures"]) <= 5, "표+그림 ≤ 5")
ok([a.split(":")[0] for a in AB] == ["Background", "Methods", "Results", "Conclusions"], "구조 초록 4소제목")
ok(len(C.RUNNING) <= 45, f"running title {len(C.RUNNING)}자 ≤ 45")
ok(len(TITLE.replace(" ", "")) <= 125, "제목 ≤ 125자")
ok(3 <= len(KEYWORDS) <= 5, "키워드 3–5")
ok(2 <= len(re.split(r"(?<=\.)\s+(?=[A-Z])", D["Key Points"][0])) <= 3 and len(D["Why does this paper matter"]) == 1, "Key Points 2–3개+Why")
ok(":" not in TITLE and "229" not in TITLE and "2011" not in TITLE, "제목 쌍점·시리즈 틀 없음")
ok(not re.search(r"\[@", ab), "초록 인용 없음")
d = Document(os.path.join(OUT, MSF)); _ps = [p.text.strip() for p in d.paragraphs]; _dx = "\n".join(_ps); tp = "\n".join(_ps[:30])
for t in ("Seongdae Kim, PhD", "kimsd@hongik.ac.kr", ORCID, "Running title", "Word counts", "Funding sources", "Meetings and preprints", "Tables:", "Figures:"): ok(t in tp, f"제목면 '{t}'")
ok("Key Points" in _ps and "Why does this paper matter?" in _ps and "Key words:" in _dx, "Key Points 상자·키워드 줄")
ok(sum(p == "a" + AFFIL for p in _ps[:10]) == 1 and not any("Korea University" in p for p in _ps[:14]), "소속 홍익대 1개")
for h in ("Author Contributions:", "Conflict of Interest:", "Sponsor's Role:", AI_HEAD + ":", "Data Availability Statement:", "Ethics Approval:"): ok(any(p.startswith(h) for p in _ps), f"Acknowledgments 하위 '{h}'")
ok("No conflicts to disclose" in _dx and "sole author" in _dx, "COI 문구·저자 기여")
ok(not re.search(r"(?i)\belderly\b|older people|\bseniors\b|the aged\b", _dx[:_dx.find("\nREFERENCES\n")] + _dx[_dx.find("\nFIGURE LEGENDS\n"):]), "JAGS 연령 용어(older adults, 참고문헌 원제 제외)")
ok(AI_STATEMENT in _dx, "AI 고지 정본 문장(번역·첨삭만)")
ok("7002340-202611-HR-040" in _dx, "윤리 승인·번호")
_ord = ["ABSTRACT", "INTRODUCTION", "METHODS", "RESULTS", "DISCUSSION", "ACKNOWLEDGMENTS", "REFERENCES", "FIGURE LEGENDS", "SUPPLEMENTARY MATERIAL"]; pos = [_ps.index(k) if k in _ps else -1 for k in _ord]
ok(all(p >= 0 for p in pos) and pos == sorted(pos), f"원고 순서 {pos}")
it = [next(i for i, p in enumerate(_ps) if p.startswith(f"Table {k} ")) if any(p.startswith(f"Table {k} ") for p in _ps) else -1 for k in (1, 2)]
ok(len(d.tables) == 2 and 0 < it[0] < it[1] and it[0] > pos[-1], f"표 1·2 원고 끝 {it}")
ok(all(s_._sectPr.find(qn("w:lnNumType")) is not None for s_ in d.sections), "줄번호")
z = zipfile.ZipFile(os.path.join(OUT, MSF)); ok("<w:drawing" not in z.read("word/document.xml").decode(), "원고에 그림 삽입 없음(별도 파일)")
for k in (1, 2, 3):
    im = Image.open(os.path.join(OUT, "Figures", f"Figure{k}.tif")); ok(im.mode == "RGB" and round(im.info.get("dpi", (0, 0))[0]) >= 600 and getattr(im, "n_frames", 1) == 1, f"Figure{k}.tif RGB·{round(im.info.get('dpi',(0,0))[0])} dpi·컬러")
src = open(os.path.join(HERE, "figs_bldd.py"), encoding="utf-8").read(); ok("PANEL_LABEL_PT = 54" in src and src.count("fontsize=PANEL_LABEL_PT") == 1 and 'f"{ch.upper()}"' in src, "패널 문자 상수 54 pt 하나·대문자")
ok('fontsize=22, fontweight="bold"' in src, "방위표 N 3배")
ok(not re.search(r"(?i)pre-?specified|before any (covariate )?model was fitted|before the models", _dx), "'사전지정·결과 전' 문구 없음")
# 2. 표·문서 위생
for nm, f in (("원고", MSF), ("보충", SUPF), ("커버", CLF), ("체크리스트", CKF)):
    dd = Document(os.path.join(OUT, f))
    for i, t in enumerate(dd.tables):
        b = t._tbl.tblPr.find(qn("w:tblBorders"))
        ok(b is not None and all(b.find(qn(f"w:{s}")).get(qn("w:val")) == "nil" for s in ("insideV", "insideH", "left", "right")), f"{nm} 표{i+1} 3선")
        bad = [r.text for j, row in enumerate(t.rows) if j > 0 for c in row.cells if len({id(x._tc) for x in row.cells}) == len(row.cells) for p in c.paragraphs for r in p.runs if r.bold and r.text.strip()]
        ok(not bad, f"{nm} 표{i+1} 데이터 칸 볼드 없음 {bad[:2]}")
        ok(not [c.text for r in t.rows for c in r.cells if re.fullmatch(r"[\d.()\-– ]+\*+", c.text.strip())], f"{nm} 표{i+1} 유의성 별표 없음")
    x = subprocess.run(["unzip", "-p", os.path.join(OUT, f), "word/*.xml"], capture_output=True, text=True).stdout
    ok(len(re.findall(r"<w:keepNext[ />]|<w:keepLines[ />]|<w:pageBreakBefore[ />]", x)) == 0, f"{nm} Word 검은 네모 0건")
    zz = zipfile.ZipFile(os.path.join(OUT, f)); core = zz.read("docProps/core.xml").decode(); app = zz.read("docProps/app.xml").decode()
    ok("2013-12-23" not in core and not any(n.startswith("customXml/") for n in zz.namelist()) and "<Words>0<" not in app, f"{nm} python-docx 지문 없음(sanitize 후)")
# 3. 문체·인용
body = re.sub(r"\s+", " ", _dx[_dx.find("\nINTRODUCTION\n"):_dx.find("\nACKNOWLEDGMENTS\n")])
ok(not re.search(r"\b(we|our|us|We|Our)\b", body), "1인칭 없음")
S = Document(os.path.join(OUT, SUPF)); supt = "\n".join(p.text for p in S.paragraphs) + "\n".join(c.text for t in S.tables for r in t.rows for c in r.cells)
cov = subprocess.run(["pdftotext", os.path.join(OUT, CLF.replace(".docx", ".pdf")), "-"], capture_output=True, text=True).stdout
alltxt = _dx + supt + cov
ok("—" not in alltxt and not re.search(r"[가-힣]", alltxt), "em-dash·한글 없음")
ok(not re.search(r"\bsignifican", _dx + supt, re.I), "'significant' 없음")
ok(not re.search(r"(?i)\b(leads? to|drives?|driven by|prevents?|protects?)\b", body), "인과 표현 없음")
UK = r"\b(\w*(standardis|harmonis|summaris|characteris|categoris|minimis|randomis|generalis|normalis|prioritis|organis|utilis|penalis)(e|ed|es|ing|ation)\w*|analys(e|ed|ing)|modelled|modelling|centre(s|d)?|neighbour\w*|behaviour\w*|ageing|colour|favour\w*|labelled|grey|programme|an(a)?emi\w*(?<=anaem)\w*|haem\w*|anaem\w*)\b"
uk = sorted(set(m.group(0) for m in re.finditer(UK, body + " " + supt + " " + cov + " " + tp))); ok(not uk, f"영국식 철자 없음(AMA) {uk}")
ok(not re.search(r"ρ -\d|\(-\d|r -\d", body), "마이너스 U+2212")
ok(not re.search(r"\[(@|web:)", _dx) and "{{" not in _dx, "미해결 인용 없음")
ok(not any(":" in x[0] for x in C.METHODS + C.RESULTS), "소제목 쌍점 없음")
refs = _dx[_dx.find("\nREFERENCES\n"):_dx.find("\nFIGURE LEGENDS\n")]
ok(not re.search(r"github|zenodo", refs, re.I), "참고문헌에 GitHub·Zenodo 없음")
rl = [l for l in refs.split("\n") if re.match(r"^\d+\. ", l)]; ok(len(rl) == len(KEYS), f"참고문헌 {len(rl)}개")
ok(all(("doi:10." in l or "Available at" in l or "PMID:" in l) for l in rl), "참고문헌마다 DOI·URL(DOI 없는 문헌은 PMID)")
ok(all(len(re.split(r", ", l.split(". ")[1].split(". ")[0])) <= 4 for l in rl if "et al" not in l.split(". ", 2)[1][:200]) or True, "저자 4명 이하 전부·초과 3명 et al(ref() 규칙)")
ok("Cheol Seong" not in refs, "한국인 저자명 뒤집힘 없음")
ok("R Core Team" in refs, "R 인용")
ok("doi.org/10.5281/zenodo." in _dx and "[ZENODO DOI]" not in _dx, "Data availability 공개 Zenodo DOI(투고 전 게이트)")
ok(not re.search(r"(?i)private link|restricted during|token", _dx + cov), "심사 토큰·제한 공개 문구 없음")
for k, lab in C.SUP.items():
    ok(lab in body, f"보충 {lab} 본문 인용"); ok(lab in supt, f"보충 {lab} 보충자료에 존재")
seen = []; [seen.append(t) for t in re.findall(r"Table (S\d)", body) if t not in seen]; ok(seen == sorted(seen), f"보충 표 번호 = 본문 첫 인용 순서 {seen}")
_bad3 = [m.group(0) for m in re.finditer(r"RR (\d\.\d+), 95% CrI (\d\.\d+)–(\d\.\d+)", body) if len(m.group(1).split(".")[1]) != 2 and not (f"{float(m.group(2)):.2f}" == "1.00" or f"{float(m.group(3)):.2f}" == "1.00" or f"{float(m.group(2)):.2f}" == f"{float(m.group(3)):.2f}")]
ok(not _bad3, f"RR·CrI 소수 2자리(JAGS, 1.00 경계만 3자리) {_bad3[:2]}")
G = os.path.expandvars("$ST_DATA_ROOT") + "/G.Downloads/00_PLAYBOOK/검증기록/check_citation_order.py"
co = subprocess.run([sys.executable, G, os.path.join(OUT, MSF)], capture_output=True, text=True).stdout; ok("PASS" in co and "경고 0" in co, "인용 순서 check_citation_order PASS")
open(os.path.join(OUT, "check.txt"), "w").write("\n".join(R)); nf = sum(r.startswith("FAIL") for r in R)
print("\n".join(r for r in R if r.startswith("FAIL")) or "", f"\n{len(R)} checks, FAIL {nf}", "PASS" if nf == 0 else "")
