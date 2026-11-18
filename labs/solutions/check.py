"""Run every lab's reference solution through the kit and assert its numbers. From labs/:

    uv run solutions/check.py            # every lab
    uv run solutions/check.py 1.2 2.2    # some of them

For each lab: the supplied starting file must NOT pass (it still holds its task), and the
reference workbook in solutions/reference/ must pass with the numbers the slides quote.
No lab calls a language model. Maysam's rule stages run for real; its model stage is the
recorded stand-in in files/maysam/items.xlsx. Outputs go to out/, which you may delete.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

LABS = Path(__file__).resolve().parents[1]
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")


def run(*args: str) -> tuple[int, str]:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    p = subprocess.run([sys.executable, *args], cwd=LABS, capture_output=True, text=True, encoding="utf-8", env=env)
    return p.returncode, p.stdout + p.stderr


def expect(cmd: list[str], code: int, *needles: str) -> str:
    c, text = run(*cmd)
    assert c == code, f"{' '.join(cmd)}: exit {c}, expected {code}\n{text[-2000:]}"
    for n in needles:
        assert re.search(n, text), f"{' '.join(cmd)}: missing {n!r}\n{text[-2000:]}"
    return text


def lab_1_1() -> None:
    expect(["kit/scope_check.py", "files/scope/inventory.xlsx"], 1, "بلا asset_id")
    t = expect(["kit/scope_check.py", "solutions/reference/inventory_reference.xlsx"], 0, "RESULT: PASS", "أصول مطابقة للمرجع: 20 من 20")
    print(t.splitlines()[-1])


def lab_1_2() -> None:
    expect(["kit/rating_check.py", "files/rating/assets_20.xlsx"], 1, "حقول فارغة")
    t = expect(["kit/rating_check.py", "solutions/reference/assets_20_reference.xlsx"], 0, "مطابقة للمرجع في 20 من 20")
    print(t.splitlines()[-1])


def lab_1_3() -> None:
    t = expect(["kit/agreement.py", "files/reconcile/peer_a.xlsx", "files/reconcile/peer_b.xlsx"], 0,
               "اتفاق على المستوى: 14 من 20", "كابا كوهين: 0.52")
    print("\n".join(t.splitlines()[:4]))
    expect(["kit/reconcile_check.py", "files/reconcile/reconcile.xlsx"], 1, "لم تُسجل")
    t = expect(["kit/reconcile_check.py", "solutions/reference/reconcile_reference.xlsx"], 0, "RESULT: PASS")
    print(t.splitlines()[-1])


def lab_1_4() -> None:
    expect(["kit/matrix_check.py", "files/handling/matrix.xlsx"], 1, "خلية فارغة")
    t = expect(["kit/matrix_check.py", "solutions/reference/matrix_reference.xlsx"], 0, "خلايا سليمة: 20 من 20")
    print(t.splitlines()[-1])


def lab_2_1() -> None:
    expect(["kit/register_check.py", "files/register/register.xlsx"], 1, "حقول فارغة")
    t = expect(["kit/register_check.py", "solutions/reference/register_reference.xlsx"], 0, "A14: استثناء موثق", "RESULT: PASS")
    print(t.splitlines()[-1])
    # the owner may not approve his own exception: the reference with the owner as approver must fail
    import openpyxl
    wb = openpyxl.load_workbook(LABS / "solutions" / "reference" / "register_reference.xlsx")
    ws = wb["register"]
    head = [c.value for c in ws[1]]
    for row in ws.iter_rows(min_row=2):
        if row[0].value == "A14":
            row[head.index("exception_approver")].value = row[head.index("owner")].value
    (LABS / "out").mkdir(exist_ok=True)
    wb.save(LABS / "out" / "register_self_approved.xlsx")
    expect(["kit/register_check.py", "out/register_self_approved.xlsx"], 1, "معتمِد الاستثناء هو المالك")


def lab_2_2() -> None:
    t = expect(["kit/maysam.py"], 0, "pattern +50", "keyword +35", "model +115")
    t = expect(["kit/measure.py"], 0, r"سري +32 +7 \( 21.9%\)", r"عام +70 +0 \(  0.0%\) +27 \( 38.6%\)",
               "التطابق التام: 161 من 200", "ar +120 عنصرًا: تلتقط القواعد 46 دون توحيد، و66 بعده")
    print("\n".join(t.splitlines()[3:9]))
    expect(["kit/route.py"], 1, "8 عنصرًا مرجعه سري")
    t = expect(["kit/route.py", "solutions/reference/routing_reference.xlsx"], 0, "إلى المراجعة البشرية: 80 من 200", "RESULT: PASS")
    print(t.splitlines()[-1])


LABS_RUN = {"1.1": lab_1_1, "1.2": lab_1_2, "1.3": lab_1_3, "1.4": lab_1_4, "2.1": lab_2_1, "2.2": lab_2_2}


def main() -> int:
    which = sys.argv[1:] or list(LABS_RUN)
    for w in which:
        print(f"\n=== Lab {w}")
        LABS_RUN[w]()
        print(f"Lab {w}: PASS")
    print("\nALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
