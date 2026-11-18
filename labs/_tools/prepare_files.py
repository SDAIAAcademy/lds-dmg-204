# /// script
# requires-python = ">=3.11"
# dependencies = ["openpyxl>=3.1"]
# ///
"""Generate the Al-Jareen Food Reserve Authority file pack used by every lab (labs/files/) and the
reference keys and filled workbooks the checks compare with (labs/solutions/reference/).

    cd labs
    uv run _tools/prepare_files.py

Deterministic: fixed seeds and fixed file times, the same bytes on every run. Everything is
synthetic: the Authority, its people, suppliers, sites and numbers.
"""
from __future__ import annotations

import json
import re
import sys
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import content as C  # noqa: E402
import items as I  # noqa: E402

LABS = HERE.parent
OUT = LABS / "files"
REF = LABS / "solutions" / "reference"
FIXED = datetime(2026, 11, 1, 9, 0, 0)
HEAD = PatternFill("solid", fgColor="0F766E")
FILL = PatternFill("solid", fgColor="FFF7E0")
ANY = "أي"


# ------------------------------------------------------------------ writing helpers
def write_text(rel: str, text: str) -> None:
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((text.strip() + "\n").encode("utf-8"))


def put_ref(name: str, data) -> None:
    REF.mkdir(parents=True, exist_ok=True)
    (REF / f"{name}.json").write_bytes((json.dumps(data, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))


def sheet(wb, title, header, rows, fill_cols=(), widths=None, lists=None):
    ws = wb.create_sheet(title)
    ws.sheet_view.rightToLeft = True
    ws.append(header)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = HEAD
        c.alignment = Alignment(wrap_text=True, vertical="top")
    for r in rows:
        ws.append(list(r))
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
            if c.column - 1 in fill_cols:
                c.fill = FILL
    for i, w in enumerate(widths or [18] * len(header)):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i + 1)].width = w
    ws.freeze_panes = "A2"
    for col, values in (lists or {}).items():
        dv = DataValidation(type="list", formula1='"' + ",".join(values) + '"', allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"{col}2:{col}{max(2, len(rows) + 1)}")
    return ws


def guide(wb, lines):
    ws = wb.create_sheet("دليل")
    ws.sheet_view.rightToLeft = True
    ws.column_dimensions["A"].width = 120
    for ln in lines:
        ws.append([ln])
        ws.cell(row=ws.max_row, column=1).alignment = Alignment(wrap_text=True, vertical="top")
    return ws


def save(wb, path: Path) -> None:
    del wb[wb.sheetnames[0]]
    wb.properties.creator = wb.properties.lastModifiedBy = "Al-Jareen (fictional)"
    wb.properties.created = wb.properties.modified = FIXED
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    wb.save(tmp)
    with zipfile.ZipFile(tmp) as z:
        items = [(i.filename, z.read(i.filename)) for i in z.infolist()]
    stamp = FIXED.strftime("%Y-%m-%dT%H:%M:%SZ").encode()
    items = [(n, re.sub(rb"(<dcterms:(?:created|modified)[^>]*>)[^<]*(</dcterms)", rb"\g<1>" + stamp + rb"\g<2>", d))
             if n == "docProps/core.xml" else (n, d) for n, d in items]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in items:
            info = zipfile.ZipInfo(name, date_time=FIXED.timetuple()[:6])
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    tmp.unlink()


ASSET = {a[0]: a for a in C.ASSETS}


def ref_level(aid: str) -> str:
    a = ASSET[aid]
    return C.level_of(a[7], a[8], a[9])


# ------------------------------------------------------------------ the brief
BRIEF = """
هيئة الجَرين للمخزون الغذائي (جهة حكومية افتراضية في القطاع التنموي)
====================================================================
كل ما في هذه الملفات اصطناعي ومكتوب لمقرر LDS-DMG-204: الهيئة وموظفوها ومواقعها ومورّدوها وأرقامها.
أرقام الهوية تبدأ بالرقم 9 والجوالات بـ 0599، والآيبانات أرقام تحقق 00، والبريد بنطاق example.com، فلا يطابق شيء منها شخصًا أو حسابًا حقيقيًا.

ماذا تفعل الهيئة: تدير مخزونًا احتياطيًا للطوارئ من الأرز والسكر والزيوت والبقول في أحد عشر موقعًا، وتشتريه من موردين محليين ودوليين، وتنشر إحصاءات الواردات والأسعار، وتتعاقد مع مزارعين محليين على زراعة البقول وتدعمهم.
الهيئة مختلقة للتدريب: لا تقابل جهة حقيقية في اسمها ولا في اختصاصها، والأخطاء التي في ملفاتها مزروعة ليتدرب عليها المشارك.

من تعمل معهم
- وائل المطوع: مدير إدارة الإمداد والاستيراد، وممثل بيانات الأعمال لبياناتها (المختبرات كلها على هذه الإدارة).
- مها الحديثي: مديرة قطاع الجودة والمختبرات (أمثلة الشرائح من قطاعها).
- خالد السبهان: مدير إدارة دعم المزارعين (مهمة المتابعة على إدارته).
- لينا الفرج: مراجِعة تصنيف البيانات في مكتب إدارة البيانات.
- أسامة الزهراني: مختص بيانات الأعمال في إدارة أمن المعلومات، يطبق الضوابط.
- أروى المنصور: محللة مشتريات، مستخدمة بيانات.
- مِيسَم: مسار الوسم الآلي الذي تجرّبه الهيئة لاقتراح مستويات التصنيف.

قاعدة الهيئة لأدوات الذكاء الاصطناعي التوليدي: لا يدخلها شيء مصنف «مقيد» فأعلى، ولا شيء لم يُصنف بعد.
ولا يُلصق شيء من ملفات هذه المختبرات في أي مساعد ذكاء اصطناعي: المختبرات تدريب على الحكم، والحكم هنا حكمك.
"""

