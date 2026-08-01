#!/usr/bin/env python3
"""配色ユーティリティ。

`diagrams` / `charts` / `illustrations` / `patterns` / `images` の 5 つが共有する。
これらは互いを import する関係にあるため、共通の色計算をここに置いて循環を避けている。

後方互換のため `diagrams` からも同じ名前で re-export している
（`from diagrams import lighten` は従来どおり動く）。
"""
from __future__ import annotations


def _clamp(v: float) -> int:
    return max(0, min(255, int(round(v))))


def mix(hex_a: str, hex_b: str, t: float) -> str:
    """hex_a と hex_b を t (0→a, 1→b) で混ぜる。"""
    a = [int(hex_a.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(hex_b.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#%02X%02X%02X" % tuple(_clamp(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lighten(hex_color: str, t: float) -> str:
    """白へ寄せる。t=0 で元の色、t=1 で白。"""
    return mix(hex_color, "#FFFFFF", t)


def darken(hex_color: str, t: float) -> str:
    return mix(hex_color, "#000000", t)


def relative_luminance(hex_color: str) -> float:
    ch = []
    for i in (0, 2, 4):
        c = int(hex_color.lstrip("#")[i:i + 2], 16) / 255
        ch.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def contrast_ratio(a: str, b: str) -> float:
    l1, l2 = relative_luminance(a), relative_luminance(b)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


def readable_on(bg: str, dark: str = "#0F172A", light: str = "#FFFFFF") -> str:
    """背景色に対してコントラストの高い方の文字色を返す。"""
    return dark if contrast_ratio(bg, dark) >= contrast_ratio(bg, light) else light


class Palette:
    """テンプレートの colorScheme から図解用の色を組み立てる。"""

    def __init__(self, colors: dict):
        c = colors
        self.primary = c.get("accent5", "#2673BB")
        self.primaryDark = darken(self.primary, 0.35)
        self.success = c.get("accent1", "#63C045")
        self.danger = c.get("accent2", "#EE2155")
        self.info = c.get("accent3", "#0985FD")
        self.warning = c.get("accent4", "#FFEF24")
        self.text = c.get("dark1", "#0F172A")
        self.muted = c.get("dark2", "#6B7280")
        self.surface = lighten(self.primary, 0.92)
        self.surfaceAlt = c.get("light2", "#F9FAFB")
        self.border = lighten(self.primary, 0.65)
        self.white = "#FFFFFF"

    def series(self, n: int) -> list[str]:
        """系列色を n 個返す。テーマ由来の色を順に使い、足りなければ明度で伸ばす。

        並びは**固定**（グラフの系列は常にこの順で塗り、循環・並べ替えをしない）。
        順序は色覚多様性の検証を通したもの: primary → info の青2連は隣どうしが
        判別できず（ΔE 10.5 < 15）、warning の黄はほぼ白に沈むため、
        青 → 緑 → 水色 → 赤 → 暗黄 の並びに置き、黄だけチャート用に暗くしている
        （全隣接ペアで CVD ΔE ≥ 9.2 / 通常視 ΔE ≥ 27）。緑と暗黄は白背景との
        コントラストが 3:1 を下回るので、グラフ側は必ず凡例と直接ラベルを添える。
        """
        chart_yellow = "#C7A500"
        base = [self.primary, self.success, self.info, self.danger, chart_yellow]
        out = []
        for i in range(n):
            c = base[i % len(base)]
            round_ = i // len(base)
            out.append(c if round_ == 0 else lighten(c, min(0.55, 0.22 * round_)))
        return out
