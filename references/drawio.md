*[日本語](drawio.ja.md)*
# draw.io (mxGraph XML) Diagram Reference

For the `drawio-diagrams` skill. Write `.drawio` files directly, then export them
to PNG with `scripts/drawio_export.py` and insert them into slides.
The styles documented here were rendering-verified via headless export as of 2026-08.

## When to use draw.io (vs. diagrams.py)

| | `diagrams.py` (native shapes) | draw.io → PNG |
|---|---|---|
| Good for | Conceptual diagrams / flows with a handful to a dozen or so elements | Cloud architecture, data-flow, and network diagrams with many nodes |
| Icons | Vendor icon images from assets | draw.io's built-in AWS/GCP/Azure-compliant shapes (including frames and groups) |
| Post-editing | Editable on the slide as individual shapes | PNG (a single flattened image), though the .drawio file itself can be handed off for editing in draw.io |
| Quality assurance | Geometric checks via validate_layout.py | Visual QA of the PNG only |

**Rule of thumb**: switch to draw.io for dense diagrams with 2+ levels of nested
containers (like VPC/subnet) or more than 10 nodes / 15 edges. When a slide has
too many shapes, both Slides API generation and QA become painful.

## File skeleton

```xml
<mxfile host="app.diagrams.net">
  <diagram id="d1" name="Page-1">
    <mxGraphModel dx="800" dy="600" grid="0" page="1" pageWidth="1169" pageHeight="826">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- ここに vertex / edge の mxCell を並べる -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

- The two mxCells `id="0"` and `id="1"` are the required base. Shapes hang off
  `parent="1"` (or a container's id)
- Coordinates are in px. **A container's child coordinates are relative to the
  parent's top-left**
- PNG export is cropped to the **bounding box of the drawn content**, so
  `pageWidth`/`pageHeight` are effectively irrelevant. The diagram's aspect ratio
  is determined entirely by the shape layout itself (roughly 16:9–2:1 fits well
  within a slide's body area)
- Since it's XML, escape `&` as `&amp;` and `<` as `&lt;`. Japanese labels are fine

## Verified style catalog

### AWS (aws4 resource icons)

```xml
<mxCell id="lambda" value="Lambda" style="sketch=0;outlineConnect=0;fontColor=#232F3E;fillColor=#ED7100;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.lambda;" vertex="1" parent="1">
  <mxGeometry x="120" y="180" width="78" height="78" as="geometry" />
</mxCell>
```

- Rendering-verified resIcons: `ec2` `s3` `lambda` `rds`. For others, always
  confirm the name first (see "Looking up shape names" below)
- Match `fillColor` to the AWS category color: Compute `#ED7100` / Storage
  `#7AA116` / Database `#C925D1` / Networking `#8C4FFF` / Security `#DD344C`
- Removing `aspect=fixed` distorts the icon. Standard size is 78x78

### AWS group frames (nested containers like VPC/subnet)

```xml
<mxCell id="vpc" value="VPC" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc2;strokeColor=#8C4FFF;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#AAB7B8;dashed=0;" vertex="1" parent="1">
  <mxGeometry x="60" y="60" width="500" height="360" as="geometry" />
</mxCell>
```

- Children should have `parent="vpc"` and be placed with **coordinates relative
  to the parent**. Nesting has been verified 2 levels deep: VPC → subnet →
  resource
- For a filled frame, use `grStroke=0;fillColor=#E6F6F7;` (the standard pattern
  for a subnet)
- Verified grIcons: `group_vpc2` `group_security_group`. Region frames etc.
  need to be confirmed

### GCP (gcp2 hexagon icons)

```xml
<mxCell id="gce" value="Compute Engine" style="sketch=0;fontColor=#5A6872;html=1;verticalLabelPosition=bottom;verticalAlign=top;align=center;shape=mxgraph.gcp2.hexIcon;prIcon=compute_engine;fillColor=#5184F3;strokeColor=none;" vertex="1" parent="1">
  <mxGeometry x="80" y="120" width="80" height="70" as="geometry" />
</mxCell>
```

