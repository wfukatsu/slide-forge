*[日本語](settings.ja.md)*
# Settings — `config/settings.json`

Two decisions that used to be re-made at every intake are settled once here and
then apply to every run:

| Key | Values | Default | What it controls |
|---|---|---|---|
| `imageGeneration` | `true` / `false` (`"on"` / `"off"` also accepted) | `true` | whether Gemini generates images at all — `aiImage` figures, `scripts/images.py`, `scripts/fill_image_slots.py` |
| `output` | `"google"` / `"local"` | `"google"` | where the deliverable lands: Google Drive / Google Slides, or a local folder as PowerPoint (`.pptx`) |
| `localOutputDir` | path | `"out/pptx"` | the folder used when `output` is `local`; a relative path resolves against the repo root |

`config/` is gitignored, so the file is per-checkout and never committed.
`config/settings.example.json` is the committed copy to start from. **The
defaults reproduce the behaviour the toolkit had before this file existed**, so
an absent `settings.json` changes nothing.

## Reading and changing them

The `settings` skill wraps all of this in a multiple-choice dialogue
(`/slide-forge:settings` on Claude Code, the `settings` skill elsewhere): it
shows the current values, asks, writes, and reads the result back. Reach for
the commands below when you already know what to set.

```bash
.venv/bin/python scripts/settings.py --show          # current values + where they come from
.venv/bin/python scripts/settings.py --json          # machine-readable

.venv/bin/python scripts/settings.py --image-generation off
.venv/bin/python scripts/settings.py --output local --local-dir ~/decks
```

Precedence, lowest to highest: **defaults → `config/settings.json` →
environment variables → command-line flag**.

```bash
GSLIDES_IMAGE_GENERATION=off  GSLIDES_OUTPUT=local  GSLIDES_LOCAL_DIR=~/decks
```

`build_deck.py` and `render_deck.py` take `--output google|local` for a single
run without touching the file. There is no per-run flag for image generation —
a deck that wants AI images either declares `aiImage` or does not.

From Python:

```python
import settings
settings.image_generation_enabled()      # bool
settings.output_target()                 # "google" | "local"
settings.local_output_dir()              # absolute path
```

## `imageGeneration: off`

Generation is refused at three points, each of them **before** anything is
spent or written:

- `images.generate()` raises `ImageGenerationError` — checked ahead of the
  cache lookup, because the switch is about whether AI imagery appears at all,
  not only about spending quota.
- `build_deck.py` rejects any `aiImage` figure during spec validation, so
  `--dry-run` reports it offline instead of a live run failing partway through
  a deck it has already created.
- `fill_image_slots.py` stops before reading the deck, since every slot it
  fills is AI-generated.

The shape-drawn alternatives — `scripts/illustrations.py`, `scripts/patterns.py`,
`scripts/diagrams.py` — are unaffected and need no API key. When the switch is
off, propose one of those instead of asking for a key.

## `output: local`

The engine always draws through the Google Slides API, so `local` is about the
**deliverable, not the build**. After a successful generation the deck is
exported to `.pptx` under `localOutputDir`, and the generated Slides deck is
deliberately left in place as the editable source — nothing is deleted for you.

```
generate (Slides API) → export .pptx → <localOutputDir>/<deck title>.pptx
                                        + the deck stays at its Drive URL
```

A failed export is reported, never fatal: the deck exists by then, and it can be
exported again with `scripts/export_pptx.py` (which writes into the same folder
when `--out` is omitted).

Visual QA (`slide-qa`) still runs against the Slides deck — thumbnails come from
the Slides API — so keep the QA-then-export order: an export is a snapshot, and
a regenerated deck needs re-exporting.

## What this means at intake

`references/interactive-intake.md` asks about the output format and about AI
imagery. **Read the settings first and don't ask what they already answer**:

- `output: local` → don't ask "also export to PowerPoint?"; it is already the
  deliverable. Report the local path along with the deck URL.
- `output: google` → the PPTX question stays as it is (asked only when PPTX
  delivery is expected).
- `imageGeneration: off` → don't offer `aiImage` and don't ask about the API
  key; offer the shape-drawn treatments instead.
