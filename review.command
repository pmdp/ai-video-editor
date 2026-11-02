#!/bin/bash
# Double-click launcher: asks for the match video and the clips file, renders out/review.mp4 next to this file.
cd "$(dirname "$0")" || exit 1

ask() {  # prompt for a dragged-in path; Terminal adds a trailing space and escapes spaces as "\ "
  local p
  read -r -p "$1" p
  p="${p%"${p##*[![:space:]]}"}"
  printf '%s' "${p//\\/}"
}

VIDEO="$(ask "Arrastra aquí el vídeo del partido y pulsa Enter: ")"
CLIPS="$(ask "Arrastra aquí el .txt de clips (Enter = clips.txt): ")"
if python3 review.py "$VIDEO" "${CLIPS:-clips.txt}" out; then
  open out
else
  read -r -p "Ha fallado. Pulsa Enter para cerrar."
fi
