#!/usr/bin/env python3
"""Cut titled review clips from a match video and join them with transitions into out_dir/review.mp4.

Usage: python3 review.py <source.mp4> [clips.txt] [out_dir]
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FADE = 0.5
TIME = r"(\d+):(\d{2})(?::(\d{2}))?"
LINE = re.compile(rf"^{TIME}\s*-\s*{TIME}\s+(.+)$")
# re-encode needed to burn text; CRF 18 keeps it visually lossless, size/fps/sample rate carry over from source
ENCODE = ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
          "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart"]


def seconds(a, b, c):
    return int(a) * 3600 + int(b) * 60 + int(c) if c else int(a) * 60 + int(b)


def parse(text):
    clips = []
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        m = LINE.match(line)
        if not m:
            sys.exit(f"clips line {n}: expected 'MM:SS-MM:SS title', got: {raw!r}")
        start, end = seconds(*m.group(1, 2, 3)), seconds(*m.group(4, 5, 6))
        if end <= start:
            sys.exit(f"clips line {n}: end {end}s is not after start {start}s")
        clips.append((start, end, m.group(7).strip()))
    return clips


def run(cmd):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def height(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=height",
                          "-of", "csv=p=0", str(path)], check=True, capture_output=True, text=True)
    return int(out.stdout)


def has_audio(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", str(path)], check=True, capture_output=True, text=True)
    return bool(out.stdout.strip())


def title_filter(textfile, h):
    # news-style lower third for the whole clip: dark box sized to the text, red bar on its left.
    # y_align=font makes box height depend on the font, not the text, so both boxes always match;
    # the red bar is a zero-width-space drawtext whose box is all border.
    fs, pad_v, pad_h, bar = h // 24, h // 54, h // 36, h // 48
    common = f"fontfile='{FONT}':expansion=none:fontsize={fs}:y_align=font:y={round(h * 0.80) + pad_v}:box=1"
    return (f"drawtext={common}:text='​':fontcolor=white@0:x={bar}:boxcolor=red:"
            f"boxborderw={pad_v}|0|{pad_v}|{bar},"
            f"drawtext={common}:textfile='{textfile}':fontcolor=white:x={bar + pad_h}:"
            f"boxcolor=black@0.65:boxborderw={pad_v}|{pad_h}")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    clips = parse(Path(sys.argv[2] if len(sys.argv) > 2 else "clips.txt").read_text(encoding="utf-8"))
    out = Path(sys.argv[3] if len(sys.argv) > 3 else "out")
    # Homebrew's ffmpeg-full is keg-only: use it when installed (Apple Silicon, then Intel prefix)
    for d in ("/opt/homebrew/opt/ffmpeg-full/bin", "/usr/local/opt/ffmpeg-full/bin"):
        if Path(d).is_dir():
            os.environ["PATH"] = d + os.pathsep + os.environ["PATH"]
            break
    filters = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    if " drawtext " not in filters:
        sys.exit("ffmpeg has no drawtext; install it with: brew install ffmpeg-full")

    out.mkdir(parents=True, exist_ok=True)
    h, audio = height(src), has_audio(src)  # some match recordings have no audio track
    # one ffmpeg pass: each clip is its own seeked input of the source, titled, then chained with
    # xfade/acrossfade in clips.txt order. Offsets use the -t durations, which both streams are trimmed to.
    with tempfile.TemporaryDirectory() as tmp:
        inputs, graph, offset = [], [], 0.0
        for i, (start, end, title) in enumerate(clips):
            textfile = Path(tmp) / f"{i}.txt"
            textfile.write_text(title.upper(), encoding="utf-8")
            inputs += ["-ss", str(start), "-t", str(end - start), "-i", str(src)]
            graph.append(f"[{i}:v]{title_filter(textfile, h)}[t{i}]")
            if i == 0:
                if audio:
                    graph.append("[0:a]anull[a0]")  # a filter output, so -map works with a single clip too
                v, a = "[t0]", "[a0]"
            else:
                graph.append(f"{v}[t{i}]xfade=transition=fade:duration={FADE}:offset={offset:.3f}[v{i}]")
                if audio:
                    graph.append(f"{a}[{i}:a]acrossfade=d={FADE}[a{i}]")
                v, a = f"[v{i}]", f"[a{i}]"
            offset += end - start - FADE
        run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(graph),
             "-map", v, *(["-map", a] if audio else []), *ENCODE, str(out / "review.mp4")])


if __name__ == "__main__":
    main()
