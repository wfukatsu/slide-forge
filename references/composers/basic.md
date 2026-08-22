*[日本語](basic.ja.md)*
# Composing the Structural Pages

The pages that hold a deck together rather than carry its argument: cover,
agenda, section divider, summary, closing, appendix. They are the ones a
template's own layouts already handle, so the rule for all of them is the same
— **use the placeholder layout, do not draw them**. A hand-drawn cover stops
following the master the moment the brand changes.

```python
plain(layout="COVER", title="…", subtitle="…", body="2026-08-22\n株式会社Scalar")
```

or, in a deck spec:

```json
{"layout": "COVER", "title": "…", "subtitle": "…", "body": "2026-08-22"}
```

Which role names a template offers is in `templates/<id>.json` and printed by
`list_templates.py`. The standard six are COVER / SECTION / CONTENT /
TITLE_ONLY / BLANK / CLOSING.

## Cover

Title, subtitle, and who is presenting on what date. The master owns the
background, the logo and the band; the deck supplies three strings.

**Build it with**: `layout="COVER"` — `title`, `subtitle`, `body` (presenter
and date, one per line).

Keep the title to one line. `deckkit.fits_one_line()` is the check
(`TITLE_EM_MAX`, 30.5 full-width equivalents at 20pt); a wrapped cover title
pushes into the subtitle.

## Agenda

The section structure as a numbered list, so the reader knows how long the
argument is. Worth a page from about eight slides on; below that it costs more
attention than it saves.

**Build it with**: `layout="CONTENT"` — `body` as a list, one section per line.
For a progress-marked agenda repeated at each divider, use `layout="SECTION"`
per section instead of dimming entries.

## Section divider

Section number and title, centered. Its job is the pause, not the information.

**Build it with**: `layout="SECTION"` — `title`, optional `body` for a
one-line description of what the section covers.

## Executive summary

The conclusion, before the argument. This one is *not* a placeholder page: it
carries structure, so it is a figure.

**Build it with**: the `exec_summary` figure (situation / complication /
resolution plus supporting points), or the `exec-summary-readable` slide
template for a read-alone document. See [slide-patterns.md](../slide-patterns.md).

## Closing

Logo and contact details. The master usually has this page already.

**Build it with**: `layout="CLOSING"`, no content. `deck.add_slide("CLOSING")`.

## Appendix divider

Marks where the main line of argument ends and the backup material begins.

**Build it with**: `layout="SECTION"`, title "Appendix". Anything the reader
must see to follow the argument does not belong behind it.
