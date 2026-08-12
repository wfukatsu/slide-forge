---
name: drawio-diagrams
description: >-
  Create dense, complex diagrams — cloud architecture (AWS/GCP/Azure), data
  flow, and network diagrams — as draw.io (.drawio) files, export them to PNG
  headlessly, QA them visually, and insert the PNG into Google Slides decks
  built with the slide-forge skills. The editable .drawio source is archived in
  the deck's Drive folder so the user can keep editing it in draw.io.
  Triggers: "draw.io で図を作って", "drawio", "クラウド構成図", "データフロー図",
  "ネットワーク構成図", "緻密な構成図", "cloud architecture diagram",
  "data flow diagram", or when a diagram is too dense for native Slides shapes.
---
*[日本語](SKILL.ja.md)*

# draw.io Diagrams for Google Slides

## Important

- **Scope**: diagrams too dense for `diagrams.py` native shapes — nested
  containers (VPC/subnet) 2+ levels deep, 10+ nodes, 15+ edges, or when
  official-style cloud vendor icons with group frames are wanted. For simple
  concept/flow figures, stay with `diagrams.py` in the `google-slides` skill.
  The routing table is at the top of `references/drawio.md`.
- **Working directory**: the slide-forge root — `${CLAUDE_PLUGIN_ROOT}` when running from an installed plugin, `/path/to/slide-forge` on a local clone (literal paths assume the local clone).
- **Requires the drawio desktop CLI** (`brew install --cask drawio`;
  `drawio` on PATH or the app bundle). Verified headless on macOS.
- **Visual QA of the exported PNG is mandatory.** A wrong shape name
  (`resIcon` / `prIcon` / azure2 SVG path) renders as a plain colored square
  with no error — never guess names; look them up
  (`references/drawio.md` § How to look up shape names).
- **Deliverables are three**: the slide with the PNG inserted, the exported
  PNG, and the editable `.drawio` source. Upload the `.drawio` and PNG into
  the deck's Drive folder (`scripts/drive_folder.py upload`) so the user can
  edit the diagram later — a PNG alone is a dead end.
- When inserting into **an existing deck the user already has**, run
  `scripts/snapshot_version.py <URL>` first (version-before-edit rule shared
  with the other slide-forge skills).

## Quick Reference

| Task | Where |
|------|-------|
| Authoring guide + verified style recipes (AWS/GCP/Azure, groups, edges) | `references/drawio.md` |
| Export .drawio to PNG | `.venv/bin/python scripts/drawio_export.py <in.drawio> [--out out/diagrams/x.png] [--scale 2]` |
| Look up shape names (never guess) | `grep -ao 'mxgraph\.aws4\.[a-z0-9_]*' /Applications/draw.io.app/Contents/Resources/app.asar \| sort -u` |
| Insert PNG into a deck spec | `{ "type": "image", "x": …, "y": …, "w": …, "h": …, "source": "out/diagrams/x.png", "fit": "contain" }` |
| Archive sources to the deck's Drive folder | `.venv/bin/python scripts/drive_folder.py upload <FOLDER> x.drawio out/diagrams/x.png` |
| Version snapshot before editing an existing deck | `.venv/bin/python scripts/snapshot_version.py <URL>` |

## Phase 0: Environment check

```bash
which drawio || ls /Applications/draw.io.app/Contents/MacOS/draw.io
```

If neither exists, ask the user to run `brew install --cask drawio`. The
Python side uses the shared slide-forge venv (`.venv`), same as the other
skills.

## Phase 1: Author the .drawio

Write the mxGraph XML directly, following `references/drawio.md`:

- File skeleton with the mandatory `id="0"` / `id="1"` root cells
- Coordinates in px; children of a container use parent-relative coordinates
- Vendor icons: AWS `resourceIcon` + `resIcon`, GCP `hexIcon` + `prIcon`,
  Azure `image=img/lib/azure2/…` — copy the verified recipes, look up any
  name you have not used before
- Edges always attach via `source`/`target` (never free coordinates), with
  `edgeLabel` child vertices for labels
- Aim the drawing bounds at the slide region's aspect ratio (16:9 to 2:1 for
  a full-body figure); PNG export crops to content, page size is irrelevant

Save the file next to the deck's spec (e.g. `<deck-dir>/figures/arch.drawio`).

## Phase 2: Export to PNG

```bash
.venv/bin/python scripts/drawio_export.py <deck-dir>/figures/arch.drawio \
    --out out/diagrams/arch.png --scale 2
```

`--scale 2` is the minimum for full-slide figures (target ≥ 1600px width for
an 8in insertion). `--transparent` for decks with tinted backgrounds;
`--page N` for multi-page files.

## Phase 3: Visual QA (mandatory)

Open the PNG with the Read tool and run the checklist at the bottom of
`references/drawio.md`: plain-square icons (wrong shape names), overlapping
labels, edges crossing unrelated shapes, children escaping containers,
legibility at insertion size. Fix the XML and re-export until clean.

## Phase 4: Insert into the deck

- **Spec path** (`build_deck.py`): add an `image` part pointing at the local
  PNG; use `fit: "contain"` and size the box to the PNG's aspect ratio.
- **Code-first path** (`deckkit`): `image(x, y, w, h, "out/diagrams/arch.png")`.
- **Existing deck**: snapshot the version first (`snapshot_version.py`), then
  insert with the API and renumber pages if needed
  (`references/code-blocks.md` shows the insertion pattern).

The generator uploads the PNG to Drive temporarily and cleans it up — the
slide keeps its own copy of the image.

## Phase 5: Archive sources in the deck's Drive folder

Every deck lives in its own Drive folder (see the Drive folder rule in the
generating skill). Put the diagram sources there too:

```bash
.venv/bin/python scripts/drive_folder.py upload <FOLDER_URL_OR_ID> \
    <deck-dir>/figures/arch.drawio out/diagrams/arch.png
```

Report the folder URL together with the deck URL, and mention that the
`.drawio` can be opened at app.diagrams.net or in the draw.io desktop app
for later edits.
