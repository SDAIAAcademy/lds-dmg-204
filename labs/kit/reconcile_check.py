"""Lab 1.3: check the reconciliation log and the three aggregated datasets.

    uv run kit/reconcile_check.py files/reconcile/reconcile.xlsx
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as K  # noqa: E402


def main() -> int:
    path = K.arg_path(K.FILES / "reconcile" / "reconcile.xlsx")
    key = K.key("lab_1_3")
    dis = {r["asset_id"]: r for r in K.read_sheet(path, "disagreements") if r.get("asset_id")}
    print(f"Reconciliation {path.name}: {len(dis)} disagreements logged\n")
    missing = [a for a in key["disagree"] if a not in dis]
    if missing:
        K.fix(f"خلافات بين الملفين لم تُسجل: {len(missing)} (شغّل kit/agreement.py على peer_a وpeer_b)")
    for a in key["disagree"]:
        r = dis.get(a)
        if not r:
            continue
        if len(r.get("evidence", "").split()) < 6:
            K.fix(f"{a}: الدليل أقصر من جملة من وصف الأصل")
        if r.get("agreed_level") in [key["agreed"][a]] + key["accept"][a]:
            K.ok(f"{a}: المستوى المتفق عليه مقبول")
        else:
            K.fix(f"{a}: المستوى المتفق عليه يختلف عن المرجع: عد إلى وصف الأصل والدليل")
    print()
    for r in K.read_sheet(path, "aggregations"):
        g = r.get("case_id")
        k = key["aggregations"].get(g)
        if not k:
            continue
        if r.get("floor_level") != k["floor"]:
            K.fix(f"{g}: الحد الأدنى هو أعلى مستويات المكوّنات")
        if r.get("level") == k["level"]:
            K.ok(f"{g}: المستوى مطابق للمرجع")
        else:
            K.fix(f"{g}: المستوى يختلف عن المرجع: قيّم أثر المجموعة كلها، لا أثر كل مكوّن")
        if len(r.get("rationale", "").split()) < 8:
            K.fix(f"{g}: المبرر أقصر من جملة")
    print()
    K.info(f"تنبيه: في {len(key['both_wrong'])} أصل اتفق الزميلان وأخطآ معًا؛ الاتفاق لا يعني الصواب.")
    return K.finish("المطابقة والتجميع")


if __name__ == "__main__":
    sys.exit(main())
