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
    if rel.endswith(".html") and 'id="search"' in text and "search-index.js" not in text:
        depth = "../" * rel.count("/")
        text = text.replace('<script src="' + depth + 'assets/common.js', '<script src="' + depth + 'assets/search-index.js"></script>\n<script src="' + depth + 'assets/common.js', 1)
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
words_data = words
readings = load("readings.json")      # reading dictionary for the on/kun engine
extra = load("sentences-extra.json")  # sentences written for the situation page
for _lv in (5, 4, 3, 2):                  # sentences written to cover words and kanji, level by level
    if (DATA / f"sentences-n{_lv}.json").exists():
        extra += load(f"sentences-n{_lv}.json")
natural_en = load("sentence-builder-english.json")
KANJI_SET = dump("".join(kanji["K"].keys()))

I_ROW = "いきしちにひみりぎじびぴ"
E_ROW = "えけせてねへめれげぜべぺ"

GODAN = {"う": ("い", "わ", "っ"), "く": ("き", "か", "い"), "ぐ": ("ぎ", "が", "い"), "す": ("し", "さ", "し"), "つ": ("ち", "た", "っ"),
         "ぬ": ("に", "な", "ん"), "ぶ": ("び", "ば", "ん"), "む": ("み", "ま", "ん"), "る": ("り", "ら", "っ")}
END = r"(?![\u3041-\u309f])|(?=[はがをにでへともかやねよの][^\u3041-\u309f]|です|でした|ので|のに|と)"

GODAN_RU = {"かじる", "ちぎる", "しゃべる", "かえる", "はいる", "しる", "きる", "はしる", "へる", "すべる", "ける", "にぎる"}   # look like る-verbs but aren't
HONORIFIC_I = {"いらっしゃる", "なさる", "くださる", "おっしゃる"}   # ます-stem in い: いらっしゃいます

def word_forms(key, group):
    """The written forms of a kana verb or adjective, so conjugated words link to the dictionary word."""
    if key.endswith("する"):
        s = key[:-2]
        tails = ("する", "します", "しました", "しません", "しませんでした", "しましょう", "して", "した", "しない", "しなかった",
                 "しよう", "すれば", "させ", "される", "できる", "できます", "しづらい", "しやすい", "しにくい", "しながら", "せず")
        return [s + x for x in tails]
    if group == "verb" and key[-1] in GODAN:
        if key[-1] == "る" and len(key) >= 2 and key[-2] in I_ROW + E_ROW and key not in GODAN_RU:   # る-verb
            s = key[:-1]
            tails = ("る", "ます", "ました", "ません", "ませんでした", "ましょう", "て", "た", "ない", "なかった", "なくて",
                     "られる", "られます", "させる", "よう", "れば", "たい", "たく", "ながら", "なさい", "ず", "やすい", "にくい", "すぎ")
            return [s + x for x in tails]
        i, a, t = GODAN[key[-1]]
        if key in HONORIFIC_I:
            i = "い"
        e = E_ROW[I_ROW.index(i)] if i in I_ROW else ""
        o = {"い": "お", "き": "こ", "ぎ": "ご", "し": "そ", "ち": "と", "に": "の", "び": "ぼ", "み": "も", "り": "ろ"}.get(i, "")
        s, voiced = key[:-1], key[-1] in "ぐぬぶむ"
        te, ta = ("で", "だ") if voiced else ("て", "た")
        tails = [key, i + "ます", i + "ました", i + "ません", i + "ませんでした", i + "ましょう", i + "たい", i + "たく",
                 i + "ながら", i + "なさい", i + "やすい", i + "にくい", i + "すぎ", t + te, t + ta,
                 a + "ない", a + "なかった", a + "なくて", a + "れる", a + "せる", a + "ず"]
        if e:
            tails += [e + "ば", e + "る", e + "ます", e + "ません"]
        if o:
            tails += [o + "う"]
        return [s + x for x in tails]
    if group == "desc" and key.endswith("い") and len(key) >= 3:        # い-adjective
        s = key[:-1]
        return [key] + [s + x for x in ("く", "くない", "くなかった", "かった", "くて", "ければ", "さ", "そう", "すぎ")]
    return [key]

def kana_word_map():
    """Every written form that should link to a kana word card: {form: [h|k, the word's own spelling]}."""
    out = {}
    for name, tag in (("kana-words.json", "h"), ("katakana-words.json", "k")):
        for w in load(name)["words"]:
            if w.get("g") == "parts":
                continue
            key = w["w"].strip("～〜")
            if "～" in key or "〜" in key:
                continue
            key = key[:-2] if key.endswith("する") and tag == "k" else key
            if len(key) < 2:
                continue
            out.setdefault(key, [tag, key])
            for form in word_forms(key, w.get("g", "")):
                if len(form) >= 2:
                    out.setdefault(form, [tag, key])
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
    """The 120 core sentences, from data/sentences-builder.json, grouped by their topic."""
    out = {}
    for t in load("sentences-builder.json"):
        for i, s in enumerate(t["sents"]):
            s = dict(s)
            enc = s.pop("enc")
            s["id"] = f"s{t['id']}-{i}"
            s["en"] = natural_en.get(f"{t['id']}-{i}") or " ".join(x[1] for x in enc)
            s["enb"] = english_blocks(s["en"], enc)
            out.setdefault(t["id"], []).append(s)
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

