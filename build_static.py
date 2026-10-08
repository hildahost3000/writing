#!/usr/bin/env python3
"""Build data/grammar.js: grammar.json plus furigana worked out ahead of time for every example.

index.html loads this file with a <script> tag when no server is running, which is what lets the
page work when opened straight from a folder, or when hosted on any static site.

    python3 build_static.py

Run it again whenever you edit grammar.json. It needs the furigana dictionary
(python3 setup_furigana.py) because that is what produces the readings.
"""
import json
import sys
from pathlib import Path

import furigana
from server import load_grammar

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "grammar.js"


def main():
    if not furigana.available():
        sys.exit("The furigana dictionary isn't installed. Run:  python3 setup_furigana.py")
    grammar = load_grammar()
    readings = {}
    for g in grammar:
        for ex in g.get("examples", []):
            plain = ex["ja"].replace("{{", "").replace("}}", "")
            if plain not in readings:
                readings[plain] = furigana.segments(plain)

    payload = json.dumps({"grammar": grammar, "furigana": readings}, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")  # safe inside a JS file
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(f"window.GP_DATA={payload};\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(grammar)} grammar points, {len(readings)} sentences with furigana, "
          f"{OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
