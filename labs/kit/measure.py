"""Lab 2.2: how often Maysam misses and raises false alarms, against the owners' decisions.

    uv run kit/measure.py                              # Maysam with rules_v1.json
    uv run kit/measure.py files/maysam/rules_v2.json   # after you change the rules (stretch)

Definitions (the same in the slides and the questions). For the items whose reference level is L:
  miss rate at L        = items Maysam put LOWER than L  / items at L   (under-classification)
  false-alarm rate at L = items Maysam put HIGHER than L / items at L   (over-classification)
So there is no miss at Public and no false alarm at Top Secret.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as K  # noqa: E402
import maysam as M  # noqa: E402


def pct(a: int, b: int) -> str:
    return "-" if b == 0 else f"{100 * a / b:.1f}%"


def rates(labels: list[dict]) -> dict:
    out = {}
    for i, lv in enumerate(K.LEVELS):
        rows = [x for x in labels if x["reference_level"] == lv]
        lower = sum(1 for x in rows if K.LEVELS.index(x["maysam_level"]) < i)
        higher = sum(1 for x in rows if K.LEVELS.index(x["maysam_level"]) > i)
        out[lv] = {"n": len(rows), "miss": lower, "false_alarm": higher, "exact": len(rows) - lower - higher}
    return out


def table(labels: list[dict], title: str) -> None:
    r = rates(labels)
    print(title)
    print(f"  {'المستوى المرجعي':16} {'العدد':>6} {'الإغفال':>14} {'الإنذار الكاذب':>16}")
    for lv in K.LEVELS:
        x = r[lv]
        print(f"  {lv:16} {x['n']:>6} {x['miss']:>4} ({pct(x['miss'], x['n']):>6}) {x['false_alarm']:>5} ({pct(x['false_alarm'], x['n']):>6})")
    n = len(labels)
    exact = sum(v["exact"] for v in r.values())
    print(f"  التطابق التام: {exact} من {n} ({pct(exact, n)})")


def main() -> int:
    rules_path = K.arg_path(M.RULES)
    labels = M.run(M.load_items(), M.load_rules(rules_path))
    print(f"Maysam on {len(labels)} items, rules: {rules_path.name}\n")
    table(labels, "1 · كل العناصر")
    for lang, name in (("ar", "العربية"), ("en", "الإنجليزية"), ("mixed", "المختلطة")):
        print()
        table([x for x in labels if x["language"] == lang], f"2 · العناصر {name}")
    print("\n3 · الإغفالات بحسب المرحلة التي قررت")
    for st in ("pattern", "keyword", "model"):
        rows = [x for x in labels if x["stage"] == st]
        miss = sum(1 for x in rows if K.LEVELS.index(x["maysam_level"]) < K.LEVELS.index(x["reference_level"]))
        print(f"  {st:8} قررت {len(rows):>3} عنصرًا، أغفلت منها {miss}")
    top = [x["item_id"] for x in labels if K.LEVELS.index(x["reference_level"]) >= 2 and x["maysam_level"] == "عام"]
    print(f"\n4 · عناصر مرجعها سري أو سري للغاية ووسمتها الآلة «عام»: {len(top)}")
    # what the two rule stages catch with and without Arabic normalisation (both run for real)
    rules = M.load_rules(rules_path)
    plain, norm = dict(rules, normalise_arabic=False), dict(rules, normalise_arabic=True)
    print("\n5 · ما تلتقطه القواعد قبل توحيد الكتابة العربية وبعده (أرقام عربية هندية، همزات، تاء مربوطة، مسافات داخل الأرقام)")
    for lang in ("ar", "en", "mixed"):
        rows = [it for it in M.load_items() if it["language"] == lang]
        a = sum(1 for it in rows if M.label(it["content"], plain)[0])
        b = sum(1 for it in rows if M.label(it["content"], norm)[0])
        print(f"  {lang:6} {len(rows):>4} عنصرًا: تلتقط القواعد {a} دون توحيد، و{b} بعده")
    return 0


if __name__ == "__main__":
    sys.exit(main())
