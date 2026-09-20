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

HEAD_EXTRA = ('<link rel="manifest" href="{r}manifest.webmanifest">\n<meta name="theme-color" content="#B3261E">\n'
              '<link rel="apple-touch-icon" href="{r}assets/icons/icon-180.png">\n<meta name="apple-mobile-web-app-capable" content="yes">\n')
WRITTEN = []

COMMON_VERSION = ""   # set once assets/common.js is written; pages load common.js?v=<version> so a page and its script always match

def write(rel, text):
    if rel.endswith(".html") and COMMON_VERSION:
        text = text.replace('assets/common.js"', 'assets/common.js?v=' + COMMON_VERSION + '"')
    if rel.endswith(".html") and 'rel="manifest"' not in text:
        depth = "../" * rel.count("/")
        text = text.replace("</head>", HEAD_EXTRA.format(r=depth) + "</head>", 1)
    WRITTEN.append(rel)
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  {rel}  ({len(text)//1024} KB)")

# ---------------------------------------------------------------- data
kanji = load("kanji.json")            # K, CH, LV, P for all N5-N2 kanji
words = load("kanji-words.json")      # words for every kanji, grouped by reading
readings = load("readings.json")      # reading dictionary for the on/kun engine
extra = load("sentences-extra.json")  # sentences written for the situation page
for _lv in (5, 4, 3, 2):                  # sentences written to cover words and kanji, level by level
    if (DATA / f"sentences-n{_lv}.json").exists():
        extra += load(f"sentences-n{_lv}.json")
natural_en = load("sentence-builder-english.json")
KANJI_SET = dump("".join(kanji["K"].keys()))

def kana_word_map():
    """Hiragana and katakana words that have their own card, for linking from sentences."""
    out = {}
    for name, tag in (("kana-words.json", "h"), ("katakana-words.json", "k")):
        for w in load(name)["words"]:
            if w.get("g") == "parts":
                continue
            key = w["w"].strip("～〜")
            key = key[:-2] if key.endswith("する") and tag == "k" else key
            if len(key) >= 2 and "～" not in key and "〜" not in key:
                out.setdefault(key, tag)
    return dump(out)
KANA_WORDS = kana_word_map()

NOTE_RE = re.compile(r"([\u4e00-\u9fff々ヶ]+)\{([^}]+)\}")

def token_roles(n, jr):
    """Hand-marked blocks [[role, text], ...] → one role per space-separated token of the sentence."""
    toks = n.split(" ")
    plains = [NOTE_RE.sub(r"\1", t) for t in toks]
    full = "".join(plains)
    marked = "".join(t for _, t in jr).replace(" ", "")
    if marked != full:
        raise SystemExit(f"block marking doesn't match the sentence:\n  {full}\n  {marked}")
    bounds, pos = [], 0
    for r, t in jr:
        t = t.replace(" ", "")
        bounds.append((pos, pos + len(t), r)); pos += len(t)
    out, pos = [], 0
    for p in plains:
        out.append(next((r for a, z, r in bounds if a <= pos < z), "V")); pos += len(p)
    return out

def english_blocks(en, er):
    """Colour the English: find each marked phrase (or, failing that, its words) and tag it with its block."""
    low = en.lower()
    mask = [""] * len(en)
    def place(t, r):
        t = t.strip().lower()
        if not t:
            return False
        start = 0
        while True:
            k = low.find(t, start)
            if k < 0:
                return False
            if all(m == "" for m in mask[k:k + len(t)]):
                for q in range(k, k + len(t)):
                    mask[q] = r
                return True
            start = k + 1
    for r, t in er:
        if not place(t, r):                       # reordered English: colour the words that are there
            for word in re.findall(r"[\w']+|[?!]", t):
                if len(word) > 1 or word in "?!":
                    place(word, r)
    segs = []
    for ch, r in zip(en, mask):
        if segs and segs[-1][0] == r:
            segs[-1][1] += ch
        else:
            segs.append([r, ch])
    return segs

def mark(s):
    """Add token roles and coloured English to a sentence that has hand-marked blocks."""
    s = dict(s)
    if s.get("jr") and s.get("n"):
        s["roles"] = token_roles(s["n"], s["jr"])
    if s.get("er"):
        s["enb"] = english_blocks(s["en"], s["er"])
    s.pop("jr", None); s.pop("er", None)
    return s

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
            s_ = out[tid][-1]
            s_["enb"] = english_blocks(s_["en"], [[r, txt(t)] for c, r, t in en])
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

I_ROW = "いきしちにひみりぎじびぴ"
E_ROW = "えけせてねへめれげぜべぺ"

GODAN = {"う": ("い", "わ", "っ"), "く": ("き", "か", "い"), "ぐ": ("ぎ", "が", "い"), "す": ("し", "さ", "し"), "つ": ("ち", "た", "っ"),
         "ぬ": ("に", "な", "ん"), "ぶ": ("び", "ば", "ん"), "む": ("み", "ま", "ん"), "る": ("り", "ら", "っ")}
END = r"(?![\u3041-\u309f])|(?=[はがをにでへともかやねよの][^\u3041-\u309f]|です|でした|ので|のに|と)"

GODAN_RU = {"かじる", "ちぎる", "しゃべる", "かえる", "はいる", "しる", "きる", "はしる", "いる", "へる", "すべる", "ける", "にぎる"}   # look like る-verbs but aren't
HONORIFIC_I = {"いらっしゃる", "なさる", "くださる", "おっしゃる"}   # ます-stem in い: いらっしゃいます

def word_pattern(key, group):
    """A regex that finds a kana word in a sentence, including the usual conjugated forms of verbs and adjectives."""
    r = word_regex(key, group)
    return re.compile(r)

def spaced(s):
    """Escape a word so it still matches when learner spacing splits it (おいでに なります)."""
    return r"\s?".join(re.escape(c) for c in s)

def word_regex(key, group):
    kata = r"[\u30a0-\u30ffー]"
    # not straight after a kanji or inside a hiragana word, but fine after a particle or a て-form (…は とても, …て もう)
    before = r"(?<![\u4e00-\u9fff" + "".join(c for c in map(chr, range(0x3041, 0x30a0)) if c not in "はがをにでへともかやねよのてた、。") + r"])"
    if key.endswith("する"):                                  # する, コピーする, びっくりする
        stem = key[:-2]
        edge = r"(?<!" + kata + ")" if stem and re.match(kata, stem[0]) else before[:-2] + r"\u30a0-\u30ffー])"
        return (edge + spaced(stem) + r"\s*(?:する|します|しま|した|して|しない|させ|される|しよう|すれ)")
    if re.fullmatch(kata + "+", key):                          # katakana: whole words only (カー is not in カード)
        return (r"(?<!" + kata + ")" + re.escape(key) + r"(?!" + kata + ")")
    if group == "verb" and key[-1] in GODAN:
        stem = spaced(key[:-1])
        if key[-1] == "る" and len(key) >= 3 and key[-2] in I_ROW + E_ROW and key not in GODAN_RU:   # る-verb
            forms = r"(?:る|ます|まし|ません|て|た|ない|なかっ|られ|よう|れば)"
            return (before + stem + forms)
        i, a, t = GODAN[key[-1]]
        if key in HONORIFIC_I:
            i = "い"
        te = ("て" if t in "いし" else "で") if key[-1] in "ぐぬぶむ" else "て"
        ta = "だ" if key[-1] in "ぐぬぶむ" else "た"
        forms = r"(?:" + "|".join([i + "ま", i + "たい", i + "ながら", t + te, t + ta, a + "な", a + "れ", a + "せ", re.escape(key[-1]) + "(?:" + END + ")"]) + ")"
        if key == "いく" or key == "行く":
            forms = forms.replace("いて", "って").replace("いた", "った")
        return (before + stem + forms)
    if group == "desc" and key.endswith("い") and len(key) >= 3:        # い-adjective
        return (before + spaced(key[:-1]) + r"(?:くな|かっ|くて|ければ|く(?![\u3041-\u309f])|い(?:" + END + "))")
    if len(key) <= 2:                                                   # short words: must stand alone
        return (before + spaced(key) + r"(?:" + END + ")")
    if len(key) >= 3:
        return (before + spaced(key))
    return (before + spaced(key) + r"(?:" + END + ")")

def sentence_records(include_phrases=True, include_grammar=False):
    """Every sentence on the site as (record, plain text with spaces between chunks). A record is what the pages render."""
    recs = []
    for sents in SB.values():
        for s in sents:
            recs.append(({k: s[k] for k in ("kj", "kn", "rj", "roles", "en", "enb")}, " ".join(s["kj"])))
    for s in extra:
        r = mark({k: v for k, v in s.items() if k in ("n", "en", "jr", "er")})
        recs.append((r, " ".join(NOTE_RE.sub(r"\1", t) for t in s["n"].split(" "))))
    if include_grammar:
        for g in load("grammar.json"):
            for e in g["ex"]:
                r = mark(e)
                recs.append((r, " ".join(NOTE_RE.sub(r"\1", t) for t in e["n"].split(" "))))
    if include_phrases:
        for c in load("phrasebook.json"):
            for sec in c["phr"]:
                marks = sec.get("marks", {})
                for i, line in enumerate(sec["items"].strip().split("\n")):
                    jp, en = line.split("|")[:2]
                    if "___" not in jp:
                        r = mark({"n": jp, "en": en, **marks.get(str(i), {})})
                        recs.append((r, " ".join(NOTE_RE.sub(r"\1", t) for t in jp.split(" "))))
    return recs

def kana_words(name="kana-words.json"):
    """Kana words plus one example sentence each, found in the site's own sentences."""
    data = load(name)
    corpus = sentence_records()
    allkeys = [w["w"].strip("～〜") for w in data["words"]]
    for w in data["words"]:
        key = w["w"].strip("～〜")
        if len(key) < 2:
            continue
        pat = word_pattern(key, w.get("g", ""))
        longer = [o for o in allkeys if len(o) > len(key) and o.startswith(key)]
        def found(text):
            for m in pat.finditer(text):
                if not any(text.startswith(o, m.start()) for o in longer):   # いつ is not the いつ in いつも
                    return True
            return False
        hits = [(r, t) for r, t in corpus if found(t)]
        if hits:
            w["ex"] = min(hits, key=lambda h: len(h[1].replace(" ", "")))[0]
    return data

VARIANTS = {"亻": "人", "氵": "水", "扌": "手", "忄": "心", "訁": "言", "糹": "糸", "飠": "食", "釒": "金"}

def study_data():
    """Everything the daily study plan needs, for all N5-N2 kanji, from data/kanji.json."""
    K, CH = kanji["K"], kanji["CH"]
    NOTE = re.compile(r"([\u4e00-\u9fff々ヶ]+)\{([^}]+)\}")
    chap = {k: i for i, c in enumerate(CH) for k in c["kanji"]}
    def example(k):
        x = K[k]
        if x.get("ex"):                          # hand-picked word (N5 and N4)
            return [NOTE.sub(r"\1", x["ex"]), NOTE.sub(r"\2", x["ex"]), x.get("exEn", "")]
        w = words.get(k)
        if not w:
            return [k, "", ""]
        cands = [z for r in w["readings"] for z in r["words"]]
        al = w.get("alone")
        if al:
            hit = next((z for z in cands if z[0] == al["w"]), None)
            if hit:
                return hit[:3]
        cands.sort(key=lambda z: (-z[3], abs(len(z[0]) - 2)))
        return cands[0][:3] if cands else [k, "", ""]
    def deps(k):
        out = set()
        for g, _ in K[k]["parts"]:
            for c in g:
                c = VARIANTS.get(c, c)
                if c in K and c != k:
                    out.add(c)
        return out
    base = load("study.json")
    def extend(order):
        done = set(order)
        out = list(order)
        for lv in (3, 2):
            todo = sorted([k for k in K if K[k]["l"] == lv], key=lambda k: (chap.get(k, 999), K[k]["n"]))
            while todo:
                for k in todo:
                    if all(d in done or K[d]["l"] < lv for d in deps(k)):
                        break
                else:
                    k = todo[0]
                todo.remove(k); out.append(k); done.add(k)
        return out
    SK = {k: {"m": x["m"], "on": x["on"], "kun": x["kun"], "l": x["l"], "parts": x["parts"],
              "story": x.get("story", ""), "traps": x.get("traps", []), "ex": example(k)} for k, x in K.items()}
    CHT = {k: (f"Chapter {i+1}: {c['title']}" if c["key"] != "other" else f"Chapter {i+1}: standalone shapes")
           for i, c in enumerate(CH) for k in c["kanji"]}
    FAM = {k: (c.get("glyph", "") if c["key"] != "other" else "") for c in CH for k in c["kanji"]}
    return {"K": SK, "CHT": CHT, "FAM": FAM, "order": extend(base["order"]), "order_n5": extend(base["order_n5"])}

print("Building:")
# ---------------------------------------------------------------- shared script
_common = (SRC / "common.js").read_text(encoding="utf-8").replace("__READINGS__", dump(readings))
write("assets/common.js", _common)
import hashlib as _h
COMMON_VERSION = _h.sha1(_common.encode("utf-8")).hexdigest()[:10]

# ---------------------------------------------------------------- master deck
def kanji_sentences(limit=3):
    """Up to three short sentences for each kanji, easiest first, from all the site's sentences."""
    LV = kanji["LV"]
    out = {}
    for r, text in sentence_records(include_phrases=False, include_grammar=True):
        ks = [c for c in text if "\u4e00" <= c <= "\u9fff"]
        lvl = min([LV.get(c, 1) for c in ks] or [5])
        for c in set(ks):
            if c in LV:
                out.setdefault(c, []).append((lvl, len(text), r))
    return {k: [dict(r, lv=lvl) for lvl, _, r in sorted(v, key=lambda x: (-x[0], x[1]))[:limit]] for k, v in out.items()}

write("kanji/master-kanji-shapes.html",
      fill("master.html", KANA_WORDS=KANA_WORDS, DATA=dump({"K": kanji["K"], "CH": kanji["CH"], "LV": kanji["LV"], "W": words, "P": kanji["P"], "S": kanji_sentences()})))

# ---------------------------------------------------------------- kanji by situation
sit = load("situation.json")
topics = sit["topics"]
for t in topics:
    t["sents"] = []
tix = {t["id"]: t for t in topics}
for sb_topic, sents in SB.items():
    tix[sit["sb_map"][sb_topic]]["sents"] += [{k: s[k] for k in ("kj", "kn", "rj", "en", "why", "roles", "enb")} for s in sents]
for topic, sents in EXTRA.items():
    tix[topic]["sents"] += [{"n": s["n"], "en": s["en"], "why": s["why"]} for s in sents]
K = {r["k"]: r for t in topics for g in t["groups"] for r in g["rows"]}
W = {k: words_for(k) for k in K if words_for(k)}
write("kanji/kanji-by-situation.html",
      fill("situation.html", KANA_WORDS=KANA_WORDS, DATA=dump({"T": topics, "K": K, "W": W, "LV": kanji["LV"], "apx": sit["apx"], "lede": sit["lede"]})))

# ---------------------------------------------------------------- phrasebook
chapters = load("phrasebook.json")
for c in chapters:
    for sec in c["phr"]:                       # hand-marked blocks → roles per token and coloured English
        lines = sec["items"].strip().split("\n")
        sec["marks"] = {i: mark({"n": lines[int(i)].split("|")[0], "en": lines[int(i)].split("|")[1], **m})
                        for i, m in sec.get("marks", {}).items()}
        for m in sec["marks"].values():
            m.pop("n", None); m.pop("en", None)
for c in chapters:
    c["sents"] = [s for t in c.pop("sb") for s in SB.get(t, [])] + [s for t in c.pop("extra") for s in EXTRA.get(t, [])]
    c.pop("_count_check", None)
write("words/phrasebook.html", fill("phrasebook.html", DATA=dump(chapters), KANJI_SET=KANJI_SET, KANA_WORDS=KANA_WORDS))

# ---------------------------------------------------------------- sentence builder
def builder_sections():
    """One set of topics: the builder's own sentences first in each, then every other marked sentence."""
    LV, NOTE = kanji["LV"], NOTE_RE
    def level(text):
        ks = [c for c in text if "\u4e00" <= c <= "\u9fff"]
        return min([LV.get(c, 2) for c in ks] or [5])
    sit = load("situation.json")
    topics = {t["id"]: {"id": t["id"], "title": t["en"], "jp": t["jp"], "blurb": t["blurb"], "sents": []} for t in sit["topics"]}
    order = [t["id"] for t in sit["topics"]]
    for t in load("sentences-builder.json"):                 # the 120 core sentences, in their topic's slot
        tid = sit["sb_map"].get(t["id"], t["id"])
        for s in t["sents"]:
            s = dict(s); s["enb"] = english_blocks(" ".join(x[1] for x in s["enc"]), s["enc"]); s.pop("enc")
            s["lv"] = level("".join(s["kj"])); s["core"] = True
            topics[tid]["sents"].append(s)
    for s in extra:                                           # everything else, in the same topics
        r = mark({k: v for k, v in s.items() if k in ("n", "en", "why", "jr", "er")})
        r["lv"] = level(NOTE.sub(r"\1", s["n"]))
        topics.setdefault(s["topic"], {"id": s["topic"], "title": "More sentences", "jp": "", "blurb": "", "sents": []})["sents"].append(r)
    for t in topics.values():                                 # core sentences first, then the rest
        t["sents"].sort(key=lambda s: (not s.get("core"), -s["lv"]))
    return [topics[i] for i in order if topics[i]["sents"]] + [t for i, t in topics.items() if i not in order and t["sents"]]

write("words/sentence-builder.html", fill("sentence-builder.html", KANJI_SET=KANJI_SET, KANA_WORDS=KANA_WORDS, DATA=dump(builder_sections())))

# ---------------------------------------------------------------- study plan
write("kanji/learn-n5-n4.html", fill("study.html", DATA=dump(study_data())))

# ---------------------------------------------------------------- kana
write("kana/kana-sounds.html", fill("kana-sounds.html", KANJI_SET=KANJI_SET))
write("kana/kana-words.html", fill("kana-words.html", DATA=dump(kana_words("kana-words.json")), KANJI_SET=KANJI_SET, KANA_WORDS=KANA_WORDS,
      TITLE="Kana words: the Japanese you write without kanji", H1="かなの言葉", STORE="kana-words", FROM="kw",
      INTRO="The words you'll write in hiragana, not kanji: greetings, question words, pointing words, the little words that link sentences, adverbs, sound words, and everyday nouns and verbs. About 425 words from N5 to N2, grouped by what you use them for, each with a real example sentence where there is one. For loanwords, see <a href=\"katakana-words.html\">katakana words</a>."))
write("kana/katakana-words.html", fill("kana-words.html", DATA=dump(kana_words("katakana-words.json")), KANJI_SET=KANJI_SET, KANA_WORDS=KANA_WORDS,
      TITLE="Katakana words: loanwords by topic", H1="カタカナの言葉", STORE="katakana-words", FROM="kt",
      INTRO="340 loanwords from N5 to N2, grouped by topic, from コーヒー to パスポート. Red notes flag the ones that don't mean what English speakers expect (マンション, コンセント, スマート) and the ones borrowed from other languages (パン, アルバイト). Each has a real example sentence where there is one. For words written in hiragana, see <a href=\"kana-words.html\">kana words</a>."))
# ---------------------------------------------------------------- grammar
_grammar = load("grammar.json")
for _g in _grammar:
    _g["ex"] = [mark(e) for e in _g["ex"]]
write("words/grammar.html", fill("grammar.html", DATA=dump(_grammar), KANJI_SET=KANJI_SET, KANA_WORDS=KANA_WORDS))

# ---------------------------------------------------------------- offline support
import hashlib
files = ["index.html", "manifest.webmanifest", "assets/icons/icon-192.png", "assets/icons/icon-512.png", "assets/icons/icon-180.png"] + WRITTEN
digest = hashlib.sha1()
for f in files:
    digest.update((ROOT / f).read_bytes())
sw = (SRC / "sw.js").read_text(encoding="utf-8").replace("__VERSION__", digest.hexdigest()[:10]).replace("__FILES__", dump(["./" + f for f in files]))
(ROOT / "sw.js").write_text(sw, encoding="utf-8")
print("  sw.js")
print("Done.")
