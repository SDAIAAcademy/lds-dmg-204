"""Shared helpers of the LDS-DMG-204 lab kit. Run every kit command from the labs/ folder:

    uv run kit/<command>.py [workbook]

Each command reads a workbook you filled, prints [OK] and [FIX] lines, and ends with
RESULT: PASS or RESULT: n to fix. It never prints the reference answer itself.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

LABS = Path(__file__).resolve().parents[1]
FILES = LABS / "files"
KEYS = LABS / "solutions" / "reference"

LEVELS = ["عام", "مقيد", "سري", "سري للغاية"]
IMPACTS = ["لا يوجد أثر", "منخفض", "متوسط", "عالي"]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROBLEMS: list[str] = []


def ok(text: str) -> None:
    print(f"[OK]  {text}")


def fix(text: str) -> None:
    PROBLEMS.append(text)
    print(f"[FIX] {text}")


def info(text: str) -> None:
    print(f"      {text}")


def finish(evidence: str) -> int:
    print()
    if PROBLEMS:
        print(f"RESULT: {len(PROBLEMS)} to fix. النتيجة: {len(PROBLEMS)} بنود تحتاج إصلاحًا قبل: {evidence}")
        return 1
    print(f"RESULT: PASS. النتيجة: تحقق {evidence}")
    return 0


def clean(v) -> str:
    if v is None:
        return ""
    if hasattr(v, "strftime"):
        return v.strftime("%Y-%m-%d")
    return " ".join(str(v).split())


def read_sheet(path: Path, name: str) -> list[dict]:
    import openpyxl

    if not path.exists():
        print(f"[FIX] الملف غير موجود: {path.name}")
        sys.exit(2)
    wb = openpyxl.load_workbook(path, data_only=True)
    if name not in wb.sheetnames:
        print(f"[FIX] لا توجد ورقة باسم {name} في {path.name}")
        sys.exit(2)
    rows = list(wb[name].iter_rows(values_only=True))
    head = [clean(h) for h in rows[0]]
    out = []
    for r in rows[1:]:
        if all(clean(v) == "" for v in r):
            continue
        out.append({h: clean(v) for h, v in zip(head, r) if h})
    return out


def key(name: str):
    """Read one of the reference keys the checks compare with (solutions/reference/<name>.json).
    A trainee copy of the course has no solutions folder: the trainer runs the check then."""
    path = KEYS / f"{name}.json"
    if not path.exists():
        print("[FIX] مفتاح المرجع غير موجود في هذه النسخة (solutions/reference). اطلب من المدرب تشغيل الفحص.")
        sys.exit(2)
    return json.loads(path.read_text(encoding="utf-8"))


def level_index(text: str) -> int:
    t = clean(text)
    return LEVELS.index(t) if t in LEVELS else -1


def arg_path(default: Path) -> Path:
    if len(sys.argv) > 1:
        p = Path(sys.argv[1])
        return p if p.is_absolute() else (Path.cwd() / p)
    return default