SCOPING_GUIDE = """
دليل الحصر في هيئة الجَرين (المختبر 1.1)
=======================================
1. النطاق: كل بيانات تتلقاها الإدارة أو تنتجها أو تتعامل معها، أيًّا كان مصدرها أو شكلها: جداول، وملفات، ووثائق ممسوحة، وبريد، وصور. البيانات المستلمة من جهة أخرى داخل النطاق.
2. الأصل: مجموعة بيانات لها مالك واحد وغرض واحد. جداول نظام واحد تخدم غرضًا واحدًا أصل واحد، وسلسلة وثائق من النوع نفسه (محاضر شهرية مثلًا) أصل واحد، ومسودة وثيقة ونسختها الموقعة أصل واحد.
3. النسخ: النسخة الاحتياطية والتصدير والنسخة في مجلد شخصي مواقع للأصل نفسه، لا أصول جديدة. سجّل كل موقع، فلكل موقع ضوابطه.
4. ليس أصلًا: ملف أو جدول بلا محتوى أعمال ينشئه النظام (ملفات القفل والمصغرات، وجداول تقنية فارغة). اكتب «ليس أصلًا».
5. إدارة أخرى: بيانات يملكها قطاع آخر وتوجد عندنا نسخة منها أو نقرؤها. لا تدخل حصر الإدارة، وتُبلَّغ إلى مالكها. اكتب «إدارة أخرى».
6. الشكل: مهيكلة (جداول بمخطط ثابت، ومنها جداول البيانات المنظمة)، شبه مهيكلة (رسائل وملفات بوسوم بلا مخطط ثابت، مثل XML وJSON)، غير مهيكلة (وثائق، وممسوحات، وبريد، وصور).
7. البيانات الشخصية: «نعم» إذا كان في الأصل ما يحدد شخصًا (اسم، هوية، جوال، حساب). هذا العمود لا يقرر المستوى: يقرره تقييم الأثر في المختبر 1.2.
"""

IMPACT_GUIDE = """
دليل تقييم الأثر في هيئة الجَرين (المختبرات 1.2 و1.3)
====================================================
مبني على سياسة تصنيف البيانات الوطنية (الإصدار الأول، 2020)، بصياغة المقرر.

1. الفئة: على من يقع الضرر لو وصل إلى البيانات من لا يحق له أو أُفصح عنها؟
   المصلحة الوطنية: سمعة المملكة، العلاقات الدبلوماسية، الأمن الوطني والنظام العام، الاقتصاد الوطني، البنى التحتية الوطنية، مهام الجهات الحكومية.
   أنشطة الجهات: أرباح الجهات الخاصة، أعمال الجهات الخاصة.
   الأفراد: صحة الأفراد وسلامتهم، الخصوصية.
   البيئة: الموارد البيئية.
   لا يوجد: حين لا ضرر على أحد.
2. مستوى الأثر: عالٍ (ضرر جسيم دائم لا يمكن تداركه)، متوسط (ضرر جسيم طويل يصعب احتواؤه)، منخفض (ضرر محدود قصير يمكن احتواؤه)، لا يوجد أثر. خذ أعلى أثر بين الفئات.
3. المستوى: عالٍ ← سري للغاية. متوسط ← سري. لا يوجد أثر ← عام.
   منخفض ← الخطوة 4: هل يمنع نظامٌ الإفصاح (مثل نظام حماية البيانات الشخصية لما فيه بيانات شخصية)؟ نعم ← مقيد.
   لا ← الخطوة 5: هل تفوق منافع الإفصاح (خدمة جديدة، شفافية، مشاركة المستفيدين) أضراره؟ نعم ← عام، لا ← مقيد.
4. فئة المقيد: (أ) إذا امتد الأثر إلى قطاع كامل أو نشاط اقتصادي عام، (ب) إذا امتد إلى عدة جهات أو مجموعة من الأفراد، (ج) إذا اقتصر على جهة واحدة أو فرد معين.
5. المبرر جملة واحدة: من يتضرر، وكيف، ولماذا ليس المستوى الأدنى.
6. قاعدة الهيئة في المقرر: لا أصل في المستويين الأعليين يصنف «عام»؛ هذا خطأ يُسقط التقييم كله.
"""


