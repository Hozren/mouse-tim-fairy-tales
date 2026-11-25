---
name: tim-story-production
description: Create a new unofficial illustrated children's story in the local «Мышонок Тим» project from a user premise, preserving the selected canon, the corpus-derived literary model, character continuity, scene-by-scene illustration coverage, project artifacts, and validated EPUB3 and PDF editions. Use for writing or rebuilding one complete story; do not use for corpus analysis alone or for editing original books in origin/.
---

# Tim Story Production

Produce one complete story under `generated/<story-slug>/` from the repository root. Treat `origin/` as read-only and never present the result as an official continuation or as a work by the original author.

Before writing:

1. Read `AGENTS.md`, `docs/artifact-registry.md`, and the relevant parts of `docs/literary-analysis.md`.
2. Choose one canon explicitly. For the Topo Tip canon use Tim, Lily, Teddy, family and the preschool world; never merge it with Diana Bulusheva's separate green-forest canon.
3. Preserve the user's premise and its concrete required beats. Ask only when a missing choice would materially change the story.
4. Read [references/production-workflow.md](references/production-workflow.md) and follow its literary, visual, artifact, and quality gates.

Create the text and scene plan before generating images. Build a visual character anchor first, then use it as a reference for the cover and every scene. Generate original compositions with the corpus's broad visual qualities; do not copy a published illustration or request imitation of a named illustrator.

Keep master images in `images/`. Create `book.json` only after text and scene numbering are final; its schema is in [references/book-json-schema.md](references/book-json-schema.md). Install `.github/requirements-build.txt`, then build the EPUB with:

```bash
python3 .skills/tim-story-production/scripts/build_epub.py \
  generated/<story-slug>
```

Build the PDF from the same manifest:

```bash
python3 .skills/tim-story-production/scripts/build_pdf.py \
  generated/<story-slug>
```

Both builders default to the repository’s ignored `_dist/<story-slug>/`. Publish EPUB/PDF through GitHub Releases using a `books-*` tag; do not commit publication binaries or ZIP duplicates. Preserve unpacked books in `origin/` for analysis; original EPUB archives are intentionally omitted.

The builders validate required metadata, scene/image alignment, internal references, ZIP integrity, the EPUB `mimetype` entry, the PDF header, and the PDF page count. Do not report completion until all literary, visual, artifact, EPUB, and PDF checks pass.

At the end, update `docs/artifact-registry.md` and the current state plus change log in `AGENTS.md`, as required by the project rules.
