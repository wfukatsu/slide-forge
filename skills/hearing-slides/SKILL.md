---
name: hearing-slides
description: >-
  Build slides whose job is to collect information rather than deliver it — the
  agenda of what you need to hear, our understanding put up to be corrected, a
  fill-in sheet to write on during the meeting, a "does this apply to you"
  poll for an event or a talk, and the page that says where to send the answers
  (with a QR). Use when asked to 「聞くためのスライド」「ヒアリング用の資料」
  「足りない情報を集めるスライド」「イベントで情報を集めたい」「アンケートの
  スライド」「記入してもらう資料」. Driven by the gaps in a hearing sheet
  (`hearing-sheet`); it never invents an answer to fill a page. Internal
  "who do we ask next" pages are `scalar-ae-materials` / `b2b-account-maps`,
  and the proposal itself is `scalar-proposal-slides`.
---

*[日本語](SKILL.ja.md)*

# Hearing Slides — pages that collect

Read `references/hearing-kit.md` first (record, customer filter, where answers
may be stored) and `references/scalar/workflow-contract.md` for the shared
generation, QA and delivery rules. **This skill does not restate either.**

Working directory: the slide-forge root. Run everything with `.venv/bin/python`.

## What makes these pages different

A proposal page asserts. **These pages leave a hole and ask the customer to
fill it.** The hole is real — it comes from `hearing.json`, where the answer is
still `未確認` or `推定`.

- **Never fill a hole with a guess to make the page look finished.** A builder
  that has no material refuses to build the page (exit 2); take that as the
  answer, not as an error to work around.
- Everything here is customer-facing, so it is built only from what survives
  the customer filter. Internal sections and the source/confidence columns
  never reach a slide.
- **Say what the customer gets back.** Collecting without returning anything
  teaches people not to answer next time.

## Boundaries

| Request | Where it goes |
|---|---|
| Slides that ask the customer / an audience for information | This skill |
| The sheet itself, and reading the answers back | `hearing-sheet` |
| Internal "who do we ask, by when" (`discovery-gaps`) | `scalar-ae-materials` / `b2b-account-maps` |
| A conversation-opening challenge hypothesis (`challenge-hypothesis`) | `scalar-ae-materials` |
| Proposal, PoC plan, quotation | `scalar-proposal-slides` / `spreadsheets` |
| Event segments and nurture tracks | `scalar-nurture-intake` |

`discovery-gaps` and this skill's `hearing-agenda` look similar and are not.
`discovery-gaps` is **internal**: it assigns each gap to a counterpart and a
date. `hearing-agenda` is **shown to the customer** and asks them directly.
Do not put one in the other's folder.

## The pages

| Template | The moment it is for | Built from |
|---|---|---|
| `hearing-agenda` | Opening a meeting: here is what we need to hear and why | `未確認` questions, ticked ones first |
| `hypothesis-check` | Mid-meeting: our understanding, put up to be corrected | questions whose confidence is `推定` |
| `fill-in-sheet` | In the room: blank rows to write on (print / screen share) | `未確認` questions in the chosen section |
| `event-poll` | A talk or a seminar: which of these is you? | a nurture segment's situations (`templates/nurture/segment-sheet.ja.md` §1) |
| `collect-cta` | Closing: where to send answers, and what comes back | `meta.renders.gsheet`, or `--where` |
| `collect-qr` | An event close: the same, as a QR to scan | as above, plus `scripts/hearing/qr.py` |

## Step 1: See what is actually open

```bash
.venv/bin/python scripts/hearing/hearing_sheet.py gaps <hearing.json> [--section 4]
```

Choose pages from what is there, not from the list above:

- Nothing `推定` → **no `hypothesis-check`.** There is no understanding to
  correct yet, and inventing one to fill the page is the exact failure this
  skill exists to prevent.
- Fewer than three `未確認` → the sheet is nearly done; a whole deck of asking
  is the wrong artifact. Say so and offer the one page that fits.
- More than one section open → ask with `--section` rather than mixing an
  infrastructure question into a budget page.

## Step 2: Build the data, then the pages

```bash
.venv/bin/python scripts/hearing/hearing_slots.py <hearing.json> hearing-agenda \
    --out out/<customer>/agenda.json --section 4
.venv/bin/python scripts/render_slide_template.py --template hearing-agenda \
    --data out/<customer>/agenda.json --out out/<customer>/agenda.slide.json
```

The generated wording is a **starting point, not the deliverable**. Rewrite
`title` and `lead` to the customer's own situation and vocabulary before
assembling — a page that reads as a form letter gets form-letter answers.

For a QR page, make the image first and check where it points:

```bash
.venv/bin/python scripts/hearing/qr.py "<answer URL>" --out out/<customer>/qr.png
```

Without `qrcode` installed this writes a clearly marked placeholder and exits 2.
**Do not put the placeholder in front of a customer** — either install
`qrcode[pil]` or use `collect-cta`, which carries the URL as text.

## Step 3: Assemble, validate, generate

```bash
.venv/bin/python scripts/assemble_spec.py out/<customer>/*.slide.json \
    --out out/<customer>/deck.json --title "<資料名>"
.venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
    --spec out/<customer>/deck.json --dry-run --strict
```

Fix the **data** when the audit fires — shorten the wording, drop a row — never
the template. Then generate into `01_顧客提示` (a page that asks the customer
is customer-facing material) and follow the shared contract's QA and cleanup.

## Step 4: Close the loop

A collection page that never gets read back is decoration. In the report, say:

1. Which pages were built, and which were refused for lack of material
2. What each page is asking for, and which sheet IDs it covers
3. **How the answers come back** — `hearing-sheet`'s `read`, with the baseline
   kept before the sheet went out
4. What is still open after this deck, and who can answer it

Event answers aggregate to type and count before they go anywhere near
`accounts/_nurture/`; anything that identifies a company is a deal, not a
segment (`references/hearing-kit.md` §4).

## Files

| Path | Role |
|---|---|
| `slide-templates/hearing/` | the six page templates and their examples |
| `scripts/hearing/hearing_slots.py` | hearing.json → slot data (refuses thin pages) |
| `scripts/hearing/qr.py` | the QR for a collect page (optional `qrcode`) |
| `references/hearing-kit.md` | shared rules with `hearing-sheet` |
