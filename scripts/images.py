#!/usr/bin/env python3
"""Functionality for placing "images" — photos, illustrations, etc. — onto slides.

This skill has 3 ways to produce a diagram. Choose based on the purpose.

| What you want to do | What to use |
|---|---|
| Show structure precisely (flow / architecture diagram / graph) | `diagrams.Canvas` |
| Show a concept visually (metaphor diagram / icon / pictogram) | `illustrations` (drawn with shapes; works offline) |
| Show mood / a scene (cover, section divider, illustration) | this module (AI-generated or your own image) |

--- 1. Generate with AI -------------------------------------------------------

    from images import generate
    path = generate("複数のマイクロサービスがひとつの台帳を共有している様子",
                    style="flat_vector", palette=template["colors"], aspect="16:9")

Generated results are cached by a hash of the content (the same prompt,
style, and aspect ratio won't be regenerated). The prompt is kept in a
sidecar .json file, so it can be traced later.

    # From the command line
    .venv/bin/python scripts/images.py --prompt "…" --style flat_vector --out out/x.png

Requires `GEMINI_API_KEY`. The image model sometimes has zero free-tier
quota, in which case it returns 429 (a key from a project with billing
enabled is required). Generation can also be switched off entirely in
`config/settings.json` (`imageGeneration: off`, see `scripts/settings.py`),
in which case `generate()` refuses before touching the cache or the API.

--- 2. Place your own image --------------------------------------------------

Used via Canvas. Accepts a local path / http(s) URL / Drive file URL or ID.

    d = Canvas(deck, slide_id, template)
    d.image(0.6, 1.1, 4.2, 2.6, "assets/screenshot.png", fit="contain")
    d.ai_image(5.2, 1.1, 4.2, 2.6, "自律型エージェントが夜間にビルドを回している様子")

Local files are uploaded temporarily to Drive, set to "anyone with the link
can view," and that URL is passed to `createImage`. Since Slides **copies
the image into the presentation** on insertion, the temporary file is
deleted right after `deck.commit()` (`AssetStore.cleanup()`, called
automatically from `TemplateDeck.commit()`).

Slides only accepts PNG / JPEG / GIF, under 50MB, under 25 megapixels.
"""
from __future__ import annotations

import argparse
import atexit
import hashlib
import json
import mimetypes
import os
import struct
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import Future, ThreadPoolExecutor  # noqa: F401

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _auth  # noqa: E402
import settings  # noqa: E402
from _i18n import t, register  # noqa: E402
from colors import Palette  # noqa: E402