KANA_ROWS = [("あ", "あいうえお"), ("か", "かきくけこがぎぐげご"), ("さ", "さしすせそざじずぜぞ"), ("た", "たちつてとだぢづでど"),
              ("な", "なにぬねの"), ("は", "はひふへほばびぶべぼぱぴぷぺぽ"), ("ま", "まみむめも"), ("や", "やゆよ"),
              ("ら", "らりるれろ"), ("わ", "わをん")]
ADVERB_EN = re.compile(r"\b(\w+ly)\b|^(very|quite|almost|always|often|sometimes|soon|already|still|again|about|roughly|at all|a little|completely|suddenly|gradually)\b", re.I)

def word_pos(word, kana, en, group=""):
    """Part of speech, worked out from the word and its English. Imperfect, but good enough to group by."""
    if word.endswith("する") or word.endswith("する"):
        return "suru"
    if en.lower().startswith("to "):
        return "verb"
    if group in ("time", "degree", "manner", "sound"):
        return "adverb"
    if group in ("desc",):
        return "adj-i" if word.endswith("い") else "adj-na"
    if word.endswith("い") and kana.endswith("い") and len(kana) >= 3 and not en.lower().startswith(("a ", "the ")):
        return "adj-i"
    if ADVERB_EN.search(en):
        return "adverb"
    if group in ("greet", "inter", "expr", "link", "question", "point", "parts"):
        return "phrase"
    return "noun"

def vocabulary():
    """Every word the site knows: the kanji words from the kanji cards, plus the kana word pages."""
    words = {}
    for k, w in words_data.items():
        for r in w["readings"]:
            for z in r["words"]:
                words.setdefault(z[0], {"w": z[0], "r": z[1], "en": z[2], "l": z[3], "kana": False})
        for z in (w.get("sp") or []):
            words.setdefault(z[0], {"w": z[0], "r": z[1], "en": z[2], "l": z[3] if len(z) > 3 else 2, "kana": False})
    for name, tag in (("kana-words.json", "kw"), ("katakana-words.json", "kt")):
        for z in load(name)["words"]:
            key = z["w"].strip("～〜")
            if "～" in z["w"] or "〜" in z["w"] or len(key) < 1:
                continue
            words.setdefault(key, {"w": key, "r": key, "en": z["en"], "l": z["l"], "kana": tag, "g": z.get("g", "")})
    corpus = sentence_records()
    allkeys = list(words)
    for v in words.values():
        v["pos"] = word_pos(v["w"], v["r"], v["en"], v.get("g", ""))
        v.pop("g", None)
        v["row"] = next((row for row, chars in KANA_ROWS if v["r"] and rdhira(v["r"])[0] in chars), "わ")
        pat = word_pattern(v["w"], {"verb": "verb", "adj-i": "desc"}.get(v["pos"], ""))
        hits = [(r, t) for r, t in corpus if pat.search(t)]
        if hits:
            v["ex"] = min(hits, key=lambda h: len(h[1].replace(" ", "")))[0]
    order = {r: i for i, (r, _) in enumerate(KANA_ROWS)}
    return sorted(words.values(), key=lambda v: (-v["l"], order.get(v["row"], 9), v["r"]))

def rdhira(s):
    return re.sub(r"[\u30a1-\u30f6]", lambda m: chr(ord(m.group()) - 0x60), s)

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
    VOC = [[v["w"], v["r"], v["en"], v["l"]] for v in vocabulary()]
    return {"K": SK, "CHT": CHT, "FAM": FAM, "VOC": VOC, "order": extend(base["order"]), "order_n5": extend(base["order_n5"])}


print("Building:")
# ---------------------------------------------------------------- shared script
def search_index():
    """A compact index of every page's entries, so a search on one page can point at the others."""
    key = lambda *parts: re.sub(r"[\u30a1-\u30f6]", lambda m: chr(ord(m.group()) - 0x60), " ".join(str(p) for p in parts if p)).lower()
    out = []
    for name, page in (("kana-words.json", "kw"), ("katakana-words.json", "kt")):
        for w in load(name)["words"]:
            if w.get("g") == "parts":
                continue
            out.append([key(w["w"], krRomaji(w["w"]), w["en"], w.get("note", "")), page, w["w"], w["w"]])
    for k, x in kanji["K"].items():
        out.append([key(k, x["m"], " ".join(x.get("on", []) + x.get("kun", [])), krRomaji(" ".join(x.get("on", []) + x.get("kun", [])))), "km", k, k + " " + x["m"].split(",")[0]])
    for g in load("grammar.json"):
        out.append([key(NOTE_RE.sub(r"\1", g["pat"]), g["mean"], g["group"]), "gr", g["id"], NOTE_RE.sub(r"\1", g["pat"])])
    for v in vocabulary():
        if v["kana"]:
            continue                                   # the kana pages already carry these
        out.append([key(v["w"], v["r"], v["en"]), "vo", v["w"], v["w"]])
    return out

