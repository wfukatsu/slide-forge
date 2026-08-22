#!/usr/bin/env python3
"""Build the spine of a nexus-architect explanation deck from coverage.json.

    .venv/bin/python scripts/nexus/collect.py --project ../nexus-architect
    .venv/bin/python scripts/nexus/build_nexus_deck.py \
        --coverage out/nexus/ec-monolith/coverage.json --profile deep
    .venv/bin/python scripts/assemble_spec.py --out out/nexus/ec-monolith/deck.json \
        out/nexus/ec-monolith/pages/

What this writes is only what the pipeline's own records already settle:

    010 cover                 project, as-of, one line of scope
    020 pipeline-coverage     completed / running / pending / skipped
    1xx phase-digest          one per completed phase (deep) or per group (exec),
                              from the phase's own recorded summary
    900 open-questions        every gap, with the command that closes it
    910 appendix              the artifact inventory, with each file's timestamp

Pages that need a report to be **read** — scores, issue registers, context maps,
roadmaps, UI mock walkthroughs — are not written here. They are authored into
the same `pages/` directory as `render_slide_template.py` output and merged by
filename order, which is what `assemble_spec.py` exists for. The numbering
leaves 18 slots between digests for exactly that. See the `nexus-report-slides`
skill for which template each report maps to.

Nothing is invented: a phase with no recorded summary gets no digest page, and
a gap with no known command says so instead of guessing one.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from _i18n import t, register  # noqa: E402
from slide_templates import load_template, render_template  # noqa: E402

register({
    "Build the deterministic pages of a nexus-architect explanation deck":
        "nexus-architect 説明デッキの、機械的に決まるページを組む",
    "path to coverage.json (from scripts/nexus/collect.py)":
        "coverage.json のパス（scripts/nexus/collect.py の出力）",
    "audience profile: exec (short) or deep (every completed phase)":
        "読者プロファイル: exec（短く）または deep（完了フェーズすべて）",
    "directory for the page fragments (default: next to coverage.json)":
        "ページ断片の出力ディレクトリ（省略時: coverage.json の隣）",
    "density passed to the templates (default: print for deep, "
    "presentation for exec)":
        "テンプレートに渡す密度（既定: deep なら print、exec なら presentation）",
    "deck title (default: built from the project name)":
        "デッキのタイトル（省略時: プロジェクト名から作る）",
    "coverage.json not found: {path}": "coverage.json がありません: {path}",
    "unsupported coverage schema: {version}":
        "未対応の coverage スキーマです: {version}",
    "  {n} pages -> {dir}": "  {n} ページ -> {dir}",
    "  {n} completed phases, {g} gaps": "  完了フェーズ {n} 件、未回答 {g} 件",
    "  note: no phase has a recorded summary; only the cover, coverage and "
    "gap pages were written":
        "  note: 要約が記録されたフェーズがありません。表紙・カバレッジ・"
        "未回答ページだけを書き出しました",
    "  next: author the interpretive pages into the same directory, then "
    "assemble_spec.py":
        "  次: 解釈が要るページを同じディレクトリに書き足し、"
        "assemble_spec.py でまとめる",
})

SCHEMA_VERSION = 1
PROFILES = ("exec", "deep")
# Report-derived pages slot in between the digests; 20 apart leaves room for
# the ~9 interpretive pages a busy phase can justify.
DIGEST_BASE = 100
DIGEST_STEP = 20

STATUS_ORDER = ("completed", "in_progress", "pending", "skipped", "failed")

LABELS = {
    "ja": {
        "coverTitle": "{project} 分析結果のご説明",
        "coverSubtitle": "{done} / {total} フェーズ完了時点（{asOf}）",
        "coverageTitle": "この資料は {plugin} {done}/{total} フェーズ完了時点の分析に基づく",
        "coverageBasis": "完了 {done} 件・スキップ {skipped} 件・実行中 {running} 件・"
                         "未着手 {pending} 件。{others}未完了フェーズが扱う論点は本資料の範囲外。",
        "otherPipeline": "{plugin} は {done}/{total} 完了。",
        "extensionTier": "拡張フェーズ {n} 件は対象外。",
        "andMore": "ほか {n} 件",
        "digestFallbackTitle": "{phase} フェーズが明らかにしたこと",
        "status": {"completed": "完了", "in_progress": "実行中",
                   "pending": "未着手", "skipped": "スキップ", "failed": "失敗"},
        "groupHeaders": ["領域", "進捗", "出力"],
        "outputCount": "{n} 件",
        "phaseLabel": "{phase} ／ {plugin} ／ {status}",
        "digestHeaders": ["出力レポート", "内容"],
        "openTitle": "まだ答えられていない論点と、その埋め方",
        "openLead": "{n} 件が未回答。内訳は未着手 {pending} 件・実行中 {running} 件・"
                    "出力欠落 {missing} 件・スキップ {skipped} 件。",
        "openHeaders": ["未回答の問い", "影響", "埋め方"],
        "gapPhrase": {"phase-pending": "{phase} が未着手",
                      "phase-in-progress": "{phase} が実行中",
                      "phase-failed": "{phase} が失敗",
                      "missing-output": "{phase} の出力が欠落",
                      "stale": "{phase} が陳腐化",
                      "open-question": "{detail} に未回答あり"},
        "gapImpact": "{n} 件のレポートが未作成",
        "gapImpactOther": "本資料では扱えない",
        "gapFixUnknown": "担当と手段を決める",
        "nextStepsHead": ["先に埋める", "並行できる"],
        "nextStepsBody": ["{first}", "完了済みフェーズの結論は、未回答が埋まっても変わらない"],
        "nextStepsFallback": "未回答なし。追加調査の前に本資料の結論を確認する",
        "appendixTitle": "付録: 本資料が参照したレポート",
        "appendixHeaders": ["レポート", "フェーズ", "生成"],
        "source": "{project} の {src}（収集 {asOf}）",
        "sourcePhase": "{files}（{gen}）",
        "noSummary": "（このフェーズは要約を記録していない）",
        "noMore": "他になし",
    },
    "en": {
        "coverTitle": "{project} — analysis walkthrough",
        "coverSubtitle": "as of {asOf} · {done} / {total} phases complete",
        "coverageTitle": "This deck rests on {done} of {total} {plugin} phases",
        "coverageBasis": "{done} completed, {skipped} skipped, {running} running, "
                         "{pending} not started. {others}What the unfinished phases "
                         "cover is out of scope here.",
        "otherPipeline": "{plugin}: {done}/{total} complete. ",
        "extensionTier": "{n} extension-tier phases excluded. ",
        "andMore": " +{n} more",
        "digestFallbackTitle": "What {phase} established",
        "status": {"completed": "completed", "in_progress": "running",
                   "pending": "not started", "skipped": "skipped",
                   "failed": "failed"},
        "groupHeaders": ["Area", "Progress", "Outputs"],
        "outputCount": "{n} files",
        "phaseLabel": "{phase} · {plugin} · {status}",
        "digestHeaders": ["Report", "What it covers"],
        "openTitle": "What this deck cannot answer yet, and how to close it",
        "openLead": "{n} open items: {pending} not started, {running} running, "
                    "{missing} missing outputs, {skipped} skipped.",
        "openHeaders": ["Open question", "Impact", "How it closes"],
        "gapPhrase": {"phase-pending": "{phase} not started",
                      "phase-in-progress": "{phase} still running",
                      "phase-failed": "{phase} failed",
                      "missing-output": "{phase} output missing",
                      "stale": "{phase} is stale",
                      "open-question": "open items in {detail}"},
        "gapImpact": "{n} reports not written",
        "gapImpactOther": "out of scope for this deck",
        "gapFixUnknown": "assign an owner and a method",
        "nextStepsHead": ["Close first", "Can run in parallel"],
        "nextStepsBody": ["{first}", "The completed phases' conclusions stand "
                                     "whether or not the gaps close"],
        "nextStepsFallback": "No open items. Review the conclusions before "
                             "commissioning more analysis",
        "appendixTitle": "Appendix: reports this deck draws on",
        "appendixHeaders": ["Report", "Phase", "Generated"],
        "source": "{src} of {project} (collected {asOf})",
        "sourcePhase": "{files} ({gen})",
        "noSummary": "(this phase recorded no summary)",
        "noMore": "nothing else",
    },
}


def clip(text: str, limit: int) -> str:
    """Trim to a template's declared cap without silently losing the end."""
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[:limit - 1] + "…"


