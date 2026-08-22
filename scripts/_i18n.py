#!/usr/bin/env python3
"""Runtime message localization for the slide-forge scripts.

English is the default. Set ``GSLIDES_LANG=ja`` to switch the CLI messages
to Japanese; any other value (or unset) selects English.

Usage in a script::

    from _i18n import t, register

    register({
        "Deck '{name}' not found": "デッキ '{name}' が見つかりません",
    })
    ...
    raise SystemExit(t("Deck '{name}' not found", name=name))

- Message IDs are the English strings themselves (gettext style), so the
  code reads naturally and untranslated messages degrade to English.
- ``register()`` merges a per-module catalog at import time; keep each
  module's translations next to its messages.
- Only *runtime messages* (print / errors / argparse help) go through
  ``t()``. Slide content, figure labels, and specs are deck data, not
  messages — never localize those here.
"""
from __future__ import annotations

import os

_CATALOG_JA: dict[str, str] = {}
_LANG: str | None = None


def lang() -> str:
    """The active language. Resolved once — ``t()`` is called from inside the
    audit loops, and re-reading the environment there is pure overhead."""
    global _LANG
    if _LANG is None:
        _LANG = "ja" if os.environ.get("GSLIDES_LANG", "").lower().startswith("ja") else "en"
    return _LANG


def set_lang(value: str | None = None) -> str:
    """Override the language, or re-read the environment when given None. For tests."""
    global _LANG
    _LANG = None if value is None else ("ja" if value.lower().startswith("ja") else "en")
    return lang()


def register(ja: dict[str, str]) -> None:
    """Merge a module's English→Japanese message catalog."""
    _CATALOG_JA.update(ja)


def t(msg: str, **kwargs) -> str:
    """Translate *msg* to the active language and fill ``{}`` placeholders."""
    if lang() == "ja":
        msg = _CATALOG_JA.get(msg, msg)
    return msg.format(**kwargs) if kwargs else msg
