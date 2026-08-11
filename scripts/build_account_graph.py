#!/usr/bin/env python3
"""Write an account graph to a .drawio file.

    .venv/bin/python scripts/build_account_graph.py <graph.json> --out out/x.drawio
    .venv/bin/python scripts/drawio_export.py out/x.drawio --out out/x.png --scale 2

Use this when the graph has more people or items than a slide can hold. The
slide shows the extracted subset (`--extract` prints what that would be); the
.drawio carries everything and stays editable.

Each card is a group of three cells — role band, body, influence band — so the
card moves as one in draw.io but every part keeps its own fill. Edges attach to
the group id, per the rule in references/drawio.md that an edge must have a
real source and target rather than free coordinates.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import account_graph as ag

ROOT = Path(__file__).resolve().parents[1]

# 参照デザインに合わせた配色。塗りは立場、破線は未面談を表す。
STANCE_FILL = {"close": "#FDE9D9", "opposed": "#DCE6F1", "neutral": "#FFFFFF"}
TIER_FILL = {"goal": "#F8CECC", "strategy": "#FFE6CC", "tactics": "#FFF2CC"}
TIER_STROKE = {"goal": "#B85450", "strategy": "#D79B00", "tactics": "#D6B656"}
BAND = "#EDEDED"
LINE = "#666666"
LINE_SOFT = "#9E9E9E"

CARD_W, CARD_H = 170, 74
BAND_H, FOOT_H = 18, 18
GAP_X, GAP_Y = 34, 62

# entity 別レイアウト（--layout grouped）。木レイアウトは根が多いと横に伸びて
# 読めなくなるので、法人ごとの枠に区切って格子に並べる
G_CARD_W, G_CARD_H = 190, 76
G_GAP_X, G_GAP_Y = 26, 30
G_PAD, G_HEAD = 24, 34
G_COLS = 4
GUTTER = 210            # 左の余白。人のつながりの線はここを通す
MARK = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫"
LINK = "#B85450"


def _esc(s: str) -> str:
    return escape(str(s)).replace("\n", "&#10;")


class Doc:
    def __init__(self) -> None:
        self.cells: list[str] = []

    def group(self, cid: str, x: int, y: int, w: int, h: int,
              parent: str = "1") -> None:
        self.cells.append(
            f'<mxCell id="{cid}" value="" style="group" vertex="1" connectable="0" '
            f'parent="{parent}"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" '
            f'as="geometry" /></mxCell>')

    def box(self, cid: str, parent: str, value: str, style: str,
            x: int, y: int, w: int, h: int) -> None:
        self.cells.append(
            f'<mxCell id="{cid}" value="{_esc(value)}" style="{style}" vertex="1" '
            f'parent="{parent}"><mxGeometry x="{x}" y="{y}" width="{w}" '
            f'height="{h}" as="geometry" /></mxCell>')

    def edge(self, cid: str, src: str, dst: str, *, style: str, label: str = "") -> None:
        self.cells.append(
            f'<mxCell id="{cid}" style="{style}" edge="1" parent="1" source="{src}" '
            f'target="{dst}"><mxGeometry relative="1" as="geometry" /></mxCell>')
        if label:
            self.cells.append(
                f'<mxCell id="{cid}l" value="{_esc(label)}" style="edgeLabel;html=1;'
                f'align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;'
                f'labelBackgroundColor=#FFF2CC;" vertex="1" connectable="0" '
                f'parent="{cid}"><mxGeometry x="-0.1" relative="1" as="geometry" />'
                f'</mxCell>')

    def xml(self, name: str) -> str:
        body = "\n        ".join(self.cells)
        return ('<mxfile host="app.diagrams.net">\n'
                f'  <diagram id="d1" name="{_esc(name)}">\n'
                '    <mxGraphModel dx="1400" dy="900" grid="0" page="1" '
                'pageWidth="1600" pageHeight="900">\n'
                '      <root>\n'
                '        <mxCell id="0" />\n'
                '        <mxCell id="1" parent="0" />\n'
                f'        {body}\n'
                '      </root>\n'
                '    </mxGraphModel>\n'
                '  </diagram>\n'
                '</mxfile>\n')


def _tree_layout(graph: dict) -> dict[str, tuple[int, int]]:
    """Place a rooted forest: leaves take slots left to right, parents centre."""
    kids = ag.children_of(graph)
    depth: dict[str, int] = {}

    def set_depth(nid: str, d: int) -> None:
        depth[nid] = d
        for c in kids[nid]:
            set_depth(c, d + 1)

    for r in ag.roots(graph):
        set_depth(r, 0)

    slot = [0]
    pos: dict[str, tuple[int, int]] = {}

    def place(nid: str) -> float:
        if not kids[nid]:
            col = slot[0]
            slot[0] += 1
        else:
            cols = [place(c) for c in kids[nid]]
            col = sum(cols) / len(cols)
        pos[nid] = (int(col * (CARD_W + GAP_X)), depth[nid] * (CARD_H + GAP_Y))
        return col

    for r in ag.roots(graph):
        place(r)
        slot[0] += 0.6                      # ルート間に少し余白
    return pos


def _dag_layout(graph: dict) -> dict[str, tuple[int, int]]:
    """Rows by graph depth, not by tier.

    A sub-goal that feeds the top goal is still a goal, but it belongs one row
    below it — laying out purely by tier would put both on the same line and
    draw the edge sideways. Depth is the longest path up to a node that
    supports nothing, so tier only decides the badge colour.
    """
    supports: dict[str, list[str]] = {n["id"]: [] for n in graph["nodes"]}
    for e in graph.get("edges", []) or []:
        supports[e["from"]].append(e["to"])

    depth: dict[str, int] = {}

    def d(nid: str) -> int:
        if nid in depth:
            return depth[nid]
        depth[nid] = 0                       # 循環は validate() が弾いている
        depth[nid] = 1 + max((d(t) for t in supports[nid]), default=-1)
        return depth[nid]

    for n in graph["nodes"]:
        d(n["id"])

    order: dict[str, float] = {}
    pos: dict[str, tuple[int, int]] = {}
    for row in sorted({depth[n["id"]] for n in graph["nodes"]}):
        nodes = [n for n in graph["nodes"] if depth[n["id"]] == row]
        # 支えている相手の平均位置に寄せると線の交差が減る
        nodes.sort(key=lambda n: (
            sum(order.get(t, 0) for t in supports[n["id"]])
            / max(1, len(supports[n["id"]])), n["id"]))
        for i, n in enumerate(nodes):
            order[n["id"]] = i
            pos[n["id"]] = (i * (CARD_W + GAP_X), row * (CARD_H + GAP_Y))
    return pos


def build_grouped(graph: dict, title: str) -> str:
    """`entity` ごとの枠に人を格子で並べる。線は枠をまたいで引く。

    人のつながり（links）は線に番号だけを置き、文言は下の一覧に出す。
    ラベルを線上に置くと、長い線ほどカードの上に落ちて読めなくなる。
    """
    d = Doc()
    people = graph["people"]
    order = graph.get("entityOrder") or []
    seen = [p.get("entity", "その他") for p in people]
    ents = [e for e in order if e in seen] + [e for e in dict.fromkeys(seen) if e not in order]

    pos: dict[str, str] = {}
    y, max_w = 70, 0
    for n, ent in enumerate(ents):
        members = [p for p in people if p.get("entity", "その他") == ent]
        rows = (len(members) + G_COLS - 1) // G_COLS
        fw = G_PAD * 2 + G_COLS * G_CARD_W + (G_COLS - 1) * G_GAP_X
        fh = G_HEAD + G_PAD + rows * G_CARD_H + (rows - 1) * G_GAP_Y + G_PAD
        fid = f"ent{n}"
        d.box(fid, "1", f"{ent}（{len(members)} 名）",
              "rounded=0;html=1;whiteSpace=wrap;fillColor=none;"
              f"strokeColor={LINE};strokeWidth=2;verticalAlign=top;align=left;"
              f"spacingLeft=12;spacingTop=6;fontSize=15;fontStyle=1;"
              "container=1;collapsible=0;pointerEvents=0;",
              GUTTER, y, fw, fh)
        for i, p in enumerate(members):
            cx = G_PAD + (i % G_COLS) * (G_CARD_W + G_GAP_X)
            cy = G_HEAD + G_PAD + (i // G_COLS) * (G_CARD_H + G_GAP_Y)
            cid = f"n_{p['id']}"
            pos[p["id"]] = cid
            met = p.get("met", True)
            dash = "dashed=1;" if not met else ""
            stroke = LINE if met else LINE_SOFT
            fill = STANCE_FILL.get(p.get("stance", "neutral"), "#FFFFFF")
            d.group(cid, cx, cy, G_CARD_W, G_CARD_H, parent=fid)
            d.box(f"{cid}_r", cid, "/".join(p["roles"]),
                  f"rounded=0;html=1;fillColor={BAND};strokeColor={stroke};{dash}"
                  f"fontSize=10;fontStyle=1;fontColor=#B85450;",
                  0, 0, G_CARD_W, BAND_H)
            d.box(f"{cid}_b", cid, f"{p.get('org','')}\n{p['name']}",
                  f"rounded=0;html=1;whiteSpace=wrap;fillColor={fill};"
                  f"strokeColor={stroke};{dash}fontSize=11;",
                  0, BAND_H, G_CARD_W, G_CARD_H - BAND_H - FOOT_H)
            d.box(f"{cid}_i", cid, p["influence"].capitalize(),
                  f"rounded=0;html=1;fillColor={BAND};strokeColor={stroke};{dash}"
                  f"fontSize=9;fontStyle=1;fontColor=#D79B00;",
                  0, G_CARD_H - FOOT_H, 82, FOOT_H)
        y += fh + 46
        max_w = max(max_w, fw)

    for p in people:
        if p.get("reportsTo") in pos:
            d.edge(f"e_{p['id']}", f"{pos[p['reportsTo']]}_b", pos[p["id"]],
                   style=("edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;"
                          f"strokeColor={LINE};endArrow=none;"))
    items = []
    for i, e in enumerate(graph.get("links", []) or []):
        if e["from"] not in pos or e["to"] not in pos:
            continue
        d.edge(f"l{i}", pos[e["from"]], pos[e["to"]],
               style=("edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;dashed=1;"
                      f"strokeColor={LINK};strokeWidth=2;endArrow=none;"
                      "exitX=0;exitY=0.5;entryX=0;entryY=0.5;fontSize=13;"
                      f"fontStyle=1;fontColor={LINK};labelBackgroundColor=#FFFFFF;"),
               label=MARK[len(items)])
        items.append(f"{MARK[len(items)]} {e.get('label', '')}")
    if items:
        d.box("rels", "1", "<b>人のつながり</b><br>" + "<br>".join(items),
              "rounded=0;html=1;whiteSpace=wrap;fillColor=#FFFFFF;"
              f"strokeColor={LINK};align=left;verticalAlign=top;spacingLeft=12;"
              "spacingTop=8;fontSize=12;",
              GUTTER, y, max_w, 34 + 22 * len(items))
        y += 34 + 22 * len(items) + 20
    d.box("legend", "1",
          "凡例　上帯＝役割（F 購買者 / T 技術者 / U 利用者 / C コーチ / S サポート）"
          "　　本文の塗り＝立場（橙＝支持 / 青＝懸念 / 白＝中立）"
          "　　下帯＝影響度　　破線の枠＝未面談　　赤の破線＝人のつながり",
          "rounded=0;html=1;whiteSpace=wrap;fillColor=#F9FAFB;strokeColor=#CCCCCC;"
          "align=left;spacingLeft=12;fontSize=12;",
          GUTTER, y, max_w, 46)
    d.box("title", "1", title,
          "text;html=1;align=left;fontSize=22;fontStyle=1;fontColor=#0F172A;",
          GUTTER, 20, 900, 34)
    return d.xml(title)


def build(graph: dict) -> str:
    d = Doc()
    k = ag.kind(graph)
    if k == "influence":
        pos = _tree_layout(graph)
        for p in graph["people"]:
            cid = f"n_{p['id']}"
            x, y = pos[p["id"]]
            met = p.get("met", True)
            dash = "dashed=1;" if not met else ""
            stroke = LINE if met else LINE_SOFT
            fill = STANCE_FILL.get(p.get("stance", "neutral"), "#FFFFFF")
            d.group(cid, x, y, CARD_W, CARD_H)
            d.box(f"{cid}_r", cid, "/".join(p["roles"]),
                  f"rounded=0;html=1;fillColor={BAND};strokeColor={stroke};{dash}"
                  f"fontSize=10;fontStyle=1;fontColor=#B85450;",
                  0, 0, CARD_W, BAND_H)
            label = "\n".join(s for s in (p.get("org", ""), p["name"]) if s)
            d.box(f"{cid}_b", cid, label,
                  f"rounded=0;html=1;whiteSpace=wrap;fillColor={fill};"
                  f"strokeColor={stroke};{dash}fontSize=11;",
                  0, BAND_H, CARD_W, CARD_H - BAND_H - FOOT_H)
            d.box(f"{cid}_i", cid, p["influence"].capitalize(),
                  f"rounded=0;html=1;fillColor={BAND};strokeColor={stroke};{dash}"
                  f"fontSize=9;fontStyle=1;fontColor=#D79B00;",
                  0, CARD_H - FOOT_H, 78, FOOT_H)
        for p in graph["people"]:
            if p.get("reportsTo"):
                # 親側は本文セルから出す。グループの下端は部分幅の影響度帯しか
                # 無く、中央から線を出すと帯の横の空白から生えてしまう
                d.edge(f"e_{p['id']}", f"n_{p['reportsTo']}_b", f"n_{p['id']}",
                       style=("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;"
                              f"strokeColor={LINE};endArrow=none;exitX=0.5;exitY=1;"
                              "entryX=0.5;entryY=0;"))
        for i, e in enumerate(graph.get("links", []) or []):
            d.edge(f"l{i}", f"n_{e['from']}", f"n_{e['to']}",
                   style=("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;"
                          f"strokeColor={LINE};endArrow=none;exitX=1;exitY=0.5;"
                          "entryX=0;entryY=0.5;"),
                   label=e.get("label", ""))
    else:
        pos = _dag_layout(graph)
        for n in graph["nodes"]:
            cid = f"n_{n['id']}"
            x, y = pos[n["id"]]
            d.group(cid, x, y, CARD_W, CARD_H)
            d.box(f"{cid}_t", cid, n["tier"].capitalize(),
                  f"rounded=0;html=1;fillColor={TIER_FILL[n['tier']]};"
                  f"strokeColor={TIER_STROKE[n['tier']]};fontSize=9;fontStyle=1;",
                  CARD_W - 78, 0, 78, BAND_H)
            d.box(f"{cid}_b", cid, n["text"],
                  f"rounded=0;html=1;whiteSpace=wrap;fillColor=#FFFFFF;"
                  f"strokeColor={LINE};fontSize=11;",
                  0, BAND_H, CARD_W, CARD_H - BAND_H - FOOT_H)
            d.box(f"{cid}_o", cid, n.get("owner", ""),
                  f"rounded=0;html=1;fillColor={BAND};strokeColor={LINE};"
                  f"fontSize=9;fontStyle=1;",
                  0, CARD_H - FOOT_H, 62, FOOT_H)
        for i, e in enumerate(graph.get("edges", []) or []):
            # 両端とも本文セルに付ける。グループの上端は右寄せの tier バッジ、
            # 下端は左寄せのオーナー帯しか無く、中央は空白になる
            d.edge(f"e{i}", f"n_{e['from']}_b", f"n_{e['to']}_b",
                   style=("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;"
                          f"strokeColor={LINE};endArrow=classic;exitX=0.5;exitY=0;"
                          "entryX=0.5;entryY=1;"))
    return d.xml(graph.get("title", k))


def main() -> int:
    ap = argparse.ArgumentParser(description="Write an account graph to .drawio")
    ap.add_argument("graph")
    ap.add_argument("--out", required=True)
    ap.add_argument("--extract", action="store_true",
                    help="write the thinned graph instead of the whole one")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--layout", choices=("tree", "grouped"), default="tree",
                    help="grouped: people[].entity ごとの枠に格子で並べる"
                         "（根が多くて木レイアウトが横に伸びるとき）")
    ap.add_argument("--title", default="インフルーエンスマップ（全体）")
    args = ap.parse_args()

    graph = ag.load(args.graph)
    dropped: list[dict] = []
    if args.extract:
        graph, dropped = ag.extract(graph, args.limit)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if args.layout == "grouped":
        if ag.kind(graph) != "influence":
            raise ag.AccountGraphError("--layout grouped は influence グラフ専用です")
        xml = build_grouped(graph, args.title)
    else:
        xml = build(graph)
    out.write_text(xml, encoding="utf-8")
    key = "people" if ag.kind(graph) == "influence" else "nodes"
    print(f"{len(graph[key])} nodes -> {out}")
    if dropped:
        names = [d.get("name") or d.get("text") for d in dropped]
        print(f"  dropped {len(dropped)}: {', '.join(names)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ag.AccountGraphError as exc:
        raise SystemExit(str(exc)) from exc
