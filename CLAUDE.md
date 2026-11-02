# ai-video-editor

Util to edit videos with AI (Claude Code + the `ffmpeg-skill` skill, installed globally in `~/.claude/skills/ffmpeg-skill`) or directly from the command line with ffmpeg.

First use case: football match review clips.

## Pipeline

1. Read a clips file (e.g. `clips.txt`): time ranges of the source match video + the text for each clip.
2. Render `out/review.mp4` in one ffmpeg pass, no per-clip files: each clip is a seeked input of the source, titled, then chained with short transitions (xfade video + acrossfade audio).
   - Same parameters as the source (codec, resolution, fps, pix_fmt, audio codec/rate). Burning text forces a re-encode, so use libx264 at visually lossless quality (CRF ~18) with the source profile, not stream copy.
   - Title burned in as a news-style lower third (box sized to the text at the bottom, red bar on its left) for the whole clip, in UPPERCASE.

## How to run it

- Full review: `python3 review.py <match.mp4> [clips.txt] [out_dir]` (implements the pipeline above). Don't rebuild it by hand with the skill.
- Then check the result with ffmpeg-skill's `look.py` (contact sheet of `out/review.mp4`, plus `--at` on the longest title) and report what the titles look like.
- Anything else (vertical export, loudness, music, a single extra clip, different title style) → use ffmpeg-skill directly.

## Input format (`clips.txt`)

One clip per line: `MM:SS-MM:SS <title>` (`H:MM:SS` also works). Time is from the start of the source video.
`clips.example.txt` is the committed sample; the real `clips.txt` holds match notes and is git-ignored.

- Clips are output in file order, not sorted by time.
- The title is everything after the range, verbatim (`|`, `/`, `¿?`, accents included), then uppercased for display. No special meaning for any character.
- Trim leading/trailing whitespace; skip empty lines.

## Environment

- ffmpeg 9 (Homebrew), Python 3.10, stdlib only.
- The default Homebrew `ffmpeg` has no `drawtext`. Use `ffmpeg-full` (keg-only); `review.py` puts `/opt/homebrew/opt/ffmpeg-full/bin` (or `/usr/local/...` on Intel) first on PATH itself. Check with `npx ffmpeg-skill doctor`.
- Title font: `/System/Library/Fonts/Supplemental/Arial Bold.ttf` (DejaVu Sans is not installed).
- Source videos (`*.mp4`) and `out/` are git-ignored; never commit them.
