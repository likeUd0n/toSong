"""VOICEVOX Engine API を使い、歌詞の音韻・モーラ診断と仮読み上げ WAV を生成する。"""
from __future__ import annotations

import argparse
import io
import re
import statistics
import sys
import wave
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import requests

DEFAULT_URL = "http://127.0.0.1:50021"
DEFAULT_SPEAKER = 2  # 四国めたん（ノーマル）

SECTION_RE = re.compile(
    r"^\[(Intro|Verse(?:\s*\d+)?|Pre-Chorus(?:\s*\d+)?|Chorus(?:\s*\d+)?|"
    r"Bridge(?:\s*\d+)?|Final\s+Chorus|Outro|Hook(?:\s*\d+)?|"
    r"Interlude|Break|Post-Chorus(?:\s*\d+)?)\]$",
    re.IGNORECASE,
)
TAG_ONLY_RE = re.compile(r"^\[.*\]$")

# 空間座標の実況になりやすい語句（誤検知を抑えるため具体表現中心）
SPATIAL_WORDS = (
    "右側", "左側", "右手", "左手", "すぐ横", "横の", "奥の", "手前",
    "ドアの上", "机の", "角の", "向こう", "内側", "外側", "正面",
    "斜め", "隣り", "隣の", "真上", "真下", "足元", "頭上",
)

# Suno / OpenJTalk で読みが割れやすく、ひらがな表記を検討すべき多音語
POLYPHONIC_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("夜風", re.compile(r"夜風")),
    ("今日", re.compile(r"今日")),
    ("明日", re.compile(r"明日")),
    ("持ち手", re.compile(r"持ち手")),
    ("一人", re.compile(r"一人")),
    ("二人", re.compile(r"二人")),
    ("開く", re.compile(r"(?<![一-龥])開[くけき]")),
    ("角", re.compile(r"(?<![一-龥])角(?![一-龥])")),
    ("端", re.compile(r"(?<![一-龥])端(?![一-龥])")),
    ("空", re.compile(r"(?<![一-龥])空(?![一-龥])")),
    ("方", re.compile(r"(?<![一-龥])方(?![一-龥])")),
    ("間", re.compile(r"(?<![一-龥])間(?![一-龥])")),
    ("灯", re.compile(r"(?<![一-龥])灯(?![一-龥])")),
    ("家", re.compile(r"(?<![一-龥])家(?![一-龥])")),
)

# 歌詞ルール上の禁止記号（ブレスはスペース・改行で表現する）
FORBIDDEN_PUNCT_RE = re.compile(r"[、「」『』]")

# 反復チェック用の語彙抽出（漢字2文字以上、またはカタカナ3文字以上）
REPEAT_TOKEN_RE = re.compile(r"[一-龥々]{2,}|[ァ-ヶー]{3,}")


@dataclass
class LineCheck:
    section: str
    line_no: int
    text: str
    reading: str
    mora_count: int
    speech_sec: float
    mora_per_sec: float
    spatial_hits: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)


def parse_lyrics(path: Path) -> list[tuple[str, int, str]]:
    """歌詞ファイルから (セクション名, 元行番号, 歌詞行) のリストを抽出する。"""
    results: list[tuple[str, int, str]] = []
    current_section = "Unknown"
    section_counts: dict[str, int] = {}

    for idx, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        m = SECTION_RE.match(line)
        if m:
            base = m.group(1).strip()
            section_counts[base] = section_counts.get(base, 0) + 1
            # 同じセクション名が複数回出る場合（例: Chorus, Pre-Chorus）を区別
            if section_counts[base] > 1 and not re.search(r"\d+$", base):
                current_section = f"{base} #{section_counts[base]}"
            else:
                current_section = base
            continue
        if TAG_ONLY_RE.match(line):
            continue
        results.append((current_section, idx, line))
    return results


