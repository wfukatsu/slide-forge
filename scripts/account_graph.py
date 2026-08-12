#!/usr/bin/env python3
"""Load, validate and thin the two account graphs.

One JSON feeds both outputs: the full graph goes to draw.io, and a slide shows
only the part that fits. Keeping a single model is the point — a slide that
disagrees with the .drawio beside it is worse than either alone.

    influence  people[] {id, roles[], org, name, influence, stance, met,
                         reportsTo, note}
               links[]  {from, to, label}      peer relationships / supplementary lines
    discovery  nodes[]  {id, tier, text, owner}
               edges[]  {from, to}             Tactics -> Strategy -> Goal

`extract()` is the part worth reading. Taking the top N nodes on their own
score would cut the middle out of a chain and leave edges pointing at nothing,
so every kept node drags its ancestors in with it. What gets dropped is
reported rather than silently vanishing.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

ROLES = {"F": "購買者", "T": "技術者", "U": "利用者", "C": "コーチ", "S": "サポート役員"}
INFLUENCE = ("champion", "high", "medium", "low")
STANCE = ("close", "neutral", "opposed")
TIERS = ("goal", "strategy", "tactics")
# can only connect from a lower tier to a higher tier
TIER_RANK = {"tactics": 0, "strategy": 1, "goal": 2}

INFLUENCE_SCORE = {"champion": 4, "high": 3, "medium": 2, "low": 1}

DEFAULT_LIMIT = {"influence": 7, "discovery": 8}


class AccountGraphError(ValueError):
    pass


def load(path: str | Path) -> dict:
    p = Path(path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AccountGraphError(f"not found: {p}") from exc
    except json.JSONDecodeError as exc:
        raise AccountGraphError(f"invalid JSON: {p}: {exc}") from exc
    problems = validate(data)
    if problems:
        raise AccountGraphError("; ".join(problems))
    return data


def kind(graph: dict) -> str:
    k = graph.get("type")
    if k not in ("influence", "discovery"):
        raise AccountGraphError("type must be 'influence' or 'discovery'")
    return k


def _items(graph: dict) -> list[dict]:
    return graph.get("people" if graph.get("type") == "influence" else "nodes") or []


def validate(graph: dict) -> list[str]:
    if not isinstance(graph, dict):
        return ["graph must be an object"]
    k = graph.get("type")
    if k not in ("influence", "discovery"):
        return ["type must be 'influence' or 'discovery'"]
    key = "people" if k == "influence" else "nodes"
    items = graph.get(key)
    if not isinstance(items, list) or not items:
        return [f"{key} must be a non-empty array"]
    problems: list[str] = []
    ids: set[str] = set()
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            problems.append(f"{key}[{i}] must be an object")
            continue
        nid = it.get("id")
        if not isinstance(nid, str) or not nid:
            problems.append(f"{key}[{i}]: id is required")
            continue
        if nid in ids:
            problems.append(f"duplicate id: {nid}")
        ids.add(nid)
        if k == "influence":
            if not it.get("name"):
                problems.append(f"{nid}: name is required")
            roles = it.get("roles", [])
            if not isinstance(roles, list) or not roles:
                problems.append(f"{nid}: roles must be a non-empty array")
            else:
                bad = [r for r in roles if r not in ROLES]
                if bad:
                    problems.append(
                        f"{nid}: unknown role {bad} (use {'/'.join(ROLES)})")
            if it.get("influence") not in INFLUENCE:
                problems.append(f"{nid}: influence must be one of {INFLUENCE}")
            if it.get("stance", "neutral") not in STANCE:
                problems.append(f"{nid}: stance must be one of {STANCE}")
        else:
            if it.get("tier") not in TIERS:
                problems.append(f"{nid}: tier must be one of {TIERS}")
            if not it.get("text"):
                problems.append(f"{nid}: text is required")
    if problems:
        return problems

    # referential integrity
    for it in items:
        parent = it.get("reportsTo")
        if parent is not None and parent not in ids:
            problems.append(f"{it['id']}: reportsTo references unknown id {parent!r}")
    for i, e in enumerate(graph.get("edges", []) or []):
        if not isinstance(e, dict) or e.get("from") not in ids or e.get("to") not in ids:
            problems.append(f"edges[{i}]: from/to must reference declared ids")
    for i, e in enumerate(graph.get("links", []) or []):
        if not isinstance(e, dict) or e.get("from") not in ids or e.get("to") not in ids:
            problems.append(f"links[{i}]: from/to must reference declared ids")
    if problems:
        return problems

    if k == "discovery":
        by_id = {n["id"]: n for n in items}
        for i, e in enumerate(graph.get("edges", []) or []):
            lo, hi = by_id[e["from"]]["tier"], by_id[e["to"]]["tier"]
            # Same tier is fine (a lower goal supports a higher goal, a lower
            # strategy supports a higher strategy). Only edges running from a
            # higher tier to a lower tier are forbidden.
            if TIER_RANK[lo] > TIER_RANK[hi]:
                problems.append(
                    f"edges[{i}]: {lo} -> {hi} points downwards; edges run "
                    f"tactics -> strategy -> goal")
    problems.extend(_cycles(graph))
    return problems


def _parents(graph: dict) -> dict[str, list[str]]:
    """node id -> ids it points at (manager, or the tier above)."""
    out: dict[str, list[str]] = {it["id"]: [] for it in _items(graph)}
    if graph.get("type") == "influence":
        for it in _items(graph):
            if it.get("reportsTo"):
                out[it["id"]].append(it["reportsTo"])
    else:
        for e in graph.get("edges", []) or []:
            out[e["from"]].append(e["to"])
    return out


def _cycles(graph: dict) -> list[str]:
    parents = _parents(graph)
    state: dict[str, int] = {}

    def walk(nid: str, trail: list[str]) -> list[str]:
        if state.get(nid) == 1:
            loop = trail[trail.index(nid):] + [nid]
            return [f"cycle: {' -> '.join(loop)}"]
        if state.get(nid) == 2:
            return []
        state[nid] = 1
        found: list[str] = []
        for p in parents[nid]:
            found.extend(walk(p, trail + [nid]))
        state[nid] = 2
        return found

    out: list[str] = []
    for nid in parents:
        out.extend(walk(nid, []))
    return sorted(set(out))


def _score(graph: dict, item: dict, parents: dict[str, list[str]]) -> tuple:
    """Higher sorts first."""
    children = sum(1 for v in parents.values() if item["id"] in v)
    if graph["type"] == "influence":
        # Within the same influence level: decision-makers > people already met >
        # people with more reports. Someone unmet and low-influence carries the
        # least information for a slide, so they sort last.
        return (INFLUENCE_SCORE.get(item.get("influence"), 0),
                1 if "F" in item.get("roles", []) else 0,
                1 if item.get("met", True) else 0,
                children)
    # goal > strategy > tactics. Within the same tier, keep whichever supports more
    return (TIER_RANK[item["tier"]], children)


def extract(graph: dict, limit: int | None = None) -> tuple[dict, list[dict]]:
    """Return (thinned graph, dropped items).

    Keeps the highest-scoring nodes, then pulls in every ancestor of a kept
    node so no edge dangles. That can push the result past `limit`; keeping the
    graph readable matters more than hitting the number exactly.
    """
    k = kind(graph)
    limit = limit or DEFAULT_LIMIT[k]
    items = _items(graph)
    parents = _parents(graph)
    by_id = {it["id"]: it for it in items}

    ranked = sorted(items, key=lambda it: _score(graph, it, parents), reverse=True)
    cut = min(limit, len(ranked))
    # If there's a tie at the cutoff, drop the whole tied group together.
    # Including only one of several equally important siblings would read as if
    # the others who weren't picked don't exist.
    if 0 < cut < len(ranked):
        edge_score = _score(graph, ranked[cut - 1], parents)
        if edge_score == _score(graph, ranked[cut], parents):
            while cut > 0 and _score(graph, ranked[cut - 1], parents) == edge_score:
                cut -= 1
    keep: set[str] = {it["id"] for it in ranked[:cut]}
    # pull in ancestors (don't leave any dangling edges)
    stack = list(keep)
    while stack:
        for p in parents[stack.pop()]:
            if p not in keep:
                keep.add(p)
                stack.append(p)

    dropped = [it for it in items if it["id"] not in keep]
    key = "people" if k == "influence" else "nodes"
    thin = {kk: v for kk, v in graph.items() if kk not in (key, "edges", "links")}
    thin[key] = [it for it in items if it["id"] in keep]
    if k == "discovery":
        thin["edges"] = [e for e in graph.get("edges", []) or []
                         if e["from"] in keep and e["to"] in keep]
    else:
        thin["links"] = [e for e in graph.get("links", []) or []
                         if e["from"] in keep and e["to"] in keep]
        # Ancestors are always kept so this normally can't happen, but sever any
        # dangling reportsTo just in case
        thin[key] = [dict(it, reportsTo=(it.get("reportsTo")
                                         if it.get("reportsTo") in keep else None))
                     for it in thin[key]]
    return thin, dropped


def roots(graph: dict) -> list[str]:
    parents = _parents(graph)
    return [nid for nid, ps in parents.items() if not ps]


def children_of(graph: dict) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {it["id"]: [] for it in _items(graph)}
    for nid, ps in _parents(graph).items():
        for p in ps:
            out[p].append(nid)
    return out
