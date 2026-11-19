#!/usr/bin/env python3
# 55N — BLDD: 전국 사인×성×5세 사망(KOSIS DT_1B34E01) 2025년만 받는다(2026-11-14). 34_fetch 원본은 long csv를 덮어쓰므로 쓰지 않는다.
#  키: ~/.kosis_key(내용 출력 금지). 산출: 00_원천/D_사망_인구_암/DT_1B34E01_national/2025.json, 02_패널/BLDD_national_2025_long.csv(D50-D89만)
import os, json, urllib.request, urllib.parse, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "00_원천", "D_사망_인구_암", "DT_1B34E01_national"); f = os.path.join(OUT, "2025.json")
if not os.path.exists(f):
    KEY = open(os.path.expanduser("~/.kosis_key")).read().strip()
    q = dict(method="getList", apiKey=KEY, itmId="ALL", objL1="ALL", objL2="ALL", objL3="ALL", format="json", jsonVD="Y",
             prdSe="Y", startPrdDe="2025", endPrdDe="2025", orgId="101", tblId="DT_1B34E01")
    d = json.loads(urllib.request.urlopen("https://kosis.kr/openapi/Param/statisticsParameterData.do?" + urllib.parse.urlencode(q), timeout=300).read().decode("utf-8"))
    if isinstance(d, dict): raise SystemExit(f"[55N] 오류 응답 코드: {d.get('err')} {d.get('errMsg')}")
    json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False)
d = json.load(open(f, encoding="utf-8"))
L = pd.DataFrame([dict(year=int(r["PRD_DE"]), cause_code=r["C1"], cause=r["C1_NM"], sex=r["C2_NM"], age_code=r["C3"], age=r["C3_NM"], item=r["ITM_NM"], value=pd.to_numeric(r["DT"], errors="coerce")) for r in d])
print("[55N] 2025 행", len(L), "전국 총사망", L[(L.cause == "계") & (L.sex == "계") & (L.age == "계") & (L.item == "사망자수")].value.tolist())
B = L[L.cause.str.contains("D50-D89")]; B.to_csv(os.path.join(ROOT, "02_패널", "BLDD_national_2025_long.csv"), index=False, encoding="utf-8-sig")
print("[55N] D50-D89 2025 사망 계", B[(B.sex == "계") & (B.age == "계") & (B.item == "사망자수")].value.tolist())
