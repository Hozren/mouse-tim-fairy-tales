#!/usr/bin/env python3
"""Build and validate a small illustrated EPUB3 from book.json."""

from __future__ import annotations

import argparse
import html
import json
import mimetypes
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import quote

from PIL import Image, ImageOps


DEFAULT_CSS = """body { font-family: serif; line-height: 1.45; margin: 5%; }
h1 { text-align: center; }
p { text-indent: 1.2em; margin: 0.35em 0; }
figure { margin: 1.25em 0 0.8em; break-before: page; page-break-before: always; }
figure:first-of-type { break-before: auto; page-break-before: auto; }
img { display: block; max-width: 100%; max-height: 85vh; margin: 0 auto; }
figcaption { display: none; }
"""

IMAGE_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
}

DEFAULT_JPEG_QUALITY = 76
DEFAULT_MAX_IMAGE_DIMENSION = 1100


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def safe_source(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        fail(f"path escapes story directory: {relative}")
    if not candidate.is_file():
        fail(f"missing file: {relative}")
    return candidate


def xml_text(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_manifest(story_dir: Path) -> dict:
    manifest_path = story_dir / "book.json"
    if not manifest_path.is_file():
        fail(f"missing {manifest_path}")
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read book.json: {exc}")

    required = ("title", "creator", "language", "identifier", "slug", "cover", "scenes")
    for key in required:
        if not data.get(key):
            fail(f"book.json field is required: {key}")
    if not isinstance(data["scenes"], list) or not data["scenes"]:
        fail("scenes must be a non-empty array")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", data["slug"]):
        fail("slug must contain lowercase ASCII letters, digits, and hyphens")

    rendering = data.get("rendering", {})
    if not isinstance(rendering, dict):
        fail("rendering must be an object")
    quality = rendering.get("jpeg_quality", DEFAULT_JPEG_QUALITY)
    max_dimension = rendering.get("max_image_dimension", DEFAULT_MAX_IMAGE_DIMENSION)
    if isinstance(quality, bool) or not isinstance(quality, int) or not 60 <= quality <= 95:
        fail("rendering.jpeg_quality must be an integer from 60 to 95")
    if (
        isinstance(max_dimension, bool)
        or not isinstance(max_dimension, int)
        or not 800 <= max_dimension <= 4000
    ):
        fail("rendering.max_image_dimension must be an integer from 800 to 4000")
    data["rendering"] = {
        "jpeg_quality": quality,
        "max_image_dimension": max_dimension,
    }

    safe_source(story_dir, data["cover"])
    for index, scene in enumerate(data["scenes"], start=1):
        if not isinstance(scene, dict):
            fail(f"scene {index} must be an object")
        for key in ("image", "alt", "paragraphs"):
            if not scene.get(key):
                fail(f"scene {index} field is required: {key}")
        if not isinstance(scene["paragraphs"], list) or not all(
            isinstance(item, str) and item.strip() for item in scene["paragraphs"]
        ):
            fail(f"scene {index} paragraphs must be non-empty strings")
        expected = f"scene-{index:02d}"
        if Path(scene["image"]).stem != expected:
            fail(f"scene {index} image must be named {expected}.*")
        safe_source(story_dir, scene["image"])
    return data


def image_media_type(path: Path) -> str:
    media_type = IMAGE_TYPES.get(path.suffix.lower())
    if not media_type:
        guessed, _ = mimetypes.guess_type(path.name)
        fail(f"unsupported image type {path.suffix!r} ({guessed or 'unknown'})")
    return media_type


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def write_jpeg_derivative(
    source: Path,
    destination: Path,
    max_dimension: int,
    quality: int,
) -> Path:
    with Image.open(source) as raw:
        image = ImageOps.exif_transpose(raw)
        image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        if image.mode in ("RGBA", "LA") or "transparency" in image.info:
            rgba = image.convert("RGBA")
            background = Image.new("RGB", rgba.size, "white")
            background.paste(rgba, mask=rgba.getchannel("A"))
            image = background
        else:
            image = image.convert("RGB")
        image.save(
            destination,
            format="JPEG",
            quality=quality,
            optimize=True,
            progressive=True,
        )
    return destination


def prepare_epub_image(source: Path, target_stem: Path, data: dict) -> Path:
    if source.suffix.lower() in {".png", ".jpg", ".jpeg"}:
        rendering = data["rendering"]
        return write_jpeg_derivative(
            source,
            target_stem.with_suffix(".jpg"),
            rendering["max_image_dimension"],
            rendering["jpeg_quality"],
        )
    destination = target_stem.with_suffix(source.suffix.lower())
    shutil.copy2(source, destination)
    return destination


def build(story_dir: Path, output: Path) -> None:
    data = load_manifest(story_dir)
    with tempfile.TemporaryDirectory(prefix="tim-story-epub-") as temp_name:
        root = Path(temp_name)
        epub = root / "EPUB"
        media = epub / "media"
        text_dir = epub / "text"
        styles = epub / "styles"
        media.mkdir(parents=True)
        text_dir.mkdir(parents=True)
        styles.mkdir(parents=True)

        write_text(root / "mimetype", "application/epub+zip")
        write_text(
            root / "META-INF/container.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="EPUB/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>
""",
        )

        css_source = data.get("stylesheet")
        css = safe_source(story_dir, css_source).read_text(encoding="utf-8") if css_source else DEFAULT_CSS
        write_text(styles / "book.css", css)

        cover_source = safe_source(story_dir, data["cover"])
        cover_target = prepare_epub_image(cover_source, media / "cover", data)
        cover_name = cover_target.name
        cover_type = image_media_type(cover_target)

        assets: list[tuple[str, str, str]] = []
        scene_markup: list[str] = []
        for index, scene in enumerate(data["scenes"], start=1):
            source = safe_source(story_dir, scene["image"])
            target = prepare_epub_image(source, media / f"scene-{index:02d}", data)
            target_name = target.name
            assets.append((f"scene-image-{index:02d}", f"media/{target_name}", image_media_type(target)))
            paragraphs = "\n".join(f"<p>{xml_text(p)}</p>" for p in scene["paragraphs"])
            scene_markup.append(
                f'<section id="scene-{index:02d}"><figure>'
                f'<img src="../media/{quote(target_name)}" alt="{xml_text(scene["alt"])}"/>'
                f'<figcaption>{xml_text(scene["alt"])}</figcaption></figure>{paragraphs}</section>'
            )

        title = xml_text(data["title"])
        language = xml_text(data["language"])
        write_text(
            text_dir / "cover.xhtml",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" lang="{language}"><head>
<title>{title}</title><link rel="stylesheet" href="../styles/book.css"/></head>
<body><figure><img src="../media/{quote(cover_name)}" alt="{title}"/></figure></body></html>
""",
        )
        write_text(
            text_dir / "story.xhtml",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" lang="{language}"><head>
<title>{title}</title><link rel="stylesheet" href="../styles/book.css"/></head>
<body><h1>{title}</h1>{''.join(scene_markup)}</body></html>
""",
        )
        write_text(
            epub / "nav.xhtml",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{language}"><head><title>{title}</title></head>
<body><nav epub:type="toc"><h1>Содержание</h1><ol><li><a href="text/story.xhtml">{title}</a></li></ol></nav></body></html>
""",
        )
        write_text(
            epub / "toc.ncx",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head><meta name="dtb:uid" content="{xml_text(data['identifier'])}"/></head>
<docTitle><text>{title}</text></docTitle><navMap><navPoint id="story" playOrder="1"><navLabel><text>{title}</text></navLabel><content src="text/story.xhtml"/></navPoint></navMap></ncx>
""",
        )

        asset_manifest = "\n".join(
            f'    <item id="{item_id}" href="{xml_text(href)}" media-type="{media_type}"/>'
            for item_id, href, media_type in assets
        )
        write_text(
            epub / "content.opf",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id" xml:lang="{language}">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="book-id">{xml_text(data['identifier'])}</dc:identifier><dc:title>{title}</dc:title>
    <dc:creator>{xml_text(data['creator'])}</dc:creator><dc:language>{language}</dc:language>
    <meta property="dcterms:modified">2000-01-01T00:00:00Z</meta><meta name="cover" content="cover-image"/>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="css" href="styles/book.css" media-type="text/css"/>
    <item id="cover-page" href="text/cover.xhtml" media-type="application/xhtml+xml"/>
    <item id="story" href="text/story.xhtml" media-type="application/xhtml+xml"/>
    <item id="cover-image" href="media/{xml_text(cover_name)}" media-type="{cover_type}" properties="cover-image"/>
{asset_manifest}
  </manifest>
  <spine toc="ncx"><itemref idref="cover-page"/><itemref idref="story"/></spine>
</package>
""",
        )

        output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output, "w") as archive:
            archive.write(root / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
            for path in sorted((root / "META-INF").rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(root), compress_type=zipfile.ZIP_DEFLATED)
            for path in sorted(epub.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(root), compress_type=zipfile.ZIP_DEFLATED)

    validate(output, len(data["scenes"]))


def validate(output: Path, scene_count: int) -> None:
    with zipfile.ZipFile(output) as archive:
        bad = archive.testzip()
        if bad:
            fail(f"corrupt ZIP member: {bad}")
        entries = archive.infolist()
        if not entries or entries[0].filename != "mimetype":
            fail("mimetype is not the first ZIP entry")
        if entries[0].compress_type != zipfile.ZIP_STORED:
            fail("mimetype must be stored without compression")
        if archive.read("mimetype") != b"application/epub+zip":
            fail("invalid mimetype contents")
        names = set(archive.namelist())
        required = {"META-INF/container.xml", "EPUB/content.opf", "EPUB/nav.xhtml", "EPUB/text/story.xhtml"}
        missing = sorted(required - names)
        if missing:
            fail(f"missing EPUB members: {', '.join(missing)}")
        story = archive.read("EPUB/text/story.xhtml").decode("utf-8")
        for index in range(1, scene_count + 1):
            if f'id="scene-{index:02d}"' not in story:
                fail(f"scene {index:02d} missing from story.xhtml")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("story_dir", type=Path, help="directory containing book.json and images")
    parser.add_argument("--output", type=Path, help="output EPUB path")
    args = parser.parse_args()

    story_dir = args.story_dir.resolve()
    if not story_dir.is_dir():
        fail(f"not a directory: {story_dir}")
    data = load_manifest(story_dir)
    output = args.output.resolve() if args.output else story_dir / f"{data['slug']}.epub"
    build(story_dir, output)
    print(f"built: {output}")
    print(f"size: {output.stat().st_size} bytes")
    print(f"scenes: {len(data['scenes'])}")


if __name__ == "__main__":
    main()
