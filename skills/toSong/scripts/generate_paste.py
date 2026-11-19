#!/usr/bin/env python3
"""ステップ8用: 曲フォルダから Suno 貼り付け用の suno-paste.md と suno-paste.html を生成する。

表示順（Suno Custom Mode の入力順）:
  1. Lyrics
  2. Style of Music
  3. Title
  (有料プラン設定がある場合: 4. Exclude Styles / 5. Parameters)
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import re
import sys
from pathlib import Path


def read_first_existing(candidates: list[Path]) -> str | None:
    """最初に見つかった非空テキストファイルの内容を返す。"""
    for path in candidates:
        if path.is_file():
            text = path.read_text(encoding="utf-8").strip()
            if text:
                return text
    return None


def extract_from_markdown(md_path: Path) -> dict[str, str]:
    """既存の suno-paste.md から各コードブロックを抽出する（移行用フォールバック）。"""
    if not md_path.is_file():
        return {}
    content = md_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^#{2,3}\s+(.+?)\s*\n+```[^\n]*\n(.*?)\n```",
        re.MULTILINE | re.DOTALL,
    )
    found: dict[str, str] = {}
    for heading, body in pattern.findall(content):
        key = heading.strip().lower()
        val = body.strip()
        if "lyric" in key:
            found["lyrics"] = val
        elif "exclude" in key:
            found["exclude"] = val
        elif "style" in key:
            found["style"] = val
        elif "title" in key:
            found["title"] = val
        elif "param" in key or "setting" in key:
            found["settings"] = val
    return found


def detect_plan(explicit_plan: str, has_paid_files: bool, song_dir: Path | None = None) -> str:
    """利用プラン（free / paid）を判定する。workspace 内の設定を優先し、サンドボックス外エラーを無視する。"""
    if explicit_plan in ("free", "paid"):
        return explicit_plan
    candidates: list[Path] = []
    if song_dir is not None:
        candidates.append(song_dir.parent / "preferences.json")
    candidates.append(Path.cwd() / "songs" / "preferences.json")
    candidates.append(Path.home() / ".config" / "toSong" / "preferences.json")
    for pref_path in candidates:
        try:
            if pref_path.is_file():
                data = json.loads(pref_path.read_text(encoding="utf-8"))
                if data.get("plan") in ("free", "paid"):
                    return str(data["plan"])
        except (OSError, json.JSONDecodeError):
            continue
    return "paid" if has_paid_files else "free"


def build_markdown(
    title: str,
    lyrics: str,
    style: str,
    exclude: str | None = None,
    settings: str | None = None,
    has_cover: bool = False,
) -> str:
    """Suno Custom Mode 順（Lyrics -> Style of Music -> Title）の Markdown を組み立てる。"""
    lines = [
        f"# {title}",
        "",
        "Suno AI（Custom Mode）貼り付け用です。ブラウザで [suno-paste.html](suno-paste.html) を開くとワンクリックでコピーできます。",
        "",
        "## Lyrics",
        "",
        "```text",
        lyrics,
        "```",
        "",
        "## Style of Music",
        "",
        "```text",
        style,
        "```",
        "",
        "## Title",
        "",
        "```text",
        title,
        "```",
    ]

    if exclude or settings:
        lines.extend(["", "---", "", "## 有料プラン（Pro / Premier）追加設定"])
        if exclude:
            lines.extend(["", "### Exclude Styles", "", "```text", exclude, "```"])
        if settings:
            lines.extend(["", "### Parameters", "", "```text", settings, "```"])

    if has_cover:
        lines.extend(["", "## Cover Image", "", "![cover](cover.jpg)"])

    lines.append("")
    return "\n".join(lines)


def render_card(card_id: str, step: int, label: str, hint: str, body: str) -> str:
    """HTML カード 1 枚分を生成する。"""
    escaped = html.escape(body)
    char_count = len(body)
    return f"""    <section class="card" id="card-{card_id}">
      <div class="card-header">
        <div class="card-title-group">
          <span class="step-badge">{step}</span>
          <h2>{html.escape(label)}</h2>
          <span class="meta">{html.escape(hint)} · {char_count} 文字</span>
        </div>
        <button type="button" class="copy-btn" data-target="content-{card_id}" data-card="card-{card_id}">
          コピー
        </button>
      </div>
      <pre class="code-box" id="content-{card_id}">{escaped}</pre>
    </section>"""


def load_cover_data_url(song_dir: Path) -> str | None:
    """曲フォルダ直下のカバー画像（cover.jpg / png / webp）を Data URL として読み込む。"""
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
    for name in ("cover.jpg", "cover.jpeg", "cover.png", "cover.webp"):
        path = song_dir / name
        if path.is_file():
            mime = mime_map[path.suffix.lower()]
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            return f"data:{mime};base64,{encoded}"
    return None


def render_cover_card(step: int, cover_data_url: str) -> str:
    """カバー画像用の HTML カードを生成する。"""
    return f"""    <section class="card" id="card-cover">
      <div class="card-header">
        <div class="card-title-group">
          <span class="step-badge">{step}</span>
          <h2>Cover Image</h2>
          <span class="meta">カバー画像（PNG形式でコピー）</span>
        </div>
        <button type="button" class="copy-btn copy-img-btn" data-card="card-cover">
          画像をコピー
        </button>
      </div>
      <div class="cover-box">
        <img id="cover-preview" class="cover-preview" src="{cover_data_url}" alt="カバー画像">
      </div>
      <p class="hint-msg" id="cover-msg"></p>
    </section>"""


def build_html(
    title: str,
    lyrics: str,
    style: str,
    exclude: str | None = None,
    settings: str | None = None,
    cover_data_url: str | None = None,
) -> str:
    """コピーボタン付きの単一 HTML ファイルを組み立てる。"""
    cards = [
        render_card("lyrics", 1, "Lyrics", "歌詞", lyrics),
        render_card("style", 2, "Style of Music", "Styles", style),
        render_card("title", 3, "Title", "タイトル", title),
    ]
    if exclude:
        cards.append(render_card("exclude", len(cards) + 1, "Exclude Styles", "除外スタイル", exclude))
    if settings:
        cards.append(render_card("settings", len(cards) + 1, "Parameters", "詳細パラメータ", settings))
    if cover_data_url:
        cards.append(render_cover_card(len(cards) + 1, cover_data_url))

    cards_html = "\n\n".join(cards)
    escaped_title = html.escape(title)

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escaped_title} - Suno 貼り付け用</title>
  <style>
    :root {{
      --bg: #0f1115;
      --surface: #181b22;
      --surface-2: #111318;
      --border: #2a2f3a;
      --text: #e8ecf2;
      --muted: #9aa3b2;
      --accent: #3b82f6;
      --accent-hover: #2563eb;
      --done: #16a34a;
      --done-bg: rgba(22, 163, 74, 0.12);
    }}
    @media (prefers-color-scheme: light) {{
      :root {{
        --bg: #f6f7f9;
        --surface: #ffffff;
        --surface-2: #f1f3f6;
        --border: #dde2ea;
        --text: #161922;
        --muted: #5c6575;
        --accent: #2563eb;
        --accent-hover: #1d4ed8;
        --done: #15803d;
        --done-bg: rgba(21, 128, 61, 0.08);
      }}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 24px 16px 48px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Sans", "Yu Gothic UI", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    .container {{
      max-width: 780px;
      margin: 0 auto;
    }}
    header {{
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 20px;
    }}
    .cover {{
      width: 60px;
      height: 60px;
      border-radius: 10px;
      object-fit: cover;
      border: 1px solid var(--border);
      flex-shrink: 0;
    }}
    header h1 {{
      margin: 0 0 2px;
      font-size: 1.35rem;
      line-height: 1.3;
    }}
    header p {{
      margin: 0;
      font-size: 0.85rem;
      color: var(--muted);
    }}
    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px 16px;
      margin-bottom: 14px;
      transition: border-color 0.2s, background-color 0.2s;
    }}
    .card.copied {{
      border-color: var(--done);
      background: linear-gradient(0deg, var(--done-bg), var(--done-bg)), var(--surface);
    }}
    .card-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 10px;
    }}
    .card-title-group {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .step-badge {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 24px;
      height: 24px;
      border-radius: 999px;
      background: var(--surface-2);
      border: 1px solid var(--border);
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--muted);
    }}
    .card-header h2 {{
      margin: 0;
      font-size: 1rem;
    }}
    .meta {{
      font-size: 0.78rem;
      color: var(--muted);
    }}
    .copy-btn {{
      appearance: none;
      border: 0;
      border-radius: 8px;
      padding: 8px 18px;
      font-size: 0.88rem;
      font-weight: 600;
      color: #fff;
      background: var(--accent);
      cursor: pointer;
      flex-shrink: 0;
      transition: background-color 0.15s, transform 0.05s;
    }}
    .copy-btn:hover {{ background: var(--accent-hover); }}
    .copy-btn:active {{ transform: translateY(1px); }}
    .copy-btn.done {{ background: var(--done); }}
    .code-box {{
      margin: 0;
      padding: 12px 14px;
      background: var(--surface-2);
      border: 1px solid var(--border);
      border-radius: 8px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 0.88rem;
      line-height: 1.55;
      white-space: pre-wrap;
      word-break: break-word;
      max-height: 360px;
      overflow-y: auto;
    }}
    .cover-box {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .cover-preview {{
      width: 180px;
      height: 180px;
      border-radius: 10px;
      object-fit: cover;
      border: 1px solid var(--border);
    }}
    .hint-msg {{
      margin: 8px 0 0;
      font-size: 0.82rem;
      color: var(--muted);
    }}
    .hint-msg:empty {{ display: none; }}
  </style>
</head>
<body>
  <main class="container">
    <header>
      <img class="cover" src="cover.jpg" alt="" onerror="this.style.display='none'">
      <div>
        <h1>{escaped_title}</h1>
        <p>Suno Custom Mode の上から順に並べています（Lyrics → Styles → Title）</p>
      </div>
    </header>

{cards_html}
  </main>

  <script>
    async function copyText(text) {{
      if (navigator.clipboard && window.isSecureContext) {{
        try {{
          await navigator.clipboard.writeText(text);
          return true;
        }} catch (_) {{}}
      }}
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      let ok = false;
      try {{
        ok = document.execCommand("copy");
      }} catch (_) {{
        ok = false;
      }}
      document.body.removeChild(ta);
      return ok;
    }}

    document.querySelectorAll(".copy-btn[data-target]").forEach((btn) => {{
      btn.addEventListener("click", async () => {{
        const target = document.getElementById(btn.dataset.target);
        const card = document.getElementById(btn.dataset.card);
        if (!target) return;
        const ok = await copyText(target.textContent);
        if (!ok) {{
          btn.textContent = "コピー失敗";
          return;
        }}
        btn.textContent = "コピー済み ✓";
        btn.classList.add("done");
        if (card) card.classList.add("copied");
      }});
    }});

    async function imageToPngBlob(img) {{
      if (!img.complete) {{
        await new Promise((resolve, reject) => {{
          img.onload = resolve;
          img.onerror = reject;
        }});
      }}
      const canvas = document.createElement("canvas");
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0);
      return await new Promise((resolve, reject) => {{
        canvas.toBlob((blob) => (blob ? resolve(blob) : reject(new Error("toBlob failed"))), "image/png");
      }});
    }}

    document.querySelectorAll(".copy-img-btn").forEach((btn) => {{
      btn.addEventListener("click", async () => {{
        const img = document.getElementById("cover-preview");
        const card = document.getElementById(btn.dataset.card);
        const msg = document.getElementById("cover-msg");
        if (!img) return;
        try {{
          if (!navigator.clipboard || typeof ClipboardItem === "undefined") {{
            throw new Error("ClipboardItem unsupported");
          }}
          const pngBlob = await imageToPngBlob(img);
          await navigator.clipboard.write([new ClipboardItem({{ "image/png": pngBlob }})]);
          btn.textContent = "コピー済み ✓";
          btn.classList.add("done");
          if (card) card.classList.add("copied");
          if (msg) msg.textContent = "";
        }} catch (_) {{
          btn.textContent = "コピー失敗";
          if (msg) msg.textContent = "この環境ではボタンからの画像コピーに非対応です。画像を右クリックして「画像をコピー」してください。";
        }}
      }});
    }});
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate suno-paste.md and suno-paste.html in a song folder."
    )
    parser.add_argument("song_dir", help="曲フォルダのパス")
    parser.add_argument(
        "--plan",
        choices=["auto", "free", "paid"],
        default="auto",
        help="Suno のプラン（既定: auto）",
    )
    args = parser.parse_args()

    song_dir = Path(args.song_dir).expanduser().resolve()
    if not song_dir.is_dir():
        print(f"Error: directory not found: {song_dir}", file=sys.stderr)
        return 1

    work_dir = song_dir / "work"
    md_fallback = extract_from_markdown(song_dir / "suno-paste.md")

    lyrics = read_first_existing([work_dir / "lyrics.txt", song_dir / "lyrics.txt"]) or md_fallback.get("lyrics")
    style = read_first_existing([work_dir / "style.txt", song_dir / "style.txt"]) or md_fallback.get("style")
    title = (
        read_first_existing([work_dir / "title.txt", song_dir / "title.txt"])
        or md_fallback.get("title")
        or song_dir.name
    )

    if not lyrics or not style:
        print(
            "Error: lyrics.txt or style.txt (or suno-paste.md fallback) not found.",
            file=sys.stderr,
        )
        return 1

    exclude = read_first_existing([work_dir / "exclude.txt", song_dir / "exclude.txt"]) or md_fallback.get("exclude")
    settings = read_first_existing([work_dir / "settings.txt", song_dir / "settings.txt"]) or md_fallback.get("settings")

    plan = detect_plan(args.plan, bool(exclude or settings), song_dir=song_dir)
    if plan == "free":
        exclude = None
        settings = None

    cover_data_url = load_cover_data_url(song_dir)

    md_path = song_dir / "suno-paste.md"
    html_path = song_dir / "suno-paste.html"

    md_path.write_text(
        build_markdown(title, lyrics, style, exclude, settings, has_cover=bool(cover_data_url)),
        encoding="utf-8",
    )
    html_path.write_text(
        build_html(title, lyrics, style, exclude, settings, cover_data_url=cover_data_url),
        encoding="utf-8",
    )

    print(f"Generated: {md_path}")
    print(f"Generated: {html_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
