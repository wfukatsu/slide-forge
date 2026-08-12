---
name: scalar-account-plan
description: >-
  Maintain a per-customer sales ledger (account.json) for a Scalar Account
  Executive — what is confirmed, who decides, what is unknown, what to do next —
  rendered as a Google Slides activity plan whose URL never changes. Use for an
  account plan / 活動計画 / アカウントプラン, recording what came out of a
  customer meeting, reviewing a deal's stage, forecast or BANT risk, working out
  what an AE must confirm next, or setting up an account's Drive folders. The
  annual Account Planning Session decks go to `scalar-account-planning-session`,
  one visit's materials to `scalar-ae-materials`, the customer proposal to
  `scalar-proposal-slides`, and the maps themselves to `b2b-account-maps`.
---

*[日本語](SKILL.ja.md)*

# Scalar Account Plan

One ledger per customer. **The ledger is the single source of truth**; the
deck is just a rendering of it. Append to the ledger after every visit, and
refresh the deck at the same URL.

Two kinds of deck come out of the ledger. They have different lifespans and
inputs, so don't mix them. **This skill covers the left one.**

| | Activity plan deck (§5) | APS deck |
|---|---|---|
| Purpose | Where things stand now and what's next | Annual/half-year review and executive review |
| Updated | After every visit | At each APS |
| Input | `account.json` (the ledger) | `aps.json` (the ledger + the customer's public information) |
| Skill | **This skill** | `scalar-account-planning-session` |

Working directory: the slide-forge root. Run commands with `.venv/bin/python`.

The source of truth for these decisions is
[references/scalar/sales-playbook.md](../../references/scalar/sales-playbook.md).
Stages, gate IDs, the 5 material types, BANT, and the 10-question checkpoint
are all defined there. **Do not redefine them in this skill.**

## Boundaries

| Request | Where it goes |
|---|---|
| Create / append to the activity plan, or answer about status | This skill (§5) |
| Build materials for an Account Planning Session | `scalar-account-planning-session` |
| Build a full set of materials for one visit | `scalar-ae-materials` |
| Draw the stakeholder map / discovery map itself | `b2b-account-maps` |
| Formal customer-facing proposal | `scalar-proposal-slides` |
| Itemized quotation | `spreadsheets` |
| Visual inspection of a generated deck | `slide-qa` |

## This is an internal document

The activity plan records judgments about named individuals (influence,
position, whether they've been contacted). **Never hand it to the customer
or a partner.** On Drive, `00_活動計画` and `90_社内` are never shared.
Only what has been placed under `01_顧客提示` / `02_顧客提案` may be shown to
the customer.

## Locations

```
config/sales.json                       Drive ルートと既定 AE 名（gitignore 済み）
accounts/<AE 名>/<顧客名>/account.json   ★ 正本（gitignore 済み。コミットしない）
accounts/<AE 名>/<顧客名>/aps.json       APS デッキの内容（別スキルが使う。同上）

Drive: <ルート>/<AE 名>/<顧客名>/
  00_活動計画/  活動計画デッキ（URL 不変）・account.json のコピー・action-plan.md
  01_顧客提示/  顧客提示用
  02_顧客提案/  顧客提案用
  90_社内/      社内説明用
```

## Workflow

### 1. Prepare the ledger

Read it if it already exists. Create it if it doesn't.

```bash
.venv/bin/python scripts/scalar/account_ledger.py init --ae "<AE 名>" --customer "<顧客名>" \
    --opportunity "<商談名>"
```

Ask for the Drive root only the first time and build the hierarchy from it
(after that, use the setting in `config/sales.json`). **Always confirm with
the user when the root is not set. Never create it under My Drive root on
your own.**

```bash
.venv/bin/python scripts/scalar/account_workspace.py ensure \
    --ledger accounts/<AE>/<顧客>/account.json [--root "<Drive フォルダ URL>"]
```

### 2. Fill it in from material at hand (read before asking)

Read minutes, meeting notes, emails, and CRM exports first. Only then, **ask
for what's still missing, in a single batch**
(`references/interactive-intake.md` §0, §5).

When writing to the ledger, always distinguish `facts[].kind`:

| kind | Meaning | Can it be promoted to `confirmed`? |
|---|---|---|
| `said` | The customer said so (who, when) | Yes |
| `observed` | Confirmed via a document, org chart, or a quote sent | Yes |
| `assumed` | Our own inference | **No** |

Status rules follow
[b2b-account-maps's discovery-map.md](../b2b-account-maps/references/discovery-map.md).
Don't define them twice.

**Never do this:**

- Place someone you haven't met at the center of the influence map as
  "neutral" (put not-yet-contacted people in `gaps`)
- Mark something `confirmed` based on a guess (`confirmed` entries with no
  `evidence` fail validation)
- Write down a number the customer never said

### 3. Validate

```bash
.venv/bin/python scripts/scalar/account_ledger.py validate accounts/<AE>/<顧客>/account.json
```

Inconsistencies get caught here — an unsubstantiated `confirmed`, a `met`
gate with no evidence, an action with no due date or completion condition, a
`Commit` forecast when BANT isn't complete. **Fix the ledger. Don't loosen
the validation.**

### 4. Turn open items into actions (the heart of this skill)

```bash
.venv/bin/python scripts/scalar/account_ledger.py gaps accounts/<AE>/<顧客>/account.json
```

Of the 10 questions in playbook §7, the ones that can't be answered come out
with who to confirm with and the completion condition. **Never fill in the
answer yourself.** Leave open items open, pull them into `actions` with
`--carry-over`, and **only let the user set the due date** (the due date is
the AE's commitment, not something this tool decides).

`--carry-over` is a flag on the following two commands (both rewrite the
ledger before printing output):

```bash
# アクションプランの Markdown を出すついでに取り込む
.venv/bin/python scripts/scalar/account_ledger.py actions <account.json> --carry-over

# デッキ生成（§5）のついでに取り込む
.venv/bin/python scripts/scalar/build_account_plan.py <account.json> --carry-over
```

Unfinished actions from last time carry forward as-is. Overdue ones trigger
a validation warning.

### 5. Build / update the activity plan deck

```bash
# 検証（API を呼ばない）
.venv/bin/python scripts/scalar/build_account_plan.py <account.json> --dry-run --strict

# 初回 — 00_活動計画 フォルダに新規作成
.venv/bin/python scripts/scalar/build_account_plan.py <account.json> --folder <00_活動計画 の ID>

# 2 回目以降 — 同じ URL の中身を差し替える（台帳の meta.decks.activityPlan を自動で使う）
.venv/bin/python scripts/scalar/build_account_plan.py <account.json>
```

The default 9 pages (excluding the cover) are ordered to be read in this
sequence:

`account-snapshot` (where things stand now) → `phase-gate` (what's not yet
met) → `bant-risk` (where the risk is) → `discovery-map` (what's unknown) →
`pain-chain` (why it works) → `influence-map` / `buying-committee` (who to
move) → `activity-timeline` (who's been reached so far) → `action-plan`
(what to do next)

**A page with insufficient material is automatically dropped.** Dropped
pages are listed in the report. Don't build a thin page with blanks filled
in — it's correct for what's missing to show up in `action-plan` instead.

`--pages` can add `visit-plan` / `win-plan` / `discovery-gaps`. These 3 are
for a single visit or a single WPS and have a different lifespan, so they
don't belong in the standing activity plan.

#### Updates after the first one are destructive

`--into` **deletes all pages of the existing deck** before rebuilding it.
Secure a version snapshot before running it:

```bash
.venv/bin/python scripts/snapshot_version.py "<デッキ URL>"
```

`build_account_plan.py` prints the pre-edit revision ID. To roll back, use
"File → Version history" in the Slides UI.

What `--into` refuses (all of these are intended behavior):

| Replace target | Result |
|---|---|
| **The template's own master** (the `presentationId` in `templates/*.json`) | Refused. Breaking the master would lose the source for every deck built from that template |
| A deck built from a different master | Refused (layouts can't be found) |
| A template type built with `predefinedLayout` (e.g. `blank-16x9`) | Refused (a real layout is required) |

**Take the replace-target URL from the ledger's `meta.decks.activityPlan`.**
When pasting a URL by hand, always confirm it's a generated deck, not the
master.

### 6. Annual / half-year review (APS)

The annual/half-year account review and executive review materials belong to
[`scalar-account-planning-session`](../scalar-account-planning-session/SKILL.md).
Its input is not the ledger but `accounts/<AE>/<customer>/aps.json`, built by
adding the customer's public information (mid-term business plan, org chart,
executive roster) to the ledger.

**This skill does not go that far.** The ledger (§1–4) is a prerequisite for
APS, so bring the ledger up to date first, then hand off to the APS side.

### 7. When there are more than 9 stakeholders

Don't cram them onto a slide. As with `b2b-account-maps`'s default, output
the whole graph to draw.io and put an extracted version on the slide,
**always noting the number of people dropped and where to find the full
version** (the `more` slot).

**Decide the layout first.** The default tree layout spreads horizontally
by the number of roots. With many roots, like a corporate group, it becomes
an unreadable band (49 people at 18,000 × 709px).

| Shape of the graph | What to use |
|---|---|
| One company, a single chain of command (1–2 roots) | Default (`--layout tree`) |
| **Corporate group, 3+ roots** | **`--layout grouped`** |

```bash
# 企業グループ。people[].entity ごとの枠に格子で並べ、法人をまたぐ線は枠の外を通す
.venv/bin/python scripts/build_account_graph.py <graph.json> --layout grouped \
    --title "<顧客> インフルーエンスマップ（全体）" \
    --out out/account-plan/<顧客>/influence-map-full.drawio

# 1 社なら既定のままでよい
.venv/bin/python scripts/build_account_graph.py <graph.json> \
    --out out/account-plan/<顧客>/influence-map-full.drawio

# PNG に書き出す（drawio CLI が要る）
drawio -x -f png -s 2 -b 8 \
    -o out/account-plan/<顧客>/influence-map-full.png \
       out/account-plan/<顧客>/influence-map-full.drawio
```

- `entity` is the legal-entity name (`entityOrder` sets the frame order).
  Use the same unit as the org chart
- **For connections between people (`links`), put only the number on the
  line and list the wording below the diagram.** A label placed on the line
  itself overlaps the card the longer the line gets, and becomes unreadable
- Always put the `.drawio` and PNG in the deck's Drive folder. A PNG alone
  can't be edited

### 8. Visual inspection and cleanup

Check the thumbnails with the `slide-qa` skill. Pay particular attention to:

- On the influence map, does **the person to move next** catch the eye first
  (squint test)?
- Do table rows overlap the logo band at the bottom edge?
- Do person labels hide each other? If so, **fix the coordinates in the
  ledger** (not the template)

When done, run `.venv/bin/python scripts/cleanup_qa.py`.

### 9. Report, together with Drive

```bash
.venv/bin/python scripts/scalar/account_workspace.py ensure --ledger <account.json>
.venv/bin/python scripts/drive_folder.py upload <00_活動計画 の ID> \
    accounts/<AE>/<顧客>/account.json out/account-plan/<顧客名>/action-plan.md
```

Always include in the report:

1. The deck URL and the Drive folder URL
2. The stage/forecast and its basis
3. **The shortest list of what to confirm next** (who, by when, and what
   completion looks like)
4. If any page was dropped for insufficient material, its name and what's
   missing

Item 3, not the URL, is the point of the report. The deck is a means; the
AE's next action is the deliverable.

## Rules

- **The ledger is the source of truth. Never edit the deck directly.** If
  something needs fixing, fix the ledger and rebuild.
- **Never replace the CRM.** Stage, amount, expected date, and Next Action
  live in the CRM as the source of truth. When you update the ledger, keep
  the CRM in sync too (playbook §8).
- **Evidence, or else unconfirmed.** `confirmed` and `met` require a source
  (who, when).
- **Never fill in an answer.** A blank is the AE's next action, not a hole
  to fill.
- **An outdated activity plan is worse than none.** If it can't be kept
  updated, retire the ledger along with it.
- Do not commit `accounts/` or `config/` (they contain customer names,
  personal names, and judgments). Keep working files under the
  gitignored `out/`.
