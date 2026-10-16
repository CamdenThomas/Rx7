"""link.py - add home rows to a page's `rows` (the merge, D-574).

    python3 02-PROJECTS/00-library/tools/link.py DOC-048.027 specs:SP-1830 procedure_steps:PR-031.16

Adds each token once, keeps the list sorted, and leaves everything else on the page alone.
A token is table:key (00-CAR) or area:table:key; `rx7.py check` refuses one naming no row.
Takes rx7.py's write lock, so any number of merge agents can run it at once.

Owns: 00-CAR pages.rows (adds only).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import rx7  # noqa: E402


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 3
    pid, toks = argv[0], argv[1:]
    rx7.take_write_lock()
    car = ROOT / "00-CAR"
    hdr, rows = rx7.read_table(car, "pages")
    hit = next((r for r in rows if r["id"] == pid), None)
    if hit is None:
        print(f"no page {pid}")
        return 3
    have = set((hit.get("rows") or "").split())
    add = [t for t in toks if t not in have]
    if not add:
        print(f"{pid}: already linked")
        return 0
    hit["rows"] = " ".join(sorted(have | set(add)))
    rx7.write_table(car, "pages", hdr, rows)
    print(f"{pid}: + {' '.join(add)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
