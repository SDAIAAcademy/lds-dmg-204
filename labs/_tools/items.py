"""The 200 items Maysam labels in lab 2.2, and the recorded stand-in for its model stage.

Every item is synthetic. Identity numbers start with 9 (no real Saudi identity number does),
mobiles with 0599, IBANs carry the check digits 00 (never valid), e-mail uses example.com.
The stand-in model is a fixed error model written for the course, not the output of any model:
it errs more on Arabic and mixed text at the two highest levels, and over-labels some English
items. Whatever the lab measures about the model stage measures this stand-in only.
"""
from __future__ import annotations

import random

NAMES = ["فيصل العبدلي", "نوال الرميح", "بندر الهزاني", "سلمى العقيلي", "ماجد الفريح", "غادة السيف",
         "تركي البواردي", "منيرة الطويان", "عادل الجبرين", "هيفاء الغنيم", "رائد العمار", "جود القحيز"]
NAMES_EN = ["Faisal Al-Abdali", "Nawal Al-Rumaih", "Bandar Al-Hazzani", "Salma Al-Uqaili", "Majed Al-Furaih"]
SUPPLIERS = ["مؤسسة السنابل الذهبية التجارية", "شركة الحقول الممتدة", "مؤسسة الوادي الأخضر", "شركة الميزان للتوريد"]
SUPPLIERS_EN = ["Golden Ears Trading", "Wide Fields Co.", "Green Valley Est.", "Balance Supply Co."]
SITES = ["ج-03", "ج-05", "ج-07", "ج-09", "ج-11"]
SITES_EN = ["J-03", "J-05", "J-07", "J-09", "J-11"]
COMMOD = ["القمح", "الأرز", "السكر", "الزيوت"]
COMMOD_EN = ["wheat", "rice", "sugar", "edible oil"]
PORTS = ["ميناء الساحل الشرقي", "ميناء البحر الأحمر الشمالي"]
PORTS_EN = ["the East Coast port", "the North Red Sea port"]
MARKETS = ["سوق المدينة المركزي", "سوق الجملة الشرقي", "سوق الحبوب الشمالي"]
AR_DIG = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")

