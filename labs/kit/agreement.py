"""Lab 1.3: how far two raters agree on the 20 assets.

    uv run kit/agreement.py files/reconcile/peer_a.xlsx files/reconcile/peer_b.xlsx
    uv run kit/agreement.py my_ratings.xlsx my_peers_ratings.xlsx

Prints the share of assets with the same level, Cohen's kappa (agreement beyond what two raters
with the same level frequencies would reach by chance) and every disagreement to reconcile.
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as K  # noqa: E402


def kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[c] * cb[c] for c in set(a) | set(b)) / (n * n)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: uv run kit/agreement.py <rater A.xlsx> <rater B.xlsx>")
        return 2
    ra = {r["asset_id"]: r for r in K.read_sheet(Path(sys.argv[1]), "assets")}
    rb = {r["asset_id"]: r for r in K.read_sheet(Path(sys.argv[2]), "assets")}
    ids = sorted(set(ra) & set(rb))
    a = [ra[i].get("level", "") for i in ids]
    b = [rb[i].get("level", "") for i in ids]
    same = sum(x == y for x, y in zip(a, b))
    print(f"Assets rated by both: {len(ids)}")
    print(f"اتفاق على المستوى: {same} من {len(ids)} ({100 * same / len(ids):.0f}%)")
    print(f"كابا كوهين: {kappa(a, b):.2f}")
    ia = [ra[i].get("impact_level", "") for i in ids]
    ib = [rb[i].get("impact_level", "") for i in ids]
    print(f"اتفاق على مستوى الأثر: {sum(x == y for x, y in zip(ia, ib))} من {len(ids)}")
    print("\nالخلافات (انقلها إلى ورقة disagreements):")
    for i, x, y in zip(ids, a, b):
        if x != y:
            print(f"  {i}  {ra[i].get('asset_name', '')}: {x} / {y}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
