#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POSTS_DIR="$PROJECT_DIR/src/content/posts"
DRAFTS_DIR="$PROJECT_DIR/borradores"

DRY=0
if [[ "${1:-}" == "--dry" ]]; then
  DRY=1
  shift
fi

if [[ $# -lt 1 ]]; then
  echo "Uso: scripts/publish.sh [--dry] <archivo.md|directorio>"
  exit 1
fi

SRC="$1"
if [[ ! -e "$SRC" ]]; then
  if [[ -e "$DRAFTS_DIR/$SRC" ]]; then
    SRC="$DRAFTS_DIR/$SRC"
  elif [[ -e "$PROJECT_DIR/$SRC" ]]; then
    SRC="$PROJECT_DIR/$SRC"
  else
    echo "ERROR: no encuentro '$SRC' (ni en borradores/ ni en la raíz)" >&2
    exit 1
  fi
fi

if [[ -d "$SRC" ]]; then
  if [[ ! -f "$SRC/index.md" ]]; then
    echo "ERROR: el directorio no contiene index.md" >&2
    exit 1
  fi
  SLUG="$(basename "$SRC")"
  DEST="$POSTS_DIR/$SLUG"
  FRONT="$SRC/index.md"
else
  if [[ "$SRC" != *.md ]]; then
    echo "ERROR: debe ser un .md o un directorio con index.md" >&2
    exit 1
  fi
  SLUG="$(basename "$SRC" .md)"
  DEST="$POSTS_DIR/$SLUG.md"
  FRONT="$SRC"
fi

if [[ -e "$DEST" ]]; then
  echo "ERROR: ya existe $DEST" >&2
  exit 1
fi
if ! grep -qE '^title:' "$FRONT"; then
  echo "ERROR: falta 'title:' en el frontmatter" >&2
  exit 1
fi
if ! grep -qE '^pubDate:' "$FRONT"; then
  echo "ERROR: falta 'pubDate:' en el frontmatter" >&2
  exit 1
fi

if [[ "$DRY" -eq 1 ]]; then
  echo "[dry] publicaría $SLUG → $DEST"
  echo "[dry] build y deploy omitidos"
  exit 0
fi

echo "==> Publicando: $SLUG"
mkdir -p "$POSTS_DIR"
mv "$SRC" "$DEST"

bash "$PROJECT_DIR/scripts/deploy.sh"

echo "==> Publicado: https://indie.pruebapublica.com/posts/${SLUG}/"
