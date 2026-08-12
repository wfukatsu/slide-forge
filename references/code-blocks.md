*[日本語](code-blocks.ja.md)*
# Code Blocks (syntax-highlighted code samples)

`Canvas.code_block()` draws a code sample using a monospace font, a dark panel,
and syntax highlighting. Highlighting is applied via the Slides API's
`updateTextStyle` (`FIXED_RANGE`) range-based coloring, so the generated text
remains editable by the user afterward.

```python
d.code_block(0.5, 1.0, 6.1, 2.9, code, lang="java")
```

Also usable from a JSON spec (`figures`):

```json
{ "type": "code_block", "x": 0.5, "y": 1.0, "w": 6.1, "h": 2.9,
  "code": "DistributedTransaction tx = manager.begin();\ntx.commit();",
  "lang": "java" }
```

## Arguments

| Argument | Default | Meaning |
|---|---|---|
| `code` | required | The code string. Don't include characters outside the BMP (e.g. emoji), since range indexing is UTF-16-based |
| `lang` | `"java"` | `java` / `graphql` / `json` / `bash`. Unknown languages are rendered in a single color |
| `size` / `line_spacing` | 7.5 / 104 | Font size (pt) / line spacing (%) |
| `bg` / `fg` | `#1F2933` / `#E8ECF1` | Panel and base text color |
| `font` | `"Roboto Mono"` | Monospace font |

## Rules to follow

- **Corners are square (RECTANGLE). Never rounded.** Confirmed by user feedback
  as a fixed convention (the same square-corner rule as accent-bar cards).
  `code_block` enforces square corners in the implementation
- **Estimate height from effective line height.** On Slides, one line's rendered
  height is `fontSize × lineSpacing × ~1.45` (accounting for the Noto Sans JP
  fallback). Rule of thumb: `h = lines × size × (ls/100) × 1.45 / 72 + 0.14in`.
  Underestimating overflows text above and below the box (since valign=MIDDLE
  overflows both sides)
- Keep lines to around 60 columns. Keep Japanese comments short (even in
  monospace, Japanese characters take up about 2 columns each)
- Source code from primary sources (official docs, repositories). If summarized
  or truncated, note the source and what was omitted in the speaker notes

## Color scheme (VS Code Dark+ style, ≥4.5:1 contrast on the dark background)

| Token | Color | Example |
|---|---|---|
| comment | `#7DBA7D` green | `// start` `# ① start` |
| string | `#E2A37E` orange | `"PAID"` `'sales'` |
| keyword | `#6FB6EA` blue | `public` `query` `SELECT` `true` |
| type | `#56C9B4` teal | `DistributedTransaction` (capitalized) |
| func | `#DCDCAA` yellow | `begin()` `newBuilder()`; in bash, the command name right after `$ ` |
| anno | `#D19FD3` purple | `@Override` `@transaction` |
| prop | `#9CDCFE` light blue | GraphQL/JSON property names, bash `--flag`s |
| number | `#B5CEA8` pale green | `1000` |

## Language-specific quirks

- **java**: capitalized identifiers are colored as types (teal). Strings
  containing SQL are colored entirely as strings (orange), matching typical IDE
  behavior
- **bash**: **the contents of double quotes are left unstyled**, so SQL keywords
  like `CREATE` / `SELECT` are still picked up (designed for ScalarDL TableStore's
  `--statement "CREATE …"`). Only single-quoted text is colored as a string
- **graphql / json**: property names like `key:` are colored light blue. JSON
  colors keys and values separately

## Adding a language

Add a `(token name, regex)` list to `Canvas._CODE_RULES` in `diagrams.py`.
**Rules listed earlier take priority**, so always place comment/string rules
first (to prevent later rules from mis-coloring text inside a string). Token
names must match the keys in `_CODE_STYLES`.

## Layout convention (code-sample slides)

A 3-way split of "left = code / right = explanation / bottom = key-point band"
fits well. Example: `~/Documents/Slides/scalar-intro-2026/add_code_samples.py`
(includes inserting into an existing deck and renumbering page numbers).

When inserting into an existing deck, always secure a version snapshot first
with `scripts/snapshot_version.py <URL>` (records the revision ID and takes a
PPTX backup), and report the revision ID to the user before proceeding.

```python
d.label(CX, y, CW, 0.2, "Java — CRUD インターフェース", size=8.5,
        bold=True, color=accent)                     # ブロック見出し
d.code_block(CX, y + 0.24, 6.1, h, code, lang="java")
# 右: 解説カード（surface 塗り + 上端 0.06in のアクセントバー。直角）
# 下: ポイント帯（lighten(accent, 0.9) 塗り。1 行の結論）
```
