#!/usr/bin/env bash
# scripts/publish.sh
# Publica un post del blog: toma un .md de la cola, lo mueve a content/posts,
# hace build y reinicia PM2.
#
# Uso:
#   scripts/publish.sh <archivo.md>
# Ejemplo:
#   scripts/publish.sh borrador-titulo.md   (desde la raíz del proyecto)
#
# El slug sale del nombre del archivo: "mi-post.md" -> /posts/mi-post/
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DRAFTS_DIR="${PROJECT_DIR}/borradores"
POSTS_DIR="${PROJECT_DIR}/src/content/posts"

if [ $# -lt 1 ]; then
  echo "Uso: scripts/publish.sh <archivo.md>"
  echo "Busca el archivo en borradores/ o en la raíz del proyecto."
  exit 1
fi

FILE="$1"

# Localizar el archivo: si es ruta absoluta, usarla; si no, buscar en borradores/ o raíz.
SRC=""
if [ -f "$FILE" ]; then
  SRC="$FILE"
elif [ -f "${DRAFTS_DIR}/${FILE}" ]; then
  SRC="${DRAFTS_DIR}/${FILE}"
elif [ -f "${PROJECT_DIR}/${FILE}" ]; then
  SRC="${PROJECT_DIR}/${FILE}"
else
  echo "ERROR: No encuentro '$FILE'. ¿Está en borradores/ o en la raíz?"
  exit 1
fi

SLUG="$(basename "$SRC" .md)"
DEST="${POSTS_DIR}/${SLUG}.md"

# Validar que no exista ya un post con ese slug
if [ -f "$DEST" ]; then
  echo "ERROR: Ya existe src/content/posts/${SLUG}.md"
  exit 1
fi

echo "==> Publicando: ${SLUG}"
mkdir -p "$POSTS_DIR"
mv "$SRC" "$DEST"

# Validar frontmatter básico (title, pubDate)
if ! grep -qE '^title:' "$DEST"; then
  echo "ERROR: Falta 'title:' en el frontmatter. Revisa el archivo."
  exit 1
fi
if ! grep -qE '^pubDate:' "$DEST"; then
  echo "ERROR: Falta 'pubDate:' en el frontmatter. Revisa el archivo."
  exit 1
fi

echo "==> Build..."
cd "$PROJECT_DIR"
npm run build

echo "==> Reiniciando PM2..."
source .env 2>/dev/null || true
ADMIN_SECRET="${ADMIN_SECRET:-}" PORT=3018 HOST=0.0.0.0 pm2 restart analisis-pub --update-env >/dev/null 2>&1

echo "==> Publicado: https://analisis.pruebapublica.com/posts/${SLUG}/"
