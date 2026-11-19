"""work/timing.log から各工程と合計の所要時間を集計して表示する。"""
from datetime import datetime
import sys
from pathlib import Path


def parse_log(path: Path) -> list[tuple[datetime, str]]:
    entries: list[tuple[datetime, str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        try:
            t = datetime.strptime(parts[0], "%H:%M:%S")
        except ValueError:
            continue
        entries.append((t, parts[1]))
    return entries


def fmt_sec(sec: int) -> str:
    m, s = divmod(max(0, sec), 60)
    return f"{m}m{s:02d}s" if m else f"{s}s"


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python calc_timing.py <timing.log>")
        return 1
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        return 1

    entries = parse_log(path)
    if len(entries) < 2:
        print("Not enough timing entries.")
        return 1

    spans: list[tuple[str, int]] = []
    for i in range(len(entries) - 1):
        t0, label = entries[i]
        t1, _ = entries[i + 1]
        diff = int((t1 - t0).total_seconds())
        if diff < 0:
            diff += 86400  # 日跨ぎ補正
        spans.append((label, diff))

    total = sum(d for _, d in spans)
    longest_label, longest_sec = max(spans, key=lambda x: x[1])
    print(f"合計: {fmt_sec(total)} ({total}s) / 最長: {longest_label} ({fmt_sec(longest_sec)})")
    for label, sec in spans:
        print(f"  - {label}: {fmt_sec(sec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
