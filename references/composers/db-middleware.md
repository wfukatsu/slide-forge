*[日本語](db-middleware.ja.md)*
# Composing Database and Middleware Pages

The four pages a data-infrastructure product keeps needing: where the data
goes, what it runs on, how fast it is, and how you get from what you have now
to it. Each entry says what the page has to establish and what to build it from
today.

## Data flow

Source → processing → store → output, with the direction made explicit. This is
the page a data-infrastructure deck is judged on: if the reader cannot trace
one record through it, nothing later lands.

**Build it with**: `flow` for a plain sequence, `icon_flow` when each stage has
an actor worth a pictogram (`database`, `server`, `bot`), `layers` when the
story is layering rather than movement. `d.link(a, b)` connects two shapes edge
to edge rather than centre to centre.

**Run `audit_connectors()`.** Endpoints that float free of the box they point
at are the characteristic defect of this page, and they are caught at
coordinate time.

Label the arrows, not just the boxes. An unlabelled arrow leaves the reader to
guess whether it carries data, a call, or a dependency.

## Multi-cloud configuration

The same product across AWS / GCP / Azure, or across on-premises and cloud —
showing what is identical and what differs per environment.

**Build it with**: `cloud_zone` to bound each environment and `cloud_icon_row`
/ `cloud_icon_grid` for the named services inside it. Service names and vendor
icons come from `cloud_icons.py --search <term>`; see
[cloud-icons.md](../cloud-icons.md).

Use one colour per vendor consistently across the deck, and put what is common
to all environments in one band rather than repeating it three times.

## Benchmark and performance

Numbers that stand up to being checked.

**Build it with**: `hbars` for a comparison of a few figures, `vbars_grouped`
when there are two dimensions, `linechart` for a curve against load.

The measurement conditions belong on the same page as the result — hardware,
dataset, concurrency, version, date — via `source_note`. A benchmark figure
without them is not usable in front of a technical audience, and no validator
will tell you it is missing.

Do not present a competitor benchmark you did not run under conditions you can
state.

## Migration path

From the system that exists to the one being proposed, in phases, with what is
running in parallel at each point.

**Build it with**: `steps` or `flow` for the phases, `before_after` for the
end-state contrast, `gantt-schedule` when the phases have dates, `roadmap`
when several workstreams run at once.

Two things carry this page and are usually missing: what runs in parallel
during each phase, and the point of no return. A migration plan without a
rollback position is not a plan a customer's operations team can approve.
