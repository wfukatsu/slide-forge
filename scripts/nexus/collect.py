#!/usr/bin/env python3
"""Collect what a nexus-architect project currently knows, as one coverage.json.

    .venv/bin/python scripts/nexus/collect.py --project ../nexus-architect
    .venv/bin/python scripts/nexus/collect.py --project ../nexus-architect --json | head -40
    .venv/bin/python scripts/nexus/collect.py --project ../nexus-architect \
        --report reports/02_evaluation/mmi-overview.md      # one report's tables

A nexus-architect pipeline is **normally unfinished**: phases pending, one
running, another that wrote two of its four declared outputs. A deck built from
it has to say what it is based on before it says anything else, so this script
answers that first and separately from the drawing:

    coverage   per-phase status for the architect / product pipelines
    artifacts  every report, review JSON, UI mock and infra document that exists
    gaps       what is not answered yet — pending/failed phases, missing
               declared outputs, stale phases, open-question files

Nothing here calls an API, writes into the project, or interprets a report's
contents. It reports what exists. The reading is the deck author's job — see
`references/nexus-reports.md`.

Status comes from `tools/nexus-status.sh --json` in the nexus-architect
checkout when one can be found (it already resolves the phase manifests,
`{project}` placeholders and staleness), and falls back to reading
`work/pipeline-progress.json` directly. With neither, the artifact inventory
still stands on its own.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _i18n import t, register  # noqa: E402

register({
    "Collect a nexus-architect project's coverage, artifacts and gaps":
        "nexus-architect プロジェクトのカバレッジ・成果物・未回答を収集する",
    "project directory (the one holding work/ and reports/)":
        "プロジェクトディレクトリ（work/ と reports/ を持つ方）",
    "nexus-architect checkout, for tools/nexus-status.sh "
    "(default: auto-detected)":
        "tools/nexus-status.sh のある nexus-architect のチェックアウト"
        "（省略時: 自動検出）",
    "where to write coverage.json (default: out/nexus/<project>/coverage.json)":
        "coverage.json の書き出し先（省略時: out/nexus/<プロジェクト>/coverage.json）",
    "also print the result to stdout": "結果を標準出力にも出す",
    "extract one report's headings, tables and mermaid blocks instead":
        "代わりに 1 つのレポートの見出し・表・mermaid ブロックを抽出する",
    "not a directory: {path}": "ディレクトリではありません: {path}",
    "no report at: {path}": "レポートがありません: {path}",
    "  status: {source}": "  状態の取得元: {source}",
    "  {plugin}: {done}/{total} phases completed": "  {plugin}: {total} フェーズ中 {done} 完了",
    "  artifacts: {n} files ({reports} reports, {mocks} UI mocks)":
        "  成果物: {n} 件（レポート {reports} 件、UI モック {mocks} 件）",
    "  gaps: {n}": "  未回答・欠落: {n} 件",
    "  wrote {path}": "  {path} を書き出しました",
    "  note: no pipeline status found ({reason}); the inventory is "
    "filesystem-only":
        "  note: パイプラインの状態を取得できません（{reason}）。"
        "成果物の一覧だけで組み立てます",
    "no work/pipeline-progress.json": "work/pipeline-progress.json がありません",
    "nexus-status.sh not found": "nexus-status.sh が見つかりません",
})

SCHEMA_VERSION = 1
PIPELINES = ("architect", "product")

# Path prefix -> artifact kind. Longest prefix wins, so the nested
# api-specifications tree is classified before the 03_design bucket it lives in.
KINDS: tuple[tuple[str, str], ...] = (
    ("reports/00_requirements/", "requirements"),
    ("reports/before/", "investigation"),
    ("reports/01_analysis/", "analysis"),
    ("reports/02_evaluation/", "evaluation"),
    ("reports/03_design/api-specifications/", "api-spec"),
    ("reports/03_design/", "design"),
    ("reports/04_stories/", "domain-story"),
    ("reports/08_infrastructure/", "infra"),
    ("reports/review/individual/", "review-finding"),
    ("reports/review/", "review"),
    ("reports/00_summary/", "summary"),
    ("reports/00_core/", "product-core"),
    ("reports/01_ux/", "ux"),
    ("reports/02_spec/ui-mocks/", "ui-mock"),
    ("reports/02_spec/", "spec"),
    ("reports/03_domain/", "domain"),
    ("reports/04_quality/", "quality"),
    ("reports/05_adaptation/", "adaptation"),
    ("reports/report/", "summary"),
    ("docs/infra/", "infra"),
    ("design-system/", "design-system"),
    ("generated/", "generated-code"),
)

# Files that exist to say what is *not* settled. Their presence is a gap the
# deck has to carry, not a report to summarize.
OPEN_QUESTION_FILES = (
    "reports/00_requirements/open-questions.md",
    "reports/00_core/assumptions.md",
    "reports/00_core/validation-plan.md",
)

SCAN_GLOBS = (
    "reports/**/*.md",
    "reports/**/*.json",
    "reports/**/*.html",
    "reports/**/*.yaml",
    "docs/infra/**/*.md",
    "design-system/**/*.json",
)

# Code generation is inventoried, not read: enough to say "this was produced",
# capped so a node_modules-sized tree cannot flood the collection.
CODE_GLOBS = (
    "generated/**/schema.json",
    "generated/**/build.gradle",
    "generated/**/docker-compose.yml",
    "generated/**/package.json",
    "**/scalardb.properties",
    "**/database.properties",
)
CODE_CAP = 40
UNFINISHED = ("pending", "in_progress", "failed")


# ---------------------------------------------------------------- utilities

def _rel(root: str, path: str) -> str:
    return os.path.relpath(path, root).replace(os.sep, "/")


def kind_of(rel_path: str) -> str:
    best = ""
    kind = "other"
    for prefix, name in KINDS:
        if rel_path.startswith(prefix) and len(prefix) > len(best):
            best, kind = prefix, name
    return kind


def read_frontmatter(text: str) -> dict:
    """The report frontmatter block, as far as a flat scalar/list reader gets.

    The nexus-architect hook guarantees the block starts at line 1 and parses;
    every key these reports use is a scalar or a list of scalars, so a full
    YAML parser would be a dependency bought for nothing (the venv has none).
    """
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    out: dict = {}
    key = None
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and key:
            out.setdefault(key, [])
            if isinstance(out[key], list):
                out[key].append(line[4:].strip().strip('"'))
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        out[key] = value.strip('"') if value else []
    return out


def markdown_tables(text: str) -> list[dict]:
    """Every GitHub-style table, as {headers, rows, section}."""
    tables: list[dict] = []
    section = ""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#"):
            section = line.lstrip("#").strip()
        elif line.startswith("|") and i + 1 < len(lines) and re.match(
                r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            headers = [c.strip() for c in line.strip().strip("|").split("|")]
            rows = []
            i += 2
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            tables.append({"section": section, "headers": headers, "rows": rows})
            continue
        i += 1
    return tables


def mermaid_blocks(text: str) -> list[dict]:
    """Fenced mermaid blocks with the diagram kind read off the first word."""
    out = []
    for m in re.finditer(r"```mermaid\n(.*?)```", text, re.S):
        code = m.group(1)
        first = next((ln.strip() for ln in code.splitlines() if ln.strip()), "")
        out.append({"kind": first.split()[0] if first else "", "code": code})
    return out


def headings(text: str) -> list[str]:
    return [ln.lstrip("#").strip() for ln in text.splitlines()
            if re.match(r"^#{2,3} ", ln)]


# ------------------------------------------------------------------- status

def find_nexus_root(project: str, given: str | None) -> str | None:
    """Where tools/nexus-status.sh lives. The project itself is the usual answer."""
    candidates = []
    if given:
        candidates.append(os.path.expanduser(given))
    candidates.append(project)
    parent = os.path.dirname(os.path.abspath(project))
    candidates += [os.path.join(parent, "nexus-architect"),
                   os.path.join(os.path.dirname(parent), "nexus-architect")]
    for c in candidates:
        if c and os.path.isfile(os.path.join(c, "tools", "nexus-status.sh")):
            return os.path.abspath(c)
    return None


def status_via_tool(nexus_root: str, project: str) -> dict | None:
    """`nexus-status.sh --json` per pipeline. None when it cannot be used.

    Only the read-only JSON mode is invoked — never --md, which would write a
    status file into the user's project.
    """
    out: dict = {}
    for plugin in PIPELINES:
        try:
            result = subprocess.run(
                ["bash", os.path.join(nexus_root, "tools", "nexus-status.sh"),
                 project, "--json", f"--view={plugin}", "--no-color"],
                capture_output=True, text=True, timeout=60, cwd=nexus_root,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if result.returncode not in (0, 1) or not result.stdout.strip():
            return None
        try:
            out[plugin] = json.loads(result.stdout)
        except json.JSONDecodeError:
            return None
    return out or None


def _resolve_placeholder(project: str, path: str, exists: bool) -> tuple[str, bool]:
    """Settle a declared output whose path still carries a `{placeholder}`.

    `create-domain-story` declares `domain-story-{domain}.md` — one file per
    domain, so the name is only known after the phase runs. The status tool
    reports it unresolved and therefore missing, which would put a written
    report in the deck's gap list. Match it as a glob instead.
    """
    if exists or "{" not in path:
        return path, exists
    hits = sorted(glob.glob(os.path.join(project, re.sub(r"\{[^}]+\}", "*", path))))
    if not hits:
        return path, False
    return _rel(project, hits[0]), True


def phases_from_tool(payload: dict, project: str) -> dict:
    phases = []
    for p in payload.get("phases") or []:
        outputs = []
        for o in (p.get("outputs") or []):
            path, exists = _resolve_placeholder(
                project, o.get("resolved") or o.get("path") or "",
                bool(o.get("exists")))
            outputs.append({"path": path, "exists": exists})
        phases.append({
            "name": p.get("name"),
            "group": p.get("group"),
            # core = the manifest pipeline; extension = the opt-in tier run by
            # hand. Mixing them gives a denominator the dashboard disagrees with.
            "tier": p.get("tier") or "core",
            "status": p.get("status"),
            "optional": bool(p.get("optional")),
            "stale": bool(p.get("stale")),
            "summary": (p.get("summary") or "").strip(),
            "note": (p.get("note") or "").strip(),
            "completedAt": p.get("completed_at"),
            "command": p.get("command"),
            "outputs": outputs,
            "outputsWritten": sum(1 for o in outputs if o["exists"]),
            "outputsDeclared": p.get("outputs_declared", len(outputs)),
        })
    summary = payload.get("summary") or {}
    return {
        "total": summary.get("total", len(phases)),
        "byStatus": summary.get("by_status", {}),
        "phases": phases,
    }


def status_from_progress(project: str) -> dict | None:
    """Fallback: read work/pipeline-progress.json without the status tool."""
    path = os.path.join(project, "work", "pipeline-progress.json")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    name = data.get("project_name") or os.path.basename(os.path.abspath(project))
    out: dict = {p: {"total": 0, "byStatus": {}, "phases": []} for p in PIPELINES}
    for phase_name, entry in (data.get("phases") or {}).items():
        plugin = entry.get("plugin") or "architect"
        bucket = out.setdefault(plugin, {"total": 0, "byStatus": {}, "phases": []})
        outputs = []
        for declared in entry.get("outputs") or []:
            resolved = declared.replace("{project}", name)
            path, exists = _resolve_placeholder(
                project, resolved, os.path.exists(os.path.join(project, resolved)))
            outputs.append({"path": path, "exists": exists})
        bucket["phases"].append({
            "name": phase_name,
            "group": entry.get("category"),
            "tier": "core",
            "status": entry.get("status", "pending"),
            "optional": bool(entry.get("optional")),
            "stale": False,
            "summary": (entry.get("summary") or "").strip(),
            "note": (entry.get("note") or "").strip(),
            "completedAt": entry.get("completed_at"),
            # The status tool derives this the same way; without it, the
            # plugin's own naming convention settles it (see the nexus
            # CLAUDE.md: architecture skills are /architect:<phase>).
            "command": f"/{plugin}:{phase_name}",
            "outputs": outputs,
            "outputsWritten": sum(1 for o in outputs if o["exists"]),
            "outputsDeclared": len(outputs),
        })
    for bucket in out.values():
        bucket["total"] = len(bucket["phases"])
        counts: dict = {}
        for p in bucket["phases"]:
            counts[p["status"]] = counts.get(p["status"], 0) + 1
        bucket["byStatus"] = counts
    return {"_project": data, "pipelines": out}


# ---------------------------------------------------------------- artifacts

def mock_meta(rel_path: str, text: str) -> dict:
    """Story / step / title of a UI mock, from its file name and <title>."""
    base = os.path.basename(rel_path)[:-len(".html")]
    m = re.match(r"^(?P<story>.+?)-(?P<step>\d+)-(?P<slug>.+)$", base)
    title = ""
    tm = re.search(r"<title>(.*?)</title>", text, re.S | re.I)
    if tm:
        title = " ".join(tm.group(1).split())
    if m:
        return {"story": m.group("story"), "step": int(m.group("step")),
                "slug": m.group("slug"), "isIndex": False, "title": title}
    return {"story": base[:-len("-index")] if base.endswith("-index") else base,
            "step": None, "slug": None,
            "isIndex": base.endswith("-index"), "title": title}


def collect_artifacts(project: str) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for pattern in SCAN_GLOBS:
        for path in sorted(glob.glob(os.path.join(project, pattern), recursive=True)):
            if not os.path.isfile(path):
                continue
            rel = _rel(project, path)
            if rel in seen:
                continue
            seen.add(rel)
            record = {"path": rel, "kind": kind_of(rel),
                      "bytes": os.path.getsize(path),
                      "modified": _dt.datetime.fromtimestamp(
                          os.path.getmtime(path)).astimezone().isoformat(timespec="seconds")}
            if rel.endswith(".md"):
                with open(path, encoding="utf-8", errors="replace") as f:
                    text = f.read()
                fm = read_frontmatter(text)
                record.update({
                    "title": fm.get("title") or "",
                    "phase": fm.get("phase") or "",
                    "skill": fm.get("skill") or "",
                    "generatedAt": fm.get("generated_at") or "",
                    "headings": headings(text)[:24],
                    "tables": len(markdown_tables(text)),
                    "diagrams": [b["kind"] for b in mermaid_blocks(text)],
                })
            elif rel.endswith(".html") and record["kind"] == "ui-mock":
                with open(path, encoding="utf-8", errors="replace") as f:
                    record.update(mock_meta(rel, f.read()))
            elif rel.endswith(".json") and record["kind"] == "review-finding":
                try:
                    with open(path, encoding="utf-8") as f:
                        data = json.load(f)
                except (json.JSONDecodeError, OSError):
                    data = {}
                record.update({
                    "perspective": data.get("perspective", ""),
                    "dimensions": [{"name": d.get("name"), "score": d.get("score"),
                                    "weight": d.get("weight")}
                                   for d in (data.get("dimensions") or [])],
                })
            out.append(record)
    code: list[dict] = []
    for pattern in CODE_GLOBS:
        for path in sorted(glob.glob(os.path.join(project, pattern), recursive=True)):
            rel = _rel(project, path)
            if rel in seen or "/node_modules/" in f"/{rel}":
                continue
            seen.add(rel)
            code.append({"path": rel, "kind": "generated-code",
                         "bytes": os.path.getsize(path)})
            if len(code) >= CODE_CAP:
                break
    return out + code


# --------------------------------------------------------------------- gaps

def collect_gaps(pipelines: dict, artifacts: list[dict]) -> list[dict]:
    gaps: list[dict] = []
    for plugin, bucket in pipelines.items():
        for phase in bucket["phases"]:
            if phase["status"] in UNFINISHED:
                gaps.append({
                    "kind": f"phase-{phase['status'].replace('_', '-')}",
                    "plugin": plugin, "phase": phase["name"],
                    "detail": phase["note"] or "",
                    "command": phase.get("command"),
                    "tier": phase.get("tier", "core"),
                    "optional": bool(phase.get("optional")),
                })
            elif phase["status"] == "completed" and \
                    phase["outputsWritten"] < phase["outputsDeclared"]:
                missing = [o["path"] for o in phase["outputs"] if not o["exists"]]
                gaps.append({
                    "kind": "missing-output", "plugin": plugin,
                    "phase": phase["name"],
                    "detail": ", ".join(missing),
                    "command": phase.get("command"),
                    "tier": phase.get("tier", "core"),
                    "optional": bool(phase.get("optional")),
                })
            if phase["stale"]:
                gaps.append({"kind": "stale", "plugin": plugin,
                             "phase": phase["name"],
                             "detail": "an upstream phase changed after this ran"})
    have = {a["path"] for a in artifacts}
    for path in OPEN_QUESTION_FILES:
        if path in have:
            gaps.append({"kind": "open-question", "plugin": None, "phase": None,
                         "detail": path})
    return gaps


# ---------------------------------------------------------------- assembling

def collect(project: str, nexus_root: str | None) -> dict:
    project = os.path.abspath(os.path.expanduser(project))
    root = find_nexus_root(project, nexus_root)
    source = None
    pipelines: dict = {p: {"total": 0, "byStatus": {}, "phases": []} for p in PIPELINES}
    progress: dict = {}
    reason = t("nexus-status.sh not found")

    payloads = status_via_tool(root, project) if root else None
    if payloads:
        source = "nexus-status.sh"
        for plugin, payload in payloads.items():
            pipelines[plugin] = phases_from_tool(payload, project)
            progress = progress or {"options": payload.get("options") or {},
                                    "project_name": payload.get("project")}
    else:
        fallback = status_from_progress(project)
        if fallback:
            source = "pipeline-progress.json"
            pipelines = fallback["pipelines"]
            progress = fallback["_project"]
        else:
            reason = t("no work/pipeline-progress.json")

    artifacts = collect_artifacts(project)
    options = progress.get("options") or {}
    name = progress.get("project_name") or os.path.basename(project)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "asOf": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "project": {
            "name": name,
            "root": project,
            "nexusRoot": root,
            "language": options.get("output_language") or "en",
            "workflow": options.get("workflow_type") or "",
            "scalardbEnabled": bool(options.get("scalardb_enabled")),
        },
        "status": {"source": source, "reason": None if source else reason},
        "pipelines": pipelines,
        "artifacts": artifacts,
        "gaps": collect_gaps(pipelines, artifacts),
    }


def extract_report(project: str, rel_path: str) -> dict:
    path = os.path.join(project, rel_path)
    if not os.path.isfile(path):
        raise SystemExit(t("no report at: {path}", path=path))
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    return {
        "path": rel_path,
        "frontmatter": read_frontmatter(text),
        "headings": headings(text),
        "tables": markdown_tables(text),
        "diagrams": mermaid_blocks(text),
    }


def main() -> int:
    p = argparse.ArgumentParser(
        description=t("Collect a nexus-architect project's coverage, "
                      "artifacts and gaps"))
    p.add_argument("--project", required=True,
                   help=t("project directory (the one holding work/ and reports/)"))
    p.add_argument("--nexus-root",
                   help=t("nexus-architect checkout, for tools/nexus-status.sh "
                          "(default: auto-detected)"))
    p.add_argument("--out",
                   help=t("where to write coverage.json "
                          "(default: out/nexus/<project>/coverage.json)"))
    p.add_argument("--json", action="store_true",
                   help=t("also print the result to stdout"))
    p.add_argument("--report", metavar="PATH",
                   help=t("extract one report's headings, tables and mermaid "
                          "blocks instead"))
    args = p.parse_args()

    project = os.path.abspath(os.path.expanduser(args.project))
    if not os.path.isdir(project):
        raise SystemExit(t("not a directory: {path}", path=project))

    if args.report:
        print(json.dumps(extract_report(project, args.report),
                         ensure_ascii=False, indent=2))
        return 0

    data = collect(project, args.nexus_root)
    out_path = args.out or os.path.join(
        "out", "nexus", data["project"]["name"], "coverage.json")
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    print(data["project"]["name"])
    if data["status"]["source"]:
        print(t("  status: {source}", source=data["status"]["source"]))
        for plugin in PIPELINES:
            bucket = data["pipelines"][plugin]
            if bucket["total"]:
                print(t("  {plugin}: {done}/{total} phases completed",
                        plugin=plugin,
                        done=bucket["byStatus"].get("completed", 0),
                        total=bucket["total"]))
    else:
        print(t("  note: no pipeline status found ({reason}); the inventory is "
                "filesystem-only", reason=data["status"]["reason"]))
    mocks = sum(1 for a in data["artifacts"] if a["kind"] == "ui-mock")
    reports = sum(1 for a in data["artifacts"] if a["path"].endswith(".md"))
    print(t("  artifacts: {n} files ({reports} reports, {mocks} UI mocks)",
            n=len(data["artifacts"]), reports=reports, mocks=mocks))
    print(t("  gaps: {n}", n=len(data["gaps"])))
    print(t("  wrote {path}", path=out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
