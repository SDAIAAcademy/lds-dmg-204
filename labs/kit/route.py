"""Lab 2.2: apply your routing rules to Maysam's labels and see what reaches a person.

    uv run kit/route.py                          # files/maysam/routing.xlsx
    uv run kit/route.py my_routing.xlsx

Rules are read top to bottom; the first rule whose conditions all hold decides the item.
A condition left as "any" (أي) always holds. The last rule must be a catch-all (every condition
"any"). Actions: review (مراجعة بشرية) or accept (قبول بموافقة مجمعة). Every rule names the person
who approves what it lets through: no machine label is used without a named human approver.

PASS when: no item whose reference is Secret or Top Secret is under-labelled and accepted; every
rule has an approver; the last rule is a catch-all; at most half of the items go to review.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as K  # noqa: E402
import maysam as M  # noqa: E402

ANY = {"", "أي", "any"}
REVIEW = "مراجعة بشرية"
ACCEPT = "قبول بموافقة مجمعة"
MAX_LOAD = 0.5


def holds(rule: dict, x: dict) -> bool:
    if rule["final_level"] not in ANY and rule["final_level"] != x["maysam_level"]:
        return False
    if rule["stage"] not in ANY and rule["stage"] != x["stage"]:
        return False
    if rule["language"] not in ANY and rule["language"] != x["language"]:
        return False
    if rule["source"] not in ANY and rule["source"] != x["source"]:
        return False
    below = rule.get("confidence_below", "")
    if below not in ANY and not x["confidence"] < float(below):
        return False
    return True


def route(labels: list[dict], rules: list[dict]) -> list[dict]:
    out = []
    for x in labels:
        rule = next((r for r in rules if holds(r, x)), None)
        out.append({**x, "rule": rule["rule_id"] if rule else "", "action": rule["action"] if rule else REVIEW})
    return out


def main() -> int:
    path = K.arg_path(K.FILES / "maysam" / "routing.xlsx")
    rules = K.read_sheet(path, "rules")
    labels = M.run(M.load_items(), M.load_rules(M.RULES))
    print(f"Routing {len(labels)} Maysam labels with {len(rules)} rules from {path.name}\n")
    if not rules:
        K.fix("لا قواعد في الورقة rules")
        return K.finish("قواعد التوجيه")
    for r in rules:
        if r.get("action") not in (REVIEW, ACCEPT):
            K.fix(f"القاعدة {r.get('rule_id')}: الإجراء يجب أن يكون «{REVIEW}» أو «{ACCEPT}»")
        if not r.get("approver"):
            K.fix(f"القاعدة {r.get('rule_id')}: لا مُعتمِد مسمّى لما تمرره")
    last = rules[-1]
    if not all(last.get(c, "") in ANY for c in ("final_level", "stage", "language", "source", "confidence_below")):
        K.fix("القاعدة الأخيرة ليست شاملة: اجعل كل شروطها «أي»")
    routed = route(labels, rules)
    n = len(routed)
    review = [x for x in routed if x["action"] == REVIEW]
    print(f"إلى المراجعة البشرية: {len(review)} من {n} ({100 * len(review) / n:.1f}%)")
    for r in rules:
        hits = [x for x in routed if x["rule"] == r["rule_id"]]
        print(f"  {r['rule_id']:5} {r['action']:18} {len(hits):>4} عنصرًا")
    print("\nما يمر دون مراجعة فردية، بحسب المستوى المرجعي:")
    residual_top = 0
    for i, lv in enumerate(K.LEVELS):
        acc = [x for x in routed if x["action"] == ACCEPT and x["reference_level"] == lv]
        miss = [x for x in acc if K.LEVELS.index(x["maysam_level"]) < i]
        fa = [x for x in acc if K.LEVELS.index(x["maysam_level"]) > i]
        print(f"  {lv:12} مقبول {len(acc):>3}، منها إغفال {len(miss):>2} وإنذار كاذب {len(fa):>2}")
        if i >= 2:
            residual_top += len(miss)
    print()
    if residual_top:
        K.fix(f"{residual_top} عنصرًا مرجعه سري أو سري للغاية وُسم بأقل منه ومرّ دون مراجعة")
    else:
        K.ok("لا إغفال في سري ولا سري للغاية يمر دون مراجعة")
    if len(review) > MAX_LOAD * n:
        K.fix(f"حمل المراجعة {len(review)} من {n}، أكثر من النصف: قواعدك ترسل كل شيء تقريبًا إلى الناس")
    else:
        K.ok(f"حمل المراجعة {len(review)} من {n}")
    return K.finish("قواعد التوجيه")


if __name__ == "__main__":
    sys.exit(main())