def build_scope():
    head = ["src_id", "origin", "system_or_path", "kind", "size_or_rows", "description", "asset_id", "form", "personal_data", "note"]
    rows = []
    for s, sys_, table, desc, nrows, _ in C.REGISTER:
        rows.append([s, "سجل الأنظمة", f"{sys_}: {table}", "جدول أو تصدير", f"{nrows} صف", desc, "", "", "", ""])
    for s, path, kind, kb, prev, _ in C.FILES:
        rows.append([s, "مخزن الملفات", path, kind, f"{kb} ك.ب", prev, "", "", "", ""])
    wb = openpyxl.Workbook()
    guide(wb, [
        "المختبر 1.1 · حصر أصول إدارة الإمداد والاستيراد",
        "في ورقة sources ستة وثلاثون مصدرًا: اثنا عشر من سجل الأنظمة وأربعة وعشرون من مخزن الملفات.",
        "لكل مصدر اكتب في asset_id رمز الأصل الذي ينتمي إليه (اختر رموزك: A01، A02…). المصادر التي هي الأصل نفسه تأخذ الرمز نفسه.",
        "أو اكتب «ليس أصلًا» أو «إدارة أخرى» بحسب دليل الحصر (scoping_guide.txt).",
        "ثم form (مهيكلة، شبه مهيكلة، غير مهيكلة) وpersonal_data (نعم، لا)، وnote إن احتجت.",
        "في ورقة assets سطر لكل أصل: رمزه واسمه وشكله، والمصادر التي هي مواقعه.",
        "الفحص من مجلد labs: uv run kit/scope_check.py files/scope/inventory.xlsx",
    ])
    forms = ["مهيكلة", "شبه مهيكلة", "غير مهيكلة"]
    sheet(wb, "sources", head, rows, fill_cols=(6, 7, 8, 9), widths=[8, 13, 42, 14, 12, 46, 14, 14, 12, 24],
          lists={"H": forms, "I": ["نعم", "لا"]})
    sheet(wb, "assets", ["asset_id", "asset_name", "form", "locations"], [], fill_cols=(0, 1, 2, 3), widths=[10, 40, 14, 40])
    save(wb, OUT / "scope" / "inventory.xlsx")
    write_text("scope/scoping_guide.txt", SCOPING_GUIDE)

    groups = {}
    for s, *_, a in C.REGISTER + C.FILES:
        groups.setdefault(a, []).append(s)
    key = {"groups": {a: sorted(v) for a, v in groups.items() if a.startswith("A")},
           "not_asset": sorted(groups.get("NOT", [])), "other": sorted(groups.get("OUT", [])),
           "form": {a[0]: a[2] for a in C.ASSETS}, "personal": {a[0]: a[3] for a in C.ASSETS}}
    put_ref("lab_1_1", key)
    # the filled reference workbook
    wb = openpyxl.Workbook()
    filled = []
    src_asset = {s: a for s, *_, a in C.REGISTER + C.FILES}
    for r in rows:
        a = src_asset[r[0]]
        if a == "NOT":
            filled.append(r[:6] + ["ليس أصلًا", "", "", ""])
        elif a == "OUT":
            filled.append(r[:6] + ["إدارة أخرى", "", "", "تُبلَّغ إلى قطاع الجودة"])
        else:
            filled.append(r[:6] + [a, ASSET[a][2], ASSET[a][3], ""])
    sheet(wb, "sources", head, filled)
    sheet(wb, "assets", ["asset_id", "asset_name", "form", "locations"],
          [[a[0], a[1], a[2], "، ".join(groups[a[0]])] for a in C.ASSETS])
    save(wb, REF / "inventory_reference.xlsx")


RATE_HEAD = ["asset_id", "asset_name", "form", "personal_data", "description", "category", "sub_category",
             "impact_level", "law_blocks", "benefits_outweigh", "level", "restricted_group", "rationale"]
RATE_LISTS = {"F": list(C.CATEGORIES), "H": C.IMPACTS, "I": ["نعم", "لا"], "J": ["نعم", "لا"], "K": C.LEVELS,
              "L": ["أ", "ب", "ج"]}
GROUP_AR = {"A": "أ", "B": "ب", "C": "ج", "": ""}


def rating_rows(levels=None, impacts=None, filled=True):
    rows = []
    for a in C.ASSETS:
        aid = a[0]
        base = [aid, a[1], a[2], a[3], a[4]]
        if not filled:
            rows.append(base + [""] * 8)
            continue
        lv = (levels or {}).get(aid, ref_level(aid))
        imp = (impacts or {}).get(aid, a[7])
        grp = GROUP_AR[a[10]] if lv == "مقيد" else ""
        if lv == "مقيد" and not grp:
            grp = "ج"
        law, ben = (a[8], a[9]) if imp == 1 else ("", "")
        if imp == 1 and lv == "عام":
            law, ben = "لا", "نعم"
        elif imp == 1 and lv == "مقيد" and law != "نعم":
            law, ben = "لا", "لا"
        elif imp == 1 and not law:
            law, ben = "نعم", ""
        rows.append(base + [a[5], a[6], C.IMPACTS[imp], law, ben, lv, grp, a[12]])
    return rows


