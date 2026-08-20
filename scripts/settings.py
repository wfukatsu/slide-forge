#!/usr/bin/env python3
"""Toolkit-wide switches, kept in `config/settings.json`.

Two decisions are made once and then apply to every run, instead of being
asked again at each intake:

| Setting | Values | What it controls |
|---|---|---|
| `imageGeneration` | `on` / `off` | whether Gemini generates images at all (`aiImage` figures, `fill_image_slots.py`) |
| `output` | `google` / `local` | where the deliverable lands: Google Drive / Google Slides, or a local folder as PowerPoint (`.pptx`) |
| `localOutputDir` | path | the local folder used when `output` is `local` (relative paths resolve against the repo root) |

    .venv/bin/python scripts/settings.py --show
    .venv/bin/python scripts/settings.py --image-generation off
    .venv/bin/python scripts/settings.py --output local --local-dir out/pptx

`config/` is gitignored, so the file is per-checkout and never committed.
The defaults reproduce the behaviour the toolkit had before this file
existed (image generation on, Google output), so an absent file changes
nothing.

Environment variables win over the file for a single run, which is what CI
and one-off overrides want:

    GSLIDES_IMAGE_GENERATION=off  GSLIDES_OUTPUT=local  GSLIDES_LOCAL_DIR=~/decks

`output: local` does **not** mean the deck is built offline — the engine
draws through the Google Slides API either way. It means the deliverable is
the exported `.pptx` in the local folder, and the generated deck is left in
Drive as the (still editable) source. Nothing is ever deleted for you.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _auth  # noqa: E402
from _i18n import t, register  # noqa: E402

register({
    "read or change the toolkit settings":
        "ツールキットの設定を表示・変更する",
    "turn Gemini image generation on or off":
        "Gemini による画像生成を ON / OFF する",
    "where the deliverable goes: google (Drive / Slides) or local (folder / PowerPoint)":
        "成果物の出力先: google（Drive / Slides）または local（フォルダ / PowerPoint）",
    "folder for the exported .pptx when output is local":
        "output が local のときに .pptx を書き出すフォルダ",
    "print the current settings (the default action)":
        "現在の設定を表示する（引数なしのときの既定動作）",
    "print the settings as JSON": "設定を JSON で表示する",
    "settings file: {path}": "設定ファイル: {path}",
    "  (not created yet — these are the defaults)":
        "  （未作成 — 以下は既定値）",
    "  overridden for this run by {vars}":
        "  この実行では {vars} が上書きしています",
    "Saved: {path}": "保存しました: {path}",
    "{path} is malformed: {err}": "{path} が壊れています: {err}",
    "{where}: expected on or off (got: {value})":
        "{where}: on か off を指定してください（指定: {value}）",
    "{where}: expected google or local (got: {value})":
        "{where}: google か local を指定してください（指定: {value}）",
    "Gemini image generation is turned off in the settings "
    "(imageGeneration: off).\n"
    "  Turn it back on with: "
    ".venv/bin/python scripts/settings.py --image-generation on\n"
    "  Or draw the picture with shapes instead "
    "(scripts/illustrations.py, scripts/patterns.py), which needs no API key.":
        "設定で Gemini の画像生成が OFF になっています"
        "（imageGeneration: off）。\n"
        "  戻すには: "
        ".venv/bin/python scripts/settings.py --image-generation on\n"
        "  もしくは図形で描く方法（scripts/illustrations.py、"
        "scripts/patterns.py）を使ってください（API キー不要）。",
    "on": "ON",
    "off": "OFF",
    "Google Drive / Google Slides": "Google Drive / Google Slides",
    "local folder / PowerPoint (.pptx)": "ローカルフォルダ / PowerPoint (.pptx)",
})

FILENAME = "settings.json"

# The defaults are the behaviour the toolkit had before settings existed:
# an absent or empty settings.json must change nothing.
DEFAULTS: dict = {
    "imageGeneration": True,
    "output": "google",
    "localOutputDir": "out/pptx",
}

GOOGLE = "google"
LOCAL = "local"

# Spellings accepted from the environment and the CLI. People reach for the
# product name as often as the key, so both resolve.
_OUTPUT_ALIASES = {
    "google": GOOGLE, "drive": GOOGLE, "slides": GOOGLE,
    "google-slides": GOOGLE, "googleslides": GOOGLE, "gslides": GOOGLE,
    "local": LOCAL, "pptx": LOCAL, "powerpoint": LOCAL, "ppt": LOCAL,
    "file": LOCAL,
}
_TRUE = {"1", "on", "true", "yes", "y", "enabled"}
_FALSE = {"0", "off", "false", "no", "n", "disabled"}


class SettingsError(RuntimeError):
    pass


# ---------- File location ----------

def path() -> str | None:
    """The settings file in effect, or None when none exists yet."""
    for d in _auth.config_dirs():
        p = os.path.join(d, FILENAME)
        if os.path.exists(p):
            return p
    return None


def write_path() -> str:
    """Where a save goes: the first config directory (honours $GSLIDES_CONFIG_DIR)."""
    return os.path.join(_auth.config_dirs()[0], FILENAME)


# ---------- Reading ----------

def _as_bool(value, where: str) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in _TRUE:
        return True
    if text in _FALSE:
        return False
    raise SettingsError(t("{where}: expected on or off (got: {value})",
                          where=where, value=value))


def _as_output(value, where: str) -> str:
    target = _OUTPUT_ALIASES.get(str(value).strip().lower())
    if not target:
        raise SettingsError(t("{where}: expected google or local (got: {value})",
                              where=where, value=value))
    return target


def stored() -> dict:
    """The raw file contents (no defaults, no environment)."""
    p = path()
    if not p:
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise SettingsError(t("{path} is malformed: {err}", path=p, err=exc)) from exc
    return data if isinstance(data, dict) else {}


def env_overrides() -> dict:
    """Settings taken from the environment for this run only."""
    out: dict = {}
    raw = os.environ.get("GSLIDES_IMAGE_GENERATION")
    if raw:
        out["imageGeneration"] = _as_bool(raw, "GSLIDES_IMAGE_GENERATION")
    raw = os.environ.get("GSLIDES_OUTPUT")
    if raw:
        out["output"] = _as_output(raw, "GSLIDES_OUTPUT")
    raw = os.environ.get("GSLIDES_LOCAL_DIR")
    if raw:
        out["localOutputDir"] = raw
    return out


def load() -> dict:
    """Defaults, overlaid with the file, overlaid with the environment."""
    values = dict(DEFAULTS)
    data = stored()
    if "imageGeneration" in data:
        values["imageGeneration"] = _as_bool(
            data["imageGeneration"], f"{path()}: imageGeneration")
    if "output" in data:
        values["output"] = _as_output(data["output"], f"{path()}: output")
    if data.get("localOutputDir"):
        values["localOutputDir"] = str(data["localOutputDir"])
    values.update(env_overrides())
    return values


def image_generation_enabled() -> bool:
    return bool(load()["imageGeneration"])


def output_target(override: str | None = None) -> str:
    """`google` or `local`; a CLI flag passed as *override* wins over both."""
    if override:
        return _as_output(override, "--output")
    return load()["output"]


def local_output_dir() -> str:
    """Absolute path of the local output folder (relative values hang off the repo root)."""
    raw = os.path.expanduser(str(load()["localOutputDir"]))
    return raw if os.path.isabs(raw) else os.path.join(_auth.SKILL_DIR, raw)


def image_generation_off_message() -> str:
    return t(
        "Gemini image generation is turned off in the settings "
        "(imageGeneration: off).\n"
        "  Turn it back on with: "
        ".venv/bin/python scripts/settings.py --image-generation on\n"
        "  Or draw the picture with shapes instead "
        "(scripts/illustrations.py, scripts/patterns.py), which needs no API key.")


# ---------- Writing ----------

def save(values: dict) -> str:
    """Merge *values* into the stored file and return the path written."""
    data = stored()
    data.update(values)
    target = write_path()
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return target


# ---------- CLI ----------

def _describe(values: dict) -> list[str]:
    return [
        f"  imageGeneration : {t('on') if values['imageGeneration'] else t('off')}",
        f"  output          : {values['output']}"
        f"  ({t('Google Drive / Google Slides') if values['output'] == GOOGLE else t('local folder / PowerPoint (.pptx)')})",
        f"  localOutputDir  : {values['localOutputDir']}",
    ]


def main() -> int:
    p = argparse.ArgumentParser(description=t("read or change the toolkit settings"))
    p.add_argument("--image-generation", metavar="on|off",
                   help=t("turn Gemini image generation on or off"))
    p.add_argument("--output", metavar="google|local",
                   help=t("where the deliverable goes: google (Drive / Slides) "
                          "or local (folder / PowerPoint)"))
    p.add_argument("--local-dir", metavar="PATH",
                   help=t("folder for the exported .pptx when output is local"))
    p.add_argument("--show", action="store_true",
                   help=t("print the current settings (the default action)"))
    p.add_argument("--json", action="store_true", help=t("print the settings as JSON"))
    args = p.parse_args()

    try:
        changes: dict = {}
        if args.image_generation is not None:
            changes["imageGeneration"] = _as_bool(
                args.image_generation, "--image-generation")
        if args.output is not None:
            changes["output"] = _as_output(args.output, "--output")
        if args.local_dir is not None:
            changes["localOutputDir"] = args.local_dir
        if changes:
            print(t("Saved: {path}", path=save(changes)))

        values = load()
        if args.json:
            print(json.dumps(values, ensure_ascii=False, indent=2))
            return 0
        current = path()
        print(t("settings file: {path}", path=current or write_path()))
        if not current:
            print(t("  (not created yet — these are the defaults)"))
        for line in _describe(values):
            print(line)
        overrides = env_overrides()
        if overrides:
            names = {"imageGeneration": "GSLIDES_IMAGE_GENERATION",
                     "output": "GSLIDES_OUTPUT",
                     "localOutputDir": "GSLIDES_LOCAL_DIR"}
            print(t("  overridden for this run by {vars}",
                    vars=", ".join(names[k] for k in overrides)))
    except SettingsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