def krRomaji(kana):
    """Rough Hepburn, only for the search index."""
    BASE = {"あ":"a","い":"i","う":"u","え":"e","お":"o","か":"ka","き":"ki","く":"ku","け":"ke","こ":"ko","さ":"sa","し":"shi","す":"su","せ":"se","そ":"so",
            "た":"ta","ち":"chi","つ":"tsu","て":"te","と":"to","な":"na","に":"ni","ぬ":"nu","ね":"ne","の":"no","は":"ha","ひ":"hi","ふ":"fu","へ":"he","ほ":"ho",
            "ま":"ma","み":"mi","む":"mu","め":"me","も":"mo","や":"ya","ゆ":"yu","よ":"yo","ら":"ra","り":"ri","る":"ru","れ":"re","ろ":"ro","わ":"wa","を":"o","ん":"n",
            "が":"ga","ぎ":"gi","ぐ":"gu","げ":"ge","ご":"go","ざ":"za","じ":"ji","ず":"zu","ぜ":"ze","ぞ":"zo","だ":"da","ぢ":"ji","づ":"zu","で":"de","ど":"do",
            "ば":"ba","び":"bi","ぶ":"bu","べ":"be","ぼ":"bo","ぱ":"pa","ぴ":"pi","ぷ":"pu","ぺ":"pe","ぽ":"po"}
    hira = re.sub(r"[\u30a1-\u30f6]", lambda m: chr(ord(m.group()) - 0x60), kana)
    out, prev = [], ""
    for ch in hira:
        if ch in "ゃゅょ" and out:
            out[-1] = out[-1][:-1] + {"ゃ":"ya","ゅ":"yu","ょ":"yo"}[ch] if out[-1].endswith("i") else out[-1]
        elif ch == "ー" and out and out[-1]:
            out.append(out[-1][-1])
        elif ch == "っ":
            prev = "x"
        else:
            out.append(BASE.get(ch, ""))
    return "".join(out)

_common = (SRC / "common.js").read_text(encoding="utf-8").replace("__READINGS__", dump(readings))
write("assets/common.js", _common)
write("assets/search-index.js", "// Where every word, kanji and pattern lives, for the cross-page search hints.\nconst JP_SEARCH_INDEX=" + dump(search_index()) + ";\n")
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
      fill("situation.html", KANA_WORDS=KANA_WORDS, DATA=dump({"T": topics, "K": K, "W": W, "LV": kanji["LV"], "apx": sit["apx"], "lede": sit["lede"],
                 "VK": "".join(sorted({c for v in vocabulary() for c in v["w"] if "\u4e00" <= c <= "\u9fff"}))})))

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
write("kanji/learn.html", fill("study.html", DATA=dump(study_data())))
write("kanji/learn-n5-n4.html", '<!DOCTYPE html><meta charset="utf-8"><title>Moved</title>'
      '<meta http-equiv="refresh" content="0; url=learn.html">'
      '<p>The daily study plan now covers N5 to N2 and lives at <a href="learn.html">learn.html</a>.</p>')

# ---------------------------------------------------------------- kana
_vocab = vocabulary()
write("words/vocabulary.html", fill("vocabulary.html", DATA=dump(_vocab), KANJI_SET=KANJI_SET, KANA_WORDS=KANA_WORDS,
      COUNT=f"{len(_vocab):,}"))
write("kana/kana-sounds.html", fill("kana-sounds.html", KANJI_SET=KANJI_SET))
write("kana/kana-words.html", fill("kana-words.html", DATA=dump(kana_words("kana-words.json")), KANJI_SET=KANJI_SET, KANA_WORDS=KANA_WORDS,
      TITLE="Kana words: the Japanese you write without kanji", H1="かなの言葉", STORE="kana-words", FROM="kw",
      INTRO="The words you'll write in hiragana, not kanji: greetings, question words, pointing words, the little words that link sentences, adverbs, sound words, and everyday nouns and verbs. 454 words from N5 to N2, grouped by what you use them for, each with a real example sentence where there is one. For loanwords, see <a href=\"katakana-words.html\">katakana words</a>."))
write("kana/katakana-words.html", fill("kana-words.html", DATA=dump(kana_words("katakana-words.json")), KANJI_SET=KANJI_SET, KANA_WORDS=KANA_WORDS,
      TITLE="Katakana words: loanwords by topic", H1="カタカナの言葉", STORE="katakana-words", FROM="kt",
      INTRO="353 loanwords from N5 to N2, grouped by topic, from コーヒー to パスポート. Red notes flag the ones that don't mean what English speakers expect (マンション, コンセント, スマート) and the ones borrowed from other languages (パン, アルバイト). Each has a real example sentence where there is one. For words written in hiragana, see <a href=\"kana-words.html\">kana words</a>."))
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
