#!/usr/bin/env bash
# Build para Cloudflare Pages
#   Build command:          bash build.sh
#   Build output directory: dist
# Copia solo lo que la web necesita (sin documentación, scripts ni fotos originales),
# mete el CSS en línea en cada página y minifica el HTML.
# Las páginas se generan con: python3 tools/generar_web.py (el resultado ya va en el repo).
set -euo pipefail

rm -rf dist
mkdir -p dist/images dist/js

cp index.html 404.html robots.txt sitemap.xml llms.txt llms-full.txt site.webmanifest favicon.ico _headers dist/
cp js/site.js dist/js/
cp -R fonts dist/
cp -R images/opt dist/images/
for page in */index.html; do
  dir="${page%/index.html}"
  case "$dir" in dist|images|fonts|tools|css|js) continue ;; esac
  mkdir -p "dist/$dir"
  cp "$page" "dist/$dir/"
done

# CSS en línea + minificado (si no hay python3, se publica el CSS como archivo aparte)
if command -v python3 >/dev/null 2>&1; then
  python3 tools/minify.py css/site.css $(find dist -name '*.html')
else
  mkdir -p dist/css && cp css/site.css dist/css/
fi

# Comprobación: toda ruta local referenciada en las páginas debe existir en dist/
missing=0
for page in $(find dist -name '*.html'); do
  for ref in $(grep -oE '(src|href|srcset|imagesrcset|data-full)="[^"]+"' "$page" | sed -E 's/^[a-z-]+="//; s/"$//' | tr ',' '\n' | awk '{print $1}' | grep -E '^/[^/]' || true); do
    clean="${ref%%[?#]*}"
    case "$clean" in */) clean="${clean}index.html" ;; esac
    if [ ! -e "dist$clean" ]; then echo "FALTA: $ref (en $page)"; missing=1; fi
  done
done
[ "$missing" -eq 0 ] || exit 1

echo "Build OK: $(find dist -type f | wc -l | tr -d ' ') archivos, $(du -sh dist | cut -f1)"
