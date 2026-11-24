# Production workflow

Use this reference when creating a complete new story. It captures the reusable method only; no plot, prose, dialogue, or scene from an existing generated story belongs here.

## 1. Inputs and canon

Required input is a user premise. Extract the non-negotiable actions, characters, objects, tone, and setting before adding connective material.

Use the local corpus and `docs/literary-analysis.md` as evidence, not as text to imitate. Select one canon and keep its family, setting, and narrative assumptions consistent. The default for an ordinary request about Tim is the Topo Tip family canon. State another choice when the user requests it.

## 2. Literary design

Design one recognizable preschool conflict around a child's legitimate desire or difficult feeling. Use this dramatic movement:

1. Ordinary situation and clear child desire.
2. Impulsive choice, refusal, exaggeration, concealment, or overreach.
3. Escalation through concrete objects and actions.
4. Natural consequence that makes the problem visible without humiliation.
5. Adult or peer names the connection and offers bounded help.
6. The child makes the decisive choice or tries a reproducible method.
7. The method is tested in the world.
8. When natural, a mirror scene lets the child apply the method to someone else.

Keep the child imperfect and emotionally credible. Validate the feeling while holding boundaries around behavior. Prefer experience, repair, and agency over fear, shame, labels, bribes, instant conversion, or a moral spoken directly to the reader.

For this corpus, a practical target is roughly 700–1100 Russian words, dominated by short dialogue, concrete verbs, readable repetition, light sound effects, and details that can be illustrated. This is a target, not a quota; the premise controls the final length.

Edit aloud. Check that every speaker is clear, no paragraph carries several unrelated actions, the resolution follows from the conflict, and the ending shows changed behavior rather than merely announcing it.

## 3. Scene architecture

Create `scene-plan.md` before illustration. The established project default is one cover plus 17 story scenes; use 16–18 story scenes when the premise needs a slightly different rhythm. Do not pad the sequence to hit a number.

Each scene should contain one visually legible dramatic beat. Across the whole sequence include:

- invitation or setup;
- the child's choice;
- two or more escalation beats;
- peak inconvenience or conflict;
- admission of the real need;
- concrete helping method;
- child-led choice;
- real-world test;
- resolved family play or mirror application.

Number scenes continuously as `scene-01` through `scene-N`. Keep the same numbering in `scene-plan.md`, image filenames, `image-manifest.md`, and `book.json`.

## 4. Visual production

Create `images/character-anchor.png` first. Show every recurring character in a neutral full-body or three-quarter view, with explicit fur colors, proportions, clothing, signature objects, and relative heights. Approve the anchor before scene generation.

The default visual language is an original children's-book illustration with lively ink contours, watercolor or gouache washes, visible paper texture, warm pastel color, expressive kind faces, and cozy domestic detail. It may share these broad properties with the corpus but must not reproduce a published composition, page, or named illustrator's exact style.

Use the anchor as the primary image reference for the cover and every scene. Repeat only the continuity-critical facts in every prompt: character identity, proportions, current clothes, setting, action, emotion, camera framing, and required objects.

Defaults:

- cover: vertical, no printed title inside the image;
- story scene: horizontal 3:2;
- no words, letters, logos, signatures, or watermarks;
- no photorealism or 3D rendering;
- no extra characters or props that alter the story;
- warm comedy without visual humiliation.

After each image, inspect it rather than trusting the generation call. Verify character identity, action, object count, clothing continuity, emotional tone, anatomy, absence of text, and consistency with adjacent scenes. Regenerate only the failed scene, preserving the same anchor and continuity facts.

Keep lossless master images. For delivery EPUBs, JPEG derivatives around quality 85–90 are acceptable when PNGs exceed the messaging or reader size limit; never overwrite the masters.

## 5. Required story directory

Create at least:

```text
generated/<story-slug>/
|-- story.md
|-- scene-plan.md
|-- design-notes.md
|-- prompts.md
|-- image-manifest.md
|-- book.json
|-- images/
|   |-- character-anchor.png
|   |-- cover.png or cover.jpg
|   `-- scene-01.png ... scene-N.png
`-- <story-slug>.epub
```

`story.md` is the editorial master. `design-notes.md` records how corpus recommendations were applied and labels the work unofficial. `prompts.md` records the shared generation specification. `image-manifest.md` records actual filenames, dimensions, scene meaning, tool, and quality checks. `book.json` is the final assembly manifest; do not duplicate unfinished drafts into it.

## 6. EPUB assembly and verification

Use `scripts/build_epub.py` with the story directory. It produces EPUB3 with XHTML, CSS, OPF, navigation, NCX fallback, cover metadata, and all scene images.

Verify after building:

- ZIP test passes;
- `mimetype` is the first entry and is stored without compression;
- cover and every numbered scene image are present;
- OPF media types match actual extensions;
- every XHTML image reference resolves;
- scene count matches `scene-plan.md`, `image-manifest.md`, and `book.json`;
- text is readable in at least one EPUB reader when a reader is available;
- final file size is practical for the requested delivery channel.

Do not discard the original full-resolution EPUB merely because a smaller delivery variant is created.

## 7. Completion gate

Before reporting completion, confirm all of the following:

- the user's required premise beats are present;
- the story uses one canon only;
- the child's desire is respected and the consequence is natural;
- adult help does not erase child agency;
- the solution is concrete and tested;
- no explicit shaming moral replaces the dramatic resolution;
- cover, anchor, and every planned scene exist and were visually inspected;
- manifests and filenames agree;
- EPUB validation succeeds;
- project registry and change log are updated.

