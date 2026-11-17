#!/usr/bin/env python3
"""One line per sentence: id, the Japanese with its blocks, the English with its blocks.
Usage: python3 build/dump.py [file-substring] [start] [count]
"""
import sys
from audit import walk, plain

def fmt(pairs):
    return " ".join(f"[{r or '-'}]{t.strip()}" for r, t in pairs)

def main():
    want = sys.argv[1] if len(sys.argv) > 1 else ""
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9
    rows = []
    for src, sid, n, en, jp, enr, s in walk():
        if want and want not in src:
            continue
        jr = s.get("jr") or [[r, c] for r, c in zip(s.get("roles", []), s.get("kj", []))]
        er = s.get("er") or s.get("enc") or []
        rows.append(f"{sid} | {fmt(jr) if jr else n} | {fmt(er) if er else en}")
    print(f"# {want or 'all'}: {len(rows)} rows, showing {start}..{start+count}")
    for r in rows[start:start + count]:
        print(r)

if __name__ == "__main__":
    main()
