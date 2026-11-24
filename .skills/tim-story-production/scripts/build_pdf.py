#!/usr/bin/env python3
"""Build and validate an illustrated PDF from book.json."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from fpdf import FPDF
from PIL import Image
from pypdf import PdfReader

from build_epub import fail, load_manifest, safe_source, write_jpeg_derivative


FONT_CANDIDATES = (
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"),
    Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
)


def find_font(explicit: Path | None) -> Path:
    candidates = (explicit,) if explicit else FONT_CANDIDATES
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate.resolve()
    fail("no Unicode TTF font found; pass --font /path/to/font.ttf")


def fitted_size(image_path: Path, max_width: float, max_height: float) -> tuple[float, float]:
    with Image.open(image_path) as image:
        width, height = image.size
    if width <= 0 or height <= 0:
        fail(f"invalid image dimensions: {image_path}")
    scale = min(max_width / width, max_height / height)
    return width * scale, height * scale


def place_centered_image(pdf: FPDF, image_path: Path, max_height: float) -> None:
    max_width = pdf.w - pdf.l_margin - pdf.r_margin
    width, height = fitted_size(image_path, max_width, max_height)
    x = (pdf.w - width) / 2
    pdf.image(str(image_path), x=x, y=pdf.get_y(), w=width, h=height)
    pdf.set_y(pdf.get_y() + height)


def build(story_dir: Path, output: Path, font_path: Path) -> None:
    data = load_manifest(story_dir)
    pdf = FPDF(format="A4", unit="mm")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_title(data["title"])
    pdf.set_author(data["creator"])
    pdf.set_creator("tim-story-production")
    pdf.add_font("Story", fname=str(font_path))

    with tempfile.TemporaryDirectory(prefix="tim-story-pdf-") as temp_name:
        temp_dir = Path(temp_name)
        pdf.add_page()
        pdf.set_font("Story", size=18)
        pdf.multi_cell(0, 9, data["title"], align="C")
        pdf.ln(5)
        rendering = data["rendering"]
        cover = write_jpeg_derivative(
            safe_source(story_dir, data["cover"]),
            temp_dir / "cover.jpg",
            rendering["max_image_dimension"],
            rendering["jpeg_quality"],
        )
        place_centered_image(pdf, cover, max_height=230)

        for index, scene in enumerate(data["scenes"], start=1):
            pdf.add_page()
            source = safe_source(story_dir, scene["image"])
            image_path = write_jpeg_derivative(
                source,
                temp_dir / f"scene-{index:02d}.jpg",
                rendering["max_image_dimension"],
                rendering["jpeg_quality"],
            )
            place_centered_image(pdf, image_path, max_height=145)
            pdf.ln(5)
            pdf.set_font("Story", size=11)
            for paragraph in scene["paragraphs"]:
                pdf.multi_cell(0, 6, paragraph)
                pdf.ln(2)

        output.parent.mkdir(parents=True, exist_ok=True)
        pdf.output(str(output))
    validate(output, minimum_pages=len(data["scenes"]) + 1)


def validate(output: Path, minimum_pages: int) -> None:
    if not output.is_file() or output.stat().st_size < 1024:
        fail("PDF was not created or is unexpectedly small")
    if output.read_bytes()[:5] != b"%PDF-":
        fail("output does not have a PDF header")
    try:
        reader = PdfReader(str(output))
        page_count = len(reader.pages)
    except Exception as exc:
        fail(f"cannot parse generated PDF: {exc}")
    if page_count < minimum_pages:
        fail(f"PDF has {page_count} pages; expected at least {minimum_pages}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("story_dir", type=Path, help="directory containing book.json and images")
    parser.add_argument("--output", type=Path, help="output PDF path")
    parser.add_argument("--font", type=Path, help="Unicode TTF font")
    args = parser.parse_args()

    story_dir = args.story_dir.resolve()
    if not story_dir.is_dir():
        fail(f"not a directory: {story_dir}")
    data = load_manifest(story_dir)
    output = args.output.resolve() if args.output else story_dir / f"{data['slug']}.pdf"
    font_path = find_font(args.font.resolve() if args.font else None)
    build(story_dir, output, font_path)
    print(f"built: {output}")
    print(f"size: {output.stat().st_size} bytes")
    print(f"scenes: {len(data['scenes'])}")


if __name__ == "__main__":
    main()
