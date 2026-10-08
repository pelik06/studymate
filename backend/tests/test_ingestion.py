"""Test: parse the golden lecture deck and inspect the result."""
from pathlib import Path

import fitz

from backend.services.ingestion import parse_pdf

ROOT = Path(__file__).resolve().parents[2]
PDF_PATH = ROOT / "data" / "DS-Lct01-IntroToDS.pdf"

PAGES = parse_pdf(str(PDF_PATH))
TOTAL = len(fitz.open(str(PDF_PATH)))

print(f"Pages kept: {len(PAGES)} of {TOTAL} (image-only slides skipped)")
print(f"Skipped pages: {sorted(set(range(1, TOTAL + 1)) - {p['page'] for p in PAGES})}")

print("\n--- Sample of parsed pages ---")
for p in PAGES[:5]:
    print(f"\n[PAGE {p['page']}] TITLE: {p['title']!r}")
    print(p["text"][:250])

print("\n--- Sanity checks ---")
leaked = [p["page"] for p in PAGES if "TF4507" in p["text"]]
print(f"Pages still containing footer text: {leaked or 'NONE ✅'}")

no_title = [p["page"] for p in PAGES if not p["title"]]
print(f"Pages without a title: {no_title or 'NONE ✅'}")