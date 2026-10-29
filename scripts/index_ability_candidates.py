"""Extract searchable subclass and ability candidates from official inventory definitions.

This is metadata classification, not a guarantee that an ability is selectable.
"""
import json
import os
from pathlib import Path

KEYWORDS = ("grenade", "melee", "super", "aspect", "fragment", "class ability",
            "jump", "movement", "subclass", "prismatic", "stasis", "strand")

def classify_candidates(items):
    result = []
    for item in items:
        name = (item.get("name") or "").strip()
        if not name:
            continue
        text = name.casefold()
        matches = [word for word in KEYWORDS if word in text]
        if not matches:
            continue
        result.append({"hash": item["hash"], "name": name,
                       "matched_terms": matches,
                       "class_type": item.get("classType"),
                       "source": "inventory-name-keyword",
                       "ability_legality": "unverified"})
    return sorted(result, key=lambda x: x["hash"])

def main():
    root = Path(os.environ.get("OUTPUT_DIR", "output"))
    items = json.loads((root / "items_extended.json").read_text())
    result = classify_candidates(items)
    (root / "ability_candidates.json").write_text(json.dumps(result, ensure_ascii=False))
    print(f"Identified {len(result)} keyword-based ability candidates; all unverified")

if __name__ == "__main__":
    main()
