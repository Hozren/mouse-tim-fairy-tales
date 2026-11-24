# book.json assembly schema

Create this file only after the story and scene plan are final. It is an explicit bridge between the editorial text and the deterministic EPUB builder.

```json
{
  "title": "Book title",
  "creator": "Local project",
  "language": "ru",
  "identifier": "urn:uuid:replace-with-a-real-uuid",
  "slug": "lowercase-story-slug",
  "cover": "images/cover.png",
  "stylesheet": "epub.css",
  "scenes": [
    {
      "image": "images/scene-01.png",
      "alt": "Concise factual description of the image",
      "paragraphs": [
        "First paragraph of this scene.",
        "Second paragraph or dialogue."
      ]
    }
  ]
}
```

Required top-level fields are `title`, `creator`, `language`, `identifier`, `slug`, `cover`, and a non-empty `scenes` array. The optional `stylesheet` points to a CSS file inside the story directory; when omitted, the builder uses its own readable default.

Each scene requires `image`, `alt`, and a non-empty `paragraphs` array. Paths are relative to the story directory and must remain inside it. Images must be PNG, JPEG, GIF, or SVG. Use continuous filenames `scene-01` through `scene-N`; the builder checks this order.

Generate a UUID locally, for example:

```bash
python3 -c 'import uuid; print("urn:uuid:" + str(uuid.uuid4()))'
```

Do not put planning notes, prompts, or hidden instructions in `book.json`; only final book metadata and published scene text belong there.