def build_rating():
    wb = openpyxl.Workbook()
    guide(wb, [
        "المختبر 1.2 · تقدير أثر 20 أصلًا وتحديد مستوياتها",
        "لكل أصل: الفئة والفئة الفرعية، ومستوى الأثر، وجواب الخطوتين 4 و5 حين يكون الأثر منخفضًا، والمستوى، وفئة المقيد، والمبرر في جملة.",
        "الدليل: impact_guide.txt. اترك law_blocks وbenefits_outweigh فارغين حين لا يكون الأثر منخفضًا.",
        "الفحص من مجلد labs: uv run kit/rating_check.py files/rating/assets_20.xlsx",
    ])
    sheet(wb, "assets", RATE_HEAD, rating_rows(filled=False), fill_cols=tuple(range(5, 13)),
          widths=[8, 30, 12, 10, 52, 16, 20, 12, 10, 10, 12, 8, 50], lists=RATE_LISTS)
    save(wb, OUT / "rating" / "assets_20.xlsx")
    write_text("rating/impact_guide.txt", IMPACT_GUIDE)
    key = {a[0]: {"level": ref_level(a[0]), "impact": C.IMPACTS[a[7]], "category": a[5], "sub_category": a[6],
                  "group": GROUP_AR[a[10]], "accept": a[11]} for a in C.ASSETS}
    put_ref("lab_1_2", key)
    wb = openpyxl.Workbook()
    sheet(wb, "assets", RATE_HEAD, rating_rows())
    save(wb, REF / "assets_20_reference.xlsx")


def build_reconcile():
    pa_lv, pa_im, pb_lv, pb_im = {}, {}, {}, {}
    for aid, (la, ia, lb, ib) in C.PEER_DISAGREE.items():
        pa_lv[aid], pa_im[aid], pb_lv[aid], pb_im[aid] = la, ia, lb, ib
    for aid, (lv, im) in C.PEER_BOTH_WRONG.items():
        pa_lv[aid], pa_im[aid], pb_lv[aid], pb_im[aid] = lv, im, lv, im
    for name, lv, im in (("peer_a", pa_lv, pa_im), ("peer_b", pb_lv, pb_im)):
        wb = openpyxl.Workbook()
        rows = rating_rows(lv, im)
        for r in rows:          # a peer's file has its own short reasons, not the reference ones
            r[12] = "تقدير الزميل: " + ("بلا أثر يذكر" if r[10] == "عام" else "أثر " + r[7] + " على " + r[6])
        sheet(wb, "assets", RATE_HEAD, rows, widths=[8, 30, 12, 10, 52, 16, 20, 12, 10, 10, 12, 8, 50])
        save(wb, OUT / "reconcile" / f"{name}.xlsx")
    wb = openpyxl.Workbook()
    guide(wb, [
        "المختبر 1.3 · المطابقة مع زميل وأثر التجميع",
        "1. قارن تقديرين: uv run kit/agreement.py files/reconcile/peer_a.xlsx files/reconcile/peer_b.xlsx (أو ملفك وملف زميلك من المختبر 1.2).",
        "2. في ورقة disagreements سطر لكل خلاف يطبعه الأمر: المستوى المتفق عليه، والدليل من وصف الأصل، والخطوة التي حسمت.",
        "3. في ورقة aggregations صنّف المجموعات الثلاث المجمّعة: الحد الأدنى (أعلى مكوّن)، ثم أثر المجموعة كلها، ثم المستوى.",
        "4. الفحص: uv run kit/reconcile_check.py files/reconcile/reconcile.xlsx",
    ])
    sheet(wb, "disagreements", ["asset_id", "level_a", "level_b", "agreed_level", "evidence", "deciding_step"], [],
          fill_cols=(0, 1, 2, 3, 4, 5), widths=[10, 12, 12, 14, 60, 30], lists={"D": C.LEVELS})
    agg_rows = [[g[0], g[1], g[2], g[3], "", "", "", ""] for g in C.AGGREGATIONS]
    sheet(wb, "aggregations", ["case_id", "name", "components", "description", "floor_level", "combined_impact", "level", "rationale"],
          agg_rows, fill_cols=(4, 5, 6, 7), widths=[8, 24, 30, 60, 12, 14, 12, 50],
          lists={"E": C.LEVELS, "F": C.IMPACTS, "G": C.LEVELS})
    save(wb, OUT / "reconcile" / "reconcile.xlsx")

    disagree = sorted(C.PEER_DISAGREE)
    key = {"disagree": disagree, "agreed": {a: ref_level(a) for a in disagree},
           "accept": {a: ASSET[a][11] for a in disagree},
           "aggregations": {g[0]: {"floor": g[4], "level": g[5]} for g in C.AGGREGATIONS},
           "both_wrong": sorted(C.PEER_BOTH_WRONG)}
    put_ref("lab_1_3", key)
    wb = openpyxl.Workbook()
    sheet(wb, "disagreements", ["asset_id", "level_a", "level_b", "agreed_level", "evidence", "deciding_step"],
          [[a, C.PEER_DISAGREE[a][0], C.PEER_DISAGREE[a][2], ref_level(a), ASSET[a][12], "تقدير الأثر والخطوتان 4 و5"] for a in disagree])
    sheet(wb, "aggregations", ["case_id", "name", "components", "description", "floor_level", "combined_impact", "level", "rationale"],
          [[g[0], g[1], g[2], g[3], g[4], "متوسط" if g[5] == "سري" else "منخفض", g[5], g[6]] for g in C.AGGREGATIONS])
    save(wb, REF / "reconcile_reference.xlsx")


