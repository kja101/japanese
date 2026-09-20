#!/usr/bin/env python3
"""Build every page from src/ templates and data/ JSON.

    python3 build/build.py

Reads:  src/*.html, src/common.js, data/*.json
Writes: assets/common.js and the pages in kanji/, words/ and kana/.
Standard library only. Run it from anywhere; paths are relative to the repo.
"""
import json, re, html as H
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, DATA = ROOT / "src", ROOT / "data"

def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))

def dump(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

def fill(template, **values):
    text = (SRC / template).read_text(encoding="utf-8")
    for key, val in values.items():
        token = f"__{key}__"
        if token not in text:
            raise SystemExit(f"{template}: placeholder {token} not found")
        text = text.replace(token, val)
    return text

def write(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  {rel}  ({len(text)//1024} KB)")

# ---------------------------------------------------------------- data
kanji = load("kanji.json")            # K, CH, LV, P for all N5-N2 kanji
words = load("kanji-words.json")      # words for every kanji, grouped by reading
readings = load("readings.json")      # reading dictionary for the on/kun engine
extra = load("sentences-extra.json")  # sentences written for the situation page
natural_en = load("sentence-builder-english.json")
KANJI_SET = dump("".join(kanji["K"].keys()))

def sentence_builder_sentences():
    """Parse the 120 sentences out of the sentence builder page (its HTML is their source)."""
    page = (SRC / "sentence-builder.html").read_text(encoding="utf-8")
    body = page[page.find("<body"):]
    txt = lambda s: H.unescape(re.sub(r"<[^>]+>", "", s)).strip()
    out = {}
    for m in re.finditer(r'<section class="card" id="(t\d+)"><header class="card-head"><h2>.*?</h2>(.*?)</section>', body, re.S):
        tid, sec = m.group(1), m.group(2)
        for i, s in enumerate(re.split(r'<div class="sent"', sec)[1:]):
            def line(cls):
                inner = re.search(r'<p class="line ' + cls + r'">(.*?)</p>', s, re.S).group(1)
                return re.findall(r'<span class="ck" style="--c:(#[0-9a-f]+)" data-r="(\w+)">(.*?)</span>', inner)
            kj, kn, rj, en = line("lay-kanji"), line("lay-kana"), line("lay-romaji"), line("en lay-en")
            why = re.search(r'<p class="why lay-why"><span class="wl">Why</span>(.*?)</p>', s, re.S)
            sid = f"{tid}-{i}"
            out.setdefault(tid, []).append({
                "id": "s" + sid, "kj": [txt(x[2]) for x in kj], "kn": [txt(x[2]) for x in kn],
                "rj": [txt(x[2]) for x in rj], "roles": [x[1] for x in kj],
                "enc": [[c, r, txt(t)] for c, r, t in en],
                "en": natural_en.get(sid) or " ".join(txt(x[2]) for x in en),
                "why": txt(why.group(1)) if why else ""})
    return out

SB = sentence_builder_sentences()
EXTRA = {}
for s in extra:
    EXTRA.setdefault(s["topic"], []).append({k: v for k, v in s.items() if k != "topic"})

def words_for(k):
    w = words.get(k)
    if not w:
        return None
    al = w.get("alone")
    return {"r": [[x["t"], x["label"], x["words"]] for x in w["readings"]], "sp": w["sp"],
            "al": [al["w"], al["r"], al["t"]] if al else None}

def kana_words():
    """Kana words plus one example sentence each, found in the site's own sentences."""
    data = load("kana-words.json")
    NOTE = re.compile(r"([\u4e00-\u9fff々ヶ]+)\{([^}]+)\}")
    plain = lambda s: NOTE.sub(r"\1", s)
    kana = lambda s: NOTE.sub(r"\2", s)
    corpus = []
    for sents in SB.values():
        for s in sents:
            corpus.append((list(zip(s["kj"], s["kn"])), s["en"]))
    for s in extra:
        corpus.append(([(plain(t), kana(t)) for t in s["n"].split(" ")], s["en"]))
    for c in load("phrasebook.json"):
        for sec in c["phr"]:
            for line in sec["items"].strip().split("\n"):
                jp, en = line.split("|")[:2]
                if "___" in jp:
                    continue
                corpus.append(([(plain(t), kana(t)) for t in jp.split(" ")], en))
    for w in data["words"]:
        key = w["w"].strip("～〜")
        if len(key) < 2:
            continue
        pat = re.compile(r"(?<![\u4e00-\u9fff])" + re.escape(key))
        hits = [(p, en) for p, en in corpus if pat.search("".join(k for k, _ in p))]
        if hits:
            p, en = min(hits, key=lambda h: len("".join(k for k, _ in h[0])))
            w["ex"] = {"p": p, "en": en}
    return data

print("Building:")
# ---------------------------------------------------------------- shared script
write("assets/common.js", (SRC / "common.js").read_text(encoding="utf-8").replace("__READINGS__", dump(readings)))

# ---------------------------------------------------------------- master deck
write("kanji/master-kanji-shapes.html",
      fill("master.html", DATA=dump({"K": kanji["K"], "CH": kanji["CH"], "LV": kanji["LV"], "W": words, "P": kanji["P"]})))

# ---------------------------------------------------------------- kanji by situation
sit = load("situation.json")
topics = sit["topics"]
for t in topics:
    t["sents"] = []
tix = {t["id"]: t for t in topics}
for sb_topic, sents in SB.items():
    tix[sit["sb_map"][sb_topic]]["sents"] += [{k: s[k] for k in ("kj", "kn", "rj", "en", "why")} for s in sents]
for topic, sents in EXTRA.items():
    tix[topic]["sents"] += [{"n": s["n"], "en": s["en"], "why": s["why"]} for s in sents]
K = {r["k"]: r for t in topics for g in t["groups"] for r in g["rows"]}
W = {k: words_for(k) for k in K if words_for(k)}
write("kanji/kanji-by-situation.html",
      fill("situation.html", DATA=dump({"T": topics, "K": K, "W": W, "LV": kanji["LV"], "apx": sit["apx"], "lede": sit["lede"]})))

# ---------------------------------------------------------------- phrasebook
chapters = load("phrasebook.json")
for c in chapters:
    c["sents"] = [s for t in c.pop("sb") for s in SB.get(t, [])] + [s for t in c.pop("extra") for s in EXTRA.get(t, [])]
    c.pop("_count_check", None)
write("words/phrasebook.html", fill("phrasebook.html", DATA=dump(chapters), KANJI_SET=KANJI_SET))

# ---------------------------------------------------------------- sentence builder
write("words/sentence-builder.html", fill("sentence-builder.html", KANJI_SET=KANJI_SET))

# ---------------------------------------------------------------- study plan
write("kanji/learn-n5-n4.html", fill("study.html", DATA=dump(load("study.json"))))

# ---------------------------------------------------------------- kana
write("kana/kana-sounds.html", (SRC / "kana-sounds.html").read_text(encoding="utf-8"))
write("kana/kana-words.html", fill("kana-words.html", DATA=dump(kana_words())))
print("Done.")
