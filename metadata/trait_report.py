import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ID_JSON = re.compile(r"^(\d+)\.json$", re.IGNORECASE)

def iter_token_files(meta_dir: Path):
    files = [p for p in meta_dir.iterdir() if p.is_file() and ID_JSON.match(p.name)]
    files.sort(key=lambda p: int(ID_JSON.match(p.name).group(1)))
    return files

def main():
    # Assume metadata folder is ./metadata next to the script execution folder
    cwd = Path(".").resolve()
    meta_dir = cwd / "metadata"

    if not meta_dir.exists():
        print("❌ No ./metadata folder found next to your images.")
        sys.exit(1)

    files = iter_token_files(meta_dir)
    if not files:
        print("❌ No metadata JSON files found named like 1.json, 2.json, ... in /metadata")
        sys.exit(1)

    counts = defaultdict(Counter)
    total_tokens = 0
    skipped = 0

    for path in files:
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            skipped += 1
            continue

        attrs = data.get("attributes", [])
        if not isinstance(attrs, list):
            skipped += 1
            continue

        total_tokens += 1

        for a in attrs:
            if not isinstance(a, dict):
                continue
            t = a.get("trait_type")
            v = a.get("value")
            if t is None or v is None:
                continue
            t = str(t).strip()
            v = str(v).strip()
            if not t:
                continue
            counts[t][v] += 1

    if total_tokens == 0:
        print("❌ No valid metadata files could be parsed.")
        sys.exit(2)

    print("\n=== Trait Rarity Report ===")
    print(f"Tokens analyzed: {total_tokens}")
    if skipped:
        print(f"⚠️ Files skipped (invalid JSON or bad attributes): {skipped}")

    for trait in sorted(counts.keys(), key=lambda x: x.lower()):
        print(f"\n## {trait}")
        items = list(counts[trait].items())
        items.sort(key=lambda x: (-x[1], x[0].lower()))  # most common first
        for val, c in items:
            pct = (c / total_tokens) * 100.0
            print(f"- {val}: {c} tokens ({pct:.2f}%)")

    print("\nDone. ✅ All trait percentages printed above.")
    sys.exit(0)

if __name__ == "__main__":
    main()
