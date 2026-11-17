#!/usr/bin/env python3
"""Walk every hand-marked sentence in data/ and report colour-block mismatches.

A sentence is well marked when the set of roles on the Japanese side equals the set
on the English side: the same blocks, in whatever order each language wants them.
Run from the repo root: python3 build/audit.py [--list]
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTE_RE = re.compile(r"([一-鿿々]+)\{[^}]*\}")


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def plain(n):
    return NOTE_RE.sub(r"\1", n).replace(" ", "")


def walk():
    """Yield (source, id, jp-text, english, jp-roles, en-roles, raw) for every marked sentence."""
    def jrer(s):
        return ({r for r, _ in s.get("jr", []) if r}, {r for r, _ in s.get("er", []) if r})

    for f in ("sentences-n5.json", "sentences-n4.json", "sentences-n3.json",
              "sentences-n2.json", "sentences-extra.json"):
        for s in load(f):
            jp, en = jrer(s)
            yield f, s.get("id", "?"), plain(s["n"]), s["en"], jp, en, s

    for sec in load("grammar.json"):
        for i, s in enumerate(sec.get("ex", [])):
            jp, en = jrer(s)
            yield "grammar.json", f"{sec['id']}#{i}", plain(s["n"]), s["en"], jp, en, s

    for fr in load("patterns.json")["frames"]:
        for tag, lst in (("ex", [fr["ex"]] if fr.get("ex") else []), ("q", fr.get("q") or [])):
            for i, s in enumerate(lst):
                jp, en = jrer(s)
                yield "patterns.json", f"{fr['id']}.{tag}{i}", plain(s["n"]), s["en"], jp, en, s

    pt = load("particles.json")
    for slot in pt.get("slots", []):
        for m in slot.get("markers", []):
            s = m.get("ex")
            if s:
                jp, en = jrer(s)
                yield "particles.json", f"{slot['role']}-{m['p']}", plain(s["n"]), s["en"], jp, en, s
    for ov in pt.get("overlays", []):
        s = ov.get("ex")
        if s:
            jp, en = jrer(s)
            yield "particles.json", f"ov-{ov['p']}", plain(s["n"]), s["en"], jp, en, s

    for t in load("sentences-builder.json"):
        for i, s in enumerate(t["sents"]):
            jp = {r for r in s.get("roles", []) if r}
            en = {r for r, _ in s.get("enc", []) if r}
            yield ("sentences-builder.json", f"{t['id']}-{i}",
                   "".join(s["kj"]), " ".join(x[1] for x in s["enc"]), jp, en, s)


def main():
    show_all = "--list" in sys.argv
    bad, total, concat = [], 0, []
    for src, sid, n, en, jp, enr, s in walk():
        total += 1
        if show_all:
            print(f"{src}\t{sid}\t{n}\t{en}")
            continue
        if jp != enr:
            bad.append((src, sid, n, en, jp, enr))
        if s.get("jr"):
            marked = "".join(t for _, t in s["jr"]).replace(" ", "")
            if marked != plain(s["n"]):
                concat.append((src, sid, n, marked))
    if show_all:
        return 0

    by_src = {}
    for src, sid, n, en, jp, enr in bad:
        by_src.setdefault(src, []).append((sid, n, en, jp, enr))

    print(f"{total} marked sentences, {len(bad)} role-set mismatches, {len(concat)} concat errors\n")
    for src in sorted(by_src):
        print(f"--- {src}: {len(by_src[src])}")
        for sid, n, en, jp, enr in by_src[src]:
            print(f"  [{sid}] {n}")
            print(f"        {en}")
            print(f"        only-JP {sorted(jp - enr)}  only-EN {sorted(enr - jp)}")
    for src, sid, n, marked in concat:
        print(f"CONCAT {src} [{sid}] {n} != {marked}")
    return 1 if bad or concat else 0


if __name__ == "__main__":
    sys.exit(main())