- `prIcon` takes the name **without a prefix** (verified: `compute_engine`
  `cloud_storage`). Check existence by looking for `mxgraph.gcp2.<name>`
- Size is 80x70 (the hexagon's aspect ratio)

### Azure (azure2 SVG image shapes)

```xml
<mxCell id="vm" value="Azure VM" style="image;aspect=fixed;html=1;points=[];align=center;fontSize=12;image=img/lib/azure2/compute/Virtual_Machine.svg;labelBackgroundColor=none;verticalLabelPosition=bottom;verticalAlign=top;" vertex="1" parent="1">
  <mxGeometry x="520" y="120" width="68" height="65" as="geometry" />
</mxCell>
```

- `image=img/lib/azure2/<category>/<name>.svg` is a path bundled with the app.
  Verified: `compute/Virtual_Machine.svg` `databases/SQL_Database.svg`
- Set width/height to match the SVG's aspect ratio (use `aspect=fixed` to
  prevent distortion)

### Edges (connecting lines) and labels

```xml
<mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#232F3E;strokeWidth=2;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="lambda" target="rds">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
<mxCell id="e1lbl" value="SQL" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=11;" vertex="1" connectable="0" parent="e1">
  <mxGeometry x="-0.1" relative="1" as="geometry" />
</mxCell>
```

- **Always connect via `source`/`target` referencing shape ids** (freeform-coordinate
  edges are forbidden, the same discipline as diagrams.py)
- To fix the entry/exit points, use `exitX/exitY` `entryX/entryY` (relative
  position 0–1)
- For waypoints, add `<Array as="points"><mxPoint x="…" y="…"/></Array>` inside
  mxGeometry
- A label is a child vertex of the edge (`edgeLabel` style). `x` is the position
  along the line, from -1 to 1
- Dashed lines: `dashed=1;`. Bidirectional: `startArrow=classic;startFill=1;`

## Looking up shape names

All built-in shape names can be extracted from the app itself (requires an
installed copy of draw.io.app):

```bash
grep -ao 'mxgraph\.aws4\.[a-z0-9_]*'  /Applications/draw.io.app/Contents/Resources/app.asar | sort -u | grep -i <keyword>
grep -ao 'mxgraph\.gcp2\.[a-z0-9_]*'  /Applications/draw.io.app/Contents/Resources/app.asar | sort -u | grep -i <keyword>
grep -ao 'img/lib/azure2/[A-Za-z0-9_/]*\.svg' /Applications/draw.io.app/Contents/Resources/app.asar | sort -u | grep -i <keyword>
```

**Don't guess names.** A nonexistent resIcon/prIcon doesn't error out — it just
renders as a "plain colored square," which you can only catch with visual QA.

## Generic shapes (data-flow diagrams, ER-style boxes, etc.)

Plain mxGraph styles are sufficient for anything other than vendor icons:

```xml
<mxCell id="box1" value="正規化バッチ" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="140" height="50" as="geometry" />
</mxCell>
```

- Cylinder (DB): `shape=cylinder3;size=15;`. Document: `shape=document;`.
  A queue/stream is best approximated with a slim rounded rectangle
- Match colors to the deck's template colors (`colors` in template.json) so the
  diagram fits the slide

## Quality checklist (check with Read after PNG export)

- [ ] No element rendered as a plain colored square (wrong shape name)
- [ ] Labels don't overlap shapes/lines and aren't cut off mid-word
- [ ] Edges don't cross unrelated shapes, and connect to the semantically correct shape
- [ ] **Edge tips actually touch the shape.** Attaching `source`/`target` to a cell
      that bundles multiple sub-cells can leave the center empty when the outer
      frame is only a partial-width edge (e.g. a right-aligned badge, a
      left-aligned label band), leaving the arrow stopping in empty space.
      **Attach to the id of the full-width cell.** This isn't visible at reduced
      zoom, so check at full magnification
- [ ] Nested container children don't overflow
- [ ] Exported at scale 2 or higher, and text is legible once placed on a slide
      (as a rule of thumb, the diagram's width should be 1600px+ against an 8in
      insertion width)
