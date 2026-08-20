---
name: settings
description: >-
  Read and change the slide-forge switches in config/settings.json through a
  short multiple-choice dialogue: whether Gemini generates images at all
  (imageGeneration), and whether the deliverable is Google Drive / Google
  Slides or a local folder as PowerPoint (output / localOutputDir). Shows the
  current values, asks with AskUserQuestion, writes via scripts/settings.py,
  then reads the result back.
  Triggers: "設定を変えたい", "設定を確認して", "画像生成をオフにして",
  "Gemini の画像生成を使わない", "出力先をローカルにして", "PowerPoint で出したい",
  "Google Drive に出したい", "slide-forge の設定", "settings", "change settings",
  "turn off AI images", "export locally instead".
  Out of scope: OAuth credentials and API keys (config/credentials.json,
  config/gemini_api_key — never read or write them here), the Drive sales root
  in config/sales.json (scalar-account-plan owns it), per-deck choices such as
  visual QA or template selection (those stay in intake), and exporting an
  existing deck (pptx-export).
---

*[日本語](SKILL.ja.md)*

# slide-forge Settings

Two switches live in `config/settings.json` and apply to every run, so they are
settled here once instead of being asked at every intake. The reference is
`references/settings.md`; this skill is the dialogue around it.

| Key | Values | Effect |
|---|---|---|
| `imageGeneration` | `true` / `false` | `false` refuses `aiImage` figures, `scripts/images.py`, and `fill_image_slots.py` — offline, before any quota is spent |
| `output` | `"google"` / `"local"` | `local` exports the deck to `.pptx` under `localOutputDir` after every generation |
| `localOutputDir` | path | where that `.pptx` goes (default `out/pptx`; relative to the repo root) |

## Important

- **Never touch anything else in `config/`.** `credentials.json`, `token.json`,
  and `gemini_api_key` are secrets; this skill only reads and writes
  `settings.json`, and never prints a key or token.
- **Show before you change, and read back after.** Every run starts with
  `--show` and ends with `--show`, so the user sees what changed.
- **Don't ask what the user already said.** "画像生成をオフにして" is a complete
  instruction — apply it, report it, and only ask about the other switch if
  they asked to review settings generally.
- **A change never touches an existing deck.** It affects the next generation.
  Say so when the user is mid-workflow.
- **Run every command from the slide-forge root as cwd** — `${CLAUDE_PLUGIN_ROOT}`
  when running from an installed plugin, `/path/to/slide-forge` on a local clone.

## Quick Reference

| Task | Command |
|------|---------|
| Show current values and where they come from | `.venv/bin/python scripts/settings.py --show` |
| Machine-readable | `.venv/bin/python scripts/settings.py --json` |
| Image generation off / on | `… scripts/settings.py --image-generation off` / `on` |
| Deliverable to a local `.pptx` | `… scripts/settings.py --output local` |
| Deliverable to Drive / Slides | `… scripts/settings.py --output google` |
| Change the local folder | `… scripts/settings.py --local-dir ~/decks` |

Flags combine in one call. Precedence, weakest first: defaults →
`config/settings.json` → `GSLIDES_IMAGE_GENERATION` / `GSLIDES_OUTPUT` /
`GSLIDES_LOCAL_DIR` → `build_deck.py --output`. If `--show` reports an
environment override, say so — the file the user is editing is not what that
run will use.

## Workflow

1. **Show the current values**, and quote them in the question descriptions so
   the user is choosing against a known state:

   ```bash
   .venv/bin/python scripts/settings.py --show
   ```

2. **Ask with `AskUserQuestion`** — one round, both switches, current value
   marked. Ask only about switches the user has not already decided:

   ```json
   {
     "questions": [
       {
         "header": "画像生成",
         "question": "Gemini による画像生成を使いますか？",
         "multiSelect": false,
         "options": [
           {"label": "使う（現在の設定）", "description": "aiImage 図・images.py・image-slots が使える。課金済みの GEMINI_API_KEY が要る（画像モデルは無料枠クォータが 0）"},
           {"label": "使わない", "description": "AI 画像を一切生成しない。aiImage は検証時に弾かれ、代わりに図形で描く illustrations / patterns を使う。API キーは不要"}
         ]
       },
       {
         "header": "出力先",
         "question": "成果物をどこに出しますか？",
         "multiSelect": false,
         "options": [
           {"label": "Google Drive / Google Slides（現在の設定）", "description": "生成したデッキの URL が成果物。共同編集・コメントができる。PPTX が要るときは pptx-export で個別に書き出す"},
           {"label": "ローカルフォルダ / PowerPoint", "description": "生成のたびに out/pptx へ .pptx を書き出す。デッキ自体は編集可能な原本として Drive に残る（削除はしない）"}
         ]
       }
     ]
   }
   ```

   Put the **current value first and label it 現在の設定**, so the safe answer
   is the top option. When "ローカルフォルダ" is chosen and the folder should
   not be `out/pptx`, ask the path in a follow-up question — the free-text
   "Other" answer is the path.

3. **Apply**, combining every change into one call:

   ```bash
   .venv/bin/python scripts/settings.py --image-generation off --output local
   ```

4. **Read back and report** — the file path, the resulting values, and what
   changes in practice. Two consequences are worth stating explicitly:

   - image generation off → propose `illustrations` / `patterns` /
     `diagrams` for visuals from now on; specs carrying `aiImage` will fail
     offline validation until they are rewritten;
   - output local → the PPTX question disappears from intake, generation
     prints a local path next to the deck URL, and visual QA still runs
     against the Slides deck (export is a snapshot: QA first, then export).

## When another skill sends the user here

The generation skills read these settings at intake
(`references/interactive-intake.md`) and drop the questions the settings
already answer. When a user asks to change one mid-workflow, run this skill,
then continue the interrupted workflow with the new values — no regeneration is
needed unless the deck was already built.
