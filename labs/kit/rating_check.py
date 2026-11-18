"""Lab 1.2: check the ratings and levels of the 20 assets.

    uv run kit/rating_check.py files/rating/assets_20.xlsx

A match is the same impact level and the same classification level as the reference (one asset
accepts a second level, with its impact). PASS needs at least 16 matches, every row complete and
consistent with the policy's steps, and no asset of the two highest levels rated Public.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as K  # noqa: E402

NEED = 16


def expected_level(impact: str, law: str, benefit: str) -> str:
    i = K.IMPACTS.index(impact)
    if i == 3:
        return "سري للغاية"
    if i == 2:
        return "سري"
    if i == 0:
        return "عام"
    if law == "نعم":
        return "مقيد"
    if law == "لا" and benefit in ("نعم", "لا"):
        return "عام" if benefit == "نعم" else "مقيد"
    return ""


def check_rows(rows: list[dict], key: dict) -> int:
    matches = 0
    for r in rows:
        aid = r["asset_id"]
        k = key.get(aid)
        if not k:
            continue
        missing = [c for c in ("category", "impact_level", "level", "rationale") if not r.get(c)]
        if missing:
            K.fix(f"{aid}: حقول فارغة: {', '.join(missing)}")
            continue
        if r["impact_level"] not in K.IMPACTS or r["level"] not in K.LEVELS:
            K.fix(f"{aid}: مستوى الأثر أو المستوى ليس من القوائم")
            continue
        own = expected_level(r["impact_level"], r.get("law_blocks", ""), r.get("benefits_outweigh", ""))
        if not own:
            K.fix(f"{aid}: الأثر منخفض، فأجب عن الخطوة 4 (law_blocks) ثم الخطوة 5 إن لزم")
        elif own != r["level"]:
            K.fix(f"{aid}: المستوى لا يتبع من أثرك وخطواتك: راجع القاعدة في الدليل")
        if r["level"] == "مقيد" and r.get("restricted_group") not in ("أ", "ب", "ج"):
            K.fix(f"{aid}: مقيد بلا فئة (أ أو ب أو ج)")
        if len(r["rationale"].split()) < 8:
            K.fix(f"{aid}: المبرر أقصر من جملة: من يتضرر، وكيف، ولماذا ليس الأدنى")
        if K.LEVELS.index(k["level"]) >= 2 and r["level"] == "عام":
            K.fix(f"{aid}: أصل من المستويين الأعليين صُنّف «عام»: هذا يُسقط التقييم كله")
        ok_levels = [k["level"]] + k["accept"]
        ok_impacts = [k["impact"]] + [K.IMPACTS[K.LEVELS.index(x)] for x in k["accept"]]
        if r["level"] in ok_levels and r["impact_level"] in ok_impacts:
            matches += 1
        else:
            K.info(f"{aid}: التقدير أو المستوى يختلف عن المرجع")
    return matches


def main() -> int:
    path = K.arg_path(K.FILES / "rating" / "assets_20.xlsx")
    rows = K.read_sheet(path, "assets")
    key = K.key("lab_1_2")
    print(f"Ratings {path.name}: {len(rows)} assets\n")
    m = check_rows(rows, key)
    print()
    (K.ok if m >= NEED else K.fix)(f"مطابقة للمرجع في {m} من {len(key)} (المطلوب {NEED} على الأقل)")
    return K.finish("تقييم الأصول العشرين")


if __name__ == "__main__":
    sys.exit(main())