register({
    "image {name}": "画像 {name}",
    "{total} temporary uploads found, {public} still shared with anyone who has the link":
        "一時アップロードが {total} 件、うち {public} 件がリンクを知る全員に公開されたままです",
    "  … and {n} more": "  … ほか {n} 件",
    "Re-run with --yes to un-share them and move them to the trash":
        "--yes を付けて再実行すると、共有を外してゴミ箱へ移動します",
    "Moved {n} temporary uploads to the trash":
        "一時アップロード {n} 件をゴミ箱へ移動しました",
    "  cleaning up {n} temporary uploads left by an interrupted run":
        "  中断した実行が残した一時アップロード {n} 件を片付けます",
    "  note: generating at {aspect} for a {target} frame; "
    "composed so the crop does not cut the subject":
        "  note: {target} の枠に対して {aspect} で生成します"
        "（切り取りで主題が欠けない構図を指示済み）",
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

# Values accepted by imageConfig.aspectRatio
ASPECTS = ("1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9")

# Only the 10 aspect ratios in ASPECTS can be generated, so they usually
# don't match the template's image frame ratio exactly. The difference is
# absorbed by cropping with cover, but if the subject sits near the edge
# that gets cropped, the picture is ruined. When the mismatch exceeds this
# tolerance, the model is instructed to compose with the crop in mind
FRAME_TOLERANCE = 0.02


def frame_note(target: float, aspect: str) -> str | None:
    """Turns the mismatch between the frame's ratio and the generated ratio
    into a composition instruction that survives cropping.

    target is the destination frame's aspect ratio (width / height). Returns
    None if the mismatch is small.
    """
    aw, ah = (int(v) for v in aspect.split(":"))
    made = aw / ah
    if abs(made - target) <= target * FRAME_TOLERANCE:
        return None
    if made > target:
        edges, cut = "left and right edges", 1 - target / made
    else:
        edges, cut = "top and bottom edges", 1 - made / target
    return (
        f"This illustration will be placed in a frame of ratio {target:.2f}:1 and "
        f"cropped from the centre to fill it, so roughly {round(cut * 100)}% of the "
        f"{edges} will be cut away. Compose for that frame: keep the subject and "
        "every detail that matters well inside the centre, and leave the outer "
        "edges free of anything that must survive."
    )

# Formats accepted by Slides' createImage
SLIDES_MIME = {"image/png", "image/jpeg", "image/gif"}


# ---------- Style ----------

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

# Constraints that always apply regardless of style. Instructions assuming the image will be placed on a slide.
GUARDRAILS = (
    "Do not render any text, letters, numbers, words, labels, watermarks, logos or UI copy "
    "anywhere in the image. Composition centered with clear margins. "
    "Plain white background unless the subject requires otherwise. "
    "Single coherent illustration, not a grid or collage of variations."
)


def palette_hint(colors: dict | None) -> str:
    """Turns the template's palette into an instruction to include in the generation prompt."""
    if not colors:
        return ""
    p = Palette(colors)
    return (
        f"Strictly limit the palette to these colors and tints of them: "
        f"primary {p.primary}, accent {p.info}, positive {p.success}, "
        f"neutral dark {p.text}, neutral light {p.surfaceAlt}."
    )


def build_prompt(subject: str, *, style: str = DEFAULT_STYLE,
                 palette: dict | None = None, extra: str | None = None,
                 frame: str | None = None) -> str:
    """Assembles the full prompt actually sent to the API, from a
    description of the subject.

    frame is the composition instruction produced by frame_note(). It's a
    more specific condition than GUARDRAILS' "centered / margins," so it's
    placed later to override it.
    """
    if style not in STYLES:
        raise ValueError(
            t("Unknown style '{style}'. Available: {styles}",
              style=style, styles=sorted(STYLES))
        )
    parts = [STYLES[style], subject.strip(), palette_hint(palette), GUARDRAILS, frame]
    if extra:
        parts.insert(2, extra.strip())
    return "\n".join(p for p in parts if p)


# ---------- Generation ----------

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
    """Calls the image model and returns (byte string, mimeType)."""
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
    else:  # pragma: no cover - unreachable (always exits via break or raise)
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
             force: bool = False, frame: str | None = None) -> str:
    """Generates an image and returns its local path. Reuses the cache for
    identical input.

    The cache key is a hash of (model, style, aspect, full prompt text).
    This means recreating the deck produces the same picture, giving
    reproducibility. Since frame is part of the full prompt text, a
    different frame triggers regeneration.
    """
    if not settings.image_generation_enabled():
        # Checked before the cache lookup on purpose: the switch is about
        # whether AI imagery appears at all, not only about spending quota.
        raise ImageGenerationError(settings.image_generation_off_message())
    if aspect not in ASPECTS:
        raise ValueError(t("aspect must be one of {aspects} (got: {aspect})",
                           aspects=ASPECTS, aspect=aspect))
    model = model or os.environ.get("GSLIDES_IMAGE_MODEL", DEFAULT_MODEL)
    prompt = build_prompt(subject, style=style, palette=palette, extra=extra,
                          frame=frame)

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
    # If a PNG corrupted by an interrupted run were left in the cache, the
    # exists() check would keep reusing it forever, so write to a temp file
    # first and place it atomically with os.replace (same approach as icons.py)
    tmp = f"{path}.{os.getpid()}.part"
    with open(tmp, "wb") as f:
        f.write(blob)
    os.replace(tmp, path)
    with open(path + ".json", "w") as f:
        json.dump({"model": model, "style": style, "aspect": aspect,
                   "subject": subject, "prompt": prompt, "mime": mime},
                  f, ensure_ascii=False, indent=2)
    return path


# ---------- Actual image dimensions ----------

def image_size(data: bytes) -> tuple[int, int]:
    """Returns (width, height) in pixels from a PNG / JPEG / GIF header.

    Needed for aspect-ratio-preserving placement. Reads only the header
    since we don't want to add a Pillow dependency.
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
            # Dimensions are in SOF0..SOF15 (excluding DHT=C4 / JPG=C8 / DAC=CC)
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            i += 2 + seg
    raise ValueError(t("Cannot read image dimensions (only PNG / JPEG / GIF "
                       "are supported)"))


def _remote_image_size(url: str, limit: int = 64 * 1024) -> tuple[int, int]:
    """Fetches only the beginning of a remote image and returns
    (width, height) in pixels.

    Actual dimensions are needed for fit="cover" / "contain" calculations.
    Instead of downloading the whole file, only enough to read the header is
    fetched. Raises ValueError if it can't be read.
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


# ---------- Resolve to a URL Slides can reference ----------

def _check_local(source: str) -> str:
    """Checks a local image's existence, format, and size, and returns the
    expanded path.

    Only network-free checks go here, so that even with asynchronous
    uploads, "wrong format" or "file not found" is still surfaced
    immediately at the call site.
    """
    path = os.path.expanduser(source)
    if not os.path.exists(path):
        raise FileNotFoundError(t("Image not found: {source}", source=source))
    with open(path, "rb") as f:
        head = f.read(64 * 1024)
    mime = sniff_mime(path, head)
    if mime not in SLIDES_MIME:
        raise ValueError(
            t("Slides cannot handle this format: {mime} ({file}). "
              "Convert it to PNG / JPEG / GIF",
              mime=mime, file=os.path.basename(path))
        )
    if os.path.getsize(path) > 49 * 1024 * 1024:
        raise ValueError(t("Image too large ({size:.1f}MB / 50MB limit)",
                           size=os.path.getsize(path) / 1e6))
    return path


class AssetStore:
    """Resolves an image source into a URL that can be passed to
    `createImage`.

    - http(s) URL ... used as-is
    - Drive URL / `drive:<id>` ... shared and turned into a direct link
    - local path ... uploaded temporarily to Drive, shared, and turned into
      a direct link

    Temporarily uploaded files are removed by `cleanup()`. Since Slides
    copies the image into the presentation at insertion time, deleting it
    afterward doesn't break the display.
    """

    # Uploading to Drive measures at about 3.1 seconds per image (1.9s
    # upload + 1.2s sharing setup). Doing this synchronously one image at a
    # time during rendering would burn 30+ seconds on images alone for a
    # 10-image deck (more than the entire batchUpdate). Since a local
    # image's URL doesn't need to be finalized the moment its placement is
    # decided, uploads are dispatched to a separate thread and the URL is
    # filled in right before commit() (flush()). Concurrency is kept modest
    # out of consideration for Drive's write quota.
    WORKERS = 6

    def __init__(self, drive=None):
        self._drive = drive
        self.temp_ids: list[str] = []
        self.shared_ids: list[str] = []
        self._resolved: dict[str, str] = {}
        self._lock = threading.Lock()
        self._tls = threading.local()
        self._pool: ThreadPoolExecutor | None = None
        # source -> Future[url]. Uploads only once even if the same image is placed multiple times
        self._futures: dict[str, "Future[str]"] = {}
        # Where to patch back into: (createImage's props, source)
        self._patch: list[tuple[dict, str]] = []
        # Images are uploaded one by one as diagrams are drawn, each becoming
        # "anyone with the link can view" as it goes. Since cleanup() is only
        # called from commit(), a run that fails partway through leaves
        # temporary files publicly shared. Register the cleanup here so it's
        # guaranteed to happen at process end
        atexit.register(self._atexit_cleanup)

    # -- Parallel upload --

    def _executor(self) -> ThreadPoolExecutor:
        if self._pool is None:
            self._pool = ThreadPoolExecutor(max_workers=self.WORKERS,
                                            thread_name_prefix="asset")
        return self._pool

    def defer(self, source: str, props: dict) -> None:
        """Schedules the upload of a local image.

        `props` is the body of createImage. flush() fills in props["url"]
        after the upload finishes. Broken input (unsupported format,
        oversized, wrong path) is rejected synchronously **right here**.
        Only the network part is deferred — otherwise it becomes impossible
        to tell which image() call an error came from.
        """
        path = _check_local(source)      # format/size check (fully local)
        with self._lock:
            if source not in self._futures:
                mime = sniff_mime(path)
                self._futures[source] = self._executor().submit(
                    lambda: self._drive_url(self._upload(path, mime)))
            self._patch.append((props, source))

    def flush(self) -> int:
        """Waits for scheduled uploads to finish and fills in createImage's
        url.

        Must always be called before commit() sends the batchUpdate. Returns
        the number of images resolved.
        """
        if not self._patch:
            return 0
        for props, source in self._patch:
            props["url"] = self._futures[source].result()   # failures propagate here
        n = len(self._patch)
        self._patch = []
        return n

    def _atexit_cleanup(self) -> None:
        """Safety net for process exit. Does nothing if cleanup() already ran.

        temp_ids can be empty while uploads are still in flight. Without
        also checking _futures, files "about to land in temp_ids" would be
        missed and left publicly shared.
        """
        if not self.temp_ids and not self.shared_ids and not self._futures:
            return
        print(t("  cleaning up {n} temporary uploads left by an interrupted run",
                n=len(self.temp_ids) + len(self.shared_ids) or len(self._futures)),
              file=sys.stderr)
        try:
            self.cleanup()
        except Exception:  # avoid raising a new exception during exit handling
            pass

    @property
    def drive(self):
        if self._drive is None:
            self._drive = _auth.services()[1]
        return self._drive

    # -- Resolution --

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

        path = _check_local(source)
        return self._drive_url(self._upload(path, sniff_mime(path)))

    def _upload(self, path: str, mime: str) -> str:
        from googleapiclient.http import MediaFileUpload
        media = MediaFileUpload(path, mimetype=mime, resumable=False)
        meta = {"name": f"gslides-tmp-{os.path.basename(path)}"}
        # The drive property shares a service object that isn't thread-safe,
        # so create one per worker (httplib2 connections can't be reused)
        fid = self._thread_drive().files().create(
            body=meta, media_body=media, fields="id", supportsAllDrives=True,
        ).execute()["id"]
        with self._lock:
            self.temp_ids.append(fid)
        return fid

    def _thread_drive(self):
        """Per-calling-thread Drive service."""
        if threading.current_thread() is threading.main_thread():
            return self.drive
        if not hasattr(self._tls, "drive"):
            self._tls.drive = _auth.services()[1]
        return self._tls.drive

    def _drive_url(self, file_id: str) -> str:
        """Makes a Drive file "anyone with the link can view" and returns a
        direct link.

        `createImage` fetches the URL **anonymously**, so it's not enough
        for just the authenticated caller to have access. Sharing is
        revoked by cleanup() after insertion.
        """
        try:
            self._thread_drive().permissions().create(
                fileId=file_id, body={"type": "anyone", "role": "reader"},
                fields="id",
            ).execute()
            with self._lock:
                self.shared_ids.append(file_id)
        except Exception as e:  # already public, or forbidden by org policy
            print(t("  warn: could not change the sharing settings of {file_id}: "
                    "{error}", file_id=file_id, error=e), file=sys.stderr)
        return f"https://drive.google.com/uc?export=download&id={file_id}"

    # -- Cleanup --

    def cleanup(self) -> None:
        """Deletes temporary uploads and removes public sharing set on
        existing files.

        Each one measures at 0.85 seconds (unsharing takes an additional 2
        round-trips: list + delete), so this runs in parallel. Since this is
        cleanup, a single failure doesn't stop the whole process — it warns
        and moves on.
        """
        # Uploads scheduled but never collected wouldn't be in temp_ids and
        # would be left behind. Exceptions are swallowed (avoid adding new
        # failures during cleanup)
        for fut in self._futures.values():
            try:
                fut.result()
            except Exception:  # noqa: BLE001
                pass
        self._futures = {}
        self._patch = []

        def drop(fid):
            try:
                self._thread_drive().files().delete(
                    fileId=fid, supportsAllDrives=True).execute()
            except Exception as e:  # noqa: BLE001
                print(t("  warn: could not delete the temporary image {file_id}: "
                        "{error}", file_id=fid, error=e), file=sys.stderr)

        def unshare(fid):
            try:
                drive = self._thread_drive()
                perms = drive.permissions().list(
                    fileId=fid, fields="permissions(id,type)").execute()
                for p in perms.get("permissions", []):
                    if p.get("type") == "anyone":
                        drive.permissions().delete(
                            fileId=fid, permissionId=p["id"]).execute()
            except Exception as e:  # noqa: BLE001
                print(t("  warn: failed to remove public sharing from {file_id}: "
                        "{error}", file_id=fid, error=e), file=sys.stderr)

        temp = set(self.temp_ids)
        # Files being deleted outright are excluded from unsharing (deleting them removes the sharing too)
        keep = [fid for fid in self.shared_ids if fid not in temp]
        jobs = [(drop, fid) for fid in self.temp_ids] + [(unshare, fid) for fid in keep]
        if jobs:
            try:
                with ThreadPoolExecutor(
                        max_workers=min(self.WORKERS, len(jobs))) as ex:
                    list(ex.map(lambda job: job[0](job[1]), jobs))
            except RuntimeError:
                # Threads can't be started while the interpreter is
                # shutting down (via atexit). Since this is the last line of
                # defense for "always delete files left publicly shared,"
                # fall back to doing it sequentially, slow but guaranteed
                for fn, fid in jobs:
                    fn(fid)

        self.temp_ids = []
        self.shared_ids = []
        self._resolved = {}
        if self._pool is not None:
            self._pool.shutdown(wait=False)
            self._pool = None


def _drive_file_id(url: str) -> str:
    import re
    m = re.search(r"/file/d/([a-zA-Z0-9_-]{10,})", url) or \
        re.search(r"[?&]id=([a-zA-Z0-9_-]{10,})", url) or \
        re.search(r"/d/([a-zA-Z0-9_-]{10,})", url)
    if not m:
        raise ValueError(t("Cannot extract the Drive file ID: {url}", url=url))
    return m.group(1)


# ---------- Methods added to Canvas ----------

class ImageMixin:
    """Mixin that adds image placement to `Canvas`. Inherited by diagrams.Canvas."""

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
        """Returns the rect and crop needed to fit a px_w×px_h image into an (x, y, w, h) frame."""
        x, y, w, h = box
        if not px_w or not px_h or mode == "stretch":
            return (x, y, w, h), None
        ar_img = px_w / px_h
        ar_box = w / h
        if mode == "cover":
            # Fills the frame completely and crops away the overflow (crop is a left/right or top/bottom ratio)
            if ar_img > ar_box:
                cut = (1 - ar_box / ar_img) / 2
                return (x, y, w, h), {"leftOffset": cut, "rightOffset": cut}
            cut = (1 - ar_img / ar_box) / 2
            return (x, y, w, h), {"topOffset": cut, "bottomOffset": cut}
        # contain: keeps the aspect ratio, fits inside the frame, and centers it
        if ar_img > ar_box:
            nw, nh = w, w / ar_img
        else:
            nh, nw = h, h * ar_img
        return (x + (w - nw) / 2, y + (h - nh) / 2, nw, nh), None

    def image(self, x, y, w, h, source, *, fit="contain", caption=None,
              caption_size=9, caption_color=None, caption_at="image",
              outline=None, outline_weight=1.0, rounded=False, alt=None) -> str:
        """Places an image and returns its objectId.

        source is a local path / http(s) URL / Drive URL, or `drive:<id>`.

        fit:
          - "contain" ... keeps the aspect ratio and fits inside the frame
            (default). Leaves margins
          - "cover"   ... fills the frame, cropping away the overflow
          - "stretch" ... stretches to fit the frame (aspect ratio distorted)

        If caption is passed, a caption is placed below. `caption_at`:

          - "image" ... attached at the image's actual bottom edge
            (default). Use this when placing a single image
          - "box"   ... attached at the frame's bottom edge. Prevents
            caption heights from varying when placing multiple images side
            by side with different fit values

        Returns the image's objectId.
        """
        if fit not in ("contain", "cover", "stretch"):
            raise ValueError(t("fit must be one of contain / cover / stretch: {fit}",
                               fit=fit))
        if getattr(self.deck, "dry", False):
            # --dry-run: don't fetch the real thing. Uploading here would
            # add another publicly shared temp file to Drive on every check
            # (same approach as icons / cloud_icons / charts)
            oid = self.shape(x, y, w, h, kind="RECTANGLE",
                             fill=self.P.border, stroke=None)
            if caption:
                self.label(x, y + h + 0.05, w, 0.26, caption, size=caption_size,
                           align="CENTER", valign="TOP",
                           color=caption_color or self.P.muted)
            return oid
        store = self._asset_store()
        px = (0, 0)
        local = os.path.expanduser(source)
        is_local = os.path.exists(local)
        url = None
        if is_local:
            # Local images have their actual dimensions readable right away,
            # so there's no need to wait for the URL to resolve. The upload
            # runs in the background, and flush() right before commit fills
            # in the url
            with open(local, "rb") as f:
                try:
                    px = image_size(f.read(64 * 1024))
                except ValueError:
                    px = (0, 0)
        else:
            # For a remote image, the URL itself is needed to read its
            # actual size (and Drive additionally requires the sharing
            # setup first), so this is resolved synchronously
            url = store.url_for(source)
            # For remote images (http / Drive) too, only the beginning is
            # fetched to read the actual size. Proceeding with cover without
            # actual dimensions would make the later absolute transform
            # effectively a stretch, distorting the aspect ratio, so if it
            # can't be read, fall back to contain (aspect preserved) with a
            # warning
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
        props = {"objectId": oid, "url": url,
                 "elementProperties": self._elem_props(*rect)}
        self.deck.requests.append({"createImage": props})
        if is_local:
            # url stays None. flush() right before commit() fills it in
            store.defer(source, props)
        if fit != "contain":
            # createImage preserves the original aspect ratio regardless of
            # the specified size (i.e. it's always shrunk to a contain-like
            # fit). To fill the frame, the transform has to be overridden
            # after creation. Have commit()'s post-processing pick this up
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
            # Slides has no rounded-corner mask. Make explicit that an
            # outline is used as a substitute
            print(t("  note: the Slides API cannot round image corners "
                    "(rounded is ignored)"), file=sys.stderr)

        self._seq += 1
        self.rects[oid] = (*rect, "IMAGE")
        # Images are opaque and cover any text placed earlier, so record
        # them as solids
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
        """Generates an image with AI and places it. The remaining
        arguments match image().

        If aspect is omitted, the ratio closest to the frame's aspect ratio
        is chosen. Since only 10 ratios can be generated, it won't match the
        frame exactly, and the remaining difference is filled in by cover's
        cropping. The model is instructed to compose with the crop in mind,
        so the subject isn't cut off even after fitting to the frame.
        Results are cached, so recreating the deck with the same subject
        produces the same picture.

        If aspect is given explicitly, it's treated as the caller's
        responsibility to make sure it matches the frame, and no composition
        instruction is added.
        """
        frame = None
        if aspect is None:
            target = w / h
            aspect = min(ASPECTS, key=lambda a: abs(
                int(a.split(":")[0]) / int(a.split(":")[1]) - target))
            frame = frame_note(target, aspect)
            if frame:
                print(t("  note: generating at {aspect} for a {target} frame; "
                        "composed so the crop does not cut the subject",
                        aspect=aspect, target=f"{target:.2f}:1"), file=sys.stderr)
        path = generate(subject, style=style, palette=self._template_colors,
                        aspect=aspect, extra=extra, model=model, force=force,
                        frame=frame)
        # Fill the frame. Since the generated ratio never matches the frame
        # exactly, contain would leave margins that expose the template's
        # background
        kw.setdefault("fit", "cover")
        kw.setdefault("alt", subject)
        return self.image(x, y, w, h, path, **kw)


def sweep_temp(delete: bool = False) -> int:
    """Cleans up temporary uploads left in Drive by an interrupted run.

    Only targets files whose name starts with `gslides-tmp-` and that the
    caller owns. Since the problem is public sharing being left on, sharing
    is removed first, then the file is sent to the trash (not permanently
    deleted — even a mistaken target can be restored for 30 days).

    Drive's `name contains` is a word-prefix match, so unrelated files that
    start with a word other than `gslides-tmp-` can also match (a similarly
    loose prefix-match query once deleted real files in the past). Don't
    trust the API's result — always confirm a strict prefix match
    client-side before selecting anything for deletion.
    """
    drive = _auth.services()[1]
    found, token = [], None
    while True:
        res = drive.files().list(
            q="name contains 'gslides-tmp-' and trashed = false",
            fields="nextPageToken, files(id,name,createdTime,ownedByMe)",
            pageSize=200, pageToken=token,
            supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
        found += [f for f in res.get("files", [])
                  if f.get("ownedByMe")
                  and f.get("name", "").startswith("gslides-tmp-")]
        token = res.get("nextPageToken")
        if not token:
            break
    # Each one takes 2 round-trips, so check in parallel. Can accumulate into the hundreds
    tls = threading.local()

    def _drive():
        if not hasattr(tls, "svc"):
            tls.svc = _auth.services()[1]
        return tls.svc

    def probe(f):
        try:
            perms = _drive().permissions().list(
                fileId=f["id"], fields="permissions(id,type)",
                supportsAllDrives=True).execute().get("permissions", [])
        except Exception:  # noqa: BLE001
            # Can be deleted between listing and checking (e.g. when running
            # alongside another cleanup). Since the goal is cleanup, nothing
            # needs to be done if it's already gone
            f["anyone"] = []
            return True          # already gone
        f["anyone"] = [p["id"] for p in perms if p.get("type") == "anyone"]
        return False

    if found:
        with ThreadPoolExecutor(max_workers=min(8, len(found))) as ex:
            list(ex.map(probe, found))
    public = [f for f in found if f["anyone"]]
    print(t("{total} temporary uploads found, {public} still shared with anyone "
            "who has the link", total=len(found), public=len(public)))
    if not found:
        return 0
    if not delete:
        for f in found[:10]:
            print(f"  {f['createdTime'][:10]}  {f['name'][:52]}")
        if len(found) > 10:
            print(t("  … and {n} more", n=len(found) - 10))
        print(t("Re-run with --yes to un-share them and move them to the trash"))
        return 0
    def purge(f):
        svc = _drive()
        # list()'s query is a word-prefix match, so do a final confirmation
        # here that the name is actually safe to delete
        if not f.get("name", "").startswith("gslides-tmp-"):
            return
        for pid in f["anyone"]:
            try:
                svc.permissions().delete(fileId=f["id"], permissionId=pid,
                                         supportsAllDrives=True).execute()
            except Exception as e:  # noqa: BLE001
                print(t("  warn: failed to remove public sharing from {file_id}: "
                        "{error}", file_id=f["id"], error=e), file=sys.stderr)
        try:
            svc.files().update(fileId=f["id"], body={"trashed": True},
                               supportsAllDrives=True).execute()
        except Exception as e:  # noqa: BLE001
            print(t("  warn: could not delete the temporary image {file_id}: "
                    "{error}", file_id=f["id"], error=e), file=sys.stderr)

    with ThreadPoolExecutor(max_workers=min(8, len(found))) as ex:
        list(ex.map(purge, found))
    print(t("Moved {n} temporary uploads to the trash", n=len(found)))
    return 0


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
    p.add_argument("--sweep-temp", action="store_true",
                   help=t("Find temporary uploads left in Drive by interrupted "
                          "runs, un-share and delete them"))
    p.add_argument("--yes", action="store_true",
                   help=t("with --sweep-temp, delete without asking"))
    args = p.parse_args()

    if args.sweep_temp:
        return sweep_temp(delete=args.yes)

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
