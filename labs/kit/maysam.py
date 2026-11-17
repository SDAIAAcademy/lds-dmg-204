"""Maysam, the assisted labelling pipeline of the (fictional) Al-Jareen Food Reserve Authority.

    uv run kit/maysam.py                       # label the 200 items and save out/maysam_labels.json
    uv run kit/maysam.py files/maysam/rules_v1.json

Three stages, in order. The first two run here for real, on the text of each item:
  1. pattern rules: personal data (identity numbers, mobiles, IBANs, e-mail) -> Restricted
  2. keyword rules: words that point to a level, in Arabic and English
  3. model stage: only for items that no rule matched. In the Authority it is a text classifier
     hosted inside the Authority. In this lab its suggestions are a recorded stand-in written for
     the course (columns model_level and model_confidence of items.xlsx): no model is called.
The first stage that matches decides, and its highest level wins.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as K  # noqa: E402

ITEMS = K.FILES / "maysam" / "items.xlsx"
RULES = K.FILES / "maysam" / "rules_v1.json"
OUT = K.LABS / "out"

ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")


def normalise(text: str) -> str:
    """Arabic normalisation: digits to Western, alef forms to bare alef, final ta marbuta to ha,
    no diacritics or tatweel, spaces inside numbers removed."""
    t = text.translate(ARABIC_DIGITS)
    t = "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
    t = t.replace("ـ", "")
    t = re.sub("[أإآ]", "ا", t).replace("ة", "ه").replace("ى", "ي")
    t = re.sub(r"(?<=\d)[ -](?=\d)", "", t)
    return t


def load_rules(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def label(text: str, rules: dict) -> tuple[str, str, list[str]]:
    """Return (level, stage, the names of the rules that matched) from the two rule stages,
    or ("", "", []) when no rule matched."""
    t = normalise(text) if rules.get("normalise_arabic") else text
    for stage in ("pattern", "keyword"):
        best, hits = -1, []
        for r in rules[stage]:
            terms = r.get("terms")
            if terms:
                low = t.lower()
                found = any((normalise(w) if rules.get("normalise_arabic") else w).lower() in low for w in terms)
            else:
                found = re.search(r["regex"], t) is not None
            if found:
                hits.append(r["name"])
                best = max(best, K.LEVELS.index(r["level"]))
        if hits:
            return K.LEVELS[best], stage, hits
    return "", "", []


def run(items: list[dict], rules: dict) -> list[dict]:
    out = []
    for it in items:
        level, stage, hits = label(it["content"], rules)
        if level:
            conf = 0.95 if stage == "pattern" else 0.9
        else:
            level, stage, conf = it["model_level"], "model", float(it["model_confidence"])
        out.append({"item_id": it["item_id"], "source": it["source"], "language": it["language"],
                    "reference_level": it["reference_level"], "maysam_level": level, "stage": stage,
                    "confidence": round(conf, 2), "rules": hits})
    return out


def load_items(path: Path = ITEMS) -> list[dict]:
    return K.read_sheet(path, "items")


def main() -> int:
    rules_path = K.arg_path(RULES)
    labels = run(load_items(), load_rules(rules_path))
    OUT.mkdir(exist_ok=True)
    (OUT / "maysam_labels.json").write_text(json.dumps(labels, ensure_ascii=False, indent=1), encoding="utf-8")
    by_stage: dict[str, int] = {}
    for x in labels:
        by_stage[x["stage"]] = by_stage.get(x["stage"], 0) + 1
    print(f"Maysam: {len(labels)} items labelled with {rules_path.name}")
    for s in ("pattern", "keyword", "model"):
        print(f"  {s:8} {by_stage.get(s, 0)}")
    print("saved out/maysam_labels.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