def clip_sentences(text: str, limit: int) -> str:
    """Trim on a sentence boundary, so a digest never stops mid-clause."""
    text = " ".join(str(text or "").split())
    if len(text) <= limit:
        return text
    kept = ""
    for part in re.split(r"(?<=[。.])", text):
        if len(kept) + len(part) > limit:
            break
        kept += part
    return kept or clip(text, limit)


def name_list(names: list[str], limit: int, more: str) -> str:
    """As many file names as fit, then "and N more" — never half a file name."""
    if not names:
        return "-"
    shown: list[str] = []
    for name in names:
        if shown and len("・".join(shown + [name])) > limit:
            break
        shown.append(name)
    rest = len(names) - len(shown)
    text = "・".join(shown)
    if not rest:
        return clip(text, limit)
    tail = more.format(n=rest)
    while len(shown) > 1 and len(text) + len(tail) > limit:
        shown.pop()
        rest = len(names) - len(shown)
        tail, text = more.format(n=rest), "・".join(shown)
    if len(text) + len(tail) > limit:
        # Half a file name plus "+3 more" tells the reader nothing; the count
        # alone at least says how much there is.
        return clip(more.format(n=len(names)).strip(), limit)
    return clip(text + tail, limit)


def pad(rows: list[list], minimum: int, label: str) -> list[list]:
    """Templates declare a minimum row count; a real project can be below it.

    A one-group pipeline or a single open question is a legitimate state, so
    the shortfall is filled with an explicit "nothing else" row rather than
    letting the render fail or inventing a second finding.
    """
    width = len(rows[0]) if rows else 3
    while len(rows) < minimum:
        rows.append([label] + ["-"] * (width - 1))
    return rows