def lv_i(x: str) -> int:
    return C.LEVELS.index(x)


def control_allowed(c, level: str) -> bool:
    return bool(c[3]) and lv_i(c[3]) <= lv_i(level) <= lv_i(c[4])


def build_handling():
    wb = openpyxl.Workbook()
    guide(wb, [
        "المختبر 1.4 · مصفوفة التعامل",
        "في ورقة systems أنظمة الهيئة وأعلى مستوى اعتُمد له كل نظام. في ورقة controls كتالوج الضوابط: لكل ضابط مرحلته والمستويات التي يصلح لها.",
        "املأ matrix.xlsx: في كل خلية (مستوى × مرحلة) رمز ضابط واحد أو أكثر من الكتالوج، تفصل بينها بفاصلة.",
        "الضوابط الإلزامية من مستوى ما فأعلى يجب أن تظهر في خلاياها. بعض الضوابط في الكتالوج لا يصلح لأي مستوى أعلى من العام، وواحد لا يصلح لأي مستوى.",
        "الفحص: uv run kit/matrix_check.py files/handling/matrix.xlsx",
    ])
    sheet(wb, "systems", ["system_id", "system", "approved_up_to", "notes"], [list(s) for s in C.SYSTEMS], widths=[10, 36, 14, 60])
    sheet(wb, "controls", ["control_id", "stage", "control", "from_level", "to_level", "mandatory_from"],
          [[c[0], c[1], c[2], c[3] or "غير معتمد", c[4] or "غير معتمد", c[5] or "-"] for c in C.CONTROLS],
          widths=[10, 12, 80, 12, 12, 14])
    save(wb, OUT / "handling" / "systems_and_controls.xlsx")
    wb = openpyxl.Workbook()
    sheet(wb, "matrix", ["level"] + C.STAGES, [[lv] + [""] * 5 for lv in C.LEVELS], fill_cols=(1, 2, 3, 4, 5),
          widths=[14, 22, 22, 22, 22, 22])
    save(wb, OUT / "handling" / "matrix.xlsx")
    ref = {}
    for lv in C.LEVELS:
        for st in C.STAGES:
            ref[f"{lv}|{st}"] = [c[0] for c in C.CONTROLS if c[1] == st and control_allowed(c, lv)
                                 and c[0] not in ("HC-06", "HC-14", "HC-24")]
    put_ref("lab_1_4", {"matrix": ref, "controls": {c[0]: {"stage": c[1], "from": c[3], "to": c[4], "mandatory_from": c[5]} for c in C.CONTROLS}})
    wb = openpyxl.Workbook()
    sheet(wb, "matrix", ["level"] + C.STAGES, [[lv] + [", ".join(ref[f"{lv}|{st}"]) for st in C.STAGES] for lv in C.LEVELS])
    save(wb, REF / "matrix_reference.xlsx")


REG_HEAD = ["asset_id", "asset_name", "owner", "level", "restricted_group", "classified_by", "classified_on",
            "reviewer", "reviewed_on", "level_after_review", "owner_approval", "owner_approved_on",
            "declass_trigger_type", "declass_trigger", "declass_or_review_date", "stored_in",
            "exception_control", "exception_reason", "compensating_control", "exception_expiry", "exception_approver"]
ESC_HEAD = ["dispute_id", "raised_by", "asset", "positions", "policy_point", "interim_level", "escalate_to", "decide_by", "evidence"]


