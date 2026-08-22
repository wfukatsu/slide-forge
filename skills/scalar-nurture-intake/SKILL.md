---
name: scalar-nurture-intake
description: >-
  Turn raw pre-deal signals — webinar and seminar attendance, inbound enquiry
  email, download logs, community and Slack questions, event badge notes,
  partner referrals, CRM/MA exports — into segment definitions, five-stage
  nurture tracks and a content ledger, using the nurture map derived from the
  Scalar nurture plan sheet. Use when asked to 「ナーチャリングを設計して」
  「リード育成」「問い合わせからセグメントを起こして」「ウェビナーの参加者を整理して」
  「コンテンツの棚卸し」「MQL / SQO」, to work out which content is missing for a
  segment, or to decide whether a lead is ready to hand to sales. Works on
  segment types, never on named individuals or customers. Once a lead is handed
  over, the per-customer records go to `scalar-deal-intake`, the deck to
  `scalar-product-slides`, and the customer proposal to `scalar-proposal-slides`.
---

*[日本語](SKILL.ja.md)*

# Scalar Nurture Intake

Pre-deal signals in, nurture design out. This skill produces Markdown under
`accounts/_nurture/`. It generates no slides.

Working directory: the slide-forge root.

Sources of truth — this skill redefines none of them:

| Concern | Source |
|---|---|
| The five nurture stages, the product and segment layers, what the sheet leaves unfinished | [`references/scalar/nurture-map.md`](../../references/scalar/nurture-map.md) |
| The deal stages a lead is handed to, and the `g1.*` gates | [`references/scalar/stage-io-map.md`](../../references/scalar/stage-io-map.md), [`sales-playbook.md`](../../references/scalar/sales-playbook.md) |
| Problem-to-product mapping | [`references/scalar/proposal-map.md`](../../references/scalar/proposal-map.md) |

## Boundaries

| Request | Where it goes |
|---|---|
| Define a segment; design a nurture track; audit content coverage | This skill |
| Decide whether a lead is ready for sales | This skill (§6) |
| Records for one named customer once a deal exists | `scalar-deal-intake` |
| The account ledger and activity-plan deck | `scalar-account-plan` |
| Materials for one visit | `scalar-ae-materials` |
| Company / product decks (not customer-specific) | `scalar-product-slides` |
| Customer-specific proposal | `scalar-proposal-slides` |

## Nurture files hold types, not people

A segment is a **pattern**, not a person or a company. Attendance lists, enquiry
email and CRM exports contain personal data; the nurture files must not.

- Never write a personal name, a company name, an email address or a job title
  tied to an individual into `accounts/_nurture/`.
- Aggregate the signal into the type: "three enquiries in the last quarter from
  MySQL users hitting column overloading" — not who sent them.
- If a signal matters because of *who* it came from, it is a deal, not a
  segment. Route it to `scalar-deal-intake`.

`accounts/` is gitignored. Do not commit filled files either way.

## Workflow

### 1. Read everything supplied first

Read the attendance log, enquiry email, download log, community thread, event
notes, partner referral and CRM/MA export before asking anything. Accept local
paths, pasted text, Drive URLs and Gmail threads.

Record what was read as counts and dates — "webinar 2026-07-15, 42 attendees,
11 with questions" — not as a roster.

### 2. Locate the segment

```bash
ls accounts/_nurture/segments/
ls accounts/*/            # live deals — always check before segmenting
```

**First, check whether the signal came from someone already in a live deal.**
Sending nurture content to a contact inside a running deal is an incident.

| Outcome of the check | What to do |
|---|---|
| From a customer with a live deal | **Keep it out of the segment.** Route to `scalar-deal-intake`; the material belongs in that deal's `deal-log.md` §1 |
| Same customer, different division or use case | **Tell the AE first.** Whether it goes into nurture is the AE's call |
| No deal | Proceed with segmentation as normal |

Recording that the check happened is fine, but **never write the company or personal
names used for the check into `accounts/_nurture/`** — record counts only, e.g.
"1 overlap with a live deal, excluded".

Match each signal against the existing segment definitions and against
`nurture-map.md` §5. For each signal, one of three outcomes:

| Outcome | What to do |
|---|---|
| Matches an existing segment | Add the evidence to that track |
| Close to one, but the situation differs | Record it as a variant on the existing segment. Do not fork a new one yet |
| Matches nothing | Park it in a "candidate segments" list with the count |

**Do not create a segment from a single signal.** One enquiry is an anecdote.
Promote a candidate to a numbered segment when the same situation appears at
least three times, or when someone decides deliberately to invest in it — and
record which of the two it was.

When you do number one, check the existing list first and never reuse an ID.
The source sheet has a duplicate `AWS #009` (`nurture-map.md` §7-2); do not add
another.

### 3. Judge the nurture stage

Stage is set by **what the buyer is looking for** (`nurture-map.md` §1), not by
how much they downloaded.

| Signal | Stage |
|---|---|
| Does not yet see anything to fix | 0. Education |
| Knows the problem, no project, has not narrowed it down | 1. Need |
| Looking for products that solve it | 2. Research |
| Comparing and narrowing candidates | 3. Evaluation |
| Deciding to buy | 4. Selection |

