*[日本語](usecase.ja.md)*
# Composing Use-Case Pages

The pages that turn a product into a reason to act: what the situation is, what
it costs to leave alone, what changed for someone who fixed it, and what the
next step is. Each entry says what the page has to establish and what to build
it from today.

Many of these already exist as registered slide templates — `case-study-card`,
`case-study-detail`, `case-fit`, `outcome-before-after`, `roi-payback`,
`poc-plan`. Prefer the template: it carries the guardrails with it.
`list_slide_templates.py --pack case-studies` and `--pack proposal` list them.

## Use-case overview

Which situations this product is for, so a reader can tell within one page
whether they are in one of them.

**Build it with**: `cards` or `icon_grid`, one card per situation, each named
by the customer's circumstance rather than by our capability — "決算処理が
夜間バッチに間に合わない", not "高速なトランザクション".

Three to five. Beyond that the reader stops matching themselves against them.

## Problem to solution

The contrast the whole deck rests on: the situation now, and the situation
after. Both halves must describe the *same* thing, in the same order.

**Build it with**: `before_after`, or `challenge-solution-map` when several
problems map to several capabilities, or `iceberg-challenge` when the visible
complaint is not the real cause.

If the left and right halves do not correspond item for item, it is not a
contrast — it is two lists.

## Case study

One customer's story: the situation, what they did, and what changed —
with numbers they have agreed can be shown.

**Build it with**: `case-study-detail` for one customer in depth,
`case-study-card` for three in brief, and `case-fit` for the page that says why
this case applies to the customer in the room.

Every figure needs its source and its date. Anything not cleared for external
use does not go in a customer-facing deck, and that is a judgement no validator
makes for you.

## Before and after

The measurable difference, on one page.

**Build it with**: `outcome-before-after` (the proposal template) or the
`before_after` figure; `hbars` when the change is one quantity, `waterfall`
when it decomposes into contributions.

Give the measurement basis — over what period, measured how. A before/after
without it is a claim, not evidence.

## ROI and impact

What the change is worth, and when it pays back.

**Build it with**: `roi-payback` for investment and payback period,
`break-even` for the crossing point, `sales-buildup` when the benefit
decomposes. `metric` for the single number the page is about.

State the assumptions on the same page as the result. An ROI whose inputs are
elsewhere cannot be argued with, which is the opposite of what it is for.

## Deployment steps

What adoption actually involves, phase by phase, with what is decided at each.

**Build it with**: `steps` or `flow` for the sequence, `poc-plan` when the
first phase is a PoC with pass/fail criteria, `gantt-schedule` when the phases
have dates, `phase-gate` when each phase has an exit condition.

Name who does what in each phase. A deployment plan that never names the
customer's side is a plan they have not agreed to.
