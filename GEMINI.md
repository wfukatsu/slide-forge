*[日本語](GEMINI.ja.md)*

# slide-forge Project Guidelines for Antigravity

This repository is an integrated engine (`slide-forge`) for Google Slides deck generation, infographic creation, visual QA, PPTX conversion, and spreadsheet generation.

## 1. Runtime rules

- **Python version / venv**:
  When running scripts, always use the virtual environment at the project root, `.venv/bin/python`.
  ```bash
  .venv/bin/python scripts/<script_name>.py [args]
  ```
- **Language setting**:
  To make script output Japanese, set the environment variable `GSLIDES_LANG=ja`.
- **Configuration / credentials**:
  Uses OAuth credentials (`config/credentials.json`, `config/token.json`) and a Gemini API key (`config/gemini_api_key` or `GEMINI_API_KEY`). If an authentication error occurs, run the re-authentication script as directed by the prompt.

## 2. Using skills

When a task request involves creating, editing, or validating slides, load the relevant skill's `SKILL.md` under `.agents/skills/` and follow its procedure.

| Task / purpose | Skill to use (`.agents/skills/`) |
|---|---|
| Run the whole deck-generation flow in one pass (pipeline) | `forge` |
| Create a deck from a registered template/master | `google-slides-template` |
| Generate a deck from scratch (no master) | `google-slides` |
| Create/register a new master template | `template-forge` |
| Create/register a reusable single-slide content template | `slide-template-creator` |
| Create Scalar product/proposal slides | `scalar-product-slides`, `scalar-proposal-slides` |
| Per-customer activity plan / visit materials (AE sales activity) | `scalar-account-plan`, `scalar-ae-materials` |
| Account Planning Session (annual org-chart / deal-stocktake deck) | `scalar-account-planning-session` |
| Create B2B deal stakeholder maps / discovery maps | `b2b-account-maps` |
| Create dense architecture diagrams with draw.io | `drawio-diagrams` |
| Automatically fill image frames (including AI image generation) | `image-slots` |
| Thumbnail-based visual QA | `slide-qa` |
| Export to PowerPoint (`.pptx`) format | `pptx-export` |
| Generate spreadsheets such as line-item estimates | `spreadsheets` |

## 3. Interactive questions

When confirming prerequisites, whether to run visual QA, or whether PPTX export is needed, make active use of Antigravity's `ask_question` tool to present choices to the user.