**"Attended a webinar" is not a stage.** State the buyer situation that puts them
there, and cite the signal it came from.

### 4. Fill the track

```bash
mkdir -p accounts/_nurture/segments accounts/_nurture/tracks
cp templates/nurture/segment-sheet.ja.md accounts/_nurture/segments/<Segment No.>.md
cp templates/nurture/nurture-track.ja.md accounts/_nurture/tracks/<Segment No.>.md
cp templates/nurture/content-inventory.ja.md accounts/_nurture/content-inventory.md
```

Snapshot before editing an existing file (`cp x.md x.md.bak-YYYYMMDD`) and append
rather than overwrite.

What the raw material is actually good for:

| Material | What it feeds |
|---|---|
| Questions asked at a webinar or in a community | §7 power script — the objections and the branches |
| Enquiry email wording | §1–§5 story, in the buyer's own words |
| What they downloaded, and in what order | Content coverage (§10) and the stage judgement |
| What they asked that we could not answer | §11 open items, and a content gap |
| Why a lead went quiet | §6 re-engagement |

Write the story as the buyer's narrative, not the pitch. Keep unverified claims
marked `（仮説）` — the source sheet does this and it is worth copying.

### 5. Update the content ledger

**The thin stages have templates**: `value-message` for 0–1,
`use-case-one-pager` for 1–2, `whitepaper-abstract` for 3, the `case-studies`
pack for cases, and `event-announce` / `session-agenda` / `speaker-intro` for
events. The briefs behind them live in `templates/marketing/`.

Fill §2 (coverage by stage) in `content-inventory.md`. **The stage with the most
`無` is where the track is stuck** — say so explicitly rather than listing every
gap flatly.

Apply the three-month rule to case studies, pricing, edition structure and
performance numbers (`nurture-map.md` freshness warning). Mark stale entries
`要更新`; never delete them.

### 6. Decide the hand-off or the re-engagement

The sheet defines neither MQL nor SQO, so use the deal-side gates
(`nurture-map.md` §2):

| Judgement | Gate |
|---|---|
| May approach as MQL → SQO | `g1.problem-recognized` |
| May open deal stage 1 | `g1.owner-reached` |
| May move to deal stage 2 | `g1.timeframe-6q` |

Verdicts are `met` / `partial` / `unmet`. A download or a webinar seat is never
evidence for `met`.

**Do not derive the deal stage from the nurture stage.** The nurture stage marks
where the buyer's interest sits; the deal stage marks what has been agreed — two
different rulers (`nurture-map.md` §2). **Open at deal stage 1 as a rule.** A lead
arriving from nurture 4 (Selection) is not "in deal stage 4"; it is **"in deal
stage 1, with only the customer's clock at stage 4."** Do not propose moving to a
proposal with `g2.goal-agreed` and `decisionCriteria` skipped. Where discovery has
to be compressed, hand over what was dropped as a risk for `deal-log.md` §3.

When a lead does cross over, hand to `scalar-deal-intake` with: the contact
history, which content they consumed, the questions they asked, and the
questions still unanswered. **The named-individual detail lives only on the deal
side**, under `accounts/<AE>/<customer>/`.

When a lead has gone quiet, fill §6 instead: which stage they stalled at, the
likely reason, which stage to return them to, and what content to send.

### 7. Report the diff

In Japanese:

1. Files created or updated, and what was added
2. Which segments the signals landed in, and which are still candidates (with counts)
3. The stage where content is thinnest, and what to build next
4. Leads ready to hand to sales, with the gate evidence
5. Anything the material contradicts in an existing track

## Refusals and cautions

- Do not put a personal name, company name or contact detail into
  `accounts/_nurture/`. If the request needs that, it belongs in
  `scalar-deal-intake`.
- Do not create or number a segment from one signal.
- Do not judge stage by activity volume.
- Do not treat the sheet's product positioning as current — it is from 2021 and
  omits ScalarDB Cluster, ScalarDB Analytics and cross-RDB transactions
  (`nurture-map.md` §7-8). Say so when a segment is built on the old framing.
- Do not invent metrics targets. The source has none (`nurture-map.md` §7-10);
  leave the target column empty and say it needs a decision.
- **Never copy event answers straight into `accounts/_nurture/`.** The
  collection slides are `hearing-slides` and the sheet behind them is
  `hearing-sheet`. Only aggregates — type and count — belong here; an answer
  that identifies a company or a person is a deal, and goes to
  `scalar-deal-intake` (`references/hearing-kit.md` §4).
- **Never write consent or opt-out records into `accounts/_nurture/`.** They are
  tied to individuals and belong in MA/CRM (`nurture-map.md` §8). What goes in the
  nurture files is the type-level fact of which consent basis each reach channel
  rests on (`segment-sheet.ja.md` §4).
- **Do not rule on whether sending is lawful.** Present the consent / opt-out /
  disclosure points from `nurture-map.md` §8 and **report that legal must confirm**.
  A track whose reach channels have no consent basis recorded is **never reported as
  ready to send**.
- Do not copy the nurture stage number into the deal stage (see §6).