def render(template_id: str, data: dict, density: str) -> dict:
    template, _ = load_template(template_id)
    return render_template(template, data, density=density)


def phase_rows(pipelines: dict) -> list[dict]:
    out = []
    for plugin, bucket in pipelines.items():
        for phase in bucket["phases"]:
            out.append(dict(phase, plugin=plugin))
    return out


def status_counts(phases: list[dict]) -> dict:
    counts = {k: 0 for k in STATUS_ORDER}
    for p in phases:
        counts[p["status"]] = counts.get(p["status"], 0) + 1
    return counts


def primary_pipeline(cov: dict) -> str:
    """The pipeline this deck is about: the one that has actually run.

    A project runs `architect`, `product`, or both, and the two are separate
    pipelines with separate manifests. Adding their phase counts together
    produces a denominator ("21 of 61") that describes no real thing.
    """
    scored = [(sum(1 for ph in bucket["phases"] if ph["status"] != "pending"),
               bucket["total"], name)
              for name, bucket in cov["pipelines"].items()]
    scored.sort(reverse=True)
    return scored[0][2] if scored else "architect"


def scope(cov: dict, L: dict) -> dict:
    """The deck's denominator: the primary pipeline's core-tier phases.

    The dashboard counts the manifest (core) tier, and agreeing with what the
    user already sees there matters more than counting every opt-in extension
    phase in the headline. The rest is stated in a sentence instead.
    """
    primary = primary_pipeline(cov)
    phases = [p for p in phase_rows(cov["pipelines"]) if p["plugin"] == primary]
    core = [p for p in phases if p.get("tier", "core") == "core"] or phases
    others = "".join(
        L["otherPipeline"].format(plugin=name, total=bucket["total"],
                                  done=sum(1 for ph in bucket["phases"]
                                           if ph["status"] == "completed"))
        for name, bucket in cov["pipelines"].items()
        if name != primary and bucket["total"])
    if len(phases) - len(core):
        others += L["extensionTier"].format(n=len(phases) - len(core))
    return {"plugin": primary, "phases": core, "counts": status_counts(core),
            "total": len(core), "others": others}


