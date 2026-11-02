# ai-video-editor

Cut football match review clips with a news-style title, then join them with transitions.
Driven by Claude Code + [ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill), or plain ffmpeg.

See [CLAUDE.md](CLAUDE.md) for the input format and pipeline.

## Uso en cualquier Mac

1. Una vez: `brew install ffmpeg-full` (Python 3 ya viene con macOS).
2. Escribe los cortes en un `.txt`: una línea por clip, `MM:SS-MM:SS título` (o `H:MM:SS`).
   Parte de `clips.example.txt`: cópialo a `clips.txt` (ignorado por git) y edítalo.
3. Doble clic en `review.command`: arrastra el vídeo del partido y pulsa Enter, luego arrastra el `.txt`
   y pulsa Enter (o solo Enter para usar `clips.txt` de esta carpeta). El resultado es `out/review.mp4`.

Si macOS no deja abrir `review.command` la primera vez: clic derecho → Abrir.
Desde la terminal: `python3 review.py partido.mp4 clips.txt out`.
