"""Lab 1.1: check a scoped inventory against the Authority's scoping guide.

    uv run kit/scope_check.py files/scope/inventory.xlsx

Compares how you grouped the 36 sources into assets, what you excluded, and the form and
personal-data columns. It names the rows that differ, never the reference answer.
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as K  # noqa: E402

NOT, OTHER = "ليس أصلًا", "إدارة أخرى"


def main() -> int:
    path = K.arg_path(K.FILES / "scope" / "inventory.xlsx")
    rows = K.read_sheet(path, "sources")
    key = K.key("lab_1_1")
    print(f"Inventory {path.name}: {len(rows)} sources\n")
    empty = [r["src_id"] for r in rows if not r.get("asset_id")]
    if empty:
        K.fix(f"{len(empty)} مصدرًا بلا asset_id: {', '.join(empty)}")
    groups: dict[str, set] = {}
    for r in rows:
        a = r.get("asset_id", "")
        if a and a not in (NOT, OTHER):
            groups.setdefault(a, set()).add(r["src_id"])
    for label, want in ((NOT, set(key["not_asset"])), (OTHER, set(key["other"]))):
        got = {r["src_id"] for r in rows if r.get("asset_id") == label}
        if got == want:
            K.ok(f"«{label}»: {len(got)} مصادر كما في الدليل")
        else:
            K.fix(f"«{label}» يختلف عن الدليل في المصادر: {', '.join(sorted(got ^ want))}")
    ref_sets = {frozenset(v): a for a, v in key["groups"].items()}
    matched = {}
    for g, srcs in sorted(groups.items()):
        a = ref_sets.get(frozenset(srcs))
        if a:
            matched[g] = a
        else:
            K.fix(f"الأصل {g} ({', '.join(sorted(srcs))}) لا يطابق أصلًا في المرجع: راجع قواعد الأصل والنسخ في الدليل")
    print()
    K.info(f"أصول مطابقة للمرجع: {len(matched)} من {len(key['groups'])}")
    if len(matched) == len(key["groups"]):
        K.ok("كل الأصول العشرين مجمّعة كما في المرجع")
    form_ok = pers_ok = 0
    for g, a in matched.items():
        rs = [r for r in rows if r.get("asset_id") == g]
        form = Counter(r.get("form", "") for r in rs).most_common(1)[0][0]
        pers = Counter(r.get("personal_data", "") for r in rs).most_common(1)[0][0]
        if form == key["form"][a]:
            form_ok += 1
        else:
            K.info(f"الأصل {g}: الشكل يختلف عن المرجع")
        if pers == key["personal"][a]:
            pers_ok += 1
        else:
            K.info(f"الأصل {g}: عمود البيانات الشخصية يختلف عن المرجع")
    n = len(key["groups"])
    (K.ok if form_ok >= n - 2 else K.fix)(f"الشكل صحيح في {form_ok} من {n}")
    (K.ok if pers_ok >= n - 2 else K.fix)(f"البيانات الشخصية صحيحة في {pers_ok} من {n}")
    return K.finish("حصر الأصول")


if __name__ == "__main__":
    sys.exit(main())