# (level, language, source, template, how the rules should treat it: a note for the answer key)
T = [
    # ---------------- Top Secret (8)
    ("سري للغاية", "ar", "crisis", "خطة السحب في الأزمات، الملحق {k}: تتحرك القافلة {k} من الموقع {site} بمرافقة أمنية عبر المسار {r}.", 2),
    ("سري للغاية", "ar", "crisis", "خطه السحب من المخزون: نقاط تجمع القوافل وتوقيت التحرك مع الجهات الأمنية للموقع {site}.", 1),
    ("سري للغاية", "ar", "crisis", "ملحق التنسيق مع الجهات العسكرية: حراسة القوافل من الموقع {site} في حالة الطوارئ الوطنية.", 1),
    ("سري للغاية", "ar", "crisis", "خطة سحب المخزون في الطوارئ: أولوية المواقع ومسارات الإمداد البديلة، والمنسق {name} على الجوال {phone}.", 1),
    ("سري للغاية", "en", "crisis", "Crisis drawdown plan, annex {k}: convoy {k} leaves site {site_en} under armed escort via route {r}.", 1),
    ("سري للغاية", "en", "crisis", "Emergency distribution schedule coordinated with the security forces for site {site_en}.", 1),
    ("سري للغاية", "mixed", "crisis", "Annex {k} من خطة السحب: convoy timings for site {site_en}.", 1),
    # ---------------- Secret (32)
    ("سري", "ar", "stock", "مستوى المخزون في الموقع {site}: {n} طن من {c}، يكفي {d} يومًا.", 4),
    ("سري", "ar", "stock", "مستويات المخزون للأسبوع {w}: الموقع {site} عند {p}٪ من سعته.", 4),
    ("سري", "ar", "stock", "رصيد المخزون الإستراتيجي من {c} في الموقع {site} انخفض إلى {n} طن.", 3),
    ("سري", "ar", "stock", "المخزون الاستراتيجي من {c} يغطي {d} يومًا على مستوى المملكة، والموقع {site} أدناها.", 2),
    ("سري", "ar", "contracts", "مسودة مذكرة التفاهم مع الشركة الدولية: الكمية السنوية {n} طن والسعر المرجعي.", 1),
    ("سري", "ar", "contracts", "مذكرة تفاهم لإنشاء مخزون مشترك مع شركة دولية، البند {k}: حصص التخزين.", 1),
    ("سري", "ar", "security", "مخطط كاميرات المراقبة ونقاط الدخول في الموقع {site}.", 2),
    ("سري", "ar", "security", "إحداثيات بوابات الموقع {site} وترتيب نوبات الحراسة، والمشرف {name} على {phone}.", 1),
    ("سري", "en", "stock", "Stock level at site {site_en}: {n} t of {c_en}, {d} days of cover.", 3),
    ("سري", "en", "stock", "Strategic reserve position, week {w}: site {site_en} at {p}% of capacity.", 2),
    ("سري", "en", "contracts", "MoU draft with the international supplier: annual volume {n} t.", 2),
    ("سري", "en", "security", "Site {site_en} gate layout and guard shift pattern.", 2),
    ("سري", "mixed", "stock", "تقرير week {w}: stock level في الموقع {site} يساوي {n} t", 2),
    ("سري", "mixed", "security", "site {site_en} حراسة: shift pattern والبوابات", 2),
    ("سري", "mixed", "stock", "أرصدة المواقع week {w}: الموقع {site} {n} t من {c}", 1),
    # ---------------- Restricted (90)
    ("مقيد", "ar", "suppliers", "جهة الاتصال في {sup}: {name}، جوال {phone}.", 8),
    ("مقيد", "ar", "suppliers", "جهة الاتصال في {sup}: {name}، جوال {phone_ar}.", 7),
    ("مقيد", "ar", "logistics", "رقم هوية السائق {id} للرحلة {k} إلى الموقع {site}.", 5),
    ("مقيد", "ar", "logistics", "هوية السائق {id_ar} وجواله {phone_ar}.", 5),
    ("مقيد", "ar", "suppliers", "آيبان {sup}: {iban}.", 4),
    ("مقيد", "ar", "procurement", "جوال المندوب {name}: {phone_sp}.", 4),
    ("مقيد", "ar", "procurement", "حضر الاجتماع: {name}، و{name2}، و{name3}.", 4),
    ("مقيد", "ar", "procurement", "عرض سعر {sup} لتوريد {c}: {price} ريالًا للطن، صالح 30 يومًا.", 4),
    ("مقيد", "ar", "hr", "مكافأة شهر {m} لفريق المستودع {site}: {n} ريال للفرد.", 3),
    ("مقيد", "ar", "suppliers", "تأخر {sup} في التوريد {d} أيام، وفُرضت غرامة {price} ريال.", 4),
    ("مقيد", "ar", "procurement", "كراسة الشروط قبل الإعلان: المواصفة {k} لنسبة الكسر في الأرز.", 2),
    ("مقيد", "ar", "procurement", "محضر لجنة المخزون: الموقف التفاوضي في الشراء القادم من {c}.", 2),
    ("مقيد", "en", "suppliers", "Supplier contact: {name_en}, mobile {phone}.", 6),
    ("مقيد", "en", "procurement", "Quotation from {sup_en}: SAR {price} per tonne of {c_en}.", 5),
    ("مقيد", "en", "suppliers", "Delivery penalty for {sup_en}: {d} days late.", 6),
    ("مقيد", "en", "logistics", "Driver ID {id} assigned to trip {k}.", 5),
    ("مقيد", "mixed", "suppliers", "contact {name} mobile {phone_ar}", 6),
    ("مقيد", "mixed", "procurement", "عرض سعر quotation من {sup_en}: {price} SAR", 5),
    ("مقيد", "mixed", "suppliers", "penalty على {sup}: {d} days", 5),
    # ---------------- Public (70)
    ("عام", "ar", "published", "وصلت شحنة {c} بكمية {n} طن إلى {port}.", 10),
    ("عام", "ar", "published", "متوسط سعر كيس {c} وزن 50 كجم في {mkt}: {price} ريالًا.", 9),
    ("عام", "ar", "published", "للاستفسار عن الحملة اتصل بالرقم المجاني {tollfree}.", 6),
    ("عام", "ar", "published", "أُعلنت المنافسة رقم {tender} لتوريد السكر.", 5),
    ("عام", "ar", "published", "حملة «لا تخزّن أكثر من حاجتك» تبدأ الأسبوع القادم في {mkt}.", 6),
    ("عام", "ar", "published", "إجراءات تسجيل المستورد: السجل التجاري وشهادة المنشأ.", 5),
    ("عام", "ar", "published", "إعلان وظيفة أخصائي جودة، والتقديم عبر بوابة التوظيف.", 4),
    ("عام", "en", "published", "Press release: {n} t of {c_en} arrived at {port_en}.", 6),
    ("عام", "en", "published", "Call our free line {tollfree} about the campaign.", 4),
    ("عام", "en", "published", "The monthly imports report for {m_en} is published.", 4),
    ("عام", "mixed", "published", "Press release: وصول {n} t من {c} إلى {port}", 6),
    ("عام", "mixed", "published", "حملة awareness: الرقم المجاني {tollfree}", 5),
]