def build_register():
    dec_rows = []
    for aid, sysid, ttype, trig, ddate in C.DECISIONS:
        a = ASSET[aid]
        dec_rows.append([aid, a[1], ref_level(aid), GROUP_AR[a[10]] if ref_level(aid) == "مقيد" else "", C.PEOPLE["wael"],
                         C.CLASSIFIED_ON, sysid, a[12]])
    wb = openpyxl.Workbook()
    guide(wb, [
        "المختبر 2.1 · مدخلات سجل التصنيف ومذكرتا التصعيد",
        "ورقة decisions: قرارات اليوم الأول لاثني عشر أصلًا، ومكان حفظ كل أصل الآن (system_id من ملف الأنظمة).",
        "ورقة systems: أعلى مستوى اعتُمد له كل نظام. أصل محفوظ في نظام لم يُعتمد لمستواه يحتاج استثناءً موثقًا أو نقلًا.",
        "املأ register.xlsx: سطر لكل أصل، ثم مذكرة تصعيد لكل نزاع في disputes.txt.",
        "الفحص: uv run kit/register_check.py files/register/register.xlsx",
    ])
    sheet(wb, "decisions", ["asset_id", "asset_name", "level", "restricted_group", "classified_by", "classified_on", "stored_in", "rationale"],
          dec_rows, widths=[8, 34, 12, 8, 16, 12, 10, 70])
    sheet(wb, "systems", ["system_id", "system", "approved_up_to"], [s[:3] for s in C.SYSTEMS], widths=[10, 36, 14])
    sheet(wb, "controls", ["control_id", "stage", "control"], [c[:3] for c in C.CONTROLS], widths=[10, 12, 80])
    save(wb, OUT / "register" / "decisions.xlsx")
    wb = openpyxl.Workbook()
    reg_rows = [[d[0], ASSET[d[0]][1]] + [""] * (len(REG_HEAD) - 2) for d in C.DECISIONS]
    sheet(wb, "register", REG_HEAD, reg_rows, fill_cols=tuple(range(2, len(REG_HEAD))), widths=[8, 30] + [14] * (len(REG_HEAD) - 2),
          lists={"D": C.LEVELS, "J": C.LEVELS, "M": C.TRIGGER_TYPES})
    sheet(wb, "escalations", ESC_HEAD, [[d[0], d[1], d[2], "", "", "", "", "", ""] for d in C.DISPUTES],
          fill_cols=(3, 4, 5, 6, 7, 8), widths=[8, 30, 24, 50, 30, 12, 26, 12, 40], lists={"F": C.LEVELS})
    save(wb, OUT / "register" / "register.xlsx")
    lines = ["النزاعان (المختبر 2.1)", "=" * 22]
    for d in C.DISPUTES:
        lines += ["", f"{d[0]} · {d[2]}", f"أثاره: {d[1]}", d[3], f"المستويان المطروحان: {d[4]} و{d[5]}"]
    lines += ["", "مذكرة التصعيد: موقف كل طرف ودليله، ونقطة السياسة محل الخلاف، والمستوى المؤقت حتى القرار، والجهة التي يُصعَّد إليها، وموعد القرار."]
    write_text("register/disputes.txt", "\n".join(lines))

    sys_level = {s[0]: s[2] for s in C.SYSTEMS}
    exc = [d[0] for d in C.DECISIONS if lv_i(ref_level(d[0])) > lv_i(sys_level[d[1]])]
    key = {"assets": {d[0]: {"level": ref_level(d[0]), "group": GROUP_AR[ASSET[d[0]][10]] if ref_level(d[0]) == "مقيد" else "",
                             "stored_in": d[1], "needs_exception": d[0] in exc} for d in C.DECISIONS},
           "owner": C.PEOPLE["wael"], "reviewer": C.PEOPLE["lina"], "classified_on": C.CLASSIFIED_ON,
           "trigger_types": C.TRIGGER_TYPES, "disputes": {d[0]: {"interim": d[4]} for d in C.DISPUTES},
           "controls": [c[0] for c in C.CONTROLS]}
    put_ref("lab_2_1", key)
    # the filled reference
    rows = []
    for aid, sysid, ttype, trig, ddate in C.DECISIONS:
        lv = ref_level(aid)
        e = aid in exc
        rows.append([aid, ASSET[aid][1], C.PEOPLE["wael"], lv, GROUP_AR[ASSET[aid][10]] if lv == "مقيد" else "", C.PEOPLE["wael"],
                     C.CLASSIFIED_ON, C.PEOPLE["lina"], "2026-11-20", lv, C.PEOPLE["wael"], "2026-11-23",
                     ttype, trig, ddate, sysid,
                     "HC-03" if e else "", "النظام S3 معتمد حتى مقيد، والنقل إلى خزنة S2 يحتاج ستة أسابيع" if e else "",
                     "HC-02 مجلد مستقل بصلاحيات الحاجة إلى المعرفة، وHC-05 علامة الحماية، ومراجعة سجل الوصول أسبوعيًا" if e else "",
                     "2027-01-31" if e else "", C.PEOPLE["lina"] if e else ""])
    esc = [["D1", C.DISPUTES[0][1], "A02", "أروى: عام لتسهيل المشاركة. وائل: مقيد لأن الأسعار تضر بالموردين وبالمنافسات القادمة.",
            "الخطوة 5: الموازنة بين المنافع والأضرار، والمشاركة لا تحتاج تصنيفًا عامًا", "مقيد",
            "لينا الفرج، مراجِعة التصنيف في مكتب إدارة البيانات", "2026-12-02",
            "طلب المشاركة يُعالج باتفاقية مشاركة (HC-21) دون تغيير المستوى"],
           ["D2", C.DISPUTES[1][1], "J01", "مها: مقيد (ب) لأن نتائج الفحص لكل مورد تضر بسمعته. وائل: عام للشفافية.",
            "تنسيق التصنيف بين الإدارات، وتحديد مالك للمجموعة المشتركة", "مقيد",
            "مكتب إدارة البيانات، ثم لجنة حوكمة البيانات إن لم يُحسم", "2026-12-02",
            "نتائج فحص لكل مورد باسمه، وما زالت قيد الاعتراض في 12 شحنة"]]
    wb = openpyxl.Workbook()
    sheet(wb, "register", REG_HEAD, rows)
    sheet(wb, "escalations", ESC_HEAD, esc)
    save(wb, REF / "register_reference.xlsx")


