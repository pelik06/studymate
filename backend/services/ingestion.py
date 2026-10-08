"""Ingestion pipeline: parse PDFs → chunk → embed → store in ChromaDB.
v2: block-based parsing with title extraction and footer stripping.

Design decisions (based on diagnostic of TF4507 lecture deck):
- Titles (top of slide) are extracted separately and kept as metadata,
  so sparse slides get a strong semantic anchor when embedded.
- Footers (course code + page numbers) are stripped — they would
  otherwise keep image-only slides alive as junk chunks.
- Image-only slides are skipped entirely (no body text to retrieve).
"""

import fitz  # pymupdf

# Classification thresholds, calibrated from the TF4507 deck diagnostic:
#   titles occupy y ≈ 43–96, footers occupy y ≈ 506–519.
# Kept as constants so they can be tuned per-deck later.
TITLE_MAX_Y = 100    # block ends above this line → it's a title
FOOTER_MIN_Y = 500   # block starts below this line → it's a footer


def _clean_text(text: str) -> str:
    """Light cleanup of extracted text. Heavy cleaning is a later TODO."""
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    lines = [" ".join(line.split()) for line in text.split("\n")]
    return "\n".join(lines).strip()


def parse_pdf(path: str) -> list[dict]:
    """Extract text from a slide-deck PDF, preserving page numbers.

    Uses block-level extraction and classifies each block by its
    vertical position: title (top), footer (bottom), or body.

    Returns:
        [{"page": 1, "title": "Revolution of Computer Systems",
          "text": "• From 1945 until ..."}, ...]

        Pages whose body is empty after footer stripping (image-only
        slides) are skipped, trading their page numbers for a cleaner
        chunk stream.
    """
    doc = fitz.open(path)
    pages = []

    for page_num, page in enumerate(doc, start=1):
        title = ""
        body_blocks = []

        for block in page.get_text("blocks"):
            x0, y0, x1, y1, block_text = block[0], block[1], block[2], block[3], block[4]
            text = block_text.strip()
            if not text:
                continue

            if y1 < TITLE_MAX_Y:
                # Title zone — take the first non-empty title block only
                if not title:
                    title = _clean_text(text)
            elif y0 > FOOTER_MIN_Y:
                # Footer zone — drop entirely (course code, page numbers)
                continue
            else:
                # Body zone — collect for joining
                body_blocks.append((y0, text))

        # Join body blocks top-to-bottom so reading order follows the slide
        body_blocks.sort(key=lambda b: b[0])
        body = _clean_text("\n".join(t for _, t in body_blocks))

        if not body:
            continue  # image-only slide: nothing to retrieve

        pages.append({"page": page_num, "title": title, "text": body})

    doc.close()
    return pages