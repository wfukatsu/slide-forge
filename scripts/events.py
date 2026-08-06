#!/usr/bin/env python3
"""イベント案内図（`diagrams.Canvas` に混ぜて使うミックスイン）。

セミナー・勉強会・カンファレンスの案内デッキで定番の部品を型にしたもの。
オンライン開催・会場（オフライン）開催・ハイブリッド開催の 3 形式に対応する。
すべて図形だけで描くのでキーもネットワークも不要、色はテンプレートの配色に従う。

    d = Canvas(deck, slide_id, template)
    d.event_overview(0.5, 1.2, 4.4, [
        ["calendar", "日時", "2026年9月18日(金) 15:00–18:00"],
        ["pin",      "会場", "Scalar オフィス（東京・神谷町）"],
        ["coin",     "参加費", "無料（事前登録制）"],
        ["people",   "定員", "現地 50 名 / オンライン 500 名"],
    ], mode="hybrid")
    d.event_access(5.2, 1.2, 4.3, 2.6, mode="hybrid",
                   venue={"name": "Scalar オフィス", "address": "東京都港区…",
                          "access": "神谷町駅 徒歩5分"},
                   online={"platform": "Zoom ウェビナー",
                           "url": "申込後にご案内", "note": "アーカイブ配信あり"})
    d.event_timetable(0.5, 1.2, 9.0, [
        ["15:00–15:10", "開会・ご挨拶", "山田 太郎"],
        ["15:10–16:00", "基調講演", "鈴木 花子"],
    ])
    d.event_speakers(0.5, 3.6, 9.0, [
        ["山田 太郎", "株式会社Scalar CTO", "基調講演"],
    ])

すべての図は他の部品と同じ積み上げ規約に従い、**描画領域の下端 y を返す**。
座標はインチ。描いたら `audit_*` の自己点検を必ず通すこと。
日付・会場・URL などの中身はユーザーの素材から取る（勝手に埋めない）。
"""
from __future__ import annotations

from _i18n import t, register

register({
    "mode must be one of {allowed} (got: {mode})":
        "mode は {allowed} のいずれか（指定: {mode}）",
    "event_access: mode '{mode}' requires {field}":
        "event_access: mode '{mode}' には {field} が必要です",
    "event_overview: each row is [icon, term, value] (row {i} has {n} items)":
        "event_overview: 行は [アイコン, 項目, 値] の 3 要素（{i} 行目が {n} 要素）",
    "event_timetable: each row is [time, session] or [time, session, speaker] "
    "(row {i} has {n} items)":
        "event_timetable: 行は [時刻, 内容] か [時刻, 内容, 登壇者]"
        "（{i} 行目が {n} 要素）",
    "event_speakers: each speaker is [name, title] or [name, title, talk] "
    "(speaker {i} has {n} items)":
        "event_speakers: 登壇者は [氏名, 肩書] か [氏名, 肩書, 講演タイトル]"
        "（{i} 人目が {n} 要素）",
    "event_speakers: up to 5 speakers per row ({n} given). Split into two rows":
        "event_speakers: 1 行に置けるのは 5 人まで（{n} 人指定）。2 行に分けること",
})

MODES = ("online", "offline", "hybrid")
MODE_LABELS = {
    "online": "オンライン開催",
    "offline": "会場開催",
    "hybrid": "ハイブリッド開催",
}