def cover_page(cov: dict, L: dict, sc: dict) -> dict:
    as_of = cov["asOf"][:16].replace("T", " ")
    return {
        "layout": "COVER",
        "title": L["coverTitle"].format(project=cov["project"]["name"]),
        "subtitle": L["coverSubtitle"].format(
            done=sc["counts"]["completed"], total=sc["total"], asOf=as_of),
    }


def coverage_page(cov: dict, L: dict, sc: dict, density: str) -> dict:
    as_of = cov["asOf"][:16].replace("T", " ")
    phases, counts, total = sc["phases"], sc["counts"], sc["total"]
    groups: dict = {}
    for p in phases:
        g = groups.setdefault(p["group"] or "-", {"done": 0, "total": 0, "outputs": []})
        g["total"] += 1
        if p["status"] == "completed":
            g["done"] += 1
            for o in p["outputs"]:
                if o["exists"]:
                    g["outputs"].append(os.path.basename(o["path"]))
    cap = 7 if density == "print" else 5
    width = 22 if density == "print" else 16
    rows = []
    for name, g in list(groups.items())[:cap]:
        # The count, not the names: the column is narrow, and a truncated file
        # name is worth less than the number. The names are in the appendix.
        rows.append([clip(name, width), f"{g['done']}/{g['total']}",
                     L["outputCount"].format(n=len(g["outputs"]))])
    counts_rows = [[L["status"][k], counts[k], str(counts[k])]
                   for k in STATUS_ORDER if counts.get(k)][:5]
    data = {
        "title": clip(L["coverageTitle"].format(
            done=counts["completed"], total=total, plugin=sc["plugin"]),
            38 if density == "print" else 30),
        "basis": clip(L["coverageBasis"].format(
            done=counts["completed"], skipped=counts["skipped"],
            running=counts["in_progress"], pending=counts["pending"],
            others=sc["others"]),
            150 if density == "print" else 110),
        "headers": L["groupHeaders"],
        "counts": pad(counts_rows, 2, L["noMore"]),
        "groups": pad(rows, 2, L["noMore"]),
        "source": clip(L["source"].format(project=cov["project"]["name"],
                                          src=cov["status"]["source"] or "reports/",
                                          asOf=as_of), 170),
    }
    return render("pipeline-coverage", data, density)


def digest_page(phase: dict, L: dict, density: str,
                titles: dict | None = None) -> dict | None:
    """One completed phase, from its own recorded summary. None without one."""
    if not phase.get("summary"):
        return None
    titles = titles or {}
    written = [o for o in phase["outputs"] if o["exists"]]
    cap = 3
    body_w = 46 if density == "print" else 34
    outputs = [[clip(os.path.basename(o["path"]), 42),
                # the report's own frontmatter title says more than its folder
                clip(titles.get(o["path"]) or os.path.dirname(o["path"]) or "-",
                     body_w)]
               for o in written[:cap]] or [["-", "-"]]
    files = ", ".join(os.path.basename(o["path"]) for o in written[:3]) or "-"
    title_cap = 38 if density == "print" else 30
    head = phase["summary"].split("。")[0]
    # A truncated fact fragment makes a poor action title; label the page
    # instead and leave the whole sentence to the finding below it.
    if len(head) > title_cap:
        head = L["digestFallbackTitle"].format(phase=phase["name"])
    data = {
        "headers": L["digestHeaders"],
        "title": clip(head, title_cap),
        "phase": clip(L["phaseLabel"].format(
            phase=phase["name"], plugin=phase["plugin"],
            status=L["status"].get(phase["status"], phase["status"])), 60),
        "finding": clip_sentences(phase["summary"],
                                  200 if density == "print" else 150),
        "outputs": outputs,
        "source": clip(L["sourcePhase"].format(
            files=files, gen=(phase.get("completedAt") or "")[:16].replace("T", " ")),
            170),
    }
    return render("phase-digest", data, density)