RULES_V1 = {
    "name": "rules_v1",
    "normalise_arabic": False,
    "pattern": [
        {"name": "ten_digit_number", "regex": "(?<![0-9])[0-9]{10}(?![0-9])", "level": "مقيد"},
        {"name": "iban", "regex": "SA[0-9]{22}", "level": "مقيد"},
        {"name": "email", "regex": "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}", "level": "مقيد"},
    ],
    "keyword": [
        {"name": "top_secret_words", "terms": ["خطة السحب", "drawdown plan"], "level": "سري للغاية"},
        {"name": "secret_words", "terms": ["المخزون الاستراتيجي", "مستوى المخزون", "مذكرة التفاهم", "stock level",
                                           "strategic reserve", "memorandum of understanding"], "level": "سري"},
        {"name": "restricted_words", "terms": ["عرض سعر", "quotation", "مكافأة", "bonus"], "level": "مقيد"},
    ],
}

ROUTE_HEAD = ["rule_id", "final_level", "stage", "language", "source", "confidence_below", "action", "approver"]


def build_maysam():
    items = I.make_items()
    wb = openpyxl.Workbook()
    guide(wb, [
        "المختبر 2.2 · قياس مسار الوسم الآلي مِيسَم",
        "ورقة items: مئتا عنصر اصطناعي، ولكل عنصر المستوى الذي اعتمده المالك (reference_level).",
        "model_level وmodel_confidence: اقتراح مرحلة النموذج، مسجل سلفًا بديلًا عن نموذج (لا يُستدعى أي نموذج في هذا المختبر).",
        "مِيسَم يشغّل قواعد الأنماط والكلمات على المحتوى فعلًا: uv run kit/measure.py",
        "ثم اكتب قواعد التوجيه في routing.xlsx وشغّل: uv run kit/route.py",
        "لا تُلصق أي عنصر من هذا الملف في أداة ذكاء اصطناعي.",
    ])
    sheet(wb, "items", ["item_id", "source", "language", "content", "reference_level", "model_level", "model_confidence"],
          [[x["item_id"], x["source"], x["language"], x["content"], x["reference_level"], x["model_level"], x["model_confidence"]] for x in items],
          widths=[8, 12, 8, 80, 12, 12, 10])
    save(wb, OUT / "maysam" / "items.xlsx")
    (OUT / "maysam").mkdir(parents=True, exist_ok=True)
    (OUT / "maysam" / "rules_v1.json").write_bytes((json.dumps(RULES_V1, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    wb = openpyxl.Workbook()
    guide(wb, [
        "قواعد التوجيه: تُقرأ من الأعلى، وأول قاعدة تنطبق كل شروطها تقرر مصير العنصر.",
        "final_level: مستوى مِيسَم النهائي أو «أي». stage: pattern أو keyword أو model أو «أي». language: ar أو en أو mixed أو «أي».",
        "source: crisis أو stock أو contracts أو security أو suppliers أو logistics أو procurement أو hr أو published أو «أي».",
        "confidence_below: رقم بين 0 و1 (ينطبق إذا كانت الثقة أقل منه) أو «أي».",
        "action: «مراجعة بشرية» أو «قبول بموافقة مجمعة». approver: اسم من يعتمد ما تمرره القاعدة.",
        "القاعدة الأخيرة شاملة: كل شروطها «أي».",
    ])
    sheet(wb, "rules", ROUTE_HEAD, [["R1", ANY, ANY, ANY, ANY, ANY, "قبول بموافقة مجمعة", C.PEOPLE["wael"]]],
          fill_cols=tuple(range(8)), widths=[8, 12, 10, 10, 12, 14, 20, 18],
          lists={"G": ["مراجعة بشرية", "قبول بموافقة مجمعة"]})
    save(wb, OUT / "maysam" / "routing.xlsx")
    ref_rules = [
        ["R1", ANY, ANY, ANY, "crisis", ANY, "مراجعة بشرية", C.PEOPLE["wael"]],
        ["R2", ANY, ANY, ANY, "security", ANY, "مراجعة بشرية", C.PEOPLE["wael"]],
        ["R3", ANY, ANY, ANY, "stock", ANY, "مراجعة بشرية", C.PEOPLE["wael"]],
        ["R4", ANY, ANY, ANY, "contracts", ANY, "مراجعة بشرية", C.PEOPLE["wael"]],
        ["R5", ANY, "model", ANY, ANY, "0.7", "مراجعة بشرية", C.PEOPLE["lina"]],
        ["R6", "عام", "model", "ar", ANY, ANY, "مراجعة بشرية", C.PEOPLE["lina"]],
        ["R7", ANY, ANY, ANY, ANY, ANY, "قبول بموافقة مجمعة", C.PEOPLE["wael"]],
    ]
    wb = openpyxl.Workbook()
    sheet(wb, "rules", ROUTE_HEAD, ref_rules)
    save(wb, REF / "routing_reference.xlsx")
    put_ref("lab_2_2_items", {"n": len(items), "by_level": {lv: sum(1 for x in items if x["reference_level"] == lv) for lv in C.LEVELS}})


CAP_REGISTER = [
    ("K01", "نظام دعم المزارعين", "farmers", "سجل المزارعين: الاسم والهوية والجوال وموقع المزرعة والآيبان", 12400),
    ("K02", "نظام دعم المزارعين", "subsidy_payments", "مدفوعات الدعم لكل مزارع", 48700),
    ("K03", "نظام دعم المزارعين", "subsidy_payments_bak", "نسخة احتياطية من جدول المدفوعات", 48700),
    ("K04", "نظام دعم المزارعين", "tmp_sync_log", "جدول تقني للمزامنة يُفرَّغ كل ليلة", 0),
    ("K05", "نظام الإمداد", "seed_reserve_levels", "أرصدة بذور البقول الاحتياطية لكل موقع في خطة الجفاف", 3300),
]
CAP_FILES = [
    ("K06", "farmer_support/published/subsidy_totals_by_region_2026.pdf", "PDF", "إجمالي الدعم المنشور لكل منطقة"),
    ("K07", "farmer_support/field/pest_reports_2026/", "مجلد نماذج ممسوحة (86)", "تقارير الآفات الميدانية بأسماء المزارعين ومواقع مزارعهم"),
    ("K08", "farmer_support/plans/drought_seed_contingency.docx", "مستند", "خطة الطوارئ لبذور البقول في الجفاف: المواقع والكميات وأولويات التوزيع"),
    ("K09", "farmer_support/mailbox/complaints.pst", "أرشيف بريد", "شكاوى المزارعين ومراسلاتهم"),
    ("K10", "farmer_support/studies/crop_area_estimates_2027_draft.xlsx", "جدول", "تقديرات المساحات المزروعة لكل منطقة قبل النشر"),
    ("K11", "farmer_support/training/attendance_2026.xlsx", "جدول", "حضور ورش التدريب: الأسماء والجوالات"),
    ("K12", "farmer_support/published/guidance_leaflets/", "مجلد (12 نشرة)", "نشرات الإرشاد المنشورة"),
    ("K13", "farmer_support/personal/khalid/farmers_extract.csv", "CSV", "تصدير من سجل المزارعين في مجلد شخصي"),
    ("K14", "farmer_support/field/Thumbs.db", "ملف نظام", "ملف مصغرات بلا محتوى أعمال"),
    ("K15", "farmer_support/supply/stock_levels_week44.xlsx", "جدول", "نسخة من أرصدة المخزون الأسبوعية لإدارة الإمداد"),
    ("K16", "farmer_support/studies/crop_area_method_note.docx", "مستند", "مذكرة منهجية التقديرات المرافقة للدراسة"),
]

CAP_BRIEF = """
مهمة المتابعة: حزمة تصنيف لإدارة دعم المزارعين
=================================================
الإدارة: إدارة دعم المزارعين في هيئة الجَرين (افتراضية). مديرها وممثل بيانات الأعمال لبياناتها: خالد السبهان.
الملف: sources.xlsx فيه ستة عشر مصدرًا من سجل الأنظمة ومخزن الملفات. الأنظمة وكتالوج الضوابط في files/handling/systems_and_controls.xlsx.

الحزمة (مجلد مشترك في Google Drive، خلال أسبوعين من الورشة):
1. الحصر: الأصول ومواقعها، وما ليس أصلًا، وما يخص إدارة أخرى.
2. التقييم: لكل أصل الفئة ومستوى الأثر والخطوتان 4 و5 حين يلزم، والمستوى وفئة المقيد، والمبرر في جملة.
3. ضوابط التعامل: أسطر المصفوفة للمستويات التي ظهرت في الإدارة، بضابط مسمّى لكل مرحلة، ونقل أي أصل محفوظ في نظام غير معتمد لمستواه أو استثناء موثق.
4. السجل: مدخل لكل أصل غير عام فيه الاعتماد والمراجعة ومحفز رفع التصنيف.
5. مذكرة تصعيد واحدة لأصعب حالة عندك.
6. قاعدة توجيه واحدة على الأقل لمِيسَم تخص أصول هذه الإدارة، مع اسم المعتمِد.

في المراجعة (عشر دقائق): خمس دقائق تعرض فيها الحزمة، ثم خمس يسألك فيها المراجِع، ومنها حقيقة تجميع جديدة تعيد بها تصنيف أصل واحد أمامه.
لا يدخل أي محتوى من هذه الملفات أداة ذكاء اصطناعي توليدي. صياغة المذكرة بمساعد مسموحة بكلماتك أنت فقط.
"""


def build_capstone():
    rows = [[k, "سجل الأنظمة", f"{s}: {t}", "جدول", f"{n} صف", d, "", "", "", ""] for k, s, t, d, n in CAP_REGISTER]
    rows += [[k, "مخزن الملفات", p, kind, "", d, "", "", "", ""] for k, p, kind, d in CAP_FILES]
    wb = openpyxl.Workbook()
    sheet(wb, "sources", ["src_id", "origin", "system_or_path", "kind", "size_or_rows", "description", "asset_id", "form", "personal_data", "note"],
          rows, fill_cols=(6, 7, 8, 9), widths=[8, 13, 46, 18, 12, 50, 12, 14, 12, 24])
    save(wb, OUT / "capstone" / "sources.xlsx")
    write_text("capstone/brief.txt", CAP_BRIEF)


def main() -> int:
    write_text("case_brief.txt", BRIEF)
    build_scope()
    build_rating()
    build_reconcile()
    build_handling()
    build_register()
    build_maysam()
    build_capstone()
    print("files written to labs/files and labs/solutions/reference")
    return 0


if __name__ == "__main__":
    sys.exit(main())
