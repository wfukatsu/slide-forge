#!/usr/bin/env python3
"""スライドに写真・イラストなどの「画像」を載せるための機能。

本スキルで図を作る手段は 3 つある。用途で使い分ける。

| やりたいこと | 使うもの |
|---|---|
| 構造を正確に示す（フロー・構成図・グラフ） | `diagrams.Canvas` |
| 概念を絵で示す（比喩図・アイコン・ピクトグラム） | `illustrations`（図形で描く。オフラインで動く） |
| 雰囲気・情景を示す（表紙・扉・挿絵） | 本モジュール（AI 生成 or 手持ちの画像） |

--- 1. AI で生成する -------------------------------------------------------

    from images import generate
    path = generate("複数のマイクロサービスがひとつの台帳を共有している様子",
                    style="flat_vector", palette=template["colors"], aspect="16:9")

生成物は内容のハッシュでキャッシュされる（同じプロンプト・スタイル・比率なら
再生成しない）。プロンプトはサイドカーの .json に残るので後から追跡できる。

    # コマンドラインから
    python scripts/images.py --prompt "…" --style flat_vector --out out/x.png

`GEMINI_API_KEY` が必要。画像モデルは無料枠のクォータが 0 のことがあり、その場合は
429 が返る（課金を有効にしたプロジェクトのキーが要る）。

--- 2. 手持ちの画像を貼る --------------------------------------------------

Canvas 経由で使う。ローカルパス / http(s) URL / Drive のファイル URL・ID を受け付ける。

    d = Canvas(deck, slide_id, template)
    d.image(0.6, 1.1, 4.2, 2.6, "assets/screenshot.png", fit="contain")
    d.ai_image(5.2, 1.1, 4.2, 2.6, "自律型エージェントが夜間にビルドを回している様子")

ローカルファイルは Drive に一時アップロードして「リンクを知る全員が閲覧可」にし、
その URL を `createImage` に渡す。Slides は挿入時に画像を**プレゼンテーション内へ
コピーする**ため、`deck.commit()` の直後に一時ファイルを削除している
（`AssetStore.cleanup()`。`TemplateDeck.commit()` から自動で呼ばれる）。

Slides が受け付ける形式は PNG / JPEG / GIF のみ、50MB 未満、25 メガピクセル未満。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import struct
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _auth  # noqa: E402
from _i18n import t, register  # noqa: E402
from colors import Palette  # noqa: E402

register({
    "image {name}": "画像 {name}",
    "Unknown style '{style}'. Available: {styles}":
        "未知のスタイル '{style}'。利用可能: {styles}",
    "GEMINI_API_KEY is not set.\n"
    "  Create a key at https://aistudio.google.com/apikey, then "
    "export GEMINI_API_KEY=... or save it to config/gemini_api_key.\n"
    "  The image model has zero free-tier quota, so the key must belong to "
    "a project with billing enabled.":
        "GEMINI_API_KEY が設定されていません。\n"
        "  https://aistudio.google.com/apikey でキーを作り、"
        "export GEMINI_API_KEY=… するか、config/gemini_api_key に保存してください。\n"
        "  画像モデルは無料枠のクォータが 0 のため、課金を有効にした"
        "プロジェクトのキーが必要です。",
    "Image generation quota exceeded (HTTP 429 / model={model}).\n"
    "  {message}\n"
    "  The image model has zero free-tier quota; use an API key from a "
    "Google Cloud project with billing enabled.":
        "画像生成のクォータを超えています（HTTP 429 / model={model}）。\n"
        "  {message}\n"
        "  画像モデルは無料枠のクォータが 0 です。"
        "課金を有効にした Google Cloud プロジェクトの API キーを使ってください。",
    "Image generation failed (HTTP {code} / model={model}): {message}":
        "画像生成に失敗しました（HTTP {code} / model={model}）: {message}",
    "Image generation failed: {message}": "画像生成に失敗しました: {message}",
    "The model returned no candidates: {body}":
        "モデルが候補を返しませんでした: {body}",
    "No image was returned (finishReason={reason}). It may have been blocked "
    "by the safety filter: {text}":
        "画像が返りませんでした（finishReason={reason}）。"
        "安全フィルタで止まった可能性があります: {text}",
    "aspect must be one of {aspects} (got: {aspect})":
        "aspect は {aspects} のいずれか（指定: {aspect}）",
    "The model returned a format Slides cannot handle: {mime} (PNG/JPEG/GIF only)":
        "Slides が扱えない形式が返りました: {mime}（PNG/JPEG/GIF のみ）",
    "Cannot read image dimensions (only PNG / JPEG / GIF are supported)":
        "画像の寸法を読めません（PNG / JPEG / GIF のみ対応）",
    "Image not found: {source}": "画像が見つかりません: {source}",
    "Slides cannot handle this format: {mime} ({file}). "
    "Convert it to PNG / JPEG / GIF":
        "Slides が扱えない形式です: {mime}（{file}）。"
        "PNG / JPEG / GIF に変換してください",
    "Image too large ({size:.1f}MB / 50MB limit)":
        "画像が大きすぎます（{size:.1f}MB / 上限 50MB）",
    "  warn: could not change the sharing settings of {file_id}: {error}":
        "  warn: {file_id} の共有設定を変更できませんでした: {error}",
    "  warn: could not delete the temporary image {file_id}: {error}":
        "  warn: 一時画像 {file_id} を削除できませんでした: {error}",
    "  warn: failed to remove public sharing from {file_id}: {error}":
        "  warn: {file_id} の共有解除に失敗しました: {error}",
    "Cannot extract the Drive file ID: {url}":
        "Drive のファイル ID を抽出できません: {url}",
    "fit must be one of contain / cover / stretch: {fit}":
        "fit は contain / cover / stretch のいずれか: {fit}",
    "  warn: cannot read the actual size of {source}, so fit=\"cover\" cannot "
    "be applied; placing it as contain (aspect preserved)":
        "  warn: {source} の実寸が取れないため fit=\"cover\" を"
        "適用できません。contain 相当（比率保持）で配置します",
    "  warn: this deck does not support image size fixups; "
    "fit will behave like contain":
        "  warn: この deck は画像の寸法補正に対応していません。"
        "fit は contain 相当になります",
    "  note: the Slides API cannot round image corners (rounded is ignored)":
        "  note: 画像の角丸は Slides API では指定できません（rounded は無視）",
    "Generate slide images with AI (results are cached)":
        "スライド用の画像を AI で生成する（結果はキャッシュされる）",
    "What to draw (Japanese OK)": "描いてほしい内容（日本語可）",
    "Path of the template.json to borrow colors from":
        "配色を借りる template.json のパス",
    "Extra instructions": "追加の指示",
    "Image model (default {model})": "画像モデル（既定 {model}）",
    "Copy destination path (prints the cache path if omitted)":
        "コピー先のパス（省略時はキャッシュのパスを表示）",
    "Ignore the cache and regenerate": "キャッシュを無視して再生成",
    "Print the assembled prompt and exit (does not call the API)":
        "組み立てたプロンプトを表示して終了（API を呼ばない）",
})

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CACHE = os.path.join(SKILL_DIR, "cache", "images")
DEFAULT_MODEL = "gemini-3.1-flash-image"
API_ROOT = "https://generativelanguage.googleapis.com/v1beta/models"

# imageConfig.aspectRatio が受け付ける値
ASPECTS = ("1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9")

# Slides の createImage が受け付ける形式
SLIDES_MIME = {"image/png", "image/jpeg", "image/gif"}


# ---------- スタイル ----------

STYLES: dict[str, str] = {
    "flat_vector": (
        "Flat vector illustration, clean geometric shapes, minimal flat design, "
        "solid fills with subtle tints, thin consistent line weight, generous negative space, "
        "no gradients on large areas, no drop shadows, corporate presentation illustration"
    ),
    "line_art": (
        "Minimal single-weight line art illustration, monoline outlines only, no fills, "
        "technical sketch feel, plenty of negative space"
    ),
    "isometric": (
        "Isometric technical illustration, 30-degree axonometric projection, "
        "flat solid colors with one flat shade per face, no perspective distortion, "
        "clean edges, infographic style"
    ),
    "photo": (
        "Photorealistic photograph, natural soft lighting, shallow depth of field, "
        "documentary style, neutral color grading"
    ),
    "blueprint": (
        "Technical blueprint illustration, thin white line work on a deep blue field, "
        "schematic drafting style, dimension marks, no photographic texture"
    ),
    "paper": (
        "Cut-paper collage illustration, layered flat paper shapes with soft edge shadows, "
        "muted palette, tactile craft feel"
    ),
}
DEFAULT_STYLE = "flat_vector"

# どのスタイルでも常に効かせる制約。スライドに載せる前提の指示。
GUARDRAILS = (
    "Do not render any text, letters, numbers, words, labels, watermarks, logos or UI copy "
    "anywhere in the image. Composition centered with clear margins. "
    "Plain white background unless the subject requires otherwise. "
    "Single coherent illustration, not a grid or collage of variations."
)


def palette_hint(colors: dict | None) -> str:
    """テンプレートの配色を、生成プロンプトに載せる指示文にする。"""
    if not colors:
        return ""
    p = Palette(colors)
    return (
        f"Strictly limit the palette to these colors and tints of them: "
        f"primary {p.primary}, accent {p.info}, positive {p.success}, "
        f"neutral dark {p.text}, neutral light {p.surfaceAlt}."
    )


def build_prompt(subject: str, *, style: str = DEFAULT_STYLE,
                 palette: dict | None = None, extra: str | None = None) -> str:
    """被写体の説明から、実際に投げるプロンプト全文を組み立てる。"""
    if style not in STYLES:
        raise ValueError(
            t("Unknown style '{style}'. Available: {styles}",
              style=style, styles=sorted(STYLES))
        )
    parts = [STYLES[style], subject.strip(), palette_hint(palette), GUARDRAILS]
    if extra:
        parts.insert(2, extra.strip())
    return "\n".join(p for p in parts if p)


# ---------- 生成 ----------

class ImageGenerationError(RuntimeError):
    pass


def _api_key() -> str:
    """Resolve the Gemini API key.

    Order: $GEMINI_API_KEY / $GOOGLE_API_KEY env vars, then the
    `gemini_api_key` file in the auth config directories (repo `config/` is
    gitignored, same policy as the OAuth credentials).
    """
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        import _auth
        for d in _auth.config_dirs():
            path = os.path.join(d, "gemini_api_key")
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    key = f.read().strip()
                if key:
                    break
    if not key:
        raise ImageGenerationError(
            t("GEMINI_API_KEY is not set.\n"
              "  Create a key at https://aistudio.google.com/apikey, then "
              "export GEMINI_API_KEY=... or save it to config/gemini_api_key.\n"
              "  The image model has zero free-tier quota, so the key must "
              "belong to a project with billing enabled.")
        )
    return key


def _post_json(url: str, payload: dict, *, timeout: int = 180) -> dict:
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _call_model(prompt: str, *, model: str, aspect: str, key: str,
                retries: int = 2) -> tuple[bytes, str]:
    """画像モデルを呼び、(バイト列, mimeType) を返す。"""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": aspect},
        },
    }
    url = f"{API_ROOT}/{model}:generateContent?key={key}"
    last = None
    for attempt in range(retries + 1):
        try:
            data = _post_json(url, payload)
            break
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            try:
                msg = json.loads(body)["error"]["message"]
            except Exception:
                msg = body[:400]
            if e.code == 429:
                raise ImageGenerationError(
                    t("Image generation quota exceeded (HTTP 429 / model={model}).\n"
                      "  {message}\n"
                      "  The image model has zero free-tier quota; use an API key "
                      "from a Google Cloud project with billing enabled.",
                      model=model, message=msg)
                ) from None
            if e.code in (500, 502, 503, 504) and attempt < retries:
                last = msg
                time.sleep(2 ** attempt)
                continue
            raise ImageGenerationError(
                t("Image generation failed (HTTP {code} / model={model}): {message}",
                  code=e.code, model=model, message=msg)
            ) from None
    else:  # pragma: no cover - 到達しない（break か raise で抜ける）
        raise ImageGenerationError(t("Image generation failed: {message}", message=last))

    cands = data.get("candidates") or []
    if not cands:
        raise ImageGenerationError(
            t("The model returned no candidates: {body}", body=json.dumps(data)[:300])
        )
    reason = cands[0].get("finishReason")
    for part in cands[0].get("content", {}).get("parts", []):
        inline = part.get("inlineData")
        if inline and inline.get("data"):
            import base64
            return base64.b64decode(inline["data"]), inline.get("mimeType", "image/png")
    texts = [p.get("text", "") for p in cands[0].get("content", {}).get("parts", [])]
    raise ImageGenerationError(
        t("No image was returned (finishReason={reason}). It may have been "
          "blocked by the safety filter: {text}",
          reason=reason, text=" ".join(texts)[:300])
    )


def generate(subject: str, *, style: str = DEFAULT_STYLE, palette: dict | None = None,
             aspect: str = "16:9", extra: str | None = None,
             model: str | None = None, cache_dir: str | None = None,
             force: bool = False) -> str:
    """画像を生成してローカルパスを返す。同じ入力ならキャッシュを使う。

    キャッシュのキーは (model, style, aspect, プロンプト全文) のハッシュ。
    デッキを作り直しても同じ絵が出るので、再現性がある。
    """
    if aspect not in ASPECTS:
        raise ValueError(t("aspect must be one of {aspects} (got: {aspect})",
                           aspects=ASPECTS, aspect=aspect))
    model = model or os.environ.get("GSLIDES_IMAGE_MODEL", DEFAULT_MODEL)
    prompt = build_prompt(subject, style=style, palette=palette, extra=extra)

    cache_dir = cache_dir or os.environ.get("GSLIDES_IMAGE_CACHE", DEFAULT_CACHE)
    os.makedirs(cache_dir, exist_ok=True)
    digest = hashlib.sha256(
        "\x00".join([model, style, aspect, prompt]).encode()
    ).hexdigest()[:20]
    path = os.path.join(cache_dir, f"{digest}.png")
    if os.path.exists(path) and not force:
        return path

    key = _api_key()
    blob, mime = _call_model(prompt, model=model, aspect=aspect, key=key)
    if mime not in SLIDES_MIME:
        raise ImageGenerationError(
            t("The model returned a format Slides cannot handle: {mime} "
              "(PNG/JPEG/GIF only)", mime=mime)
        )
    # 中断で壊れた PNG がキャッシュに残ると exists() チェックで恒久的に再利用される
    # ため、一時ファイルに書いてから os.replace でアトミックに置く（icons.py と同じ流儀）
    tmp = f"{path}.{os.getpid()}.part"
    with open(tmp, "wb") as f:
        f.write(blob)
    os.replace(tmp, path)
    with open(path + ".json", "w") as f:
        json.dump({"model": model, "style": style, "aspect": aspect,
                   "subject": subject, "prompt": prompt, "mime": mime},
                  f, ensure_ascii=False, indent=2)
    return path


# ---------- 画像の実寸 ----------

def image_size(data: bytes) -> tuple[int, int]:
    """PNG / JPEG / GIF のヘッダから (幅, 高さ) をピクセルで返す。

    アスペクト比を保った配置に必要。Pillow を足したくないのでヘッダだけ読む。
    """
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:6] in (b"GIF87a", b"GIF89a"):
        w, h = struct.unpack("<HH", data[6:10])
        return w, h
    if data[:3] == b"\xff\xd8\xff":
        i = 2
        n = len(data)
        while i + 9 < n:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            if marker == 0xD9:
                break
            seg = struct.unpack(">H", data[i + 2:i + 4])[0]
            # SOF0..SOF15（DHT=C4 / JPG=C8 / DAC=CC を除く）に寸法が入る
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            i += 2 + seg
    raise ValueError(t("Cannot read image dimensions (only PNG / JPEG / GIF "
                       "are supported)"))


def _remote_image_size(url: str, limit: int = 64 * 1024) -> tuple[int, int]:
    """リモート画像の先頭だけ取得して (幅, 高さ) をピクセルで返す。

    fit="cover" / "contain" の計算には実寸が要る。全体をダウンロードせず
    ヘッダが読める分だけ取る。読めなければ ValueError。
    """
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "gslides-template"})
    with urllib.request.urlopen(req, timeout=15) as r:
        head = r.read(limit)
    return image_size(head)


def sniff_mime(path: str, data: bytes | None = None) -> str:
    if data:
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            return "image/png"
        if data[:3] == b"\xff\xd8\xff":
            return "image/jpeg"
        if data[:6] in (b"GIF87a", b"GIF89a"):
            return "image/gif"
    return mimetypes.guess_type(path)[0] or "application/octet-stream"


# ---------- Slides から参照できる URL にする ----------

class AssetStore:
    """画像ソースを `createImage` に渡せる URL に解決する。

    - http(s) の URL … そのまま使う
    - Drive の URL / `drive:<id>` … 共有設定を付けて直リンクにする
    - ローカルのパス … Drive へ一時アップロードして共有し、直リンクにする

    一時アップロードしたファイルは `cleanup()` で消す。Slides は挿入時に画像を
    プレゼンテーション内へコピーするので、消しても表示は壊れない。
    """

    def __init__(self, drive=None):
        self._drive = drive
        self.temp_ids: list[str] = []
        self.shared_ids: list[str] = []
        self._resolved: dict[str, str] = {}

    @property
    def drive(self):
        if self._drive is None:
            self._drive = _auth.services()[1]
        return self._drive

    # -- 解決 --

    def url_for(self, source: str) -> str:
        if source in self._resolved:
            return self._resolved[source]
        url = self._resolve(source)
        self._resolved[source] = url
        return url

    def _resolve(self, source: str) -> str:
        if source.startswith(("http://", "https://")):
            if "drive.google.com" in source or "docs.google.com" in source:
                return self._drive_url(_drive_file_id(source))
            return source
        if source.startswith("drive:"):
            return self._drive_url(source[len("drive:"):])

        path = os.path.expanduser(source)
        if not os.path.exists(path):
            raise FileNotFoundError(t("Image not found: {source}", source=source))
        with open(path, "rb") as f:
            data = f.read()
        mime = sniff_mime(path, data)
        if mime not in SLIDES_MIME:
            raise ValueError(
                t("Slides cannot handle this format: {mime} ({file}). "
                  "Convert it to PNG / JPEG / GIF",
                  mime=mime, file=os.path.basename(path))
            )
        if len(data) > 49 * 1024 * 1024:
            raise ValueError(t("Image too large ({size:.1f}MB / 50MB limit)",
                               size=len(data) / 1e6))
        return self._drive_url(self._upload(path, mime))

    def _upload(self, path: str, mime: str) -> str:
        from googleapiclient.http import MediaFileUpload
        media = MediaFileUpload(path, mimetype=mime, resumable=False)
        meta = {"name": f"gslides-tmp-{os.path.basename(path)}"}
        fid = self.drive.files().create(
            body=meta, media_body=media, fields="id"
        ).execute()["id"]
        self.temp_ids.append(fid)
        return fid

    def _drive_url(self, file_id: str) -> str:
        """Drive のファイルを「リンクを知る全員が閲覧可」にして直リンクを返す。

        `createImage` は URL を**匿名で**取りに行くため、認証済みの自分が
        アクセスできるだけでは足りない。挿入後は cleanup() で共有を解除する。
        """
        try:
            self.drive.permissions().create(
                fileId=file_id, body={"type": "anyone", "role": "reader"},
                fields="id",
            ).execute()
            self.shared_ids.append(file_id)
        except Exception as e:  # 既に公開済み、または組織ポリシーで禁止
            print(t("  warn: could not change the sharing settings of {file_id}: "
                    "{error}", file_id=file_id, error=e), file=sys.stderr)
        return f"https://drive.google.com/uc?export=download&id={file_id}"

    # -- 後始末 --

    def cleanup(self) -> None:
        """一時アップロードを削除し、既存ファイルに付けた公開共有を外す。"""
        for fid in self.temp_ids:
            try:
                self.drive.files().delete(fileId=fid).execute()
            except Exception as e:
                print(t("  warn: could not delete the temporary image {file_id}: "
                        "{error}", file_id=fid, error=e), file=sys.stderr)
        temp = set(self.temp_ids)
        for fid in self.shared_ids:
            if fid in temp:
                continue  # ファイルごと消えている
            try:
                perms = self.drive.permissions().list(
                    fileId=fid, fields="permissions(id,type)").execute()
                for p in perms.get("permissions", []):
                    if p.get("type") == "anyone":
                        self.drive.permissions().delete(
                            fileId=fid, permissionId=p["id"]).execute()
            except Exception as e:
                print(t("  warn: failed to remove public sharing from {file_id}: "
                        "{error}", file_id=fid, error=e), file=sys.stderr)
        self.temp_ids = []
        self.shared_ids = []
        self._resolved = {}


def _drive_file_id(url: str) -> str:
    import re
    m = re.search(r"/file/d/([a-zA-Z0-9_-]{10,})", url) or \
        re.search(r"[?&]id=([a-zA-Z0-9_-]{10,})", url) or \
        re.search(r"/d/([a-zA-Z0-9_-]{10,})", url)
    if not m:
        raise ValueError(t("Cannot extract the Drive file ID: {url}", url=url))
    return m.group(1)


# ---------- Canvas に生やすメソッド ----------

class ImageMixin:
    """`Canvas` に画像配置を足すミックスイン。diagrams.Canvas が継承する。"""

    def _asset_store(self) -> AssetStore:
        store = getattr(self.deck, "assets", None)
        if store is None:
            store = AssetStore(getattr(self.deck, "drive", None))
            try:
                self.deck.assets = store
            except Exception:
                pass
        return store

    @staticmethod
    def _fit_rect(box, px_w, px_h, mode):
        """(x, y, w, h) の枠に px_w×px_h の画像を収める矩形と crop を返す。"""
        x, y, w, h = box
        if not px_w or not px_h or mode == "stretch":
            return (x, y, w, h), None
        ar_img = px_w / px_h
        ar_box = w / h
        if mode == "cover":
            # 枠いっぱいに敷き、はみ出す分を crop で切る（crop は左右/上下の比率）
            if ar_img > ar_box:
                cut = (1 - ar_box / ar_img) / 2
                return (x, y, w, h), {"leftOffset": cut, "rightOffset": cut}
            cut = (1 - ar_img / ar_box) / 2
            return (x, y, w, h), {"topOffset": cut, "bottomOffset": cut}
        # contain: 比率を保ったまま枠内に収め、中央に置く
        if ar_img > ar_box:
            nw, nh = w, w / ar_img
        else:
            nh, nw = h, h * ar_img
        return (x + (w - nw) / 2, y + (h - nh) / 2, nw, nh), None

    def image(self, x, y, w, h, source, *, fit="contain", caption=None,
              caption_size=9, caption_color=None, caption_at="image",
              outline=None, outline_weight=1.0, rounded=False, alt=None) -> str:
        """画像を配置し、objectId を返す。

        source はローカルパス / http(s) URL / Drive の URL または `drive:<id>`。

        fit:
          - "contain" … 比率を保って枠内に収める（既定）。余白ができる
          - "cover"   … 枠を埋め、はみ出しを切り落とす
          - "stretch" … 枠に合わせて引き伸ばす（比率が崩れる）

        caption を渡すと下にキャプションを置く。`caption_at`:

          - "image" … 画像の実際の下端に付ける（既定）。1 枚だけ置くときはこちら
          - "box"   … 枠の下端に付ける。複数の画像を横に並べるとき、fit の違いで
                      キャプションの高さがバラバラになるのを防ぐ

        戻り値は画像の objectId。
        """
        if fit not in ("contain", "cover", "stretch"):
            raise ValueError(t("fit must be one of contain / cover / stretch: {fit}",
                               fit=fit))
        store = self._asset_store()
        url = store.url_for(source)

        px = (0, 0)
        local = os.path.expanduser(source)
        if os.path.exists(local):
            with open(local, "rb") as f:
                try:
                    px = image_size(f.read(64 * 1024))
                except ValueError:
                    px = (0, 0)
        else:
            # リモート画像（http / Drive）も先頭だけ取得して実寸を読む。
            # cover を実寸なしで進めると後処理の絶対 transform が実質 stretch になり
            # 比率が崩れるため、読めなければ contain（比率保持）へ落として警告する
            try:
                px = _remote_image_size(url)
            except Exception:
                px = (0, 0)
            if not px[0] and fit != "stretch":
                if fit == "cover":
                    print(t("  warn: cannot read the actual size of {source}, so "
                            "fit=\"cover\" cannot be applied; placing it as "
                            "contain (aspect preserved)", source=source),
                          file=sys.stderr)
                fit = "contain"

        rect, crop = self._fit_rect((x, y, w, h), px[0], px[1], fit)
        oid = self._oid("i")
        self.deck.requests.append({"createImage": {
            "objectId": oid, "url": url,
            "elementProperties": self._elem_props(*rect)}})
        if fit != "contain":
            # createImage は指定サイズに関係なく元の縦横比を保つ（＝常に contain
            # 相当に縮められる）。枠を埋めたい場合は、生成後に transform を
            # 上書きして直すしかない。commit() の後処理で拾わせる
            fixups = getattr(self.deck, "image_fixups", None)
            if fixups is None:
                print(t("  warn: this deck does not support image size fixups; "
                        "fit will behave like contain"), file=sys.stderr)
            else:
                fixups.append((oid, *rect))

        props, fields = {}, []
        if crop:
            props["cropProperties"] = crop
            fields.append("cropProperties")
        if outline:
            props["outline"] = {
                "outlineFill": {"solidFill": {
                    "color": {"rgbColor": _auth.hex_to_rgb(outline)}, "alpha": 1}},
                "weight": {"magnitude": int(outline_weight * _auth.EMU_PER_PT), "unit": "EMU"},
                "dashStyle": "SOLID",
            }
            fields.append("outline")
        if props:
            self.deck.requests.append({"updateImageProperties": {
                "objectId": oid, "imageProperties": props,
                "fields": ",".join(fields)}})
        if alt:
            self.deck.requests.append({"updatePageElementAltText": {
                "objectId": oid, "description": alt}})
        if rounded:
            # Slides に角丸マスクは無い。枠線で代用する旨を明示しておく
            print(t("  note: the Slides API cannot round image corners "
                    "(rounded is ignored)"), file=sys.stderr)

        self._seq += 1
        self.rects[oid] = (*rect, "IMAGE")
        # 画像は不透明。先に置かれた文字を覆い隠すので solids として記録する
        self.solids.append({"rect": rect, "seq": self._seq,
                            "name": t("image {name}",
                                      name=os.path.basename(str(source))[:16])})
        if caption:
            cy = (y + h) if caption_at == "box" else (rect[1] + rect[3])
            self.label(x, cy + 0.05, w, 0.26, caption,
                       size=caption_size, align="CENTER", valign="TOP",
                       color=caption_color or self.P.muted)
        return oid

    def ai_image(self, x, y, w, h, subject, *, style=DEFAULT_STYLE, aspect=None,
                 extra=None, model=None, force=False, **kw) -> str:
        """AI で画像を生成して配置する。引数の残りは image() と同じ。

        aspect を省略すると枠の縦横比に最も近い比率を選ぶ。生成物はキャッシュされる
        ので、同じ subject でデッキを作り直しても絵は変わらない。
        """
        if aspect is None:
            target = w / h
            aspect = min(ASPECTS, key=lambda a: abs(
                int(a.split(":")[0]) / int(a.split(":")[1]) - target))
        path = generate(subject, style=style, palette=self._template_colors,
                        aspect=aspect, extra=extra, model=model, force=force)
        kw.setdefault("fit", "contain")
        kw.setdefault("alt", subject)
        return self.image(x, y, w, h, path, **kw)


# ---------- CLI ----------

def main() -> int:
    p = argparse.ArgumentParser(
        description=t("Generate slide images with AI (results are cached)"))
    p.add_argument("--prompt", required=True, help=t("What to draw (Japanese OK)"))
    p.add_argument("--style", default=DEFAULT_STYLE, choices=sorted(STYLES))
    p.add_argument("--aspect", default="16:9", choices=list(ASPECTS))
    p.add_argument("--template",
                   help=t("Path of the template.json to borrow colors from"))
    p.add_argument("--extra", help=t("Extra instructions"))
    p.add_argument("--model",
                   help=t("Image model (default {model})", model=DEFAULT_MODEL))
    p.add_argument("--out",
                   help=t("Copy destination path (prints the cache path if omitted)"))
    p.add_argument("--force", action="store_true",
                   help=t("Ignore the cache and regenerate"))
    p.add_argument("--show-prompt", action="store_true",
                   help=t("Print the assembled prompt and exit (does not call the API)"))
    args = p.parse_args()

    palette = None
    if args.template:
        with open(args.template) as f:
            palette = json.load(f).get("colors")

    if args.show_prompt:
        print(build_prompt(args.prompt, style=args.style, palette=palette,
                           extra=args.extra))
        return 0

    try:
        path = generate(args.prompt, style=args.style, palette=palette,
                        aspect=args.aspect, extra=args.extra, model=args.model,
                        force=args.force)
    except ImageGenerationError as e:
        print(str(e), file=sys.stderr)
        return 1

    if args.out:
        import shutil
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        shutil.copyfile(path, args.out)
        path = args.out
    with open(path, "rb") as f:
        w, h = image_size(f.read(64 * 1024))
    print(f"{path}  ({w}x{h})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
