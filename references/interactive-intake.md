*[日本語](interactive-intake.ja.md)*
# Nailing Down a Deck's Design Through Dialogue

The procedure for confirming the **template, purpose, structure, and length** with the user
before building a deck. Use whatever interactive-question feature is available on the host, and
present decisions as multiple-choice options. Under Codex, follow the question rules in the root
`AGENTS.md`.

This skill's generation follows an "edit the spec and rebuild" convention, so **generating 40
slides with a wrong premise means rebuilding the whole thing**. Confirm the premise before
generation, all at once.

## When another skill references this one

Sections **0 (when to ask), 3 (the outline approval gate), 4 (post-generation confirmation), and
5 (question styles to avoid) are conventions shared regardless of deck type.** Skills built on
top of this one (e.g. `scalar-product-slides`) refer to these sections and follow them.

Sections **1 and 2's question sets are specific to this skill** (starting from template
selection). Skills with their own dedicated workflow should own a question set suited to their
own branching, borrowing only the conventions from here.

---

## 0. When to ask, and when not to

**Don't ask** (decide it yourself and proceed):

- Anything the user has already specified. If told "10 slides for a talk, using scalar-2026,"
  the template, category, and length are all already settled. Only ask about what's left.
- When told "use your judgment," "whatever," or "just make it quick." Assemble it with the
  defaults, **state the premises you adopted in one line** before generating (never decide
  silently).
- Anything `config/settings.json` already decides — whether Gemini generates images at all, and
  whether the deliverable is Google Slides or a local `.pptx`. **Read them before the Q2 set**
  (`.venv/bin/python scripts/settings.py --show`) and drop the questions they answer; see
  `references/settings.md`. A request to *change* them goes to the `settings` skill, not here.
- Coordinates, font sizes, choice of figure parts, colors. These are **your responsibility**, not
  something to hand to the user to choose. When in doubt, follow the conventions in
  `references/`.
- Minor edits to an existing deck, regenerating a catalog or demo, or any work with no design
  branch point.

**Do ask**:

- For a new deck, when any of template, purpose, structure, or length is unspecified.
- For any branch point where the choice **triggers a rebuild** (template, Proposal vs.
  Presentation category, structure type, expected length, output destination folder).
- The pre-generation outline approval (the gate described below). Never skip this.

