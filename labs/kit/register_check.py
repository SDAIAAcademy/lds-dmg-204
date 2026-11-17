"""Lab 2.1: check register entries and the two escalation notes.

    uv run kit/register_check.py files/register/register.xlsx

Checks what a register entry must hold (the national standard's data register fields and the
Authority's rules): the level of the decision, owner approval, a reviewer who is not the
classifier, a review within one month, a declassification trigger for every non-public asset,
and an exception (with a compensating control, an expiry within 90 days and an approver)
wherever an asset sits in a system not approved for its level.
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as K  # noqa: E402

REQUIRED = ["owner", "level", "classified_by", "classified_on", "reviewer", "reviewed_on", "level_after_review",
            "owner_approval", "owner_approved_on", "stored_in"]


def day(text: str) -> date | None:
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def main() -> int:
    path = K.arg_path(K.FILES / "register" / "register.xlsx")
    key = K.key("lab_2_1")
    rows = {r["asset_id"]: r for r in K.read_sheet(path, "register")}
    print(f"Register {path.name}: {len(rows)} entries\n")
    for aid, k in key["assets"].items():
        r = rows.get(aid)
        if not r:
            K.fix(f"{aid}: لا مدخل في السجل")
            continue
        miss = [c for c in REQUIRED if not r.get(c)]
        if miss:
            K.fix(f"{aid}: حقول فارغة: {', '.join(miss)}")
            continue
        if r["level"] != k["level"]:
            K.fix(f"{aid}: المستوى في السجل غير مستوى القرار")
        if k["level"] == "مقيد" and r.get("restricted_group") != k["group"]:
            K.fix(f"{aid}: فئة المقيد غير فئة القرار")
        if r["reviewer"] == r["classified_by"]:
            K.fix(f"{aid}: المراجِع هو من صنّف: الفصل بين المهام")
        if r["owner_approval"] != key["owner"]:
            K.fix(f"{aid}: الاعتماد ليس من ممثل بيانات الأعمال لهذه الإدارة")
        c, v = day(r["classified_on"]), day(r["reviewed_on"])
        if not c or not v:
            K.fix(f"{aid}: تاريخ التصنيف أو المراجعة ليس بصيغة سنة-شهر-يوم")
        elif not 0 <= (v - c).days <= 31:
            K.fix(f"{aid}: المراجعة بعد أكثر من شهر من التصنيف الأولي، أو قبله")
        if r["level_after_review"] not in K.LEVELS:
            K.fix(f"{aid}: المستوى بعد المراجعة ليس من القائمة")
        if k["level"] != "عام":
            if r.get("declass_trigger_type") not in key["trigger_types"] or len(r.get("declass_trigger", "").split()) < 3:
                K.fix(f"{aid}: لا محفز لرفع التصنيف أو مراجعته")
            if not day(r.get("declass_or_review_date", "")):
                K.fix(f"{aid}: لا تاريخ لرفع التصنيف أو مراجعته")
        if k["needs_exception"]:
            exp, app = day(r.get("exception_expiry", "")), day(r["owner_approved_on"])
            comp = re.findall(r"HC-\d\d", r.get("compensating_control", ""))
            if not (r.get("exception_control") and r.get("exception_reason") and comp and r.get("exception_approver")):
                K.fix(f"{aid}: محفوظ في نظام غير معتمد لمستواه بلا استثناء كامل (الضابط، والسبب، وضابط تعويضي من الكتالوج، والمعتمِد)")
            elif not exp or not app or not 0 < (exp - app).days <= 90:
                K.fix(f"{aid}: الاستثناء بلا تاريخ انتهاء خلال 90 يومًا")
            elif any(x not in key["controls"] for x in comp):
                K.fix(f"{aid}: الضابط التعويضي ليس في الكتالوج")
            else:
                K.ok(f"{aid}: استثناء موثق")
    print()
    esc = {r["dispute_id"]: r for r in K.read_sheet(path, "escalations") if r.get("dispute_id")}
    for d, k in key["disputes"].items():
        r = esc.get(d, {})
        miss = [c for c in ("positions", "policy_point", "interim_level", "escalate_to", "decide_by", "evidence") if not r.get(c)]
        if miss:
            K.fix(f"{d}: مذكرة التصعيد ناقصة: {', '.join(miss)}")
        elif r["interim_level"] != k["interim"]:
            K.fix(f"{d}: المستوى المؤقت يجب أن يكون الأعلى بين الموقفين حتى يُحسم النزاع")
        else:
            K.ok(f"{d}: مذكرة التصعيد مكتملة")
    return K.finish("مدخلات السجل ومذكرتا التصعيد")


if __name__ == "__main__":
    sys.exit(main())
