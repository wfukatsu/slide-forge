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


def lang() -> str:
    v = os.environ.get("GSLIDES_LANG", "")
    return "ja" if v.lower().startswith("ja") else "en"


def register(ja: dict[str, str]) -> None:
    """Merge a module's English→Japanese message catalog."""
    _CATALOG_JA.update(ja)


def t(msg: str, **kwargs) -> str:
    """Translate *msg* to the active language and fill ``{}`` placeholders."""
    if lang() == "ja":
        msg = _CATALOG_JA.get(msg, msg)
    return msg.format(**kwargs) if kwargs else msg