**Ask in batches.** At most 4 questions per round, 2–4 options per question. Don't go back and
forth one question at a time — stay within **at most 3 round trips**: the Q1 set (4 questions) →
the Q2 set (only what's still needed) → outline approval.

---

## 1. Q1 set — deciding the premise

Asked once, up front. The option wording below can be reused as-is, but **build the template
options from live data** (so they don't go stale as registrations change):

```bash
.venv/bin/python scripts/list_templates.py        # human-readable form
.venv/bin/python scripts/list_templates.py --json # material for building options
```

| # | header | Question | How to build the options |
|---|---|---|---|
| 1 | Template | Which template should we use? | Up to 3 entries from `list_templates.py`'s output, plus "Parse and register a new URL." Put "N layouts / N boilerplate slides included" in `description`. If the user has no existing template and wants a brand-new design matched to their brand, point them to the `template-forge` skill instead |
| 2 | Purpose | What is this deck for? | Proposal / sales material (Proposal category + template density `print`) / conference talk or study session (Presentation category + density `presentation`) / internal sharing or reporting (Proposal category + density `print`). The answer fixes **both** the layout family and the density variant of every registered slide template used in the deck. If the template has no notion of category, don't skip — ask the reduced two-option form instead: 「このデッキはプレゼン投影用ですか、印刷・配布用ですか？」 (投影用 → `presentation` / 印刷・配布用 → `print`), whenever templated slides will be used |
| 3 | Structure | Which structure should we build it with? | 3 types from `references/deck-outlines.md`, plus "Build it to match the content." **Put section headings into `preview`** so they're easy to compare |
| 4 | Length | About how many slides? | ~10 slides (15 min) / ~20 slides (30 min) / 40+ slides (detailed version, with appendix) |

The actual call (substitute values to match `list_templates.py`'s output):

```json
{
  "questions": [
    {
      "header": "テンプレート",
      "question": "どのテンプレートで作りますか？",
      "multiSelect": false,
      "options": [
        {"label": "scalar-2026 (推奨)", "description": "Scalar Slide Master 2026。8 レイアウト・Proposal / Presentation の 2 系統。まっさらな状態から作る"},
        {"label": "scalar-2026-boilerplate", "description": "同じマスターに会社概要・製品概要など定型スライド 12 枚が同梱。会社紹介を含むデッキ向け"},
        {"label": "aixdevops", "description": "AIxDevOps 共同ブランド。22 レイアウト・2/3 カラムあり"},
        {"label": "新しい URL を解析して登録", "description": "手元の Google Slides をテンプレートとして解析する。ロール確認の手間が 1 回だけ増える"}
      ]
    },
    {
      "header": "用途",
      "question": "このデッキは何に使いますか？",
      "multiSelect": false,
      "options": [
        {"label": "提案書・営業資料", "description": "Proposal 系レイアウト。フッターと © 表記あり。読み物として配布される前提で文字は多め（テンプレート密度 print）"},
        {"label": "登壇・勉強会", "description": "Presentation 系レイアウト。タイトル領域が広い。1 枚 1 メッセージで文字は少なめ（テンプレート密度 presentation）"},
        {"label": "社内共有・報告", "description": "Proposal 系。数値と根拠を厚めに、装飾は控えめに組む（テンプレート密度 print）"}
      ]
    },
    {
      "header": "構成",
      "question": "どの構成で組みますか？",
      "multiSelect": false,
      "options": [
        {"label": "課題解決型の提案", "description": "現状 → 課題 → 打ち手 → 効果 → 進め方。営業・導入提案の定番",
         "preview": "1. 背景と現状\n2. 課題（3 点に絞る）\n3. 打ち手\n4. 期待効果（数値）\n5. 進め方とスケジュール\n6. 体制・費用"},
        {"label": "新規事業・企画の稟議", "description": "才流の 15 セクション。承認者の不安を先回りして潰す順序",
         "preview": "1. 背景 / 2. 課題と市場性\n3. ターゲット・市場規模\n4. 事業内容 / 5. 顧客の声\n6. 競争環境 / 7. スケジュール\n8. 収益性 / 9. 投資・コスト\n10. リスク / 11-12. 体制\n13. 法規 / 14-15. 声・全社戦略"},
        {"label": "製品・サービス紹介", "description": "課題 → 製品 → 特長 → 事例 → 次のステップ",
         "preview": "1. 顧客の課題\n2. 製品の位置づけ\n3. 特長（3 つ）\n4. 仕組み・アーキテクチャ\n5. 導入事例\n6. 次のステップ"},
        {"label": "内容に合わせて組む", "description": "定型に当てはめず、渡した素材から構成を起こす。まずアウトライン案を出して確認する"}
      ]
    },
    {
      "header": "分量",
      "question": "目安の枚数はどのくらいですか？",
      "multiSelect": false,
      "options": [
        {"label": "10 枚前後", "description": "15 分の説明向け。1 セクション 1〜2 枚"},
        {"label": "20 枚前後", "description": "30 分の説明向け。標準"},
        {"label": "40 枚以上", "description": "詳細版。読み物として配布する・Appendix を持たせる場合"}
      ]
    }
  ]
}
```

**How the density answer is applied.** Registered slide templates with
`$density` variants (e.g. the `read-alone` pack) are rendered by passing the
chosen density to every `render_slide_template.py --density …` call; templates
without variants ignore it. For a `print` deck, the spec may additionally set
spec-level `defaults` (e.g. `"bodyFontSize": 10`) so non-templated body slides
match the handout density — an existing spec feature, no engine flag needed.

---

## 2. Q2 set — deciding the premises for the content

Ask only about what Q1's answers didn't settle. There's no need to ask all of them.

| header | Question | Options |
|---|---|---|
| Use of figures | Which visual treatments should we use? (multiple allowed, `multiSelect: true`) | Tables/charts / illustrative diagrams or frameworks / cloud architecture diagrams / code samples |
| Page type | Which page structures should we build with? (for handout materials) | Choose from 6 skeleton types. Generating `examples/slide-pattern-index.json` and showing the real thing is faster |
| Materials | Do you have source content? | Have it on hand (provide a path/URL) / carry over from an existing deck / we'll research it / placeholder (leave as ○○) |
| Output destination | Where in Drive should it go? | My Drive root / a specified folder (URL or ID) / append to an existing deck |
| Cover | What information goes on the cover? | Date + company name / date only / none |
| Verification | Run visual QA (thumbnail verification) after generation? | Run it (recommended, default) / skip it (generation only; can be run later via the `slide-qa` skill) |
| Output format | In addition to Google Slides, also export to PowerPoint (.pptx)? | Google Slides only (default) / also export PPTX (for delivery/distribution; exported after generation via the `pptx-export` skill). **Skip this question when `output` is set in `config/settings.json`** — `local` already means the .pptx is the deliverable |
| Cost breakdown | Also produce a cost/composition breakdown (quotation) as a spreadsheet? | No (default; slide summary only) / yes — Excel + Google Spreadsheet (via the `spreadsheets` skill; placed in the same Drive folder as the deck, with the total matching the slides) |

Notes:

- **If "cloud architecture diagram" is chosen, first check whether
  `scripts/fetch_cloud_icons.py` has already ingested them** (generation halts if it hasn't).
- **AI images (`aiImage`) require a billed `GEMINI_API_KEY`.** If the answer indicates they plan
  to use one, check for a key first; if there isn't one, propose a shape-based alternative
  (`illustrations` / `patterns`). A free-tier key has zero quota for the image model and fails
  with a 429 at generation time. **When `imageGeneration` is off in `config/settings.json`,
  don't offer AI images or ask about the key at all** — go straight to the shape-based
  alternative (the engine refuses `aiImage` at validation time anyway).
- If materials are "we'll research it," **never fill in numbers by guessing.** Anything without
  a verifiable source becomes an `○○` placeholder, and tell the user so.
- **For "verification," default to putting "run it" first (recommended).** Mention in the
  `description` that text overflow or mis-wired connectors can't be detected from the API
  response alone. If "skip it" is chosen, treat generation alone as complete, and state clearly
  in the final report that QA was not performed. The QA procedure (fetch thumbnails → visual
  review → fix loop → delete verification files) is owned by the `slide-qa` skill.
- **Only ask about "output format" when PPTX delivery/distribution is expected** (proposals,
  customer-facing materials, etc.), **and only when `config/settings.json` leaves it open.** With
  `output: local` the deck is exported to the local folder automatically after generation, so
  state that as a premise instead of asking, and report the local path next to the deck URL.
  Don't ask for conference talks or internal sharing — default to Google Slides only. If "also export PPTX" is chosen, export via the `pptx-export` skill
  only **after generation and QA are both fully complete** (an export is a snapshot, so
  regenerating the deck requires re-exporting). Procedure and fidelity notes are owned by that
  skill.
- **Only ask about "cost breakdown" when the deck will carry cost/composition figures**
  (proposals, approval requests, decks with a BOM). If "yes" is chosen, generate the quotation
  breakdown as Excel + Google Spreadsheet via the `spreadsheets` skill, placed in the same Drive
  folder as the deck. Keep the slide side to totals/summary only, and always make the
  breakdown's total match the number on the slide. Unit prices and tax rates come from the user
  or the source material (never fill them in by guessing — anything missing becomes `○○`).

---

## 3. Outline approval gate (never skip)

**Present the draft outline as text** from the Q1/Q2 answers, then get approval. The JSON spec
and slide generation come after this.

What to present (write it in the chat body; don't paste long JSON):

```
全 18 枚 / scalar-2026 / Proposal 系 / 課題解決型

 1  COVER       表紙
 2  CONTENT     アジェンダ
 3  SECTION     1. 背景と現状
 4  TITLE_ONLY  受注処理は月 120 時間を手作業に費やしている   [hbars]
 …
18  CLOSING
```

Then get approval:

```json
{
  "questions": [{
    "header": "構成の確認",
    "question": "このアウトラインで生成に進みますか？",
    "multiSelect": false,
    "options": [
      {"label": "これで生成する", "description": "この構成で JSON 仕様を書き、--dry-run で検証してから生成する"},
      {"label": "枚数を減らす", "description": "各セクションを 1 枚に圧縮し、詳細は Appendix に回す"},
      {"label": "セクションを増減する", "description": "追加・削除したいセクションを指定してもらう"}
    ]
  }]
}
```

**Once the outline is approved, run everything through to the end without asking anything
further.** Writing the spec → `--dry-run --strict` → generation → (if verification was chosen)
thumbnail QA form one continuous piece of work; inserting a confirmation partway through only
adds waiting time.

---

## 4. Confirmation after generation

**If verification was chosen as "run it,"** finish QA yourself first (`slide-qa` skill: visual
review of thumbnails → fix → delete verification files with `cleanup_qa.py`) **before**
delivering the result. Don't make the user find defects that a visual check would have caught.
**If it was "skip it,"** treat generation plus the report as complete, and state clearly in the
final report both that QA was not performed and that it can be run later via `slide-qa`.
After that, only ask if there's room to refine it:

| header | Question | Options |
|---|---|---|
| Finishing touches | Should we finalize this as-is? | Finalize / revise the wording / change how a figure is presented / adjust the slide count |

Fixes are made by **editing the spec and rebuilding** (never a partial edit). When rebuilding,
**delete the old generated output from Drive first**, then regenerate (never leave stale
leftovers behind).

---

## 5. Question styles to avoid

- **Asking one question at a time.** It only adds round trips. Ask about the premises together,
  in one go.
- **Asking when you already have the answer.** Don't ask back "What templates are available?"
  when running `list_templates.py` would tell you.
- **Asking as free text instead of offering options.** Instead of "How should we structure it?",
  present 3 types to choose from. If none fit, the user can always write their own ("Other").
- **Stopping generation to ask.** Don't pause outside the approval gate. Push forward on
  anything that doesn't need an answer yet, and defer only the parts that depend on one.
- **Asking, then not reflecting the answer.** Once you've asked, the answer must always be
  reflected in the spec. For an answer that can't be honored (e.g. a layout the template doesn't
  have), explain why on the spot and offer an alternative.
