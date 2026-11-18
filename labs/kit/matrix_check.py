"""Lab 1.4: check a handling matrix against the Authority's control catalogue.

    uv run kit/matrix_check.py files/handling/matrix.xlsx

Every cell (level x stage) needs at least one control from the catalogue; each control must be
of that stage and approved for that level; the controls the catalogue makes mandatory from a
level up must be there; storage, transfer and sharing need a control that says where or how.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as K  # noqa: E402

STAGES = ["التخزين", "النقل", "المشاركة", "الاحتفاظ", "الإتلاف"]
WHERE = {"التخزين": {"HC-01", "HC-02", "HC-03", "HC-04"}, "النقل": {"HC-10", "HC-11", "HC-12", "HC-13", "HC-14"},
         "المشاركة": {"HC-20", "HC-21", "HC-22", "HC-23", "HC-24"}}


def allowed(c: dict, level: str) -> bool:
    if c["from"] not in K.LEVELS:
        return False
    i = K.LEVELS.index(level)
    return K.LEVELS.index(c["from"]) <= i <= K.LEVELS.index(c["to"])


def main() -> int:
    path = K.arg_path(K.FILES / "handling" / "matrix.xlsx")
    rows = {r["level"]: r for r in K.read_sheet(path, "matrix")}
    key = K.key("lab_1_4")
    cat = key["controls"]
    print(f"Matrix {path.name}\n")
    filled = 0
    for lv in K.LEVELS:
        r = rows.get(lv, {})
        for st in STAGES:
            ids = re.findall(r"HC-\d\d", r.get(st, "").upper())
            cell = f"{lv} × {st}"
            if not ids:
                K.fix(f"{cell}: خلية فارغة")
                continue
            bad = [i for i in ids if i not in cat]
            if bad:
                K.fix(f"{cell}: رموز ليست في الكتالوج: {', '.join(bad)}")
            wrong_stage = [i for i in ids if i in cat and cat[i]["stage"] != st]
            if wrong_stage:
                K.fix(f"{cell}: ضوابط من مرحلة أخرى: {', '.join(wrong_stage)}")
            not_ok = [i for i in ids if i in cat and cat[i]["stage"] == st and not allowed(cat[i], lv)]
            if not_ok:
                K.fix(f"{cell}: ضوابط غير معتمدة لهذا المستوى: {', '.join(not_ok)}")
            mand = [i for i, c in cat.items() if c["stage"] == st and c["mandatory_from"]
                    and K.LEVELS.index(lv) >= K.LEVELS.index(c["mandatory_from"]) and i not in ids]
            if mand:
                K.fix(f"{cell}: ينقصه ضابط إلزامي من هذا المستوى")
            if st in WHERE and not (set(ids) & WHERE[st]):
                K.fix(f"{cell}: لا ضابط يحدد أين أو كيف ({st})")
            if not (bad or wrong_stage or not_ok or mand) and (st not in WHERE or set(ids) & WHERE[st]):
                filled += 1
    print()
    K.info(f"خلايا سليمة: {filled} من {len(K.LEVELS) * len(STAGES)}")
    return K.finish("مصفوفة التعامل")


if __name__ == "__main__":
    sys.exit(main())
