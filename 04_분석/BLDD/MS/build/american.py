# american.py — AMA(미국식) 철자 변환: 빌더가 원고·표·범례·보충·커버 문자열을 출력 직전에 변환한다(참고문헌 서지는 원문 유지).
import re
STEMS = ["standardis", "harmonis", "summaris", "characteris", "categoris", "recognis", "emphasis", "minimis", "maximis", "prioritis", "utilis", "organis",
         "randomis", "generalis", "normalis", "visualis", "hospitalis", "urbanis", "stabilis", "specialis", "realis", "finalis", "authoris", "localis",
         "conceptualis", "operationalis", "penalis", "parameteris", "criticis", "hypothesis", "optimis", "mobilis"]
SUFFIX = r"(?:e|ed|es|ing|ation|ations|er|ers)"
WORDS = {"analyse": "analyze", "analysed": "analyzed", "analysing": "analyzing", "modelled": "modeled", "modelling": "modeling",
         "centre": "center", "centres": "centers", "centred": "centered", "neighbour": "neighbor", "neighbours": "neighbors", "neighbouring": "neighboring",
         "neighbourhood": "neighborhood", "neighbourhoods": "neighborhoods", "behaviour": "behavior", "behaviours": "behaviors", "behavioural": "behavioral",
         "ageing": "aging", "colour": "color", "colours": "colors", "favour": "favor", "favourable": "favorable", "labelled": "labeled", "travelled": "traveled",
         "grey": "gray", "fibre": "fiber", "programme": "program", "programmes": "programs", "haemoglobin": "hemoglobin", "glycaemic": "glycemic",
         "anaemia": "anemia", "anaemias": "anemias", "anaemic": "anemic", "haematology": "hematology", "haematological": "hematological", "haemophilia": "hemophilia",
         "haemolytic": "hemolytic", "haemorrhage": "hemorrhage", "haemostasis": "hemostasis", "foetal": "fetal", "paediatric": "pediatric", "oedema": "edema",
         "equalled": "equaled", "acknowledgement": "acknowledgment", "acknowledgements": "acknowledgments", "judgement": "judgment", "towards": "toward",
         "whilst": "while", "amongst": "among", "commonest": "most common"}
def amer(t):
    if not t: return t
    def stem(m):
        w = m.group(0); low = w.lower()
        for s in STEMS:
            if low.startswith(s) and re.fullmatch(SUFFIX, low[len(s):] or "x"):
                r = s[:-1] + "z" + low[len(s):]
                return r[0].upper() + r[1:] if w[0].isupper() else r
        return w
    t = re.sub(r"\b[A-Za-z]*is(?:e|ed|es|ing|ation|ations|er|ers)\b", stem, t)
    def word(m):
        w = m.group(0); r = WORDS.get(w.lower())
        if r is None: return w
        return r[0].upper() + r[1:] if w[0].isupper() else r
    t = re.sub(r"\b[A-Za-z]+\b", word, t)
    return t.replace("per cent", "percent")
if __name__ == "__main__":
    print(amer("Expected deaths were standardised and harmonised; anaemias, haematology, standardisation, Analysis, hypotheses, analyses, ageing, the commonest cause, promise, rise, otherwise, exercise."))
