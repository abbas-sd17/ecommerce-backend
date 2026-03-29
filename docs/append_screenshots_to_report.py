"""
One-off: merge Scaler report template (parent folder) with docs/screenshots/*.png
Output: docs/Project_Report_Template_with_Screenshots.docx

Run from repo root:
  python docs/append_screenshots_to_report.py
"""
from pathlib import Path

from docx import Document
from docx.shared import Inches

ROOT = Path(__file__).resolve().parent.parent
DOCS = Path(__file__).resolve().parent
SHOTS = DOCS / "screenshots"
TEMPLATE = DOCS.parent.parent / (
    "Scaler Neovarsity _ Academy Project Report Template (Backend Specialization).docx"
)
OUT = DOCS / "Project_Report_Template_with_Screenshots.docx"

FIGURES = [
    (
        "Figure A1 — GET /api/products/ — product list (Lecture 1: DRF & serializers).",
        SHOTS / "01-api-products-list.png",
    ),
    (
        "Figure A2 — GET /api/products/filter/ — price range filter (Lecture 2: Q objects).",
        SHOTS / "02-api-products-filter.png",
    ),
    (
        "Figure A3 — Django administration — login.",
        SHOTS / "03-django-admin-login.png",
    ),
    (
        "Figure A4 — Django administration — registered models (Products, Payments, Users, …).",
        SHOTS / "04-django-admin-index.png",
    ),
    (
        "Figure A5 — GET /api/products/1/stock/ — stock check (Lecture 4: custom handling).",
        SHOTS / "05-api-product-stock.png",
    ),
    (
        "Figure A6 — GET /api/payments/ — payment list with idempotency & webhook fields "
        "(Lectures 8–9).",
        SHOTS / "06-api-payments-list.png",
    ),
]


def main() -> None:
    if not TEMPLATE.is_file():
        raise SystemExit(f"Template not found: {TEMPLATE}")
    for _, p in FIGURES:
        if not p.is_file():
            raise SystemExit(f"Missing screenshot: {p}")

    doc = Document(str(TEMPLATE))
    doc.add_page_break()
    doc.add_heading("Appendix — Project screenshots", level=1)
    doc.add_paragraph(
        "The following figures were captured from the local e-commerce backend "
        "(Django / Django REST Framework) at http://127.0.0.1:8000/."
    )

    for caption, path in FIGURES:
        doc.add_paragraph()
        p = doc.add_paragraph()
        r = p.add_run(caption)
        r.bold = True
        doc.add_picture(str(path), width=Inches(6.25))

    doc.save(str(OUT))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
