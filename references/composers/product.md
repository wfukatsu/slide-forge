*[日本語](product.ja.md)*
# Composing Product Pages

The pages a product deck is made of: what the product is, how it is put
together, what it does, how it compares, and where it is going. Each entry says
what the page has to establish and what to build it from today.

All of them are figures on a page with no body placeholder, inside the safe
area `X0 / W` horizontally and `DY0`–`DY1` vertically (`deckkit`; 0.5–9.5in and
0.84–4.30in on a 16:9 template). Key points go on the `NY` line via `foot()`.

## Product overview

Establishes what the product *is* before any feature is named: the product
name, the one line that says what it does for whom, and three or four
capabilities that make that line true.

**Build it with**: `icon_row` or `cards` for the capabilities, with the tagline
as a `governing_message`. A `metric` earns its place only if the headline claim
is a number with a source.

Three or four capabilities. A six-capability overview is a feature list that
has not decided what matters.

## Architecture

Shows how the parts sit relative to each other — what is layered on what, and
what talks to what.

**Build it with**: `layers` when the story is "each layer rests on the one
below", `hub` for one centre and its integrations, `flow` / `icon_flow` for a
request path, and `cloud_icon_*` when the components are named cloud services
([cloud-icons.md](../cloud-icons.md)).

Once it exceeds roughly nine boxes it stops being readable as a slide figure:
draw it in draw.io, export the PNG, and put the PNG on the page with the points
to read off it (`architecture-exhibit`). See
[../../skills/drawio-diagrams/SKILL.md](../../skills/drawio-diagrams/SKILL.md).

**Run `audit_connectors()`** on any page with arrows — a connector whose
endpoint floats free of the box it points at is the single most common defect
here, and it is caught before generation.

## Feature matrix

Which editions or products have which capability. Its job is to be scanned, not
read.

**Build it with**: the `table` figure with ●/−/△ marks, or the
`license-pattern-compare` template when the axis is a licence pattern. Mind the
column widths: the audit measures cells in full-width equivalents and rejects
overruns.

Mark availability with a symbol *and* the word, never with colour alone.

## Feature detail

One capability, one page: what it does, what it is for, and what it costs to
adopt.

**Build it with**: a figure that matches the capability's own shape (see
[diagrams.md](../diagrams.md)), plus `foot()` for the takeaway and the
availability line (edition, GA/preview status). Preview-stage capabilities must
say so on the page.

## Technical specifications

The numbers a reader will check you on: supported versions, limits, throughput.

**Build it with**: the `table` figure, plus a `source_note` naming the document
and the date the numbers were read. A spec table with no date goes stale
silently.

## Competitive comparison

Where the product wins, in terms the customer already uses to decide.

**Build it with**: `comparison` for a few columns of like-for-like rows, or
`dense-comparison-table` when there are many criteria. `positioning-map` when
the argument is about two axes rather than a checklist.

State the evaluation criteria before the verdicts, and only claim what a public
source supports. A competitor's weakness with no citation does not go in a
customer-facing deck.

## Roadmap

What is coming, in what order, with how much certainty.

**Build it with**: `timeline` or `journey` for a sequence, `roadmap` (the
`nexus` template) for phases against workstreams, `gantt-schedule` when the
items have real dates.

Separate what is committed from what is intended, on the page. An unlabelled
roadmap is read as a promise.