# Most consequential first: a failed phase is a different problem from one that
# has simply not started, and only the first few rows fit on the page.
GAP_ORDER = {"phase-failed": 0, "phase-in-progress": 1, "missing-output": 2,
             "stale": 3, "open-question": 4, "phase-pending": 5}


def open_questions_page(cov: dict, L: dict, density: str) -> dict:
    # Severity first, then the pipeline's own spine before its opt-in extras:
    # "generate-test-specs not started" must not outrank a failed core phase.
    gaps = sorted(cov["gaps"], key=lambda g: (
        GAP_ORDER.get(g["kind"], 9), bool(g.get("optional")),
        g.get("tier", "core") != "core"))
    kinds = {k: sum(1 for g in gaps if g["kind"] == k) for k in
             ("phase-pending", "phase-in-progress", "missing-output", "open-question")}
    cap = 5 if density == "print" else 4
    # Per column, because they are not the same width: the "how it closes"
    # column holds a slash command and must not be truncated to an ellipsis.
    q_w, i_w, f_w = (30, 22, 36) if density == "print" else (26, 18, 28)
    rows = []
    for g in gaps[:cap]:
        phrase = L["gapPhrase"].get(g["kind"], "{phase}")
        question = phrase.format(phase=g.get("phase") or "-",
                                 detail=g.get("detail") or "-")
        # A recorded note says why better than a generic phrase can.
        if g["kind"] == "missing-output":
            impact = L["gapImpact"].format(n=len((g.get("detail") or "").split(",")))
        else:
            impact = g.get("detail") or L["gapImpactOther"]
        rows.append([clip(question, q_w), clip(impact, i_w),
                     clip(g.get("command") or L["gapFixUnknown"], f_w)])
    rows = pad(rows, 2, L["noMore"])
    first = rows[0][0] if gaps else L["nextStepsFallback"]
    steps = [[L["nextStepsHead"][0], clip(L["nextStepsBody"][0].format(first=first),
                                          50 if density == "print" else 38)],
             [L["nextStepsHead"][1], clip(L["nextStepsBody"][1],
                                          50 if density == "print" else 38)]]
    data = {
        "title": clip(L["openTitle"], 38 if density == "print" else 30),
        "lead": clip(L["openLead"].format(
            n=len(gaps), pending=kinds["phase-pending"],
            running=kinds["phase-in-progress"], missing=kinds["missing-output"],
            skipped=sum(1 for g in gaps if g["kind"] == "stale")),
            140 if density == "print" else 100),
        "headers": L["openHeaders"],
        "questions": rows,
        "nextSteps": steps,
        "source": clip(L["source"].format(
            project=cov["project"]["name"],
            src=cov["status"]["source"] or "reports/",
            asOf=cov["asOf"][:16].replace("T", " ")), 170),
    }
    return render("open-questions", data, density)


# A Slides row never shrinks below its font's line height, so the page fits a
# fixed number of rows however small rowH is set (see charts.min_table_row_h).
APPENDIX_ROWS = {"print": 11, "presentation": 8}


def appendix_pages(cov: dict, L: dict, density: str) -> list[dict]:
    """The report inventory, split across as many pages as it takes."""
    reports = [a for a in cov["artifacts"] if a["path"].endswith(".md")]
    if not reports:
        return []
    size = 8.5 if density == "print" else 10
    per_page = APPENDIX_ROWS[density]
    pages = []
    for start in range(0, len(reports), per_page):
        chunk = reports[start:start + per_page]
        rows = [[clip(os.path.basename(a["path"]), 40),
                 clip(a.get("phase") or a.get("kind") or "-", 22),
                 (a.get("generatedAt") or a.get("modified") or "")[:10]]
                for a in chunk]
        n = start // per_page + 1
        total = (len(reports) + per_page - 1) // per_page
        title = L["appendixTitle"] + (f" ({n}/{total})" if total > 1 else "")
        pages.append({
            "layout": "TITLE_ONLY",
            "title": title,
            "figures": [
                {"type": "table", "x": 0.5, "y": 1.15, "w": 9.0,
                 "headers": L["appendixHeaders"], "rows": rows,
                 "size": size, "rowH": 0.3, "headerH": 0.34,
                 "colWidths": [3.0, 1.6, 1.0], "textMargin": 0.02},
            ],
        })
    return pages