def fetch_audio_query(base_url: str, text: str, speaker: int) -> dict:
    resp = requests.post(
        f"{base_url}/audio_query",
        params={"text": text, "speaker": speaker},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def synthesize_wav(base_url: str, query: dict, speaker: int) -> bytes:
    resp = requests.post(
        f"{base_url}/synthesis",
        params={"speaker": speaker},
        json=query,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.content


def analyze_query(section: str, line_no: int, text: str, query: dict) -> LineCheck:
    moras: list[str] = []
    speech_sec = 0.0
    for phrase in query.get("accent_phrases", []):
        for m in phrase.get("moras", []):
            moras.append(m.get("text", ""))
            speech_sec += float(m.get("consonant_length") or 0.0)
            speech_sec += float(m.get("vowel_length") or 0.0)
        pause = phrase.get("pause_mora")
        if pause:
            moras.append(" ")

    reading = "".join(moras).strip()
    mora_count = sum(
        len(phrase.get("moras", [])) for phrase in query.get("accent_phrases", [])
    )
    mps = (mora_count / speech_sec) if speech_sec > 0 else 0.0
    spatial_hits = [w for w in SPATIAL_WORDS if w in text]
    poly_hits = [label for label, pat in POLYPHONIC_PATTERNS if pat.search(text)]
    punct_hits = sorted(set(FORBIDDEN_PUNCT_RE.findall(text)))

    flags: list[str] = []
    if mora_count >= 22:
        flags.append("長すぎ")
    elif mora_count <= 4:
        flags.append("極短")
    if mps >= 9.0:
        flags.append("詰まり気味")
    if spatial_hits:
        flags.append(f"座標語({','.join(spatial_hits)})")
    if poly_hits:
        flags.append(f"多音字({','.join(poly_hits)})")
    if punct_hits:
        flags.append(f"禁止記号({''.join(punct_hits)})")

    return LineCheck(
        section=section,
        line_no=line_no,
        text=text,
        reading=reading,
        mora_count=mora_count,
        speech_sec=speech_sec,
        mora_per_sec=mps,
        spatial_hits=spatial_hits,
        flags=flags,
    )


def flag_section_outliers(checks: list[LineCheck]) -> None:
    """同一セクション内で中央値から大きく外れる行にフラグを立てる。"""
    by_sec: dict[str, list[LineCheck]] = {}
    for c in checks:
        by_sec.setdefault(c.section, []).append(c)

    for items in by_sec.values():
        if len(items) < 3:
            continue
        med = statistics.median(i.mora_count for i in items)
        for i in items:
            if i.mora_count >= med + 5 and "長すぎ" not in i.flags:
                i.flags.append(f"拍突出(中央値{med:.0f})")


def compare_symmetric_sections(checks: list[LineCheck]) -> list[str]:
    """Verse 1 vs Verse 2 などの対称セクションの行数・モーラ差を比較する。"""
    by_sec: dict[str, list[LineCheck]] = {}
    for c in checks:
        by_sec.setdefault(c.section, []).append(c)

    notes: list[str] = []
    pairs = [("Verse 1", "Verse 2"), ("Pre-Chorus", "Pre-Chorus #2"), ("Chorus", "Chorus #2")]
    for a, b in pairs:
        if a in by_sec and b in by_sec:
            la, lb = by_sec[a], by_sec[b]
            ma = statistics.mean(x.mora_count for x in la)
            mb = statistics.mean(x.mora_count for x in lb)
            diff_lines = len(lb) - len(la)
            diff_mora = abs(mb - ma)
            status = "OK"
            if diff_lines != 0 or diff_mora >= 2.5:
                status = "注意"
            notes.append(
                f"- **{a} vs {b}** [{status}]: "
                f"行数 {len(la)} vs {len(lb)} / 平均モーラ {ma:.1f} vs {mb:.1f}"
            )
    return notes


def find_repeated_words(checks: list[LineCheck], min_count: int = 3) -> list[tuple[str, int]]:
    """重複行（サビ再掲など）を除いたユニーク行内で、過度に反復される語を抽出する。"""
    seen_lines: set[str] = set()
    counter: Counter[str] = Counter()
    for c in checks:
        norm = re.sub(r"\s+", "", c.text)
        if norm in seen_lines:
            continue
        seen_lines.add(norm)
        for token in set(REPEAT_TOKEN_RE.findall(c.text)):
            counter[token] += 1
    return [(w, n) for w, n in counter.most_common() if n >= min_count]


def concat_wavs(
    segments: list[tuple[str, bytes]],
    out_path: Path,
    line_gap_sec: float = 0.35,
    section_gap_sec: float = 0.90,
) -> float:
    """各行の WAV を結合し、行間・セクション間に無音を挿入して書き出す。総秒数を返す。"""
    if not segments:
        return 0.0

    params = None
    frames_out: list[bytes] = []
    total_frames = 0
    prev_sec = None

    for sec, wav_bytes in segments:
        with wave.open(io.BytesIO(wav_bytes), "rb") as w:
            if params is None:
                params = w.getparams()
                frame_size = params.nchannels * params.sampwidth
                rate = params.framerate
            elif prev_sec is not None:
                gap = section_gap_sec if sec != prev_sec else line_gap_sec
                gap_frames = int(rate * gap)
                frames_out.append(b"\x00" * (gap_frames * frame_size))
                total_frames += gap_frames

            data = w.readframes(w.getnframes())
            frames_out.append(data)
            total_frames += w.getnframes()
            prev_sec = sec

    assert params is not None
    with wave.open(str(out_path), "wb") as out:
        out.setparams(params)
        for chunk in frames_out:
            out.writeframes(chunk)

    return total_frames / params.framerate


def render_markdown(
    src_path: Path,
    speaker: int,
    checks: list[LineCheck],
    sym_notes: list[str],
    repeated_words: list[tuple[str, int]],
    wav_path: Path | None,
    wav_sec: float,
) -> str:
    total_moras = sum(c.mora_count for c in checks)
    avg_mora = statistics.mean(c.mora_count for c in checks) if checks else 0.0
    total_speech = sum(c.speech_sec for c in checks)
    spatial_total = sum(len(c.spatial_hits) for c in checks)
    flagged = [c for c in checks if c.flags]

    lines = [
        f"# 音韻・音声チェック: {src_path.name}",
        "",
        "## サマリー",
        f"- 対象行数: **{len(checks)}行** / 総モーラ数: **{total_moras}**（平均 **{avg_mora:.1f}** モーラ/行）",
        f"- 純発声時間合計: **{total_speech:.1f}秒**"
        + (f" / 試聴 WAV: `{wav_path.name}`（{wav_sec:.1f}秒, speaker={speaker}）" if wav_path else ""),
        f"- 警告あり: **{len(flagged)}行** / 座標語ヒット: **{spatial_total}件** / 反復語(3回以上): **{len(repeated_words)}語**",
        "",
    ]

    if sym_notes:
        lines.extend(["## セクション対称性", *sym_notes, ""])

    if repeated_words:
        rep_str = " / ".join(f"`{w}` ({n}回)" for w, n in repeated_words)
        lines.extend(["## 語彙の反復（ユニーク行内3回以上）", f"- {rep_str}", ""])

    lines.extend([
        "## 行別チェック",
        "",
        "| セクション | 歌詞 | 読み（OpenJTalk） | モーラ | 秒 | 拍/秒 | 指摘 |",
        "| :--- | :--- | :--- | ---: | ---: | ---: | :--- |",
    ])
    for c in checks:
        flag_str = ", ".join(c.flags) if c.flags else "-"
        lines.append(
            f"| {c.section} | {c.text} | {c.reading} | {c.mora_count} | "
            f"{c.speech_sec:.2f} | {c.mora_per_sec:.1f} | {flag_str} |"
        )

    return "\n".join(lines) + "\n"


def check_engine(base_url: str) -> str:
    resp = requests.get(f"{base_url}/version", timeout=5)
    resp.raise_for_status()
    return resp.text.strip().strip('"')


def main() -> int:
    parser = argparse.ArgumentParser(description="VOICEVOX Engine で歌詞の音韻診断と仮読み上げ WAV を生成")
    parser.add_argument("lyrics_file", type=Path, help="歌詞ファイル（07_lyrics.txt 等）")
    parser.add_argument("--speaker", type=int, default=DEFAULT_SPEAKER, help=f"話者ID（既定: {DEFAULT_SPEAKER}）")
    parser.add_argument("--url", default=DEFAULT_URL, help=f"VOICEVOX Engine URL（既定: {DEFAULT_URL}）")
    parser.add_argument("--no-wav", action="store_true", help="WAV 出力を省き音韻解析のみ実行")
    parser.add_argument("--out-dir", type=Path, default=None, help="出力先フォルダ（既定: 入力ファイルと同じ場所）")
    args = parser.parse_args()

    if not args.lyrics_file.exists():
        print(f"File not found: {args.lyrics_file}", file=sys.stderr)
        return 1

    try:
        ver = check_engine(args.url)
    except requests.RequestException:
        print(
            f"VOICEVOX Engine に接続できません ({args.url})。\n"
            "VOICEVOX アプリ（または Engine）を起動してから再実行してください。",
            file=sys.stderr,
        )
        return 1

    parsed = parse_lyrics(args.lyrics_file)
    if not parsed:
        print("歌詞行が見つかりませんでした。", file=sys.stderr)
        return 1

    print(f"VOICEVOX Engine v{ver} 接続OK / {len(parsed)}行を解析中...")

    checks: list[LineCheck] = []
    wav_segments: list[tuple[str, bytes]] = []
    for sec, line_no, text in parsed:
        query = fetch_audio_query(args.url, text, args.speaker)
        checks.append(analyze_query(sec, line_no, text, query))
        if not args.no_wav:
            wav_segments.append((sec, synthesize_wav(args.url, query, args.speaker)))

    flag_section_outliers(checks)
    sym_notes = compare_symmetric_sections(checks)
    repeated_words = find_repeated_words(checks)

    out_dir = args.out_dir or args.lyrics_file.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    wav_path: Path | None = None
    wav_sec = 0.0
    if not args.no_wav:
        wav_path = out_dir / "preview.wav"
        wav_sec = concat_wavs(wav_segments, wav_path)

    md_path = out_dir / "audio-check.md"
    md_text = render_markdown(
        args.lyrics_file, args.speaker, checks, sym_notes, repeated_words, wav_path, wav_sec
    )
    md_path.write_text(md_text, encoding="utf-8")

    # コンソール要約
    flagged = [c for c in checks if c.flags]
    avg_mora = statistics.mean(c.mora_count for c in checks)
    print(
        f"完了: {len(checks)}行 / 平均 {avg_mora:.1f} モーラ / "
        f"警告 {len(flagged)}行 / 反復語 {len(repeated_words)}語"
    )
    for note in sym_notes:
        print(f"  {note}")
    if repeated_words:
        print("  [反復語] " + ", ".join(f"{w}({n})" for w, n in repeated_words))
    if flagged:
        print("  [警告行]")
        for c in flagged:
            print(f"    - [{c.section}] {c.text} ({c.mora_count}mora, {', '.join(c.flags)})")
    print(f"出力: {md_path}")
    if wav_path:
        print(f"音声: {wav_path} ({wav_sec:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
