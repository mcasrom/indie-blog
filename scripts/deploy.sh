#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DEST="/var/www/indie"
RESTART_API=0
if [[ "${1:-}" == "--restart-api" ]]; then
  RESTART_API=1
fi

echo "[indie] build"
npm run build

if [[ ! -f dist/client/index.html ]]; then
  echo "[indie] ERROR: falta dist/client/index.html" >&2
  exit 1
fi
if ! grep -q '| indie' dist/client/index.html; then
  echo "[indie] ERROR: la portada generada no es de indie (¿build cruzado?)" >&2
  exit 1
fi
if grep -q 'Geopolítica y análisis crítico del poder | Análisis' dist/client/index.html; then
  echo "[indie] ERROR: la portada generada es del blog de análisis" >&2
  exit 1
fi
if [[ ! -d dist/client/posts ]]; then
  echo "[indie] ERROR: faltan los posts en dist/client/posts" >&2
  exit 1
fi

echo "[indie] publicar en $DEST"
rsync -a --delete dist/client/ "$DEST"/

if ! grep -q '| indie' "$DEST/index.html"; then
  echo "[indie] ERROR: $DEST/index.html no es de indie" >&2
  exit 1
fi
if grep -q 'Geopolítica y análisis crítico del poder | Análisis' "$DEST/index.html"; then
  echo "[indie] ERROR: $DEST/index.html es del blog de análisis" >&2
  exit 1
fi

missing=0
while IFS= read -r -d '' p; do
  rel="${p#dist/client/}"
  if [[ ! -f "$DEST/$rel" ]]; then
    echo "[indie] ERROR: falta $DEST/$rel" >&2
    missing=1
  fi
done < <(find dist/client/posts -type f -name 'index.html' -print0)
[[ "$missing" -eq 0 ]] || exit 1

if [[ "$RESTART_API" -eq 1 ]]; then
  echo "[indie] reiniciar API"
  pm2 restart indie-blog
fi

echo "[indie] OK · $(grep -o '<title>[^<]*' "$DEST/index.html" | head -1 | sed 's/<title>//')"
echo "[indie] purga CF pendiente: bash demo/cf_purge.sh pruebapublica"
