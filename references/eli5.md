*[日本語](eli5.ja.md)*

# ELI5 Mode — Decks a Newcomer Can Follow

ELI5 ("explain like I'm 5") is a **reading level**, not a layout. The deck
keeps its template, density and structure; what changes is how every page is
written. Use it when the audience has no background in the subject: a
non-technical executive, a new hire, a business-side stakeholder, a customer
seeing the product for the first time, a school class.

It is not a simplified *topic*. An ELI5 deck still says what is true — it
says it in words the audience already owns.

## Turning it on

Set it at the top of the deck spec:

```jsonc
{
  "title": "…",
  "readingLevel": "eli5",          // "standard" (default) or "eli5"
  "plainTerms": ["AI", "PC"],      // optional: acronyms this audience already knows
  "slides": [ … ]
}
```

or `assemble_spec.py --reading-level eli5` when assembling fragments. It
combines with either density; `presentation` suits it best (one message per
slide, large text).

## Writing rules

1. **One idea per slide.** The action title is that idea, in one short
   sentence a newcomer could repeat.
2. **Everyday words.** Prefer 「しまう・取り出す・確かめる」 to
   「永続化・参照・検証」; "store, fetch, check" to "persist, query, validate".
3. **Explain a term the first time it appears**, in brackets next to it:
   `API（ソフト同士の窓口）` or `ソフト同士の窓口（API）`. After that the
   term may be used bare. If a term isn't needed for the message, drop it.
4. **One analogy from daily life, kept consistent.** If the database is "a
   shared notebook" on slide 2, it stays a notebook to the end. Don't switch
   metaphors mid-deck.
5. **Say where the analogy stops.** A sales or technical deck must not let an
   analogy promise more than the product does. Give one slide (or one line)
   to 「たとえと違うところ」 / "where the analogy breaks".
6. **Make numbers concrete.** Turn an abstract figure into something the
   audience can picture or compare ("10,000 orders a second — every shopper
   in a full stadium paying at once"). Keep the source number in the notes.
7. **Picture before words.** Lead with a pictogram, a metaphor figure or a
   before/after, and let the body text name what the picture shows.
8. **Short sentences, at most three points**, one level deep. The detail an
   expert would want goes to the speaker notes, which the audit does not read.
9. **No "simply", "just", "obviously".** They tell the reader they should
   already have understood.

## Outline skeleton

When the user asks for an ELI5 explanation without a structure of their own,
offer this one at the outline gate. Show the chosen analogy next to each title
so the user can approve the metaphor as well as the structure:

| # | Page | What it does |
|---|---|---|
| 1 | Cover | The question the deck answers, in plain words |
| 2 | 「〜って、〜みたいなもの」 / "It's like …" | The analogy, with a picture |
| 3 | What goes wrong today | The problem in the analogy's terms |
| 4 | How it works | The mechanism as a 3–4 step picture |
| 5 | What gets better | One concrete example, numbers made tangible |
| 6 | Where the analogy breaks | The honest limit or caveat |
| 7 | In one sentence | The takeaway, plus the next step |

For 10+ slides, repeat 3–5 per sub-topic; never add a page that is only
detail.

## Figures that suit ELI5

- **Metaphor figures** from `illustrations` — `before_after`, `steps`,
  `balance`, `iceberg`, `journey`, `funnel`, `layers` (`diagrams.md`).
- **Pictograms** (`illustrations.py --list`) and Scalar pictograms
  (`icons.md`) next to every point.
- **A flow of at most four boxes.** A dense architecture diagram, a wide table
  or a code block belongs in a separate standard-level deck; link it from the
  last slide rather than appending it here (the audit reads every page).
- `aiImage` for the analogy's scene, when `imageGeneration` is on.

## What the dry-run checks

`build_deck.py --dry-run --strict` runs a reading-level audit on an ELI5 deck
(`scripts/reading_level.py`) and fails on any finding:

| Check | Limit |
|---|---|
| Acronym (2+ capitals: API, OCC, 2PC) not explained in brackets at its first use in the deck | — (`plainTerms` exempts) |
| Action title width | 30 full-width characters (an ASCII character counts as half) |
| Sentence width in a body | 40 full-width characters |
| Points in one body slot (headings don't count) | 3 |
| Indented sub-points | none |

Titles, subtitles, body lines and the visible text of figures are read;
speaker notes are not. What no script can judge — whether the analogy is apt,
consistent and honest — is settled at the outline approval gate and in visual
QA (`slide-qa`): read each page as the newcomer would.