def write(pages_dir: str, number: int, name: str, slide: dict) -> str:
    os.makedirs(pages_dir, exist_ok=True)
    path = os.path.join(pages_dir, f"{number:03d}-{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(slide, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return path


def main() -> int:
    p = argparse.ArgumentParser(
        description=t("Build the deterministic pages of a nexus-architect "
                      "explanation deck"))
    p.add_argument("--coverage", required=True,
                   help=t("path to coverage.json (from scripts/nexus/collect.py)"))
    p.add_argument("--profile", choices=PROFILES, default="deep",
                   help=t("audience profile: exec (short) or deep (every "
                          "completed phase)"))
    p.add_argument("--pages-dir",
                   help=t("directory for the page fragments (default: next to "
                          "coverage.json)"))
    p.add_argument("--density", choices=("print", "presentation"),
                   help=t("density passed to the templates (default: print for "
                          "deep, presentation for exec)"))
    p.add_argument("--title", help=t("deck title (default: built from the "
                                     "project name)"))
    args = p.parse_args()

    if not os.path.isfile(args.coverage):
        raise SystemExit(t("coverage.json not found: {path}", path=args.coverage))
    with open(args.coverage, encoding="utf-8") as f:
        cov = json.load(f)
    if cov.get("schemaVersion") != SCHEMA_VERSION:
        raise SystemExit(t("unsupported coverage schema: {version}",
                           version=cov.get("schemaVersion")))

    density = args.density or ("print" if args.profile == "deep" else "presentation")
    L = LABELS.get(cov["project"].get("language") or "en", LABELS["en"])
    pages_dir = args.pages_dir or os.path.join(
        os.path.dirname(os.path.abspath(args.coverage)), "pages")

    phases = phase_rows(cov["pipelines"])
    sc = scope(cov, L)
    titles = {a["path"]: a.get("title") for a in cov["artifacts"] if a.get("title")}
    written = []

    cover = cover_page(cov, L, sc)
    if args.title:
        cover["title"] = args.title
    written.append(write(pages_dir, 10, "cover", cover))
    written.append(write(pages_dir, 20, "pipeline-coverage",
                         coverage_page(cov, L, sc, density)))

    done = [p for p in phases if p["status"] == "completed"]
    if args.profile == "exec":
        # One digest per area: the executive read is the shape of the work,
        # not its 21 steps. The richest recorded summary represents its group.
        by_group: dict = {}
        for phase in done:
            key = phase["group"] or "-"
            best = by_group.get(key)
            if not best or len(phase.get("summary") or "") > len(best.get("summary") or ""):
                by_group[key] = phase
        selected = list(by_group.values())
    else:
        selected = done

    digests = 0
    for i, phase in enumerate(selected):
        slide = digest_page(phase, L, density, titles)
        if slide is None:
            continue
        written.append(write(pages_dir, DIGEST_BASE + i * DIGEST_STEP,
                             f"digest-{phase['name']}", slide))
        digests += 1

    written.append(write(pages_dir, 900, "open-questions",
                         open_questions_page(cov, L, density)))
    if args.profile == "deep":
        for i, page in enumerate(appendix_pages(cov, L, density)):
            written.append(write(pages_dir, 910 + i, f"appendix-reports-{i + 1}", page))

    print(t("  {n} pages -> {dir}", n=len(written), dir=pages_dir))
    print(t("  {n} completed phases, {g} gaps", n=len(done), g=len(cov["gaps"])))
    if not digests:
        print(t("  note: no phase has a recorded summary; only the cover, "
                "coverage and gap pages were written"))
    print(t("  next: author the interpretive pages into the same directory, "
            "then assemble_spec.py"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
