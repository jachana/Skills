#!/usr/bin/env bash
# Prepara/publica evidencia visual (IMÁGENES o VIDEOS) para el PR de un issue.
#
#   Acepta capturas (.png/.jpg/.jpeg/.gif/.webp) y videos de Playwright
#   (.webm/.mp4/.mov/.mkv). Los videos se convierten a GIF (ffmpeg); las imágenes
#   se usan tal cual.
#
#   - Repo PÚBLICO: publica los assets en una rama `media/issue-<N>` (worktree
#     temporal, no toca tu rama del fix) y comenta el PR embebiéndolos inline vía
#     raw.githubusercontent.
#   - Repo PRIVADO: GitHub NO renderiza assets desde URLs raw (404 al proxy de
#     imágenes) NI permite subir adjuntos por API (eso necesita sesión de
#     navegador, no token). El script deja los archivos en ./evidencia-issue-<N>/
#     y te indica arrastrarlos al PR (imágenes inline; .webm con reproductor nativo).
#
# Uso:
#   publicar-evidencia.sh <num-issue> <archivo> [archivo...]
#   archivo = imagen (.png/.jpg/.jpeg/.gif/.webp) o video (.webm/.mp4/.mov/.mkv)
#
# Requiere: gh autenticado. ffmpeg solo si pasas videos.
set -euo pipefail

REPO="${REPO:-$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)}"
N="${1:?uso: publicar-evidencia.sh <num-issue> <archivo> [archivo...]}"
shift
[ "$#" -ge 1 ] || { echo "Pasa al menos un archivo de evidencia (imagen o video)." >&2; exit 1; }
command -v gh >/dev/null || { echo "Falta gh en el PATH." >&2; exit 1; }

ext_lc()   { printf '%s' "${1##*.}" | tr '[:upper:]' '[:lower:]'; }
is_image() { case "$(ext_lc "$1")" in png|jpg|jpeg|gif|webp) return 0;; *) return 1;; esac; }
is_video() { case "$(ext_lc "$1")" in webm|mp4|mov|mkv|m4v)  return 0;; *) return 1;; esac; }

# Genera el asset embebible de $1 dentro del dir $2 e imprime SOLO su nombre.
# Imagen → copia tal cual. Video → convierte a gif (requiere ffmpeg).
make_asset() {
  local src="$1" dir="$2" base; base="$(basename "${src%.*}")"
  if is_image "$src"; then
    local out="issue-$N-$base.$(ext_lc "$src")"
    cp -f "$src" "$dir/$out"; printf '%s' "$out"
  elif is_video "$src"; then
    command -v ffmpeg >/dev/null || { echo "Falta ffmpeg (necesario para videos)." >&2; return 1; }
    local out="issue-$N-$base.gif"
    ffmpeg -y -loglevel error -i "$src" -vf "fps=12,scale=960:-1:flags=lanczos" "$dir/$out"
    printf '%s' "$out"
  else
    echo "Tipo no soportado: $src (usa imagen o video)." >&2; return 1
  fi
}

# ── Repo PRIVADO: no se puede inline por API. Dejar archivos para arrastrar. ──
if [ "$(gh repo view "$REPO" --json isPrivate -q .isPrivate 2>/dev/null)" = "true" ]; then
  DEST="evidencia-issue-$N"; mkdir -p "$DEST"
  for src in "$@"; do
    [ -f "$src" ] || { echo "No existe: $src" >&2; exit 1; }
    cp -f "$src" "$DEST/"                                   # el original (para arrastrar)
    if is_video "$src" && command -v ffmpeg >/dev/null; then
      ffmpeg -y -loglevel error -i "$src" -vf "fps=12,scale=960:-1:flags=lanczos" \
        "$DEST/$(basename "${src%.*}").gif"                # gif opcional, por conveniencia
    fi
  done
  echo "Repo PRIVADO: GitHub no renderiza assets desde URLs raw ni acepta adjuntos por API."
  echo "Archivos en ./$DEST/ — arrástralos a la descripción o un comentario del PR"
  echo "(las imágenes se ven directo; los .webm con el reproductor nativo)."
  exit 0
fi

# ── Repo PÚBLICO: publicar en rama media/ y comentar inline. ──
HEAD_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
BRANCH="media/issue-$N"
WT="$(mktemp -d)"
trap 'git worktree remove --force "$WT" 2>/dev/null || true' EXIT

if git ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1; then
  git fetch -q origin "$BRANCH"; git worktree add -q "$WT" "$BRANCH"
else
  git worktree add -q --detach "$WT"
  # Orphan + vaciar el working tree (no solo el índice) para que media/ tenga SOLO los assets.
  ( cd "$WT" && git checkout -q --orphan "$BRANCH" && git rm -rfq . >/dev/null 2>&1 || true )
fi

md="## Evidencia (generada automáticamente)"$'\n'
for src in "$@"; do
  [ -f "$src" ] || { echo "No existe: $src" >&2; exit 1; }
  out="$(make_asset "$src" "$WT")" || exit 1
  label="$(basename "${src%.*}")"
  md+=$'\n'"### $label"$'\n'"![$label](https://raw.githubusercontent.com/$REPO/$BRANCH/$out)"$'\n'
done

( cd "$WT" && git add -A && git commit -q -m "evidencia issue #$N" && git push -q -u origin "$BRANCH" )
printf '%s\n' "$md" | gh pr comment "$HEAD_BRANCH" --repo "$REPO" --body-file -
echo "✓ Evidencia publicada en rama '$BRANCH' y comentada en el PR del issue #$N."