MONTHS = ["يوليو", "أغسطس", "سبتمبر"]
MONTHS_EN = ["July", "August", "September"]


def make_items(seed: int = 2204) -> list[dict]:
    rng = random.Random(seed)
    items = []
    for level, lang, source, tpl, count in T:
        for _ in range(count):
            phone = "0599" + "".join(rng.choice("0123456789") for _ in range(6))
            nid = "9" + "".join(rng.choice("0123456789") for _ in range(9))
            v = dict(
                k=rng.randint(1, 9), r=rng.randint(1, 6), site=rng.choice(SITES), site_en=rng.choice(SITES_EN),
                n=rng.randrange(2000, 90000, 500), d=rng.randint(12, 140), w=rng.randint(30, 44), p=rng.randint(31, 96),
                c=rng.choice(COMMOD), c_en=rng.choice(COMMOD_EN), name=rng.choice(NAMES), name2=rng.choice(NAMES),
                name3=rng.choice(NAMES), name_en=rng.choice(NAMES_EN), sup=rng.choice(SUPPLIERS), sup_en=rng.choice(SUPPLIERS_EN),
                phone=phone, phone_ar=phone.translate(AR_DIG), phone_sp=f"{phone[:2]} {phone[2:4]} {phone[4:7]} {phone[7:]}",
                id=nid, id_ar=nid.translate(AR_DIG), iban="SA0099" + "".join(rng.choice("0123456789") for _ in range(18)),
                price=rng.randrange(900, 4200, 10), m=rng.choice(MONTHS), m_en=rng.choice(MONTHS_EN),
                port=rng.choice(PORTS), port_en=rng.choice(PORTS_EN), mkt=rng.choice(MARKETS),
                tollfree="800" + "".join(rng.choice("0123456789") for _ in range(7)),
                tender="2026" + "".join(rng.choice("0123456789") for _ in range(6)),
            )
            items.append({"level": level, "language": lang, "source": source, "content": tpl.format(**v)})
    rng.shuffle(items)
    out = []
    for i, it in enumerate(items, 1):
        lv = ["عام", "مقيد", "سري", "سري للغاية"].index(it["level"])
        model, conf = stand_in(rng, lv, it["language"])
        out.append({"item_id": f"M{i:03d}", "source": it["source"], "language": it["language"], "content": it["content"],
                    "reference_level": it["level"], "model_level": ["عام", "مقيد", "سري", "سري للغاية"][model],
                    "model_confidence": conf})
    return out


def stand_in(rng: random.Random, lv: int, lang: str) -> tuple[int, float]:
    """The recorded stand-in for the model stage: a fixed error model, not a model."""
    u = rng.random()
    if lang == "en":
        p_ok = {0: 0.80, 1: 0.90, 2: 0.90, 3: 0.90}[lv]
    else:
        p_ok = {0: 0.90, 1: 0.85, 2: 0.70, 3: 0.70}[lv]
    if u < p_ok:
        return lv, round(rng.uniform(0.70, 0.98), 2)
    if lv == 0:
        wrong = 1
    elif lv == 1:
        wrong = 0 if (lang != "en" and rng.random() < 0.7) else 2
    else:
        wrong = lv - 1
    return wrong, round(rng.uniform(0.45, 0.85), 2)