class EventMixin:
    # ---------- 開催形式バッジ ----------

    def event_mode_badge(self, x, y, mode, *, label=None, size=10) -> float:
        """開催形式のピル型バッジ。戻り値は下端 y。

        mode: "online" / "offline" / "hybrid"。label で文言を差し替えられる
        （例: "オンライン開催（無料）"）。
        """
        if mode not in MODES:
            raise ValueError(t("mode must be one of {allowed} (got: {mode})",
                               allowed="/".join(MODES), mode=mode))
        text = label or MODE_LABELS[mode]
        h = 0.34
        w = max(1.3, 0.32 + 0.145 * _text_width(text, size))
        self.shape(x, y, w, h, kind="ROUND_RECTANGLE", fill=self.P.primary,
                   stroke=None)
        self.label(x, y, w, h, text, size=size, bold=True, align="CENTER",
                   valign="MIDDLE", color="#FFFFFF")
        return y + h

    # ---------- 開催概要 ----------

    def event_overview(self, x, y, w, rows, *, mode=None, size=11,
                       term_w=1.15, icon_size=0.34, row_h=0.5) -> float:
        """開催概要のアイコン付き項目リスト。戻り値は下端 y。

        rows は [ピクトグラム名, 項目, 値] の並び。値が 2 行になるときは
        row_h を広げる（自動では広げない — 座標検査で拾えるように）。
        mode を渡すと先頭に開催形式バッジを置く。
        """
        cy = y
        if mode:
            cy = self.event_mode_badge(x, cy, mode, size=size - 1) + 0.14
        for i, row in enumerate(rows):
            if len(row) != 3:
                raise ValueError(t(
                    "event_overview: each row is [icon, term, value] "
                    "(row {i} has {n} items)", i=i + 1, n=len(row)))
            icon_name, term, value = row
            iy = cy + (row_h - icon_size) / 2
            self.icon(icon_name, x, iy, icon_size)
            tx = x + icon_size + 0.14
            self.label(tx, cy, term_w, row_h, str(term), size=size, bold=True,
                       align="START", valign="MIDDLE", color=self.P.primaryDark)
            vx = tx + term_w + 0.06
            self.label(vx, cy, x + w - vx, row_h, str(value), size=size,
                       align="START", valign="MIDDLE", color=self.P.text,
                       line_spacing=112)
            cy += row_h
        return cy

    # ---------- タイムテーブル ----------

    def event_timetable(self, x, y, w, rows, *, size=11, time_w=1.55,
                        row_h=0.42, zebra=True) -> float:
        """プログラム（時刻 | 内容 | 登壇者）。戻り値は下端 y。

        rows は [時刻, 内容] か [時刻, 内容, 登壇者]。時刻は "15:00–15:30" の
        ような文字列をそのまま描く。行数が多いときは row_h を詰めるより
        2 枚に分けること（1 枚 8 行まで目安）。
        """
        speaker_w = 0.0
        for row in rows:
            if len(row) not in (2, 3):
                raise ValueError(t(
                    "event_timetable: each row is [time, session] or "
                    "[time, session, speaker] (row {i} has {n} items)",
                    i=rows.index(row) + 1, n=len(row)))
            if len(row) == 3 and row[2]:
                speaker_w = max(speaker_w,
                                min(2.6, 0.3 + 0.16 * _text_width(str(row[2]),
                                                                  size)))
        for i, row in enumerate(rows):
            ry = y + i * row_h
            if zebra and i % 2 == 1:
                self.shape(x, ry, w, row_h, kind="RECTANGLE",
                           fill=self.P.surfaceAlt, stroke=None)
            self.label(x + 0.06, ry, time_w, row_h, str(row[0]), size=size,
                       bold=True, align="START", valign="MIDDLE",
                       color=self.P.primary)
            sx = x + time_w + 0.14
            sw = w - time_w - 0.14 - (speaker_w + 0.1 if speaker_w else 0.1)
            self.label(sx, ry, sw, row_h, str(row[1]), size=size,
                       align="START", valign="MIDDLE", color=self.P.text)
            if len(row) == 3 and row[2]:
                self.label(x + w - speaker_w - 0.06, ry, speaker_w, row_h,
                           str(row[2]), size=size - 1.5, align="END",
                           valign="MIDDLE", color=self.P.muted)
        bottom = y + len(rows) * row_h
        self.line(x, y, x + w, y, color=self.P.border, weight=1.0, free=True)
        self.line(x, bottom, x + w, bottom, color=self.P.border, weight=1.0,
                  free=True)
        return bottom

    # ---------- 登壇者 ----------

    def event_speakers(self, x, y, w, speakers, *, size=10, icon="person",
                       gap=0.24) -> float:
        """登壇者カードの横並び。戻り値は下端 y。

        speakers は [氏名, 肩書] か [氏名, 肩書, 講演タイトル]。1 行 5 人まで
        （超えるなら 2 回呼んで 2 段にする）。氏名・肩書は実在の登壇者の
        確定情報だけを使うこと。
        """
        n = len(speakers)
        if n > 5:
            raise ValueError(t("event_speakers: up to 5 speakers per row "
                               "({n} given). Split into two rows", n=n))
        has_talk = False
        for i, sp in enumerate(speakers):
            if len(sp) not in (2, 3):
                raise ValueError(t(
                    "event_speakers: each speaker is [name, title] or "
                    "[name, title, talk] (speaker {i} has {n} items)",
                    i=i + 1, n=len(sp)))
            has_talk = has_talk or (len(sp) == 3 and sp[2])
        cw = (w - gap * (n - 1)) / n
        ch = 1.62 if has_talk else 1.28
        ic = 0.5
        for i, sp in enumerate(speakers):
            cx = x + i * (cw + gap)
            self.shape(cx, y, cw, ch, kind="ROUND_RECTANGLE",
                       fill=self.P.surfaceAlt, stroke=self.P.border)
            self.icon(icon, cx + (cw - ic) / 2, y + 0.12, ic)
            name_y = y + 0.12 + ic + 0.05
            self.label(cx + 0.08, name_y, cw - 0.16, 0.24, str(sp[0]),
                       size=size + 0.5, bold=True, align="CENTER",
                       valign="TOP", color=self.P.text)
            self.label(cx + 0.08, name_y + 0.25, cw - 0.16, 0.2, str(sp[1]),
                       size=size - 1.5, align="CENTER", valign="TOP",
                       color=self.P.muted)
            if len(sp) == 3 and sp[2]:
                self.label(cx + 0.08, name_y + 0.47, cw - 0.16,
                           y + ch - name_y - 0.51, str(sp[2]), size=size - 1,
                           align="CENTER", valign="TOP",
                           color=self.P.primaryDark, line_spacing=112)
        return y + ch

    # ---------- アクセス（会場 / オンライン） ----------

    def event_access(self, x, y, w, h, *, mode, venue=None, online=None,
                     size=10.5) -> float:
        """参加方法パネル。戻り値は下端 y。

        - mode="offline": venue（{"name", "address", "access"}）のパネルのみ
        - mode="online":  online（{"platform", "url", "note"}）のパネルのみ
        - mode="hybrid":  両方を左右に並べる（venue と online の両方が必要）

        URL や住所は確定情報だけを描く。未確定は「申込後にご案内」のような
        文言にする（勝手に URL を作らない）。
        """
        if mode not in MODES:
            raise ValueError(t("mode must be one of {allowed} (got: {mode})",
                               allowed="/".join(MODES), mode=mode))
        need = {"offline": ("venue",), "online": ("online",),
                "hybrid": ("venue", "online")}[mode]
        given = {"venue": venue, "online": online}
        for field in need:
            if not given[field]:
                raise ValueError(t("event_access: mode '{mode}' requires "
                                   "{field}", mode=mode, field=field))

        def panel(px, pw, icon_name, heading, lines):
            self.shape(px, y, pw, h, kind="ROUND_RECTANGLE",
                       fill=self.P.surfaceAlt, stroke=self.P.border)
            self.icon(icon_name, px + 0.16, y + 0.14, 0.36)
            self.label(px + 0.62, y + 0.14, pw - 0.76, 0.36, heading,
                       size=size + 1, bold=True, align="START",
                       valign="MIDDLE", color=self.P.primaryDark)
            ly = y + 0.62
            for text, styled in lines:
                if not text:
                    continue
                self.label(px + 0.2, ly, pw - 0.4, 0.34, str(text), size=size,
                           bold=styled == "bold", align="START", valign="TOP",
                           color=self.P.muted if styled == "muted"
                           else self.P.text, line_spacing=112)
                ly += 0.34

        venue_lines = venue and [
            (venue.get("name"), "bold"),
            (venue.get("address"), "plain"),
            (venue.get("access"), "muted"),
        ]
        online_lines = online and [
            (online.get("platform"), "bold"),
            (online.get("url"), "plain"),
            (online.get("note"), "muted"),
        ]
        if mode == "offline":
            panel(x, w, "pin", "会場", venue_lines)
        elif mode == "online":
            panel(x, w, "browser", "オンライン参加", online_lines)
        else:
            pw = (w - 0.3) / 2
            panel(x, pw, "pin", "会場参加", venue_lines)
            panel(x + pw + 0.3, pw, "browser", "オンライン参加", online_lines)
        return y + h


def _text_width(text: str, size: float) -> float:
    """ラベル幅の見積もり（CJK=1、半角=0.55 文字換算）。"""
    units = sum(1.0 if ord(ch) > 0x2E7F else 0.55 for ch in str(text))
    return units * size / 10
