#!/usr/bin/env python3
"""template.json とデッキ仕様からプレゼンテーションを生成する。

テンプレートを Drive API で複製 → 同梱スライドを削除 → `createSlide(layoutId)` で
スライドを積む。テンプレートのマスターが定義する装飾・ロゴ・フッターは自動継承される。

    # 仕様の検証だけ（API 呼び出しなし）
    python scripts/build_deck.py --template templates/x.json --spec deck.json --dry-run

    # 生成
    python scripts/build_deck.py --template templates/x.json --spec deck.json \
        --title "資料タイトル" [--folder <DRIVE_FOLDER_URL_OR_ID>]

ライブラリとして:
    deck = TemplateDeck.create(template, title="…")
    deck.add_slide("CONTENT", title="…", body=["…"])
    print(deck.commit())
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _auth  # noqa: E402
from _i18n import t, register  # noqa: E402

register({
    "  warn: {what} failed with HTTP {code}; retrying in {wait:.0f}s "
    "({attempt}/{attempts})":
        "  warn: {what} が HTTP {code} で失敗。{wait:.0f} 秒後に再試行 "
        "({attempt}/{attempts})",
    "template copy": "テンプレートの複製",
    "template.json has no presentationId":
        "template.json に presentationId がありません",
    "  warn: template.json existingSlideIds contains IDs that do not exist: "
    "{ids}\n        The template may have been updated; re-analyze it with "
    "inspect_template.py.":
        "  warn: template.json の existingSlideIds に実在しない ID があります: "
        "{ids}\n        テンプレートが更新された可能性があります。"
        "inspect_template.py で再解析してください。",
    "cannot resolve layout '{key}'; available roles: {roles} / "
    "layout keys: {keys}":
        "レイアウト '{key}' を解決できません。"
        "利用可能なロール: {roles} / レイアウトキー: {keys}",
    "body and bodies cannot be specified together":
        "body と bodies は同時に指定できません",
    "layout '{key}' ({name}) has no {ph} placeholder; it declares {declared}":
        "レイアウト '{key}' ({name}) は {ph} プレースホルダを持ちません。"
        "保持しているのは {declared}",
    "layout '{key}' ({name}) has only {slots} BODY slots but {given} were "
    "given (declares: {declared})":
        "レイアウト '{key}' ({name}) の BODY は {slots} 枠しかありませんが "
        "{given} 個指定されています（保持: {declared}）",
    "  warn: notes placeholder for {slide_id} not found; skipped":
        "  warn: {slide_id} のノート枠が見つからずスキップしました",
    "  warn: could not read the size of image {oid}; frame-filling placement "
    "was not applied":
        "  warn: 画像 {oid} の寸法が取れず、枠ぴったりの配置を適用できませんでした",
    "slides[{i}]: 'figures' must be an array":
        "slides[{i}]: 'figures' は配列である必要があります",
    "{where}: missing 'type'": "{where}: 'type' がありません",
    "{where}: unknown type '{kind}' (available: {available})":
        "{where}: 未知の type '{kind}'（利用可能: {available}）",
    "{where}: type '{kind}' is missing required keys: {missing}":
        "{where}: type '{kind}' に必要なキーがありません: {missing}",
    "{where}: '{k}' must be a number (inches)":
        "{where}: '{k}' は数値（インチ）である必要があります",
    "{where}: extends horizontally past the page ({pw}in) "
    "(x={x} w={w} → right edge {right:.2f}in)":
        "{where}: 横方向がページ({pw}in)からはみ出します"
        "（x={x} w={w} → 右端 {right:.2f}in）",
    "{where}: extends vertically past the page ({ph}in) "
    "(y={y} h={h} → bottom edge {bottom:.2f}in)":
        "{where}: 縦方向がページ({ph}in)からはみ出します"
        "（y={y} h={h} → 下端 {bottom:.2f}in）",
    "{where}: the table overlaps the master logo/footer band "
    "(below y={band:.2f}in) (bottom edge {bottom:.2f}in); reduce the rows or "
    "split it across slides":
        "{where}: 表がマスターのロゴ・フッター帯（y={band:.2f}in 以下）に"
        "重なります（下端 {bottom:.2f}in）。行数を減らすか複数枚に分けること",
    "slides[{i}]: failed to draw figures: {etype}: {e}":
        "slides[{i}]: 図の描画に失敗しました: {etype}: {e}",
    "spec has no slides array": "spec に slides 配列がありません",
    "{where}: missing 'layout'": "{where}: 'layout' がありません",
    "{where}: cannot resolve layout '{key}' (roles: {roles} / keys: {keys})":
        "{where}: レイアウト '{key}' を解決できません "
        "(ロール: {roles} / キー: {keys})",
    "{where}: layout '{key}' ({name}) has no {ph} but '{field}' is specified "
    "(declares: {declared})":
        "{where}: レイアウト '{key}' ({name}) は {ph} を持たないのに "
        "'{field}' が指定されています（保持: {declared}）",
    "{where}: 'body' and 'bodies' cannot be specified together":
        "{where}: 'body' と 'bodies' は同時に指定できません",
    "{where}: 'bodies' must be an array":
        "{where}: 'bodies' は配列である必要があります",
    "{where}: layout '{key}' ({name}) has no BODY but body text is specified "
    "(declares: {declared})":
        "{where}: レイアウト '{key}' ({name}) は BODY を持たないのに"
        "本文が指定されています（保持: {declared}）",
    "{where}: layout '{key}' ({name}) has {slots} BODY slots but {given} were "
    "given (declares: {declared})":
        "{where}: レイアウト '{key}' ({name}) の BODY は {slots} 枠ですが "
        "{given} 個指定されています（保持: {declared}）",
    "generate a presentation from a template":
        "テンプレートからプレゼンテーションを生成する",
    "path to template.json": "template.json のパス",
    "path to the deck-spec JSON": "デッキ仕様 JSON のパス",
    "presentation title (defaults to spec.title)":
        "生成するプレゼンテーションのタイトル（既定は spec.title）",
    "destination Drive folder URL or ID":
        "出力先 Drive フォルダの URL または ID",
    "validate the spec only, without calling the API":
        "API を呼ばず仕様の検証だけ行う",
    "do not draw page numbers": "ページ番号を描画しない",
    "keep the slides bundled with the template":
        "テンプレート同梱スライドを残す",
    "fail if the figure audit (overlaps / text overflow) reports anything":
        "図の検査（重なり・文字溢れ）で 1 件でも出たら失敗にする",
    "The spec has problems:": "仕様に問題があります:",
    "No title (specify --title or spec.title)":
        "タイトルがありません（--title か spec.title を指定してください）",
    "OK: the {n}-slide spec is consistent with the template":
        "OK: {n} 枚のスライド仕様はテンプレートと整合しています",
    "  + {n} figures": "  + 図 {n} 個",
    "Figure audit found {n} findings (images excluded; they need the real "
    "file):":
        "図の検査で {n} 件（画像は実物が要るため対象外）:",
    "figure audit (connectors / overlaps / text overflow): no problems":
        "図の検査（コネクタ・重なり・文字溢れ）: 問題なし",
    "(dry-run: nothing was generated)": "(dry-run: 生成していません)",
    "Figure audit found {n} findings:": "図の検査で {n} 件:",
    "slides[{i}] ({title}): body{col} needs about {used:.0f}pt but the "
    "placeholder is {cap:.0f}pt. Reduce the text, lower bodyFontSize, or "
    "split the slide":
        "slides[{i}] ({title}): 本文{col}は約 {used:.0f}pt 必要ですが枠は "
        "{cap:.0f}pt です。文を減らすか bodyFontSize を下げるか、"
        "スライドを分けてください",
    "  warn: body text contains characters outside the BMP (emoji etc.); "
    "emphasis ranges may shift":
        "  warn: 本文に BMP 外の文字（絵文字など）が含まれます。"
        "強調の範囲がずれることがあります",
    "  warn: unknown body role '{role}' (known: {known})":
        "  warn: 未知の本文ロール '{role}'（使えるもの: {known}）",
    "  warn: cannot use '{target}' as a link (use https://… or #12)":
        "  warn: '{target}' はリンク先にできません（https://… か #12 の形で）",
    "{where}: body line {n} must be a string or "
    "{{\"text\": …, \"role\": …}}": "{where}: 本文 {n} 行目は文字列か "
                                    "{{\"text\": …, \"role\": …}} で書きます",
    "slides[{i}].figures[{j}]: placed in the image slot of layout "
    "'{layout}' (x={x} y={y} w={w} h={h})":
        "slides[{i}].figures[{j}]: レイアウト '{layout}' の画像枠に配置 "
        "(x={x} y={y} w={w} h={h})",
    "slides[{i}].figures[{j}]: layout '{layout}' has no image slot, "
    "so x/y/w/h are required":
        "slides[{i}].figures[{j}]: レイアウト '{layout}' に画像枠が無いので "
        "x/y/w/h が必要です",
    "slides[{i}].figures[{j}]: slot {n} does not exist "
    "(layout '{layout}' has {total})":
        "slides[{i}].figures[{j}]: 画像枠 {n} は存在しません"
        "（レイアウト '{layout}' の枠は {total} 個）",
    "slides[{i}].figures[{j}]: the layout has an image slot at "
    "(x={x} y={y} w={w} h={h}) but this image is placed elsewhere "
    "(x={fx} y={fy} w={fw} h={fh}). Omit x/y/w/h to use the slot":
        "slides[{i}].figures[{j}]: レイアウトには画像枠"
        "（x={x} y={y} w={w} h={h}）がありますが、画像が別の場所"
        "（x={fx} y={fy} w={fw} h={fh}）に置かれています。"
        "x/y/w/h を省略すると枠に収まります",
})

# CENTERED_TITLE は Google 既定マスター(template-forge の blank ベース)の
# 表紙タイトル。spec 上は 'title' で受け、TITLE が無いレイアウトではこちらに流す
FILLABLE = ("TITLE", "CENTERED_TITLE", "SUBTITLE", "BODY")

# ---------- 本文の強調（役割つきの行と、行内の **強調**） ----------

# テンプレートが bodyRoles を持たないときの既定。
# サイズは変えない（変えると行数の見積もりが崩れるため。spaceAbove までに留める）
DEFAULT_BODY_ROLES = {
    "heading": {"bold": True, "spaceAbove": 6},
    "strong": {"bold": True},
    "note": {"color": "theme:DARK2"},
    # リンクは色と下線でそれと分かるようにする（API はリンクを付けても
    # 見た目を変えないため、こちらで付けないとクリックできると気づけない）
    "link": {"color": "theme:ACCENT5", "underline": True},
}
# 役割に書けるキー。文字スタイルと段落スタイルに振り分ける
_TEXT_STYLE_KEYS = ("bold", "italic", "underline", "color", "fontSize")
_PARA_STYLE_KEYS = ("spaceAbove", "spaceBelow")

# `**強調**` と `[表示テキスト](リンク先)` の 2 つだけ。Markdown 全体には
# 対応しない（`#` や `-` まで効くと誤解されると、かえって崩れるため）
_INLINE = re.compile(r"\*\*(?P<b>.+?)\*\*"
                     r"|\[(?P<t>[^\]]+)\]\((?P<u>[^)]+)\)", re.S)


def parse_inline(text: str) -> tuple[str, list[tuple]]:
    """記法を剥がし、剥がしたあとの文字列と (開始, 終了, 種類, リンク先) を返す。

    種類は "strong" か "link"。範囲は剥がしたあとの文字列の先頭からの位置。
    """
    out, spans, pos, cursor = [], [], 0, 0
    for m in _INLINE.finditer(text):
        out.append(text[pos:m.start()])
        cursor += m.start() - pos
        if m.group("b") is not None:
            inner, kind, target = m.group("b"), "strong", None
        else:
            inner, kind, target = m.group("t"), "link", m.group("u").strip()
        spans.append((cursor, cursor + len(inner), kind, target))
        out.append(inner)
        cursor += len(inner)
        pos = m.end()
    out.append(text[pos:])
    return "".join(out), spans


def link_target(value: str) -> dict | None:
    """リンク先を Slides API の link に変換する。

    "https://…" は URL、"#12" は同じデッキの 12 枚目（1 始まり）。
    """
    if not value:
        return None
    if value.startswith("#"):
        try:
            return {"slideIndex": max(0, int(value[1:]) - 1)}
        except ValueError:
            return None
    if value.startswith(("http://", "https://", "mailto:")):
        return {"url": value}
    return None


def normalize_body_lines(value) -> list[tuple[str, str | None]]:
    """body の各行を (本文, 役割) に正規化する。

    行は文字列でも {"text": "…", "role": "heading"} でもよい。
    """
    items = value if isinstance(value, list) else [value]
    lines: list[tuple[str, str | None]] = []
    for item in items:
        if isinstance(item, dict):
            lines.append((str(item.get("text", "")), item.get("role")))
        else:
            lines.append((str(item), None))
    return lines

# オブジェクト ID をプロセス間で衝突させないためのランダムトークン。
# 連番だけだと、既存デッキへ別プロセスから追記したとき slide_001 等が衝突する
_RUN_TOKEN = uuid.uuid4().hex[:4]


def _retry(call, *, what: str, attempts: int = 4, base_delay: float = 3.0):
    """一時的な 5xx / 429 を吸収して API 呼び出しを繰り返す。

    枚数の多いテンプレートの `files.copy` は、混んでいるときに 500 Internal Error を
    返すことが実際にある。1 回で諦めると生成が丸ごと落ちるので指数バックオフで粘る。
    HttpError 以外に、socket timeout 等のネットワーク例外（OSError）も再試行する。
    """
    import time
    from googleapiclient.errors import HttpError

    for i in range(attempts):
        try:
            return call()
        except (HttpError, OSError) as e:
            code = getattr(getattr(e, "resp", None), "status", None)
            retryable = isinstance(e, OSError) or code in (429, 500, 502, 503, 504)
            if not retryable or i == attempts - 1:
                raise
            code = code or type(e).__name__
            wait = base_delay * (2 ** i)
            print(t("  warn: {what} failed with HTTP {code}; retrying in "
                    "{wait:.0f}s ({attempt}/{attempts})", what=what, code=code,
                    wait=wait, attempt=i + 1, attempts=attempts - 1),
                  file=sys.stderr)
            time.sleep(wait)


# batchUpdate は 1 回にまとめるほど速い。分割すると 1 リクエストあたりの実測コストが
# 跳ね上がるため（実測: 8000 リクエストを 500 ずつ 16 回 = 18.2s、1 回 = 6.3s）、
# 上限いっぱいまで積む。並列化は逆効果（同一プレゼンへの同時書き込みが競合し、
# 4 並列 x 2000 で 20.1s / 逐次 2000 で 12.2s）なので**やってはいけない**。
#
# 上限は Google API のリクエストボディ 10MB。図のリクエストは実測 288 bytes 程度
# なので、安全率を見て 5MB / 10000 件で切る（実測 30305 件 / 7.5MB は 20s で通る）。
MAX_REQUESTS_PER_BATCH = 10000
MAX_BATCH_BYTES = 5_000_000


def _batches(requests: list[dict], max_requests: int = MAX_REQUESTS_PER_BATCH,
             max_bytes: int = MAX_BATCH_BYTES):
    """リクエスト列を、件数とバイト数の両方が上限に収まる塊に切って返す。

    順序は保つ。batchUpdate は塊ごとに逐次実行されるので、塊の境界が
    スライドや図形をまたいでも結果は変わらない。
    """
    batch: list[dict] = []
    size = 0
    for req in requests:
        n = len(json.dumps(req, ensure_ascii=False).encode())
        # 1 件で上限を超える場合でも、その 1 件だけの塊として必ず送る
        if batch and (len(batch) >= max_requests or size + n > max_bytes):
            yield batch
            batch, size = [], 0
        batch.append(req)
        size += n
    if batch:
        yield batch


def load_template(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


class TemplateDeck:
    """テンプレートを複製した上にスライドを積んでいくビルダー。"""

    def __init__(self, slides_service, drive_service, presentation_id: str, template: dict):
        self.slides = slides_service
        self.drive = drive_service
        self.presentation_id = presentation_id
        self.template = template
        self.requests: list[dict] = []
        self.slide_ids: list[str] = []
        self._added: list[dict] = []
        self._notes: list[tuple[str, str]] = []  # (slideId, notes)
        self._counter = 0
        # keep_existing で残したテンプレート同梱スライドの枚数。
        # add_page_numbers() が新規スライドの番号をこの分だけずらす
        self.kept_slides = 0
        # 画像を挿入したときに images.AssetStore が入る。commit() の後で後始末する
        self.assets = None
        # (objectId, x, y, w, h)。createImage は比率を保つため、枠ぴったりに
        # 敷きたい画像は commit 後に transform を上書きして直す
        self.image_fixups: list[tuple] = []

    # ---------- 生成 ----------

    @classmethod
    def create(
        cls,
        template: dict,
        title: str,
        folder: str | None = None,
        creds=None,
        keep_existing: bool = False,
    ) -> "TemplateDeck":
        src = template.get("presentationId")
        if not src:
            raise ValueError(t("template.json has no presentationId"))
        slides, drive = _auth.services(creds)

        body: dict = {"name": title}
        fid = _auth.folder_id(folder)
        if fid:
            body["parents"] = [fid]
        copied = _retry(
            lambda: drive.files().copy(fileId=src, body=body, fields="id",
                                       supportsAllDrives=True).execute(),
            what=t("template copy"))

        deck = cls(slides, drive, copied["id"], template)
        if not keep_existing:
            deck._delete_existing_slides()
        else:
            # 残したスライドの実枚数を数え、ページ番号の起点をずらす。
            # template.json の existingSlideIds はテンプレート更新で古くなり得るため実物を見る
            pres = _retry(
                lambda: deck.slides.presentations().get(
                    presentationId=deck.presentation_id, fields="slides.objectId"
                ).execute(),
                what="presentations.get")
            deck.kept_slides = len(pres.get("slides", []))
        return deck

    def _delete_existing_slides(self) -> None:
        """複製直後に残っているテンプレート同梱スライドを削除する。"""
        pres = _retry(
            lambda: self.slides.presentations().get(
                presentationId=self.presentation_id, fields="slides.objectId"
            ).execute(),
            what="presentations.get")
        present = [s["objectId"] for s in pres.get("slides", [])]
        expected = set(self.template.get("existingSlideIds", []))
        stale = expected - set(present)
        if stale:
            print(
                t("  warn: template.json existingSlideIds contains IDs that "
                  "do not exist: {ids}\n        The template may have been "
                  "updated; re-analyze it with inspect_template.py.",
                  ids=sorted(stale)),
                file=sys.stderr,
            )
        # 実在するスライドは全て削除する（テンプレート側でスライドが増えていても取りこぼさない）
        for oid in present:
            self.requests.append({"deleteObject": {"objectId": oid}})

    # ---------- レイアウト解決 ----------

    def resolve_layout(self, key: str) -> tuple[str, dict]:
        """ロール名（CONTENT 等）またはレイアウトキーからレイアウト定義を引く。"""
        layouts = self.template["layouts"]
        resolved = self.template.get("roles", {}).get(key, key)
        if resolved not in layouts:
            roles = sorted(self.template.get("roles", {}))
            raise KeyError(
                t("cannot resolve layout '{key}'; available roles: {roles} / "
                  "layout keys: {keys}", key=key, roles=roles,
                  keys=sorted(layouts))
            )
        return resolved, layouts[resolved]

    # ---------- スライド追加 ----------

    def _next_id(self, prefix: str) -> str:
        self._counter += 1
        # objectId は 50 文字まで。長いレイアウト名でも収まるよう prefix を丸める
        return f"{prefix[:40]}_{_RUN_TOKEN}_{self._counter:03d}"

    def add_slide(
        self,
        layout_key: str,
        *,
        title: str | None = None,
        subtitle: str | None = None,
        body: str | list[str] | None = None,
        bodies: list | None = None,
        notes: str | None = None,
        index: int | None = None,
        body_font_size: float | None = None,
        body_line_spacing: float | None = None,
        body_space_above: float | None = None,
        body_space_below: float | None = None,
    ) -> dict:
        """レイアウトを指定してスライドを追加し、プレースホルダを埋める。

        `bodies` は 2カラム/3カラムのレイアウト用。BODY プレースホルダの index 0,1,2… に
        順番に流し込む。`body` は `bodies=[body]` と等価。

        戻り値は {"slideId", "placeholders", "layout", "layoutKey"}。
        追加の図形を描きたい場合はこの slideId を pageObjectId に使う。
        """
        resolved_key, layout = self.resolve_layout(layout_key)
        declared = layout.get("placeholders", [])

        if body is not None and bodies is not None:
            raise ValueError(t("body and bodies cannot be specified together"))
        if body is not None:
            bodies = [body]

        # リクエストを積む前に検証する。失敗しても中途半端な状態を残さないため。
        title_slot = ("TITLE" if "TITLE" in declared
                      else "CENTERED_TITLE" if "CENTERED_TITLE" in declared
                      else None)
        for ph_type, value in ((title_slot or "TITLE", title),
                               ("SUBTITLE", subtitle)):
            if value is not None and ph_type not in declared:
                raise ValueError(
                    t("layout '{key}' ({name}) has no {ph} placeholder; "
                      "it declares {declared}", key=layout_key,
                      name=layout["displayName"], ph=ph_type,
                      declared=declared)
                )
        body_slots = [p for p in declared if p.split("#")[0] == "BODY"]
        if bodies is not None and len(bodies) > len(body_slots):
            raise ValueError(
                t("layout '{key}' ({name}) has only {slots} BODY slots but "
                  "{given} were given (declares: {declared})", key=layout_key,
                  name=layout["displayName"], slots=len(body_slots),
                  given=len(bodies), declared=declared)
            )

        slide_id = self._next_id("slide")
        ph_ids: dict[str, str] = {}
        mappings = []
        # SLIDE_NUMBER はマッピングしても API に無視されるため対象外（add_page_numbers で描画）
        for name in [t for t in declared if t.split("#")[0] in FILLABLE]:
            ph_type, _, idx = name.partition("#")
            idx = int(idx) if idx else 0
            safe = name.replace("#", "x").lower()
            oid = self._next_id(f"{resolved_key.lower()}_{safe}")
            ph_ids[name] = oid
            mappings.append(
                {"layoutPlaceholder": {"type": ph_type, "index": idx}, "objectId": oid}
            )

        create_req: dict = {
            "objectId": slide_id,
            "slideLayoutReference": {"layoutId": layout["layoutId"]},
        }
        if mappings:
            create_req["placeholderIdMappings"] = mappings
        if index is not None:
            create_req["insertionIndex"] = index
        self.requests.append({"createSlide": create_req})
        self.slide_ids.append(slide_id)
        self._added.append(
            {"slideId": slide_id, "layoutKey": resolved_key, "layout": layout}
        )

        filled_bodies = list(zip(body_slots, bodies or []))
        for name, value in ((title_slot or "TITLE", title), ("SUBTITLE", subtitle)):
            if value is None:
                continue
            text = "\n".join(value) if isinstance(value, list) else value
            self.requests.append(
                {"insertText": {"objectId": ph_ids[name], "text": text}}
            )

        # 本文は行ごとに役割・行内強調を持ちうるので、範囲を数えながら組み立てる
        body_spans: dict[str, list[dict]] = {}
        for name, value in filled_bodies:
            if value is None:
                continue
            text, spans = self._compose_body(value)
            body_spans[name] = spans
            self.requests.append(
                {"insertText": {"objectId": ph_ids[name], "text": text}}
            )

        # 本文の見た目調整。プレースホルダの既定サイズは手書き向けに大きめなことが多く、
        # 日本語の本文は行間を広げないと詰まって見える（既定 100〜115%）。
        for name, value in filled_bodies:
            if value is None:
                continue
            if body_font_size is not None:
                self.requests.append({"updateTextStyle": {
                    "objectId": ph_ids[name],
                    "style": {"fontSize": {"magnitude": body_font_size, "unit": "PT"}},
                    "textRange": {"type": "ALL"},
                    "fields": "fontSize",
                }})
            # プレースホルダの既定は段落前後にも余白を持つことがあり、行数の
            # 見積もりから大きくずれる。spaceAbove / spaceBelow も明示できる
            para_style: dict = {}
            if body_line_spacing is not None:
                para_style["lineSpacing"] = body_line_spacing
            if body_space_above is not None:
                para_style["spaceAbove"] = {
                    "magnitude": body_space_above, "unit": "PT"}
            if body_space_below is not None:
                para_style["spaceBelow"] = {
                    "magnitude": body_space_below, "unit": "PT"}
            if para_style:
                self.requests.append({"updateParagraphStyle": {
                    "objectId": ph_ids[name],
                    "style": para_style,
                    "textRange": {"type": "ALL"},
                    "fields": ",".join(para_style),
                }})

        # 役割つきの行と行内強調。**ALL レンジのあとに積むこと**（先に積むと
        # 一括指定に上書きされて効かない）
        for name, spans in body_spans.items():
            self._apply_body_spans(ph_ids[name], spans)

        if notes:
            self._notes.append((slide_id, notes))

        return {
            "slideId": slide_id,
            "placeholders": ph_ids,
            "layout": layout,
            "layoutKey": resolved_key,
        }

    # ---------- 本文の強調 ----------

    def body_roles(self) -> dict:
        """テンプレートが定義する役割ごとの見た目（無ければ既定）。"""
        return {**DEFAULT_BODY_ROLES, **(self.template.get("bodyRoles") or {})}

    def _resolve_color(self, value: str) -> dict | None:
        """"#RRGGBB" または "theme:DARK1" を rgbColor に解決する。"""
        if not isinstance(value, str):
            return None
        if value.startswith("theme:"):
            hexv = (self.template.get("colors") or {}).get(value[6:].lower())
            if not hexv:
                return None
            value = hexv
        return _auth.hex_to_rgb(value)

    def _compose_body(self, value) -> tuple[str, list[dict]]:
        """本文を1本の文字列に組み立て、範囲つきのスタイル指定を返す。

        インデックスは Slides API と同じ UTF-16 単位で数える。
        """
        roles = self.body_roles()
        parts, spans, cursor = [], [], 0
        for text, role in normalize_body_lines(value):
            plain, inline = parse_inline(text)
            if any(ord(ch) > 0xFFFF for ch in plain):
                print(t("  warn: body text contains characters outside the BMP "
                        "(emoji etc.); emphasis ranges may shift"),
                      file=sys.stderr)
            start = cursor
            end = start + len(plain)
            style = roles.get(role) if role else None
            if role and style is None:
                print(t("  warn: unknown body role '{role}' (known: {known})",
                        role=role, known=sorted(roles)), file=sys.stderr)
            if style:
                spans.append({"start": start, "end": end, "style": style,
                              "paragraph": True})
            for s, e, kind, target in inline:
                span = {"start": start + s, "end": start + e,
                        "style": roles.get(kind, {}), "paragraph": False}
                if kind == "link":
                    link = link_target(target)
                    if link is None:
                        print(t("  warn: cannot use '{target}' as a link "
                                "(use https://… or #12)", target=target),
                              file=sys.stderr)
                        continue
                    span["link"] = link
                spans.append(span)
            parts.append(plain)
            cursor = end + 1        # 改行ぶん
        return "\n".join(parts), spans

    def _apply_body_spans(self, object_id: str, spans: list[dict]) -> None:
        for span in spans:
            if span["end"] <= span["start"]:
                continue          # 空行に役割を付けても意味が無い
            style, fields = {}, []
            for key in _TEXT_STYLE_KEYS:
                if key not in span["style"]:
                    continue
                val = span["style"][key]
                if key == "color":
                    rgb = self._resolve_color(val)
                    if rgb is None:
                        continue
                    style["foregroundColor"] = {"opaqueColor": {"rgbColor": rgb}}
                    fields.append("foregroundColor")
                elif key == "fontSize":
                    style["fontSize"] = {"magnitude": val, "unit": "PT"}
                    fields.append("fontSize")
                else:
                    style[key] = val
                    fields.append(key)
            if span.get("link"):
                style["link"] = span["link"]
                fields.append("link")
            rng = {"type": "FIXED_RANGE",
                   "startIndex": span["start"], "endIndex": span["end"]}
            if fields:
                self.requests.append({"updateTextStyle": {
                    "objectId": object_id, "style": style,
                    "textRange": rng, "fields": ",".join(fields)}})
            if not span.get("paragraph"):
                continue
            para, pfields = {}, []
            for key in _PARA_STYLE_KEYS:
                if key in span["style"]:
                    para[key] = {"magnitude": span["style"][key], "unit": "PT"}
                    pfields.append(key)
            if pfields:
                self.requests.append({"updateParagraphStyle": {
                    "objectId": object_id, "style": para,
                    "textRange": rng, "fields": ",".join(pfields)}})

    # ---------- ページ番号 ----------

    def add_page_numbers(self, start: int | None = None) -> int:
        """ページ番号をテキストボックスで描画し、描画枚数を返す。

        Slides API は SLIDE_NUMBER プレースホルダを生成できない（createSlide の
        placeholderIdMappings に指定してもエラーにならず黙って無視される）ため、
        レイアウトの slideNumber 座標に合わせて自前で描画する。

        注意: 番号は add_slide() の呼び出し順に振る。add_slide(index=...) で
        挿入位置を指定したデッキでは実際の並び順と一致しない。
        """
        cfg = self.template.get("pageNumber", {})
        # keep_existing で残したスライドの後に積む場合は、その枚数分だけ番号を進める
        start = cfg.get("startAt", 1) + self.kept_slides if start is None else start
        font = cfg.get("font", "Arial")
        size = cfg.get("fontSize", 7)
        color = cfg.get("color", "#666666")
        align = cfg.get("align", "END")

        drawn = 0
        for offset, entry in enumerate(self._added):
            layout = entry["layout"]
            geo = layout.get("elements", {}).get("slideNumber")
            if not layout.get("hasPageNumber") or not geo:
                continue
            # 元の枠は数 mm 幅しかなく 2 桁で切れるため、右端を保ったまま最小 0.5in に広げる
            right = geo["x"] + geo["w"]
            w = max(geo["w"], 0.5)
            x = right - w if align == "END" else geo["x"]
            oid = self._next_id("pagenum")
            self.requests += [
                {
                    "createShape": {
                        "objectId": oid,
                        "shapeType": "TEXT_BOX",
                        "elementProperties": {
                            "pageObjectId": entry["slideId"],
                            "size": {
                                "width": {"magnitude": _auth.inches(w), "unit": "EMU"},
                                "height": {"magnitude": _auth.inches(geo["h"]), "unit": "EMU"},
                            },
                            "transform": {
                                "scaleX": 1, "scaleY": 1,
                                "translateX": _auth.inches(x),
                                "translateY": _auth.inches(geo["y"]),
                                "unit": "EMU",
                            },
                        },
                    }
                },
                {"insertText": {"objectId": oid, "text": str(start + offset)}},
                {
                    "updateTextStyle": {
                        "objectId": oid,
                        "style": {
                            "fontFamily": font,
                            "fontSize": {"magnitude": size, "unit": "PT"},
                            "foregroundColor": {
                                "opaqueColor": {"rgbColor": _auth.hex_to_rgb(color)}
                            },
                        },
                        "textRange": {"type": "ALL"},
                        "fields": "fontFamily,fontSize,foregroundColor",
                    }
                },
                {
                    "updateParagraphStyle": {
                        "objectId": oid,
                        "style": {"alignment": align},
                        "textRange": {"type": "ALL"},
                        "fields": "alignment",
                    }
                },
            ]
            drawn += 1
        return drawn

    # ---------- 実行 ----------

    def commit(self, chunk_size: int = MAX_REQUESTS_PER_BATCH) -> str:
        """溜めたリクエストを batchUpdate で実行し、プレゼンテーション URL を返す。"""
        try:
            # ローカル画像のアップロードは描画中に裏で走っている。
            # createImage の url を埋めてからでないと batchUpdate に出せない
            if self.assets is not None:
                n_img = self.assets.flush()
                if n_img:
                    print(f"  images uploaded: {n_img}")
            for n, chunk in enumerate(_batches(self.requests, chunk_size), 1):
                _retry(
                    lambda: self.slides.presentations().batchUpdate(
                        presentationId=self.presentation_id, body={"requests": chunk}
                    ).execute(),
                    what=f"batchUpdate ({len(chunk)} requests)")
                print(f"  batch {n}: {len(chunk)} requests")
            self.requests = []
            if self._notes or self.image_fixups:
                self._post_pass()
        finally:
            # Slides は挿入時に画像を中へコピーする。batchUpdate が失敗した場合も、
            # 「リンクを知る全員が閲覧可」で共有した一時アップロードを残さないよう
            # 必ずここで畳む
            if self.assets is not None:
                self.assets.cleanup()
        return f"https://docs.google.com/presentation/d/{self.presentation_id}/edit"

    def _post_pass(self) -> None:
        """スライド作成後にしか分からない情報を使う 2 回目の batchUpdate。

        - スピーカーノート … ノート枠の objectId は createSlide のレスポンスに無い
        - 画像の寸法補正 … createImage は**指定サイズに関係なく元の縦横比を保つ**ため、
          枠を埋める配置（fit="cover" / "stretch"）は作成時には実現できない。
          生成された要素の素の大きさを読み、transform を絶対値で置き換えて直す。
        """
        pres = _retry(
            lambda: self.slides.presentations().get(
                presentationId=self.presentation_id,
                fields=("slides(objectId,"
                        "slideProperties.notesPage.notesProperties.speakerNotesObjectId,"
                        "pageElements(objectId,size))"),
            ).execute(),
            what="presentations.get (post pass)")
        slides = pres.get("slides", [])
        note_ids = {
            s["objectId"]: (
                s.get("slideProperties", {})
                .get("notesPage", {})
                .get("notesProperties", {})
                .get("speakerNotesObjectId")
            )
            for s in slides
        }
        sizes = {
            el["objectId"]: el.get("size", {})
            for s in slides for el in s.get("pageElements", [])
        }

        reqs = []
        for slide_id, text in self._notes:
            oid = note_ids.get(slide_id)
            if not oid:
                print(t("  warn: notes placeholder for {slide_id} not found; "
                        "skipped", slide_id=slide_id), file=sys.stderr)
                continue
            reqs.append({"insertText": {"objectId": oid, "text": text}})
        n_notes = len(reqs)

        n_img = 0
        for oid, x, y, w, h in self.image_fixups:
            size = sizes.get(oid) or {}
            mw = size.get("width", {}).get("magnitude")
            mh = size.get("height", {}).get("magnitude")
            if not mw or not mh:
                print(t("  warn: could not read the size of image {oid}; "
                        "frame-filling placement was not applied", oid=oid),
                      file=sys.stderr)
                continue
            reqs.append({"updatePageElementTransform": {
                "objectId": oid,
                "applyMode": "ABSOLUTE",
                "transform": {
                    "scaleX": _auth.inches(w) / mw,
                    "scaleY": _auth.inches(h) / mh,
                    "translateX": _auth.inches(x),
                    "translateY": _auth.inches(y),
                    "unit": "EMU",
                },
            }})
            n_img += 1

        if reqs:
            _retry(
                lambda: self.slides.presentations().batchUpdate(
                    presentationId=self.presentation_id, body={"requests": reqs}
                ).execute(),
                what=f"batchUpdate (post pass, {len(reqs)} requests)")
            if n_notes:
                print(f"  speaker notes: {n_notes} slides")
            if n_img:
                print(f"  image fit: {n_img} images")
        self._notes = []
        self.image_fixups = []


# ---------- 図・画像のブロック ----------

# spec の "figures" で使える type と、位置引数として渡すキーの並び。
# ここに無いキーは snake_case に直してキーワード引数として渡す。
FIGURES: dict[str, tuple[str, list[str]]] = {
    # イメージ図（illustrations.py・図形だけで描く。ネットワーク不要）
    "icon":         ("icon",         ["name", "x", "y", "size"]),
    "icon_row":     ("icon_row",     ["x", "y", "w", "items"]),
    "icon_flow":    ("icon_flow",    ["x", "y", "w", "items"]),
    "icon_grid":    ("icon_grid",    ["x", "y", "w", "items"]),
    "pyramid":      ("pyramid",      ["x", "y", "w", "h", "items"]),
    "funnel":       ("funnel",       ["x", "y", "w", "h", "items"]),
    "venn":         ("venn",         ["x", "y", "w", "h", "items"]),
    "iceberg":      ("iceberg",      ["x", "y", "w", "h", "above", "below"]),
    "balance":      ("balance",      ["x", "y", "w", "h", "left", "right"]),
    "steps":        ("steps",        ["x", "y", "w", "h", "items"]),
    "layers":       ("layers",       ["x", "y", "w", "h", "items"]),
    "hub":          ("hub",          ["x", "y", "w", "h", "center", "items"]),
    "matrix":       ("matrix",       ["x", "y", "w", "h", "items"]),
    "before_after": ("before_after", ["x", "y", "w", "h", "before", "after"]),
    "journey":      ("journey",      ["x", "y", "w", "h", "items"]),
    "timeline":     ("timeline",     ["x", "y", "w", "items"]),
    # ブランドのアイコン素材（icons.py・Drive 経由で貼るので通信が要る。
    # --dry-run では同じ大きさの矩形に置き換えて座標だけ検査する）
    "asset_icon":       ("asset_icon",       ["name", "x", "y", "size"]),
    "asset_icon_row":   ("asset_icon_row",   ["x", "y", "w", "items"]),
    "asset_icon_flow":  ("asset_icon_flow",  ["x", "y", "w", "items"]),
    "asset_icon_grid":  ("asset_icon_grid",  ["x", "y", "w", "items"]),
    "asset_icon_cards": ("asset_icon_cards", ["x", "y", "w", "h", "items"]),
    # クラウドベンダーの公式アイコン（cloud_icons.py）。asset_icon と同じく
    # --dry-run では矩形に置き換えて座標だけ検査する
    "cloud_icon":      ("cloud_icon",      ["name", "x", "y", "size"]),
    "cloud_icon_row":  ("cloud_icon_row",  ["x", "y", "w", "items"]),
    "cloud_icon_flow": ("cloud_icon_flow", ["x", "y", "w", "items"]),
    "cloud_icon_grid": ("cloud_icon_grid", ["x", "y", "w", "items"]),
    "cloud_zone":      ("cloud_zone",      ["x", "y", "w", "h"]),
    # 構造図（diagrams.py の既存パーツ）
    # band は塗りだけの角丸矩形。図の下地（表紙・章扉の白カード等）に使う。
    # 中身より先に書くこと（後ろに書くと中身を覆う）
    "band":         ("band",         ["x", "y", "w", "h"]),
    "cards":        ("cards",        ["x", "y", "w", "h", "items"]),
    "flow":         ("flow",         ["x", "y", "w", "h", "items"]),
    "hbars":        ("hbars",        ["x", "y", "w", "items"]),
    "metric":       ("metric",       ["x", "y", "w", "h", "value", "caption"]),
    # 表・グラフ（charts.py）。pie は画像で貼るが、--dry-run では
    # プレースホルダに置き換えて自分で座標検査を通す
    "table":         ("table",         ["x", "y", "w", "headers", "rows"]),
    "vbars":         ("vbars",         ["x", "y", "w", "h", "items"]),
    "vbars_grouped": ("vbars_grouped", ["x", "y", "w", "h", "categories", "series"]),
    "vbars_stacked": ("vbars_stacked", ["x", "y", "w", "h", "categories", "series"]),
    "linechart":     ("linechart",     ["x", "y", "w", "h", "labels", "series"]),
    "pie":           ("pie",           ["x", "y", "size", "items"]),
    # ビジネスフレームワーク図（patterns.py・図形だけで描く。ネットワーク不要）
    "posmap":         ("posmap",         ["x", "y", "w", "h", "points"]),
    "gantt":          ("gantt",          ["x", "y", "w", "h", "columns", "rows"]),
    "orgchart":       ("orgchart",       ["x", "y", "w", "h", "tree"]),
    "lean_canvas":    ("lean_canvas",    ["x", "y", "w", "h", "blocks"]),
    "nested_circles": ("nested_circles", ["x", "y", "w", "h", "rings"]),
    "testimonial":    ("testimonial",    ["x", "y", "w", "h", "quote", "name"]),
    # イベント案内図（events.py・図形だけで描く。ネットワーク不要）
    "event_mode_badge": ("event_mode_badge", ["x", "y", "mode"]),
    "event_overview":   ("event_overview",   ["x", "y", "w", "rows"]),
    "event_timetable":  ("event_timetable",  ["x", "y", "w", "rows"]),
    "event_speakers":   ("event_speakers",   ["x", "y", "w", "speakers"]),
    "event_access":     ("event_access",     ["x", "y", "w", "h"]),
    # ページ部品と分析図（pages.py・図形だけで描く。ネットワーク不要）
    "governing_message": ("governing_message", ["x", "y", "w", "text"]),
    "lead_in":           ("lead_in",           ["x", "y", "w", "text"]),
    "so_what":           ("so_what",           ["x", "y", "w", "h", "text"]),
    "source_note":       ("source_note",       ["x", "y", "w", "source"]),
    # exhibit_frame の戻り値（内側領域）は JSON からは受け取れない。枠を描き、
    # 中身は内側座標（x+0.2 / ヘッダー下 +0.45 目安）を手で合わせて別の図で描く
    "exhibit_frame":     ("exhibit_frame",     ["x", "y", "w", "h", "number", "title"]),
    "mece_tree":         ("mece_tree",         ["x", "y", "w", "h", "tree"]),
    "waterfall":         ("waterfall",         ["x", "y", "w", "h", "items"]),
    "rating_matrix":     ("rating_matrix",     ["x", "y", "w", "columns", "rows"]),
    "exec_summary":      ("exec_summary",      ["x", "y", "w", "h", "situation",
                                                "complication", "resolution"]),
    "storyline":         ("storyline",         ["x", "y", "w", "titles"]),
    "ghost":             ("ghost",             ["x", "y", "w", "h", "slides"]),
    # コードサンプル（diagrams.py。等幅 + シンタックスハイライト。ネットワーク不要）
    "code_block":   ("code_block",   ["x", "y", "w", "h", "code"]),
    # 画像（images.py）
    "image":        ("image",        ["x", "y", "w", "h", "source"]),
    "aiImage":      ("ai_image",     ["x", "y", "w", "h", "prompt"]),
}

# API を呼ぶ（＝ --dry-run では実行できない）type
NETWORK_FIGURES = {"image", "aiImage"}

def min_table_row_h(size: float) -> float:
    """Slides のテーブル行が実際に取る最小の高さ（インチ）。

    `minRowHeight` をこれより小さくしても行は縮まない。文字の行高にセルの
    余白が乗った値で、実測（size 9 で約 0.34in、size 8.5 で約 0.32in）に
    合わせてある。高さの見積もりはこの値で下から抑える。
    """
    return max(0.28, size * 1.45 / 72 + 0.16)


def _snake(key: str) -> str:
    out = []
    for ch in key:
        if ch.isupper():
            out.append("_")
            out.append(ch.lower())
        else:
            out.append(ch)
    return "".join(out)


def _figure_args(fig: dict) -> tuple[list, dict]:
    """図のブロックを (位置引数, キーワード引数) に振り分ける。"""
    _, order = FIGURES[fig["type"]]
    args = [fig[k] for k in order if k in fig]
    kwargs = {_snake(k): v for k, v in fig.items()
              if k != "type" and k not in order}
    return args, kwargs


def draw_figures(canvas, figures: list, *, skip_network: bool = False) -> None:
    """figures ブロックを Canvas に描く。"""
    for fig in figures:
        kind = fig["type"]
        if skip_network and kind in NETWORK_FIGURES:
            continue
        method, _ = FIGURES[kind]
        args, kwargs = _figure_args(fig)
        getattr(canvas, method)(*args, **kwargs)


def validate_figures(spec: dict, page: dict, template: dict | None = None) -> list[str]:
    """figures ブロックを、API を呼ばずに検証する。

    `template` を渡すと、マスターのロゴ・フッター帯への重なりも検査する。
    ページ内に収まっていても帯に重なれば読めなくなるので、座標だけで分かる
    不具合としてここで止める。
    """
    problems = []
    pw = page.get("widthInches", 10.0)
    ph = page.get("heightInches", 5.625)
    band = footer_band(template) if template else None
    layouts = (template or {}).get("layouts", {})
    roles = (template or {}).get("roles", {})
    for i, s in enumerate(spec.get("slides", [])):
        figs = s.get("figures")
        if figs is None:
            continue
        # 全面の矩形を持つレイアウトはマスターの装飾を覆い隠すので、帯の検査から外す
        layout = layouts.get(roles.get(s.get("layout"), s.get("layout")), {})
        covers_footer = any(
            d.get("w", 0) > pw * 0.95 and d.get("h", 0) > ph * 0.9
            for d in (layout.get("decorations") or []))
        if not isinstance(figs, list):
            problems.append(t("slides[{i}]: 'figures' must be an array", i=i))
            continue
        for j, fig in enumerate(figs):
            where = f"slides[{i}].figures[{j}]"
            if not isinstance(fig, dict) or "type" not in fig:
                problems.append(t("{where}: missing 'type'", where=where))
                continue
            kind = fig["type"]
            if kind not in FIGURES:
                problems.append(t(
                    "{where}: unknown type '{kind}' (available: {available})",
                    where=where, kind=kind, available=sorted(FIGURES)))
                continue
            _, order = FIGURES[kind]
            missing = [k for k in order if k not in fig]
            if missing:
                problems.append(t(
                    "{where}: type '{kind}' is missing required keys: "
                    "{missing}", where=where, kind=kind, missing=missing))
                continue
            for k in ("x", "y", "w", "h"):
                if k in fig and not isinstance(fig[k], (int, float)):
                    problems.append(t(
                        "{where}: '{k}' must be a number (inches)",
                        where=where, k=k))
            # "size" が空間量（インチ）なのは位置引数に size を持つ type
            # （icon 系・pie）だけ。table 等ではフォントサイズ（pt）なので、
            # 高さの代わりに使うと 8.5pt を 8.5in と誤読してしまう
            spatial_size = fig.get("size", 0) if "size" in order else 0
            x, y = fig.get("x", 0), fig.get("y", 0)
            w = fig.get("w", spatial_size)
            h = fig.get("h", spatial_size)
            # 表は h を宣言しない。行数から見積もる。Slides のテーブル行には
            # フォントに応じた最小内寸があり、row_h をそれ未満にしても縮まない
            # （実測 ≒ 0.28in）。折り返せばさらに伸びるので、これは下限の見積もり
            if kind == "table" and isinstance(fig.get("rows"), list):
                floor = min_table_row_h(fig.get("size", 10))
                rh = max(fig.get("rowH", fig.get("row_h", 0.34)), floor)
                hh = max(fig.get("headerH", fig.get("header_h", 0.38)), floor)
                h = hh + rh * len(fig["rows"])
            if isinstance(x, (int, float)) and isinstance(w, (int, float)):
                if x < 0 or x + w > pw + 0.01:
                    problems.append(t(
                        "{where}: extends horizontally past the page ({pw}in) "
                        "(x={x} w={w} → right edge {right:.2f}in)",
                        where=where, pw=pw, x=x, w=w, right=x + w))
            if isinstance(y, (int, float)) and isinstance(h, (int, float)):
                if y < 0 or y + h > ph + 0.01:
                    problems.append(t(
                        "{where}: extends vertically past the page ({ph}in) "
                        "(y={y} h={h} → bottom edge {bottom:.2f}in)",
                        where=where, ph=ph, y=y, h=h, bottom=y + h))
                # 帯への重なりは **表だけ** 検査する。表は h を宣言せず、行数から
                # 出した高さがほぼそのまま実寸になるので判定が当たる。図形の図は
                # 宣言した枠の下端に余白があること（posmap の軸ラベル領域など）が
                # 多く、宣言値で判定すると誤検出になる。図形側は audit_bounds が
                # 実際に描いた座標で見ている
                elif (kind == "table" and band and not covers_footer
                      and y + h > band[0] + 0.01
                      and isinstance(x, (int, float)) and isinstance(w, (int, float))
                      and x < band[2] and x + w > band[1]):
                    problems.append(t(
                        "{where}: the table overlaps the master logo/footer "
                        "band (below y={band:.2f}in) (bottom edge "
                        "{bottom:.2f}in); reduce the rows or split it across "
                        "slides", where=where, band=band[0], bottom=y + h))
    return problems


class _StubDeck:
    """--dry-run で Canvas を動かすためのダミー。API は一切呼ばない。"""

    # ブランドアイコンは画像なので実物を取りに行けない。Canvas 側はこの旗を見て
    # 同じ大きさの矩形に置き換え、座標の検査だけ通す
    dry = True

    def __init__(self):
        self.requests: list[dict] = []
        self.assets = None
        self.image_fixups: list[tuple] = []


class DryRunDeck(_StubDeck):
    """TemplateDeck の代わりに置ける --dry-run 用のデッキ。

    add_slide / add_page_numbers / commit を API 抜きで受け流すので、コードで
    デッキを組み立てるスクリプト（scripts/scalar/*.py）は deck をこれに差し替える
    だけで、座標・文字量の検査だけを走らせられる。

    template は TemplateDeck と同じく `.template` として読めるようにしておく。
    ページ番号を自前で描くスクリプトがここを見に来るため。
    """

    def __init__(self, template: dict | None = None):
        super().__init__()
        self.template = template or {}
        self._n = 0
        self._counter = 0

    def _next_id(self, prefix: str) -> str:
        self._counter += 1
        return f"{prefix[:40]}_dry_{self._counter:03d}"

    def add_slide(self, layout_key, **kw):
        """TemplateDeck.add_slide と同じ形の戻り値を返す。

        呼び手が ref["layout"] からページ番号の位置を読むことがあるので、
        slideId だけでは足りない。
        """
        self._n += 1
        self.last = dict(kw, layout=layout_key)
        resolved = self.template.get("roles", {}).get(layout_key, layout_key)
        return {
            "slideId": f"dry_{self._n}",
            "placeholders": {},
            "layout": (self.template.get("layouts", {}) or {}).get(resolved, {}),
            "layoutKey": resolved,
        }

    def add_page_numbers(self, start=None):
        return 0

    def commit(self, chunk_size=500):
        return t("(dry-run: nothing was generated)")


def audit_figures(template: dict, spec: dict) -> list[str]:
    """figures を実際に座標へ展開し、重なり・文字溢れを API 抜きで検査する。

    生成してサムネイルを見るまで気づけない不具合を、仕様の段階で拾う。
    画像は実物を取りに行く必要があるためこの検査からは外れる。
    """
    from diagrams import Canvas  # 遅延 import（--dry-run 以外では毎回は要らない）

    out = []
    for i, s in enumerate(spec.get("slides", [])):
        figs = s.get("figures")
        if not figs:
            continue
        canvas = Canvas(_StubDeck(), f"dry_{i}", template)
        try:
            draw_figures(canvas, figs, skip_network=True)
        except Exception as e:  # 引数の不整合はここで初めて分かることがある
            out.append(t("slides[{i}]: failed to draw figures: {etype}: {e}",
                         i=i, etype=type(e).__name__, e=e))
            continue
        for msg in (canvas.audit_bounds() + canvas.audit_connectors()
                    + canvas.audit_overlaps() + canvas.audit_text_fit()):
            out.append(f"slides[{i}]: {msg}")
    out += audit_body_fit(template, spec)
    out += audit_image_slots(template, spec)
    return out


# ---------- 仕様の検証と組み立て ----------

def footer_band(template: dict) -> tuple[float, float, float] | None:
    """マスターが下端に敷く帯（ロゴ・著作権表記）の上端 y と x 範囲を返す。

    ページの下端まで使えると思って図を置くと、ロゴやフッターに重なる。
    ページサイズだけを見る検査ではこれを拾えないので、装飾の実座標から
    「ここより下には置けない」線を出す。該当が無ければ None。
    """
    page_h = template.get("pageSize", {}).get("heightInches", 5.625)
    decs = [d for d in template.get("masterDecorations", []) or []
            if isinstance(d.get("y"), (int, float)) and d["y"] > page_h * 0.75]
    if not decs:
        return None
    top = min(d["y"] for d in decs)
    x0 = min(d.get("x", 0.0) for d in decs)
    x1 = max(d.get("x", 0.0) + d.get("w", 0.0) for d in decs)
    return top, x0, x1


IMAGE_FIGURES = ("image", "aiImage")
_SLOT_KEYS = ("x", "y", "w", "h")


def layout_image_slots(template: dict, layout_key: str) -> list[dict]:
    """スライドのレイアウトが持つ画像の差し込み枠を返す。"""
    resolved = template.get("roles", {}).get(layout_key, layout_key)
    return (template.get("layouts", {}).get(resolved, {}) or {}).get("imageSlots") or []


def resolve_image_slots(template: dict, spec: dict) -> list[str]:
    """image / aiImage の座標を、レイアウトの差し込み枠から埋める。

    テンプレートが「ここに絵を置く」と決めている場所があるなら、そこに置く
    のが正しい。仕様では x/y/w/h を省略する（枠が複数あるときは "slot": N で
    選ぶ）。spec をその場で書き換え、補った内容を説明文のリストで返す。

    fit は省略時 "cover" にする。枠は縦横比まで含めてデザインなので、
    余白付き（contain）ではなく枠を埋めるのが既定として自然。
    """
    notes: list[str] = []
    for i, s in enumerate(spec.get("slides", [])):
        figs = s.get("figures")
        if not figs or not isinstance(figs, list):
            continue
        slots = layout_image_slots(template, s.get("layout", ""))
        auto = 0
        for j, fig in enumerate(figs):
            if not isinstance(fig, dict) or fig.get("type") not in IMAGE_FIGURES:
                continue
            explicit = fig.pop("slot", None)
            has_box = all(k in fig for k in _SLOT_KEYS)
            if has_box and explicit is None:
                continue
            if not slots:
                if explicit is not None or not has_box:
                    notes.append(t(
                        "slides[{i}].figures[{j}]: layout '{layout}' has no image "
                        "slot, so x/y/w/h are required",
                        i=i, j=j, layout=s.get("layout")))
                continue
            n = explicit if isinstance(explicit, int) else auto
            if n >= len(slots):
                notes.append(t(
                    "slides[{i}].figures[{j}]: slot {n} does not exist "
                    "(layout '{layout}' has {total})",
                    i=i, j=j, n=n, layout=s.get("layout"), total=len(slots)))
                continue
            slot = slots[n]
            fig.update({k: slot[k] for k in _SLOT_KEYS})
            fig.setdefault("fit", "cover")
            auto = n + 1
            notes.append(t(
                "slides[{i}].figures[{j}]: placed in the image slot of layout "
                "'{layout}' (x={x} y={y} w={w} h={h})",
                i=i, j=j, layout=s.get("layout"),
                x=slot["x"], y=slot["y"], w=slot["w"], h=slot["h"]))
    return notes


def audit_body_fit(template: dict, spec: dict) -> list[str]:
    """本文がプレースホルダの高さに収まるかを、API を呼ばずに見積もる。

    役割つきの行（見出しなど）は spaceAbove を足すので、素の行数だけで数えると
    溢れる。溢れは API がエラーにせず、サムネイルを見るまで気づけないため、
    ここで拾う。

    段落間隔をテンプレート既定のままにしている場合は実際の余白が分からないので、
    **少なめに見積もる**（見落とすことはあっても、誤検出はしない側に倒す）。
    """
    out = []
    defaults = spec.get("defaults", {})
    layouts = template.get("layouts", {})
    roles = template.get("roles", {})
    role_styles = {**DEFAULT_BODY_ROLES, **(template.get("bodyRoles") or {})}

    for i, s in enumerate(spec.get("slides", [])):
        bodies = s.get("bodies")
        if bodies is None and s.get("body") is not None:
            bodies = [s["body"]]
        if not bodies:
            continue
        layout = layouts.get(roles.get(s.get("layout"), s.get("layout")), {})
        elements = layout.get("elements") or {}
        base_size = ((layout.get("textStyles") or {}).get("body") or {}).get("fontSize")
        size = s.get("bodyFontSize", defaults.get("bodyFontSize")) or base_size
        if not size:
            continue
        ls = s.get("bodyLineSpacing", defaults.get("bodyLineSpacing")) or 100
        sa = s.get("bodySpaceAbove", defaults.get("bodySpaceAbove")) or 0
        sb = s.get("bodySpaceBelow", defaults.get("bodySpaceBelow")) or 0

        for col, value in enumerate(bodies):
            key = "body" if col == 0 else f"body#{col}"
            geo = elements.get(key)
            if not geo:
                continue
            per_line = (geo["w"] - 0.2) * 72 / size
            if per_line <= 0:
                continue
            used = 0.0
            for text, role in normalize_body_lines(value):
                plain, _ = parse_inline(text)
                width = sum(1.0 if ord(ch) > 0x2E80 else 0.5 for ch in plain)
                n = max(1, int(width / per_line + 0.999))
                style = role_styles.get(role) or {}
                fs = style.get("fontSize", size)
                used += (n * fs * 1.2 * (ls / 100)
                         + sa + sb
                         + style.get("spaceAbove", 0) + style.get("spaceBelow", 0))
            capacity = geo["h"] * 72
            if used > capacity * 1.02:
                out.append(t(
                    "slides[{i}] ({title}): body{col} needs about {used:.0f}pt "
                    "but the placeholder is {cap:.0f}pt. Reduce the text, lower "
                    "bodyFontSize, or split the slide",
                    i=i, title=s.get("title") or s.get("layout"),
                    col="" if col == 0 else f"#{col}",
                    used=used, cap=capacity))
    return out


def audit_image_slots(template: dict, spec: dict) -> list[str]:
    """テンプレートに枠があるのに、そこから外れた場所へ画像を置いていないか。

    枠があること自体に気づかないまま別の場所に置く、という取り違えを拾う。
    """
    out = []
    for i, s in enumerate(spec.get("slides", [])):
        slots = layout_image_slots(template, s.get("layout", ""))
        if not slots:
            continue
        for j, fig in enumerate(s.get("figures") or []):
            if not isinstance(fig, dict) or fig.get("type") not in IMAGE_FIGURES:
                continue
            if not all(k in fig for k in _SLOT_KEYS):
                continue
            if any(_boxes_overlap(fig, slot) >= 0.5 for slot in slots):
                continue
            near = slots[0]
            out.append(t(
                "slides[{i}].figures[{j}]: the layout has an image slot at "
                "(x={x} y={y} w={w} h={h}) but this image is placed elsewhere "
                "(x={fx} y={fy} w={fw} h={fh}). Omit x/y/w/h to use the slot",
                i=i, j=j, x=near["x"], y=near["y"], w=near["w"], h=near["h"],
                fx=fig["x"], fy=fig["y"], fw=fig["w"], fh=fig["h"]))
    return out


def _boxes_overlap(a: dict, b: dict) -> float:
    ix = max(0.0, min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"]))
    iy = max(0.0, min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"]))
    small = min(a["w"] * a["h"], b["w"] * b["h"])
    return (ix * iy) / small if small > 0 else 0.0


def validate_spec(template: dict, spec: dict) -> list[str]:
    """デッキ仕様をテンプレートと突き合わせ、問題点のリストを返す（空なら OK）。"""
    problems = []
    slides = spec.get("slides")
    if not isinstance(slides, list) or not slides:
        return [t("spec has no slides array")]

    layouts = template["layouts"]
    roles = template.get("roles", {})
    for i, s in enumerate(slides):
        where = f"slides[{i}]"
        key = s.get("layout")
        if not key:
            problems.append(t("{where}: missing 'layout'", where=where))
            continue
        resolved = roles.get(key, key)
        layout = layouts.get(resolved)
        if not layout:
            problems.append(
                t("{where}: cannot resolve layout '{key}' "
                  "(roles: {roles} / keys: {keys})", where=where, key=key,
                  roles=sorted(roles), keys=sorted(layouts))
            )
            continue
        declared = layout.get("placeholders", [])
        title_ph = "CENTERED_TITLE" if ("CENTERED_TITLE" in declared
                                        and "TITLE" not in declared) else "TITLE"
        for field, ph in (("title", title_ph), ("subtitle", "SUBTITLE")):
            if s.get(field) is not None and ph not in declared:
                problems.append(
                    t("{where}: layout '{key}' ({name}) has no {ph} but "
                      "'{field}' is specified (declares: {declared})",
                      where=where, key=key, name=layout["displayName"], ph=ph,
                      field=field, declared=declared)
                )
        if s.get("body") is not None and s.get("bodies") is not None:
            problems.append(t("{where}: 'body' and 'bodies' cannot be "
                              "specified together", where=where))
            continue
        bodies = s.get("bodies")
        if bodies is None and s.get("body") is not None:
            bodies = [s["body"]]
        if bodies is not None:
            if not isinstance(bodies, list):
                problems.append(t("{where}: 'bodies' must be an array",
                                  where=where))
                continue
            for col in bodies:
                for n, line in enumerate(col if isinstance(col, list) else [col], 1):
                    if isinstance(line, str):
                        continue
                    if isinstance(line, dict) and "text" in line:
                        continue
                    problems.append(t(
                        '{where}: body line {n} must be a string or '
                        '{{"text": …, "role": …}}', where=where, n=n))
            slots = [p for p in declared if p.split("#")[0] == "BODY"]
            if not slots:
                problems.append(
                    t("{where}: layout '{key}' ({name}) has no BODY but body "
                      "text is specified (declares: {declared})", where=where,
                      key=key, name=layout["displayName"], declared=declared)
                )
            elif len(bodies) > len(slots):
                problems.append(
                    t("{where}: layout '{key}' ({name}) has {slots} BODY "
                      "slots but {given} were given (declares: {declared})",
                      where=where, key=key, name=layout["displayName"],
                      slots=len(slots), given=len(bodies), declared=declared)
                )
    return problems


def build_from_spec(deck: TemplateDeck, spec: dict) -> list[str]:
    """spec からスライドを積む。図を描いた場合は検査結果を返す。"""
    defaults = spec.get("defaults", {})
    warnings: list[str] = []
    for i, s in enumerate(spec.get("slides", [])):
        ref = deck.add_slide(
            s["layout"],
            title=s.get("title"),
            subtitle=s.get("subtitle"),
            body=s.get("body"),
            bodies=s.get("bodies"),
            notes=s.get("notes"),
            body_font_size=s.get("bodyFontSize", defaults.get("bodyFontSize")),
            body_line_spacing=s.get("bodyLineSpacing", defaults.get("bodyLineSpacing")),
            body_space_above=s.get("bodySpaceAbove", defaults.get("bodySpaceAbove")),
            body_space_below=s.get("bodySpaceBelow", defaults.get("bodySpaceBelow")),
        )
        figs = s.get("figures")
        if not figs:
            continue
        from diagrams import Canvas  # 図を使う spec のときだけ読み込む
        canvas = Canvas(deck, ref["slideId"], deck.template)
        draw_figures(canvas, figs)
        for msg in (canvas.audit_bounds() + canvas.audit_connectors()
                    + canvas.audit_overlaps() + canvas.audit_text_fit()):
            warnings.append(f"slides[{i}] ({s.get('title') or s['layout']}): {msg}")
    return warnings


def main() -> int:
    p = argparse.ArgumentParser(
        description=t("generate a presentation from a template"))
    p.add_argument("--template", required=True,
                   help=t("path to template.json"))
    p.add_argument("--spec", required=True,
                   help=t("path to the deck-spec JSON"))
    p.add_argument("--title",
                   help=t("presentation title (defaults to spec.title)"))
    p.add_argument("--folder", help=t("destination Drive folder URL or ID"))
    p.add_argument("--dry-run", action="store_true",
                   help=t("validate the spec only, without calling the API"))
    p.add_argument("--no-page-numbers", action="store_true",
                   help=t("do not draw page numbers"))
    p.add_argument("--keep-existing", action="store_true",
                   help=t("keep the slides bundled with the template"))
    p.add_argument("--strict", action="store_true",
                   help=t("fail if the figure audit (overlaps / text "
                          "overflow) reports anything"))
    args = p.parse_args()

    template = load_template(args.template)
    with open(args.spec) as f:
        spec = json.load(f)

    # 検証より先に、レイアウトが持つ画像枠を座標へ解決しておく
    # （以降の検証・監査・生成はすべて解決後の座標を見る）
    slot_notes = resolve_image_slots(template, spec)
    for msg in slot_notes:
        print(f"  {msg}")

    problems = validate_spec(template, spec)
    problems += validate_figures(spec, template.get("pageSize", {}), template)
    if problems:
        print(t("The spec has problems:"), file=sys.stderr)
        for msg in problems:
            print(f"  - {msg}", file=sys.stderr)
        return 1

    title = args.title or spec.get("title")
    if not title:
        print(t("No title (specify --title or spec.title)"), file=sys.stderr)
        return 1

    if args.dry_run:
        print(t("OK: the {n}-slide spec is consistent with the template",
                n=len(spec["slides"])))
        for i, s in enumerate(spec["slides"], 1):
            resolved = template.get("roles", {}).get(s["layout"], s["layout"])
            n_fig = len(s.get("figures") or [])
            extra = t("  + {n} figures", n=n_fig) if n_fig else ""
            print(f"  {i:2d}. {s['layout']:24s} -> "
                  f"{template['layouts'][resolved]['displayName']}{extra}")
        findings = audit_figures(template, spec)
        if findings:
            print("\n" + t("Figure audit found {n} findings (images excluded; "
                           "they need the real file):", n=len(findings)),
                  file=sys.stderr)
            for msg in findings:
                print(f"  - {msg}", file=sys.stderr)
            return 1 if args.strict else 0
        if any(s.get("figures") for s in spec["slides"]):
            print(t("figure audit (connectors / overlaps / text overflow): "
                    "no problems"))
        return 0

    deck = TemplateDeck.create(
        template, title=title, folder=args.folder, keep_existing=args.keep_existing
    )
    warnings = build_from_spec(deck, spec)
    if not args.no_page_numbers:
        n = deck.add_page_numbers()
        print(f"  page numbers: {n} slides")
    url = deck.commit()
    print(f"Done! {len(deck.slide_ids)} slides created.")
    if warnings:
        print("\n" + t("Figure audit found {n} findings:", n=len(warnings)),
              file=sys.stderr)
        for msg in warnings:
            print(f"  - {msg}", file=sys.stderr)
    print(f"Open: {url}")
    return 1 if (warnings and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
