#!/usr/bin/env python3
"""List every sentence where a hand-marked block boundary falls inside a token.
Those tokens take a single colour, so part of the sentence is coloured wrongly.
Run from the repo root: python3 build/straddle.py
"""
import re, sys
from audit import walk, plain

NOTE_RE = re.compile(r"([一-鿿々]+)\{[^}]*\}")


def main():
    n = 0
    for src, sid, _, _, _, _, s in walk():
        jr = s.get("jr")
        if not jr or not s.get("n"):
            continue
        toks = [NOTE_RE.sub(r"\1", t) for t in s["n"].split(" ")]
        bounds, pos = [], 0
        for r, t in jr:
            t = t.replace(" ", "")
            bounds.append((pos, pos + len(t), r)); pos += len(t)
        pos = 0
        for t in toks:
            inside = {r for a, z, r in bounds if a < pos + len(t) and z > pos}
            if len(inside) > 1:
                n += 1
                print(f"{src} [{sid}] {' '.join(toks)}")
                print(f"    token {t!r} spans {sorted(inside)}   n={s['n']!r}")
            pos += len(t)
    print(f"\n{n} straddling tokens")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
