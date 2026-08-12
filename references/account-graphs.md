*[日本語](account-graphs.ja.md)*

# Account graphs (influence map / discovery map)

## Table of contents

- What kind of diagram this is
- Data model
- What validation blocks
- Extraction (thinning for slides)
- draw.io output
- When to use which

## What kind of diagram this is

Two graphs used in B2B deals. **Both are produced from a single JSON, with the full graph
going to draw.io and the key subset going to a slide.** Using the same source data prevents
the two adjacent diagrams from disagreeing with each other.

- **Influence**: connects buying-committee participants via organizational structure,
  annotating role, influence level, stance, and whether a meeting has taken place
- **Discovery**: connects Goal / Strategy / Tactics via upward "supports" relationships. A
  single Tactic can support multiple Strategies (a multi-parent structure)

This is distinct from `influence-map` (`slide-templates/b2b-sales/`), which places people on
2 axes; that one shows positional relationships, while this one shows **structure**.

## Data model

```json
{
  "type": "influence",
  "title": "…",
  "people": [
    {"id": "kaneko", "roles": ["F", "C"], "org": "CFO", "name": "金子",
     "influence": "high", "stance": "close", "met": true,
     "reportsTo": "fukatsu", "note": "資金・経費についての相談役"}
  ],
  "links": [{"from": "a", "to": "b", "label": "二人で話し合って決めている"}]
}
```

| Field | Value | Rendering |
|---|---|---|
| `roles` | `F` buyer / `T` technical / `U` user / `C` coach / `S` supporting executive | Joined as `F/C` in the top band |
| `influence` | `champion` / `high` / `medium` / `low` | Bottom band |
| `stance` | `close` warm / `neutral` / `opposed` hostile | Body fill |
| `met` | `false` means not yet met | Whole card rendered dashed |
| `reportsTo` | Manager's `id` | Solid line up/down |
| `links` | Peer relationship / annotation | Labeled horizontal line |

```json
{
  "type": "discovery",
  "nodes": [{"id": "s1", "tier": "strategy", "text": "…", "owner": "COO"}],
  "edges": [{"from": "t1", "to": "s1"}]
}
```

`tier` is `goal` / `strategy` / `tactics`. `edges` run **from the supporting side to the
supported side**.

## What validation blocks

`account_graph.validate()` rejects the following. Always run it before generation.

- Duplicate `id` values, references to a nonexistent `id` (`reportsTo` / `edges` / `links`)
- Invalid enum values (role, influence, stance, tier)
- **Cycles** (`a -> b -> a`)
- **Downward edges** (`goal -> tactics`). Edges within the same tier are fine, and a
  lower-level goal supporting a higher-level one is valid.

## Extraction (thinning for slides)

`extract()` keeps only what fits on a slide. Default caps are influence 7 / discovery 8.

**Simply taking the top N breaks edges.** If an intermediate node is dropped, the edges
beyond it become dangling. So the extraction **always pulls in the ancestors** of the nodes it
keeps. The result may exceed the cap, but a readable diagram is prioritized over a strict cap.

On a tie at the cutoff, the whole tied group is dropped together. Showing only one sibling out
of a group with equal weight would make it read as if the unselected ones don't exist.

| Graph | Priority order |
|---|---|
| influence | Influence level → buyer role (`F`) → met → number of direct reports |
| discovery | Tier (goal > strategy > tactics) → number of things it supports |

Dropped nodes are listed on stdout. The slide should state explicitly: "See the draw.io
version for the other N people."

## draw.io output

```bash
.venv/bin/python scripts/build_account_graph.py <graph.json> --out out/x.drawio
.venv/bin/python scripts/build_account_graph.py <graph.json> --out out/key.drawio --extract
.venv/bin/python scripts/drawio_export.py out/x.drawio --out out/x.png --scale 2
```

A card is a **group + 3 cells** (band, body, band). Each card can be moved as a unit in
draw.io, and each part's fill is preserved.

**Attach edges to the body cell (`_b`), not the group.** The top/bottom bands are only
partial width (the tier badge is right-aligned, the influence/owner band is left-aligned), so
drawing a line from the group's outer bounding box's center makes it sprout from the empty
space beside a band, reading as "not connected." Only the body cell is drawn full-width. The
slide-side `influence_graph` / `outcome_tree` connect edges to the body box for the same
reason.

Layout is tiered. For influence, it's a tree by `reportsTo`, with parents centered over their
children. For discovery, tiers are determined by **graph depth, not the `tier` field**.
Mechanically assigning tiers by the `tier` field causes a lower-level goal that supports a
higher-level one to land in the same tier, making the edge run horizontally. `tier` only
determines the badge color.

Always visually inspect the exported PNG with Read.

## Placing on a slide

The extracted version is drawn from `influence-map-org` / `discovery-map-tree` in
`slide-templates/b2b-sales/`. The diagram parts are `influence_graph` / `outcome_tree`, which
paint the same 3-tier card as the draw.io version using the template's semantic palette
(warm = success colors, hostile = danger colors, tier = primary / warning / muted).

```bash
.venv/bin/python scripts/render_slide_template.py \
  --template influence-map-org --data out/<account>-key.json --out out/<account>-slide.json
```

## When to use which

| Situation | Output |
|---|---|
| Few participants/items | Draw directly on the slide |
| Many | Full graph in draw.io, extracted version on the slide |
| Showing the customer | **Show neither.** This is an internal document recording judgments about real individuals |
