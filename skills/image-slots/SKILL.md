---
name: image-slots
description: >-
  Fill the empty image slots of an **existing** Google Slides deck with
  AI-generated pictures: find the frames the template reserves for a picture
  (PICTURE-family placeholders, empty image elements left in a layout, frames
  the deck reuses), generate a picture composed for each frame's shape, and
  place it so it fills the frame. Runs standalone on any accessible deck URL,
  including decks slide-forge did not generate, and works without a registered
  template by analyzing the deck itself.
  Triggers: "表紙に絵を入れて", "章扉の画像枠を埋めて", "空いている画像枠に画像を生成",
  "このデッキに画像を足して", "image-slots", "fill the image placeholders",
  "generate images into the slots".
  Out of scope: decks still being generated from a deck spec (put `aiImage`
  in the spec and let build_deck.py fill the slot — see below), drawing
  diagrams with shapes (google-slides-template's figure families), replacing
  pictures that are already in place, and visual verification (slide-qa).
---

# Fill Image Slots on an Existing Deck

Working directory: the slide-forge root — `${CLAUDE_PLUGIN_ROOT}` when running
from an installed plugin, `/Users/wfukatsu/work/slide-forge` on a local clone.

## Important

- **Prefer the spec path when the deck is still being generated.** If the deck
  comes from a slide-forge deck spec, add an `aiImage` figure with `x`/`y`/`w`/`h`
  omitted and regenerate — `build_deck.py` puts it in the slot. That keeps the
  spec the source of truth, which is the repo's standing rule (see slide-qa:
  *fixes happen in the source, not the artifact*). **This skill is for decks
  that have no spec behind them**, or for adding imagery to a deck that already
  exists and must keep its URL.
- **This writes to a live deck.** Take a version snapshot first and report the
  revision ID:
  `.venv/bin/python scripts/snapshot_version.py <URL>`
- **Always `--dry-run` first** and show the user which slides and frames will be
  filled, with the prompt each one will use, before generating anything.
- **Slots that already hold a picture are never touched.** Replacing an existing
  picture is out of scope — delete it by hand first if that is the intent.
- **`GEMINI_API_KEY` is required** and the image model has **zero free-tier
  quota**; the key must belong to a billing-enabled project
  (`references/images.md`).
- **Verify with thumbnails afterwards.** A clean API response cannot show a
  picture whose subject got cropped. Hand off to the `slide-qa` skill.

## Quick Reference

| Task | Use |
|------|-----|
| List the fillable frames (no API image calls, no changes) | `.venv/bin/python scripts/fill_image_slots.py <URL> --dry-run` |
| Fill every empty frame | `.venv/bin/python scripts/fill_image_slots.py <URL>` |
| One slide, explicit subject | `… <URL> --slide 3 --prompt "夜間のデータセンター"` |
| Pick a frame when a slide has several | `… --slot 1` (0-based, in the order the survey lists them) |
| Change the illustration style | `--style isometric` (`flat_vector` / `line_art` / `blueprint` / `paper` / `photo`) |
| Snapshot before writing | `.venv/bin/python scripts/snapshot_version.py <URL>` |
| What a slot is, and how images are composed for it | `references/images.md` |

## How a frame is found

Same three sources as template registration (`references/template-schema.md`):

1. a **PICTURE-family placeholder** on the slide (`PICTURE` / `CLIP_ART` /
   `DIAGRAM` / `MEDIA` / `OBJECT` / `SLIDE_IMAGE`)
2. an **empty image element** on the slide — it renders as nothing, so it is a
   slot, not a decoration
3. otherwise the **layout's** `imageSlots`, largest frame first

Frames on the slide itself win over the layout's, because a slide that carries
its own placeholder is more specific than the layout it was made from. The
survey lists layout frames largest-first; frames found on the slide come in the
order the slide stores them, so read the `--dry-run` output rather than assuming
an order when picking `--slot`.

**A picture is layered over the frame, not poured into it.** An empty PICTURE
placeholder is not consumed — the image is created at the frame's coordinates
and the placeholder stays underneath. It renders as nothing, but it is still
there in the editor. The spec path (`build_deck.py`) behaves the same way.

Pass `--template templates/<id>.json` when the deck was generated from a
registered template — its verified roles and palette are then used. Without it
the deck is analyzed on the fly, so the skill works on **any** deck.

## What gets drawn

The prompt defaults to the slide's **own text**, read top-down and capped at 120
characters, so a section divider titled 第1章 データ基盤の刷新 asks for a picture
about that. Override per run with `--prompt`. A slide with **no text** is skipped
with a message rather than guessed at — pass `--prompt` for those.

The picture is generated for the frame's shape: the closest aspect ratio the
model supports, plus a prompt instruction naming the edges and percentage the
fill will crop, so the subject survives. It is then placed with `fit="cover"`,
exactly filling the frame. Details in `references/images.md`.

Generation is cached by (model, style, aspect, full prompt), so re-running does
not redraw or re-bill; `--force` overrides.

## Flow

1. **Snapshot** — `snapshot_version.py <URL>`; keep the revision ID for the report.
2. **Survey** — `fill_image_slots.py <URL> --dry-run`. Show the user the slide
   numbers, frames, and prompts. If everything is "already has a picture" or no
   frames exist, say so and stop — do not invent frames.
3. **Confirm subjects.** The auto-derived prompts come from slide text and are
   often literal. Offer to set `--prompt` per slide when the subject reads badly
   as a picture (long body text, numbers, product names).
4. **Fill** — run without `--dry-run`. Each placement prints the chosen aspect
   ratio and the composition note.
5. **QA** — invoke the `slide-qa` skill on the deck URL and check the pictures
   are not cropped through their subject and do not fight the layout's text.
6. **Report** — slides filled, the style used, the snapshot revision ID, and the
   deck URL.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `Nothing to fill` | Every frame already holds a picture, or the layouts reserve none. Check with `inspect_template.py <URL>`; place the image by coordinates via a deck spec instead |
| `skipped: no text on this slide to build a prompt from` | Title-less slide — pass `--prompt` |
| The picture's subject is cut off | The frame's ratio is far from anything the model can produce. Re-run that slide with `--prompt` describing a centred, simple subject, or `--force` for a different draw |
| `HTTP 429 / limit: 0` | The API key's project has no image quota — billing must be enabled |
| Picture looks stretched or letterboxed | Report it: frames are always filled with `cover`, so this means the fit-up pass failed (the run prints a warning when it cannot read the created image's size) |
