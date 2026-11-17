#!/usr/bin/env python3
"""Sharper checks on the hand-marked blocks than plain set equality.

  verbatim  an English phrase that isn't in the English sentence (the build then
            falls back to colouring loose words, which scatters the colours)
  gap       a run of uncoloured English words
  particle  a Japanese block whose role disagrees with the particle it ends in
  shape     an English phrase whose shape disagrees with its role
"""
import json, re, sys
from audit import walk, plain, load

TIME = re.compile(r"(時|分|秒|日|月|年|週|朝|昼|夜|晩|今|昨|明日|毎|曜|後|前|頃|ごろ|間|中|とき|時々|すぐ|最近|将来|以来|うち)")
TIME_EN = re.compile(r"\b(yesterday|today|tomorrow|tonight|now|then|soon|later|morning|afternoon|evening|night|week|month|year|day|days|hour|minute|o'clock|am|pm|spring|summer|autumn|winter|monday|tuesday|wednesday|thursday|friday|saturday|sunday|january|february|march|april|may|june|july|august|september|october|november|december|every|always|usually|often|sometimes|never|while|when|before|after|during|since|until|ago|recently|lately|already|still|yet|last|next|this|these|at|in|on|by|from|for|a|the|whole|past|future|early|late|first|time|times|end|beginning|holiday|holidays|weekend|season|moment|once|twice|daily|weekly|monthly|yearly|overnight|midnight|noon)\b", re.I)
PLACE_EN = re.compile(r"\b(in|at|to|from|into|onto|on|out|outside|inside|up|down|through|across|toward|towards|here|there|where|home|back|over|around|near|beside|behind|under|above|along|past|via|abroad|upstairs|downstairs)\b", re.I)
VERB_EN = re.compile(r"\b(is|are|was|were|be|been|am|'s|'re|'m|do|does|did|don't|doesn't|didn't|have|has|had|haven't|hasn't|hadn't|can|can't|could|couldn't|will|won't|would|wouldn't|should|shouldn't|may|might|must|mustn't|let|let's|please|there's|isn't|aren't|wasn't|weren't|not|no|never|get|got|go|went|gone|come|came|'ll|'ve|'d|want|wants|wanted|like|likes|liked|seems|seem|looks|look|it)\b", re.I)
JP_VERB_END = re.compile(r"(ます|ました|ません|ませんでした|です|でした|だ|る|た|て|で|ない|なかった|う|く|ぐ|す|つ|ぬ|ぶ|む|い|よ|ね|か|ください|しよう|たい|かった|そう|ちゃ|じゃ|ろ|え|せ|め|べ|げ|つ|ぜ)$")
ENDER = re.compile(r"[かねよ]$")


def words(t):
    return re.findall(r"[A-Za-z']+", t)


def check(src, sid, n, en, jp, enr, s):
    out = []
    jr, er = s.get("jr") or [], s.get("er") or s.get("enc") or []

    # --- English phrases must be present verbatim, or the colours scatter
    low, mask = en.lower(), [""] * len(en)
    for r, t in er:
        t2 = t.strip().lower()
        if not t2:
            continue
        k, placed = 0, False
        while True:
            k = low.find(t2, k)
            if k < 0:
                break
            if all(m == "" for m in mask[k:k + len(t2)]):
                for q in range(k, k + len(t2)):
                    mask[q] = r
                placed = True
                break
            k += 1
        if not placed:
            out.append(("verbatim", f"{r!r} phrase {t!r} not found in {en!r}"))

    # --- uncoloured runs of real words
    gap = "".join((c if m == "" else " ") for c, m in zip(en, mask))
    for g in re.findall(r"[A-Za-z'][A-Za-z' ]*", gap):
        if len(g.strip()) > 1:
            out.append(("gap", f"uncoloured {g.strip()!r} in {en!r}"))

    # --- Japanese block vs the particle it ends in
    for r, t in jr:
        t = t.strip()
        if not t:
            continue
        if t.endswith("を") and r != "O":
            out.append(("particle", f"{t} ends in を but is {r}"))
        if ENDER.search(t) and len(t) == 1 and r != "Q":
            out.append(("particle", f"{t} is a sentence ender but is {r}"))
        if r == "T" and not TIME.search(t):
            out.append(("particle", f"{t} is T but has no time word"))
        if r == "Q" and not ENDER.search(t):
            out.append(("particle", f"{t} is Q but doesn't end か/ね/よ"))
        if r == "P" and not re.search(r"(で|に|へ|から|まで)$", t):
            out.append(("particle", f"{t} is P but ends in no place particle"))

    # --- English phrase shape vs its role
    for r, t in er:
        w = words(t)
        if not w:
            continue
        if r == "T" and not TIME_EN.search(t):
            out.append(("shape", f"T phrase {t!r} doesn't look like a time"))
        if r == "P" and not PLACE_EN.search(t):
            out.append(("shape", f"P phrase {t!r} doesn't look like a place"))
    return out


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    counts, rows = {}, []
    for src, sid, n, en, jp, enr, s in walk():
        for kind, msg in check(src, sid, n, en, jp, enr, s):
            if only and kind != only:
                continue
            counts[kind] = counts.get(kind, 0) + 1
            rows.append((kind, src, sid, n, en, msg))
    print("counts:", counts, f"over {len(rows)} findings\n")
    for kind, src, sid, n, en, msg in rows:
        print(f"[{kind}] {src} {sid}  {n} / {en}\n     {msg}")


if __name__ == "__main__":
    main()
